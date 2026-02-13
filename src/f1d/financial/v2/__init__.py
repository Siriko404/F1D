"""Financial feature engineering (V2 methodology) for F1D pipeline.

Tier 2: Stage-specific module - Stage 3 V2 variant - Active variant.

This module implements the V2 methodology for constructing
financial variables from Compustat and CRSP data.

IMPORTANT: V2 is NOT deprecated. Both V1 and V2 are active variants
representing different methodology approaches. Use V2 for hypothesis-specific
variable construction with enhanced features.

Modules:
    3.1_H1Variables: H1 (Cash Holdings) variables
    3.2_H2Variables: H2 (Investment Efficiency) variables
    3.3_H3Variables: H3 (Payout Policy) variables
    3.5_H5Variables: H5 (Analyst Dispersion) variables
    3.6_H6Variables: H6 (CCC) variables
    3.7_H7IlliquidityVariables: H7 (Illiquidity) variables
    3.8_H8TakeoverVariables: H8 (Takeover) variables
    3.9_H2_BiddleInvestmentResidual: Investment residual calculation
    3.10_H2_PRiskUncertaintyMerge: PRisk uncertainty merge
    3.11_H9_StyleFrozen: CEO style frozen variables
    3.12_H9_PRiskFY: PRisk fiscal year variables
    3.13_H9_AbnormalInvestment: Abnormal investment calculation
"""

__all__: list[str] = []
