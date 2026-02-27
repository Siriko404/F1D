"""Builder for OCF_Volatility variable (rolling 5-year std of operating cash flow / assets).

Uses 5-year rolling window with minimum 3 years required (matches v2 design).
Previously used 4-year window with min 2 years.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, OCF_Volatility.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class OCFVolatilityBuilder(VariableBuilder):
    """Build OCF_Volatility = rolling 5-year std (min 3 yrs) of (oancfy/atq_{t-1}) per gvkey.

    Uses lagged assets to avoid correlated measurement error from contemporaneous
    asset changes.
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

        data = merged[["file_name", "OCF_Volatility"]].copy()
        stats = self.get_stats(data["OCF_Volatility"], "OCF_Volatility")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "OCF_Volatility",
                "source": "Compustat/oancfy/atq_{t-1} rolling std",
            },
        )


__all__ = ["OCFVolatilityBuilder"]
