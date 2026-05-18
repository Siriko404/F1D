"""STEP 4 — timeline / DiD window (Campello et al. 2022 JFQA, §IV.C.2 + eq-14).

Built FRESH from the paper (Sina supervised rebuild). Archived timeline code
is NOT used as authority; the verbatim primary text governs.

Verbatim (Campello §IV.C, Sina-pasted 2026-05-17):

  "Differences over the 2016:Q3–Q4 period are taken relative to the same two
   quarters in the previous year (2015:Q3–Q4) in order to minimize the impact
   of seasonal effects. This is equivalent to estimating the following model:
       Y_{i,t} = α + δ[POST_t·HIGH_UK_EXPOSURE_i] + θ·CONTROLS_{i,t-1}
                 + Σ_i FIRM_i + Σ_j Σ_t INDUSTRY_j×QUARTER_t + ε_{i,t}   (14)
   ... POST_t equals 1 if the time period is in the 2016:Q3–Q4 window."

⇒ Baseline DiD = 4 calendar quarters {2015Q3, 2015Q4, 2016Q3, 2016Q4}.
  POST = 1 for 2016Q3/Q4, 0 for 2015Q3/Q4. The "same two quarters in the
  previous year" seasonal rationale is only coherent for a 4-quarter design;
  a continuous 2010–2016 panel would not need it. Primary text governs
  (locked process) — any archived "full-panel" view is superseded by this
  verbatim. (Table 12 alternative windows = robustness, NOT baseline; not
  built — scope.)

  HIGH_UK_EXPOSURE_i = 1 iff firm ∈ top tercile of β^UK (Step-3 `treated`);
  0 = Step-3 `control` (bottom tercile of nonnegative range). Middle tercile
  and β^UK<0 firms are NOT in the baseline 2×2 (continuous spec only, later).

This step assembles ONLY the calendar frame + POST + treatment dummy on the
Step-1 firm-quarter panel. Controls/DV = Step 6; estimator = Step 5.

Output: outputs/campello_rebuild/step4_timeline/<ts>/
    panel.parquet   (gvkey, cal_yr_qtr, POST, HIGH_UK_EXPOSURE)
    summary.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]

PRE_Q = [20153, 20154]   # 2015Q3, 2015Q4  (cal_yr_qtr = year*10 + quarter)
POST_Q = [20163, 20164]  # 2016Q3, 2016Q4
WINDOW_Q = PRE_Q + POST_Q


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def main() -> None:
    print("=== STEP 4 — timeline / DiD window (§IV.C.2 + eq-14, fresh) ===\n")

    s1_dir = _latest("step1_sample")
    s3_dir = _latest("step3_treatment")
    s1 = pd.read_parquet(s1_dir / "sample.parquet", columns=["gvkey", "cal_yr_qtr"])
    s1["gvkey"] = s1["gvkey"].astype(str).str.zfill(6)
    trt = pd.read_parquet(s3_dir / "treatment.parquet",
                          columns=["gvkey", "group", "in_step1"])
    trt["gvkey"] = trt["gvkey"].astype(str).str.zfill(6)
    print(f"Step-1 source: {s1_dir.name}  ({len(s1):,} fq, "
          f"{s1['gvkey'].nunique():,} firms)")
    print(f"Step-3 source: {s3_dir.name}")

    # --- DIAGNOSTIC: is the 4-quarter window actually populated? --------
    s1_q = s1["cal_yr_qtr"].value_counts().sort_index()
    print("\nStep-1 firm-quarter counts at the 4 DiD quarters "
          "(verify populated — no paper-over):")
    for q in WINDOW_Q:
        tag = "POST" if q in POST_Q else "PRE "
        print(f"  {q}  [{tag}]: {int(s1_q.get(q, 0)):,} fq")
    max_q = int(s1["cal_yr_qtr"].max())
    print(f"  (Step-1 cal_yr_qtr range: {int(s1['cal_yr_qtr'].min())} – {max_q})")
    if max_q < max(POST_Q):
        print(f"  *** WARNING: Step-1 sample ends at {max_q} < {max(POST_Q)} "
              f"— POST quarters NOT covered. Surfacing, not papering over. ***")

    # --- baseline 2×2 firm set: treated vs control ---------------------
    tc = trt[trt["in_step1"] & trt["group"].isin(["treated", "control"])].copy()
    tc["HIGH_UK_EXPOSURE"] = (tc["group"] == "treated").astype(int)
    print(f"\nBaseline 2×2 firms (Step-3 treated/control ∩ step-1): "
          f"{len(tc):,}  "
          f"(treated={int((tc['HIGH_UK_EXPOSURE']==1).sum()):,}, "
          f"control={int((tc['HIGH_UK_EXPOSURE']==0).sum()):,})")

    # --- assemble panel: step-1 fq ∩ 4 quarters ∩ treated/control ------
    panel = s1[s1["cal_yr_qtr"].isin(WINDOW_Q)].merge(
        tc[["gvkey", "HIGH_UK_EXPOSURE"]], on="gvkey", how="inner"
    )
    panel["POST"] = panel["cal_yr_qtr"].isin(POST_Q).astype(int)
    panel = panel[["gvkey", "cal_yr_qtr", "POST", "HIGH_UK_EXPOSURE"]] \
        .sort_values(["gvkey", "cal_yr_qtr"]).reset_index(drop=True)

    # --- 2×2 cell counts + balance ------------------------------------
    print("\n--- DiD 2×2 firm-quarter counts ---")
    cell = panel.groupby(["POST", "HIGH_UK_EXPOSURE"]).size().unstack(fill_value=0)
    print(cell.rename(index={0: "PRE(2015Q3-4)", 1: "POST(2016Q3-4)"},
                      columns={0: "control", 1: "treated"}).to_string())

    fq_per_firm = panel.groupby("gvkey")["cal_yr_qtr"].nunique()
    balanced = int((fq_per_firm == 4).sum())
    print(f"\nfirms in panel: {panel['gvkey'].nunique():,}; "
          f"firm-quarters: {len(panel):,}")
    print(f"balanced firms (all 4 quarters present): {balanced:,} "
          f"({balanced/panel['gvkey'].nunique():.1%}) — "
          f"unbalanced is expected (firm FE handles it; Campello uses "
          f"unbalanced panel).")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step4_timeline" / ts
    odir.mkdir(parents=True, exist_ok=True)
    panel.to_parquet(odir / "panel.parquet", index=False)
    summary = {
        "window": {"PRE": PRE_Q, "POST": POST_Q,
                   "encoding": "cal_yr_qtr = year*10 + quarter"},
        "rule": "verbatim §IV.C: DiD 2016Q3-Q4 vs 2015Q3-Q4 (seasonal "
                "control); POST=1 in 2016Q3-Q4; HIGH_UK_EXPOSURE=1 iff "
                "Step-3 treated (top β^UK tercile), 0=control",
        "primary_text_governs": "4-quarter baseline resolved from verbatim; "
                                "archived full-panel view superseded",
        "baseline_2x2_firms": {
            "treated": int((tc["HIGH_UK_EXPOSURE"] == 1).sum()),
            "control": int((tc["HIGH_UK_EXPOSURE"] == 0).sum())},
        "panel_firms": int(panel["gvkey"].nunique()),
        "panel_firm_quarters": int(len(panel)),
        "balanced_firms_4q": balanced,
        "cell_counts": {f"POST{p}_HIGH{h}": int(
            ((panel["POST"] == p) & (panel["HIGH_UK_EXPOSURE"] == h)).sum())
            for p in (0, 1) for h in (0, 1)},
        "step1_dir": s1_dir.name, "step3_dir": s3_dir.name,
        "step1_quarter_range": [int(s1["cal_yr_qtr"].min()),
                                int(s1["cal_yr_qtr"].max())],
    }
    (odir / "summary.json").write_text(json.dumps(summary, indent=2),
                                       encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
