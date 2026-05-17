"""Campello et al. (2022 JFQA) supervised rebuild — STEP 1: sample construction.

From-scratch. Implements Supplementary Table C.1 sample-selection waterfall
VERBATIM, in the stated order. Filters 1-8 only; filters 9 (missing βᵁᴷ)
and 10 (missing CRSP & I/B/E/S controls) are DEFERRED downstream
(strict-sequential: βᵁᴷ does not exist until Step 2; control completeness
until controls are assembled). Step-1 terminal = filter 8.

Verbatim Table C.1 (firm-quarter counts):
    1  Raw COMPUSTAT 2010:Q1-2016:Q4 .......................... 262,412
    2  Drop non-US (USD, US HQ, duplicates excluded) .......... 160,254
    3  Drop negative fundamentals (ASSETS and SALES) .......... 158,312
    4  Drop financials and utilities .......................... 112,939
    5  Drop if ASSETS or MARKET_CAP < $10M .................... 93,011
    6  Drop if missing key vars (INVESTMENT, ASSETS,
       CASH_FLOW, TOBIN_Q, SALES_GROWTH) ..................... 75,013
    7  Drop if non-consecutive quarters, or <12 quarters ...... 56,081
    8  Drop if missing Hoberg-Phillips (2016) FIC-100 ......... 49,107
    9  Drop if missing βᵁᴷ ................. 43,025  [DEFERRED -> Step 2]
    10 Drop if missing CRSP & I/B/E/S ...... 41,630  [DEFERRED -> controls]

Operationalization (verbatim + Sina-ratified where the paper is silent):
  * Input: inputs/comp_na_daily_all (Compustat NA Quarterly). This is
    NORTH AMERICA (US+Canada); the raw 2010Q1-2016Q4 NA count (~321,853)
    will exceed Campello's US-raw 262,412 — KNOWN extract-vintage gap,
    NOT a bug. Meaningful target tracking starts at filter 2.
  * Filter 2 "duplicates excluded": canonical Compustat screen
    consol=='C' & indfmt=='INDL' & datafmt=='STD' (popsrc ABSENT in this
    extract — loc=='USA' already enforces domestic) + 1 row per
    (gvkey, cal_yr_qtr) keep-last-by-datadate. [Sina 2026-05-17]
  * Filter 3: drop atq<0 OR saleq<0.
  * Filter 4: SIC financials 6000-6999 / utilities 4900-4999, header
    `sic` (`sich` ABSENT in this extract).
  * Filter 5: ASSETS=atq ($M); MARKET_CAP=prccq*cshoq ($M); drop if
    either < 10.
  * Filter 6 key-var construction (verbatim Table 1 note):
      INVESTMENT   = capx_q / atq_{t-1}   (capx_q de-cumulated from YTD
                     `capxy` within gvkey×fyearq — `capxq` ABSENT;
                     standard Compustat practice, data-availability dev.)
      ASSETS       = atq
      CASH_FLOW    = oibdpq / atq_{t-1}
      TOBIN_Q      = (cshoq*prccq + atq - ceqq + txditcq)/atq  — STRICT:
                     all 5 components required (Sina 2026-05-17, no
                     impute-0).
      SALES_GROWTH = (saleq - saleq_{t-4})/saleq_{t-4}  (YoY)
    Lags atq_{t-1}, saleq_{t-4} via calendar-prev merge (NOT row-shift),
    drawn from a 2008Q1+ load buffer so 2010Q1 is not a boundary
    artifact. Drop the in-window firm-qtr if ANY of the 5 is missing.
  * Filter 7: keep firm iff it has an unbroken run of >=12 consecutive
    calendar quarters in the surviving panel. [Sina 2026-05-17]
  * Filter 8: inner-join Hoberg-Phillips FIC-100 by (gvkey, year).

Output:
    outputs/campello_rebuild/step1_sample/<ts>/sample.parquet
    outputs/campello_rebuild/step1_sample/<ts>/metadata.json

Run:  python scripts/campello_rebuild/step1_sample.py
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

try:  # Windows cp1252 console can't encode Δ / βᵁᴷ glyphs
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
OUT_BASE = ROOT / "outputs" / "campello_rebuild" / "step1_sample"

WIN_LO, WIN_HI = 20101, 20164          # 2010Q1 .. 2016Q4 (in-window)
BUFFER_LO = pd.Timestamp("2008-01-01")  # load buffer for saleq_{t-4}/atq_{t-1}
WIN_HI_DATE = pd.Timestamp("2016-12-31")

# Verbatim Table C.1 targets (firm-quarters).
TARGETS = {
    1: 262_412, 2: 160_254, 3: 158_312, 4: 112_939, 5: 93_011,
    6: 75_013, 7: 56_081, 8: 49_107, 9: 43_025, 10: 41_630,
}


def _abort(msg: str) -> None:
    print(f"\nABORT — {msg}")
    sys.exit(1)


def _yq(s: pd.Series) -> pd.Series:
    return s.dt.year * 10 + s.dt.quarter


def _prev_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr - 1) * 10 + 4 if q == 1 else yr * 10 + (q - 1)


def _prev_yr_q(yq: int) -> int:
    return (yq // 10 - 1) * 10 + (yq % 10)


def _line(step: int, label: str, n: int, prev: int | None) -> None:
    tgt = TARGETS[step]
    d = "" if prev is None else f"  Δ {n - prev:+,}"
    print(f"  {step:>2}. {label:<46s} {n:>10,}  [Campello {tgt:>9,}]"
          f"{d}  ({n - tgt:+,} vs target)")


def main() -> None:
    print("Campello supervised rebuild — STEP 1  sample construction\n")
    if not COMP.exists():
        _abort(f"missing input: {COMP}")

    cols = ["gvkey", "datadate", "fyearq", "fqtr", "curcdq", "loc",
            "consol", "indfmt", "datafmt", "sic", "atq", "saleq",
            "capxy", "oibdpq", "ceqq", "txditcq", "prccq", "cshoq"]
    df = pq.read_table(COMP, columns=cols).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)].copy()
    for c in ["atq", "saleq", "capxy", "oibdpq", "ceqq", "txditcq",
              "prccq", "cshoq", "fyearq", "fqtr"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = _yq(df["datadate"]).astype("int64")
    df["sic"] = pd.to_numeric(df["sic"], errors="coerce")

    inwin = lambda d: d[(d["cal_yr_qtr"] >= WIN_LO) & (d["cal_yr_qtr"] <= WIN_HI)]

    print("WATERFALL (counts = in-window firm-quarters 2010Q1-2016Q4)\n")

    # --- 1. Raw COMPUSTAT 2010Q1-2016Q4 (pre-screen, in-window) ---------
    iw = inwin(df)
    n1 = len(iw)
    _line(1, "Raw COMPUSTAT 2010Q1-2016Q4", n1, None)
    print(f"      nunique(gvkey,cal_yr_qtr)={iw.duplicated(['gvkey','cal_yr_qtr']).pipe(lambda s: len(iw)-s.sum()):,}"
          f"  (raw rows {n1:,}; NA-source — US-raw target {TARGETS[1]:,}, "
          f"extract-vintage gap expected, track from filter 2)")

    # --- 2. Drop non-US: USD + US HQ + canonical screen + dedup --------
    scr = df[(df["curcdq"] == "USD") & (df["loc"] == "USA")
             & (df["consol"] == "C") & (df["indfmt"] == "INDL")
             & (df["datafmt"] == "STD")].copy()
    scr = scr.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    scr = scr.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last").reset_index(drop=True)
    n2 = len(inwin(scr))
    _line(2, "Drop non-US (USD/US HQ/canon/dedup)", n2, n1)

    # Calendar lags on the screened+deduped buffered frame.
    base = scr[["gvkey", "cal_yr_qtr", "atq", "saleq"]].copy()
    atq_lag = base.assign(_t=base["cal_yr_qtr"].map(_prev_q).astype("int64"))
    atq_lag = atq_lag[["gvkey", "_t", "atq"]].rename(
        columns={"_t": "cal_yr_qtr", "atq": "atq_lag1"})
    sal_lag = base.assign(_t=base["cal_yr_qtr"].map(_prev_yr_q).astype("int64"))
    sal_lag = sal_lag[["gvkey", "_t", "saleq"]].rename(
        columns={"_t": "cal_yr_qtr", "saleq": "saleq_lag4"})
    scr = scr.merge(atq_lag, on=["gvkey", "cal_yr_qtr"], how="left")
    scr = scr.merge(sal_lag, on=["gvkey", "cal_yr_qtr"], how="left")

    # Quarterly capex from YTD capxy (de-cumulate within gvkey x fiscal yr).
    scr = scr.sort_values(["gvkey", "fyearq", "fqtr"], kind="stable")
    prev_capxy = scr.groupby(["gvkey", "fyearq"])["capxy"].shift(1)
    scr["capx_q"] = np.where(scr["fqtr"] == 1, scr["capxy"],
                             scr["capxy"] - prev_capxy)

    # From here filters operate on the IN-WINDOW rows (lags carried in).
    s = inwin(scr).copy()

    # --- 3. Drop negative fundamentals (ASSETS and SALES) -------------
    s = s[~((s["atq"] < 0) | (s["saleq"] < 0))]
    n3 = len(s); _line(3, "Drop negative ASSETS/SALES", n3, n2)

    # --- 4. Drop financials (6000-6999) and utilities (4900-4999) -----
    s = s[~(s["sic"].between(6000, 6999) | s["sic"].between(4900, 4999))]
    n4 = len(s); _line(4, "Drop financials & utilities", n4, n3)

    # --- 5. Drop if ASSETS or MARKET_CAP < $10M ----------------------
    s["mktcap"] = s["prccq"] * s["cshoq"]
    s = s[~((s["atq"] < 10) | (s["mktcap"] < 10))]
    n5 = len(s); _line(5, "Drop ASSETS/MKTCAP < $10M", n5, n4)

    # --- 6. Drop if missing key vars ---------------------------------
    has_inv = s["capx_q"].notna() & (s["atq_lag1"] > 0)
    has_ast = s["atq"].notna()
    has_cf = s["oibdpq"].notna() & (s["atq_lag1"] > 0)
    has_tq = (s["cshoq"].notna() & s["prccq"].notna() & s["atq"].notna()
              & s["ceqq"].notna() & s["txditcq"].notna() & (s["atq"] > 0))
    has_sg = s["saleq"].notna() & s["saleq_lag4"].notna() & (s["saleq_lag4"] != 0)
    keep6 = has_inv & has_ast & has_cf & has_tq & has_sg
    drop_by = {
        "INVESTMENT": int((~has_inv).sum()), "ASSETS": int((~has_ast).sum()),
        "CASH_FLOW": int((~has_cf).sum()), "TOBIN_Q(strict)": int((~has_tq).sum()),
        "SALES_GROWTH": int((~has_sg).sum()),
    }
    s = s[keep6]
    n6 = len(s); _line(6, "Drop missing key vars", n6, n5)
    print(f"      key-var missingness (non-exclusive): {drop_by}")

    # --- 7. Non-consecutive / <12 quarters: unbroken >=12 run --------
    def _longest_run(qs: list[int]) -> int:
        qs = sorted(set(qs)); best = run = 1
        for i in range(1, len(qs)):
            run = run + 1 if qs[i] == _next_q(qs[i - 1]) else 1
            best = max(best, run)
        return best if qs else 0
    runs = s.groupby("gvkey")["cal_yr_qtr"].apply(lambda x: _longest_run(list(x)))
    keep_g = set(runs[runs >= 12].index)
    s = s[s["gvkey"].isin(keep_g)]
    n7 = len(s); _line(7, "Drop non-consec / <12 qtrs", n7, n6)

    # --- 8. Drop if missing Hoberg-Phillips FIC-100 ------------------
    from f1d.shared.variables.hoberg_phillips_fic100 import HobergPhillipsFIC100Builder
    fic = HobergPhillipsFIC100Builder().build(range(2010, 2017), root_path=ROOT).data
    fic = fic.copy()
    fic["gvkey"] = fic["gvkey"].astype(str).str.zfill(6)
    s["year"] = (s["cal_yr_qtr"] // 10).astype("int64")
    fic["year"] = fic["year"].astype("int64")
    s = s.merge(fic[["gvkey", "year", "fic100_industry_id"]],
                on=["gvkey", "year"], how="inner")
    n8 = len(s); _line(8, "Drop missing HP FIC-100", n8, n7)

    print(f"\n  9-10 DEFERRED (strict-sequential): βᵁᴷ -> Step 2 "
          f"[Campello {TARGETS[9]:,}];  CRSP&I/B/E/S -> controls "
          f"[Campello {TARGETS[10]:,}]")
    print(f"\n  STEP-1 TERMINAL = filter 8: {n8:,} firm-qtrs / "
          f"{s['gvkey'].nunique():,} firms")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = OUT_BASE / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    keep_cols = ["gvkey", "cal_yr_qtr", "datadate", "fyearq", "fqtr",
                 "atq", "atq_lag1", "saleq", "saleq_lag4", "capx_q",
                 "oibdpq", "ceqq", "txditcq", "prccq", "cshoq", "sic",
                 "mktcap", "fic100_industry_id"]
    s[keep_cols].to_parquet(out_dir / "sample.parquet", index=False)
    meta = {
        "step": "1 — sample construction (Campello 2022 Supp. Table C.1)",
        "input": str(COMP),
        "counts_vs_targets": {
            str(k): {"ours": v, "campello": TARGETS[k]} for k, v in
            {1: n1, 2: n2, 3: n3, 4: n4, 5: n5, 6: n6, 7: n7, 8: n8}.items()
        },
        "filter6_keyvar_missingness": drop_by,
        "terminal": {"filter": 8, "firm_quarters": n8,
                     "firms": int(s["gvkey"].nunique())},
        "deferred": {"9_betaUK": "Step 2", "10_crsp_ibes": "controls"},
        "deviations": [
            "comp_na_daily_all = North America (US+Canada); raw filter-1 "
            "count exceeds Campello US-raw 262,412 (extract vintage)",
            "popsrc absent -> canonical screen = consol/indfmt/datafmt only",
            "sich absent -> SIC exclusion uses header sic",
            "capxq absent -> quarterly capex de-cumulated from YTD capxy",
            "TOBIN_Q strict: all 5 components required, no impute-0 (Sina)",
        ],
    }
    (out_dir / "metadata.json").write_text(json.dumps(meta, indent=2))
    print(f"\n  -> {out_dir / 'sample.parquet'}")
    print(f"  -> {out_dir / 'metadata.json'}")


def _next_q(yq: int) -> int:
    yr, q = yq // 10, yq % 10
    return (yr + 1) * 10 + 1 if q == 4 else yr * 10 + (q + 1)


if __name__ == "__main__":
    main()
