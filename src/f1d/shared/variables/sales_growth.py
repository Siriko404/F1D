"""Builder for SalesGrowth variable (year-over-year revenue growth).

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, SalesGrowth.

Formula: SalesGrowth = (saley_t - saley_{t-1}) / |saley_{t-1}|
    saley: annual total revenue YTD (Q4 value = full fiscal year revenue).
    Falls back to saleq (quarterly revenue) when saley is missing.
    Computed on Q4-only annual panel (fiscal year), then joined back to all
    quarterly rows by gvkey+fyearq. Winsorized once at 1%/99% within fiscal year.
    Year gaps (missing fiscal year t-1) are set to NaN.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class SalesGrowthBuilder(VariableBuilder):
    """Build SalesGrowth from raw Compustat quarterly data (annual Q4 panel)."""

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

        data = merged[["file_name", "SalesGrowth"]].copy()
        stats = self.get_stats(data["SalesGrowth"], "SalesGrowth")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "SalesGrowth",
                "source": "Compustat/saley_Q4_YoY",
                "formula": "(saley_t - saley_{t-1}) / |saley_{t-1}|  (Q4-only annual; saley with saleq fallback)",
            },
        )


__all__ = ["SalesGrowthBuilder"]
