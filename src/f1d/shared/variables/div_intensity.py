"""Builder for DivIntensity variable (cash dividends / total assets).

DivIntensity = dvy_Q4 / atq, where dvy is annual cash dividends extracted
from Q4 Compustat rows (YTD cumulative) and atq is contemporaneous total assets.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, DivIntensity.

H12 extension: Tests whether language uncertainty predicts dividend intensity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class DivIntensityBuilder(VariableBuilder):
    """Build DivIntensity = dvy_Q4 / atq from raw Compustat quarterly data."""

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
        merged = engine.match_to_manifest(manifest, root_path)

        data = merged[["file_name", "DivIntensity"]].copy()
        stats = self.get_stats(data["DivIntensity"], "DivIntensity")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "DivIntensity",
                "source": "Compustat/dvy_Q4/atq",
            },
        )


__all__ = ["DivIntensityBuilder"]
