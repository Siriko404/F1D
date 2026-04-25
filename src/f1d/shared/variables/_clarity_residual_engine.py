"""Private engine to load clarity residuals from CEO Clarity Extended Stage 4 output.

This engine loads the residual parquet files from the most recent
ceo_clarity_extended econometric run and caches them for reuse.

Used by: CEOClarityResidualBuilder, ManagerClarityResidualBuilder

Source files (from outputs/econometric/ceo_clarity_extended/{latest}/):
    - ceo_clarity_residual.parquet (column: UncResCEO — DWZ-faithful name post-2026-04-24)
    - manager_clarity_residual.parquet (column: UncResMgr — DWZ-faithful name post-2026-04-24)
    - ceo_clarity_fe.parquet (cols: ceo_id, FE_CEO, ClarityCEO)
    - manager_clarity_fe.parquet (cols: ceo_id, FE_Mgr, ClarityMgr)

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

        print(f"    ClarityResidualEngine: Loading from {output_dir}")

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
        """Get CEO Q&A clarity residuals (DWZ Eq.4 full-sample baseline).

        Returns DataFrame with columns: file_name, UncResCEO
        """
        return self._load_residuals(
            root_path, "ceo_clarity_residual.parquet", "ceo"
        )

    def get_manager_residuals(self, root_path: Path) -> pd.DataFrame:
        """Get Manager Q&A clarity residuals (DWZ Eq.4 full-sample baseline).

        Returns DataFrame with columns: file_name, UncResMgr
        """
        return self._load_residuals(
            root_path, "manager_clarity_residual.parquet", "manager"
        )

    def get_ceo_fe(self, root_path: Path) -> pd.DataFrame:
        """Get CEO entity FE table (DWZ Eq.5 ClarityCEO = -CEO_FE).

        Returns DataFrame with columns: ceo_id, FE_CEO, ClarityCEO
        """
        return self._load_residuals(
            root_path, "ceo_clarity_fe.parquet", "ceo_fe"
        )

    def get_manager_fe(self, root_path: Path) -> pd.DataFrame:
        """Get Manager entity FE table (CEO-grain Mgr-pool FE).

        Returns DataFrame with columns: ceo_id, FE_Mgr, ClarityMgr
        """
        return self._load_residuals(
            root_path, "manager_clarity_fe.parquet", "mgr_fe"
        )


# Module-level singleton
_engine = ClarityResidualEngine()


def get_engine() -> ClarityResidualEngine:
    """Return the module-level singleton ClarityResidualEngine."""
    return _engine


__all__ = ["ClarityResidualEngine", "get_engine"]
