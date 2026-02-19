"""Builder for Stock Return variable.

Delegates to CRSPReturnsBuilder and returns only the StockRet column.
Raw computation is in crsp_returns.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .crsp_returns import CRSPReturnsBuilder


class StockReturnBuilder(VariableBuilder):
    """Build Stock Return variable from raw CRSP daily stock files.

    Delegates to CRSPReturnsBuilder, returns only file_name + StockRet.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._delegate = CRSPReturnsBuilder(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        result = self._delegate.build(years, root_path)
        data = result.data[["file_name", "StockRet"]].copy()
        stats = self.get_stats(data["StockRet"], "StockRet")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={**result.metadata, "column": "StockRet"},
        )


__all__ = ["StockReturnBuilder"]
