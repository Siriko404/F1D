"""NWC isolating test (auditor note #3).

Campello Table 8 cols 3-4: NON_CASH_WORKING_CAPITAL = "working capital (net of
cash) divided by lagged total assets" (GROSS lagged denominator — identical in
Table 1 and Table 8, no G2 conflict). Targets: market -0.687*** (0.281),
textual -0.608*** (0.079).

NWC shares the SAME sample, controls, FE, SE, window, and winsorization as the
CASH regression. We swap ONLY the DV by monkeypatching the runner's
_cash_dv_t8 to return NWC in the 'CASH' column — every other line of
_build_and_fit (winsor, controls, FE, clustering) stays byte-identical.

NWC = (current assets - cash&STI - current liabilities) / lagged total assets
    = (actq - cheq - lctq) / atq_{t-1}    (gross lagged denom)

If NWC matches the paper while CASH undershoots -> miss is cash-DV-specific.
If NWC ALSO undershoots -> shared attenuation (scaling / winsor dim / controls).
Read-only on data.
"""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts" / "campello_rebuild"))

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

_rp = ROOT / "src" / "f1d" / "econometric" / "run_h1_5_brexit_did.py"
_rs = importlib.util.spec_from_file_location("_runner", _rp)
_runner = importlib.util.module_from_spec(_rs)
_rs.loader.exec_module(_runner)

from step7_fullpanel_hypothesis import _prev_q

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")


def _nwc_dv() -> pd.DataFrame:
    """NWC = (actq - cheq - lctq) / atq_{t-1}; column named 'CASH' for reuse."""
    df = pq.read_table(COMP, columns=["gvkey", "datadate", "curcdq", "loc",
                       "consol", "indfmt", "datafmt", "actq", "lctq",
                       "cheq", "atq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"] >= BUFFER_LO) & (df["datadate"] <= WIN_HI_DATE)]
    df = df[(df["curcdq"] == "USD") & (df["loc"] == "USA") & (df["consol"] == "C")
            & (df["indfmt"] == "INDL") & (df["datafmt"] == "STD")].copy()
    for c in ("actq", "lctq", "cheq", "atq"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year * 10
                        + df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey", "cal_yr_qtr", "datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last")
    src = df[["gvkey", "cal_yr_qtr", "atq"]].rename(
        columns={"cal_yr_qtr": "_pq", "atq": "atq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey", "_pq"], how="left").drop(columns="_pq")
    df = df[df["actq"].notna() & df["lctq"].notna() & df["cheq"].notna()
            & (df["atq_l1"] > 0)].copy()
    df["CASH"] = (df["actq"] - df["cheq"] - df["lctq"]) / df["atq_l1"]
    return df[["gvkey", "cal_yr_qtr", "CASH"]]


def main() -> None:
    # monkeypatch the DV — everything else in _build_and_fit unchanged
    _runner._cash_dv_t8 = _nwc_dv

    print("=" * 68)
    print("NWC ISOLATING TEST — shared machinery, DV swapped CASH->NWC")
    print("=" * 68)
    print("Campello Table 8: market -0.687*** (0.281) | textual -0.608*** (0.079)\n")

    mkt = _runner._load_market_treatment()
    txt = _runner._load_textual_treatment()

    print(f"{'arm':<22} {'δ̂(NWC)':>10} {'SE':>8} {'p':>8} {'N':>8}  target")
    print("-" * 68)
    r_m = _runner._build_and_fit(mkt, "NWC_market")
    print(f"{'MARKET (β^UK)':<22} {r_m['delta_hat']:>+10.4f} {r_m['se']:>8.4f} "
          f"{r_m['pvalue']:>8.4f} {r_m['nobs']:>8,}  -0.687***")
    r_t = _runner._build_and_fit(txt, "NWC_textual")
    print(f"{'TEXTUAL (§1+7)':<22} {r_t['delta_hat']:>+10.4f} {r_t['se']:>8.4f} "
          f"{r_t['pvalue']:>8.4f} {r_t['nobs']:>8,}  -0.608***")
    print("-" * 68)
    print("Read: NWC matches paper -> CASH miss is cash-DV-specific.")
    print("      NWC also misses -> shared attenuation (scaling/winsor/controls).")


if __name__ == "__main__":
    main()
