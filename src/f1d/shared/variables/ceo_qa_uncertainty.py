"""Builder for CEO Q&A Uncertainty variable.

Queries the shared LinguisticEngine for CEO_QA_Uncertainty_pct.
Winsorization (pooled 1%/99%) is applied at engine level for consistency.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from ._linguistic_engine import get_engine


class CEOQAUncertaintyBuilder(VariableBuilder):
    """Build CEO Q&A Uncertainty variable via LinguisticEngine.

    Source: outputs/2_Textual_Analysis/2.2_Variables/latest/
    Column: CEO_QA_Uncertainty_pct
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "CEO_QA_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        engine = get_engine()
        all_data = engine.get_data(root_path, years)

        if self.column not in all_data.columns:
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column, n=0, mean=0.0, std=0.0, min=0.0,
                    p25=0.0, median=0.0, p75=0.0, max=0.0, n_missing=0, pct_missing=100.0
                ),
                metadata={"source": "LinguisticEngine", "column": self.column}
            )

        data = all_data[["file_name", self.column]].copy()
        stats = self.get_stats(data[self.column], self.column)

        return VariableResult(
            data=data,
            stats=stats,
            metadata={"source": "LinguisticEngine", "column": self.column}
        )


__all__ = ["CEOQAUncertaintyBuilder"]
