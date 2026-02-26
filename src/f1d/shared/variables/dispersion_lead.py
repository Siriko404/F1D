"""Builder for dispersion_lead (H5 Dependent Variable).

Fetches the t+1 quarter analyst forecast dispersion from the IBES engine.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult
from ._ibes_engine import get_engine as get_ibes_engine
from ._compustat_engine import get_engine as get_compustat_engine
from f1d.shared.path_utils import get_latest_output_dir


class DispersionLeadBuilder(VariableBuilder):
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

        # Step 1: Match call to exactly the prior consensus (t=0)
        i_engine = get_ibes_engine()
        ibes = i_engine.get_data(root_path)

        ibes_sorted = (
            ibes[["gvkey", "statpers", "dispersion"]].dropna().sort_values("statpers")
        )

        manifest_sorted = manifest.sort_values("start_date").dropna(
            subset=["start_date"]
        )
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))

        # To get t+1, we find the first consensus strictly AFTER the call date.
        target_df = manifest_sorted.copy()
        target_df["target_date"] = target_df["start_date"] + pd.Timedelta(days=1)
        target_df = target_df.sort_values("target_date")

        df = pd.merge_asof(
            target_df,
            ibes_sorted.rename(columns={"dispersion": "dispersion_lead"}),
            left_on="target_date",
            right_on="statpers",
            by="gvkey",
            direction="forward",
            tolerance=pd.Timedelta(days=180),
        )
        df = df.sort_values("_row_idx")

        # Map back to original manifest to ensure complete rows
        final_merged = manifest[["file_name"]].merge(
            df[["file_name", "dispersion_lead"]], on="file_name", how="left"
        )

        data = final_merged[["file_name", "dispersion_lead"]].copy()
        stats = self.get_stats(data["dispersion_lead"], "dispersion_lead")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "dispersion_lead", "source": "IBES (STDEV/|MEANEST|)"},
        )


__all__ = ["DispersionLeadBuilder"]
