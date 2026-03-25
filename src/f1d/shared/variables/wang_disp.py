"""Builder for WangDISP — Wang (2020) analyst forecast dispersion.

Computes pre-announcement analyst forecast dispersion following Wang (2020,
Review of Accounting and Finance 19(3): 289-312).

Output columns: file_name, WangDISP

Construction:
    WangDISP = SD(latest analyst EPS forecasts in T-31..T-1 window) / prccq_prior
    where:
        - T = earnings announcement date (start_date)
        - Forecasts: each analyst's most recent quarterly EPS forecast issued
          in the 30-day pre-announcement window [T-31, T-1]
        - prccq_prior = prior fiscal quarter-end stock price from Compustat

Filters:
    - FPI in ['6','7'] (loaded by IBES engine; matched by FPEDATS, not FPI)
    - PDF='D' (diluted EPS only)
    - Minimum 2 analysts for valid dispersion
    - FPEDATS within 120 days of call date (date fence)

Winsorization: 1%/99% pooled (Wang 2020 implementation).

Performance: Fully vectorized via merge + groupby. No row-by-row iteration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_detail_engine import get_engine as get_ibes_detail_engine
from ._compustat_engine import get_engine as get_compustat_engine
from f1d.shared.path_utils import get_latest_output_dir


class WangDispBuilder(VariableBuilder):
    """Build WangDISP from IBES Detail + Compustat prccq.

    WangDISP: SD of analyst forecasts issued T-31..T-1, scaled by prior
    quarter-end stock price. Wang (2020) definition.
    """

    NUMEST_MIN = 2  # Minimum analysts for valid dispersion

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.window_days = 31  # T-31 to T-1 (31 calendar days before announcement)
        self.fpedats_max_days = 120  # Date fence for FPEDATS matching

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build WangDISP for all calls."""
        # Load manifest
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest = pd.read_parquet(
            manifest_dir / "master_sample_manifest.parquet",
            columns=["file_name", "gvkey", "start_date"],
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Load IBES Detail data (FPI in [6,7], PDF=D via engine defaults)
        ibes_engine = get_ibes_detail_engine()
        ibes = ibes_engine.get_data(root_path, years)

        # Load Compustat for prccq_lag (prior quarter-end price)
        prccq_lag = self._build_prccq_lag(root_path)

        # Compute Wang dispersion for each call (vectorized)
        results = self._compute_wang_disp(manifest, ibes, prccq_lag)

        # Merge back to ensure all file_names present
        final = manifest[["file_name"]].merge(results, on="file_name", how="left")

        # Winsorize at 1%/99% pooled (Wang 2020)
        valid = final["WangDISP"].dropna()
        if len(valid) > 0:
            lo = valid.quantile(0.01)
            hi = valid.quantile(0.99)
            final["WangDISP"] = final["WangDISP"].clip(lo, hi)
            print(f"    WangDispBuilder: Winsorized WangDISP at [{lo:.6f}, {hi:.6f}]")

        coverage = final["WangDISP"].notna().sum()
        print(f"    WangDispBuilder: Final coverage: {coverage:,} / {len(final):,} "
              f"({100 * coverage / len(final):.1f}%)")

        stats = self.get_stats(final["WangDISP"], "WangDISP")

        return VariableResult(
            data=final,
            stats=stats,
            metadata={
                "columns": ["WangDISP"],
                "source": "IBES Detail + Compustat prccq",
                "window": f"T-{self.window_days} to T-1 (pre-announcement)",
                "denominator": "prccq_lag (prior fiscal quarter-end stock price)",
                "reference": "Wang (2020, RAF 19(3): 289-312)",
                "fpedats_fence_days": self.fpedats_max_days,
                "winsorization": "1%/99% pooled",
            },
        )

    def _build_prccq_lag(self, root_path: Path) -> pd.DataFrame:
        """Build prior quarter-end stock price lookup from Compustat.

        Returns DataFrame with (gvkey, datadate, prccq_lag) where prccq_lag
        is the PRIOR quarter's closing stock price.
        """
        engine = get_compustat_engine()
        comp = engine.get_data(root_path)

        # Extract quarterly price data
        price_cols = ["gvkey", "datadate", "prccq"]
        price = comp[price_cols].dropna(subset=["prccq"]).copy()
        price["gvkey"] = price["gvkey"].astype(str).str.zfill(6)
        price["datadate"] = pd.to_datetime(price["datadate"])

        # Sort and create lagged price (prior quarter)
        price = price.sort_values(["gvkey", "datadate"]).reset_index(drop=True)
        price["prccq_lag"] = price.groupby("gvkey")["prccq"].shift(1)

        # Drop rows without valid lag
        price = price.dropna(subset=["prccq_lag"])

        print(f"    WangDispBuilder: prccq_lag coverage: {len(price):,} firm-quarters")

        return price[["gvkey", "datadate", "prccq_lag"]]

    def _compute_wang_disp(
        self,
        manifest: pd.DataFrame,
        ibes: pd.DataFrame,
        prccq_lag: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute Wang (2020) DISP for each call — fully vectorized.

        Strategy:
        1. Match each call to target FPEDATS via merge_asof (forward, 120d)
        2. Join matched calls with IBES estimates on (gvkey, fpedats)
        3. Filter to T-31..T-1 window, keep latest per analyst, compute SD
        4. Merge prccq_lag, divide SD by prior quarter price
        """
        print(f"    WangDispBuilder: Computing WangDISP for {len(manifest):,} calls...")

        calls = manifest[["file_name", "gvkey", "start_date"]].copy()
        calls["date_min"] = calls["start_date"] - pd.Timedelta(days=self.window_days)
        calls["date_max"] = calls["start_date"] - pd.Timedelta(days=1)

        # ── Step 1: Match calls to target FPEDATS ──
        fpedats_index = (
            ibes[["gvkey", "fpedats"]]
            .drop_duplicates()
            .sort_values(["gvkey", "fpedats"])
            .rename(columns={"fpedats": "target_fpedats"})
        )

        matched_chunks = []
        for gvkey, chunk in calls.sort_values(["gvkey", "start_date"]).groupby("gvkey"):
            fp_chunk = fpedats_index[fpedats_index["gvkey"] == gvkey]
            if len(fp_chunk) == 0:
                chunk = chunk.copy()
                chunk["target_fpedats"] = pd.NaT
                matched_chunks.append(chunk)
                continue
            m = pd.merge_asof(
                chunk.sort_values("start_date"),
                fp_chunk.sort_values("target_fpedats"),
                left_on="start_date",
                right_on="target_fpedats",
                direction="forward",
                tolerance=pd.Timedelta(days=self.fpedats_max_days),
                suffixes=("", "_r"),
            )
            if "gvkey_r" in m.columns:
                m = m.drop(columns=["gvkey_r"])
            matched_chunks.append(m)

        matched = pd.concat(matched_chunks, ignore_index=True)

        n_matched = matched["target_fpedats"].notna().sum()
        print(f"    WangDispBuilder: {n_matched:,} / {len(matched):,} calls matched to FPEDATS")

        matched = matched.dropna(subset=["target_fpedats"])
        if len(matched) == 0:
            return pd.DataFrame(columns=["file_name", "WangDISP"])

        # ── Step 2: Join with IBES estimates on (gvkey, target_fpedats) ──
        estimates = ibes[["gvkey", "fpedats", "actdats", "analys", "value"]].copy()

        pairs = matched[["file_name", "gvkey", "target_fpedats", "date_min", "date_max"]].merge(
            estimates,
            left_on=["gvkey", "target_fpedats"],
            right_on=["gvkey", "fpedats"],
            how="inner",
        )
        pairs = pairs.drop(columns=["fpedats"])

        print(f"    WangDispBuilder: {len(pairs):,} call-estimate pairs")

        # ── Step 3: Wang bulk computation ──
        sd_per_call = self._wang_dispersion_bulk(pairs)

        # ── Step 4: Merge prccq_lag to calls ──
        # merge_asof backward: for each call, find most recent Compustat quarter
        calls_for_price = matched[["file_name", "gvkey", "start_date"]].copy()
        calls_for_price = calls_for_price.sort_values(["gvkey", "start_date"])
        prccq_sorted = prccq_lag.sort_values(["gvkey", "datadate"])

        price_chunks = []
        for gvkey, chunk in calls_for_price.groupby("gvkey"):
            p_chunk = prccq_sorted[prccq_sorted["gvkey"] == gvkey]
            if len(p_chunk) == 0:
                chunk = chunk.copy()
                chunk["prccq_lag"] = np.nan
                price_chunks.append(chunk)
                continue
            m = pd.merge_asof(
                chunk.sort_values("start_date"),
                p_chunk.sort_values("datadate"),
                left_on="start_date",
                right_on="datadate",
                direction="backward",
                suffixes=("", "_comp"),
            )
            if "gvkey_comp" in m.columns:
                m = m.drop(columns=["gvkey_comp"])
            price_chunks.append(m)

        price_matched = pd.concat(price_chunks, ignore_index=True)
        price_matched = price_matched[["file_name", "prccq_lag"]]

        # ── Step 5: Combine SD and price ──
        result = sd_per_call.merge(price_matched, on="file_name", how="left")

        # DISP = SD / prccq_lag (NaN if price missing or <= 0)
        valid_price = result["prccq_lag"].notna() & (result["prccq_lag"] > 0)
        result["WangDISP"] = np.where(
            valid_price & result["_sd"].notna(),
            result["_sd"] / result["prccq_lag"],
            np.nan,
        )

        n_valid = result["WangDISP"].notna().sum()
        print(f"    WangDispBuilder: {n_valid:,} calls with valid WangDISP")

        return result[["file_name", "WangDISP"]]

    def _wang_dispersion_bulk(self, pairs: pd.DataFrame) -> pd.DataFrame:
        """Compute SD of analyst forecasts in T-31..T-1 window.

        Args:
            pairs: DataFrame with file_name, date_min, date_max, actdats, analys, value

        Returns:
            DataFrame with file_name, _sd
        """
        # 1. Filter: estimate must be in [T-31, T-1] window
        active = pairs[
            (pairs["actdats"] >= pairs["date_min"])
            & (pairs["actdats"] <= pairs["date_max"])
        ].copy()

        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 2. Keep latest estimate per (file_name, analyst)
        active = (
            active.sort_values("actdats")
            .groupby(["file_name", "analys"], sort=False)
            .last()
            .reset_index()
        )

        # 3. Count analysts per call, require >= NUMEST_MIN
        analyst_counts = active.groupby("file_name")["analys"].transform("count")
        active = active[analyst_counts >= self.NUMEST_MIN]

        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 4. Compute SD per call
        agg = active.groupby("file_name")["value"].agg("std").reset_index()
        agg.columns = ["file_name", "_sd"]

        return agg


__all__ = ["WangDispBuilder"]
