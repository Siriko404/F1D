"""STEP 3b — TEXTUAL-SEARCH treatment arm (Campello §IV.A.2, verbatim).

Sina-authorized 2026-05-18 ("go for the textual arm"). Parallel to
step3 (βᵁᴷ-tercile market-based treatment); this is Campello's
ALTERNATIVE treatment assignment for the SAME eq-(14) outcomes.

SPEC AUTHORITY = the paper, programmatically extracted (NOT the
archived implementation). Verbatim, campello_etal_2022_brexit_jfqa.pdf
PDF p.14 §IV.A.2 "Textual-Search-Based Measure of Uncertainty"
(tmp/campello_pdf_extract/buk_pdfpage14.txt L225-257):
  keywords (body L229): "Brexit", "Great Britain", "Uncertainty"
  fn 14 (L256-257) subsumed: "Referendum", "Uncertain",
    "United Kingdom", "UK", "U.K.", "G.B."  ⇒ 9 total.
  rule (L229-232 + p.16 L181-184): treated = >5 entries in 2015 10-K;
    control = 0 entries; 1-5 excluded (binary contrast).
  Campello realized: 807 treated / 433 control.

DATA-PLUMBING REFERENCE ONLY (not Campello authority; locked process):
the archived ETL `archive/.../scripts/brexit/parse_10k_keywords.py`
documented the non-obvious input mechanics — re-implemented fresh here,
not imported:
  * SRAF zip path: <yyyy>/QTRn/YYYYMMDD_TYPE_edgar_data_CIK_acc.txt
  * U.K./G.B. need lookbehind/lookahead (\\b fails at embedded dots)
  * CIK→gvkey via CCM time-varying window (rebuild convention:
    LINKPRIM∈{P,C} & LINKTYPE∈{LU,LC} — consistent with the other
    rebuild builders' 2026-05-14 'all 4 fixes'; archived used P-only,
    deviation noted in summary.json)
  * dedupe: latest filing_date per CIK (10-K/A amendments supersede)

KNOWN REPRODUCTION GAP (firm, archived diagnostic): a literal 9-word
tally over-counts (~2,847 treated vs 807) because "Uncertainty"/
"Uncertain" are generic; Campello's 807 implies an undisclosed
scoping constraint (proximity/Item-scope) the paper does NOT state.
We follow the verbatim spec and REPORT the gap (same documented-
deviation pattern as CONSENSUS/CASH; interpretive verdict Sina-gated).

Reads inputs/10-X_C_2015_10Konly.zip IN-PLACE (826 MB, ~9,275 filings;
streamed, ≤1 file resident — memory-aware per Sina standing rule).
Output: outputs/campello_rebuild/step3b_textual_treatment/<ts>/
  treatment_textual.parquet  [gvkey, total_count, group, HIGH_UK_EXPOSURE]
  summary.json
No spec change to other steps; no commit; no verdict (gated).
"""
from __future__ import annotations

import json
import re
import sys
import time
import zipfile
from datetime import datetime
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
ZIP = ROOT / "inputs" / "10-X_C_2015_10Konly.zip"
CCM = ROOT / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
OUTBASE = ROOT / "outputs" / "campello_rebuild" / "step3b_textual_treatment"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# Campello verbatim 9 keywords (buk_pdfpage14 L229 + fn14 L256-257).
PAT_WB = re.compile(
    r"\b(brexit|great britain|uncertainty|referendum|uncertain|"
    r"united kingdom|uk)\b", re.IGNORECASE)
PAT_ABBR = re.compile(r"(?<![A-Za-z])(u\.k\.|g\.b\.)(?![A-Za-z])",
                      re.IGNORECASE)
FNAME = re.compile(
    r"\d{4}/QTR\d/(\d{8})_([A-Z0-9-]+)_edgar_data_(\d+)_([A-Za-z0-9-]+)"
    r"\.txt")
HIGH_T, ZERO_T = 5, 0          # >5 treated, ==0 control (verbatim)
CAMPELLO = {"treated": 807, "control": 433}


def _count(text: str) -> int:
    return len(PAT_WB.findall(text)) + len(PAT_ABBR.findall(text))


def _load_ccm() -> pd.DataFrame:
    c = pd.read_parquet(CCM, columns=["gvkey", "cik", "LINKPRIM",
                                      "LINKTYPE", "LINKDT", "LINKENDDT"])
    c = c[c["LINKPRIM"].isin(["P", "C"])
          & c["LINKTYPE"].isin(["LU", "LC"])].copy()
    c["LINKDT"] = pd.to_datetime(c["LINKDT"], errors="coerce")
    c["LINKENDDT"] = pd.to_datetime(
        c["LINKENDDT"].astype(str).replace({"E": "2099-12-31"}),
        errors="coerce")
    c["cik"] = pd.to_numeric(c["cik"], errors="coerce")
    c = c.dropna(subset=["gvkey", "cik", "LINKDT", "LINKENDDT"])
    c["cik"] = c["cik"].astype("int64")
    c["gvkey"] = c["gvkey"].astype("int64").astype(str).str.zfill(6)
    return c[["gvkey", "cik", "LINKDT", "LINKENDDT"]]


def main() -> None:
    print("=== STEP 3b — TEXTUAL-SEARCH treatment (Campello §IV.A.2) ===\n")
    t0 = time.time()
    rows, n_dir, n_badname, n_decerr = [], 0, 0, 0
    with zipfile.ZipFile(ZIP, "r") as zf:
        infos = zf.infolist()
        print(f"zip entries: {len(infos):,}  (streaming, ≤1 resident)")
        for i, info in enumerate(infos, 1):
            if info.is_dir() or info.file_size == 0:
                n_dir += 1
                continue
            m = FNAME.match(info.filename)
            if not m:
                n_badname += 1
                continue
            date_str, ftype, cik, _acc = m.groups()
            try:
                with zf.open(info, "r") as f:
                    text = f.read().decode("utf-8", errors="replace")
            except Exception:
                n_decerr += 1
                continue
            tot = _count(text)
            del text
            rows.append({"filing_date": pd.to_datetime(date_str,
                         format="%Y%m%d"), "filing_type": ftype,
                         "cik": int(cik), "total_count": tot})
            if i % 1500 == 0:
                print(f"  …{i:,}/{len(infos):,} "
                      f"({time.time()-t0:.0f}s)")
    f = pd.DataFrame(rows)
    print(f"\nparsed {len(f):,} filings  (dirs {n_dir}, badname "
          f"{n_badname}, decode-err {n_decerr})  {time.time()-t0:.0f}s")

    # dedupe: latest filing per CIK (10-K/A amendments supersede)
    f = (f.sort_values(["cik", "filing_date"], kind="stable")
           .drop_duplicates("cik", keep="last"))
    print(f"after CIK dedupe (latest filing): {len(f):,} CIKs")

    # CIK → gvkey, time-varying window
    ccm = _load_ccm()
    mg = f.merge(ccm, on="cik", how="left")
    ok = ((mg["filing_date"] >= mg["LINKDT"])
          & (mg["filing_date"] <= mg["LINKENDDT"]))
    mp = (mg[ok].sort_values(["cik", "LINKDT"], kind="stable")
              .drop_duplicates("cik", keep="first"))
    n_unmapped = f["cik"].nunique() - mp["cik"].nunique()
    print(f"CIK→gvkey mapped: {mp['cik'].nunique():,}  "
          f"unmapped: {n_unmapped:,}")

    # firm-level exposure = sum of retained filings' counts per gvkey
    g = (mp.groupby("gvkey", as_index=False)["total_count"].sum())
    g["group"] = pd.cut(g["total_count"], bins=[-1, ZERO_T, HIGH_T,
                        10**12], labels=["control", "_excl", "treated"])
    g["group"] = g["group"].astype(str)
    g.loc[g["total_count"] == 0, "group"] = "control"
    g.loc[g["total_count"] > HIGH_T, "group"] = "treated"
    g.loc[(g["total_count"] >= 1) & (g["total_count"] <= HIGH_T),
          "group"] = "_excl"
    g["HIGH_UK_EXPOSURE"] = g["group"].map(
        {"treated": 1.0, "control": 0.0}).astype("float64")

    nt = int((g["group"] == "treated").sum())
    nc = int((g["group"] == "control").sum())
    nx = int((g["group"] == "_excl").sum())
    print(f"\n  treated (>5)  : {nt:,}   (Campello 807)")
    print(f"  control (==0) : {nc:,}   (Campello 433)")
    print(f"  excluded(1-5) : {nx:,}")
    print(f"  total firms   : {len(g):,}")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    od = OUTBASE / ts
    od.mkdir(parents=True, exist_ok=True)
    keep = g[g["group"].isin(["treated", "control"])][
        ["gvkey", "total_count", "group", "HIGH_UK_EXPOSURE"]]
    keep.to_parquet(od / "treatment_textual.parquet", index=False)
    (od / "summary.json").write_text(json.dumps({
        "step": "3b_textual_treatment",
        "spec_source": "campello_etal_2022_brexit_jfqa.pdf p.14 "
            "§IV.A.2 + fn14 (programmatic buk_pdfpage14.txt) — "
            "9 keywords; treated >5 / control 0 / 1-5 excluded",
        "keywords": ["Brexit", "Great Britain", "Uncertainty",
                     "Referendum", "Uncertain", "United Kingdom",
                     "UK", "U.K.", "G.B."],
        "data_plumbing_ref": "archive/.../parse_10k_keywords.py "
            "(reference only; fresh re-impl). CCM LINKPRIM∈{P,C} "
            "LINKTYPE∈{LU,LC} (rebuild convention; archived used "
            "P-only — noted deviation, data-plumbing not Campello spec)",
        "n_filings_parsed": int(len(f)),
        "n_ciks_after_dedupe": int(f["cik"].nunique()),
        "n_cik_mapped": int(mp["cik"].nunique()),
        "n_unmapped": int(n_unmapped),
        "treated": nt, "control": nc, "excluded_1_5": nx,
        "total_firms": int(len(g)),
        "campello_realized": CAMPELLO,
        "reproduction_gap_note": "literal 9-word tally over-counts vs "
            "Campello 807/433 (generic 'Uncertainty'/'Uncertain'); "
            "undisclosed scoping constraint in paper — documented "
            "deviation, verdict Sina-gated (cf. CONSENSUS/CASH).",
        "campello_t8_textual_cash_benchmark": {
            "delta_hat": 0.357, "se": 0.062, "n": 24195,
            "rsquared": 0.24, "stars": "***",
            "source": "Campello et al. 2022 JFQA Table 8 col.2 "
                "(POST×HIGH_10K_ENTRIES; programmatic "
                "table8_pdfpage31.txt L298-308)"},
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {od}")


if __name__ == "__main__":
    main()
