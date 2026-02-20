"""Shared variable builders for F1D project.

Each shared module builds exactly ONE variable and returns a VariableResult
with file_name + that variable's column. Stage 3 panel builders import
the individual builders they need and merge the results.

Architecture:
    Private compute engines (not VariableBuilders):
        _compustat_engine.CompustatEngine  — loads Compustat once, caches result
        _crsp_engine.CRSPEngine            — loads CRSP yearly, caches result

    Individual Compustat variable builders (one column each):
        SizeBuilder           → Size = ln(atq)
        BMBuilder             → BM = ceqq / (cshoq * prccq)
        LevBuilder            → Lev = ltq / atq
        ROABuilder            → ROA = niq / atq
        CurrentRatioBuilder   → CurrentRatio = actq / lctq
        RDIntensityBuilder    → RD_Intensity = xrdq / atq
        EPSGrowthBuilder      → EPS_Growth (date-based YoY, robust to gaps)
        CashHoldingsBuilder   → CashHoldings = cheq / atq
        TobinsQBuilder        → TobinsQ = (mkvaltq + ltq) / atq
        CapexIntensityBuilder → CapexAt = capxq / atq
        DividendPayerBuilder  → DividendPayer = (dvpq > 0).astype(float)
        OCFVolatilityBuilder  → OCF_Volatility = rolling 4yr std of oancfy/atq

    Individual CRSP variable builders (one column each):
        StockReturnBuilder    → StockRet (compound return over call window)
        MarketReturnBuilder   → MarketRet (compound VWRETD over call window)
        VolatilityBuilder     → Volatility (annualized std over call window)

    IBES variable builder:
        EarningsSurpriseBuilder → SurpDec (earnings surprise decile -5..+5)

    CCCL instrument builder (reads inputs/CCCL_instrument/):
        CCCLInstrumentBuilder → shift_intensity_sale_ff48

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
from .lev import LevBuilder
from .roa import ROABuilder
from .current_ratio import CurrentRatioBuilder
from .rd_intensity import RDIntensityBuilder
from .eps_growth import EPSGrowthBuilder

# H1 Compustat variable builders (one column each)
from .cash_holdings import CashHoldingsBuilder
from .tobins_q import TobinsQBuilder
from .capex_intensity import CapexIntensityBuilder
from .dividend_payer import DividendPayerBuilder
from .ocf_volatility import OCFVolatilityBuilder

# CRSP individual variable builders
from .stock_return import StockReturnBuilder
from .market_return import MarketReturnBuilder
from .volatility import VolatilityBuilder

# IBES variable builder
from .earnings_surprise import EarningsSurpriseBuilder

# Manifest fields (Stage 1)
from .manifest_fields import ManifestFieldsBuilder

# CCCL instrument builder (inputs/CCCL_instrument/)
from .cccl_instrument import CCCLInstrumentBuilder

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
    "ROABuilder",
    "CurrentRatioBuilder",
    "RDIntensityBuilder",
    "EPSGrowthBuilder",
    # H1 Compustat variable builders (cash holdings regression)
    "CashHoldingsBuilder",
    "TobinsQBuilder",
    "CapexIntensityBuilder",
    "DividendPayerBuilder",
    "OCFVolatilityBuilder",
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
    # CCCL instrument builder (B.4 Liquidity)
    "CCCLInstrumentBuilder",
    # Takeover indicator builder (B.5 Takeover Hazards) — firm-level
    "TakeoverIndicatorBuilder",
]
