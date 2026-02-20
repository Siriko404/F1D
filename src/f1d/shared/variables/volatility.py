"""Builder for Stock Volatility variable.

Reads raw CRSP daily stock files via the shared CRSPEngine.
Returns one column: file_name, Volatility.

Volatility = annualized standard deviation of daily returns (%) over the window
    [prev_call_date + 5 days, call start_date - 5 days],
    requiring >= 10 trading days.
    Formula: std(daily_ret) * sqrt(252) * 100
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._crsp_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class VolatilityBuilder(VariableBuilder):
    """Build Volatility from raw CRSP daily stock files via CRSPEngine."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        engine = get_engine()
        result_df = engine.get_data(root_path, manifest_path)

        manifest_years = pd.read_parquet(
            manifest_path, columns=["file_name", "start_date"]
        )
        manifest_years["start_date"] = pd.to_datetime(manifest_years["start_date"])
        manifest_years["year"] = manifest_years["start_date"].dt.year
        valid_files = manifest_years[manifest_years["year"].isin(list(years))][
            "file_name"
        ]

        data = result_df[result_df["file_name"].isin(valid_files)][
            ["file_name", "Volatility"]
        ].copy()

        stats = self.get_stats(data["Volatility"], "Volatility")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "Volatility", "source": "CRSP/RET"},
        )


__all__ = ["VolatilityBuilder"]
