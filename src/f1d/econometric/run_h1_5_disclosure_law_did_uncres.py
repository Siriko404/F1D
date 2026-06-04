#!/usr/bin/env python3
"""
================================================================================
STAGE 4b: H1.5 Boasiako Disclosure Law DiD on UncResCEO — canonical spec only
================================================================================
ID: econometric/run_h1_5_disclosure_law_did_uncres
Description: CLONE of run_h1_5_disclosure_law_did.py canonical spec
             (industry+state+year FE, state-clustered SE, 11 controls + IndCFVol),
             DV = UncResCEO_c instead of CASH. Novel extension — no Boasiako
             benchmark exists for speech uncertainty.

             Reuses assemble_panel() and _fit_one() from the CASH runner
             (no code duplication). Single column output.

Outputs:
    - outputs/econometric/h1_5_disclosure_law_did_uncres/<timestamp>/suite_spec_*.json
================================================================================
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src"))

from run_h1_5_disclosure_law_did import (
    assemble_panel, _fit_one, KEY_IV, ALL_CONTROLS, CLUSTERING,
    SUITE_ID as _CASH_SUITE_ID,
)

SUITE_ID = "H1.5.disclosure_law_did_uncres"
SUITE_DIR_NAME = "h1_5_disclosure_law_did_uncres"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def main() -> int:
    print("=" * 64)
    print("H1.5 — Boasiako Disclosure Law DiD on UncResCEO (canonical spec)")
    print("=" * 64)

    panel = assemble_panel(ROOT)
    # Drop rows where UncResCEO_c is missing (speech coverage < cash coverage)
    speech = panel.dropna(subset=["UncResCEO_c"]).copy()
    print(f"\n  Speech panel: {len(speech):,} firm-years / "
          f"{speech['gvkey'].nunique():,} firms")

    # Canonical spec: industry+state+year FE
    fe = "industry_state_year"
    result, meta = _fit_one(
        speech, dv="UncResCEO_c",
        treatment_terms=[KEY_IV],
        extra_controls=ALL_CONTROLS,
        fe=fe,
    )

    if result is None:
        print(f"FIT FAILED: {meta.get('skipped', 'unknown')}")
        return 1

    headline = result.params.get(KEY_IV, np.nan)
    headline_se = result.std_errors.get(KEY_IV, np.nan)
    headline_t = result.tstats.get(KEY_IV, np.nan)
    p_two = result.pvalues.get(KEY_IV, np.nan)
    p_one = p_two / 2 if not np.isnan(p_two) else np.nan

    print(f"\n  Disclosure_Law on UncResCEO_c:")
    print(f"    beta={float(headline):+.4f}  SE={float(headline_se):.4f}  "
          f"t={float(headline_t):+.3f}  p_two={float(p_two):.4f}  "
          f"p_one={float(p_one):.4f}")
    print(f"    N={meta['n_obs']:,}  R²={meta.get('r2', np.nan):.4f}")

    # Build coefs dict
    coefs: Dict[str, Any] = {}
    for var in result.params.index:
        coefs[var] = {
            "beta": float(result.params[var]),
            "se": float(result.std_errors[var]),
            "p_two": float(result.pvalues[var]),
            "p_one": float(result.pvalues[var]) / 2,
        }

    # Build suite_spec (single column)
    suite_spec = {
        "schema_version": "1.0",
        "suite_id": SUITE_ID,
        "dir_name": SUITE_DIR_NAME,
        "title": (
            "Boasiako Disclosure Law DiD on CEO Speech Uncertainty — "
            "canonical industry+state+year FE (novel extension)"
        ),
        "caption": (
            "Disclosure-Law DiD: CEO Speech Uncertainty (UncResCEO). "
            "Canonical industry+state+year FE, state-clustered SE."
        ),
        "label": "tab:h1_5_disclosure_law_did_uncres",
        "sample_label": "Boasiako 1997-2015 annual, speech-coverage subset",
        "model_family": "PanelOLS",
        "suite_type": "DiD",
        "clustering": "state",
        "tail": "one-tailed (beta>0 — precautionary speech)",
        "ivs": [KEY_IV],
        "controls": ALL_CONTROLS,
        "header_rows": [],
        "columns": [{
            "col": 1,
            "dv": "UncResCEO_c",
            "dv_label": "CEO Speech Uncertainty (UncResCEO, centered)",
            "fe_entity": "industry",
            "fe_time": "year+state_dummies",
            "control_vars": ALL_CONTROLS,
            "n_obs": int(meta["n_obs"]),
            "n_firms": meta.get("n_firms"),
            "r2": meta.get("r2", 0.0),
            "adj_r2": meta.get("adj_r2"),
            "dv_mean": meta.get("dv_mean"),
            "cluster_fallback": None,
            "indicator_rows": [],
            "coefs": coefs,
        }],
        "render_hints": {},
    }

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = ROOT / "outputs" / "econometric" / SUITE_DIR_NAME / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    spec_name = f"suite_spec_{SUITE_ID}.json"
    (out_dir / spec_name).write_text(json.dumps(suite_spec, indent=2), encoding="utf-8")
    print(f"\n-> {out_dir / spec_name}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
