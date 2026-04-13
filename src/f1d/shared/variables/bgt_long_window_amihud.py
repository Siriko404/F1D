"""Builder for BGT (2018) 25-day post-call Amihud illiquidity (H7c/d/e).

Reads raw CRSP daily stock files via the shared CRSPEngine.get_raw_daily_data().
Returns columns: file_name, BGTLevel_Amihud, BGTDelta_Amihud, BGTAvg_Amihud.

BGT (2018, JAR) verbatim window:
    "the period starting the day of the call and ending 25 trading days
     subsequent to the call"

Three constructions:
    BGTLevel_Amihud: mean over [0, +25] trading days (day 0 INCLUDED -- BGT verbatim)
    BGTDelta_Amihud: mean over [+1, +25] - mean over [-25, -1] (F1D extension; day 0 excluded)
    BGTAvg_Amihud:   mean over [-25, +25] (F1D extension; day 0 INCLUDED; 51-day symmetric)

Daily Amihud formula: |RET| / (VOL * |PRC|) * 1e6
    Identical to AmihudChangeBuilder; matches Amihud (2002) x 1e6 scaling.

Min-valid-days filter (scales with window_days, defaults are tuned for w=25):
    Level:   >= 12 days of 26-day [0, +25] window  (~half coverage)
    Delta:   >= 20 days each of pre [-25, -1] and post [+1, +25] windows (80% coverage)
    Average: >= 25 days of 51-day [-25, +25] window (~half coverage)

Output: per-year winsorization at 1%/99% (matches AmihudChangeBuilder convention).

Documented deviations from BGT (2018):
    - BGT percentile-ranks the output ("to mitigate measurement error");
      we winsorize 1%/99% per-year. F1D pipeline convention.
    - BGT uses an 11-control set (Size, BM, Returns, IdioVol, Coverage, Dispersion,
      MgmtForecast, Surprise, Loss, SpecItems, SmallBeat). The H7c/H7d/H7e runners
      use H7's existing BASE/EXTENDED control set instead. Documented in runner
      docstrings.
    - BGT Delta and BGT Average are F1D-pipeline extensions (window from BGT,
      shape from H7 convention). The Level construction is 100% BGT-verbatim.

Day-0 reference convention:
    Day 0 is identified by EXACT calendar match (date == start_date). For weekday
    calls (>99% of the sample) the call happens on a trading day and day 0 has
    one observation. For rare weekend/holiday calls, day 0 has zero observations
    (BGT-faithful: there is no trading on the call day).
    Pre/post ranking still uses the F1D convention call_ref_date = last trading
    day on or before the call, so for weekend calls the post window starts at the
    next trading day after the call (Monday for a Sunday call) and the pre window
    ends at the trading day before that (Thursday for a Sunday call where Friday
    becomes call_ref_date but is excluded from Pre via days_from_ref<0). The
    weekend-call edge case affects <1% of observations.

Reference: Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic
    complexity in firm disclosures: Obfuscation or information? Journal of
    Accounting Research, 56(1), 85-121.

Source pattern: cloned from AmihudChangeBuilder
    (src/f1d/shared/variables/amihud_change.py) with the trading-day position
    logic widened to a 25-day window each side and split into 3 output columns.
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


class BGTLongWindowAmihudBuilder(VariableBuilder):
    """Compute BGT (2018) long-window Amihud illiquidity around earnings calls.

    Returns 3 output columns per call:
        BGTLevel_Amihud: mean over [0, +25] (day 0 INCLUDED, BGT verbatim)
        BGTDelta_Amihud: mean over [+1, +25] - mean over [-25, -1] (F1D extension)
        BGTAvg_Amihud:   mean over [-25, +25] (day 0 INCLUDED, F1D extension)

    See module docstring for full construction details and BGT references.

    Config options:
        window_days (int): Trading days in each side of the window (default 25).
                           BGT 2018 uses 25; do not change without updating the
                           runner docstrings' referee defense.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.window_days = config.get("window_days", 25)
        # Min-valid-days thresholds (scale with window_days for parameterization)
        self.min_level = max(1, self.window_days // 2)            # 12 for w=25
        self.min_delta_side = max(1, (self.window_days * 4) // 5)  # 20 for w=25
        self.min_avg = max(1, self.window_days)                    # 25 for w=25

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Build permno mapping using date-bounded CCM linkage
        permno_map = self._build_permno_map(root_path, manifest_path, manifest)
        manifest = manifest.merge(permno_map, on="file_name", how="left")

        # Load raw CRSP daily data via singleton (cached if H7 panel already loaded)
        engine = get_engine()
        crsp_data = engine.get_raw_daily_data(root_path, years=list(years))

        out_col_names = ["BGTLevel_Amihud", "BGTDelta_Amihud", "BGTAvg_Amihud"]

        if crsp_data.empty:
            logger.warning("BGTLongWindowAmihudBuilder: No CRSP data loaded!")
            result_df = manifest[["file_name"]].copy()
            for col in out_col_names:
                result_df[col] = np.nan
            return VariableResult(
                data=result_df,
                stats=self.get_stats(result_df["BGTLevel_Amihud"], "BGTLevel_Amihud"),
                metadata={"column": "BGTLevel_Amihud", "source": "CRSP"},
            )

        results = self._compute_bgt_amihud_vectorized(manifest, crsp_data)

        # Per-year winsorization at 1%/99% -- matches AmihudChangeBuilder convention.
        # NOTE: BGT (2018) percentile-ranks instead of winsorizing; this is a
        # documented F1D pipeline-convention deviation. See module docstring.
        from .winsorization import winsorize_by_year

        year_lookup = manifest[["file_name", "year"]].drop_duplicates("file_name")
        results = results.merge(year_lookup, on="file_name", how="left")
        winsorize_cols = [c for c in out_col_names if c in results.columns]
        results = winsorize_by_year(
            results, winsorize_cols, year_col="year", lower=0.01, upper=0.99,
        )
        results = results.drop(columns=["year"])

        out_cols = ["file_name"] + [c for c in out_col_names if c in results.columns]

        return VariableResult(
            data=results[out_cols],
            stats=self.get_stats(results["BGTLevel_Amihud"], "BGTLevel_Amihud"),
            metadata={
                "column": "BGTLevel_Amihud",
                "source": "CRSP via get_raw_daily_data",
                "window_days": self.window_days,
                "BGTLevel_Amihud": "mean Amihud over [0, +25], day 0 INCLUDED (BGT 2018 verbatim)",
                "BGTDelta_Amihud": "mean Amihud over [+1, +25] - mean over [-25, -1] (F1D extension)",
                "BGTAvg_Amihud": "mean Amihud over [-25, +25], day 0 INCLUDED (F1D extension, 51-day)",
                "reference": "Bushee, Gow & Taylor (2018, JAR) 56(1):85-121",
            },
        )

    def _build_permno_map(
        self, root_path: Path, manifest_path: Path, manifest: pd.DataFrame
    ) -> pd.DataFrame:
        """Build file_name -> permno_int mapping using date-bounded CCM linkage.

        Cloned from AmihudChangeBuilder._build_permno_map for consistency with the
        H7 panel's existing CCM linkage. Same date-bounded logic, no linkprim filter.
        """
        ccm_path = (
            root_path / "inputs" / "CRSPCompustat_CCM" / "CRSPCompustat_CCM.parquet"
        )

        if not ccm_path.exists():
            logger.warning(f"CCM file not found: {ccm_path}")
            return pd.DataFrame(columns=["file_name", "permno_int"])

        all_ccm_cols = pd.read_parquet(ccm_path, columns=None).columns.tolist()
        all_ccm_cols_lower = {c.lower(): c for c in all_ccm_cols}

        ccm_cols = ["gvkey", "LPERMNO"]
        for date_col_lower in ["linkdt", "linkenddt"]:
            actual_col = all_ccm_cols_lower.get(date_col_lower)
            if actual_col:
                ccm_cols.append(actual_col)

        ccm = pd.read_parquet(ccm_path, columns=ccm_cols)

        ccm = ccm.rename(
            columns={c: c.lower() for c in ccm.columns if c.upper() not in ["GVKEY", "LPERMNO"]}
        )
        if "lpermno" in ccm.columns:
            ccm = ccm.rename(columns={"lpermno": "LPERMNO"})

        ccm = ccm.copy()
        ccm["gvkey"] = ccm["gvkey"].astype(str).str.zfill(6)
        ccm["LPERMNO"] = pd.to_numeric(ccm["LPERMNO"], errors="coerce")
        ccm = ccm[ccm["LPERMNO"].notna()].copy()
        ccm["LPERMNO"] = ccm["LPERMNO"].astype(int)

        if "linkdt" in ccm.columns:
            ccm["linkdt"] = pd.to_datetime(ccm["linkdt"], errors="coerce")
        else:
            ccm["linkdt"] = pd.NaT

        if "linkenddt" in ccm.columns:
            ccm["linkenddt"] = pd.to_datetime(ccm["linkenddt"], errors="coerce")
            ccm["linkenddt"] = ccm["linkenddt"].fillna(pd.Timestamp("2099-12-31"))
        else:
            ccm["linkenddt"] = pd.Timestamp("2099-12-31")

        manifest_subset = manifest[["file_name", "gvkey", "start_date"]].copy()
        joined = manifest_subset.merge(
            ccm[["gvkey", "LPERMNO", "linkdt", "linkenddt"]],
            on="gvkey",
            how="left",
        )

        valid_link = (
            joined["linkdt"].isna() | (joined["start_date"] >= joined["linkdt"])
        ) & (joined["start_date"] <= joined["linkenddt"])
        joined = joined[valid_link].copy()

        joined = (
            joined.sort_values("linkdt", na_position="first")
            .groupby("file_name")["LPERMNO"]
            .last()
            .reset_index()
            .rename(columns={"LPERMNO": "permno_int"})
        )

        return joined

    def _compute_bgt_amihud_vectorized(
        self, manifest: pd.DataFrame, crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Year-chunked computation of the 3 BGT Amihud variants.

        Memory-safe pattern: process one call_year at a time, filter CRSP to
        relevant PERMNOs and a +/- 1 year window, then explicit del to release
        the year-chunk before moving on.
        """
        out_col_names = ["BGTLevel_Amihud", "BGTDelta_Amihud", "BGTAvg_Amihud"]

        valid = manifest[manifest["permno_int"].notna()].copy()
        valid["permno_int"] = valid["permno_int"].astype(int)

        if len(valid) == 0:
            result = manifest[["file_name"]].copy()
            for col in out_col_names:
                result[col] = np.nan
            return result

        crsp = crsp.copy()
        crsp = crsp[crsp["PERMNO"].notna()].copy()
        crsp["PERMNO"] = crsp["PERMNO"].astype(int)
        crsp["crsp_year"] = crsp["date"].dt.year

        valid["call_year"] = valid["start_date"].dt.year

        all_results = []

        for year in valid["call_year"].unique():
            if pd.isna(year):
                continue
            year = int(year)

            year_calls = valid[valid["call_year"] == year].copy()
            if year_calls.empty:
                continue

            # Filter CRSP to year +/- 1 (25-day window can cross year boundaries)
            year_permnos = year_calls["permno_int"].unique()
            year_crsp = crsp[
                crsp["PERMNO"].isin(year_permnos) &
                (crsp["crsp_year"] >= year - 1) & (crsp["crsp_year"] <= year + 1)
            ].copy()

            if year_crsp.empty:
                del year_calls
                continue

            year_results = self._process_year_calls(year_calls, year_crsp)

            if year_results is not None and not year_results.empty:
                all_results.append(year_results)

            # Explicit memory cleanup per feedback_memory_safe_builders
            del year_crsp, year_calls

        if not all_results:
            logger.warning("BGTLongWindowAmihudBuilder: No valid results!")
            result = manifest[["file_name"]].copy()
            for col in out_col_names:
                result[col] = np.nan
            return result

        combined = pd.concat(all_results, ignore_index=True)

        result = manifest[["file_name"]].merge(
            combined,
            on="file_name",
            how="left",
        )

        logger.info(
            f"  BGTLongWindowAmihudBuilder: "
            f"Level={result['BGTLevel_Amihud'].notna().sum():,}, "
            f"Delta={result['BGTDelta_Amihud'].notna().sum():,}, "
            f"Avg={result['BGTAvg_Amihud'].notna().sum():,}"
        )

        return result

    def _process_year_calls(
        self, year_calls: pd.DataFrame, year_crsp: pd.DataFrame
    ) -> Optional[pd.DataFrame]:
        """Process one year's calls to compute the 3 BGT Amihud variants."""
        w = self.window_days

        required_crsp_cols = ["PERMNO", "date"]
        for c in ["VOL", "PRC", "RET"]:
            if c in year_crsp.columns:
                required_crsp_cols.append(c)
            else:
                logger.warning(f"BGTLongWindowAmihudBuilder: Missing CRSP column {c}")
                return None

        merged = year_calls[["file_name", "start_date", "permno_int"]].merge(
            year_crsp[required_crsp_cols],
            left_on="permno_int",
            right_on="PERMNO",
            how="inner",
        )

        if merged.empty:
            return None

        # Filter to +/- 50 calendar days around each call (covers +/- 25 trading
        # days plus weekend/holiday buffer; 25 trading days <= 35 calendar days)
        cal_window = max(40, w * 2)
        merged["date_diff"] = (merged["date"] - merged["start_date"]).dt.days.abs()
        merged = merged[merged["date_diff"] <= cal_window].copy()

        if merged.empty:
            return None

        # Compute daily Amihud illiquidity: |RET| / (VOL * |PRC|) * 1e6
        merged["VOL"] = pd.to_numeric(merged["VOL"], errors="coerce")
        merged["PRC"] = pd.to_numeric(merged["PRC"], errors="coerce")
        merged["RET"] = pd.to_numeric(merged["RET"], errors="coerce")

        merged["dollar_volume"] = merged["VOL"] * merged["PRC"].abs()
        dollar_vol_masked = merged["dollar_volume"].replace(0, np.nan)
        merged["daily_illiq"] = merged["RET"].abs() / dollar_vol_masked * 1e6
        merged["daily_illiq"] = merged["daily_illiq"].replace([np.inf, -np.inf], np.nan)

        # Sort by date within each call
        merged = merged.sort_values(["file_name", "date"])

        # Reference date = last trading day on or before call (F1D convention).
        # For weekday calls, this is the call day itself.
        merged["is_on_or_before_call"] = merged["date"] <= merged["start_date"]
        call_ref = merged[merged["is_on_or_before_call"]].copy()
        call_ref = call_ref.sort_values(["file_name", "date"])
        call_ref = call_ref.groupby("file_name").last().reset_index()
        call_ref = call_ref[["file_name", "date"]].rename(columns={"date": "call_ref_date"})

        merged = merged.merge(call_ref, on="file_name", how="left")
        merged["days_from_ref"] = (merged["date"] - merged["call_ref_date"]).dt.days

        # Three masks:
        #   day0  = exact calendar match to start_date (BGT-faithful: weekend
        #           calls have day0_n=0 because there is no trading on call day)
        #   pre   = days_from_ref <  0 (trading days strictly before call_ref_date)
        #   post  = days_from_ref >  0 (trading days strictly after  call_ref_date)
        day0_mask = merged["date"] == merged["start_date"]
        pre_mask = merged["days_from_ref"] < 0
        post_mask = merged["days_from_ref"] > 0

        # Trading-day positions: rank within each (file_name, mask) by date
        # pre_rank: 1 = closest trading day before call_ref_date
        merged.loc[pre_mask, "pre_rank"] = (
            merged[pre_mask]
            .groupby("file_name")["date"]
            .rank(ascending=False, method="first")
        )
        # post_rank: 1 = closest trading day after call_ref_date
        merged.loc[post_mask, "post_rank"] = (
            merged[post_mask]
            .groupby("file_name")["date"]
            .rank(ascending=True, method="first")
        )

        # Restrict each side to the first w trading days from the reference
        pre_window = merged[pre_mask & (merged["pre_rank"] <= w)].copy()
        post_window = merged[post_mask & (merged["post_rank"] <= w)].copy()
        day0_rows = merged[day0_mask].copy()

        # Per-call aggregates: mean and count of non-null daily_illiq
        pre_agg = pre_window.groupby("file_name").agg(
            pre_mean=("daily_illiq", "mean"),
            pre_n=("daily_illiq", lambda x: x.notna().sum()),
        ).reset_index()
        post_agg = post_window.groupby("file_name").agg(
            post_mean=("daily_illiq", "mean"),
            post_n=("daily_illiq", lambda x: x.notna().sum()),
        ).reset_index()
        day0_agg = day0_rows.groupby("file_name").agg(
            day0_illiq=("daily_illiq", "mean"),
            day0_n=("daily_illiq", lambda x: x.notna().sum()),
        ).reset_index()

        # Combine on call universe (one row per call_year-call)
        result = year_calls[["file_name"]].drop_duplicates().copy()
        result = result.merge(pre_agg, on="file_name", how="left")
        result = result.merge(post_agg, on="file_name", how="left")
        result = result.merge(day0_agg, on="file_name", how="left")

        # Fill counts to enable arithmetic; means stay NaN if window empty
        result["pre_n"] = result["pre_n"].fillna(0).astype(int)
        result["post_n"] = result["post_n"].fillna(0).astype(int)
        result["day0_n"] = result["day0_n"].fillna(0).astype(int)

        # ============================================================
        # BGTLevel_Amihud: sample-size-weighted mean over day0 + post
        #   = (day0_sum + post_sum) / (day0_n + post_n)
        # where pre/post means * counts give sums of non-null daily values
        # ============================================================
        level_n = result["day0_n"] + result["post_n"]
        level_sum = (
            result["day0_illiq"].fillna(0) * result["day0_n"]
            + result["post_mean"].fillna(0) * result["post_n"]
        )
        result["BGTLevel_Amihud"] = level_sum / level_n.replace(0, np.nan)
        result.loc[level_n < self.min_level, "BGTLevel_Amihud"] = np.nan

        # ============================================================
        # BGTDelta_Amihud: post_mean - pre_mean (day 0 EXCLUDED, F1D extension)
        # ============================================================
        result["BGTDelta_Amihud"] = result["post_mean"] - result["pre_mean"]
        bad_delta_mask = (
            (result["pre_n"] < self.min_delta_side)
            | (result["post_n"] < self.min_delta_side)
        )
        result.loc[bad_delta_mask, "BGTDelta_Amihud"] = np.nan

        # ============================================================
        # BGTAvg_Amihud: sample-size-weighted mean over [-25, +25] inclusive
        # ============================================================
        avg_n = result["pre_n"] + result["day0_n"] + result["post_n"]
        avg_sum = (
            result["pre_mean"].fillna(0) * result["pre_n"]
            + result["day0_illiq"].fillna(0) * result["day0_n"]
            + result["post_mean"].fillna(0) * result["post_n"]
        )
        result["BGTAvg_Amihud"] = avg_sum / avg_n.replace(0, np.nan)
        result.loc[avg_n < self.min_avg, "BGTAvg_Amihud"] = np.nan

        out_cols = ["file_name", "BGTLevel_Amihud", "BGTDelta_Amihud", "BGTAvg_Amihud"]
        return result[out_cols]


__all__ = ["BGTLongWindowAmihudBuilder"]
