"""Builder for RepurchaseIntensity variable (quarterly repurchase intensity).

RepurchaseIntensity = quarterly_prstkcy / atq_{t-1}
  - prstkcy = Purchase of Common and Preferred Stock (YTD cumulative, de-cumulated
    to quarterly flow in CompustatEngine)
  - atq_{t-1} = Total Assets at end of previous quarter (validated consecutive)
  - NaN when atq_{t-1} <= 0 or missing, or when prstkcy cannot be de-cumulated
  - Negative quarterly repurchases (restatements) clamped to 0

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns columns: file_name, RepurchaseIntensity, fqtr.

H17 suite: Tests whether speech uncertainty predicts repurchase intensity.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class RepurchaseIntensityBuilder(VariableBuilder):
    """Build RepurchaseIntensity = quarterly_prstkcy / lagged_atq from Compustat."""

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

        # Include fqtr (fiscal quarter) — needed by panel builder for quarter-lead logic
        data = merged[["file_name", "RepurchaseIntensity", "fqtr"]].copy()
        stats = self.get_stats(data["RepurchaseIntensity"], "RepurchaseIntensity")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "RepurchaseIntensity",
                "source": "Compustat/quarterly_prstkcy/lagged_atq",
            },
        )


__all__ = ["RepurchaseIntensityBuilder"]
