"""Builder for loss_dummy (H5 Control Variable).

1 if niq < 0, else 0. Fetched from Compustat engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd
import numpy as np

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class LossDummyBuilder(VariableBuilder):
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

        engine = get_engine()
        comp = engine.get_data(root_path)

        # We compute loss_dummy on the fly and merge it via standard backward ASOF
        comp["loss_dummy"] = np.where(
            comp["ibq"].isna(), np.nan, (comp["ibq"] < 0).astype(float)
        )

        fyearq_df = (
            comp[["gvkey", "datadate", "loss_dummy"]].dropna().sort_values("datadate")
        )

        manifest_sorted = manifest.sort_values("start_date").dropna(
            subset=["start_date"]
        )
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))

        merged = pd.merge_asof(
            manifest_sorted,
            fyearq_df,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        merged = merged.sort_values("_row_idx")
        final_merged = manifest[["file_name"]].merge(
            merged[["file_name", "loss_dummy"]], on="file_name", how="left"
        )

        data = final_merged[["file_name", "loss_dummy"]].copy()
        stats = self.get_stats(data["loss_dummy"], "loss_dummy")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "loss_dummy", "source": "Compustat ibq < 0"},
        )


__all__ = ["LossDummyBuilder"]
