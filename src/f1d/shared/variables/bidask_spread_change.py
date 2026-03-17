"""Builder for bid-ask spread change variables around earnings calls (H14).

Reads raw CRSP daily stock files via the shared CRSPEngine.get_raw_daily_data().
Returns columns: file_name, delta_spread, pre_call_spread, and optionally
delta_spread_closing, pre_call_spread_closing, pre_spread_change.

Event-window calculation (VECTORIZED with year-chunking for memory efficiency):
    Spread_d = 2 * (ASKHI - BIDLO) / (ASKHI + BIDLO)          [high-low spread]
    Spread_closing_d = 2 * (ASK - BID) / (ASK + BID)          [closing spread]
    PreSpread  = mean(Spread for trading days in pre-window relative to call)
    PostSpread = mean(Spread for trading days in post-window relative to call)
    DeltaSpread = PostSpread - PreSpread

Uses trading-day positions, not calendar days, to handle weekends/holidays.
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

# Minimum valid trading days required in each window
MIN_PRE_DAYS = 2
MIN_POST_DAYS = 2


class BidAskSpreadChangeBuilder(VariableBuilder):
    """Compute bid-ask spread change around earnings calls (VECTORIZED).

    The dependent variable for H14: delta_spread = post_avg - pre_avg.
    Also returns pre_call_spread as a control variable.

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

        # Load raw CRSP daily data (includes BIDLO, ASKHI, SHROUT)
        engine = get_engine()
        crsp_data = engine.get_raw_daily_data(root_path, years=list(years))

        sfx = self.column_suffix
        ds_col = f"delta_spread{sfx}"
        pcs_col = f"pre_call_spread{sfx}"
        dsc_col = f"delta_spread_closing{sfx}"
        pcsc_col = f"pre_call_spread_closing{sfx}"
        psc_col = f"pre_spread_change{sfx}"

        if crsp_data.empty:
            logger.warning("BidAskSpreadChangeBuilder: No CRSP data loaded!")
            result_df = manifest[["file_name"]].copy()
            result_df[ds_col] = np.nan
            result_df[pcs_col] = np.nan
            result_df[dsc_col] = np.nan
            result_df[pcsc_col] = np.nan
            result_df[psc_col] = np.nan
            return VariableResult(
                data=result_df,
                stats=self.get_stats(result_df[ds_col], ds_col),
                metadata={"column": ds_col, "source": "CRSP"},
            )

        # Compute spread change using vectorized operations
        results = self._compute_spread_change_vectorized(manifest, crsp_data)

        # Rename columns if suffix is set
        if sfx:
            results = results.rename(columns={
                "delta_spread": ds_col,
                "pre_call_spread": pcs_col,
                "delta_spread_closing": dsc_col,
                "pre_call_spread_closing": pcsc_col,
                "pre_spread_change": psc_col,
            })

        out_cols = ["file_name", ds_col, pcs_col, dsc_col, pcsc_col, psc_col]
        # Only include columns that exist
        out_cols = [c for c in out_cols if c in results.columns]

        return VariableResult(
            data=results[out_cols],
            stats=self.get_stats(results[ds_col], ds_col),
            metadata={
                "column": ds_col,
                "source": "CRSP via get_raw_daily_data",
                "window_days": self.window_days,
                "pre_call_spread": f"control variable (pre-call average spread)",
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
        for col_lower in ["linkdt", "linkenddt", "linkprim"]:
            actual_col = all_ccm_cols_lower.get(col_lower)
            if actual_col:
                ccm_cols.append(actual_col)

        ccm = pd.read_parquet(ccm_path, columns=ccm_cols)

        # Normalize column names
        ccm = ccm.rename(
            columns={c: c.lower() for c in ccm.columns if c.upper() not in ["GVKEY", "LPERMNO"]}
        )
        if "lpermno" in ccm.columns:
            ccm = ccm.rename(columns={"lpermno": "LPERMNO"})

        # Filter to primary CCM links only (same as _ibes_engine.py)
        if "linkprim" in ccm.columns:
            before_lp = len(ccm)
            ccm = ccm[ccm["linkprim"].isin(["P", "C"])].copy()
            logger.info(f"LINKPRIM filter: {len(ccm):,} / {before_lp:,} links retained")

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

    def _compute_spread_change_vectorized(
        self, manifest: pd.DataFrame, crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Compute delta_spread and pre_call_spread using vectorized operations.

        Memory-efficient implementation using year-chunking to avoid
        creating massive intermediate arrays from the merge.

        Algorithm:
        1. Process calls by year
        2. For each year, filter CRSP to relevant dates
        3. Merge, filter to event window, compute spreads
        4. Aggregate using groupby
        """
        # Filter manifest to valid permnos
        valid = manifest[manifest["permno_int"].notna()].copy()
        valid["permno_int"] = valid["permno_int"].astype(int)

        if len(valid) == 0:
            result = manifest[["file_name"]].copy()
            result["delta_spread"] = np.nan
            result["pre_call_spread"] = np.nan
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
                (crsp["crsp_year"] >= year - 1) & (crsp["crsp_year"] <= year + 1)
            ].copy()

            if year_crsp.empty:
                continue

            # Process this year's calls
            year_results = self._process_year_calls(year_calls, year_crsp)

            if year_results is not None and not year_results.empty:
                all_results.append(year_results)

        if not all_results:
            logger.warning("BidAskSpreadChangeBuilder: No valid results!")
            result = manifest[["file_name"]].copy()
            result["delta_spread"] = np.nan
            result["pre_call_spread"] = np.nan
            return result

        # Combine all years
        combined = pd.concat(all_results, ignore_index=True)

        # Merge back to manifest — include all output columns
        result = manifest[["file_name"]].merge(
            combined,
            on="file_name",
            how="left",
        )

        logger.info(f"  BidAskSpreadChangeBuilder: {result['delta_spread'].notna().sum():,} valid observations")

        return result

    def _process_year_calls(
        self, year_calls: pd.DataFrame, year_crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Process one year's calls to compute spread change."""
        w = self.window_days
        # Scale minimum valid days with window size
        min_pre = max(1, w - 1)
        min_post = max(1, w - 1)

        # Merge calls with CRSP on PERMNO — include BID/ASK for closing spread
        crsp_cols = ["PERMNO", "date", "BIDLO", "ASKHI"]
        for c in ["BID", "ASK"]:
            if c in year_crsp.columns:
                crsp_cols.append(c)
        merged = year_calls[["file_name", "start_date", "permno_int"]].merge(
            year_crsp[crsp_cols],
            left_on="permno_int",
            right_on="PERMNO",
            how="inner",
        )

        if merged.empty:
            return None

        # Filter to calendar window around each call (scale with window size)
        cal_window = max(15, w * 5)
        merged["date_diff"] = (merged["date"] - merged["start_date"]).dt.days.abs()
        merged = merged[merged["date_diff"] <= cal_window].copy()

        if merged.empty:
            return None

        # Compute high-low spread for each day
        valid_spread_mask = (
            merged["ASKHI"].notna() & merged["BIDLO"].notna() &
            (merged["ASKHI"] > 0) & (merged["BIDLO"] > 0)
        )
        merged["spread"] = np.nan
        merged.loc[valid_spread_mask, "spread"] = (
            2 * (merged.loc[valid_spread_mask, "ASKHI"] - merged.loc[valid_spread_mask, "BIDLO"]) /
            (merged.loc[valid_spread_mask, "ASKHI"] + merged.loc[valid_spread_mask, "BIDLO"])
        )

        # Compute closing spread (BID/ASK) if columns available
        has_closing = "BID" in merged.columns and "ASK" in merged.columns
        if has_closing:
            valid_closing_mask = (
                merged["ASK"].notna() & merged["BID"].notna() &
                (merged["ASK"] > 0) & (merged["BID"] > 0)
            )
            merged["spread_closing"] = np.nan
            merged.loc[valid_closing_mask, "spread_closing"] = (
                2 * (merged.loc[valid_closing_mask, "ASK"] - merged.loc[valid_closing_mask, "BID"]) /
                (merged.loc[valid_closing_mask, "ASK"] + merged.loc[valid_closing_mask, "BID"])
            )

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

        # Get trading days in our windows (parameterized by window_days)
        pre_window = merged[pre_mask & (merged["pre_rank"] <= w)].copy()
        post_window = merged[post_mask & (merged["post_rank"] <= w)].copy()

        # --- High-low spread aggregation ---
        pre_avg = pre_window.groupby("file_name").agg(
            pre_call_spread=("spread", "mean"),
            pre_n_valid=("spread", lambda x: x.notna().sum()),
        ).reset_index()

        post_avg = post_window.groupby("file_name").agg(
            post_call_spread=("spread", "mean"),
            post_n_valid=("spread", lambda x: x.notna().sum()),
        ).reset_index()

        spreads = pre_avg.merge(post_avg, on="file_name", how="outer")
        spreads["delta_spread"] = spreads["post_call_spread"] - spreads["pre_call_spread"]

        # Apply minimum valid days filter
        min_valid_mask = (
            (spreads["pre_n_valid"] >= min_pre) &
            (spreads["post_n_valid"] >= min_post)
        )
        spreads.loc[~min_valid_mask, "delta_spread"] = np.nan
        spreads.loc[~min_valid_mask, "pre_call_spread"] = np.nan

        # --- Closing spread aggregation (L1) ---
        if has_closing:
            pre_avg_c = pre_window.groupby("file_name").agg(
                pre_call_spread_closing=("spread_closing", "mean"),
                pre_n_valid_c=("spread_closing", lambda x: x.notna().sum()),
            ).reset_index()
            post_avg_c = post_window.groupby("file_name").agg(
                post_call_spread_closing=("spread_closing", "mean"),
                post_n_valid_c=("spread_closing", lambda x: x.notna().sum()),
            ).reset_index()
            closing = pre_avg_c.merge(post_avg_c, on="file_name", how="outer")
            closing["delta_spread_closing"] = (
                closing["post_call_spread_closing"] - closing["pre_call_spread_closing"]
            )
            min_valid_c = (
                (closing["pre_n_valid_c"] >= min_pre) &
                (closing["post_n_valid_c"] >= min_post)
            )
            closing.loc[~min_valid_c, "delta_spread_closing"] = np.nan
            closing.loc[~min_valid_c, "pre_call_spread_closing"] = np.nan
            spreads = spreads.merge(
                closing[["file_name", "delta_spread_closing", "pre_call_spread_closing"]],
                on="file_name", how="left",
            )

        # --- Placebo DV (L2): pre-period spread change ---
        # spread on day -1 minus spread on day -(window_days)
        # Tests whether uncertainty predicts spread changes BEFORE the call
        if w >= 2:
            pre_first = pre_window[pre_window["pre_rank"] == w].set_index("file_name")["spread"]
            pre_last = pre_window[pre_window["pre_rank"] == 1].set_index("file_name")["spread"]
            placebo = (pre_last - pre_first).rename("pre_spread_change").reset_index()
            spreads = spreads.merge(placebo, on="file_name", how="left")

        out_cols = ["file_name", "delta_spread", "pre_call_spread"]
        if has_closing:
            out_cols += ["delta_spread_closing", "pre_call_spread_closing"]
        if "pre_spread_change" in spreads.columns:
            out_cols += ["pre_spread_change"]

        return spreads[out_cols]


__all__ = ["BidAskSpreadChangeBuilder"]
