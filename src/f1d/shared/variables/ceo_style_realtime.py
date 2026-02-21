"""Builder for ClarityStyle_Realtime — H_TT Tone-at-the-Top.

    CEOStyleRealtimeBuilder — 4-call rolling window, min 4 prior calls.

Applies Empirical Bayes (James-Stein) shrinkage and quarter-standardisation.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from f1d.shared.path_utils import get_latest_output_dir


def _load_base_df(root_path: Path) -> pd.DataFrame:
    """Load and merge manifest + CEO_QA_Uncertainty_pct for all years."""
    manifest_dir = get_latest_output_dir(
        root_path / "outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest = pd.read_parquet(
        manifest_dir / "master_sample_manifest.parquet",
        columns=["file_name", "ceo_id", "start_date"],
    )
    manifest["start_date"] = pd.to_datetime(manifest["start_date"])
    manifest["year"] = manifest["start_date"].dt.year
    manifest["quarter"] = manifest["start_date"].dt.quarter

    var_dir = get_latest_output_dir(
        root_path / "outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2010.parquet",
    )
    dfs = [
        pd.read_parquet(p, columns=["file_name", "CEO_QA_Uncertainty_pct"])
        for p in var_dir.glob("linguistic_variables_*.parquet")
    ]
    if not dfs:
        raise FileNotFoundError("No linguistic_variables parquet files found.")

    text_df = pd.concat(dfs, ignore_index=True)
    df = manifest.merge(text_df, on="file_name", how="inner")
    df = df.dropna(subset=["ceo_id", "start_date", "CEO_QA_Uncertainty_pct"]).copy()
    return df.sort_values("start_date").reset_index(drop=True)


def _standardize_series(x: pd.Series) -> pd.Series:
    """Standardise a series to mean-0, std-1; return all-NaN if degenerate."""
    valid = x.dropna()
    if len(valid) < 2 or valid.std() == 0:
        return pd.Series(np.nan, index=x.index)
    return (x - valid.mean()) / valid.std()


def _estimate_realtime_style(
    df: pd.DataFrame,
    col_name: str,
    min_calls: int,
    window: Optional[int],  # None = expanding; int = rolling N calls
) -> pd.Series:
    """
    Core estimation: rolling/expanding CEO FE with EB shrinkage.

    Parameters
    ----------
    df        : sorted DataFrame with ceo_id, start_date, CEO_QA_Uncertainty_pct
    col_name  : output column name
    min_calls : minimum prior calls required; else NaN
    window    : None → expanding; positive int → rolling window of that many calls

    Returns
    -------
    pd.Series aligned to df.index, named col_name
    """
    # 1. Demean by year-quarter
    df = df.copy()
    df["yq"] = df["year"].astype(str) + "Q" + df["quarter"].astype(str)
    yq_means = df.groupby("yq")["CEO_QA_Uncertainty_pct"].transform("mean")
    df["unc_demeaned"] = df["CEO_QA_Uncertainty_pct"] - yq_means

    # 2. Rolling prior stats (strictly prior calls via shift)
    grp = df.groupby("ceo_id")["unc_demeaned"]

    if window is None:
        # Expanding: all prior calls
        df["prior_mean"] = grp.transform(lambda x: x.shift().expanding().mean())
        df["prior_count"] = grp.transform(lambda x: x.shift().expanding().count())
    else:
        # Fixed rolling window of `window` calls
        df["prior_mean"] = grp.transform(
            lambda x: x.shift().rolling(window, min_periods=min_calls).mean()
        )
        df["prior_count"] = grp.transform(
            lambda x: x.shift().rolling(window, min_periods=min_calls).count()
        )

    # 3. Empirical Bayes (James-Stein) shrinkage
    sigma_e_sq = float(df["unc_demeaned"].var())

    ceo_means = df.groupby("ceo_id")["unc_demeaned"].mean()
    ceo_counts = df.groupby("ceo_id").size()
    robust = ceo_means[ceo_counts >= 10]
    sigma_u_sq = float(robust.var()) if len(robust) > 1 else 1.0

    safe_count = df["prior_count"].replace(0, np.nan)
    B_hat = (sigma_e_sq / (safe_count * sigma_u_sq)).clip(upper=1.0)
    df["gamma_shrunk"] = (1.0 - B_hat) * df["prior_mean"]

    # 4. Apply min_calls floor
    df.loc[df["prior_count"] < min_calls, "gamma_shrunk"] = np.nan

    # 5. Standardise within each calendar quarter
    out = df.groupby("yq")["gamma_shrunk"].transform(_standardize_series)
    out.name = col_name
    return out


class CEOStyleRealtimeBuilder(VariableBuilder):
    """4-call rolling-window CEO style (min 4 prior calls). Primary H_TT1 variable."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "ClarityStyle_Realtime")
        self.min_calls = config.get("min_calls", 4)

    def build(self, years: range, root_path: Path) -> VariableResult:
        df = _load_base_df(root_path)
        print("    [CEOStyleRealtime] Computing EB shrinkage (window=4, min=4)...")
        df[self.column] = _estimate_realtime_style(
            df, col_name=self.column, min_calls=self.min_calls, window=4
        )
        df_out = df[df["year"].isin(years)].copy()
        return VariableResult(
            data=df_out[["file_name", self.column]].copy(),
            stats=self.get_stats(df_out[self.column], self.column),
            metadata={
                "column": self.column,
                "description": "Rolling EB-shrunk CEO FE, 4-call rolling window, min N=4",
                "min_calls": self.min_calls,
                "window": 4,
            },
        )


__all__ = ["CEOStyleRealtimeBuilder"]
