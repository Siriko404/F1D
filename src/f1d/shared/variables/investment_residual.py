"""Builder for InvestmentResidual variable (Biddle 2009 abnormal investment).

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, InvestmentResidual.

The residual is computed via the Biddle et al. (2009, JAE) specification:
    Investment = (CapEx + R&D + Acquisitions - AssetSales) / lagged(AT)
    First-stage OLS within each FF48-year cell (min 20 obs per cell):
        Investment ~ TobinQ_lag + SalesGrowth_lag
    InvestmentResidual = actual - predicted
    > 0 = overinvestment; < 0 = underinvestment

New Compustat columns required: xrdy, aqcy, sppey, saleq, sic.
FF48 codes derived from SIC via inputs/FF1248/Siccodes48.zip.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class InvestmentResidualBuilder(VariableBuilder):
    """Build InvestmentResidual from raw Compustat via Biddle (2009) first-stage OLS."""

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

        data = merged[["file_name", "InvestmentResidual"]].copy()
        stats = self.get_stats(data["InvestmentResidual"], "InvestmentResidual")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "InvestmentResidual",
                "source": "Biddle (2009): (capxy+xrdy+aqcy-sppey)/at_lag; "
                "residual from FF48-year OLS: Investment ~ TobinQ_lag + SalesGrowth_lag",
            },
        )


__all__ = ["InvestmentResidualBuilder"]
