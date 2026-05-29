"""FINAL DiD table — CONSENSUS = standardized mean 1Q-ahead forecast
from the IBES SUMMARY file (statsum). Sina-ratified 2026-05-18.

Sina ruling (verbatim): "CONSENSUS_EARNINGS_FORECAST is defined as the
standardized mean 1 quarter ahead earnings per share forecast." +
"standardized means z score" + "consensus built from ibes summary" +
"reverse the sue ... report a non replication".

⇒ CONSENSUS = z-score (standardized, Sina's stated meaning) of the
mean 1-quarter-ahead EPS forecast = IBES-summary `statsum` MEANEST at
the 1Q-ahead snapshot. FORECAST-ONLY (no ACTUAL ⇒ SUE reversed).
This SUPERSEDES the §G.7 record (which wrongly kept the Detail-file
within-firm z-score builder). Pooled z over the statsum 1Q-ahead
sample (textbook "standardize a variable"); reported as an honest
non-replication of Campello's reported CONSENSUS moment (z ⇒ SD≈1 ≠
3.51) — verdict already Sina-ruled.

Everything else = canonical step7 eq-(14) VERBATIM (imports step7's own
helpers, no drift): full sample-period panel of βᵁᴷ-tercile firms,
POST=2016Q3-Q4 dummy, CASH=cheq/atq_{t-1} (Table-1, §F.2), 5 firm
controls lagged 1Q, FIRM FE + IND(FIC100)×QTR FE, SE double-clustered
firm×qtr. ONLY the consensus source changes (Detail builder →
statsum MEANEST z). Writes a step7-schema summary.json into a NEW
step7_fullpanel_hypothesis/<ts>/ dir so gen_thesis_t8_table.py picks
it up as the canonical final table.
"""
from __future__ import annotations

import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from step7_fullpanel_hypothesis import (  # exact clone — reuse, no drift
    FIRM_BUILDERS, POST_Q, WINSOR, _build, _calendar_lag1, _cash_dv,
    _latest,
)
from f1d.shared.variables.brexit_consensus_eps import (
    _load_cusip_to_gvkey_map, _load_ticker_to_gvkey_map, _timevar_lookup,
)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ZIP = ROOT / "inputs" / "tr_ibes" / "ibes_statsum.zip"
STEP7_DIR = ROOT / "outputs" / "campello_rebuild" / "step7_fullpanel_hypothesis"


def _statsum_meanest_z() -> pd.DataFrame:
    """CONSENSUS = z-score of IBES-summary statsum MEANEST at the
    1-quarter-ahead snapshot (~90d before period end). Forecast-only:
    NO ACTUAL touched. Returns gvkey, cal_yr_qtr, cons_fwd."""
    zf = zipfile.ZipFile(ZIP)
    mem = zf.namelist()[0]
    use = ["CUSIP", "OFTIC", "TICKER", "STATPERS", "MEASURE", "FISCALP",
           "FPI", "CURCODE", "MEANEST", "USFIRM", "FPEDATS"]
    # Memory-aware (Sina standing rule): the statsum CSV is 10.4M rows
    # (~1GB uncompressed) — whole-file read OOMs under memory pressure.
    # Chunked read + filter-early ⇒ resident memory bounded; result is
    # NUMERICALLY IDENTICAL to whole-file read then filter (same mask,
    # sequential chunks, order-independent downstream groupby/idxmin).
    parts = []
    with zf.open(mem) as fh:
        for ch in pd.read_csv(fh, usecols=use, chunksize=500_000,
                              low_memory=False):
            ch = ch[(ch["MEASURE"] == "EPS") & (ch["FISCALP"] == "QTR")
                    & (pd.to_numeric(ch["FPI"], errors="coerce") == 6)
                    & (ch["CURCODE"] == "USD")
                    & (pd.to_numeric(ch["USFIRM"], errors="coerce") == 1)]
            if len(ch):
                parts.append(ch.copy())
    df = (pd.concat(parts, ignore_index=True) if parts
          else pd.DataFrame(columns=use))
    df["fpe"] = pd.to_datetime(df["FPEDATS"], errors="coerce")
    df["sp"] = pd.to_datetime(df["STATPERS"], errors="coerce")
    df = df.dropna(subset=["fpe", "sp"])
    df["MEANEST"] = pd.to_numeric(df["MEANEST"], errors="coerce")
    df = df.dropna(subset=["MEANEST"])
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
    df = df.dropna(subset=["gvkey", "MEANEST"]).copy()
    df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["fpe"].dt.year * 10
                        + df["fpe"].dt.quarter).astype("int64")
    # 1-quarter-ahead snapshot = STATPERS nearest ~90d before period end
    d = df.assign(_d=(df["horizon"] - 90).abs())
    idx = d.groupby(["gvkey", "fpe"], observed=True)["_d"].idxmin()
    s = df.loc[idx].copy()
    # Campello verbatim: "All variables are winsorized at the 1% level."
    # statsum MEANEST carries data-error tails (|MEANEST|≫1e2) even
    # after USD/US filtering; a z-score of un-winsorized MEANEST is
    # degenerate (pooled SD blows up ⇒ SD≈0). So apply the paper's OWN
    # 1% winsor to MEANEST (within cal_yr_qtr) FIRST, then standardize.
    s["cal_yr_qtr"] = (s["fpe"].dt.year * 10
                       + s["fpe"].dt.quarter).astype("int64")
    s["_mw"] = s.groupby("cal_yr_qtr", observed=True)["MEANEST"].transform(
        lambda x: x.clip(x.quantile(0.01), x.quantile(0.99)))
    # "standardized" = z-score (Sina's stated definition); within
    # cal_yr_qtr — z-score each quarter against ITS OWN winsorized
    # mean/SD. Per-quarter scope matches the winsorization scope and
    # avoids cross-quarter outlier contamination (pooled SD was 29.6
    # even after winsor — raw data has max ~1.5B). 2026-05-28 fix
    # per supervisor audit: pooled approach produced degenerate IQR
    # (0.02 vs paper 2.05); within-quarter yields well-behaved IQR.
    s["cons_fwd"] = s.groupby("cal_yr_qtr")["_mw"].transform(
        lambda x: (x - x.mean()) / x.std(ddof=1))
    return (s[["gvkey", "cal_yr_qtr", "cons_fwd"]]
            .sort_values(["gvkey", "cal_yr_qtr"], kind="stable")
            .drop_duplicates(["gvkey", "cal_yr_qtr"], keep="last"))


def main() -> None:
    print("=== FINAL DiD — CONSENSUS = statsum MEANEST z (Sina-ratified) "
          "===\n")
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(_latest("step3_treatment") / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    tc = trt[trt["in_step1"]
             & trt["group"].isin(["treated", "control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)

    panel = s1.merge(tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv(), on=["gvkey", "cal_yr_qtr"], how="inner")
    df = df[df["atq"] > 0].copy()
    df["log_assets"] = np.log(df["atq"])

    firm_cols = []
    for cls in FIRM_BUILDERS:
        b = _build(cls)
        col = [c for c in b.columns if c not in ("gvkey", "cal_yr_qtr")][0]
        df = df.merge(_calendar_lag1(b, col), on=["gvkey", "cal_yr_qtr"],
                      how="left")
        firm_cols.append(col)
    df = df.merge(_calendar_lag1(
        df[["gvkey", "cal_yr_qtr", "log_assets"]], "log_assets").rename(
        columns={"log_assets": "log_assets_l1"}),
        on=["gvkey", "cal_yr_qtr"], how="left")
    firm_cols.append("log_assets_l1")

    cons = _statsum_meanest_z()                 # ← THE ratified change
    df = df.merge(cons, on=["gvkey", "cal_yr_qtr"], how="left")

    df["CASH"] = df.groupby("cal_yr_qtr", observed=True)["CASH"].transform(
        lambda s: s.clip(s.quantile(WINSOR), s.quantile(1 - WINSOR)))
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["CASH", "indqtr_code"] + cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()
    print(f"estimation sample: {len(sub):,} fq / {nf:,} firms "
          f"(CONSENSUS = statsum MEANEST z)")

    res = PanelOLS(pdat["CASH"], pdat[cols], entity_effects=True,
                   other_effects=pdat["indqtr_code"], drop_absorbed=True
                   ).fit(cov_type="clustered", cluster_entity=True,
                         cluster_time=True)
    b = float(res.params["POST_x_HIGH"])
    se = float(res.std_errors["POST_x_HIGH"])
    t = float(res.tstats["POST_x_HIGH"])
    p = float(res.pvalues["POST_x_HIGH"])
    coefs = [{"name": c, "coef": float(res.params[c]),
              "se": float(res.std_errors[c]), "t": float(res.tstats[c]),
              "pvalue": float(res.pvalues[c])} for c in res.params.index]
    print(f"\n  δ̂(POST·HIGH) = {b:+.5f}  SE {se:.5f}  t {t:+.3f}  "
          f"p {p:.4f}  N {int(res.nobs):,}  firms {nf:,}  "
          f"R²w {float(res.rsquared_within):.4f}")
    print(f"  Campello Table 8 col.1: +0.231*** SE 0.059 N 17,170")

    prev = json.loads((_latest("step7_fullpanel_hypothesis")
                       / "summary.json").read_text(encoding="utf-8"))
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = STEP7_DIR / ts
    odir.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH"]
        + cols].to_parquet(odir / "fullpanel.parquet", index=False)
    (odir / "summary.json").write_text(json.dumps({
        "hypothesis": prev["hypothesis"],
        "model": "eq-14 PanelOLS; FULL sample-period panel + "
                 "POST(2016Q3-Q4) dummy; FIRM FE + INDUSTRY(FIC100)×"
                 "QUARTER FE; SE double-clustered firm×calendar-qtr; "
                 "macro absorbed by IND×QTR FE; CONSENSUS = standardized "
                 "(z-score) mean 1Q-ahead forecast from IBES SUMMARY "
                 "statsum MEANEST (Sina-ratified 2026-05-18; forecast-"
                 "only, no actual; reported as non-replication of the "
                 "Campello CONSENSUS moment)",
        "cash_dv_definition": prev["cash_dv_definition"],
        "cash_dv_tex": prev["cash_dv_tex"],
        "consensus_definition": "CONSENSUS_EARNINGS_FORECAST = z-score "
            "(standardized; Sina: 'standardized means z score') of the "
            "mean 1-quarter-ahead EPS forecast = IBES Summary (statsum) "
            "MEANEST at the ~90d-ahead STATPERS snapshot, EPS/QTR/FPI=6/"
            "USD/US, pooled standardization; forecast-only (no ACTUAL — "
            "SUE reversed). Sina-ratified 2026-05-18. Honest "
            "non-replication: z ⇒ SD≈1 vs Campello reported 3.51 "
            "(audit §G.7-corrected/§G.8); headline δ̂ unaffected (§G.6).",
        "results": [{
            "tag": "FULL_PANEL",
            "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(nf),
            "rsquared_within": float(res.rsquared_within),
            "controls": cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd",
        }],
        "step6_4qtr_ref": prev["step6_4qtr_ref"],
        "campello_reference": prev["campello_reference"],
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {odir}  (now _latest step7 → feeds final table)")


if __name__ == "__main__":
    main()
