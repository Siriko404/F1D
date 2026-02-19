"""Builder for EPS Growth variable.

Loads EPS_Growth from Stage 3 firm controls output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class EPSGrowthBuilder(VariableBuilder):
    """Build EPS Growth variable from Stage 3 outputs.

    Source: outputs/3_Financial_Features/latest/
    File: firm_controls_{year}.parquet
    Column: EPS_Growth
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "EPS_Growth")

    def build(self, years: range, root_path: Path) -> VariableResult:
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                cols = ["file_name"]
                if self.column in df.columns:
                    cols.append(self.column)
                all_data.append(df[cols])

        if not all_data:
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column, n=0, mean=0.0, std=0.0, min=0.0,
                    p25=0.0, median=0.0, p75=0.0, max=0.0, n_missing=0, pct_missing=100.0
                ),
                metadata={"source": str(source_dir), "column": self.column}
            )

        combined = pd.concat(all_data, ignore_index=True)
        stats = self.get_stats(combined[self.column], self.column)

        return VariableResult(
            data=combined[["file_name", self.column]],
            stats=stats,
            metadata={"source": str(source_dir), "column": self.column}
        )


__all__ = ["EPSGrowthBuilder"]
