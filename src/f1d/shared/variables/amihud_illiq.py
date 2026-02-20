from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._crsp_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class AmihudIlliqBuilder(VariableBuilder):
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
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        engine = get_engine()
        crsp_data = engine.get_data(root_path, manifest_path)
        
        merged = manifest.merge(
            crsp_data[["file_name", "amihud_illiq"]], on="file_name", how="left"
        )
        
        data = merged[["file_name", "amihud_illiq"]].copy()
        
        return VariableResult(
            data=data,
            stats=self.get_stats(data["amihud_illiq"], "amihud_illiq"),
            metadata={"column": "amihud_illiq", "source": "CRSP via CRSPEngine"},
        )

__all__ = ["AmihudIlliqBuilder"]
