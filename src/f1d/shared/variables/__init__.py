"""Shared variable builders for F1D project.

Each shared module builds exactly ONE variable and returns a VariableResult
with file_name + that variable's column. Stage 3 panel builders import
the individual builders they need and merge the results.

Architecture:
    Private compute engines (not VariableBuilders):
        _compustat_engine.CompustatEngine  — loads Compustat once, caches result
        _crsp_engine.CRSPEngine            — loads CRSP yearly, caches result

    Individual Compustat variable builders (one column each):
        SizeBuilder           → lnAssets = ln(atq)
        BMBuilder             → BTM = ceqq / (cshoq * prccq)
        BookLevBuilder        → Leverage = (dlcq + dlttq) / atq
        ROABuilder            → ROA = iby_annual / avg_assets
        CurrentRatioBuilder   → CurrentRatio = actq / lctq
        RDIntensityBuilder    → RDSales = xrdq / atq
        EPSGrowthBuilder      → EPSgrowth (date-based YoY, robust to gaps)
        CashHoldingsBuilder   → CashRatio = cheq / atq
        TobinsQBuilder        → TobinsQ = (atq + cshoq*prccq - ceqq) / atq
        CapexIntensityBuilder → Capex = capxy_Q4 / atq
        DividendPayerBuilder  → DivDummy = (dvy_Q4 > 0).astype(float)
        OCFVolatilityBuilder  → sCFO = rolling 5yr std (min 3) of oancfy/atq_{t-1}

    Individual CRSP variable builders (one column each):
        StockReturnBuilder    → StockRet (compound return over call window)
        MarketReturnBuilder   → MarketRet (compound VWRETD over call window)
        VolatilityBuilder     → DailyVola (annualized std over call window)

    IBES variable builder:
        EarningsSurpriseBuilder → SurpDec (earnings surprise decile -5..+5)

    Textual variable builders (read Stage 2 outputs):
        ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder,
        AnalystQAUncertaintyBuilder, NegativeSentimentBuilder,
        EntireAllUncertaintyBuilder, CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder,
        ManagerQAPositiveBuilder, ManagerQANegativeBuilder,
        ManagerPresPositiveBuilder, ManagerPresNegativeBuilder,
        CEOQAPositiveBuilder, CEOQANegativeBuilder,
        CEOPresPositiveBuilder, CEOPresNegativeBuilder,
        NonCEOManagerQAPositiveBuilder, NonCEOManagerQANegativeBuilder,
        AnalystQAPositiveBuilder, AnalystQANegativeBuilder,
        ManagerQAWeakModalBuilder, CEOQAWeakModalBuilder,
        ManagerPresWeakModalBuilder, CEOPresWeakModalBuilder

Usage:
    # Clarity pipeline
    from f1d.shared.variables import (
        CEOQAUncertaintyBuilder,
        CEOPresUncertaintyBuilder,
        AnalystQAUncertaintyBuilder,
        NegativeSentimentBuilder,
        EPSGrowthBuilder,
        StockReturnBuilder,
        MarketReturnBuilder,
        EarningsSurpriseBuilder,
        ManifestFieldsBuilder,
    )

    # Tone pipeline (B.3)
    from f1d.shared.variables import (
        EntireAllUncertaintyBuilder,
        ManagerQAPositiveBuilder, ManagerQANegativeBuilder,
        ManagerPresPositiveBuilder, ManagerPresNegativeBuilder,
        CEOQAPositiveBuilder, CEOQANegativeBuilder,
        CEOPresPositiveBuilder, CEOPresNegativeBuilder,
        NonCEOManagerQAPositiveBuilder, NonCEOManagerQANegativeBuilder,
        AnalystQAPositiveBuilder, AnalystQANegativeBuilder,
    )
"""

from .base import (
    VariableBuilder,
    VariableResult,
    VariableStats,
    stats_to_dict,
    stats_list_to_dataframe,
)

# Textual variables (Stage 2 outputs)
from .manager_qa_uncertainty import ManagerQAUncertaintyBuilder
from .manager_pres_uncertainty import ManagerPresUncertaintyBuilder
from .analyst_qa_uncertainty import AnalystQAUncertaintyBuilder
from .negative_sentiment import NegativeSentimentBuilder
from .entire_all_uncertainty import EntireAllUncertaintyBuilder
from .ceo_qa_uncertainty import CEOQAUncertaintyBuilder
from .ceo_pres_uncertainty import CEOPresUncertaintyBuilder
from .nonceo_manager_qa_uncertainty import NonCEOManagerQAUncertaintyBuilder
from .nonceo_manager_pres_uncertainty import NonCEOManagerPresUncertaintyBuilder

# Tone/sentiment builders (Positive/Negative pct per speaker/context — Stage 2)
from .manager_qa_positive import ManagerQAPositiveBuilder
from .manager_qa_negative import ManagerQANegativeBuilder
from .manager_pres_positive import ManagerPresPositiveBuilder
from .manager_pres_negative import ManagerPresNegativeBuilder
from .ceo_qa_positive import CEOQAPositiveBuilder
from .ceo_qa_negative import CEOQANegativeBuilder
from .ceo_pres_positive import CEOPresPositiveBuilder
from .ceo_pres_negative import CEOPresNegativeBuilder
from .nonceo_manager_qa_positive import NonCEOManagerQAPositiveBuilder
from .nonceo_manager_qa_negative import NonCEOManagerQANegativeBuilder
from .analyst_qa_positive import AnalystQAPositiveBuilder
from .analyst_qa_negative import AnalystQANegativeBuilder

# Weak modal builders (H1 extension — Stage 2 outputs)
from .manager_qa_weak_modal import ManagerQAWeakModalBuilder
from .ceo_qa_weak_modal import CEOQAWeakModalBuilder
from .manager_pres_weak_modal import ManagerPresWeakModalBuilder
from .ceo_pres_weak_modal import CEOPresWeakModalBuilder

# Compustat individual variable builders
from .size import SizeBuilder
from .bm import BMBuilder
from .lev import LevBuilder  # backward compat alias
from .book_lev import BookLevBuilder
from .debt_to_capital import DebtToCapitalBuilder
from .roa import ROABuilder
from .current_ratio import CurrentRatioBuilder
from .rd_intensity import RDIntensityBuilder
from .eps_growth import EPSGrowthBuilder

# H1 Compustat variable builders (one column each)
from .cash_holdings import CashHoldingsBuilder
from .tobins_q import TobinsQBuilder
from .capex_intensity import CapexIntensityBuilder
from .dividend_payer import DividendPayerBuilder
from .dividend_payer_quarterly import DividendPayerQuarterlyBuilder
from .ocf_volatility import OCFVolatilityBuilder
from .cash_flow_volatility import CashFlowVolatilityBuilder
from .hedging_needs import HedgingNeedsBuilder

# Quarterly Payout Ratio
from .payout_ratio_quarterly import PayoutRatioQuarterlyBuilder

# Extended control builders
from .cash_flow import CashFlowBuilder
from .sales_growth import SalesGrowthBuilder

# H9 Compustat variable builders (Expanded Robustness Block)
from .intangibility import IntangibilityBuilder
from .asset_growth import AssetGrowthBuilder

# H17 Compustat variable builder (Repurchase Intensity)
from .repurchase_intensity import RepurchaseIntensityBuilder

# H19/H20 Compustat variable builder (Leary & Roberts 2010 financing classification)
from .external_funding import ExternalFundingBuilder

# H19b/H20b Compustat variable builder (Chang, Dasgupta & Hilary 2006 financing classification)
from .chang_external_funding import ChangExternalFundingBuilder

# H16 Compustat variable builder (R&D Investment Intensity — Jiang et al. 2021)
from .rd_sales import RDSalesBuilder

# CRSP individual variable builders
from .stock_return import StockReturnBuilder
from .market_return import MarketReturnBuilder
from .volatility import VolatilityBuilder

# IBES variable builder
from .earnings_surprise import EarningsSurpriseBuilder

# Manifest fields (Stage 1)
from .manifest_fields import ManifestFieldsBuilder

# Takeover indicator builder (inputs/SDC/) — firm-level, not call-level
from .takeover_indicator import TakeoverIndicatorBuilder

__all__ = [
    # Base classes
    "VariableBuilder",
    "VariableResult",
    "VariableStats",
    "stats_to_dict",
    "stats_list_to_dataframe",
    # Textual variables (Stage 2)
    "ManagerQAUncertaintyBuilder",
    "ManagerPresUncertaintyBuilder",
    "AnalystQAUncertaintyBuilder",
    "NegativeSentimentBuilder",
    "EntireAllUncertaintyBuilder",
    "CEOQAUncertaintyBuilder",
    "CEOPresUncertaintyBuilder",
    "NonCEOManagerQAUncertaintyBuilder",
    "NonCEOManagerPresUncertaintyBuilder",
    # Tone/sentiment builders (Positive/Negative pct per speaker/context)
    "ManagerQAPositiveBuilder",
    "ManagerQANegativeBuilder",
    "ManagerPresPositiveBuilder",
    "ManagerPresNegativeBuilder",
    "CEOQAPositiveBuilder",
    "CEOQANegativeBuilder",
    "CEOPresPositiveBuilder",
    "CEOPresNegativeBuilder",
    "NonCEOManagerQAPositiveBuilder",
    "NonCEOManagerQANegativeBuilder",
    "AnalystQAPositiveBuilder",
    "AnalystQANegativeBuilder",
    # Compustat variable builders (one column each)
    "SizeBuilder",
    "BMBuilder",
    "LevBuilder",
    "BookLevBuilder",
    "DebtToCapitalBuilder",
    "ROABuilder",
    "CurrentRatioBuilder",
    "RDIntensityBuilder",
    "EPSGrowthBuilder",
    # H1 Compustat variable builders (cash holdings regression)
    "CashHoldingsBuilder",
    "TobinsQBuilder",
    "CapexIntensityBuilder",
    "DividendPayerBuilder",
    "DividendPayerQuarterlyBuilder",
    "OCFVolatilityBuilder",
    "CashFlowVolatilityBuilder",
    "HedgingNeedsBuilder",
    # Quarterly Payout Ratio
    "PayoutRatioQuarterlyBuilder",
    # Extended control builders
    "CashFlowBuilder",
    "SalesGrowthBuilder",
    # H9 Compustat variable builders (Expanded Robustness Block)
    "IntangibilityBuilder",
    "AssetGrowthBuilder",
    # H17 Compustat variable builder (Repurchase Intensity)
    "RepurchaseIntensityBuilder",
    # H19/H20 Compustat variable builder (Leary & Roberts 2010 financing classification)
    "ExternalFundingBuilder",
    # H19b/H20b Compustat variable builder (Chang, Dasgupta & Hilary 2006 financing classification)
    "ChangExternalFundingBuilder",
    # H19b/H20b Compustat variable builder (Chang, Dasgupta & Hilary 2006 financing classification)
    "ChangExternalFundingBuilder",
    # H16 Compustat variable builder (R&D Investment Intensity)
    "RDSalesBuilder",
    # Weak modal builders (H1 — Stage 2 linguistic)
    "ManagerQAWeakModalBuilder",
    "CEOQAWeakModalBuilder",
    "ManagerPresWeakModalBuilder",
    "CEOPresWeakModalBuilder",
    # CRSP variable builders (one column each)
    "StockReturnBuilder",
    "MarketReturnBuilder",
    "VolatilityBuilder",
    # IBES variable builder
    "EarningsSurpriseBuilder",
    # Manifest fields (Stage 1)
    "ManifestFieldsBuilder",
    # Takeover indicator builder (B.5 Takeover Hazards) — firm-level
    "TakeoverIndicatorBuilder",
    # H3 (kept for H11 — DivStability, PayoutFlexibility, FCFGrowth, IsDivPayer5yr archived)
    "EarningsVolatilityBuilder",
    "FirmMaturityBuilder",
    # H5 (Wang 2020)
    "LossDummyBuilder",
    "WangDispBuilder",
    # H7
    "AmihudIlliqBuilder",
    "AmihudChangeBuilder",
    # H7c/d/e BGT 25-day Amihud (Level/Delta/Avg)
    "BGTLongWindowAmihudBuilder",
    # H14
    "BidAskSpreadChangeBuilder",
    "StockPriceBuilder",
    "TurnoverBuilder",
    # H14c/d/e BGT 25-day closing-quote Spread (Level/Delta/Avg)
    "BGTLongWindowSpreadBuilder",
    # Clarity Residuals (from CEO Clarity Extended Stage 4)
    "CEOClarityResidualBuilder",
    "ManagerClarityResidualBuilder",
    # H11
    "PRiskQBuilder",
    # H11-Lag
    "PRiskQLagBuilder",
    # H11-Lag2
    "PRiskQLag2Builder",
    # H11-Lead
    "PRiskQLeadBuilder",
    # H11-Lead2
    "PRiskQLead2Builder",
    # H1.5 Trump 2016 DiD design
    "PRiskSubtopicsBuilder",
    "TrumpDiDTreatmentBuilder",
    # H1.6 Redistricting DiD design (ZCTA-CD baseline)
    "RedistrictingTreatmentBuilder",
    # H1.6 Redistricting DiD TEST 3 — Geocode + Lewis 2013 shapefile variant
    "RedistrictingTreatmentGeocodeBuilder",
    # H1.5 Brexit DiD design (Campello et al 2022 JFQA verbatim)
    "BrexitBetaUKBuilder",
    "Brexit10KTreatmentBuilder",
    "BrexitMacroControlsBuilder",
    "BrexitConsensusEPSBuilder",
    "HobergPhillipsFIC100Builder",
    "BrexitTobinsQBuilder",
    "BrexitSalesGrowthBuilder",
    "BrexitStockReturnBuilder",
    "BrexitCashFlowBuilder",
    "BrexitPSMMatchingBuilder",
    "run_parallel_trends_test",
    # H24/H24b/H25 Macro Uncertainty (EPU / GEPU / GPR)
    "MacroUncertaintyBuilder",
    # Panel-building utilities
    "assign_industry_sample",
    "attach_fyearq",
    # Winsorization utilities
    "winsorize_by_year",
    "winsorize_pooled",
]

# H3 Payout Policy (kept for H11; DivStability, PayoutFlexibility, FCFGrowth, IsDivPayer5yr archived)
from .earnings_volatility import EarningsVolatilityBuilder
from .firm_maturity import FirmMaturityBuilder

# H5 Analyst Dispersion (Wang 2020)
from .loss_dummy import LossDummyBuilder
from .wang_disp import WangDispBuilder

# H7 Illiquidity
from .amihud_illiq import AmihudIlliqBuilder
from .amihud_change import AmihudChangeBuilder

# H7c/d/e BGT (2018) 25-day post-call Amihud illiquidity (Level/Delta/Avg)
from .bgt_long_window_amihud import BGTLongWindowAmihudBuilder

# H14 Bid-Ask Spread Change
from .bidask_spread_change import BidAskSpreadChangeBuilder
from .stock_price import StockPriceBuilder
from .turnover import TurnoverBuilder

# H14c/d/e BGT (2018) window + Lee (2016) closing-quote spread (Level/Delta/Avg)
from .bgt_long_window_spread import BGTLongWindowSpreadBuilder

# Clarity Residuals (from CEO Clarity Extended Stage 4)
from .ceo_clarity_residual import CEOClarityResidualBuilder
from .manager_clarity_residual import ManagerClarityResidualBuilder

# H11 Political Risk (Quarterly)
from .prisk_q import PRiskQBuilder

# H11-Lag Political Risk (Quarterly, Lagged)
from .prisk_q_lag import PRiskQLagBuilder

# H11-Lag2 Political Risk (Quarterly, 2-quarter Lagged)
from .prisk_q_lag2 import PRiskQLag2Builder

# H11-Lead Political Risk (Quarterly, Lead)
from .prisk_q_lead import PRiskQLeadBuilder

# H11-Lead2 Political Risk (Quarterly, 2-quarter Lead)
from .prisk_q_lead2 import PRiskQLead2Builder

# H1.5 Trump 2016 DiD design — sub-topic PRisk loader + treatment-label builder
from .political_risk_subtopics import PRiskSubtopicsBuilder
from .trump_did_treatment import TrumpDiDTreatmentBuilder

# H1.6 Redistricting DiD design (Hasan 2022 Layer 2 replication)
from .redistricting_treatment import RedistrictingTreatmentBuilder

# H1.6 Redistricting DiD TEST 3 — Geocode + Lewis 2013 shapefile variant
# Replaces lossy ZCTA-CD crosswalk path with point-in-polygon spatial join.
from .redistricting_treatment_geocode import RedistrictingTreatmentGeocodeBuilder

# H1.5 Brexit DiD design (Campello et al 2022 JFQA verbatim) — modules #1-#12 + utility
from .brexit_treatment_beta_uk import BrexitBetaUKBuilder
from .brexit_treatment_10k import Brexit10KTreatmentBuilder
from .brexit_macro_controls import BrexitMacroControlsBuilder
from .brexit_consensus_eps import BrexitConsensusEPSBuilder
from .hoberg_phillips_fic100 import HobergPhillipsFIC100Builder
from .brexit_tobins_q import BrexitTobinsQBuilder
from .brexit_sales_growth import BrexitSalesGrowthBuilder
from .brexit_stock_return import BrexitStockReturnBuilder
from .brexit_cash_flow import BrexitCashFlowBuilder
from .brexit_psm_matching import BrexitPSMMatchingBuilder
from .brexit_parallel_trends import run_parallel_trends_test

# H24/H24b/H25 Macro Uncertainty — aggregate monthly macro indices matched by calendar month
# (Caldara-Iacoviello 2022 GPR, BBD 2016 US EPU, Davis 2016 GEPU)
from .macro_uncertainty import MacroUncertaintyBuilder

# Panel-building utilities (canonical shared helpers — all panel builders must import from here)
from .panel_utils import assign_industry_sample, attach_fyearq

# Winsorization utilities
from .winsorization import winsorize_by_year, winsorize_pooled
