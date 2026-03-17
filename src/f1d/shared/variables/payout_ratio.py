"""Builder for PayoutRatio variable (Attig et al.).

PayoutRatio = DVC / IB = dvy_Q4 / iby_Q4
  - dvy = annual common dividends (Q4 cumulative)
  - iby = income before extraordinary items (annual, Q4 cumulative)
  - NaN when iby <= 0 (negative earnings)
  - dvy NaN with iby > 0 => PayoutRatio = 0 (no dividends paid)

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, PayoutRatio.

H12 redesign: Tests whether speech uncertainty predicts payout ratio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class PayoutRatioBuilder(VariableBuilder):
    """Build PayoutRatio = dvy / iby (Attig et al.) from Compustat."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
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

        engine = get_engine()
        merged = engine.match_to_manifest(manifest, root_path)

        data = merged[["file_name", "PayoutRatio"]].copy()
        stats = self.get_stats(data["PayoutRatio"], "PayoutRatio")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "PayoutRatio",
                "source": "Compustat/dvy_Q4/iby_Q4 (Attig et al.)",
            },
        )


__all__ = ["PayoutRatioBuilder"]
