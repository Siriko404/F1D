"""Econometric analysis module for F1D pipeline.

Tier 2: Stage-specific module - Stage 4 of the pipeline.

This module runs panel regressions and diagnostics.

Active Modules (19 runners):
    - run_h0_3_ceo_clarity_extended: Extended CEO Clarity robustness check
    - run_h1_cash_holdings: Cash Holdings hypothesis test
    - run_h1_1_cash_tsimm: Cash Holdings (Tsimm channel/moderation)
    - run_h1_1b_cash_tsimm_binary: Cash Holdings (Tsimm binary)
    - run_h1_2_cash_constraint: Cash Constraint hypothesis test
    - run_h4_leverage: Leverage hypothesis test
    - run_h5b_wang_disp: Analyst Forecast Dispersion hypothesis test (H5, Wang 2020)
    - run_h7_illiquidity: Illiquidity hypothesis test
    - run_h9_takeover_hazards: Takeover Hazards hypothesis test
    - run_h11_prisk_uncertainty: Political Risk x Uncertainty hypothesis test
    - run_h11_prisk_uncertainty_lag: Political Risk x Uncertainty (lagged)
    - run_h11_prisk_uncertainty_lead: Political Risk x Uncertainty (lead)
    - run_h12_payout: Quarterly Payout Ratio hypothesis test
    - run_h13_1_competition: Product Market Competition hypothesis test
    - run_h13_capex: Capital Expenditure hypothesis test
    - run_h14_bidask_spread: Bid-Ask Spread hypothesis test
    - run_h16_rd_sales: R&D Investment Intensity hypothesis test
    - run_h17_repurchase_intensity: Repurchase Intensity hypothesis test
    - run_h18_cccl_received: CCCL Received hypothesis test

Archived Modules (in _archived/):
    - run_h0_1_manager_clarity: Superseded by H0.2
    - run_h0_2_ceo_clarity: Archived
    - run_h0_4_ceo_clarity_regime: Consolidated into H0.2
    - run_h0_5_ceo_tone: Archived
    - run_h10_tone_at_top: Archived
    - run_h3_payout_policy: Archived (superseded by H12)
    - run_h13_2_employment: Archived
"""

__all__: list[str] = []
