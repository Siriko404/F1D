"""TEXTUAL-arm eq-(14) DiD — Campello §IV.A.2 alternative treatment.

Sina-authorized 2026-05-18 ("go for the textual arm"; words kept;
D3 unmapped deferred). Parallel column to the canonical βᵁᴷ CASH
result: SAME eq-(14) (full sample-period panel, POST 2016Q3-Q4,
CASH=cheq/(atq_{t-1}−cheq_{t-1}) Table-8 net-of-cash, 5 firm controls lagged 1Q,
CONSENSUS=statsum MEANEST winsor→z §G.8/§G.9, FIRM FE +
INDUSTRY(FIC100)×QTR FE, SE double-clustered firm×qtr) — ONLY the
treatment assignment changes: step3 βᵁᴷ-tercile → step3b textual
(absolute >5 treated / ==0 control, Campello verbatim, NOT terciles).

Imports step7 + the §G.8 statsum consensus helpers directly (no code
drift). Writes a step7-schema summary.json into
outputs/campello_rebuild/step7b_textual_did/<ts>/ for the generator.
Campello col benchmark = Table 8 col.2 (textual CASH) δ̂ +0.357***
SE 0.062 N 24,195 R² 0.24 (programmatic table8_pdfpage31 L298-308).
No commit; no verdict (gated); off-ramp forbidden.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from step7_fullpanel_hypothesis import (  # exact canonical helpers
    FIRM_BUILDERS, POST_Q, WINSOR, _build, _calendar_lag1, _latest, _prev_q,
)

COMP = ROOT / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"
BUFFER_LO = pd.Timestamp("2008-01-01")
WIN_HI_DATE = pd.Timestamp("2016-12-31")


def _cash_dv_t8() -> pd.DataFrame:
    """T8 net-of-cash CASH: cheq_t / (atq_{t-1} - cheq_{t-1})."""
    df = pq.read_table(COMP, columns=["gvkey","datadate","curcdq","loc",
                       "consol","indfmt","datafmt","atq","cheq"]).to_pandas()
    df["datadate"] = pd.to_datetime(df["datadate"], errors="coerce")
    df = df[(df["datadate"]>=BUFFER_LO)&(df["datadate"]<=WIN_HI_DATE)]
    df = df[(df["curcdq"]=="USD")&(df["loc"]=="USA")&(df["consol"]=="C")
            &(df["indfmt"]=="INDL")&(df["datafmt"]=="STD")].copy()
    for c in ("atq","cheq"): df[c] = pd.to_numeric(df[c], errors="coerce")
    df["gvkey"] = df["gvkey"].astype("int64").astype(str).str.zfill(6)
    df["cal_yr_qtr"] = (df["datadate"].dt.year*10+df["datadate"].dt.quarter).astype("int64")
    df = df.sort_values(["gvkey","cal_yr_qtr","datadate"], kind="stable")
    df = df.drop_duplicates(["gvkey","cal_yr_qtr"], keep="last")
    src = df[["gvkey","cal_yr_qtr","atq","cheq"]].rename(
        columns={"cal_yr_qtr":"_pq","atq":"atq_l1","cheq":"cheq_l1"})
    df["_pq"] = df["cal_yr_qtr"].map(_prev_q).astype("int64")
    df = df.merge(src, on=["gvkey","_pq"], how="left").drop(columns="_pq")
    df["denom"] = df["atq_l1"] - df["cheq_l1"]
    df = df[df["cheq"].notna()&(df["denom"]>0)].copy()
    df["CASH"] = df["cheq"]/df["denom"]
    return df[["gvkey","cal_yr_qtr","CASH"]]

# reuse the §G.8 ratified statsum-MEANEST-z consensus (single source)
_p = Path(__file__).resolve().parent / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

STEP7B = ROOT / "outputs" / "campello_rebuild" / "step7b_textual_did"


def main() -> None:
    print("=== TEXTUAL-arm eq-(14) DiD (treatment = step3b >5/0) ===\n")
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    # TREATMENT = step3b textual (NOT step3 βᵁᴷ tercile)
    s3b = _latest("step3b_textual_treatment")
    tt = pd.read_parquet(s3b / "treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated", "control"])].copy()
    tt["HIGH_UK_EXPOSURE"] = (tt["group"] == "treated").astype(int)
    print(f"step3b textual treatment: {len(tt):,} firms "
          f"(T={int((tt.HIGH_UK_EXPOSURE==1).sum()):,}, "
          f"C={int((tt.HIGH_UK_EXPOSURE==0).sum()):,})  src={s3b.name}")

    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    df = panel.merge(_cash_dv_t8(), on=["gvkey", "cal_yr_qtr"], how="inner")
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

    df = df.merge(_statsum_meanest_z(), on=["gvkey", "cal_yr_qtr"],
                  how="left")            # §G.8 ratified consensus

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
    print(f"estimation sample: {len(sub):,} fq / {nf:,} firms")

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
    print(f"\n  δ̂(POST·HIGH_textual) = {b:+.5f}  SE {se:.5f}  "
          f"t {t:+.3f}  p {p:.4f}  N {int(res.nobs):,}  firms {nf:,}  "
          f"R²w {float(res.rsquared_within):.4f}")
    print(f"  Campello Table 8 col.2 (textual CASH): +0.357*** "
          f"SE 0.062 N 24,195 R² 0.24")

    prev = json.loads((_latest("step7_fullpanel_hypothesis")
                       / "summary.json").read_text(encoding="utf-8"))
    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    od = STEP7B / ts
    od.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "CASH"]
        + cols].to_parquet(od / "fullpanel.parquet", index=False)
    (od / "summary.json").write_text(json.dumps({
        "hypothesis": "eq-14 textual-treatment arm (Campello §IV.A.2): "
            "treatment = 2015 10-K Brexit-word count >5 (treated) / "
            "==0 (control), Campello verbatim absolute rule (NOT "
            "terciles). Same canonical eq-(14) otherwise.",
        "model": prev["model"] + "  | TREATMENT = textual >5/0 "
            "(step3b, Sina 2026-05-18; words kept verbatim, D3 "
            "unmapped deferred)",
        "cash_dv_definition": "CASH = cheq_t / (atq_{t-1} - cheq_{t-1}) — "
            "Table-8 net-of-cash (Campello Table 8 caption; Sina-ratified "
            "2026-05-28, supersedes step7 T1-dv which gives dead δ≈0)",
        "cash_dv_tex": r"$cheq_t/(atq_{t-1} - cheq_{t-1})$ (Table-8 "
            "net-of-cash, patched 2026-05-28; T1 dv dead for textual arm)",
        "treatment_definition": "TEXTUAL: 2015 10-K count of 9 "
            "Campello keywords; >5 treated / ==0 control / 1-5 "
            "excluded (verbatim §IV.A.2; step3b " + s3b.name + "). "
            "Documented deviation: treated 3,037 vs Campello 807, "
            "control 278 vs 433 (word-breadth gap; verdict gated).",
        "results": [{
            "tag": "TEXTUAL_FULL_PANEL",
            "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(nf),
            "rsquared_within": float(res.rsquared_within),
            "controls": cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd",
        }],
        "campello_reference": {
            "cash_delta": 0.357, "se": 0.062, "n": 24195,
            "rsquared": 0.24, "stars": "***",
            "source": "Campello et al. 2022 JFQA Table 8 col.2 "
                "(textual CASH, POST×HIGH_10K_ENTRIES; programmatic "
                "table8_pdfpage31.txt L298-308)",
            "note": "reference only; NOT a tuning target; no "
                "replication verdict (gated)"},
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {od}")


if __name__ == "__main__":
    main()
