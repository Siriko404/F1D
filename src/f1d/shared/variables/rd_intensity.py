"""Builder for R&D Sales variable.

RDSales = xrdy_Q4-annual / saley_Q4-annual (Bates 2009 / Jiang-John-Larsen
2021 R&D-over-sales convention; missing xrd treated as zero; non-positive
sales treated as NaN).  Implementation in src/f1d/shared/variables/
_compustat_engine.py L984-993.

The earlier xrdq/atq form was deprecated 2026-04-02 in favor of xrdy/saley.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, RDSales.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class RDIntensityBuilder(VariableBuilder):
    """Build RDSales = xrdy_Q4-annual / saley_Q4-annual via CompustatEngine.

    Missing R&D (xrdy = NaN) is treated as zero per standard convention.
    Non-positive sales -> NaN.
    """

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

        data = merged[["file_name", "RDSales"]].copy()
        stats = self.get_stats(data["RDSales"], "RDSales")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "RDSales", "source": "Compustat/xrdy,saley (Q4-annual)"},
        )


__all__ = ["RDIntensityBuilder"]
