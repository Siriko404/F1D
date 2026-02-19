"""Builder for CEO Q&A Uncertainty variable.

Loads CEO_QA_Uncertainty_pct from Stage 2 linguistic variables output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class CEOQAUncertaintyBuilder(VariableBuilder):
    """Build CEO Q&A Uncertainty variable from Stage 2 outputs.

    Source: outputs/2_Textual_Analysis/2.2_Variables/latest/
    File: linguistic_variables_{year}.parquet
    Column: CEO_QA_Uncertainty_pct

    Example:
        config = load_variable_config()["ceo_qa_uncertainty"]
        builder = CEOQAUncertaintyBuilder(config)
        result = builder.build(range(2002, 2019), root_path)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with variable config.

        Args:
            config: Must contain 'source', 'file_pattern', 'column'
        """
        super().__init__(config)
        self.column = config.get("column", "CEO_QA_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build CEO Q&A Uncertainty variable.

        Args:
            years: Range of years to process
            root_path: Project root path

        Returns:
            VariableResult with file_name and CEO_QA_Uncertainty_pct columns
        """
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                # Select only needed columns
                cols = ["file_name"]
                if self.column in df.columns:
                    cols.append(self.column)
                all_data.append(df[cols])

        if not all_data:
            # Return empty result with proper schema
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
                    pct_missing=100.0
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


__all__ = ["CEOQAUncertaintyBuilder"]
