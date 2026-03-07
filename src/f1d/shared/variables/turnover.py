"""Builder for share turnover at call date (H14 control variable).

Reads raw CRSP daily stock files via the shared CRSPEngine.get_raw_daily_data().
Returns columns: file_name, Turnover.

Turnover = VOL / SHROUT at call date (or nearest prior trading day).

VECTORIZED implementation using merge + groupby, with year-chunking for memory efficiency.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._crsp_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir

logger = logging.getLogger(__name__)


class TurnoverBuilder(VariableBuilder):
    """Compute share turnover at earnings call date (VECTORIZED).

    Control variable for H14: higher turnover may indicate more liquidity,
    affecting bid-ask spread.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        # Load manifest with required columns
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Build permno mapping using date-bounded CCM linkage
        permno_map = self._build_permno_map(root_path, manifest_path, manifest)

        # Merge permno to manifest
        manifest = manifest.merge(permno_map, on="file_name", how="left")

        # Load raw CRSP daily data (includes VOL, SHROUT)
        engine = get_engine()
        crsp_data = engine.get_raw_daily_data(root_path, years=list(years))

        if crsp_data.empty:
            logger.warning("TurnoverBuilder: No CRSP data loaded!")
            result_df = manifest[["file_name"]].copy()
            result_df["Turnover"] = np.nan
            return VariableResult(
                data=result_df,
                stats=self.get_stats(result_df["Turnover"], "Turnover"),
                metadata={"column": "Turnover", "source": "CRSP"},
            )

        # Compute turnover using vectorized operations
        results = self._compute_turnover_vectorized(manifest, crsp_data)

        return VariableResult(
            data=results[["file_name", "Turnover"]],
            stats=self.get_stats(results["Turnover"], "Turnover"),
            metadata={"column": "Turnover", "source": "CRSP via get_raw_daily_data"},
        )

    def _build_permno_map(
        self, root_path: Path, manifest_path: Path, manifest: pd.DataFrame
    ) -> pd.DataFrame:
        """Build file_name -> permno_int mapping using date-bounded CCM linkage."""
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        if not ccm_path.exists():
            logger.warning(f"CCM file not found: {ccm_path}")
            return pd.DataFrame(columns=["file_name", "permno_int"])

        # Load CCM with link date columns
        all_ccm_cols = pd.read_parquet(ccm_path, columns=None).columns.tolist()
        all_ccm_cols_lower = {c.lower(): c for c in all_ccm_cols}

        ccm_cols = ["gvkey", "LPERMNO"]
        for date_col_lower in ["linkdt", "linkenddt"]:
            actual_col = all_ccm_cols_lower.get(date_col_lower)
            if actual_col:
                ccm_cols.append(actual_col)

        ccm = pd.read_parquet(ccm_path, columns=ccm_cols)

        # Normalize column names
        ccm = ccm.rename(
            columns={c: c.lower() for c in ccm.columns if c.upper() not in ["GVKEY", "LPERMNO"]}
        )
        if "lpermno" in ccm.columns:
            ccm = ccm.rename(columns={"lpermno": "LPERMNO"})

        # Process CCM
        ccm = ccm.copy()
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
        ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
        ccm = ccm[ccm["LPERMNO"].notna()].copy()
        ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)

        # Normalize link dates
        if "linkdt" in ccm.columns:
            ccm["linkdt"] = pd.to_datetime(ccm["linkdt"], errors="coerce")
        else:
            ccm["linkdt"] = pd.NaT

        if "linkenddt" in ccm.columns:
            ccm["linkenddt"] = pd.to_datetime(ccm["linkenddt"], errors="coerce")
            ccm["linkenddt"] = ccm["linkenddt"].fillna(pd.Timestamp("2099-12-31"))
        else:
            ccm["linkenddt"] = pd.Timestamp("2099-12-31")

        # Join manifest to CCM on gvkey
        manifest_subset = manifest[["file_name", "gvkey", "start_date"]].copy()
        joined = manifest_subset.merge(
            ccm[["gvkey", "LPERMNO", "linkdt", "linkenddt"]],
            on="gvkey",
            how="left",
        )

        # Date-bounded filter
        valid_link = (
            joined["linkdt"].isna() | (joined["start_date"] >= joined["linkdt"])
        ) & (joined["start_date"] <= joined["linkenddt"])
        joined = joined[valid_link].copy()

        # If multiple links valid for one call, take the most recent linkdt
        joined = (
            joined.sort_values("linkdt", na_position="first")
            .groupby("file_name")["LPERMNO"]
            .last()
            .reset_index()
            .rename(columns={"LPERMNO": "permno_int"})
        )

        return joined

    def _compute_turnover_vectorized(
        self, manifest: pd.DataFrame, crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Get share turnover at call date for each call (VECTORIZED, memory-efficient).

        Uses nearest prior trading day if call date is not a trading day.
        Processes by year to avoid memory explosion from large merges.
        """
        # Filter manifest to valid permnos
        valid = manifest[manifest["permno_int"].notna()].copy()
        valid["permno_int"] = valid["permno_int"].astype(int)

        if len(valid) == 0:
            result = manifest[["file_name"]].copy()
            result["Turnover"] = np.nan
            return result

        # Prepare CRSP data
        crsp = crsp.copy()
        crsp = crsp[crsp["PERMNO"].notna()].copy()
        crsp["PERMNO"] = crsp["PERMNO"].astype(int)

        # Add year column to CRSP for filtering
        crsp["crsp_year"] = crsp["date"].dt.year

        # Add year column to manifest
        valid["call_year"] = valid["start_date"].dt.year

        # Process by year to avoid memory explosion
        all_results = []

        for year in valid["call_year"].unique():
            if pd.isna(year):
                continue
            year = int(year)

            # Get calls for this year
            year_calls = valid[valid["call_year"] == year].copy()

            if year_calls.empty:
                continue

            # CRITICAL: First filter to only the PERMNOs we need for this year
            # This avoids loading ALL CRSP data for all PERMNOs
            year_permnos = year_calls["permno_int"].unique()
            year_crsp = crsp[
                crsp["PERMNO"].isin(year_permnos) &
                ((crsp["crsp_year"] == year) | (crsp["crsp_year"] == year - 1))
            ].copy()

            if year_crsp.empty:
                continue

            # Merge year's calls with year's CRSP
            merged = year_calls[["file_name", "start_date", "permno_int"]].merge(
                year_crsp[["PERMNO", "date", "VOL", "SHROUT"]],
                left_on="permno_int",
                right_on="PERMNO",
                how="inner",
            )

            if merged.empty:
                continue

            # Filter to dates on or before call date
            merged = merged[merged["date"] <= merged["start_date"]].copy()

            if merged.empty:
                continue

            # For each file_name, get the most recent values
            merged = merged.sort_values(["file_name", "date"], ascending=[True, False])
            latest = merged.groupby("file_name").first().reset_index()

            # Compute turnover
            latest["Turnover"] = np.where(
                (latest["SHROUT"].notna()) & (latest["SHROUT"] > 0) & (latest["VOL"].notna()),
                latest["VOL"] / (latest["SHROUT"] * 1000),
                np.nan
            )

            all_results.append(latest[["file_name", "Turnover"]])

        if not all_results:
            logger.warning("TurnoverBuilder: No matching CRSP data!")
            result = manifest[["file_name"]].copy()
            result["Turnover"] = np.nan
            return result

        # Combine all years
        combined = pd.concat(all_results, ignore_index=True)

        # Merge back to manifest
        result = manifest[["file_name"]].merge(
            combined,
            on="file_name",
            how="left",
        )

        logger.info(f"  TurnoverBuilder: {result['Turnover'].notna().sum():,} valid observations")

        return result


__all__ = ["TurnoverBuilder"]
