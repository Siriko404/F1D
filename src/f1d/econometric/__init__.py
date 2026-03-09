"""Econometric analysis module for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 of the pipeline.

This module runs panel regressions and diagnostics.

Active Modules:
    - run_h0_2_ceo_clarity: Run CEO Clarity hypothesis test
    - run_h0_3_ceo_clarity_extended: Run extended CEO Clarity robustness check
    - run_h1_cash_holdings: Run Cash Holdings hypothesis test
    - run_h2_investment: Run Investment hypothesis test
    - run_h3_payout_policy: Run Payout Policy hypothesis test
    - run_h4_leverage: Run Leverage hypothesis test
    - run_h5_dispersion: Run Dispersion hypothesis test
    - run_h6_cccl: Run CCCL hypothesis test
    - run_h7_illiquidity: Run Illiquidity hypothesis test
    - run_h9_takeover_hazards: Run Takeover Hazards hypothesis test

Archived Modules (in _archived/):
    - run_h0_1_manager_clarity: Superseded by H0.2
    - run_h0_4_ceo_clarity_regime: Consolidated into H0.2
    - run_h0_5_ceo_tone: Archived
    - run_h10_tone_at_top: Archived
    - generate_h03_complete_table: Temporary workaround, now obsolete
"""

__all__: list[str] = []
