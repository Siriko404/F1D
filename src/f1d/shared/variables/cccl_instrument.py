"""Builder for CCCL shift-intensity instrument (shift_intensity_sale_ff48).

Reads the pre-computed CCCL instrument from inputs/CCCL_instrument/ and
returns one column: file_name, shift_intensity_sale_ff48.

The instrument is at firm-year (gvkey × fiscal-year) granularity. It is
merged onto the manifest via gvkey + fyearq (Compustat fiscal year) to
correctly match ~30% of firms whose fiscal year-end differs from December.

B5 fix: prior code merged on gvkey + calendar year (start_date.dt.year),
which mismatches Compustat controls (matched to fyearq) for all non-December
fiscal year firms. We now:
1. Attach fyearq to the manifest via merge_asof (call start_date → Compustat
   datadate, per-gvkey backward match) — same pattern used for all other
   Compustat variables.
2. Rename CCCL 'year' to 'fyearq' and merge on gvkey + fyearq.

Architecture note: The CCCL file starts in 2005. Calls before 2005 will have
NaN instrument values (expected; those calls drop out of the IV regression
sample but are still included in OLS regressions).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._compustat_engine import get_engine
from f1d.shared.path_utils import get_latest_output_dir


class CCCLInstrumentBuilder(VariableBuilder):
    """Build shift_intensity_sale_ff48 from CCCL instrument parquet.

    B5 fix: merges on gvkey + fyearq (Compustat fiscal year) instead of
    gvkey + calendar year to eliminate temporal mismatch for ~30% of firms
    with non-December fiscal year-ends.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.target_col = config.get("column", "shift_intensity_sale_ff48")

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
        manifest["_cal_year"] = manifest["start_date"].dt.year
        manifest = manifest[manifest["_cal_year"].isin(list(years))].copy()

        # B5 fix: attach fyearq via merge_asof (call start_date → Compustat
        # datadate, per-gvkey backward match) so we merge on fiscal year.
        engine = get_engine()
        comp = engine.get_data(root_path)

        fyearq_df = (
            comp[["gvkey", "datadate", "fyearq"]]
            .dropna(subset=["fyearq"])
            .sort_values("datadate")
            .copy()
        )
        fyearq_df["gvkey"] = fyearq_df["gvkey"].astype(str).str.zfill(6)

        manifest_sorted = manifest.sort_values("start_date").copy()
        merged_fyearq = pd.merge_asof(
            manifest_sorted,
            fyearq_df,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )
        # Drop helper datadate column if introduced
        if "datadate" in merged_fyearq.columns:
            merged_fyearq = merged_fyearq.drop(columns=["datadate"])

        # Convert fyearq to int (it's float64 from Compustat)
        merged_fyearq["fyearq_int"] = pd.to_numeric(
            merged_fyearq["fyearq"], errors="coerce"
        ).astype("Int64")

        n_fyearq_matched = merged_fyearq["fyearq_int"].notna().sum()
        print(
            f"    CCCL: fyearq attached to {n_fyearq_matched:,}/{len(merged_fyearq):,} "
            f"calls ({100.0 * n_fyearq_matched / len(merged_fyearq):.1f}%)"
        )

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
            columns=["gvkey", "year", self.target_col],
        )
        cccl["gvkey"] = cccl["gvkey"].astype(str).str.zfill(6)
        # Rename 'year' → 'fyearq_int': the CCCL instrument year is the
        # Compustat fiscal year (fyearq), constructed from Compustat data.
        cccl = cccl.rename(columns={"year": "fyearq_int"})
        cccl["fyearq_int"] = cccl["fyearq_int"].astype("Int64")

        # Assert uniqueness on gvkey+fyearq_int before merge to prevent fan-out
        if cccl.duplicated(subset=["gvkey", "fyearq_int"]).any():
            n_dups = cccl.duplicated(subset=["gvkey", "fyearq_int"]).sum()
            raise ValueError(
                f"CCCL instrument has {n_dups} duplicate gvkey+fyearq_int rows. "
                "This would cause row fan-out on merge."
            )

        # Merge instrument onto manifest via gvkey + fyearq_int (B5 fix)
        before_len = len(merged_fyearq)
        merged = merged_fyearq.merge(
            cccl,
            on=["gvkey", "fyearq_int"],
            how="left",
        )

        # Hard-fail if merge caused row duplication
        if len(merged) != before_len:
            raise ValueError(
                f"CCCL merge changed row count {before_len} → {len(merged)}. "
                "Duplicate gvkey+fyearq_int in CCCL data caused fan-out."
            )

        # Validate target column present
        if self.target_col not in merged.columns:
            raise ValueError(
                f"'{self.target_col}' not found after CCCL merge. "
                "Check CCCL parquet column names."
            )

        data = merged[["file_name", self.target_col]].copy()
        n_matched = data[self.target_col].notna().sum()
        print(
            f"    CCCL: {n_matched:,}/{len(data):,} calls matched instrument "
            f"({100.0 * n_matched / len(data):.1f}%)"
        )

        stats = self.get_stats(
            data[self.target_col], self.target_col
        )
        return VariableResult(
            data=data,
            stats=stats,
            metadata={
                "column": self.target_col,
                "source": "inputs/CCCL_instrument/",
                "merge_key": "gvkey + fyearq (fiscal year, B5 fix)",
                "note": "NaN for calls before 2005 — expected",
            },
        )


__all__ = ["CCCLInstrumentBuilder"]
