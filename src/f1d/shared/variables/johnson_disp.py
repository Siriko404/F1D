"""Builder for JohnsonDISP2 — Johnson (2004) analyst forecast dispersion.

Computes month-end analyst forecast dispersion following Johnson (2004,
Journal of Financial Economics 74(1): 3-40), DISP2 variant.

Output columns: file_name, JohnsonDISP2

Construction:
    JohnsonDISP2 = SD(current-fiscal-year EPS forecasts outstanding at month-end) / atq
    where:
        - Month-end = last calendar day of the call's month
        - Forecasts: each analyst's most recent current-fiscal-year EPS forecast
          outstanding at month-end, issued within past 180 days
        - Fiscal period filter: fpedats >= month_end (drop ended fiscal years)
        - atq = most recently reported book value of total assets (Compustat)

Filters:
    - FPI='1' (current-fiscal-year EPS forecasts)
    - PDF='D' (diluted EPS only)
    - Stale: age <= 180 days from month-end
    - Minimum 2 analysts for valid dispersion
    - Fiscal period not yet ended: fpedats >= month_end

Winsorization: 1%/99% pooled (Johnson 2004 implementation).

Memory-safe: uses per-gvkey merge_asof loops (same pattern as postcall_dispersion).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_detail_engine import IbesDetailEngine
from ._compustat_engine import get_engine as get_compustat_engine
from f1d.shared.path_utils import get_latest_output_dir


class JohnsonDispBuilder(VariableBuilder):
    """Build JohnsonDISP2 from IBES Detail (annual forecasts) + Compustat atq.

    DISP2: SD of current-fiscal-year analyst forecasts outstanding at month-end,
    scaled by book assets. Johnson (2004) definition.
    """

    NUMEST_MIN = 2

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.max_stale_days = 180  # 6-month stale window (Johnson spec)

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build JohnsonDISP2 for all calls."""
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

        # Load IBES Detail with FPI=['1'] (annual forecasts)
        # Fresh instance to avoid singleton cache collision with PostCallDispersion
        ibes_engine = IbesDetailEngine()
        ibes_engine.fpi_valid = ['1']
        ibes = ibes_engine.get_data(root_path, years)

        # Load Compustat for fyearq (fiscal year), fqtr (Q4 detection), atq
        comp_engine = get_compustat_engine()
        comp = comp_engine.get_data(root_path)

        # Build lookups
        fy_end_lookup = self._build_fiscal_year_end_lookup(comp)
        atq_lookup = self._build_atq_lookup(comp)
        fyearq_lookup = self._build_fyearq_lookup(comp)

        # Compute Johnson DISP2
        results = self._compute_johnson_disp(
            manifest, ibes, fy_end_lookup, atq_lookup, fyearq_lookup
        )

        # Merge back to full manifest
        final = manifest[["file_name"]].merge(results, on="file_name", how="left")

        # Winsorize at 1%/99% pooled (Johnson 2004)
        valid = final["JohnsonDISP2"].dropna()
        if len(valid) > 0:
            lo = valid.quantile(0.01)
            hi = valid.quantile(0.99)
            final["JohnsonDISP2"] = final["JohnsonDISP2"].clip(lo, hi)
            print(f"    JohnsonDispBuilder: Winsorized at [{lo:.2e}, {hi:.2e}]")

        coverage = final["JohnsonDISP2"].notna().sum()
        print(f"    JohnsonDispBuilder: Final coverage: {coverage:,} / {len(final):,} "
              f"({100 * coverage / len(final):.1f}%)")

        stats = self.get_stats(final["JohnsonDISP2"], "JohnsonDISP2")

        return VariableResult(
            data=final,
            stats=stats,
            metadata={
                "columns": ["JohnsonDISP2"],
                "source": "IBES Detail (FPI=1, annual) + Compustat atq",
                "window": "Month-end snapshot, 180-day stale filter",
                "denominator": "atq (book value of total assets, Compustat units)",
                "reference": "Johnson (2004, JFE 74(1): 3-40), DISP2 variant",
                "winsorization": "1%/99% pooled",
            },
        )

    # ------------------------------------------------------------------
    # Lookup builders (small DataFrames, no memory concern)
    # ------------------------------------------------------------------

    def _build_fiscal_year_end_lookup(self, comp: pd.DataFrame) -> pd.DataFrame:
        """(gvkey, fyearq) -> fiscal year-end datadate. Q4 datadate = FY end."""
        df = comp[["gvkey", "datadate", "fqtr", "fyearq"]].copy()
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["fyearq"] = pd.to_numeric(df["fyearq"], errors="coerce")
        df["fqtr"] = pd.to_numeric(df["fqtr"], errors="coerce")

        q4 = df[df["fqtr"] == 4][["gvkey", "fyearq", "datadate"]].drop_duplicates()
        q4 = q4.rename(columns={"datadate": "fiscal_year_end"})
        q4 = q4.dropna(subset=["fyearq", "fiscal_year_end"])
        print(f"    JohnsonDispBuilder: Fiscal year-end lookup: {len(q4):,} firm-years")
        return q4

    def _build_atq_lookup(self, comp: pd.DataFrame) -> pd.DataFrame:
        """(gvkey, datadate) -> atq, sorted for merge_asof."""
        df = comp[["gvkey", "datadate", "atq"]].copy()
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
        df["datadate"] = pd.to_datetime(df["datadate"])
        df = df.dropna(subset=["atq"])
        df = df[df["atq"] > 0]
        df = df.sort_values(["gvkey", "datadate"])
        print(f"    JohnsonDispBuilder: atq lookup: {len(df):,} firm-quarters")
        return df

    def _build_fyearq_lookup(self, comp: pd.DataFrame) -> pd.DataFrame:
        """(gvkey, datadate) -> fyearq, sorted for merge_asof."""
        df = comp[["gvkey", "datadate", "fyearq"]].copy()
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)
        df["datadate"] = pd.to_datetime(df["datadate"])
        df["fyearq"] = pd.to_numeric(df["fyearq"], errors="coerce")
        df = df.dropna(subset=["fyearq"])
        df = df.sort_values(["gvkey", "datadate"])
        return df

    # ------------------------------------------------------------------
    # Main computation (memory-safe per-gvkey loops)
    # ------------------------------------------------------------------

    def _compute_johnson_disp(
        self,
        manifest: pd.DataFrame,
        ibes: pd.DataFrame,
        fy_end_lookup: pd.DataFrame,
        atq_lookup: pd.DataFrame,
        fyearq_lookup: pd.DataFrame,
    ) -> pd.DataFrame:
        """Compute Johnson (2004) DISP2 — memory-safe per-gvkey processing."""
        print(f"    JohnsonDispBuilder: Computing DISP2 for {len(manifest):,} calls...")

        calls = manifest[["file_name", "gvkey", "start_date"]].copy()
        calls["month_end"] = calls["start_date"] + pd.offsets.MonthEnd(0)

        # ── Step 1: Attach fyearq per gvkey (memory-safe loop) ──
        calls_sorted = calls.sort_values(["gvkey", "start_date"])
        fy_chunks = []
        gvkeys = calls_sorted["gvkey"].unique()
        print(f"    JohnsonDispBuilder: Attaching fyearq for {len(gvkeys):,} firms...")

        for gvkey in gvkeys:
            chunk = calls_sorted[calls_sorted["gvkey"] == gvkey].copy()
            fy = fyearq_lookup[fyearq_lookup["gvkey"] == gvkey]
            if len(fy) == 0:
                chunk["fyearq"] = np.nan
                fy_chunks.append(chunk)
                continue
            m = pd.merge_asof(
                chunk.sort_values("start_date"),
                fy.sort_values("datadate"),
                left_on="start_date", right_on="datadate",
                direction="backward",
            )
            m = m.drop(columns=[c for c in ["datadate", "gvkey_y"] if c in m.columns], errors="ignore")
            if "gvkey_x" in m.columns:
                m = m.rename(columns={"gvkey_x": "gvkey"})
            fy_chunks.append(m)

        calls = pd.concat(fy_chunks, ignore_index=True)
        n_fy = calls["fyearq"].notna().sum()
        print(f"    JohnsonDispBuilder: {n_fy:,} / {len(calls):,} calls matched to fyearq")
        del fy_chunks  # Free memory

        # ── Step 2: Derive target FPEDATS from fiscal year-end ──
        calls = calls.merge(fy_end_lookup, on=["gvkey", "fyearq"], how="left")
        calls["target_fpedats"] = calls["fiscal_year_end"]

        n_matched = calls["target_fpedats"].notna().sum()
        print(f"    JohnsonDispBuilder: {n_matched:,} calls matched to fiscal year-end FPEDATS")

        calls_valid = calls.dropna(subset=["target_fpedats"]).copy()
        if len(calls_valid) == 0:
            return pd.DataFrame(columns=["file_name", "JohnsonDISP2"])

        # ── Step 3: Join with IBES estimates on (gvkey, target_fpedats) ──
        estimates = ibes[["gvkey", "fpedats", "actdats", "analys", "value"]].copy()

        pairs = calls_valid[["file_name", "gvkey", "target_fpedats", "month_end"]].merge(
            estimates,
            left_on=["gvkey", "target_fpedats"],
            right_on=["gvkey", "fpedats"],
            how="inner",
        )
        pairs = pairs.drop(columns=["fpedats"])
        print(f"    JohnsonDispBuilder: {len(pairs):,} call-estimate pairs")

        # ── Step 4: Johnson filters + SD computation ──
        sd_per_call = self._johnson_dispersion_bulk(pairs)
        del pairs  # Free memory

        # ── Step 5: Attach atq per gvkey (memory-safe loop) ──
        calls_for_atq = calls_valid[["file_name", "gvkey", "start_date"]].sort_values(["gvkey", "start_date"])
        atq_chunks = []
        for gvkey in calls_for_atq["gvkey"].unique():
            chunk = calls_for_atq[calls_for_atq["gvkey"] == gvkey].copy()
            a = atq_lookup[atq_lookup["gvkey"] == gvkey]
            if len(a) == 0:
                chunk["atq"] = np.nan
                atq_chunks.append(chunk)
                continue
            m = pd.merge_asof(
                chunk.sort_values("start_date"),
                a.sort_values("datadate"),
                left_on="start_date", right_on="datadate",
                direction="backward",
            )
            m = m.drop(columns=[c for c in ["datadate", "gvkey_y"] if c in m.columns], errors="ignore")
            if "gvkey_x" in m.columns:
                m = m.rename(columns={"gvkey_x": "gvkey"})
            atq_chunks.append(m)

        atq_matched = pd.concat(atq_chunks, ignore_index=True)[["file_name", "atq"]]
        del atq_chunks  # Free memory

        # ── Step 6: DISP2 = SD / atq ──
        result = sd_per_call.merge(atq_matched, on="file_name", how="left")

        valid_atq = result["atq"].notna() & (result["atq"] > 0)
        result["JohnsonDISP2"] = np.where(
            valid_atq & result["_sd"].notna(),
            result["_sd"] / result["atq"],
            np.nan,
        )

        n_valid = result["JohnsonDISP2"].notna().sum()
        print(f"    JohnsonDispBuilder: {n_valid:,} calls with valid JohnsonDISP2")

        return result[["file_name", "JohnsonDISP2"]]

    def _johnson_dispersion_bulk(self, pairs: pd.DataFrame) -> pd.DataFrame:
        """Compute SD using Johnson (2004) filters — vectorized on pairs DataFrame.

        Filters:
        1. actdats <= month_end (estimate outstanding at month-end)
        2. (month_end - actdats).days <= 180 (6-month stale)
        3. target_fpedats >= month_end (fiscal period not yet ended)
        4. Keep latest per (file_name, analyst)
        5. Require >= 2 analysts
        """
        # 1. Outstanding at month-end
        active = pairs[pairs["actdats"] <= pairs["month_end"]].copy()
        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 2. Stale filter
        active["_age_days"] = (active["month_end"] - active["actdats"]).dt.days
        active = active[active["_age_days"] <= self.max_stale_days]
        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 3. Fiscal period not yet ended
        active = active[active["target_fpedats"] >= active["month_end"]]
        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 4. Latest per (file_name, analyst)
        active = (
            active.sort_values("actdats")
            .groupby(["file_name", "analys"], sort=False)
            .last()
            .reset_index()
        )

        # 5. Min analysts
        analyst_counts = active.groupby("file_name")["analys"].transform("count")
        active = active[analyst_counts >= self.NUMEST_MIN]
        if len(active) == 0:
            return pd.DataFrame(columns=["file_name", "_sd"])

        # 6. SD per call
        agg = active.groupby("file_name")["value"].agg("std").reset_index()
        agg.columns = ["file_name", "_sd"]
        return agg


__all__ = ["JohnsonDispBuilder"]
