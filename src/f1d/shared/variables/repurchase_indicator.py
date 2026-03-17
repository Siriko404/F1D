"""Builder for REPO variable (1 if firm repurchased shares in the quarter, else 0).

Uses cshopq (total shares repurchased - quarter) > 0.
cshopq is a true quarterly flow (NOT YTD cumulative like capxy/dvy).
NaN cshopq means the field was not reported (common before 2004), not zero repurchases.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, REPO.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class RepurchaseIndicatorBuilder(VariableBuilder):
    """Build REPO = (cshopq > 0).astype(float) from raw Compustat quarterly data."""

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
        data = merged[["file_name", "REPO", "fqtr"]].copy()
        stats = self.get_stats(data["REPO"], "REPO")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "REPO", "source": "Compustat/cshopq>0"},
        )


__all__ = ["RepurchaseIndicatorBuilder"]
