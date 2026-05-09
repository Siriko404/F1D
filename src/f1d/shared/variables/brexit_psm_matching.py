"""Brexit PSM matching builder — H1.5.brexit_did design (Module #11).

Replicates Campello et al. 2022 JFQA supplementary Tables C2-C3 (PSM-matched
sample) per spec lines 838-846 of tmp/3did_replication_v2_2026_05_08.md.

ALGORITHM.
For each treatment in {HIGH_BETA_UK, HIGH_10K}:
    1. Restrict universe to firms with valid HIGH (in {0, 1}) and complete
       6-control measurements at 2014Q4 (last pre-treatment quarter).
    2. Fit logistic regression of HIGH on 6 firm-level features:
       Tobin's Q, sales growth, stock return, cash flow, ln(assets),
       consensus EPS z-score.
    3. Compute propensity score p_i for each firm.
    4. 1-to-1 nearest-neighbor greedy matching without replacement on |p_t - p_c|.
    5. Output flag in_psm_sample = 1 for matched pairs, 0 for unmatched.

Output:
    outputs/variables/brexit_psm_matching/<ts>/
      psm_matched_per_firm.parquet  schema: gvkey, treatment_type, HIGH,
                                            p_score, match_partner_gvkey,
                                            match_distance, in_psm_sample
      run_manifest.json             diagnostics on match quality

The Brexit runner reads in_psm_sample column and restricts the panel to
matched firms when re-running the 16-cell baseline as PSM-matched cells.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd

from f1d.shared.path_utils import get_latest_output_dir
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler

from .base import VariableBuilder, VariableResult

logger = logging.getLogger(__name__)


PRE_TREATMENT_YQ = 20144  # 2014Q4 = last quarter before pre-Brexit window per spec §1G
TREATMENT_TYPES = ["beta_uk", "10k"]
PSM_FEATURES = [
    "brexit_tobins_q",
    "brexit_sales_growth",
    "brexit_stock_return",
    "brexit_cash_flow",
    "ln_atq",
    "consensus_eps_z",
]


def _load_treatment_assignments(root_path: Path) -> pd.DataFrame:
    """Load HIGH_BETA_UK + HIGH_10K per gvkey, merged to a single firm-level frame."""
    beta_uk_dir = get_latest_output_dir(
        root_path / "outputs" / "variables" / "brexit_treatment_beta_uk",
        required_file="beta_uk_per_firm.parquet",
    )
    bu = pd.read_parquet(beta_uk_dir / "beta_uk_per_firm.parquet", columns=["gvkey", "HIGH_BETA_UK"])

    tk_dir = get_latest_output_dir(
        root_path / "outputs" / "variables" / "brexit_treatment_10k",
        required_file="treatment_10k_per_firm.parquet",
    )
    tk = pd.read_parquet(tk_dir / "treatment_10k_per_firm.parquet", columns=["gvkey", "HIGH_10K"])

    merged = bu.merge(tk, on="gvkey", how="outer")
    return merged


def _load_pre_treatment_features(root_path: Path) -> pd.DataFrame:
    """Load 6-feature firm-level matrix at 2014Q4."""
    # Compustat raw at 2014Q4 for ln(atq).
    comp = pd.read_parquet(
        root_path / "inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet",
        columns=["gvkey", "datadate", "atq"],
    )
    comp["atq"] = pd.to_numeric(comp["atq"], errors="coerce")
    comp["datadate"] = pd.to_datetime(comp["datadate"])
    comp["cal_yr_qtr"] = comp["datadate"].dt.year * 10 + comp["datadate"].dt.quarter
    comp_q4 = comp[comp["cal_yr_qtr"] == PRE_TREATMENT_YQ].copy()
    comp_q4 = comp_q4.dropna(subset=["atq"])
    comp_q4 = comp_q4[comp_q4["atq"] > 0]
    comp_q4["gvkey"] = comp_q4["gvkey"].astype(int).astype(str).str.zfill(6)
    comp_q4["ln_atq"] = np.log(comp_q4["atq"])
    comp_q4 = comp_q4.sort_values(["gvkey", "datadate"], kind="stable").drop_duplicates(
        subset=["gvkey"], keep="last"
    )[["gvkey", "ln_atq"]]

    feat_dirs = {
        "brexit_tobins_q": "brexit_tobins_q",
        "brexit_sales_growth": "brexit_sales_growth",
        "brexit_stock_return": "brexit_stock_return",
        "brexit_cash_flow": "brexit_cash_flow",
        "consensus_eps_z": "brexit_consensus_eps",
    }
    feat_files = {
        "brexit_tobins_q": "brexit_tobins_q.parquet",
        "brexit_sales_growth": "brexit_sales_growth.parquet",
        "brexit_stock_return": "brexit_stock_return.parquet",
        "brexit_cash_flow": "brexit_cash_flow.parquet",
        "consensus_eps_z": "consensus_eps_per_firm_quarter.parquet",
    }
    out = comp_q4.copy()
    for col, dir_name in feat_dirs.items():
        d = get_latest_output_dir(
            root_path / "outputs" / "variables" / dir_name,
            required_file=feat_files[col],
        )
        df = pd.read_parquet(d / feat_files[col])
        df_q4 = df[df["cal_yr_qtr"] == PRE_TREATMENT_YQ][["gvkey", col]].copy()
        out = out.merge(df_q4, on="gvkey", how="inner")

    return out[["gvkey"] + PSM_FEATURES]


def _greedy_nn_match(
    treated_ids: np.ndarray,
    treated_p: np.ndarray,
    control_ids: np.ndarray,
    control_p: np.ndarray,
) -> List[Tuple[str, str, float]]:
    """1-to-1 nearest-neighbor match without replacement, sorted by treated p ascending.

    Returns list of (treated_gvkey, control_gvkey, |p_t - p_c|).
    """
    used_control = np.zeros(len(control_ids), dtype=bool)
    pairs: List[Tuple[str, str, float]] = []

    # Iterate treated firms in order — order shouldn't matter for greedy NN
    # but stable order makes the result deterministic.
    order = np.argsort(treated_p)
    for ti in order:
        t_id = treated_ids[ti]
        t_p = treated_p[ti]
        # Compute distances to all unused controls.
        avail = ~used_control
        if not avail.any():
            break
        dists = np.abs(control_p[avail] - t_p)
        local_idx = np.argmin(dists)
        avail_idx = np.where(avail)[0][local_idx]
        d = float(dists[local_idx])
        used_control[avail_idx] = True
        pairs.append((str(t_id), str(control_ids[avail_idx]), d))

    return pairs


def _run_psm_for_treatment(
    feat: pd.DataFrame,
    treat: pd.DataFrame,
    treatment_col: str,
    label: str,
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Run PSM for a single treatment dummy. Returns (per-firm output, diagnostics)."""
    sub = feat.merge(treat[["gvkey", treatment_col]], on="gvkey", how="inner")
    sub = sub.dropna(subset=PSM_FEATURES + [treatment_col])
    sub = sub[sub[treatment_col].isin([0.0, 1.0])].copy()

    n_full = len(sub)
    n_treated = int((sub[treatment_col] == 1).sum())
    n_control = int((sub[treatment_col] == 0).sum())
    logger.info(f"  {label}: full sample {n_full:,} (treated {n_treated:,}, control {n_control:,})")

    if n_treated < 5 or n_control < 5:
        logger.warning(f"  {label}: too few firms for PSM ({n_treated}/{n_control}); returning unmatched")
        sub["p_score"] = np.nan
        sub["match_partner_gvkey"] = pd.NA
        sub["match_distance"] = np.nan
        sub["in_psm_sample"] = 0
        sub["treatment_type"] = label
        return sub.rename(columns={treatment_col: "HIGH"})[
            ["gvkey", "treatment_type", "HIGH", "p_score", "match_partner_gvkey", "match_distance", "in_psm_sample"]
        ], {"label": label, "n_treated": n_treated, "n_control": n_control, "n_matched_pairs": 0}

    # Logistic regression on standardized features.
    X = sub[PSM_FEATURES].to_numpy(dtype=float)
    y = sub[treatment_col].to_numpy(dtype=int)
    scaler = StandardScaler()
    X_std = scaler.fit_transform(X)

    lr = LogisticRegression(max_iter=2000, solver="lbfgs", C=1.0)
    lr.fit(X_std, y)
    p_score = lr.predict_proba(X_std)[:, 1]
    sub["p_score"] = p_score

    treated = sub[sub[treatment_col] == 1].reset_index(drop=True)
    control = sub[sub[treatment_col] == 0].reset_index(drop=True)
    pairs = _greedy_nn_match(
        treated["gvkey"].to_numpy(),
        treated["p_score"].to_numpy(),
        control["gvkey"].to_numpy(),
        control["p_score"].to_numpy(),
    )

    # Build per-firm output flags + partner via dict-based lookup (robust to dups).
    pair_df = pd.DataFrame(pairs, columns=["treated_gvkey", "control_gvkey", "match_distance"])
    treated_to_control: Dict[str, str] = dict(zip(pair_df["treated_gvkey"], pair_df["control_gvkey"]))
    control_to_treated: Dict[str, str] = dict(zip(pair_df["control_gvkey"], pair_df["treated_gvkey"]))
    dist_map: Dict[str, float] = {}
    for t, c, d in zip(pair_df["treated_gvkey"], pair_df["control_gvkey"], pair_df["match_distance"]):
        dist_map[t] = float(d)
        dist_map[c] = float(d)
    matched_treated = set(treated_to_control.keys())
    matched_control = set(control_to_treated.keys())

    sub["in_psm_sample"] = sub["gvkey"].isin(matched_treated | matched_control).astype(int)

    def _partner(g: str) -> Any:
        if g in treated_to_control:
            return treated_to_control[g]
        if g in control_to_treated:
            return control_to_treated[g]
        return pd.NA

    sub["match_partner_gvkey"] = sub["gvkey"].apply(_partner)
    sub["match_distance"] = sub["gvkey"].map(dist_map)

    sub["treatment_type"] = label
    out = sub[
        ["gvkey", "treatment_type", treatment_col, "p_score", "match_partner_gvkey", "match_distance", "in_psm_sample"]
    ].rename(columns={treatment_col: "HIGH"})

    diagnostics = {
        "label": label,
        "n_full": n_full,
        "n_treated": n_treated,
        "n_control": n_control,
        "n_matched_pairs": int(len(pairs)),
        "max_match_distance": float(pair_df["match_distance"].max()) if len(pair_df) else None,
        "median_match_distance": float(pair_df["match_distance"].median()) if len(pair_df) else None,
    }
    logger.info(
        f"  {label}: {len(pairs):,} matched pairs "
        f"(median d={diagnostics['median_match_distance']:.4f}, max d={diagnostics['max_match_distance']:.4f})"
    )
    return out, diagnostics


class BrexitPSMMatchingBuilder(VariableBuilder):
    """Build PSM-matched-sample indicator per (gvkey, treatment_type)."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.column = "in_psm_sample"

    def build(self, years: range, root_path: Path) -> VariableResult:
        del years

        treat = _load_treatment_assignments(root_path)
        logger.info(f"BrexitPSMMatchingBuilder: treatment-assignment frame {len(treat):,} rows")

        feat = _load_pre_treatment_features(root_path)
        logger.info(f"  pre-treatment features at 2014Q4: {len(feat):,} firms with complete 6-feature vector")

        out_frames: List[pd.DataFrame] = []
        diagnostics: List[Dict[str, Any]] = []
        for label, col in [("beta_uk", "HIGH_BETA_UK"), ("10k", "HIGH_10K")]:
            df, diag = _run_psm_for_treatment(feat, treat, col, label)
            out_frames.append(df)
            diagnostics.append(diag)

        out = pd.concat(out_frames, ignore_index=True)
        n_total_rows = int(len(out))
        n_matched = int((out["in_psm_sample"] == 1).sum())
        logger.info(f"BrexitPSMMatchingBuilder: total rows {n_total_rows:,}; in_psm_sample=1 → {n_matched:,}")

        stats = self.get_stats(out["in_psm_sample"], "in_psm_sample")
        metadata = {
            "source": "Campello et al. 2022 JFQA Tables C2-C3 (PSM 1:1 NN no-replace)",
            "pre_treatment_yq": PRE_TREATMENT_YQ,
            "psm_features": PSM_FEATURES,
            "diagnostics_per_treatment": diagnostics,
            "n_total_rows": n_total_rows,
            "n_matched_rows": n_matched,
            "column": "in_psm_sample",
        }
        return VariableResult(data=out, stats=stats, metadata=metadata)
