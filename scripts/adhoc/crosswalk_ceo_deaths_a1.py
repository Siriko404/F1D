"""Phase A1 — Cross-walk CEO-death candidate events to gvkey + report per-source yields.

Per plan default: STOP after A1. A2 (panel-filter) + A3 (cross-source dedup) require
explicit user authorization. Inputs: 4 filtered parquets at data/raw/ceo_death_events/
+ ExecuComp at inputs/Execucomp/. Outputs: 5 per-source gvkey-tagged parquets +
crosswalk_summary.json.

Q1 CapIQ KD          : gvkey native; pass through. (592 events)
Q2-A action=Deceased : cusip_number → cusip8 → CCM gvkey. (145 events; high-confidence)
Q2-B residual        : cusip_number → cusip8 → CCM gvkey. (3,743 events; confirmation-only)
Q3 BoardEx           : companyname-fuzzy → CCM conm PRIMARY; ISIN[2:11] for US fallback. (1,905 events)
Q4 ExecuComp         : reason='DECEASED' + ceoann='CEO' + year ∈ [2002,2018]. gvkey native.
"""
from __future__ import annotations
import json
import time
import zipfile
from pathlib import Path
from typing import Optional

import pandas as pd
import polars as pl
import pyarrow.csv as pa_csv

import re

from f1d.shared.string_matching import match_company_names

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "ceo_death_events"
CCM_PATH = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
EXECUCOMP_PATH = ROOT / "inputs" / "Execucomp" / "comp_execucomp.parquet"
BOARDEX_PROFILE_ZIP = ROOT / "inputs" / "BoardEx - Company Profile Details" / "od6uhxa0heyxdjtl.csv.zip"
BOARDEX_PROFILE_PARQUET = DATA_DIR / "boardex_company_profile.parquet"

LINKPRIM_RANK = {"P": 1, "C": 2, "J": 3, "N": 4}
LINKTYPE_RANK = {"LC": 1, "LU": 2}

WIN_START = pd.Timestamp("2002-01-01")
WIN_END = pd.Timestamp("2018-12-31")

# Strict fuzzy threshold — user requires 95%+ confidence.
# token_sort_ratio (not WRatio) avoids substring-bonus false positives like
# "FIRST MIDWEST BANCORP INC" matching generic "BANCORP INC".
FUZZY_THRESHOLD = 95
FUZZY_SCORER = "token_sort_ratio"

# BoardEx companyname annotations to strip BEFORE fuzzy match
BOARDEX_ANNOTATION_RE = re.compile(r"\([^)]*\)")  # strip any "(...)" content


def extract_boardex_profile_lookup() -> pd.DataFrame:
    """Stream BoardEx Company Profile Details zip → small lookup parquet.
    boardid → boardnameshort, cikcode, ticker, isin, hocountryname.
    Idempotent: caches to BOARDEX_PROFILE_PARQUET.
    """
    if BOARDEX_PROFILE_PARQUET.exists():
        df = pd.read_parquet(BOARDEX_PROFILE_PARQUET)
        print(f"[BoardEx-profile] cache hit: {len(df):,} rows", flush=True)
        return df
    print(f"[BoardEx-profile] streaming {BOARDEX_PROFILE_ZIP.name} ...", flush=True)
    cols = ["boardid", "boardname", "boardnameshort", "cikcode", "ticker", "isin", "hocountryname", "previouscompanyid", "successorcompanyid"]
    column_types = {c: "string" for c in cols if c not in {"boardid"}}
    with zipfile.ZipFile(BOARDEX_PROFILE_ZIP) as z:
        inner = z.namelist()[0]
        with z.open(inner) as fh:
            tbl = pa_csv.read_csv(
                fh,
                read_options=pa_csv.ReadOptions(use_threads=True, block_size=64 * 1024 * 1024),
                convert_options=pa_csv.ConvertOptions(
                    include_columns=cols,
                    strings_can_be_null=True,
                    column_types=column_types,
                ),
                parse_options=pa_csv.ParseOptions(invalid_row_handler=lambda r: "skip"),
            )
    df = tbl.to_pandas()
    df.to_parquet(BOARDEX_PROFILE_PARQUET, index=False, compression="zstd")
    print(f"[BoardEx-profile] {len(df):,} rows extracted; saved to {BOARDEX_PROFILE_PARQUET}", flush=True)
    return df


def cik_to_gvkey(
    events: pd.DataFrame,
    cik_col: str,
    date_col: str,
    ccm: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    events = events.copy()
    events["_event_idx"] = events.index
    events["_cik_int"] = pd.to_numeric(events[cik_col], errors="coerce")
    merged = events.merge(
        ccm[["cik", "gvkey", "conm", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"]].dropna(subset=["cik"]),
        left_on="_cik_int", right_on="cik", how="left",
    )
    valid = (
        merged["LINKDT"].isna()
        | merged["LINKENDDT_dt"].isna()
        | (
            (merged[date_col] >= merged["LINKDT"])
            & (merged[date_col] <= merged["LINKENDDT_dt"])
        )
    )
    keep = valid | merged["gvkey"].isna()
    merged = merged[keep].copy()
    merged = merged.sort_values(["_event_idx", "linkprim_rank", "linktype_rank"], kind="stable")
    merged = merged.drop_duplicates(subset=["_event_idx"], keep="first")
    merged = merged.set_index("_event_idx")
    merged.index.name = None
    merged = merged.drop(columns=["cik", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"])
    matched = merged["gvkey"].notna().sum()
    print(f"[{label}] cik→gvkey: {matched:,}/{len(events):,} matched ({100*matched/max(len(events),1):.1f}%)", flush=True)
    return merged


def ticker_to_gvkey(
    events: pd.DataFrame,
    ticker_col: str,
    date_col: str,
    ccm: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    events = events.copy()
    events["_event_idx"] = events.index
    events["_ticker_upper"] = events[ticker_col].astype(str).str.upper().str.strip()
    ccm_tic = ccm[["tic", "gvkey", "conm", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"]].copy()
    ccm_tic["_tic_upper"] = ccm_tic["tic"].astype(str).str.upper().str.strip()
    merged = events.merge(ccm_tic, left_on="_ticker_upper", right_on="_tic_upper", how="left")
    valid = (
        merged["LINKDT"].isna()
        | merged["LINKENDDT_dt"].isna()
        | (
            (merged[date_col] >= merged["LINKDT"])
            & (merged[date_col] <= merged["LINKENDDT_dt"])
        )
    )
    keep = valid | merged["gvkey"].isna()
    merged = merged[keep].copy()
    merged = merged.sort_values(["_event_idx", "linkprim_rank", "linktype_rank"], kind="stable")
    merged = merged.drop_duplicates(subset=["_event_idx"], keep="first")
    merged = merged.set_index("_event_idx")
    merged.index.name = None
    merged = merged.drop(columns=["tic", "_tic_upper", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"])
    matched = merged["gvkey"].notna().sum()
    print(f"[{label}] ticker→gvkey: {matched:,}/{len(events):,} matched ({100*matched/max(len(events),1):.1f}%)", flush=True)
    return merged


def load_ccm() -> pd.DataFrame:
    print("[CCM] loading + sentinel-handling ...", flush=True)
    ccm = pd.read_parquet(CCM_PATH)
    ccm["LINKDT"] = pd.to_datetime(ccm["LINKDT"], errors="coerce")
    # 'E' sentinel = open-ended; coerce to far-future
    ccm["LINKENDDT_clean"] = ccm["LINKENDDT"].replace("E", "2099-12-31")
    ccm["LINKENDDT_dt"] = pd.to_datetime(ccm["LINKENDDT_clean"], errors="coerce")
    ccm["cusip8"] = ccm["cusip"].astype(str).str[:8]
    ccm["linkprim_rank"] = ccm["LINKPRIM"].map(LINKPRIM_RANK).fillna(99)
    ccm["linktype_rank"] = ccm["LINKTYPE"].map(LINKTYPE_RANK).fillna(99)
    print(f"[CCM] {len(ccm):,} rows; {ccm['gvkey'].nunique():,} unique gvkeys", flush=True)
    return ccm


def cusip_to_gvkey(
    events: pd.DataFrame,
    cusip_col: str,
    date_col: str,
    ccm: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    """Cross-walk events with cusip + event_date to gvkey via CCM date-windowed match.
    Dedups on EVENT INDEX so that multiple events sharing same (cusip,date) all get gvkey.
    """
    events = events.copy()
    events["_event_idx"] = events.index
    events["_cusip8"] = events[cusip_col].astype(str).str[:8]
    events["_event_date"] = pd.to_datetime(events[date_col], errors="coerce")

    merged = events.merge(
        ccm[["cusip8", "gvkey", "conm", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"]],
        left_on="_cusip8", right_on="cusip8", how="left",
    )
    valid_window = (
        merged["LINKDT"].isna()
        | merged["LINKENDDT_dt"].isna()
        | (
            (merged["_event_date"] >= merged["LINKDT"])
            & (merged["_event_date"] <= merged["LINKENDDT_dt"])
        )
    )
    keep = valid_window | merged["gvkey"].isna()
    merged = merged[keep].copy()

    # Sort by event-idx + priority, keep highest-priority CCM match per event
    merged = merged.sort_values(["_event_idx", "linkprim_rank", "linktype_rank"], kind="stable")
    merged = merged.drop_duplicates(subset=["_event_idx"], keep="first")
    merged = merged.set_index("_event_idx")
    merged.index.name = None
    merged = merged.drop(columns=["cusip8", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"])

    matched = merged["gvkey"].notna().sum()
    print(f"[{label}] cusip→gvkey: {matched:,}/{len(events):,} matched ({100*matched/max(len(events),1):.1f}%)", flush=True)
    return merged


def companyname_to_gvkey_fuzzy(
    events: pd.DataFrame,
    name_col: str,
    date_col: str,
    ccm: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    """Cross-walk events with companyname → CCM conm via fuzzy match.
    Date-windowed CCM filter: candidates whose [LINKDT, LINKENDDT_dt] cover event_date.
    """
    events = events.copy()
    events["_event_date"] = pd.to_datetime(events[date_col], errors="coerce")

    # Build per-event-date a candidate-pool via vectorized window join. With 1,905
    # events and 32K CCM rows, build name→gvkey lookup using all CCM names; date-check
    # post-fuzzy.
    ccm_names = ccm[["conm", "gvkey", "LINKDT", "LINKENDDT_dt", "linkprim_rank", "linktype_rank"]].copy()
    ccm_names = ccm_names[ccm_names["conm"].notna()]
    # Dedup conm to take highest-priority (linkprim_rank min) gvkey
    ccm_names = ccm_names.sort_values(["conm", "linkprim_rank", "linktype_rank"]).drop_duplicates("conm", keep="first")

    # Build choice_list of conm strings
    choice_list = ccm_names["conm"].tolist()
    conm_to_meta = {row["conm"]: row for _, row in ccm_names.iterrows()}

    matched_records = []
    n_events = len(events)
    progress = max(1, n_events // 20)
    for i, row in enumerate(events.itertuples(index=True), 1):
        query_name = getattr(row, name_col, None)
        if query_name is None or pd.isna(query_name):
            continue
        # Pre-clean BoardEx annotations like "(De-listed XX/YYYY)" before fuzzy.
        query_clean = BOARDEX_ANNOTATION_RE.sub("", str(query_name)).strip()
        if not query_clean:
            continue
        best_match, best_score = match_company_names(
            query=query_clean,
            candidates=choice_list,
            threshold=FUZZY_THRESHOLD,
            scorer_name=FUZZY_SCORER,
            preprocess=True,
        )
        if best_score > 0:
            meta = conm_to_meta[best_match]
            matched_records.append({
                "_event_idx": row.Index,
                "gvkey_fuzzy": meta["gvkey"],
                "conm_fuzzy": meta["conm"],
                "fuzzy_score": float(best_score),
                "query_clean": query_clean,
            })
        if i % progress == 0 or i == n_events:
            print(f"  [{label}] fuzzy progress {i:,}/{n_events:,} -> matched {len(matched_records):,}", flush=True)

    if matched_records:
        match_df = pd.DataFrame(matched_records).set_index("_event_idx")
        events = events.join(match_df, how="left")
    else:
        events["gvkey_fuzzy"] = pd.NA
        events["conm_fuzzy"] = pd.NA
        events["fuzzy_score"] = pd.NA

    matched = events["gvkey_fuzzy"].notna().sum()
    print(f"[{label}] companyname-fuzzy → gvkey: {matched:,}/{len(events):,} matched ({100*matched/max(len(events),1):.1f}%)", flush=True)
    return events


def isin_us_to_gvkey(
    events: pd.DataFrame,
    isin_col: str,
    date_col: str,
    ccm: pd.DataFrame,
    label: str,
) -> pd.DataFrame:
    """Fallback: for events with non-null isin starting 'US', extract cusip = isin[2:11].
    Match via CCM cusip8 + date-window.
    """
    events = events.copy()
    is_us = (
        events[isin_col].notna()
        & events[isin_col].astype(str).str.startswith("US")
        & (events[isin_col].astype(str).str.len() == 12)
    )
    events["_cusip_from_isin"] = events[isin_col].astype(str).str[2:11]
    events.loc[~is_us, "_cusip_from_isin"] = pd.NA

    sub = events[is_us].copy()
    if sub.empty:
        events["gvkey_isin"] = pd.NA
        return events
    sub_matched = cusip_to_gvkey(sub, "_cusip_from_isin", date_col, ccm, f"{label}-isin")
    sub_matched = sub_matched.rename(columns={"gvkey": "gvkey_isin"})[["gvkey_isin"]]
    events = events.join(sub_matched, how="left")
    return events


def crosswalk_q1(ccm: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Q1 CapIQ KD (gvkey native) ===", flush=True)
    df = pl.read_parquet(DATA_DIR / "q1_capiq_filtered.parquet").to_pandas()
    df["announcedate_dt"] = pd.to_datetime(df["announcedate"], errors="coerce")
    df["gvkey"] = df["gvkey"].astype(str)  # gvkey native
    matched = df["gvkey"].notna().sum()
    print(f"[Q1] passthrough: {matched:,}/{len(df):,} have native gvkey", flush=True)
    return df


def crosswalk_q2(ccm: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    print("\n=== Q2 Audit Analytics (partition + cusip→gvkey) ===", flush=True)
    df = pl.read_parquet(DATA_DIR / "q2_audit_filtered.parquet").to_pandas()
    df["eff_date_dt"] = pd.to_datetime(df["eff_date"], errors="coerce")

    q2a = df[df["action"] == "Deceased"].copy()
    q2b = df[df["action"] != "Deceased"].copy()
    print(f"[Q2-partition] Q2-A (action=Deceased): {len(q2a):,} ; Q2-B (residual): {len(q2b):,}", flush=True)

    q2a_xw = cusip_to_gvkey(q2a, "cusip_number", "eff_date_dt", ccm, "Q2-A")
    q2b_xw = cusip_to_gvkey(q2b, "cusip_number", "eff_date_dt", ccm, "Q2-B")
    return q2a_xw, q2b_xw


def crosswalk_q3(ccm: pd.DataFrame, profile: pd.DataFrame) -> pd.DataFrame:
    """Q3 deterministic crosswalk: companyid → boardid → cikcode|ticker|isin → CCM gvkey.
    Priority: cik (most reliable, SEC unique) > ticker (collision risk if reused) > isin → cusip.
    """
    print("\n=== Q3 BoardEx (deterministic via Company Profile Details) ===", flush=True)
    df = pl.read_parquet(DATA_DIR / "q3_boardex_ceo_deaths_in_office.parquet").to_pandas()
    df["dod_date_dt"] = pd.to_datetime(df["dod_date"], errors="coerce")

    # Step 1: Q3.companyid → boardid lookup (companyid in Q3 is float; boardid in profile is float too)
    df["companyid_int"] = pd.to_numeric(df["companyid"], errors="coerce").astype("Int64")
    profile["boardid_int"] = pd.to_numeric(profile["boardid"], errors="coerce").astype("Int64")
    profile_keys = profile[["boardid_int", "boardnameshort", "cikcode", "ticker", "isin", "hocountryname"]].drop_duplicates("boardid_int").rename(
        columns={"isin": "isin_p", "hocountryname": "hocountryname_p"}
    )
    df = df.merge(profile_keys, left_on="companyid_int", right_on="boardid_int", how="left")
    matched_to_profile = df["boardid_int"].notna().sum()
    print(f"[Q3] companyid → boardid lookup: {matched_to_profile:,}/{len(df):,} matched profile ({100*matched_to_profile/max(len(df),1):.1f}%)", flush=True)

    # Step 2: deterministic CCM crosswalks in priority order
    df["gvkey_cik"] = pd.NA
    df["gvkey_tic"] = pd.NA
    df["gvkey_isin"] = pd.NA

    # Path 1: cikcode → CCM cik
    has_cik = df["cikcode"].notna() & (df["cikcode"].astype(str) != "")
    if has_cik.any():
        sub = df[has_cik].copy()
        sub_xw = cik_to_gvkey(sub, "cikcode", "dod_date_dt", ccm, "Q3-cik")
        sub_xw = sub_xw.rename(columns={"gvkey": "gvkey_cik_match"})
        df.loc[sub_xw.index, "gvkey_cik"] = sub_xw["gvkey_cik_match"]

    # Path 2: ticker → CCM tic (only for events without cik match)
    no_cik = df["gvkey_cik"].isna() & df["ticker"].notna() & (df["ticker"].astype(str) != "")
    if no_cik.any():
        sub = df[no_cik].copy()
        sub_xw = ticker_to_gvkey(sub, "ticker", "dod_date_dt", ccm, "Q3-tic")
        sub_xw = sub_xw.rename(columns={"gvkey": "gvkey_tic_match"})
        df.loc[sub_xw.index, "gvkey_tic"] = sub_xw["gvkey_tic_match"]

    # Path 3: ISIN[2:11] → CCM cusip8 (only for events still without match)
    # Use profile-lookup ISIN (isin_p) since it's more complete than Q3-native isin.
    no_match = df["gvkey_cik"].isna() & df["gvkey_tic"].isna() & df["isin_p"].notna()
    if no_match.any():
        sub = df[no_match].drop(columns=["gvkey_isin"]).copy()
        sub_xw = isin_us_to_gvkey(sub, "isin_p", "dod_date_dt", ccm, "Q3-isin")
        df.loc[sub_xw.index, "gvkey_isin"] = sub_xw["gvkey_isin"]

    # Combine: prefer cik > ticker > isin
    df["gvkey"] = df["gvkey_cik"].fillna(df["gvkey_tic"]).fillna(df["gvkey_isin"])
    matched = df["gvkey"].notna().sum()
    cik_n = df["gvkey_cik"].notna().sum()
    tic_n = df["gvkey_tic"].notna().sum()
    isin_n = df["gvkey_isin"].notna().sum()
    print(f"[Q3] DETERMINISTIC combined: {matched:,}/{len(df):,} ({100*matched/max(len(df),1):.1f}%)", flush=True)
    print(f"     cik={cik_n} | ticker={tic_n} | isin={isin_n}", flush=True)
    return df


def crosswalk_q4(ccm: pd.DataFrame) -> pd.DataFrame:
    print("\n=== Q4 ExecuComp (reason=DECEASED + ceoann=CEO) ===", flush=True)
    cols = ["gvkey", "year", "exec_fullname", "ceoann", "reason", "leftofc", "leftco", "execid", "co_per_rol"]
    df = pd.read_parquet(EXECUCOMP_PATH, columns=cols)
    print(f"[Q4] ExecuComp loaded: {len(df):,} rows", flush=True)

    mask = (
        (df["reason"].astype(str).str.upper() == "DECEASED")
        & (df["ceoann"] == "CEO")
        & (df["year"] >= 2002)
        & (df["year"] <= 2018)
    )
    q4 = df[mask].copy()
    q4["death_year"] = q4["year"].astype(int)
    # Use leftofc as proxy for date-of-death (date the deceased CEO left office)
    q4["leftofc_dt"] = pd.to_datetime(q4["leftofc"], errors="coerce")
    q4["death_date_proxy"] = q4["leftofc_dt"].fillna(pd.to_datetime(q4["death_year"].astype(str) + "-12-31"))
    q4["gvkey"] = q4["gvkey"].astype(str)
    print(f"[Q4] reason=DECEASED + ceoann=CEO + year ∈ [2002,2018]: {len(q4):,} matched", flush=True)
    return q4


def main():
    t0 = time.time()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    ccm = load_ccm()
    profile = extract_boardex_profile_lookup()

    q1 = crosswalk_q1(ccm)
    q2a, q2b = crosswalk_q2(ccm)
    q3 = crosswalk_q3(ccm, profile)
    q4 = crosswalk_q4(ccm)

    # Save outputs
    pl.from_pandas(q1).write_parquet(DATA_DIR / "q1_with_gvkey.parquet", compression="zstd")
    pl.from_pandas(q2a).write_parquet(DATA_DIR / "q2A_with_gvkey.parquet", compression="zstd")
    pl.from_pandas(q2b).write_parquet(DATA_DIR / "q2B_with_gvkey.parquet", compression="zstd")
    pl.from_pandas(q3).write_parquet(DATA_DIR / "q3_with_gvkey.parquet", compression="zstd")
    pl.from_pandas(q4).write_parquet(DATA_DIR / "q4_with_gvkey.parquet", compression="zstd")

    summary = {
        "Q1_total": len(q1),
        "Q1_gvkey_matched": int(q1["gvkey"].notna().sum()),
        "Q2A_total": len(q2a),
        "Q2A_gvkey_matched": int(q2a["gvkey"].notna().sum()),
        "Q2B_total": len(q2b),
        "Q2B_gvkey_matched": int(q2b["gvkey"].notna().sum()),
        "Q3_total": len(q3),
        "Q3_gvkey_via_cik": int(q3["gvkey_cik"].notna().sum()),
        "Q3_gvkey_via_ticker": int(q3["gvkey_tic"].notna().sum()),
        "Q3_gvkey_via_isin": int(q3["gvkey_isin"].notna().sum()),
        "Q3_gvkey_combined": int(q3["gvkey"].notna().sum()),
        "Q4_total": len(q4),
        "Q4_gvkey_native": int(q4["gvkey"].notna().sum()),
        "elapsed_sec": round(time.time() - t0, 1),
    }
    with open(DATA_DIR / "crosswalk_summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 60)
    print("PHASE A1 COMPLETE — STOPPING per plan default")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")
    print()
    print("Next: user authorizes A2 (panel-filter) + A3 (cross-source dedup).")


if __name__ == "__main__":
    main()
