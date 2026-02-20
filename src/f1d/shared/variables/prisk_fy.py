"""Builder for PRiskFY variable — H8.

Reads Hassan et al. (2019) quarterly PRisk data via the HassanEngine singleton
and maps fiscal-year-level PRiskFY values onto individual earnings calls.

Returns per-call data:
    file_name : earnings call identifier
    PRiskFY   : mean quarterly PRisk over (fy_end - 366d, fy_end], NaN if
                fewer than 2 quarters available (no interpolation/forward-fill)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult
from ._hassan_engine import get_engine as get_hassan_engine
from ._compustat_engine import get_engine as get_compustat_engine
from f1d.shared.path_utils import get_latest_output_dir


class PRiskFYBuilder(VariableBuilder):
    """Map fiscal-year PRiskFY onto each earnings call."""

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        # 1. Load manifest
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

        # 2. Retrieve PRiskFY from engine (cached)
        hassan_engine = get_hassan_engine()
        priskfy = hassan_engine.get_data(root_path)
        # priskfy has: gvkey, fyearq, PRiskFY, n_quarters_used

        # 3. Attach fyearq to each call via merge_asof(backward) on start_date
        comp_engine = get_compustat_engine()
        comp_df = comp_engine.get_data(root_path)

        fyearq_df = (
            comp_df[["gvkey", "fyearq", "datadate"]]
            .dropna(subset=["fyearq", "datadate"])
            .copy()
        )
        fyearq_df["fyearq"] = pd.to_numeric(fyearq_df["fyearq"], errors="coerce")
        fyearq_df = fyearq_df.dropna(subset=["fyearq"]).copy()
        fyearq_df["fyearq"] = fyearq_df["fyearq"].astype(int)
        fyearq_df["datadate"] = pd.to_datetime(fyearq_df["datadate"], errors="coerce")
        fyearq_df = (
            fyearq_df.dropna(subset=["datadate"])
            .sort_values("datadate")
        )

        manifest_sorted = manifest.sort_values("start_date").copy()
        merged = pd.merge_asof(
            manifest_sorted,
            fyearq_df,
            left_on="start_date",
            right_on="datadate",
            by="gvkey",
            direction="backward",
        )

        # 4. Map PRiskFY via (gvkey, fyearq)
        priskfy["gvkey"] = priskfy["gvkey"].astype(str).str.zfill(6)
        merged["fyearq"] = pd.to_numeric(merged.get("fyearq"), errors="coerce")
        merged["fyearq"] = merged["fyearq"].where(merged["fyearq"].notna(), other=None)
        merged = merged.merge(
            priskfy[["gvkey", "fyearq", "PRiskFY"]],
            on=["gvkey", "fyearq"],
            how="left",
        )

        # 5. Align back to original manifest (preserve row order & count)
        data = manifest[["file_name"]].merge(
            merged[["file_name", "PRiskFY"]], on="file_name", how="left"
        )
        data = data.drop_duplicates(subset=["file_name"])

        return VariableResult(
            data=data[["file_name", "PRiskFY"]].copy(),
            stats=self.get_stats(data["PRiskFY"], "PRiskFY"),
            metadata={
                "column": "PRiskFY",
                "source": "Hassan et al. (2019) PRisk via HassanEngine",
                "description": (
                    "Mean quarterly PRisk over (fy_end - 366d, fy_end]; "
                    "min 2 quarters required; no forward-fill."
                ),
            },
        )


__all__ = ["PRiskFYBuilder"]
