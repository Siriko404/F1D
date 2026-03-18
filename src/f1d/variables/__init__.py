"""Stage 3: Variables package for F1D project.

This package contains scripts that build complete panels for each
hypothesis test by loading and merging variables from various sources.

Active Modules:
    - build_h0_3_ceo_clarity_extended_panel: Build extended CEO clarity panel
    - build_h1_cash_holdings_panel: Build panel for Cash Holdings test (H1)
    - build_h2_investment_panel: Build panel for Investment test (H2)
    - build_h4_leverage_panel: Build panel for Leverage test (H4)
    - build_h5_dispersion_panel: Build panel for Dispersion test (H5)
    - build_h6_cccl_panel: Build panel for CCCL test (H6)
    - build_h7_illiquidity_panel: Build panel for Illiquidity test (H7)
    - build_h9_takeover_panel: Build panel for Takeover test (H9)
    - build_h13_capex_panel: Build panel for Capital Expenditure test (H13)
    - build_h14_bidask_spread_panel: Build panel for Bid-Ask Spread test (H14)
    - build_h15_repurchase_panel: Build panel for Share Repurchase test (H15)

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
