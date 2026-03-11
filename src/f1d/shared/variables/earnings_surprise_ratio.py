"""Builder for earnings_surprise_ratio (H5 Control Variable).

Fetches the unranked ratio |ACTUAL - MEANEST| / |MEANEST| from the IBES Detail engine.
Uses individual analyst estimates to compute consensus mean and matches to actuals
from IBES reported actuals.

Returns one column: file_name, earnings_surprise_ratio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_detail_engine import get_engine as get_ibes_detail_engine
from f1d.shared.path_utils import get_latest_output_dir


class EarningsSurpriseRatioBuilder(VariableBuilder):
    """Build earnings surprise ratio from IBES Detail data.

    Computes: |ACTUAL - MEANEST| / |MEANEST|
    where MEANEST is the mean of most recent analyst estimates before the call
    and ACTUAL is the actual earnings from IBES.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.numest_min = config.get("numest_min", 2)
        self.max_stale_days = config.get("max_stale_days", 180)

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

        # Get IBES Detail engine
        engine = get_ibes_detail_engine()
        ibes_detail = engine.get_data(root_path, years)

        # Convert dates
        ibes_detail = ibes_detail.copy()
        ibes_detail["actdats"] = pd.to_datetime(ibes_detail["ACTDATS"])
        ibes_detail["fpedats"] = pd.to_datetime(ibes_detail["FPEDATS"])

        # Get actuals from IBES Detail (one per gvkey-fpedats)
        # Actuals are at the estimate level but should be same for all estimates of same period
        actuals_df = (
            ibes_detail[["gvkey", "fpedats", "ACTUAL"]]
            .dropna(subset=["ACTUAL"])
            .drop_duplicates(subset=["gvkey", "fpedats"])
        )

        # Compute earnings surprise for each call
        results = []
        total_calls = len(manifest)

        for idx, row in manifest.iterrows():
            if idx % 10000 == 0:
                print(f"    EarningsSurprise: Processing call {idx}/{total_calls}...")

            file_name = row["file_name"]
            gvkey = row["gvkey"]
            call_date = row["start_date"]

            if pd.isna(call_date):
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            # Get estimates for this gvkey
            gvkey_estimates = ibes_detail[ibes_detail["gvkey"] == gvkey].copy()

            if len(gvkey_estimates) == 0:
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            # Find the target fiscal period closest to the call date (within 90 days after)
            gvkey_estimates["days_diff"] = (gvkey_estimates["fpedats"] - call_date).dt.days
            valid_quarters = gvkey_estimates[
                (gvkey_estimates["days_diff"] >= 0) &
                (gvkey_estimates["days_diff"] <= 90)
            ]

            if len(valid_quarters) == 0:
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            target_fpedats = valid_quarters.loc[valid_quarters["days_diff"].idxmin(), "fpedats"]
            quarter_estimates = gvkey_estimates[gvkey_estimates["fpedats"] == target_fpedats].copy()

            # Filter to estimates before the call
            pre_call = quarter_estimates[quarter_estimates["actdats"] <= call_date].copy()

            if len(pre_call) == 0:
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            # Apply stale filter
            age_days = (call_date - pre_call["actdats"]).dt.days
            pre_call = pre_call[age_days <= self.max_stale_days]

            # Keep most recent per analyst
            pre_call = pre_call.sort_values("actdats").groupby("ANALYS").last()

            if len(pre_call) < self.numest_min:
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            # Compute consensus mean
            meanest = pre_call["VALUE"].mean()

            if abs(meanest) < 0.01:  # Avoid division by near-zero
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            # Get actual for this gvkey and fpedats
            actual_row = actuals_df[
                (actuals_df["gvkey"] == gvkey) &
                (actuals_df["fpedats"] == target_fpedats)
            ]

            if len(actual_row) == 0 or pd.isna(actual_row["ACTUAL"].iloc[0]):
                results.append({"file_name": file_name, "earnings_surprise_ratio": np.nan})
                continue

            actual = actual_row["ACTUAL"].iloc[0]
            surprise = abs(actual - meanest) / abs(meanest)

            results.append({"file_name": file_name, "earnings_surprise_ratio": surprise})

        data = pd.DataFrame(results)
        valid_count = data["earnings_surprise_ratio"].notna().sum()
        print(f"    EarningsSurprise: {valid_count}/{total_calls} calls with valid earnings surprise ({100*valid_count/total_calls:.1f}%)")

        stats = self.get_stats(data["earnings_surprise_ratio"], "earnings_surprise_ratio")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "earnings_surprise_ratio",
                "source": "IBES Detail |ACTUAL-MEANEST|/|MEANEST|",
                "coverage": f"{valid_count}/{total_calls}",
            },
        )


__all__ = ["EarningsSurpriseRatioBuilder"]
