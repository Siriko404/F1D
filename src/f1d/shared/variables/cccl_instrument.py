"""Builder for CCCL shift-intensity instrument (shift_intensity_sale_ff48).

Reads the pre-computed CCCL instrument from inputs/CCCL_instrument/ and
returns one column: file_name, shift_intensity_sale_ff48.

The instrument is at firm-year (gvkey × year) granularity. It is merged onto
the manifest via gvkey + year and then mapped to file_name.

Architecture note: The CCCL file starts in 2005. Calls before 2005 will have
NaN instrument values (expected; those calls drop out of the IV regression
sample but are still included in OLS regressions).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from f1d.shared.path_utils import get_latest_output_dir


class CCCLInstrumentBuilder(VariableBuilder):
    """Build shift_intensity_sale_ff48 from CCCL instrument parquet.

    Merges on gvkey + year (call year). The instrument is constructed at the
    firm-year level (each firm has its own sales-weighted shift intensity based
    on its FF48 industry). NaN values for calls before 2005 are expected.
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
            manifest_path,
            columns=["file_name", "gvkey", "start_date"],
        )
        manifest["gvkey"] = manifest["gvkey"].astype(str).str.zfill(6)
        manifest["start_date"] = pd.to_datetime(manifest["start_date"])
        manifest["year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["year"].isin(list(years))].copy()

        # Load CCCL instrument (firm-year level)
        cccl_path = (
            root_path
            / "inputs"
            / "CCCL_instrument"
            / "instrument_shift_intensity_2005_2022.parquet"
        )
        if not cccl_path.exists():
            raise FileNotFoundError(
                f"CCCL instrument not found at: {cccl_path}\n"
                "Expected: inputs/CCCL_instrument/instrument_shift_intensity_2005_2022.parquet"
            )

        cccl = pd.read_parquet(
            cccl_path,
            columns=["gvkey", "year", "shift_intensity_sale_ff48"],
        )
        cccl["gvkey"] = cccl["gvkey"].astype(str).str.zfill(6)
        cccl["year"] = cccl["year"].astype(int)

        # Assert uniqueness on gvkey+year before merge to prevent fan-out
        if cccl.duplicated(subset=["gvkey", "year"]).any():
            n_dups = cccl.duplicated(subset=["gvkey", "year"]).sum()
            raise ValueError(
                f"CCCL instrument has {n_dups} duplicate gvkey+year rows. "
                "This would cause row fan-out on merge."
            )

        # Merge instrument onto manifest via gvkey + year
        merged = manifest.merge(
            cccl,
            on=["gvkey", "year"],
            how="left",
        )

        # Hard-fail if merge caused row duplication
        if len(merged) != len(manifest):
            raise ValueError(
                f"CCCL merge changed row count {len(manifest)} → {len(merged)}. "
                "Duplicate gvkey+year in CCCL data caused fan-out."
            )

        # Validate target column present
        if "shift_intensity_sale_ff48" not in merged.columns:
            raise ValueError(
                "'shift_intensity_sale_ff48' not found after CCCL merge. "
                "Check CCCL parquet column names."
            )

        data = merged[["file_name", "shift_intensity_sale_ff48"]].copy()
        n_matched = data["shift_intensity_sale_ff48"].notna().sum()
        print(
            f"    CCCL: {n_matched:,}/{len(data):,} calls matched "
            f"({100.0 * n_matched / len(data):.1f}%)"
        )

        stats = self.get_stats(
            data["shift_intensity_sale_ff48"], "shift_intensity_sale_ff48"
        )
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": "shift_intensity_sale_ff48",
                "source": "inputs/CCCL_instrument/",
                "merge_key": "gvkey + year",
                "note": "NaN for calls before 2005 — expected",
            },
        )


__all__ = ["CCCLInstrumentBuilder"]
