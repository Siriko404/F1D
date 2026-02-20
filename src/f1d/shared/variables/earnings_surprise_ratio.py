"""Builder for earnings_surprise_ratio (H5 Control Variable).

Fetches the unranked ratio |ACTUAL - MEANEST| / |MEANEST| from the IBES engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


class EarningsSurpriseRatioBuilder(VariableBuilder):
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
        
        ibes_sorted = ibes[["gvkey", "statpers", "earnings_surprise_ratio"]].dropna().sort_values("statpers")
        
        manifest_sorted = manifest.sort_values("start_date").dropna(subset=["start_date"])
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))
        
        df = pd.merge_asof(
            manifest_sorted,
            ibes_sorted,
            left_on="start_date",
            right_on="statpers",
            by="gvkey",
            direction="backward",
        )
        df = df.sort_values("_row_idx")
        
        final_merged = manifest[["file_name"]].merge(df[["file_name", "earnings_surprise_ratio"]], on="file_name", how="left")

        data = final_merged[["file_name", "earnings_surprise_ratio"]].copy()
        stats = self.get_stats(data["earnings_surprise_ratio"], "earnings_surprise_ratio")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "earnings_surprise_ratio", "source": "IBES |ACTUAL-MEANEST|/|MEANEST|"},
        )

__all__ = ["EarningsSurpriseRatioBuilder"]
