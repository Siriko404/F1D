"""Builder for raw Earnings Surprise variable (EarningsSurprise_Raw).

Computes ACTUAL - MEANEST from IBES consensus data (via IbesEngine).
Returns one column: file_name, EarningsSurprise_Raw.

Algorithm:
  1. Load IBES consensus from IbesEngine (computed from yearly detail files).
  2. For each call, match to most recent pre-call consensus via merge_asof.
  3. Filter by FPEDATS proximity (±45 days of call date).
  4. Return raw surprise = ACTUAL - MEANEST.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


class EarningsSurpriseRawBuilder(VariableBuilder):
    """Build raw Earnings Surprise from IBES data via IbesEngine.

    Returns a VariableResult whose .data contains: file_name, EarningsSurprise_Raw.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        print("    EarningsSurpriseRawBuilder: loading manifest...")
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Load IBES consensus from summary engine
        engine = get_ibes_engine()
        ibes_data = engine.get_data(root_path)

        if ibes_data.empty or "surprise_raw" not in ibes_data.columns:
            print("    EarningsSurpriseRawBuilder: No IBES data available")
            data = manifest[["file_name"]].copy()
            data["EarningsSurprise_Raw"] = np.nan
            return VariableResult(
                data=data,
                stats=self.get_stats(data["EarningsSurprise_Raw"], "EarningsSurprise_Raw"),
                metadata={"column": "EarningsSurprise_Raw", "source": "IBES"},
            )

        # merge_asof: for each call, find the most recent consensus whose fiscal
        # period ended before the call (fpedats <= start_date, ±120 day tolerance)
        manifest_sorted = manifest.sort_values("start_date")
        ibes_sorted = ibes_data.sort_values("fpedats")

        merged = pd.merge_asof(
            manifest_sorted[["file_name", "gvkey", "start_date"]],
            ibes_sorted[["gvkey", "fpedats", "surprise_raw"]],
            left_on="start_date",
            right_on="fpedats",
            by="gvkey",
            direction="backward",
            tolerance=pd.Timedelta(days=120),
        )

        # Restore original manifest order
        results_df = manifest[["file_name"]].merge(
            merged[["file_name", "surprise_raw"]], on="file_name", how="left"
        )

        matched = int(results_df["surprise_raw"].notna().sum())
        if len(manifest) > 0:
            print(
                f"    EarningsSurpriseRawBuilder: matched {matched:,}/{len(manifest):,} "
                f"({matched / len(manifest) * 100:.1f}%)"
            )

        results_df = results_df.rename(columns={"surprise_raw": "EarningsSurprise_Raw"})

        data = results_df[["file_name", "EarningsSurprise_Raw"]].copy()
        stats = self.get_stats(data["EarningsSurprise_Raw"], "EarningsSurprise_Raw")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "source": "IBES Detail via IbesEngine consensus",
                "column": "EarningsSurprise_Raw",
                "matched": matched,
                "total": len(manifest),
            },
        )


__all__ = ["EarningsSurpriseRawBuilder"]
