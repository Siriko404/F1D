"""Builder for EPS Growth variable.

Delegates to CompustatControlsBuilder and returns only the EPS_Growth column.
Raw computation is in compustat_controls.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats
from .compustat_controls import CompustatControlsBuilder


class EPSGrowthBuilder(VariableBuilder):
    """Build EPS Growth variable from raw Compustat quarterly data.

    Delegates to CompustatControlsBuilder, returns only file_name + EPS_Growth.
    """

    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self._delegate = CompustatControlsBuilder(config)

    def build(self, years: range, root_path: Path) -> VariableResult:
        result = self._delegate.build(years, root_path)
        data = result.data[["file_name", "EPS_Growth"]].copy()
        stats = self.get_stats(data["EPS_Growth"], "EPS_Growth")
        return VariableResult(
            data=data,
            stats=stats,
            metadata={**result.metadata, "column": "EPS_Growth"},
        )


__all__ = ["EPSGrowthBuilder"]
