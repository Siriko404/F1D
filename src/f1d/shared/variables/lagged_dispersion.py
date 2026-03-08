"""Builder for lagged_dispersion (H5 Control Variable).

Fetches the prior quarter (t-1) analyst forecast dispersion from the IBES engine.
Queries the shared IBES engine for analyst forecast data and finds the
consensus that is ONE PERIOD BEFORE the current period consensus.

Returns one column: file_name, lagged_dispersion.
Formula: STDEV / |MEANEST| (prior consensus before the current one)
Timing: t-1 (prior period, for use as lagged DV control)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


class LaggedDispersionBuilder(VariableBuilder):
    """Build lagged_dispersion = t-1 analyst forecast dispersion via IBES engine.

    Output: file_name, lagged_dispersion
    Formula: STDEV / |MEANEST| at t-1 (prior consensus)
    Timing: t-1 (prior period, for use as lagged DV control)

    Implementation: Uses a shift-based approach to find the prior consensus
    for each gvkey after matching to current consensus.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        i_engine = get_ibes_engine()
        ibes = i_engine.get_data(root_path)

        # Get all consensus dates sorted by statpers (required for merge_asof)
        ibes_sorted = ibes[["gvkey", "statpers", "dispersion"]].dropna().sort_values("statpers")

        manifest_sorted = manifest.sort_values("start_date").dropna(subset=["start_date"])
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))

        # Step 1: Find the current period consensus (backward merge)
        df_current = pd.merge_asof(
            manifest_sorted,
            ibes_sorted.rename(columns={"dispersion": "dispersion_current", "statpers": "statpers_current"}),
            left_on="start_date",
            right_on="statpers_current",
            by="gvkey",
            direction="backward",
            tolerance=pd.Timedelta(days=365),
        )

        # Step 2: Create lagged dispersion using shift within gvkey groups
        # First, sort IBES by gvkey and statpers to get the sequence of consensuses
        ibes_by_gvkey = ibes[["gvkey", "statpers", "dispersion"]].dropna().sort_values(["gvkey", "statpers"])
        ibes_by_gvkey = ibes_by_gvkey.drop_duplicates(subset=["gvkey", "statpers"], keep="first")

        # Create a shifted version within each gvkey to get the prior consensus
        ibes_by_gvkey["lagged_dispersion"] = ibes_by_gvkey.groupby("gvkey")["dispersion"].shift(1)

        # Now merge this lagged dispersion back to df_current using statpers_current
        df_with_lag = df_current.merge(
            ibes_by_gvkey[["gvkey", "statpers", "lagged_dispersion"]],
            left_on=["gvkey", "statpers_current"],
            right_on=["gvkey", "statpers"],
            how="left"
        )

        # Sort back to original order
        df_with_lag = df_with_lag.sort_values("_row_idx")

        # Create final result
        final_merged = manifest[["file_name"]].merge(
            df_with_lag[["file_name", "lagged_dispersion"]], on="file_name", how="left"
        )

        data = final_merged[["file_name", "lagged_dispersion"]].copy()
        stats = self.get_stats(data["lagged_dispersion"], "lagged_dispersion")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "lagged_dispersion", "source": "IBES STDEV/|MEANEST| (t-1)"},
        )

__all__ = ["LaggedDispersionBuilder"]
