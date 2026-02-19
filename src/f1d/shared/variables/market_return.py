"""Builder for Market Return variable.

Delegates to CRSPReturnsBuilder and returns only the MarketRet column.
Raw computation is in crsp_returns.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .crsp_returns import CRSPReturnsBuilder


class MarketReturnBuilder(VariableBuilder):
    """Build Market Return variable from raw CRSP daily stock files.

    Delegates to CRSPReturnsBuilder, returns only file_name + MarketRet.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._delegate = CRSPReturnsBuilder(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        result = self._delegate.build(years, root_path)
        data = result.data[["file_name", "MarketRet"]].copy()
        stats = self.get_stats(data["MarketRet"], "MarketRet")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={**result.metadata, "column": "MarketRet"},
        )


__all__ = ["MarketReturnBuilder"]
