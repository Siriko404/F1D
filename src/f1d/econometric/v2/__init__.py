"""Econometric analysis (V2 methodology) for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 V2 variant - Active variant.

This module implements the V2 methodology for panel
regressions and model diagnostics.

IMPORTANT: V2 is NOT deprecated. Both V1 and V2 are active variants
representing different methodology approaches. Use V2 for hypothesis-specific
regression models (H1-H9).

Modules:
    4.1_H1CashHoldingsRegression: H1 (Cash Holdings) regressions
    4.2_H2InvestmentEfficiencyRegression: H2 (Investment Efficiency)
    4.3_H3PayoutPolicyRegression: H3 (Payout Policy) regressions
    4.4_H4_LeverageDiscipline: H4 (Leverage Discipline) regressions
    4.5_H5DispersionRegression: H5 (Analyst Dispersion) regressions
    4.6_H6CCCLRegression: H6 (CCC) regressions
    4.7_H7IlliquidityRegression: H7 (Illiquidity) regressions
    4.8_H8TakeoverRegression: H8 (Takeover) regressions
    4.9_CEOFixedEffects: CEO fixed effects estimation
    4.10_H2_PRiskUncertainty_Investment: PRisk investment regressions
    4.11_H9_Regression: H9 (Abnormal Investment) regressions
"""

__all__: list[str] = []
