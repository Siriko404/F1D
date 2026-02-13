"""Financial feature engineering module for F1D pipeline.

Tier 2: Stage-specific module - Stage 3 of the pipeline.

This module constructs financial variables from Compustat and CRSP data.
Supports both V1 and V2 methodology variants as ACTIVE processing approaches.

Import Guidance:
    - For V1 methodology: from f1d.financial.v1 import ...
    - For V2 methodology: from f1d.financial.v2 import ...

Both V1 and V2 are active variants. Neither is deprecated.
Use the variant appropriate for your research methodology.
"""

__all__: list[str] = []
