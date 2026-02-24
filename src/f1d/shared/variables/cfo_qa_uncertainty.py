"""Builder for CFO Q&A Uncertainty variable.

Extracts CFO-specific uncertainty from the speaker-level tokenize output
by applying a strict regex filter for CFO roles.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class CFOQAUncertaintyBuilder(VariableBuilder):
    """Build CFO Q&A Uncertainty variable from Stage 2.1 tokenize output.

    Reads linguistic_counts_{year}.parquet directly.
    Filters to context == "qa" and role matching narrow CFO pattern.
    Aggregates by file_name using ratio-of-sums.
    """

    # Narrow CFO role pattern (Option A) — used with str.contains() (vectorized)
    CFO_ROLE_PATTERN = (
        r"(?i)\bCFO\b"
        r"|Chief\s+Financial"
        r"|Financial\s+Officer"
        r"|Principal\s+Financial"
    )

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "CFO_QA_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                # Filter to QA context and valid roles
                df = df[df["context"].str.lower() == "qa"].copy()
                df = df[df["role"].notna()].copy()

                # Apply CFO pattern — vectorized str.contains() replaces
                # per-row .apply(lambda: regex.search()), 5-20x faster
                is_cfo = df["role"].str.contains(
                    self.CFO_ROLE_PATTERN, regex=True, na=False
                )
                df_cfo = df[is_cfo].copy()

                if not df_cfo.empty:
                    # Aggregate per call: sum(Uncertainty) / sum(Total) * 100
                    agg = (
                        df_cfo.groupby("file_name")
                        .agg({"Uncertainty_count": "sum", "total_tokens": "sum"})
                        .reset_index()
                    )

                    # Ratio of sums
                    agg[self.column] = np.where(
                        agg["total_tokens"] > 0,
                        (agg["Uncertainty_count"] / agg["total_tokens"]) * 100.0,
                        0.0,
                    )

                    all_data.append(agg[["file_name", self.column]])

        if not all_data:
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column,
                    n=0,
                    mean=0.0,
                    std=0.0,
                    min=0.0,
                    p25=0.0,
                    median=0.0,
                    p75=0.0,
                    max=0.0,
                    n_missing=0,
                    pct_missing=100.0,
                ),
                metadata={
                    "source": str(source_dir),
                    "column": self.column,
                    "pattern": "Option A Narrow",
                },
            )

        combined = pd.concat(all_data, ignore_index=True)
        combined = self._finalize_data(combined)  # Pooled 1%/99% winsorization
        stats = self.get_stats(combined[self.column], self.column)

        return VariableResult(
            data=combined[["file_name", self.column]],
            stats=stats,
            metadata={
                "source": str(source_dir),
                "column": self.column,
                "pattern": "Option A Narrow",
                "description": "CFO Q&A Uncertainty % via ratio-of-sums",
            },
        )


__all__ = ["CFOQAUncertaintyBuilder"]
