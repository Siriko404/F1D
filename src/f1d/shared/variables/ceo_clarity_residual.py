"""Builder for CEO Clarity Residual variable.

Loads the CEO Q&A uncertainty residual from the CEO Clarity Extended Stage 4
regression. The residual represents the component of CEO language uncertainty
that cannot be explained by firm and linguistic factors.

Source: outputs/econometric/ceo_clarity_extended/{latest}/ceo_clarity_residual.parquet
Output column: CEO_Clarity_Residual
Merge key: file_name (call-level identifier)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from ._clarity_residual_engine import get_engine


class CEOClarityResidualBuilder(VariableBuilder):
    """Build CEO Clarity Residual variable via ClarityResidualEngine.

    The residual is computed in H0.3 CEO Clarity Extended regression as:
        ceo_clarity_residual = CEO_QA_Uncertainty - predicted (from firm/linguistic controls)

    This isolates the idiosyncratic CEO-specific uncertainty component.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "CEO_Clarity_Residual")
        # Skip winsorization - residuals are already cleaned from regression
        self._skip_winsorization = True

    def build(self, years: range, root_path: Path) -> VariableResult:
        engine = get_engine()

        try:
            source_df = engine.get_ceo_residuals(root_path)
        except FileNotFoundError as e:
            # Return empty result if residuals not yet computed
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column, n=0, mean=0.0, std=0.0, min=0.0,
                    p25=0.0, median=0.0, p75=0.0, max=0.0, n_missing=0, pct_missing=100.0
                ),
                metadata={"source": "ClarityResidualEngine", "column": self.column, "error": str(e)}
            )

        # Rename source column to output column name
        data = source_df[["file_name", "ceo_clarity_residual"]].copy()
        data = data.rename(columns={"ceo_clarity_residual": self.column})

        stats = self.get_stats(data[self.column], self.column)

        return VariableResult(
            data=data,
            stats=stats,
            metadata={"source": "ClarityResidualEngine", "column": self.column}
        )


__all__ = ["CEOClarityResidualBuilder"]
