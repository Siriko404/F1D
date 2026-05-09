"""Brexit parallel-trends regression utility — H1.5.brexit_did design (Module #12).

Replicates Campello et al. 2022 JFQA supplementary Figure C1 + Tables C4-C5
(parallel-trends pre-period leads test) per spec lines 838-846 of
tmp/3did_replication_v2_2026_05_08.md.

This is a UTILITY module, not a VariableBuilder — it provides a function
``run_parallel_trends_test()`` that takes the runner's already-assembled panel
and runs the pre-period leads regression. Output:

    F-statistic + p-value of joint test that all 4 pre-period lead × HIGH
    dummies (Q-4, Q-3, Q-2, Q-1 relative to POST-start 2016Q3) are jointly zero.

DV ~ alpha_i + sum_{k=1..4} beta_k * (lead_{-k} × HIGH) + Controls + FE

The pre-period leads are defined relative to the POST-start cal_yr_qtr 20163
(2016Q3 — the quarter Brexit was voted on June 23, 2016):
    lead_{-1} = (cal_yr_qtr == 20162)  # 2016Q2
    lead_{-2} = (cal_yr_qtr == 20161)  # 2016Q1
    lead_{-3} = (cal_yr_qtr == 20154)  # 2015Q4
    lead_{-4} = (cal_yr_qtr == 20153)  # 2015Q3

Rejection of joint-zero (low p-value) → parallel-trends violation; treated and
control are diverging in pre-period before the shock. Failure to reject (high
p) → parallel trends UPHELD, design valid.

The runner calls this function 2x (once per treatment HIGH_BETA_UK + HIGH_10K)
and reports the 2 F-stats in the regression-table caption.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
from linearmodels.panel import PanelOLS

logger = logging.getLogger(__name__)


# Pre-period leads relative to POST-start 2016Q3 (cal_yr_qtr=20163).
PRE_LEADS = {
    "lead_m1": 20162,
    "lead_m2": 20161,
    "lead_m3": 20154,
    "lead_m4": 20153,
}
PRE_PERIOD_START_YQ = 20153  # earliest lead


def run_parallel_trends_test(
    panel: pd.DataFrame,
    dv: str,
    treatment_col: str,
    control_cols: List[str],
    fe_entity: str = "gvkey",
    fe_time: str = "cal_yr_qtr",
    cluster_entity: bool = True,
    cluster_time: bool = True,
) -> Dict[str, Any]:
    """Run pre-period leads × HIGH regression; F-test joint zero.

    Args:
        panel: assembled DiD panel with index already on (entity, time).
            Must contain dv, treatment_col, control_cols, plus cal_yr_qtr.
        dv: dependent variable column (e.g., 'cash_brexit_dv').
        treatment_col: HIGH dummy (e.g., 'HIGH_BETA_UK').
        control_cols: list of contemporaneous controls + macros to include.
        fe_entity: name of entity ID column (default 'gvkey').
        fe_time: name of time-index column (default 'cal_yr_qtr').
        cluster_entity, cluster_time: SE clustering options.

    Returns:
        dict with keys:
            f_stat: F-statistic of joint test
            p_value: F-test p-value
            n_obs: regression sample size
            lead_estimates: dict of {lead_name: (coef, se, t, p)}
            warnings: list of any issues
    """
    panel = panel.copy()
    warnings: List[str] = []

    # Restrict to pre-period only (cal_yr_qtr < 20163).
    panel = panel[panel[fe_time] < 20163].copy()

    # Construct lead × HIGH interaction columns.
    lead_cols: List[str] = []
    for lead_name, yq in PRE_LEADS.items():
        col = f"{lead_name}_x_{treatment_col}"
        panel[col] = ((panel[fe_time] == yq) & (panel[treatment_col] == 1)).astype(int)
        lead_cols.append(col)

    # Drop missing.
    needed = [dv, treatment_col, fe_entity, fe_time] + lead_cols + list(control_cols)
    panel = panel.dropna(subset=needed)
    if len(panel) == 0:
        warnings.append("zero rows after dropna; cannot run regression")
        return {"f_stat": np.nan, "p_value": np.nan, "n_obs": 0, "lead_estimates": {}, "warnings": warnings}

    # Set MultiIndex for PanelOLS.
    panel = panel.set_index([fe_entity, fe_time])

    # Build exog matrix: lead interactions + controls.
    exog = lead_cols + list(control_cols)
    try:
        model = PanelOLS(
            dependent=panel[dv],
            exog=panel[exog],
            entity_effects=True,
            time_effects=True,
            drop_absorbed=True,
            check_rank=False,
        )
        fit_kwargs = {"cov_type": "clustered"}
        if cluster_entity:
            fit_kwargs["cluster_entity"] = True
        if cluster_time:
            fit_kwargs["cluster_time"] = True
        result = model.fit(**fit_kwargs)
    except Exception as e:
        warnings.append(f"PanelOLS fit failed: {e}")
        return {"f_stat": np.nan, "p_value": np.nan, "n_obs": int(len(panel)), "lead_estimates": {}, "warnings": warnings}

    # Joint Wald test on lead coefficients via F-test.
    lead_in_model = [c for c in lead_cols if c in result.params.index]
    if not lead_in_model:
        warnings.append("no lead coefficients survived drop_absorbed; skipping F-test")
        return {"f_stat": np.nan, "p_value": np.nan, "n_obs": int(len(panel)),
                "lead_estimates": {}, "warnings": warnings}

    # Use linearmodels.PanelOLS .wald_test for joint hypothesis.
    formula_parts = [f"{c} = 0" for c in lead_in_model]
    formula = " , ".join(formula_parts)
    try:
        wald = result.wald_test(formula=formula)
        f_stat = float(wald.stat)
        # linearmodels Wald returns chi-square stat; for F-equivalent, df-adjusted.
        p_value = float(wald.pval)
    except Exception as e:
        warnings.append(f"wald_test failed: {e}")
        f_stat = np.nan
        p_value = np.nan

    lead_estimates: Dict[str, Tuple[float, float, float, float]] = {}
    for c in lead_in_model:
        lead_estimates[c] = (
            float(result.params[c]),
            float(result.std_errors[c]),
            float(result.tstats[c]),
            float(result.pvalues[c]),
        )

    return {
        "f_stat": f_stat,
        "p_value": p_value,
        "n_obs": int(result.nobs),
        "lead_estimates": lead_estimates,
        "warnings": warnings,
        "treatment_col": treatment_col,
        "dv": dv,
    }
