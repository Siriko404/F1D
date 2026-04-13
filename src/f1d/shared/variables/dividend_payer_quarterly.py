"""Builder for DivPayerQ variable (1 if firm paid a dividend in the fiscal quarter, else 0).

Uses Compustat dvpsxq (dividend per share by EX date, quarterly) > 0.
This is the HP (2009) Compustat item 26 (dvpsx = ex-date) analog at quarterly
frequency — the same Compustat field family, extended from firm-year to
firm-quarter to match the F1D call-level speech-uncertainty treatment.

Reference:
    Hoberg, G. and N. R. Prabhala (2009). "Disappearing Dividends, Catering,
    and Risk." Review of Financial Studies 22(1), 79-116. DOI: 10.1093/rfs/hhn073.
    Their DV: `Compustat item 26 (dvpsx) > 0` at fiscal-year frequency.
    H26/H12b extends to firm-quarter via dvpsxq > 0.

Secondary reference:
    Chetty, R. and E. Saez (2005). "Dividend Taxes and Corporate Behavior."
    Quarterly Journal of Economics 120(3), 791-833. Firm-quarter frequency precedent.

Distinct from DivDummy (annual, dvy_Q4 > 0) which is a pay-date fiscal-year
proxy used as a CONTROL in other suites. DivPayerQ is the H12b regression DV.

Reads raw Compustat quarterly data via the shared CompustatEngine.
Returns one column: file_name, DivPayerQ.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class DividendPayerQuarterlyBuilder(VariableBuilder):
    """Build DivPayerQ = (dvpsxq > 0).astype(float) from raw Compustat quarterly data.

    Reference: Hoberg & Prabhala (2009, RFS) — Compustat item 26 (dvpsx ex-date) analog.
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

        data = merged[["file_name", "DivPayerQ"]].copy()
        stats = self.get_stats(data["DivPayerQ"], "DivPayerQ")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "DivPayerQ",
                "source": "Compustat/dvpsxq>0 (quarterly ex-date)",
                "reference": "Hoberg & Prabhala (2009, RFS) — Compustat item 26 (dvpsx) analog",
            },
        )


__all__ = ["DividendPayerQuarterlyBuilder"]
