"""Econometric analysis module for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 of the pipeline.

This module runs panel regressions and diagnostics.
Supports both V1 and V2 methodology variants as ACTIVE processing approaches.

Modules:
    - run_h0_1_manager_clarity: Run Manager Clarity hypothesis test
    - run_h0_2_ceo_clarity: Run CEO Clarity hypothesis test
    - run_h0_3_ceo_clarity_extended: Run extended CEO Clarity hypothesis test
    - run_h0_4_ceo_clarity_regime: Run CEO Clarity regime analysis
    - run_h0_5_ceo_tone: Run CEO Tone hypothesis test
    - run_h1_cash_holdings: Run Cash Holdings hypothesis test
    - run_h2_investment: Run Investment hypothesis test
    - run_h3_payout_policy: Run Payout Policy hypothesis test
    - run_h4_leverage: Run Leverage hypothesis test
    - run_h5_dispersion: Run Dispersion hypothesis test
    - run_h6_cccl: Run CCCL hypothesis test
    - run_h7_illiquidity: Run Illiquidity hypothesis test
    - run_h8_political_risk: Run Political Risk hypothesis test
    - run_h9_takeover_hazards: Run Takeover Hazards hypothesis test
    - run_h10_tone_at_top: Run Tone at the Top hypothesis test
    - generate_h03_complete_table: Generate complete LaTeX table for H0.3

Import Guidance:
    - For V1 methodology: from f1d.econometric.v1 import ...
    - For V2 methodology: from f1d.econometric.v2 import ...
    - For new Architecture (Manager Clarity test): run_h0_1_manager_clarity.py

Both V1 and V2 are active variants. Neither is deprecated.
Use the variant appropriate for your research methodology.
"""

__all__: list[str] = []
