"""Econometric analysis (V1 methodology) for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 V1 variant - Active variant.

This module implements the V1 methodology for panel
regressions and model diagnostics.

IMPORTANT: V1 is NOT deprecated. Both V1 and V2 are active variants
representing different methodology approaches. Use V1 for CEO clarity
estimation, liquidity regressions, takeover hazard models, and summary
statistics generation.

Modules:
    4.1_EstimateCeoClarity: CEO clarity score estimation
    4.1.1_EstimateCeoClarity_CeoSpecific: CEO-specific clarity
    4.1.2_EstimateCeoClarity_Extended: Extended clarity model
    4.1.3_EstimateCeoClarity_Regime: Regime-based clarity
    4.1.4_EstimateCeoTone: CEO tone estimation
    4.2_LiquidityRegressions: Stock liquidity regressions
    4.3_TakeoverHazards: Takeover hazard models
    4.4_GenerateSummaryStats: Summary statistics generation
"""

__all__: list[str] = []
