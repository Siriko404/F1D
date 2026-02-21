"""Econometric analysis module for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 of the pipeline.

This module runs panel regressions and diagnostics.
Supports both V1 and V2 methodology variants as ACTIVE processing approaches.

Import Guidance:
    - For V1 methodology: from f1d.econometric.v1 import ...
    - For V2 methodology: from f1d.econometric.v2 import ...
    - For new Architecture (Manager Clarity test): run_h0_1_manager_clarity.py

Both V1 and V2 are active variants. Neither is deprecated.
Use the variant appropriate for your research methodology.
"""

__all__: list[str] = []
