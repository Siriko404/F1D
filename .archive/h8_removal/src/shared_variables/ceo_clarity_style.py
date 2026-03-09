"""Builder for CEO Clarity Style (StyleFrozen) variable — H8.

Reads CEO Clarity scores from Phase 56 output and assigns a time-invariant
(within CEO tenure) vagueness score to each firm-fiscal-year using the
frozen constraint: only calls observed up to and including fiscal year-end
are used to identify the "dominant CEO" for that year.

Returns per-call data with two columns:
    file_name    : earnings call identifier
    style_frozen : ClarityCEO score of the dominant CEO for that firm-year
                   (NaN if the firm-year cannot be matched)

Implementation notes:
    - "Dominant CEO" = CEO with the most calls in the firm-year window
      (frozen: calls ≤ fiscal year-end date), tiebreaker = earlier first_call_date.
    - style_frozen is the standardised ClarityCEO from Phase 56
      (mean ≈ 0, SD ≈ 1; negative = more vague).
    - Fiscal year-end dates come from CompustatEngine; matched via merge_asof
      (backward) on call start_date → datadate.
    - Requires `ceo_id` and `ceo_name` columns in the manifest.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine as get_compustat_engine
from f1d.shared.path_utils import get_latest_output_dir


class CEOClarityStyleBuilder(VariableBuilder):
    """Build style_frozen (frozen CEO vagueness score) for each call."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _load_ceo_clarity(self, root_path: Path) -> pd.DataFrame:
        """Load CEO Clarity scores from Phase 56 output."""
        try:
            ceo_dir = get_latest_output_dir(
                root_path / "outputs" / "econometric" / "ceo_clarity",
                required_file="clarity_scores.parquet",
            )
        except Exception as e:
            raise FileNotFoundError(
                f"CEOClarityStyleBuilder: cannot locate clarity_scores.parquet "
                f"under outputs/econometric/ceo_clarity — {e}"
            )

        df = pd.read_parquet(ceo_dir / "clarity_scores.parquet")
        required = {"ceo_id", "ClarityCEO", "n_calls"}
        missing = required - set(df.columns)
        if missing:
            raise ValueError(
                f"CEOClarityStyleBuilder: missing columns in clarity_scores: {missing}"
            )
        return df

    def _build_firm_year_ceo_map(
        self,
        manifest: pd.DataFrame,
        ceo_clarity: pd.DataFrame,
        comp_df: pd.DataFrame,
        min_calls_total: int = 5,
    ) -> pd.DataFrame:
        """Return (gvkey, fyearq) → (ceo_id, style_frozen) lookup.

        Uses frozen constraint: only calls ≤ fiscal year-end are considered
        when selecting the dominant CEO.
        """
        # --- Filter to CEOs with sufficient total calls ---
        valid_ceos = ceo_clarity[ceo_clarity["n_calls"] >= min_calls_total]["ceo_id"]
        mf = manifest[manifest["ceo_id"].isin(valid_ceos)][
            ["file_name", "gvkey", "start_date", "ceo_id"]
        ].copy()

        if len(mf) == 0:
            return pd.DataFrame(columns=["gvkey", "fyearq", "style_frozen", "ceo_id"])

        # --- Build fiscal year-end grid from Compustat ---
        fy = (
            comp_df[["gvkey", "fyearq", "datadate"]]
            .dropna(subset=["fyearq", "datadate"])
            .copy()
        )
        fy["fyearq"] = fy["fyearq"].astype(int)
        fy["datadate"] = pd.to_datetime(fy["datadate"], errors="coerce")
        fy = (
            fy.dropna(subset=["datadate"])
            .sort_values("datadate")
            .drop_duplicates(subset=["gvkey", "fyearq"], keep="last")
        )

        # Keep only Q4 (annual) rows — use fqtr if available
        if "fqtr" in comp_df.columns:
            fy_q4 = fy[fy["gvkey"].isin(comp_df[comp_df["fqtr"] == 4]["gvkey"])].copy()
            # Re-filter comp_df properly
            q4_keys = comp_df[comp_df["fqtr"] == 4][
                ["gvkey", "fyearq"]
            ].drop_duplicates()
            fy = fy.merge(q4_keys, on=["gvkey", "fyearq"], how="inner")

        # --- Cross-join: for each (gvkey, fyearq), which calls are ≤ fy_end? ---
        # Efficient: merge on gvkey, then filter by date
        fy_expanded = fy.merge(mf, on="gvkey", how="inner")
        fy_expanded = fy_expanded[fy_expanded["start_date"] <= fy_expanded["datadate"]]

        if len(fy_expanded) == 0:
            return pd.DataFrame(columns=["gvkey", "fyearq", "style_frozen", "ceo_id"])

        # Count calls per (gvkey, fyearq, ceo_id)
        counts = (
            fy_expanded.groupby(["gvkey", "fyearq", "ceo_id"])
            .size()
            .reset_index(name="n_calls_fy")
        )

        # Compute first_call_date from the manifest for each CEO as a tiebreaker
        first_dates = (
            manifest.groupby("ceo_id")["start_date"]
            .min()
            .reset_index(name="first_call_date")
        )

        # Merge in first_call_date for tiebreaker
        counts = counts.merge(first_dates, on="ceo_id", how="left")

        # Select dominant CEO: most calls in FY; tiebreak = earliest first_call_date
        counts = counts.sort_values(
            ["n_calls_fy", "first_call_date"], ascending=[False, True]
        )
        dominant = counts.groupby(["gvkey", "fyearq"]).first().reset_index()

        # Attach ClarityCEO as style_frozen
        dominant = dominant.merge(
            ceo_clarity[["ceo_id", "ClarityCEO"]], on="ceo_id", how="left"
        )
        dominant = dominant.rename(columns={"ClarityCEO": "style_frozen"})

        return dominant[["gvkey", "fyearq", "style_frozen", "ceo_id"]].copy()

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        manifest = pd.read_parquet(manifest_path)
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        if "ceo_id" not in manifest.columns:
            # Return all-NaN if CEO column absent
            data = manifest[["file_name"]].copy()
            data["style_frozen"] = float("nan")
            return VariableResult(
                data=data,
                stats=self.get_stats(data["style_frozen"], "style_frozen"),
                metadata={
                    "column": "style_frozen",
                    "note": "ceo_id absent in manifest",
                },
            )

        # 2. Load CEO Clarity scores
        ceo_clarity = self._load_ceo_clarity(root_path)

        # 3. Load Compustat for fiscal year-end dates
        comp_engine = get_compustat_engine()
        comp_df = comp_engine.get_data(root_path)

        # 4. Build (gvkey, fyearq) → style_frozen lookup
        fy_map = self._build_firm_year_ceo_map(manifest, ceo_clarity, comp_df)

        # 5. Attach fyearq to manifest via merge_asof(backward) on start_date → datadate
        fyearq_df = (
            comp_df[["gvkey", "fyearq", "datadate"]]
            .dropna(subset=["fyearq", "datadate"])
            .sort_values("datadate")
        )
        fyearq_df["datadate"] = pd.to_datetime(fyearq_df["datadate"], errors="coerce")

        manifest_sorted = manifest.sort_values("start_date").copy()
        merged_fy = pd.merge_asof(
            manifest_sorted,
            fyearq_df,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )
        # fyearq might have been set from comp_df
        if "fyearq" not in merged_fy.columns:
            merged_fy["fyearq"] = float("nan")
        merged_fy["fyearq"] = (
            pd.to_numeric(merged_fy["fyearq"], errors="coerce").dropna().astype(int)
        )

        # 6. Map style_frozen back to each call
        merged_fy = merged_fy.merge(
            fy_map[["gvkey", "fyearq", "style_frozen"]],
            on=["gvkey", "fyearq"],
            how="left",
        )

        data = manifest[["file_name"]].merge(
            merged_fy[["file_name", "style_frozen"]], on="file_name", how="left"
        )
        data = data.drop_duplicates(subset=["file_name"])

        return VariableResult(
            data=data[["file_name", "style_frozen"]].copy(),
            stats=self.get_stats(data["style_frozen"], "style_frozen"),
            metadata={
                "column": "style_frozen",
                "source": "Phase 56 ClarityCEO + frozen constraint",
                "description": (
                    "CEO clarity score (standardised) for the dominant CEO of "
                    "each firm-fiscal-year, assigned using only calls ≤ fy_end."
                ),
            },
        )


__all__ = ["CEOClarityStyleBuilder"]
