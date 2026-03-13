"""Builder for earnings_surprise_ratio (H14 Control Variable).

Computes |ACTUAL - MEANEST| / |MEANEST| from the IBES summary engine which
aggregates individual analyst estimates into consensus stats.

Returns one column: file_name, earnings_surprise_ratio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


class EarningsSurpriseRatioBuilder(VariableBuilder):
    """Build earnings surprise ratio from IBES data via IbesEngine.

    Uses the summary engine which computes consensus from detail-level data.
    Matches each call to the most recent consensus via merge_asof, then
    filters by FPEDATS proximity (±90 days).

    Computes: |ACTUAL - MEANEST| / |MEANEST|
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

        # Get IBES consensus data from summary engine
        engine = get_ibes_engine()
        ibes_data = engine.get_data(root_path)

        if ibes_data.empty or "earnings_surprise_ratio" not in ibes_data.columns:
            print("    EarningsSurpriseRatio: No IBES data available")
            data = manifest[["file_name"]].copy()
            data["earnings_surprise_ratio"] = np.nan
            return VariableResult(
                data=data,
                stats=self.get_stats(data["earnings_surprise_ratio"], "earnings_surprise_ratio"),
                metadata={"column": "earnings_surprise_ratio", "source": "IBES"},
            )

        # merge_asof: for each call, find the most recent consensus whose fiscal
        # period ended before the call (fpedats <= start_date, ±120 day tolerance)
        manifest_sorted = manifest.sort_values("start_date")
        ibes_sorted = ibes_data.sort_values("fpedats")

        merged = pd.merge_asof(
            manifest_sorted[["file_name", "gvkey", "start_date"]],
            ibes_sorted[["gvkey", "fpedats", "earnings_surprise_ratio"]],
            left_on="start_date",
            right_on="fpedats",
            by="gvkey",
            direction="backward",
            tolerance=pd.Timedelta(days=120),
        )

        # Merge back to preserve original manifest order
        data = manifest[["file_name"]].merge(
            merged[["file_name", "earnings_surprise_ratio"]],
            on="file_name",
            how="left",
        )

        valid_count = data["earnings_surprise_ratio"].notna().sum()
        total = len(manifest)
        pct = 100 * valid_count / total if total > 0 else 0
        print(f"    EarningsSurpriseRatio: {valid_count:,}/{total:,} calls with valid surprise ({pct:.1f}%)")

        stats = self.get_stats(data["earnings_surprise_ratio"], "earnings_surprise_ratio")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "earnings_surprise_ratio",
                "source": "IBES Detail via IbesEngine consensus",
                "coverage": f"{valid_count}/{total}",
            },
        )


__all__ = ["EarningsSurpriseRatioBuilder"]
