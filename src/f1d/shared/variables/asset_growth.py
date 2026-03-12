"""Builder for AssetGrowth variable (year-over-year total asset growth).

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, AssetGrowth.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class AssetGrowthBuilder(VariableBuilder):
    """Build AssetGrowth = (atq_t - atq_{t-4}) / |atq_{t-4}| from Compustat.

    Year-over-year asset growth using date-based lag.
    Asset growth effect documented by Cooper et al. (2008) - high asset growth
    predicts lower future returns. In takeover context, rapid asset growth may
    signal expansion or acquisition activity.
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

        engine = get_engine()
        merged = engine.match_to_manifest(manifest, root_path)

        data = merged[["file_name", "AssetGrowth"]].copy()
        stats = self.get_stats(data["AssetGrowth"], "AssetGrowth")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "AssetGrowth", "source": "Compustat/atq (date-based lag)"},
        )


__all__ = ["AssetGrowthBuilder"]
