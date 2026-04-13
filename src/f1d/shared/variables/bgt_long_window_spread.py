"""Builder for BGT (2018) 25-day post-call closing bid-ask spread (H14c/d/e).

Reads raw CRSP daily stock files via the shared CRSPEngine.get_raw_daily_data().
Returns columns: file_name, BGTLevel_Spread, BGTDelta_Spread, BGTAvg_Spread.

Hybrid construction: window from BGT (2018), formula from Lee (2016).
    BGT (2018, JAR) provides the verbatim 25-day post-call window:
        "the period starting the day of the call and ending 25 trading days
         subsequent to the call"
    BGT itself uses an intraday Madhavan-Richardson-Roomans structural lambda
    estimated from TAQ data, which is NOT compatible with our daily-CRSP setting.
    We adapt BGT's window to Lee (2016, TAR)'s closing-quote spread formula:
        Spread_d = 2 * (ASK_d - BID_d) / (ASK_d + BID_d)
    using CRSP daily closing BID/ASK columns. This hybrid is documented as a
    deviation in the runner docstrings (window from BGT, formula from Lee).

CRITICAL: this builder uses CRSP `BID` / `ASK` (closing quotes) ONLY, never
`BIDLO` / `ASKHI` (intraday low/high). Mixing the two would put `BGTLevel_Spread`
on a different scale than the existing H14 `DSPREAD` column (which is also
closing-quote -- see `bidask_spread_change.py:339-349` for the existing pattern)
and would break the algebraic identity `PostCallSpread = PreCallSpread + DSPREAD`
that H14b's runner-time computation relies on. The high-low spread is built
separately by `BidAskSpreadChangeBuilder` and exposed as `delta_spread` /
`pre_call_spread` (legacy columns). Those legacy columns are NOT touched here.

Three constructions (mirroring BGTLongWindowAmihudBuilder):
    BGTLevel_Spread: mean over [0, +25] trading days (day 0 INCLUDED -- BGT verbatim)
    BGTDelta_Spread: mean over [+1, +25] - mean over [-25, -1] (F1D extension)
    BGTAvg_Spread:   mean over [-25, +25] (F1D extension; 51-day symmetric)

Min-valid-days filter (scales with window_days, defaults are tuned for w=25):
    Level:   >= 12 days of 26-day [0, +25] window
    Delta:   >= 20 days each of pre [-25, -1] and post [+1, +25] windows
    Average: >= 25 days of 51-day [-25, +25] window

Crossed quotes (BID > ASK or non-positive BID/ASK) excluded per Balakrishnan
et al (2014, JF) convention already in use in BidAskSpreadChangeBuilder.

Output: pooled winsorization at 1%/99% is NOT applied here -- the existing
H14 panel builder applies pooled winsorization at the panel level (line 203 of
build_h14_bidask_spread_panel.py) for DSPREAD/PreCallSpread/StockPrice/etc.
The new BGT spread columns will receive the same pooled winsorization when
they're added to the H14 panel builder's `winsorize_cols` list in Phase C.

Documented deviations:
    - Window from BGT (2018), formula from Lee (2016) -- Frankenstein construction
      forced by BGT's intraday-only spread methodology. Documented in runner
      docstrings.
    - BGT's spread variant uses TAQ intraday MRR lambda; not relevant for daily CRSP.
    - BGT Delta and BGT Average are F1D-pipeline extensions (window from BGT,
      shape from H14 convention). The Level construction follows BGT's window
      definition verbatim but with Lee's formula.

Day-0 reference convention: identical to BGTLongWindowAmihudBuilder. Day 0 is
identified by EXACT calendar match (date == start_date). Weekend/holiday call
edge case affects <1% of observations. See bgt_long_window_amihud.py module
docstring for details.

References:
    Bushee, B. J., Gow, I. D., & Taylor, D. J. (2018). Linguistic complexity in
        firm disclosures: Obfuscation or information? Journal of Accounting
        Research, 56(1), 85-121.
    Lee, K. (2016). Information asymmetry around earnings announcements during
        the financial crisis. The Accounting Review.

Source pattern: cloned from BidAskSpreadChangeBuilder
    (src/f1d/shared/variables/bidask_spread_change.py) with the trading-day
    position logic widened to 25-day windows each side and split into 3 output
    columns. _build_permno_map preserves the LINKPRIM = P/C filter that the
    existing spread builder uses (the Amihud builder does NOT have this filter
    -- different historical conventions, preserved per builder for consistency
    with the analog).
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


class BGTLongWindowSpreadBuilder(VariableBuilder):
    """Compute BGT (2018) long-window closing bid-ask spread around earnings calls.

    Returns 3 output columns per call:
        BGTLevel_Spread: mean over [0, +25] (day 0 INCLUDED, BGT verbatim window)
        BGTDelta_Spread: mean over [+1, +25] - mean over [-25, -1] (F1D extension)
        BGTAvg_Spread:   mean over [-25, +25] (day 0 INCLUDED, F1D extension)

    Daily spread formula (Lee 2016 closing-quote):
        Spread_d = 2 * (ASK_d - BID_d) / (ASK_d + BID_d)

    See module docstring for full construction details, BGT/Lee references,
    and BID/ASK vs BIDLO/ASKHI critical-instruction note.

    Config options:
        window_days (int): Trading days in each side of the window (default 25).
                           BGT 2018 uses 25; do not change without updating the
                           runner docstrings' referee defense.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.window_days = config.get("window_days", 25)
        # Min-valid-days thresholds (scale with window_days, tuned for w=25)
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

        # Build permno mapping (LINKPRIM filter, matches BidAskSpreadChangeBuilder)
        permno_map = self._build_permno_map(root_path, manifest_path, manifest)
        manifest = manifest.merge(permno_map, on="file_name", how="left")

        # Load raw CRSP daily data via singleton (cached by H14 panel preceding it)
        engine = get_engine()
        crsp_data = engine.get_raw_daily_data(root_path, years=list(years))

        out_col_names = ["BGTLevel_Spread", "BGTDelta_Spread", "BGTAvg_Spread"]

        if crsp_data.empty:
            logger.warning("BGTLongWindowSpreadBuilder: No CRSP data loaded!")
            result_df = manifest[["file_name"]].copy()
            for col in out_col_names:
                result_df[col] = np.nan
            return VariableResult(
                data=result_df,
                stats=self.get_stats(result_df["BGTLevel_Spread"], "BGTLevel_Spread"),
                metadata={"column": "BGTLevel_Spread", "source": "CRSP"},
            )

        results = self._compute_bgt_spread_vectorized(manifest, crsp_data)

        # NOTE: no winsorization here. The H14 panel builder applies pooled
        # 1%/99% winsorization to the spread columns at panel-build time
        # (line 203 of build_h14_bidask_spread_panel.py). Phase C of the
        # liquidity-extension plan adds the 3 BGT spread columns to that
        # winsorize_cols list so they receive the same treatment as DSPREAD
        # and PreCallSpread. Don't double-winsorize here.

        out_cols = ["file_name"] + [c for c in out_col_names if c in results.columns]

        return VariableResult(
            data=results[out_cols],
            stats=self.get_stats(results["BGTLevel_Spread"], "BGTLevel_Spread"),
            metadata={
                "column": "BGTLevel_Spread",
                "source": "CRSP via get_raw_daily_data (closing BID/ASK)",
                "window_days": self.window_days,
                "BGTLevel_Spread": "mean closing-quote spread over [0, +25], day 0 INCLUDED (BGT 2018 window, Lee 2016 formula)",
                "BGTDelta_Spread": "mean spread [+1, +25] - mean [-25, -1] (F1D extension)",
                "BGTAvg_Spread": "mean spread over [-25, +25], day 0 INCLUDED (F1D extension, 51-day)",
                "reference": "Bushee, Gow & Taylor (2018, JAR) [window]; Lee (2016, TAR) [formula]",
            },
        )

    def _build_permno_map(
        self, root_path: Path, manifest_path: Path, manifest: pd.DataFrame
    ) -> pd.DataFrame:
        """Build file_name -> permno_int mapping using date-bounded CCM linkage.

        Cloned from BidAskSpreadChangeBuilder._build_permno_map for consistency
        with the H14 panel's existing CCM linkage. Includes LINKPRIM = P/C
        filter (the AmihudChangeBuilder version does NOT have this filter --
        different historical conventions, preserved per builder for consistency
        with the analog).
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
        for col_lower in ["linkdt", "linkenddt", "linkprim"]:
            actual_col = all_ccm_cols_lower.get(col_lower)
            if actual_col:
                ccm_cols.append(actual_col)

        ccm = pd.read_parquet(ccm_path, columns=ccm_cols)

        ccm = ccm.rename(
            columns={c: c.lower() for c in ccm.columns if c.upper() not in ["GVKEY", "LPERMNO"]}
        )
        if "lpermno" in ccm.columns:
            ccm = ccm.rename(columns={"lpermno": "LPERMNO"})

        # LINKPRIM = P / C filter (matches BidAskSpreadChangeBuilder + _ibes_engine)
        if "linkprim" in ccm.columns:
            before_lp = len(ccm)
            ccm = ccm[ccm["linkprim"].isin(["P", "C"])].copy()
            logger.info(f"LINKPRIM filter: {len(ccm):,} / {before_lp:,} links retained")

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

    def _compute_bgt_spread_vectorized(
        self, manifest: pd.DataFrame, crsp: pd.DataFrame
    ) -> pd.DataFrame:
        """Year-chunked computation of the 3 BGT spread variants.

        Memory-safe pattern: process one call_year at a time, filter CRSP to
        relevant PERMNOs and a +/- 1 year window, then explicit del to release
        the year-chunk before moving on.
        """
        out_col_names = ["BGTLevel_Spread", "BGTDelta_Spread", "BGTAvg_Spread"]

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
            logger.warning("BGTLongWindowSpreadBuilder: No valid results!")
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
            f"  BGTLongWindowSpreadBuilder: "
            f"Level={result['BGTLevel_Spread'].notna().sum():,}, "
            f"Delta={result['BGTDelta_Spread'].notna().sum():,}, "
            f"Avg={result['BGTAvg_Spread'].notna().sum():,}"
        )

        return result

    def _process_year_calls(
        self, year_calls: pd.DataFrame, year_crsp: pd.DataFrame
    ) -> Optional[pd.DataFrame]:
        """Process one year's calls to compute the 3 BGT spread variants."""
        w = self.window_days

        # Required columns: PERMNO, date, BID, ASK (CLOSING quotes -- not BIDLO/ASKHI)
        required_crsp_cols = ["PERMNO", "date"]
        for c in ["BID", "ASK"]:
            if c in year_crsp.columns:
                required_crsp_cols.append(c)
            else:
                logger.warning(
                    f"BGTLongWindowSpreadBuilder: Missing CRSP column {c} "
                    f"(required for closing-quote spread; do NOT fall back to BIDLO/ASKHI)"
                )
                return None

        merged = year_calls[["file_name", "start_date", "permno_int"]].merge(
            year_crsp[required_crsp_cols],
            left_on="permno_int",
            right_on="PERMNO",
            how="inner",
        )

        if merged.empty:
            return None

        # Filter to +/- 50 calendar days around each call
        cal_window = max(40, w * 2)
        merged["date_diff"] = (merged["date"] - merged["start_date"]).dt.days.abs()
        merged = merged[merged["date_diff"] <= cal_window].copy()

        if merged.empty:
            return None

        # Compute daily closing-quote spread (Lee 2016): 2 * (ASK - BID) / (ASK + BID)
        # Crossed-quote and non-positive-quote rows excluded (Balakrishnan et al 2014).
        merged["BID"] = pd.to_numeric(merged["BID"], errors="coerce")
        merged["ASK"] = pd.to_numeric(merged["ASK"], errors="coerce")
        valid_quote_mask = (
            merged["BID"].notna() & merged["ASK"].notna()
            & (merged["BID"] > 0) & (merged["ASK"] > 0)
            & (merged["ASK"] >= merged["BID"])
        )
        merged["daily_spread"] = np.nan
        merged.loc[valid_quote_mask, "daily_spread"] = (
            2.0 * (merged.loc[valid_quote_mask, "ASK"] - merged.loc[valid_quote_mask, "BID"])
            / (merged.loc[valid_quote_mask, "ASK"] + merged.loc[valid_quote_mask, "BID"])
        )

        # Sort by date within each call
        merged = merged.sort_values(["file_name", "date"])

        # Reference date = last trading day on or before call (F1D convention).
        merged["is_on_or_before_call"] = merged["date"] <= merged["start_date"]
        call_ref = merged[merged["is_on_or_before_call"]].copy()
        call_ref = call_ref.sort_values(["file_name", "date"])
        call_ref = call_ref.groupby("file_name").last().reset_index()
        call_ref = call_ref[["file_name", "date"]].rename(columns={"date": "call_ref_date"})

        merged = merged.merge(call_ref, on="file_name", how="left")
        merged["days_from_ref"] = (merged["date"] - merged["call_ref_date"]).dt.days

        # Three masks (BGT-faithful day0 via exact calendar match)
        day0_mask = merged["date"] == merged["start_date"]
        pre_mask = merged["days_from_ref"] < 0
        post_mask = merged["days_from_ref"] > 0

        # Trading-day positions
        merged.loc[pre_mask, "pre_rank"] = (
            merged[pre_mask]
            .groupby("file_name")["date"]
            .rank(ascending=False, method="first")
        )
        merged.loc[post_mask, "post_rank"] = (
            merged[post_mask]
            .groupby("file_name")["date"]
            .rank(ascending=True, method="first")
        )

        # Restrict windows to first w trading days each side
        pre_window = merged[pre_mask & (merged["pre_rank"] <= w)].copy()
        post_window = merged[post_mask & (merged["post_rank"] <= w)].copy()
        day0_rows = merged[day0_mask].copy()

        # Per-call aggregates
        pre_agg = pre_window.groupby("file_name").agg(
            pre_mean=("daily_spread", "mean"),
            pre_n=("daily_spread", lambda x: x.notna().sum()),
        ).reset_index()
        post_agg = post_window.groupby("file_name").agg(
            post_mean=("daily_spread", "mean"),
            post_n=("daily_spread", lambda x: x.notna().sum()),
        ).reset_index()
        day0_agg = day0_rows.groupby("file_name").agg(
            day0_spread=("daily_spread", "mean"),
            day0_n=("daily_spread", lambda x: x.notna().sum()),
        ).reset_index()

        result = year_calls[["file_name"]].drop_duplicates().copy()
        result = result.merge(pre_agg, on="file_name", how="left")
        result = result.merge(post_agg, on="file_name", how="left")
        result = result.merge(day0_agg, on="file_name", how="left")

        result["pre_n"] = result["pre_n"].fillna(0).astype(int)
        result["post_n"] = result["post_n"].fillna(0).astype(int)
        result["day0_n"] = result["day0_n"].fillna(0).astype(int)

        # ============================================================
        # BGTLevel_Spread: sample-size-weighted mean over day0 + post
        # ============================================================
        level_n = result["day0_n"] + result["post_n"]
        level_sum = (
            result["day0_spread"].fillna(0) * result["day0_n"]
            + result["post_mean"].fillna(0) * result["post_n"]
        )
        result["BGTLevel_Spread"] = level_sum / level_n.replace(0, np.nan)
        result.loc[level_n < self.min_level, "BGTLevel_Spread"] = np.nan

        # ============================================================
        # BGTDelta_Spread: post_mean - pre_mean (day 0 EXCLUDED, F1D extension)
        # ============================================================
        result["BGTDelta_Spread"] = result["post_mean"] - result["pre_mean"]
        bad_delta_mask = (
            (result["pre_n"] < self.min_delta_side)
            | (result["post_n"] < self.min_delta_side)
        )
        result.loc[bad_delta_mask, "BGTDelta_Spread"] = np.nan

        # ============================================================
        # BGTAvg_Spread: sample-size-weighted mean over [-25, +25] inclusive
        # ============================================================
        avg_n = result["pre_n"] + result["day0_n"] + result["post_n"]
        avg_sum = (
            result["pre_mean"].fillna(0) * result["pre_n"]
            + result["day0_spread"].fillna(0) * result["day0_n"]
            + result["post_mean"].fillna(0) * result["post_n"]
        )
        result["BGTAvg_Spread"] = avg_sum / avg_n.replace(0, np.nan)
        result.loc[avg_n < self.min_avg, "BGTAvg_Spread"] = np.nan

        out_cols = ["file_name", "BGTLevel_Spread", "BGTDelta_Spread", "BGTAvg_Spread"]
        return result[out_cols]


__all__ = ["BGTLongWindowSpreadBuilder"]
