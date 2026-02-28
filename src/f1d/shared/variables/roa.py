"""Builder for Return on Assets (ROA) variable.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, ROA.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class ROABuilder(VariableBuilder):
    """Build ROA = iby_annual / avg_assets from Compustat quarterly data.

    ROA is computed using annual income before extraordinary items (iby) from
    Q4 filing, divided by average total assets (atq_t + atq_{t-1}) / 2.

    Uses iby rather than niq per variable definitions spec for consistency
    with investment efficiency literature (Biddle et al. 2009).
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

        data = merged[["file_name", "ROA"]].copy()
        stats = self.get_stats(data["ROA"], "ROA")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "ROA", "source": "Compustat/iby,atq"},
        )


__all__ = ["ROABuilder"]
