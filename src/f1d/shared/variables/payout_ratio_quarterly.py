"""Builder for PayoutRatio_q variable (quarterly payout ratio).

PayoutRatio_q = (dvpspq × cshoq) / ibq
  - dvpspq = dividends per share by pay date (true quarterly field)
  - cshoq = common shares outstanding (quarterly)
  - ibq = income before extraordinary items (quarterly, single-quarter)
  - NaN when ibq <= 0 (explicit negative earnings filter)
  - dvpspq NaN with ibq > 0 => PayoutRatio_q = 0 (no dividends paid)

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, PayoutRatio_q.

H12Q suite: Tests whether speech uncertainty predicts quarterly payout ratio.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class PayoutRatioQuarterlyBuilder(VariableBuilder):
    """Build PayoutRatio_q = (dvpspq × cshoq) / ibq from Compustat."""

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

        data = merged[["file_name", "PayoutRatio_q"]].copy()
        stats = self.get_stats(data["PayoutRatio_q"], "PayoutRatio_q")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "PayoutRatio_q",
                "source": "Compustat/(dvpspq*cshoq)/ibq (quarterly)",
                "negative_earnings_filter": "ibq <= 0 -> NaN",
            },
        )


__all__ = ["PayoutRatioQuarterlyBuilder"]
