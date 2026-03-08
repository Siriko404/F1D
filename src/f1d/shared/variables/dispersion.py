"""Builder for dispersion (H5 Dependent Variable).

Fetches the current quarter (t) analyst forecast dispersion from the IBES engine.
Queries the shared IBES engine for analyst forecast data and matches
to calls via merge_asof on gvkey and statpers.

Returns one column: file_name, dispersion.
Formula: STDEV / |MEANEST| (standard deviation of forecasts divided by
absolute mean estimate).
Timing: t (current period, contemporaneous with call) — backward merge to
most recent consensus before or on the call date.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


class DispersionBuilder(VariableBuilder):
    """Build dispersion = current period analyst forecast dispersion via IBES engine.

    Output: file_name, dispersion
    Formula: STDEV / |MEANEST| (backward merge to most recent consensus before call)
    Timing: t (current period, contemporaneous with call)
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

        # Backward merge: find the most recent consensus on or before the call date
        ibes_sorted = ibes[["gvkey", "statpers", "dispersion"]].dropna().sort_values("statpers")

        manifest_sorted = manifest.sort_values("start_date").dropna(subset=["start_date"])
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))

        df = pd.merge_asof(
            manifest_sorted,
            ibes_sorted,
            left_on="start_date",
            right_on="statpers",
            by="gvkey",
            direction="backward",
            tolerance=pd.Timedelta(days=365),
        )
        df = df.sort_values("_row_idx")

        final_merged = manifest[["file_name"]].merge(df[["file_name", "dispersion"]], on="file_name", how="left")

        data = final_merged[["file_name", "dispersion"]].copy()
        stats = self.get_stats(data["dispersion"], "dispersion")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "dispersion", "source": "IBES STDEV/|MEANEST|"},
        )

__all__ = ["DispersionBuilder"]
