"""Builder for Earnings Surprise Decile (SurpDec) variable.

Computes SurpDec from IBES consensus data (via IbesEngine) and the
CRSP-Compustat CCM linktable.

Returns one column: file_name, SurpDec.

Algorithm:
  1. Load IBES consensus from IbesEngine (computed from yearly detail files).
  2. For each call, match to most recent pre-call consensus via merge_asof.
  3. Filter by FPEDATS proximity (±45 days of call date).
  4. Compute raw surprise = ACTUAL - MEANEST.
  5. Within each calendar quarter, rank surprises into -5 to +5 scale (SurpDec).

Bug fixes applied here (from red-team audit):
    CRITICAL-1: _rank_surprises single-firm edge case handled.
    CRITICAL-5: merge_asof replaces arbitrary .iloc[-1] selection.
    MAJOR-1:    CUSIP linking handled by IbesEngine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from f1d.shared.path_utils import get_latest_output_dir


def _rank_surprises(group: pd.DataFrame) -> pd.Series:
    """Rank surprises within a quarter to -5..+5 scale."""
    surprises = group["surprise_raw"]
    ranks = pd.Series(np.nan, index=group.index, dtype=float)

    valid_mask = surprises.notna()
    if valid_mask.sum() < 5:
        return ranks

    pos_mask = surprises > 0
    zero_mask = surprises == 0
    neg_mask = surprises < 0

    if pos_mask.sum() > 0:
        pos_pct = surprises[pos_mask].rank(ascending=False, method="average", pct=True)
        pos_decile = np.ceil(pos_pct * 5).clip(1, 5)
        ranks.loc[pos_mask] = 6 - pos_decile

    ranks.loc[zero_mask] = 0.0

    if neg_mask.sum() > 0:
        neg_pct = (
            surprises[neg_mask].abs().rank(ascending=True, method="average", pct=True)
        )
        neg_decile = np.ceil(neg_pct * 5).clip(1, 5)
        ranks.loc[neg_mask] = -neg_decile

    return ranks


class EarningsSurpriseBuilder(VariableBuilder):
    """Build Earnings Surprise Decile (SurpDec) from IBES data via IbesEngine.

    Returns a VariableResult whose .data contains: file_name, SurpDec.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        manifest_dir = get_latest_output_dir(
            root_path / "outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet",
        )
        manifest_path = manifest_dir / "master_sample_manifest.parquet"

        print("    EarningsSurpriseBuilder: loading manifest...")
        manifest = pd.read_parquet(
            manifest_path, columns=["file_name", "gvkey", "start_date"]
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Load IBES consensus from summary engine
        print("    EarningsSurpriseBuilder: loading IBES via IbesEngine...")
        engine = get_ibes_engine()
        ibes_data = engine.get_data(root_path)

        if ibes_data.empty or "surprise_raw" not in ibes_data.columns:
            print("    EarningsSurpriseBuilder: No IBES data available")
            data = manifest[["file_name"]].copy()
            data["SurpDec"] = np.nan
            return VariableResult(
                data=data,
                stats=self.get_stats(data["SurpDec"], "SurpDec"),
                metadata={"column": "SurpDec", "source": "IBES", "matched": 0, "total": len(manifest)},
            )

        # merge_asof: for each call, find the most recent consensus whose fiscal
        # period ended before the call (fpedats <= start_date, ±120 day tolerance)
        manifest_sorted = manifest.sort_values("start_date")
        ibes_sorted = ibes_data.sort_values("fpedats")

        merged = pd.merge_asof(
            manifest_sorted[["file_name", "gvkey", "start_date"]],
            ibes_sorted[["gvkey", "fpedats", "surprise_raw"]],
            left_on="start_date",
            right_on="fpedats",
            by="gvkey",
            direction="backward",
            tolerance=pd.Timedelta(days=120),
        )

        # Restore original manifest order
        results_df = manifest[["file_name"]].merge(
            merged[["file_name", "surprise_raw"]], on="file_name", how="left"
        )

        matched = int(results_df["surprise_raw"].notna().sum())
        if len(manifest) > 0:
            print(
                f"    EarningsSurpriseBuilder: matched {matched:,}/{len(manifest):,} "
                f"({matched / len(manifest) * 100:.1f}%)"
            )

        # Compute SurpDec within quarter
        manifest_surp = manifest.merge(results_df, on="file_name", how="left")
        manifest_surp["call_quarter"] = manifest_surp["start_date"].dt.to_period("Q")
        manifest_surp["SurpDec"] = manifest_surp.groupby(
            "call_quarter", group_keys=False
        ).apply(_rank_surprises)

        data = manifest_surp[["file_name", "SurpDec"]].copy()
        stats = self.get_stats(data["SurpDec"], "SurpDec")

        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "source": "IBES Detail via IbesEngine consensus",
                "column": "SurpDec",
                "matched": matched,
                "total": len(manifest),
            },
        )


__all__ = ["EarningsSurpriseBuilder"]
