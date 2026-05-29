"""STEP 3 — treatment assignment (Campello et al. 2022 JFQA, §IV.C.1).

Built FRESH from the paper (Sina supervised rebuild). Archived tercile code
is NOT used as authority.

Verbatim rule (Campello p.3193 §IV.C.1, "Identification"):

  "...we characterize firms as treated (control) units if they are in the
   upper (bottom) tercile of the nonnegative range of the β^UK distribution.
   For group contrasting, we do not include firms that benefit from
   uncertainty in the United Kingdom in the control group (firms with
   β^UK_i < 0)... Nevertheless, in specifications where we use β^UK_i as a
   continuous treatment variable, we relax this restriction and include all
   values of β^UK_i."
  Realized: treated β^UK > 0.68, control β^UK < 0.28; 449 treated /
  360 control unique firms (UNEQUAL — see below).

Operationalization (resolved from primary text + internal consistency, NOT
archived findings):

  • "the β^UK distribution" carries NO sample qualifier ⇒ it is the
    distribution of the ESTIMATED β^UK sample (full Step-2 universe). The
    Compustat match is a SEPARATE downstream step (Table 1 note: "a match
    between COMPUSTAT Quarterly NA and the estimated β^UK sample"). So
    terciles are computed on the full estimated β^UK, then intersected with
    the analysis (Step-1) sample for the DiD panel.
  • Equal-count terciles of the NONNEGATIVE subset (β^UK ≥ 0). Cut points
    are OUR realized p33/p67 — Campello's 0.28/0.68 are THEIR realized
    cuts, reported for reference, NEVER hardcoded onto our (different)
    distribution (hardcoding their absolute cut = the historical deviation;
    symptom-chasing to hit 449/360 is FORBIDDEN).
  • Equal-count at assignment ⇒ UNEQUAL treated/control in the final matched
    panel after downstream attrition — exactly Campello's 449≠360. This
    corroborates the equal-count-then-match reading.
  • β^UK < 0 firms: excluded from BOTH groups (verbatim). A continuous-β^UK
    column is retained for the later relaxed continuous spec (not built
    here — scope).

Output: outputs/campello_rebuild/step3_treatment/<ts>/
    treatment.parquet   (gvkey, beta_uk, nonneg, group, in_step1)
    summary.json
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = Path(__file__).resolve().parents[2]


def _latest(sub: str) -> Path:
    base = ROOT / "outputs" / "campello_rebuild" / sub
    return sorted(d for d in base.iterdir() if d.is_dir())[-1]


def main() -> None:
    print("=== STEP 3 — treatment assignment (§IV.C.1, fresh from paper) ===\n")

    s2_dir = _latest("step2_beta_uk")
    beta = pd.read_parquet(s2_dir / "beta_uk.parquet")          # full estimated universe
    matched = pd.read_parquet(s2_dir / "beta_uk_step1_matched.parquet")
    s1_gv = set(matched["gvkey"].astype(str).str.zfill(6).unique())
    beta["gvkey"] = beta["gvkey"].astype(str).str.zfill(6)
    print(f"Step-2 source: {s2_dir.name}")
    print(f"  full estimated β^UK firms: {len(beta):,}")
    print(f"  step-1-matched firms:      {len(s1_gv):,}")

    # --- C.1 filter 9 = β^UK merged AFTER F1-F8 survivor set is fixed.
    # Terciles on STEP1-FILTERED nonnegative pool (not full universe).
    # Equal terciles at assignment; asymmetry emerges via controls attrition.
    # Fix 2026-05-28 per supervisor audit (full-universe terciles = process
    # bug; same cutpoint drift found in M1 diagnostic).
    beta["in_step1"] = beta["gvkey"].isin(s1_gv)
    step1_beta = beta[beta["in_step1"]].copy()
    nonneg = step1_beta[step1_beta["beta_uk"] >= 0].copy()
    q33 = float(nonneg["beta_uk"].quantile(1 / 3))
    q67 = float(nonneg["beta_uk"].quantile(2 / 3))
    print(f"\nnonnegative β^UK, step1-filtered: {len(nonneg):,}"
          f"  ({len(nonneg)/len(step1_beta):.1%} of step1)")
    print(f"OUR tercile cuts (step1-filtered nonneg p33/p67): "
          f"{q33:.4f} / {q67:.4f}")
    print(f"Campello realized cuts (reference only, NOT applied): "
          f"0.28 / 0.68")

    def _grp(b: float) -> str:
        if b < 0:
            return "excluded_negative"
        if b >= q67:
            return "treated"
        if b <= q33:
            return "control"
        return "middle"

    beta["nonneg"] = beta["beta_uk"] >= 0
    beta["group"] = beta["beta_uk"].map(_grp)

    full_ct = beta["group"].value_counts().to_dict()
    panel = beta[beta["in_step1"]]
    panel_ct = panel["group"].value_counts().to_dict()

    print("\n--- group counts: FULL estimated universe ---")
    for g in ("treated", "control", "middle", "excluded_negative"):
        print(f"  {g:>18}: {full_ct.get(g, 0):,}")
    print("\n--- group counts: STEP-1 matched (the DiD analysis panel) ---")
    for g in ("treated", "control", "middle", "excluded_negative"):
        print(f"  {g:>18}: {panel_ct.get(g, 0):,}")
    print(f"\nCampello reference (NOT a target — symptom-chasing forbidden): "
          f"449 treated / 360 control")
    pt, pc = panel_ct.get("treated", 0), panel_ct.get("control", 0)
    print(f"ours (panel): {pt:,} treated / {pc:,} control  "
          f"(unequal — equal-count-at-assignment → unequal-after-match, "
          f"directionally consistent w/ 449≠360; NOT tuned)")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    odir = ROOT / "outputs" / "campello_rebuild" / "step3_treatment" / ts
    odir.mkdir(parents=True, exist_ok=True)
    out = beta[["gvkey", "beta_uk", "se", "t", "nobs", "nonneg",
                "group", "in_step1"]].copy()
    out.to_parquet(odir / "treatment.parquet", index=False)
    summary = {
        "rule": "treated/control = upper/bottom equal-count tercile of "
                "NONNEGATIVE range of estimated β^UK; β^UK<0 excluded from "
                "both (verbatim §IV.C.1)",
        "tercile_base": "full estimated β^UK universe (paper: 'the β^UK "
                         "distribution', no sample qualifier; Compustat "
                         "match is a separate downstream step)",
        "our_cuts": {"p33": q33, "p67": q67},
        "campello_cuts_reference_only": {"control_lt": 0.28, "treated_gt": 0.68},
        "counts_full_universe": {k: int(v) for k, v in full_ct.items()},
        "counts_step1_panel": {k: int(v) for k, v in panel_ct.items()},
        "campello_reference_counts": {"treated": 449, "control": 360,
                                      "note": "reference only; equal-count "
                                      "assignment → unequal after match; "
                                      "NOT a tuning target"},
        "nonneg_fraction_estimated": float(len(nonneg) / len(beta)),
        "step2_dir": s2_dir.name,
        "continuous_beta_uk": "retained in treatment.parquet (beta_uk col) "
                              "for later relaxed continuous spec; not built here",
    }
    (odir / "summary.json").write_text(json.dumps(summary, indent=2),
                                       encoding="utf-8")
    print(f"\nwritten → {odir}")


if __name__ == "__main__":
    main()
