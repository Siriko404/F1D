"""Builder for Amihud illiquidity change around earnings calls (H7).

Reads raw CRSP daily stock files via the shared CRSPEngine.get_raw_daily_data().
Returns columns: file_name, delta_amihud, pre_call_amihud.

Event-window calculation (VECTORIZED with year-chunking for memory efficiency):
    daily_illiq_d = |RET_d| / (VOL_d * |PRC_d|) * 1e6
    PreAmihud  = mean(daily_illiq for trading days in pre-window relative to call)
    PostAmihud = mean(daily_illiq for trading days in post-window relative to call)
    DeltaAmihud = PostAmihud - PreAmihud

Uses trading-day positions, not calendar days, to handle weekends/holidays.
Mirrors the BidAskSpreadChangeBuilder design for consistency with H14.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._crsp_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir

logger = logging.getLogger(__name__)

# Minimum valid trading days required in each window
MIN_PRE_DAYS = 2
MIN_POST_DAYS = 2


class AmihudChangeBuilder(VariableBuilder):
    """Compute Amihud illiquidity change around earnings calls (VECTORIZED).

    The dependent variable for H7: delta_amihud = post_avg - pre_avg.
    Also returns pre_call_amihud as a control variable.

    Config options:
        window_days (int): Number of trading days in each window (default 3).
        column_suffix (str): Suffix appended to output columns for non-default windows.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.window_days = config.get("window_days", 3)
        self.column_suffix = config.get("column_suffix", "")

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

        # Load raw CRSP daily data (includes VOL, PRC, RET)
        engine = get_engine()
        crsp_data = engine.get_raw_daily_data(root_path, years=list(years))

        sfx = self.column_suffix
        da_col = f"delta_amihud{sfx}"
        pca_col = f"pre_call_amihud{sfx}"

        if crsp_data.empty:
            logger.warning("AmihudChangeBuilder: No CRSP data loaded!")
            result_df = manifest[["file_name"]].copy()
            result_df[da_col] = np.nan
            result_df[pca_col] = np.nan
            return VariableResult(
                data=result_df,
                stats=self.get_stats(result_df[da_col], da_col),
                metadata={"column": da_col, "source": "CRSP"},
            )

        # Compute amihud change using vectorized operations
        results = self._compute_amihud_change_vectorized(manifest, crsp_data)

        # Rename columns if suffix is set
        if sfx:
            results = results.rename(columns={
                "delta_amihud": da_col,
                "pre_call_amihud": pca_col,
            })

        # Per-year winsorization at 1%/99% — consistent with CRSP engine treatment.
        # delta_amihud is extremely right-skewed (skew~162, kurtosis~29K unwinsorized)
        # due to micro-cap stocks with near-zero dollar volume.
        from .winsorization import winsorize_by_year

        year_lookup = manifest[["file_name", "year"]].drop_duplicates("file_name")
        results = results.merge(year_lookup, on="file_name", how="left")
        winsorize_cols = [c for c in [da_col, pca_col] if c in results.columns]
        results = winsorize_by_year(
            results, winsorize_cols, year_col="year", lower=0.01, upper=0.99,
        )
        results = results.drop(columns=["year"])

        out_cols = ["file_name", da_col, pca_col]
        out_cols = [c for c in out_cols if c in results.columns]

        return VariableResult(
            data=results[out_cols],
            stats=self.get_stats(results[da_col], da_col),
            metadata={
                "column": da_col,
                "source": "CRSP via get_raw_daily_data",
                "window_days": self.window_days,
                "pre_call_amihud": "control variable (pre-call average Amihud)",
            },
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

        # Date-bounded filter: keep rows where linkdt <= start_date <= linkenddt
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

    def _compute_amihud_change_vectorized(
        self, manifest: pd.DataFrame, crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute delta_amihud and pre_call_amihud using vectorized operations.

        Memory-efficient implementation using year-chunking.
        """
        # Filter manifest to valid permnos
        valid = manifest[manifest["permno_int"].notna()].copy()
        valid["permno_int"] = valid["permno_int"].astype(int)

        if len(valid) == 0:
            result = manifest[["file_name"]].copy()
            result["delta_amihud"] = np.nan
            result["pre_call_amihud"] = np.nan
            return result

        # Prepare CRSP data
        crsp = crsp.copy()
        crsp = crsp[crsp["PERMNO"].notna()].copy()
        crsp["PERMNO"] = crsp["PERMNO"].astype(int)
        crsp["crsp_year"] = crsp["date"].dt.year

        valid["call_year"] = valid["start_date"].dt.year

        # Process by year to avoid memory explosion
        all_results = []

        for year in valid["call_year"].unique():
            if pd.isna(year):
                continue
            year = int(year)

            year_calls = valid[valid["call_year"] == year].copy()
            if year_calls.empty:
                continue

            # Filter CRSP to relevant PERMNOs and date range
            year_permnos = year_calls["permno_int"].unique()
            year_crsp = crsp[
                crsp["PERMNO"].isin(year_permnos) &
                (crsp["crsp_year"] >= year - 1) & (crsp["crsp_year"] <= year + 1)
            ].copy()

            if year_crsp.empty:
                continue

            year_results = self._process_year_calls(year_calls, year_crsp)

            if year_results is not None and not year_results.empty:
                all_results.append(year_results)

        if not all_results:
            logger.warning("AmihudChangeBuilder: No valid results!")
            result = manifest[["file_name"]].copy()
            result["delta_amihud"] = np.nan
            result["pre_call_amihud"] = np.nan
            return result

        # Combine all years
        combined = pd.concat(all_results, ignore_index=True)

        # Merge back to manifest
        result = manifest[["file_name"]].merge(
            combined,
            on="file_name",
            how="left",
        )

        logger.info(f"  AmihudChangeBuilder: {result['delta_amihud'].notna().sum():,} valid observations")

        return result

    def _process_year_calls(
        self, year_calls: pd.DataFrame, year_crsp: pd.DataFrame
    ) -> Optional[pd.DataFrame]:
        """Process one year's calls to compute Amihud change."""
        w = self.window_days
        min_pre = max(1, w - 1)
        min_post = max(1, w - 1)

        # Need VOL, PRC, RET for Amihud
        required_crsp_cols = ["PERMNO", "date"]
        for c in ["VOL", "PRC", "RET"]:
            if c in year_crsp.columns:
                required_crsp_cols.append(c)
            else:
                logger.warning(f"AmihudChangeBuilder: Missing CRSP column {c}")
                return None

        merged = year_calls[["file_name", "start_date", "permno_int"]].merge(
            year_crsp[required_crsp_cols],
            left_on="permno_int",
            right_on="PERMNO",
            how="inner",
        )

        if merged.empty:
            return None

        # Filter to calendar window around each call
        cal_window = max(15, w * 5)
        merged["date_diff"] = (merged["date"] - merged["start_date"]).dt.days.abs()
        merged = merged[merged["date_diff"] <= cal_window].copy()

        if merged.empty:
            return None

        # Compute daily Amihud illiquidity for each day
        merged["VOL"] = pd.to_numeric(merged["VOL"], errors="coerce")
        merged["PRC"] = pd.to_numeric(merged["PRC"], errors="coerce")
        merged["RET"] = pd.to_numeric(merged["RET"], errors="coerce")

        merged["dollar_volume"] = merged["VOL"] * merged["PRC"].abs()
        dollar_vol_masked = merged["dollar_volume"].replace(0, np.nan)
        merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked * 1e6
        # Clamp Inf
        merged["daily_illiq"] = merged["daily_illiq"].replace([np.inf, -np.inf], np.nan)

        # Sort by date within each call
        merged = merged.sort_values(["file_name", "date"])

        # Find the reference date (last trading day on or before call)
        merged["is_on_or_before_call"] = merged["date"] <= merged["start_date"]
        call_ref = merged[merged["is_on_or_before_call"]].copy()
        call_ref = call_ref.sort_values(["file_name", "date"])
        call_ref = call_ref.groupby("file_name").last().reset_index()
        call_ref = call_ref[["file_name", "date"]].rename(columns={"date": "call_ref_date"})

        # Merge back to get reference date
        merged = merged.merge(call_ref, on="file_name", how="left")

        # Compute days from reference
        merged["days_from_ref"] = (merged["date"] - merged["call_ref_date"]).dt.days

        # Assign trading-day positions
        pre_mask = merged["days_from_ref"] < 0
        post_mask = merged["days_from_ref"] > 0

        # For pre-call: rank by date descending (most recent = -1)
        merged.loc[pre_mask, "pre_rank"] = (
            merged[pre_mask]
            .groupby("file_name")["date"]
            .rank(ascending=False, method="first")
        )

        # For post-call: rank by date ascending (closest = +1)
        merged.loc[post_mask, "post_rank"] = (
            merged[post_mask]
            .groupby("file_name")["date"]
            .rank(ascending=True, method="first")
        )

        # Get trading days in our windows
        pre_window = merged[pre_mask & (merged["pre_rank"] <= w)].copy()
        post_window = merged[post_mask & (merged["post_rank"] <= w)].copy()

        # Amihud aggregation
        pre_avg = pre_window.groupby("file_name").agg(
            pre_call_amihud=("daily_illiq", "mean"),
            pre_n_valid=("daily_illiq", lambda x: x.notna().sum()),
        ).reset_index()

        post_avg = post_window.groupby("file_name").agg(
            post_call_amihud=("daily_illiq", "mean"),
            post_n_valid=("daily_illiq", lambda x: x.notna().sum()),
        ).reset_index()

        amihud = pre_avg.merge(post_avg, on="file_name", how="outer")
        amihud["delta_amihud"] = amihud["post_call_amihud"] - amihud["pre_call_amihud"]

        # Apply minimum valid days filter
        min_valid_mask = (
            (amihud["pre_n_valid"] >= min_pre) &
            (amihud["post_n_valid"] >= min_post)
        )
        amihud.loc[~min_valid_mask, "delta_amihud"] = np.nan
        amihud.loc[~min_valid_mask, "pre_call_amihud"] = np.nan

        out_cols = ["file_name", "delta_amihud", "pre_call_amihud"]
        return amihud[out_cols]


__all__ = ["AmihudChangeBuilder"]
