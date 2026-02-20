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
        
        ibes_sorted = ibes[["gvkey", "statpers", "dispersion"]].dropna().sort_values("statpers")
        
        manifest_sorted = manifest.sort_values("start_date").dropna(subset=["start_date"])
        manifest_sorted["_row_idx"] = np.arange(len(manifest_sorted))
        
        # Backward merge gets the consensus immediately preceding the call
        t0_df = pd.merge_asof(
            manifest_sorted,
            ibes_sorted,
            left_on="start_date",
            right_on="statpers",
            by="gvkey",
            direction="backward",
        )
        
        # Step 2: To get t+1, we shift the matched consensus forward by 90 days.
        # We then do another backward merge to find the consensus active 90 days from now.
        t0_df["target_lead_date"] = t0_df["start_date"] + pd.Timedelta(days=90)
        
        # Drop the t=0 merge artifacts so we can merge cleanly again
        t0_df = t0_df.drop(columns=["statpers", "dispersion"]).sort_values("target_lead_date")
        
        df = pd.merge_asof(
            t0_df,
            ibes_sorted.rename(columns={"dispersion": "dispersion_lead"}),
            left_on="target_lead_date",
            right_on="statpers",
            by="gvkey",
            direction="backward",
        )
        df = df.sort_values("_row_idx")
        
        # Map back to original manifest to ensure complete rows
        final_merged = manifest[["file_name"]].merge(df[["file_name", "dispersion_lead"]], on="file_name", how="left")

        data = final_merged[["file_name", "dispersion_lead"]].copy()
        stats = self.get_stats(data["dispersion_lead"], "dispersion_lead")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={"column": "dispersion_lead", "source": "IBES (STDEV/|MEANEST|)"},
        )


__all__ = ["DispersionLeadBuilder"]
