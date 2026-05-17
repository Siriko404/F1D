"""Campello et al. (2022 JFQA) replication — STEP 1: sample construction.

From-scratch rebuild. Implements ONLY the raw-Compustat sample-selection
filters from the paper. No beta^UK, no panel, no DiD, no comparison to any
prior F1D output. Step 2+ are deliberately NOT scaffolded here.

Authoritative spec
------------------
Main text, Campello et al. 2022 JFQA, Section IV.B (PDF p.15 / journal p.3192):
    "We use COMPUSTAT Quarterly ... We consider U.S. companies from the first
     calendar quarter of 2010 to the fourth quarter of 2016. We drop utility
     and financial firms, as well as companies whose market value or book
     assets are lower than $10 million."

Supplementary Table C.1 "Sample Selection" full filter sequence (verbatim,
supplementary p.8). Step 1 implements ONLY the raw-Compustat selection
filters; the rest are later-step (need constructed controls / panel /
classifiers) and are intentionally NOT implemented here ("this step only /
not ahead"):
    Raw COMPUSTAT between 2010:Q1 and 2016:Q4                          [Step 1]
    Drop non-US firm-quarters (retain USD, US HQ, dedup)               [Step 1]
    Drop firm-quarters with negative fundamentals (ASSETS and SALES)   [Step 1]
    Drop financials and utilities                                     [Step 1]
    Drop if ASSETS or MARKET_CAPITALIZATION less than $10 million      [Step 1]
    Drop if missing key variables (INVESTMENT, ASSETS, CASH_FLOW, ...)  [later]
    Drop if non-consecutive quarters, or < 12 quarters non-missing      [later]
    Drop if missing Hoberg-Phillips (2016) industry classification      [later]
    Drop if missing beta^UK                                             [later]
    Drop if missing CRSP and I/B/E/S controls                           [later]

Operationalization (resolved against the raw extract, see probe/guard)
---------------------------------------------------------------------
* US firm-quarter   : curcdq == 'USD'  AND  loc == 'USA'  (loc = HQ country).
                      "duplicates excluded": the WRDS extract is already
                      canonical (indfmt=INDL, datafmt=STD, consol=C all
                      single-valued; (gvkey,datadate) already unique), so the
                      dedup filter is a verified no-op — asserted, not applied.
* Negative fund.    : drop atq < 0  OR  saleq < 0.
* Financials/util.  : drop SIC in [6000,6999] (financials) or [4900,4999]
                      (utilities).
* $10M screen       : keep atq >= 10  AND  mktcap >= 10, where
                      mktcap = prccq * cshoq (Compustat $millions).
                      Cross-checked vs mkvaltq: median rel.diff 0.0000.
* Window            : datadate in [2010-01-01, 2016-12-31] (calendar quarters
                      2010Q1..2016Q4), applied before the C.1 filters.

Output
------
outputs/campello_rebuild/step1_sample/<timestamp>/
    sample.parquet   filtered firm-quarter universe
    metadata.json    waterfall counts + exact filter definitions (audit trail)

Run:  python scripts/campello_rebuild/step1_sample.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step1_sample"

WINDOW_START = pd.Timestamp("2010-01-01")
WINDOW_END = pd.Timestamp("2016-12-31")

# SIC ranges dropped per Table C.1 "financials and utilities".
FIN_SIC = (6000, 6999)
UTIL_SIC = (4900, 4999)

# $10 million in Compustat units ($millions).
SIZE_THRESHOLD = 10.0

READ_COLS = [
    "gvkey", "datadate", "fyearq", "fqtr", "sic",
    "atq", "saleq", "prccq", "cshoq", "mkvaltq",
    "loc", "curcdq", "fic", "indfmt", "datafmt", "consol",
]

def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    print("Step 1 sample NOT built. Resolve the data issue before proceeding.")
    sys.exit(1)


def load_raw() -> pd.DataFrame:
    if not RAW.exists():
        _abort(f"raw Compustat parquet not found: {RAW}")
    schema_cols = {f.name for f in pq.read_schema(RAW)}
    missing = [c for c in READ_COLS if c not in schema_cols]
    if missing:
        _abort(f"required columns absent from raw extract: {missing}")
    df = pq.read_table(RAW, columns=READ_COLS).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df["sic_int"] = pd.to_numeric(df["sic"], errors="coerce")
    for c in ("atq", "saleq", "prccq", "cshoq", "mkvaltq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def probe_guard(df: pd.DataFrame) -> None:
    """Verify the assumptions Step 1 depends on. Abort (do not auto-recover)
    if the extract is not in the expected canonical state."""
    print("PROBE / GUARD")
    for c, expected in (("indfmt", "INDL"), ("datafmt", "STD"), ("consol", "C")):
        vals = df[c].dropna().unique().tolist()
        print(f"  {c}: {vals}")
        if vals != [expected]:
            _abort(
                f"'{c}' is not single-valued '{expected}' (got {vals}). The "
                f"'duplicates excluded' filter would need real dedup logic; "
                f"refusing to silently drop_duplicates."
            )
    n_dup = int(df.duplicated(["gvkey", "datadate"]).sum())
    print(f"  (gvkey,datadate) duplicate rows: {n_dup}")
    if n_dup != 0:
        _abort(f"{n_dup} duplicate (gvkey,datadate) rows in a supposedly "
               f"canonical extract — investigate, do not paper over.")
    print("  GUARD PASSED — extract is canonical; dedup is a verified no-op.\n")


def build(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    waterfall: dict[str, int] = {}

    def mark(label: str, frame: pd.DataFrame) -> None:
        waterfall[label] = int(len(frame))
        print(f"  {label:<34s} {len(frame):>10,d}")

    print("WATERFALL  (Table C.1 order)")
    mark("raw_rows", df)

    df = df[(df["datadate"] >= WINDOW_START) & (df["datadate"] <= WINDOW_END)].copy()
    mark("window_2010Q1_2016Q4", df)

    # C.1 #1 — non-US drop (USD-reported, US HQ; dedup already guaranteed).
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA")].copy()
    mark("drop_non_us", df)
    if int(df.duplicated(["gvkey", "datadate"]).sum()) != 0:
        _abort("non-unique (gvkey,datadate) after US filter.")

    # C.1 #2 — negative fundamentals (ASSETS and SALES).
    df = df[~((df["atq"] < 0) | (df["saleq"] < 0))].copy()
    mark("drop_negative_fundamentals", df)

    # C.1 #3 — financials and utilities.
    is_fin = df["sic_int"].between(*FIN_SIC)
    is_util = df["sic_int"].between(*UTIL_SIC)
    df = df[~(is_fin | is_util)].copy()
    mark("drop_financials_utilities", df)

    # C.1 #4 — ASSETS or MARKET_CAP < $10M.  mktcap = prccq * cshoq.
    df["mktcap"] = df["prccq"] * df["cshoq"]
    df = df[(df["atq"] >= SIZE_THRESHOLD) & (df["mktcap"] >= SIZE_THRESHOLD)].copy()
    mark("drop_size_under_10m", df)

    print("\n  HARD STOP — Table C.1 filters #5 (missing key vars) and #6 "
          "(>=12 consecutive quarters) require constructed controls + panel "
          "structure. They are LATER steps, not implemented here.\n")

    q = ((df["datadate"].dt.month - 1) // 3 + 1).astype(int)
    df["cal_yr_qtr"] = df["datadate"].dt.year * 10 + q  # 2016Q3 -> 20163

    keep = [
        "gvkey", "datadate", "cal_yr_qtr", "sic", "sic_int",
        "atq", "saleq", "prccq", "cshoq", "mktcap",
        "loc", "curcdq", "fic", "indfmt", "datafmt", "consol",
    ]
    out = df[keep].sort_values(["gvkey", "datadate"]).reset_index(drop=True)
    return out, waterfall


def main() -> None:
    print(f"Campello replication — STEP 1 sample construction\nraw: {RAW}\n")
    df = load_raw()
    probe_guard(df)
    out, waterfall = build(df)

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    pq_path = out_dir / "sample.parquet"
    out.to_parquet(pq_path, index=False)

    metadata = {
        "step": "1 — sample construction (Campello 2022 JFQA §IV.B + Table C.1)",
        "raw_input": str(RAW),
        "window": [str(WINDOW_START.date()), str(WINDOW_END.date())],
        "filters_applied": {
            "us_firm_quarter": "curcdq=='USD' AND loc=='USA' (dedup = verified no-op)",
            "negative_fundamentals": "drop atq<0 OR saleq<0",
            "financials_utilities": f"drop SIC in {FIN_SIC} or {UTIL_SIC}",
            "size_10m": f"keep atq>={SIZE_THRESHOLD} AND mktcap>={SIZE_THRESHOLD}; "
                        f"mktcap=prccq*cshoq ($millions)",
        },
        "filters_deferred_to_later_steps": [
            "C.1 #5 missing key vars (needs INVESTMENT/TOBIN_Q/CASH_FLOW/...)",
            "C.1 #6 >=12 consecutive quarters (needs panel structure)",
        ],
        "waterfall_f1d": waterfall,
        "output_rows": int(len(out)),
        "output_firms": int(out["gvkey"].nunique()),
    }
    (out_dir / "metadata.json").write_text(json.dumps(metadata, indent=2))

    print("RESULT")
    print(f"  rows : {len(out):,}  firms : {out['gvkey'].nunique():,}")
    print(f"  -> {pq_path}")
    print(f"  -> {out_dir / 'metadata.json'}")


if __name__ == "__main__":
    main()
