"""DIAG — step7 sensitivity: does swapping CONSENSUS (builder z-score →
SUE) flip the cash δ̂ sign? (2026-05-18, Sina-authorized "go test it").

Question: SUE matched Campello's CONSENSUS summary stats (§G.4) — does
adopting it as the eq-(14) consensus control change the headline cash
δ̂ (currently −0.0073 NS, Campello +0.231***)?

Design (one variable isolated): import step7's OWN helpers (no code
drift), rebuild the exact step7 panel, merge BOTH consensus series —
cons_z (BrexitConsensusEPSBuilder, builder z-score, what step7 uses)
and cons_sue (IBES statsum snap_q (ACTUAL−MEANEST)/STDEV, best §G.4
match) — then fit the SAME PanelOLS on the SAME common sample (rows
non-null for CASH+controls+BOTH consensus). Only the consensus
definition differs ⇒ Δδ̂ is purely attributable to the swap.

Prior (evidence-based, stated before running): CONSENSUS is 1 of 6
controls; §D binding constraint = βᵁᴷ-tercile; §F.2 showed the larger
DV lever moved δ̂ only −0.033→−0.007. Expect NO sign flip. Firm
evidence adjudicates. NO builder/spec change; NO commit; NO verdict
(gated). Read-only diagnostic.
"""
from __future__ import annotations

import importlib.util
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

# import step7 module by path (reuse its exact helpers — no duplication)
_s7p = Path(__file__).resolve().parent / "step7_fullpanel_hypothesis.py"
_spec = importlib.util.spec_from_file_location("_step7", _s7p)
s7 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(s7)

from f1d.shared.variables.brexit_consensus_eps import (
    _load_cusip_to_gvkey_map, _load_ticker_to_gvkey_map, _timevar_lookup,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ZIP = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"


def _sue_statsum() -> pd.DataFrame:
    """IBES statsum SUE = (ACTUAL−MEANEST)/STDEV, snap_q (~90d), the
    best §G.4 Campello-shape match. Returns gvkey,cal_yr_qtr,cons_sue."""
    zf = zipfile.ZipFile(ZIP)
    mem = zf.namelist()[0]
    use = ["CUSIP", "OFTIC", "TICKER", "STATPERS", "MEASURE", "FISCALP",
           "FPI", "CURCODE", "MEANEST", "STDEV", "USFIRM", "FPEDATS",
           "ACTUAL"]
    with zf.open(mem) as fh:
        df = pd.read_csv(fh, usecols=use, low_memory=False)
    df = df[(df["MEASURE"] == "EPS") & (df["FISCALP"] == "QTR") &
            (pd.to_numeric(df["FPI"], errors="coerce") == 6) &
            (df["CURCODE"] == "USD") &
            (pd.to_numeric(df["USFIRM"], errors="coerce") == 1)].copy()
    df["fpe"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df["sp"] = pd.to_datetime(df["STATPERS"], errors="coerce")
    df = df.dropna(subset=["fpe", "sp"])
    for c in ("MEANEST", "STDEV", "ACTUAL"):
        df[c] = pd.to_numeric(df[c], errors="coerce")
    df["horizon"] = (df["fpe"] - df["sp"]).dt.days
    df = df[df["horizon"] >= 0].copy()
    df["cusip8"] = df["CUSIP"].astype(str).str.zfill(8).str[:8]
    df["cusip8"] = df["cusip8"].where(
        ~df["cusip8"].isin(["00000000", "nan", "NaN", "None", ""]))
    df["oftic_up"] = df["OFTIC"].astype(str).str.upper().str.strip()
    df["ticker_up"] = df["TICKER"].astype(str).str.upper().str.strip()
    cu = _load_cusip_to_gvkey_map(ROOT)
    tk = _load_ticker_to_gvkey_map(ROOT)
    gc = _timevar_lookup(df, "cusip8", cu, "cusip8", date_col="fpe")
    go = _timevar_lookup(df, "oftic_up", tk, "tic", date_col="fpe")
    gt = _timevar_lookup(df, "ticker_up", tk, "tic", date_col="fpe")
    df["gvkey"] = gc.fillna(go).fillna(gt)
    df = df.dropna(subset=["gvkey", "MEANEST", "ACTUAL"]).copy()
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["fpe"].dt.year * 10
                        + df["fpe"].dt.quarter).astype("int64")
    d = df.assign(_d=(df["horizon"] - 90).abs())
    idx = d.groupby(["gvkey", "fpe"], observed=True)["_d"].idxmin()
    s = df.loc[idx].copy()
    sd = s["STDEV"].where(s["STDEV"] > 0)
    s["cons_sue"] = (s["ACTUAL"] - s["MEANEST"]) / sd
    s = s.dropna(subset=["cons_sue"])
    return (s[["gvkey", "cal_yr_qtr", "cons_sue"]]
            .sort_values(["gvkey", "cal_yr_qtr"], kind="stable")
            .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))


def _fit(pdat, cols):
    from linearmodels.panel import PanelOLS
    r = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                 other_effects=pdat["indqtr_code"], drop_absorbed=True
                 ).fit(cov_type="clustered", cluster_entity=True,
                       cluster_time=True)
    k = "POST_x_HIGH"
    return (float(r.params[k]), float(r.std_errors[k]), float(r.tstats[k]),
            float(r.pvalues[k]), int(r.nobs), float(r.rsquared_within))


def main() -> None:
    print("=== DIAG — step7 CONSENSUS swap sensitivity (z-score → SUE) "
          "===\n")
    from f1d.shared.variables.brexit_consensus_eps import (
        BrexitConsensusEPSBuilder)

    s1 = pd.read_parquet(s7._latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(s7._latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"]
             & trt["group"].isin(["treated", "control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)

    panel = s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(s7.POST_Q).astype(int)
    df = panel.merge(s7._cash_dv(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in s7.FIRM_BUILDERS:
        b = s7._build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(s7._calendar_lag1(b, col),
                      on=["gvkey", "cal_yr_qtr"], how="left")
        firm_cols.append(col)
    df = df.merge(s7._calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}),
        on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    # consensus A: builder z-score (what step7 uses)
    cz = s7._build("BrexitConsensusEPSBuilder")
    cz = (cz.sort_values(["gvkey", "cal_yr_qtr"], kind="stable")
            .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))
    zc = [c for c in cz.columns if c not in ("gvkey", "cal_yr_qtr")][0]
    df = df.merge(cz.rename(columns={zc: "cons_z"}),
                  on=["gvkey", "cal_yr_qtr"], how="left")
    # consensus B: IBES statsum SUE (best §G.4 match)
    df = df.merge(_sue_statsum(), on=["gvkey", "cal_yr_qtr"], how="left")

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(s7.WINSOR), s.quantile(1 - s7.WINSOR)))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    base = ["POST_x_HIGH"] + firm_cols
    # COMMON sample: rows valid for CASH + controls + BOTH consensus
    common = df.dropna(subset=["CASH", "indqtr_code"] + base
                       + ["cons_z", "cons_sue"]).copy()
    pdat = common.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    print(f"common sample (CASH ∩ controls ∩ BOTH consensus): "
          f"{len(common):,} fq / {common['gvkey'].nunique():,} firms\n")

    bz = _fit(pdat, base + ["cons_z"])
    bs = _fit(pdat, base + ["cons_sue"])
    print("  consensus = builder z-score (step7 baseline):")
    print(f"    δ̂ {bz[0]:+.5f}  SE {bz[1]:.5f}  t {bz[2]:+.3f}  "
          f"p {bz[3]:.4f}  N {bz[4]:,}  R²w {bz[5]:.4f}")
    print("  consensus = IBES statsum SUE (best §G.4 match):")
    print(f"    δ̂ {bs[0]:+.5f}  SE {bs[1]:.5f}  t {bs[2]:+.3f}  "
          f"p {bs[3]:.4f}  N {bs[4]:,}  R²w {bs[5]:.4f}")
    print(f"\n  Δδ̂ (SUE − z) = {bs[0]-bz[0]:+.6f}")
    print(f"  Campello Table 8: +0.231*** ; sign flip to + & sig? "
          f"{'YES' if bs[0] > 0 and bs[3] < 0.10 else 'NO'}")
    print("\n[Sensitivity diagnostic only — no builder/spec change, no "
          "commit, no replication verdict (gated on Sina).]")


if __name__ == "__main__":
    main()
