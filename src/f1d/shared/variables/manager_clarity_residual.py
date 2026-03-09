"""Builder for Manager Clarity Residual variable.

Loads the Manager Q&A uncertainty residual from the CEO Clarity Extended Stage 4
regression. The residual represents the component of Manager language uncertainty
that cannot be explained by firm and linguistic factors.

Source: outputs/econometric/ceo_clarity_extended/{latest}/manager_clarity_residual.parquet
Output column: Manager_Clarity_Residual
Merge key: file_name (call-level identifier)
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from ._clarity_residual_engine import get_engine


class ManagerClarityResidualBuilder(VariableBuilder):
    """Build Manager Clarity Residual variable via ClarityResidualEngine.

    The residual is computed in H0.3 CEO Clarity Extended regression as:
        manager_clarity_residual = Manager_QA_Uncertainty - predicted (from firm/linguistic controls)

    This isolates the idiosyncratic management team uncertainty component.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.column = config.get("column", "Manager_Clarity_Residual")
        # Skip winsorization - residuals are already cleaned from regression
        self._skip_winsorization = True

    def build(self, years: range, root_path: Path) -> VariableResult:
        engine = get_engine()

        try:
            source_df = engine.get_manager_residuals(root_path)
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
        data = source_df[["file_name", "manager_clarity_residual"]].copy()
        data = data.rename(columns={"manager_clarity_residual": self.column})

        stats = self.get_stats(data[self.column], self.column)

        return VariableResult(
            data=data,
            stats=stats,
            metadata={"source": "ClarityResidualEngine", "column": self.column}
        )


__all__ = ["ManagerClarityResidualBuilder"]
