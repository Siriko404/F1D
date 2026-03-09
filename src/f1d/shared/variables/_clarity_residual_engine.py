"""Private engine to load clarity residuals from CEO Clarity Extended Stage 4 output.

This engine loads the residual parquet files from the most recent
ceo_clarity_extended econometric run and caches them for reuse.

Used by: CEOClarityResidualBuilder, ManagerClarityResidualBuilder

Source files (from outputs/econometric/ceo_clarity_extended/{latest}/):
    - ceo_clarity_residual.parquet (column: ceo_clarity_residual)
    - manager_clarity_residual.parquet (column: manager_clarity_residual)

Both merge on file_name (call-level identifier).

NOT a VariableBuilder — this is an internal helper.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from f1d.shared.path_utils import get_latest_output_dir


class ClarityResidualEngine:
    """Load and cache clarity residuals from CEO Clarity Extended output.

    The engine finds the most recent timestamped directory in
    outputs/econometric/ceo_clarity_extended/ and loads both residual files.

    Usage:
        engine = ClarityResidualEngine()
        ceo_df = engine.get_ceo_residuals(root_path)
        mgr_df = engine.get_manager_residuals(root_path)
    """

    def __init__(self) -> None:
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_root: Optional[Path] = None

    def _get_output_dir(self, root_path: Path) -> Path:
        """Find the most recent ceo_clarity_extended output directory."""
        base_dir = root_path / "outputs" / "econometric" / "ceo_clarity_extended"
        return get_latest_output_dir(base_dir)

    def _load_residuals(self, root_path: Path, file_name: str, cache_key: str) -> pd.DataFrame:
        """Load a residual parquet file (cached)."""
        if self._cache_root == root_path and cache_key in self._cache:
            return self._cache[cache_key]

        output_dir = self._get_output_dir(root_path)
        file_path = output_dir / file_name

        if not file_path.exists():
            raise FileNotFoundError(
                f"Clarity residual file not found: {file_path}\n"
                f"Run H0.3 CEO Clarity Extended Stage 4 first."
            )

        df = pd.read_parquet(file_path)
        self._cache[cache_key] = df
        self._cache_root = root_path
        return df

    def get_ceo_residuals(self, root_path: Path) -> pd.DataFrame:
        """Get CEO Q&A clarity residuals.

        Returns DataFrame with columns: file_name, ceo_clarity_residual
        """
        return self._load_residuals(
            root_path, "ceo_clarity_residual.parquet", "ceo"
        )

    def get_manager_residuals(self, root_path: Path) -> pd.DataFrame:
        """Get Manager Q&A clarity residuals.

        Returns DataFrame with columns: file_name, manager_clarity_residual
        """
        return self._load_residuals(
            root_path, "manager_clarity_residual.parquet", "manager"
        )


# Module-level singleton
_engine = ClarityResidualEngine()


def get_engine() -> ClarityResidualEngine:
    """Return the module-level singleton ClarityResidualEngine."""
    return _engine


__all__ = ["ClarityResidualEngine", "get_engine"]
