"""Builder for PostCallDispersion and PreCallDispersion (H5 DV and control).

Computes post-call and pre-call analyst forecast dispersion around earnings calls
using IBES Detail data (individual analyst estimates).

Output columns: file_name, PreCallDispersion, PostCallDispersion

Construction (Druz, Petzev, Wagner & Zeckhauser 2020; Diether, Malloy & Scherbina 2002):
    PostCallDispersion = SD(next-quarter EPS forecasts) / |Mean| * 100
        measured 3 trading days AFTER the earnings call
    PreCallDispersion = SD(next-quarter EPS forecasts) / |Mean| * 100
        measured 1 trading day BEFORE the earnings call

Filters:
    - FPI='6' (next-quarter EPS forecasts only)
    - PDF='D' (diluted EPS only)
    - Stale estimate filter: 180 days
    - Minimum 2 analysts for valid dispersion
    - FPEDATS within 120 days of call date (date fence)

Winsorization: 1%/99% pooled (Diether et al. 2002 standard).

Performance: Fully vectorized via merge + groupby. No row-by-row iteration.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd
from pandas.tseries.offsets import CustomBusinessDay
from pandas.tseries.holiday import USFederalHolidayCalendar

from .base import VariableBuilder, VariableResult
from ._ibes_detail_engine import get_engine as get_ibes_detail_engine
from f1d.shared.path_utils import get_latest_output_dir


class PostCallDispersionBuilder(VariableBuilder):
    """Build PostCallDispersion and PreCallDispersion from IBES Detail data.

    PostCallDispersion: dispersion measured +3 trading days after earnings call.
    PreCallDispersion: dispersion measured -1 trading day before earnings call.

    Both use next-quarter (FPI=6) diluted (PDF=D) EPS forecasts.
    Formula: SD(analyst forecasts) / |Mean(analyst forecasts)| * 100
    """

    NUMEST_MIN = 2  # Minimum analysts for valid dispersion

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.days_before = 1  # 1 trading day before call (Druz et al. 2020)
        self.days_after = 3  # 3 trading days after call
        self.max_stale_days = config.get("max_stale_days", 180)
        self.fpedats_max_days = 120  # Date fence for FPEDATS matching

        # Initialize trading day calendar
        self.bday = CustomBusinessDay(calendar=USFederalHolidayCalendar())

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build PostCallDispersion and PreCallDispersion for all calls."""
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

        # Load IBES Detail data (FPI=6, PDF=D via engine defaults)
        engine = get_ibes_detail_engine()
        ibes = engine.get_data(root_path, years)

        # Compute dispersion for each call (vectorized)
        results = self._compute_dispersions(manifest, ibes)

        # Merge back to ensure all file_names present
        final = manifest[["file_name"]].merge(results, on="file_name", how="left")

        # Winsorize at 1%/99% pooled (Diether et al. 2002)
        for col in ["PreCallDispersion", "PostCallDispersion"]:
            valid = final[col].dropna()
            if len(valid) > 0:
                lo = valid.quantile(0.01)
                hi = valid.quantile(0.99)
                final[col] = final[col].clip(lo, hi)
                print(f"    PostCallDispersionBuilder: Winsorized {col} at [{lo:.2f}, {hi:.2f}]")

        stats = self.get_stats(final["PostCallDispersion"], "PostCallDispersion")

        return VariableResult(
            data=final,
            stats=stats,
            metadata={
                "columns": ["PreCallDispersion", "PostCallDispersion"],
                "source": "IBES Detail (individual analyst estimates)",
                "pre_call_window": f"-{self.days_before} trading day",
                "post_call_window": f"+{self.days_after} trading days",
                "fpi": "6 (next quarter)",
                "pdf": "D (diluted)",
                "stale_filter_days": self.max_stale_days,
                "fpedats_fence_days": self.fpedats_max_days,
                "winsorization": "1%/99% pooled",
            },
        )

    def _compute_dispersions(
        self,
        manifest: pd.DataFrame,
        ibes: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute PreCallDispersion and PostCallDispersion — fully vectorized.

        Strategy:
        1. Match each call to its target FPEDATS via merge_asof (forward, 120d fence)
        2. Join matched calls with IBES estimates on (gvkey, fpedats)
        3. Compute dispersion in bulk for pre-call and post-call windows
        """
        print(f"    PostCallDispersionBuilder: Computing dispersions for {len(manifest):,} calls (vectorized)...")

        calls = manifest[["file_name", "gvkey", "start_date"]].copy()
        calls["date_before"] = calls["start_date"] - self.days_before * self.bday
        calls["date_after"] = calls["start_date"] + self.days_after * self.bday

        # ── Step 1: Match calls to target FPEDATS ─────────────────────────
        # Build unique (gvkey, fpedats) from IBES, then merge_asof forward
        fpedats_index = (
            ibes[["gvkey", "fpedats"]]
            .drop_duplicates()
            .sort_values(["gvkey", "fpedats"])
            .rename(columns={"fpedats": "target_fpedats"})
        )

        calls_sorted = calls.sort_values(["gvkey", "start_date"]).reset_index(drop=True)

        # merge_asof requires left key sorted; with by="gvkey" pandas needs
        # start_date sorted within each gvkey group. We achieve this by
        # doing the merge per-gvkey in a grouped apply to avoid the global
        # sort requirement, OR by using a workaround: sort by start_date
        # globally and use the by= parameter.
        # Pandas merge_asof with by= requires the left_on column to be
        # monotonically sorted WITHIN each by-group. Since we sorted by
        # [gvkey, start_date], we need to verify pandas accepts this.
        # Safest approach: merge per group.
        matched_chunks = []
        for gvkey, chunk in calls_sorted.groupby("gvkey"):
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
            # Drop duplicate gvkey column from right if present
            if "gvkey_r" in m.columns:
                m = m.drop(columns=["gvkey_r"])
            matched_chunks.append(m)

        matched = pd.concat(matched_chunks, ignore_index=True)

        n_matched = matched["target_fpedats"].notna().sum()
        print(f"    PostCallDispersionBuilder: {n_matched:,} / {len(matched):,} calls matched to FPEDATS")

        # Drop unmatched calls (no IBES coverage)
        matched = matched.dropna(subset=["target_fpedats"])

        if len(matched) == 0:
            print("    PostCallDispersionBuilder: WARNING — no calls matched to IBES data")
            return pd.DataFrame(columns=["file_name", "PreCallDispersion", "PostCallDispersion"])

        # ── Step 2: Join with IBES estimates on (gvkey, target_fpedats) ───
        # Only keep columns needed for dispersion computation
        estimates = ibes[["gvkey", "fpedats", "actdats", "analys", "value"]].copy()

        pairs = matched[["file_name", "gvkey", "target_fpedats", "date_before", "date_after"]].merge(
            estimates,
            left_on=["gvkey", "target_fpedats"],
            right_on=["gvkey", "fpedats"],
            how="inner",
        )
        # Drop duplicate fpedats column from right side
        pairs = pairs.drop(columns=["fpedats"])

        print(f"    PostCallDispersionBuilder: {len(pairs):,} call-estimate pairs for dispersion computation")

        # ── Step 3: Compute dispersion for each window ────────────────────
        pre_disp = self._dispersion_bulk(pairs, "date_before")
        post_disp = self._dispersion_bulk(pairs, "date_after")

        # ── Step 4: Assemble results ──────────────────────────────────────
        result = matched[["file_name"]].copy()
        result = result.merge(
            pre_disp.rename(columns={"dispersion": "PreCallDispersion"}),
            on="file_name", how="left",
        )
        result = result.merge(
            post_disp.rename(columns={"dispersion": "PostCallDispersion"}),
            on="file_name", how="left",
        )

        for col in ["PreCallDispersion", "PostCallDispersion"]:
            coverage = result[col].notna().sum()
            pct = 100 * coverage / len(result)
            print(f"    PostCallDispersionBuilder: {col}: {coverage:,} / {len(result):,} ({pct:.1f}%)")

        return result

    def _dispersion_bulk(
        self,
        pairs: pd.DataFrame,
        date_col: str,
    ) -> pd.DataFrame:
        """Compute dispersion = SD / |Mean| × 100 for many calls at once.

        Args:
            pairs: DataFrame with file_name, [date_col], actdats, analys, value
            date_col: column name for the cutoff date (date_before or date_after)

        Returns:
            DataFrame with file_name, dispersion
        """
        # 1. Filter: estimate must be active on/before cutoff date
        active = pairs[pairs["actdats"] <= pairs[date_col]].copy()

        # 2. Stale filter: age <= max_stale_days
        active["_age_days"] = (active[date_col] - active["actdats"]).dt.days
        active = active[active["_age_days"] <= self.max_stale_days]

        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "dispersion"])

        # 3. Keep latest estimate per (file_name, analyst)
        active = (
            active.sort_values("actdats")
            .groupby(["file_name", "analys"], sort=False)
            .last()
            .reset_index()
        )

        # 4. Count analysts per call, require >= NUMEST_MIN
        analyst_counts = active.groupby("file_name")["analys"].transform("count")
        active = active[analyst_counts >= self.NUMEST_MIN]

        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "dispersion"])

        # 5. Compute SD and Mean per call
        agg = active.groupby("file_name")["value"].agg(["std", "mean"]).reset_index()
        agg.columns = ["file_name", "_sd", "_mean"]

        # 6. Dispersion = SD / |Mean| * 100 (NaN if mean == 0)
        valid_mean = agg["_mean"].abs() > 0
        agg["dispersion"] = np.where(
            valid_mean & agg["_sd"].notna(),
            agg["_sd"] / agg["_mean"].abs() * 100,
            np.nan,
        )

        return agg[["file_name", "dispersion"]]


__all__ = ["PostCallDispersionBuilder"]
