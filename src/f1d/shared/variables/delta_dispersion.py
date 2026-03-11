"""Builder for delta_dispersion (H5 Dependent Variable).

Computes the change in analyst dispersion around earnings calls using
IBES Detail data (individual analyst estimates).

Output columns: file_name, dispersion_before, dispersion_after, delta_dispersion

Formula:
    dispersion = STDEV(VALUE) / |MEAN(VALUE)| at a specific date
    dispersion_before = dispersion at (call_date - 3 trading days)
    dispersion_after = dispersion at (call_date + 3 trading days)
    delta_dispersion = dispersion_after - dispersion_before

Methodology:
    1. For each call, identify the target fiscal quarter (FPEDATS closest to call)
    2. Filter to estimates for that gvkey/quarter
    3. Compute dispersion before call using estimates active 3 trading days before
    4. Compute dispersion after call using estimates active 3 trading days after
    5. Delta captures the change in analyst disagreement around the call

Reference: Diether et al. (2002) - dispersion methodology
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

from .base import VariableBuilder, VariableResult
from ._ibes_detail_engine import get_engine as get_ibes_detail_engine
from f1d.shared.path_utils import get_latest_output_dir


class DeltaDispersionBuilder(VariableBuilder):
    """Build delta dispersion = dispersion_{t+3} - dispersion_{t-3}.

    Output: file_name, dispersion_before, dispersion_after, delta_dispersion
    Timing: 3 trading days before call → 3 trading days after call
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.days_before = config.get("days_before", 3)
        self.days_after = config.get("days_after", 3)
        self.max_stale_days = config.get("max_stale_days", 180)

        # Initialize trading day calendar
        self.bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build delta dispersion variable for all calls in the year range.

        Args:
            years: Range of years to process
            root_path: Project root path

        Returns:
            VariableResult with file_name, dispersion_before, dispersion_after, delta_dispersion
        """
        # Load manifest
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

        # Load IBES Detail data
        engine = get_ibes_detail_engine()
        ibes = engine.get_data(root_path, years)

        # Compute delta dispersion for each call
        results = self._compute_delta_dispersion(manifest, ibes, engine)

        # Ensure we have all original file_names (left join)
        final = manifest[["file_name"]].merge(
            results, on="file_name", how="left"
        )

        # Create stats for all three columns
        stats = self.get_stats(final["delta_dispersion"], "delta_dispersion")

        return VariableResult(
            data=final,
            stats=stats,
            metadata={
                "columns": ["dispersion_before", "dispersion_after", "delta_dispersion"],
                "source": "IBES Detail (individual analyst estimates)",
                "window": f"±{self.days_before} trading days",
                "stale_filter_days": self.max_stale_days,
            },
        )

    def _compute_delta_dispersion(
        self,
        manifest: pd.DataFrame,
        ibes: pd.DataFrame,
        engine
    ) -> pd.DataFrame:
        """Compute dispersion before/after call for each filing.

        Args:
            manifest: DataFrame with file_name, gvkey, start_date
            ibes: IBES Detail DataFrame with gvkey, actdats, analys, value, fpedats
            engine: IbesDetailEngine instance for dispersion computation

        Returns:
            DataFrame with file_name, dispersion_before, dispersion_after, delta_dispersion
        """
        print(f"    DeltaDispersionBuilder: Computing delta dispersion for {len(manifest):,} calls...")

        # Pre-compute trading day offsets
        manifest["date_before"] = manifest["start_date"] - self.days_before * self.bday
        manifest["date_after"] = manifest["start_date"] + self.days_after * self.bday

        # Group IBES by gvkey for faster lookup
        ibes_by_gvkey = ibes.groupby("gvkey")

        results = []
        processed = 0

        for _, row in manifest.iterrows():
            gvkey = row["gvkey"]
            call_date = row["start_date"]
            date_before = row["date_before"]
            date_after = row["date_after"]

            # Get estimates for this gvkey
            if gvkey not in ibes_by_gvkey.groups:
                results.append({
                    "file_name": row["file_name"],
                    "dispersion_before": np.nan,
                    "dispersion_after": np.nan,
                    "delta_dispersion": np.nan,
                })
                continue

            gvkey_estimates = ibes_by_gvkey.get_group(gvkey)

            # Find the target fiscal quarter (FPEDATS closest to call date)
            fpedats = self._find_target_quarter(gvkey_estimates, call_date)

            if fpedats is None:
                results.append({
                    "file_name": row["file_name"],
                    "dispersion_before": np.nan,
                    "dispersion_after": np.nan,
                    "delta_dispersion": np.nan,
                })
                continue

            # Filter to estimates for this quarter
            quarter_estimates = gvkey_estimates[
                gvkey_estimates["fpedats"] == fpedats
            ].copy()

            if len(quarter_estimates) < engine.numest_min:
                results.append({
                    "file_name": row["file_name"],
                    "dispersion_before": np.nan,
                    "dispersion_after": np.nan,
                    "delta_dispersion": np.nan,
                })
                continue

            # Compute dispersion before and after
            disp_before = engine.compute_dispersion_at_date(
                quarter_estimates, date_before, self.max_stale_days
            )
            disp_after = engine.compute_dispersion_at_date(
                quarter_estimates, date_after, self.max_stale_days
            )

            # Compute delta (only if both are available)
            if disp_before is not None and disp_after is not None:
                delta = disp_after - disp_before
            else:
                delta = np.nan

            results.append({
                "file_name": row["file_name"],
                "dispersion_before": disp_before if disp_before is not None else np.nan,
                "dispersion_after": disp_after if disp_after is not None else np.nan,
                "delta_dispersion": delta,
            })

            processed += 1
            if processed % 10000 == 0:
                print(f"      Processed {processed:,} / {len(manifest):,} calls...")

        df = pd.DataFrame(results)
        coverage = df["delta_dispersion"].notna().sum()
        print(f"    DeltaDispersionBuilder: {coverage:,} calls with valid delta_dispersion ({100*coverage/len(df):.1f}%)")

        return df

    def _find_target_quarter(
        self,
        estimates: pd.DataFrame,
        call_date: pd.Timestamp
    ) -> Optional[pd.Timestamp]:
        """Find the fiscal quarter (FPEDATS) closest to the call date.

        For earnings calls, analysts are typically forecasting the current
        or next quarter. We find the closest FPEDATS to the call date.

        Args:
            estimates: DataFrame with fpedats column for a single gvkey
            call_date: The earnings call date

        Returns:
            The FPEDATS closest to the call date, or None if no valid quarters
        """
        unique_quarters = estimates["fpedats"].dropna().unique()

        if len(unique_quarters) == 0:
            return None

        # Find the quarter with FPEDATS closest to call date
        # Prefer forward-looking quarters (analysts forecast future earnings)
        quarters = pd.Series(unique_quarters)
        quarters = quarters.sort_values()

        # Find quarters on or after call date (forward-looking)
        forward = quarters[quarters >= call_date]

        if len(forward) > 0:
            # Return the nearest forward quarter
            return forward.iloc[0]

        # If no forward quarters, return the nearest backward quarter
        backward = quarters[quarters < call_date]
        if len(backward) > 0:
            return backward.iloc[-1]

        return quarters.iloc[0]  # Fallback to any available quarter


__all__ = ["DeltaDispersionBuilder"]
