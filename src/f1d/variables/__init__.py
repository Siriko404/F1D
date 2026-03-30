"""Stage 3: Variables package for F1D project.

This package contains scripts that build complete panels for each
hypothesis test by loading and merging variables from various sources.

Active Modules (17 panel builders):
    - build_h0_3_ceo_clarity_extended_panel: Extended CEO clarity panel
    - build_h1_cash_holdings_panel: Cash Holdings panel (H1)
    - build_h4_leverage_panel: Leverage panel (H4)
    - build_h5_dispersion_panel: Analyst Forecast Dispersion panel (H5)
    - build_h5b_johnson_disp_panel: Johnson Dispersion panel (H5b)
    - build_h5b_wang_disp_panel: Wang Dispersion panel (H5b)
    - build_h7_illiquidity_panel: Illiquidity panel (H7)
    - build_h9_takeover_panel: Takeover panel (H9)
    - build_h11_prisk_uncertainty_panel: Political Risk x Uncertainty panel (H11)
    - build_h11_prisk_uncertainty_lag_panel: Political Risk x Uncertainty lag panel (H11)
    - build_h11_prisk_uncertainty_lead_panel: Political Risk x Uncertainty lead panel (H11)
    - build_h12_payout_panel: Quarterly Payout Ratio panel (H12)
    - build_h13_capex_panel: Capital Expenditure panel (H13)
    - build_h14_bidask_spread_panel: Bid-Ask Spread panel (H14)
    - build_h16_rd_sales_panel: R&D Investment Intensity panel (H16)
    - build_h17_repurchase_intensity_panel: Repurchase Intensity panel (H17)
    - build_h18_cccl_received_panel: CCCL Received panel (H18)

Archived Modules (in _archived/):
    - build_h0_1_manager_clarity_panel: Superseded by H0.2
    - build_h0_2_ceo_clarity_panel: Archived
    - build_h0_5_ceo_tone_panel: Archived
    - build_h10_tone_at_top_panel: Archived
    - build_h3_payout_policy_panel: Archived (superseded by H12)
    - build_h13_2_employment_panel: Archived
"""

from pathlib import Path

__all__ = []
