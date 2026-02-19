"""Builder for manifest fields (ceo_id, gvkey, ff12_code, start_date, etc.).

Loads key identifier and classification fields from Stage 1 manifest output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class ManifestFieldsBuilder(VariableBuilder):
    """Build manifest fields from Stage 1 outputs.

    Source: outputs/1.4_AssembleManifest/latest/
    File: master_sample_manifest.parquet
    Columns: file_name, ceo_id, ceo_name, gvkey, ff12_code, ff12_name, start_date

    This builder returns multiple columns (all manifest fields) rather than
    a single variable column.
    """

    # Default columns to load from manifest
    DEFAULT_COLUMNS = [
        "file_name",
        "ceo_id",
        "ceo_name",
        "gvkey",
        "ff12_code",
        "ff12_name",
        "start_date",
    ]

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.columns = config.get("columns", self.DEFAULT_COLUMNS)
        self.file_name = config.get("file_name", "master_sample_manifest.parquet")

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build manifest fields.

        Note: The manifest is a single file, not year-partitioned.
        The years parameter is used to filter to relevant years if start_date is available.

        Args:
            years: Range of years to include (filters by start_date)
            root_path: Project root path

        Returns:
            VariableResult with manifest columns
        """
        source_dir = self.resolve_source_dir(root_path)
        manifest_path = source_dir / self.file_name

        if not manifest_path.exists():
            # Return empty result with error info
            cols = self.columns
            return VariableResult(
                data=pd.DataFrame(columns=cols),
                stats=VariableStats(
                    name="manifest", n=0, mean=0.0, std=0.0, min=0.0,
                    p25=0.0, median=0.0, p75=0.0, max=0.0, n_missing=0, pct_missing=100.0
                ),
                metadata={
                    "source": str(source_dir),
                    "file": self.file_name,
                    "error": f"File not found: {manifest_path}"
                }
            )

        # Load manifest
        df = pd.read_parquet(manifest_path)

        # Select available columns
        available_cols = [c for c in self.columns if c in df.columns]
        df = df[available_cols].copy()

        # Filter by year if start_date is available
        if "start_date" in df.columns:
            # Convert to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df["start_date"]):
                df["start_date"] = pd.to_datetime(df["start_date"], errors="coerce")

            # Extract year and filter
            df["year"] = df["start_date"].dt.year
            year_list = list(years)
            df = df[df["year"].isin(year_list)].copy()

        # Create stats for row count
        stats = VariableStats(
            name="manifest",
            n=len(df),
            mean=float(len(df)),
            std=0.0,
            min=0.0,
            p25=0.0,
            median=0.0,
            p75=0.0,
            max=0.0,
            n_missing=0,
            pct_missing=0.0
        )

        return VariableResult(
            data=df,
            stats=stats,
            metadata={"source": str(manifest_path), "columns": available_cols}
        )


__all__ = ["ManifestFieldsBuilder"]
