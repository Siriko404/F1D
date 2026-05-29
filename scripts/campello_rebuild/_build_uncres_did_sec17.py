"""UncResCEO DV × §1+7 TEXTUAL treatment — eq-(14) (Sina 2026-05-18).

"do uncres for textual sec1and7 also": the UncResCEO arm under the
textual-search treatment (10-K Item1+7, >5/0) instead of βᵁᴷ-tercile.
Parallels step9 (UncResCEO×βᵁᴷ); only the treatment assignment
differs, so CASH§1+7 (step7b3) vs UncRes§1+7 (this) differ ONLY in DV.

Reuse, no drift:
  - DV: step9_uncres_did._uncres_dv  (ClarityResidualEngine + H1 bridge;
        mean per gvkey×cal_yr_qtr; NOT winsorized — pre-cleaned residual)
  - treatment: step3b3_textual_treatment_sec17 (latest) — >5 treated /
        ==0 control, 9-kw verbatim, 10-K Item1+7 scope
  - canonical eq-(14): step7 helpers (panel/POST/controls/FE) +
        §G.8 ratified statsum-MEANEST-z consensus (same stack as the
        CASH textual arm). NB: step9 (UncRes×βᵁᴷ, table col) uses the
        OLD Detail-z consensus; the difference is IMMATERIAL to δ̂
        (§G.6: ~0.0005) — noted, not silently mixed.

No Campello benchmark (Table 8 = CASH/NWC/PROFITS) — novel extension.
Output: outputs/campello_rebuild/step9b_uncres_textual_sec17/<ts>/.
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

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from step7_fullpanel_hypothesis import (  # canonical helpers, no drift
    FIRM_BUILDERS, POST_Q, _build, _calendar_lag1, _latest,
)
from step9_uncres_did import _uncres_dv          # reuse DV builder

_p = Path(__file__).resolve().parent / "_build_final_did_statsum_consensus.py"
_s = importlib.util.spec_from_file_location("_fin", _p)
_fin = importlib.util.module_from_spec(_s)
_s.loader.exec_module(_fin)
_statsum_meanest_z = _fin._statsum_meanest_z     # §G.8 ratified consensus

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

OUTB = ROOT / "outputs" / "campello_rebuild" / "step9b_uncres_textual_sec17"


def main() -> None:
    print("=== UncResCEO DV × §1+7 TEXTUAL treatment — eq-(14) ===\n")
    from linearmodels.panel import PanelOLS

    s1 = pd.read_parquet(_latest("step1_sample") / "sample.parquet",
                         columns=["gvkey", "cal_yr_qtr", "atq",
                                  "fic100_industry_id"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)

    s3b = _latest("step3b3_textual_treatment_sec17")
    tt = pd.read_parquet(s3b / "treatment_textual.parquet")
    tt["gvkey"] = tt["gvkey"].astype(str).str.zfill(6)
    tt = tt[tt["group"].isin(["treated", "control"])].copy()
    tt["HIGH_UK_EXPOSURE"] = (tt["group"] == "treated").astype(int)
    print(f"§1+7 textual treatment: {len(tt):,} firms "
          f"(T={int((tt.HIGH_UK_EXPOSURE==1).sum()):,}, "
          f"C={int((tt.HIGH_UK_EXPOSURE==0).sum()):,})  src={s3b.name}")

    panel = s1.merge(tt[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey",
                     how="inner")
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)

    dv = _uncres_dv()                              # gvkey,cal_yr_qtr,UNCRES
    print(f"UncResCEO DV (mean/firm-qtr, NOT winsorized): {len(dv):,} fq")
    df = panel.merge(dv, on=["gvkey", "cal_yr_qtr"], how="inner")
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
                  how="left")                      # §G.8 consensus

    # NO winsorization of UNCRES (pre-cleaned residual; step9 convention)
    df["POST_x_HIGH"] = (df["POST"] * df["HIGH_UK_EXPOSURE"]).astype(float)
    df["indqtr_code"] = ((df["fic100_industry_id"].astype("int64").astype(str)
                          + "_" + df["cal_yr_qtr"].astype(str))
                         .astype("category").cat.codes)

    cols = ["POST_x_HIGH"] + firm_cols + ["cons_fwd"]
    sub = df.dropna(subset=["UNCRES", "indqtr_code"] + cols).copy()
    pdat = sub.set_index(["gvkey", "cal_yr_qtr"]).sort_index()
    nf = sub["gvkey"].nunique()
    print(f"estimation sample (panel ∩ UncResCEO ∩ controls): "
          f"{len(sub):,} fq / {nf:,} firms")

    res = PanelOLS(pdat["UNCRES"], pdat[cols], entity_effects=True,
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
    print(f"\n  δ̂(POST·HIGH_textual§1+7, DV=UncResCEO) = {b:+.5f}  "
          f"SE {se:.5f}  t {t:+.3f}  p {p:.4f}  N {int(res.nobs):,}  "
          f"firms {nf:,}  R²w {float(res.rsquared_within):.4f}")
    print("  [No Campello benchmark for UncResCEO — novel extension; "
          "no verdict (gated).]")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    od = OUTB / ts
    od.mkdir(parents=True, exist_ok=True)
    sub[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE", "UNCRES"]
        + cols].to_parquet(od / "uncres_panel.parquet", index=False)
    (od / "summary.json").write_text(json.dumps({
        "dv": "UncResCEO (DWZ Eq.4 CEO Q&A call-level residual); mean "
              "per (gvkey,cal_yr_qtr); NOT winsorized",
        "treatment": "§1+7-scoped textual >5/0 (step3b3 " + s3b.name
                     + "); 9-kw verbatim, 10-K Item1+7 scope",
        "model": "eq-14 PanelOLS canonical (step7 helpers) + §G.8 "
                 "statsum-MEANEST-z consensus; FIRM FE + "
                 "INDUSTRY(FIC100)xQUARTER FE; SE double-clustered "
                 "firm x cal-qtr. NB consensus=statsum-z (vs step9 "
                 "UncRes×βᵁᴷ Detail-z; immaterial §G.6 ~0.0005).",
        "results": [{
            "tag": "UNCRES_TEXTUAL_SEC17",
            "delta_hat": b, "se": se, "t": t, "pvalue": p,
            "nobs": int(res.nobs), "n_firms": int(nf),
            "rsquared_within": float(res.rsquared_within),
            "controls": cols, "coefficients": coefs,
            "consensus_variant": "cons_fwd",
        }],
        "campello_reference": None,
        "campello_note": "Campello Table 8 has NO UncResCEO benchmark "
                         "(CASH/NWC/PROFITS only) — novel extension; "
                         "no verdict (gated on Sina)",
        "verdict_gated_on_sina": True,
    }, indent=2), encoding="utf-8")
    print(f"\nwritten → {od}")


if __name__ == "__main__":
    main()
