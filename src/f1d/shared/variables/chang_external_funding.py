"""Builder for ChangExternalFunding and ChangDebtChoice variables (Chang, Dasgupta & Hilary 2006).

ChangExternalFunding = 1 if firm uses external financing (cash-flow debt or equity
  issuance >5% of lagged total assets), 0 if internal financing.
ChangDebtChoice = 1 if debt-only, 0 if equity-only (NaN if dual issuer or internal).

Classification per Chang, Dasgupta & Hilary (2006, JF):
  - Debt issuance: (dltisy - dltry + dlcchy) / lagged_atq > 5% (cash flow statement)
  - Equity issuance: (sstky - prstkcy) / lagged_atq > 5% (cash flow statement)
  - Internal: neither threshold met
  - Dual: EXCLUDED (ChangDebtChoice = NaN), unlike L&R which classifies as equity

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns columns: file_name, ChangExternalFunding, ChangDebtChoice, fqtr.

H19b suite: Robustness test for external vs internal funding (Chang et al. 2006).
H20b suite: Robustness test for debt vs equity choice (Chang et al. 2006).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class ChangExternalFundingBuilder(VariableBuilder):
    """Build ChangExternalFunding and ChangDebtChoice from Compustat (Chang et al. 2006)."""

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

        data = merged[["file_name", "ChangExternalFunding", "ChangDebtChoice", "fqtr"]].copy()
        stats = self.get_stats(data["ChangExternalFunding"], "ChangExternalFunding")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "ChangExternalFunding,ChangDebtChoice",
                "source": "Compustat/Chang_Dasgupta_Hilary_2006_classification",
            },
        )


__all__ = ["ChangExternalFundingBuilder"]
