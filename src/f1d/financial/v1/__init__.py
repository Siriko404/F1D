"""Financial feature engineering (V1 methodology) for F1D pipeline.

Tier 2: Stage-specific module - Stage 3 V1 variant - Active variant.

This module implements the V1 methodology for constructing
financial variables from Compustat and CRSP data.

IMPORTANT: V1 is NOT deprecated. Both V1 and V2 are active variants
representing different methodology approaches. Use V1 for standard
financial feature construction based on the original methodology.

Modules:
    3.0_BuildFinancialFeatures: Orchestrator for V1 financial features
    3.1_FirmControls: Firm-level control variables
    3.2_MarketVariables: Market-based variables
    3.3_EventFlags: Event flag construction
    3.4_Utils: Utility functions
"""

__all__: list[str] = []
