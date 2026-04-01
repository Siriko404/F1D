"""Builder for ExternalFunding and DebtChoice variables (Leary & Roberts 2010).

ExternalFunding = 1 if firm uses external financing (debt or equity issuance >5%
  of lagged total assets), 0 if internal financing (neither threshold met).
DebtChoice = 1 if debt-only issuance, 0 if equity or dual issuance (NaN if internal).

Classification per Leary & Roberts (2010, JFE, Table 3 p.341):
  - Debt issuance: Δ(dlcq + dlttq) / lagged_atq > 5% (balance sheet change)
  - Equity issuance: (sstky - prstkcy) / lagged_atq > 5% (cash flow statement)
  - Internal: neither threshold met
  - Dual: both met → classified as equity per L&R convention

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns columns: file_name, ExternalFunding, DebtChoice, fqtr.

H19 suite: Tests whether speech uncertainty predicts external vs internal funding.
H20 suite: Tests whether speech uncertainty predicts debt vs equity choice.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class ExternalFundingBuilder(VariableBuilder):
    """Build ExternalFunding and DebtChoice from Compustat (Leary & Roberts 2010)."""

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

        data = merged[["file_name", "ExternalFunding", "DebtChoice", "fqtr"]].copy()
        stats = self.get_stats(data["ExternalFunding"], "ExternalFunding")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "ExternalFunding,DebtChoice",
                "source": "Compustat/Leary_Roberts_2010_classification",
            },
        )


__all__ = ["ExternalFundingBuilder"]
