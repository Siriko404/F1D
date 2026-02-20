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

    Individual CRSP variable builders (one column each):
        StockReturnBuilder    → StockRet (compound return over call window)
        MarketReturnBuilder   → MarketRet (compound VWRETD over call window)
        VolatilityBuilder     → Volatility (annualized std over call window)

    IBES variable builder:
        EarningsSurpriseBuilder → SurpDec (earnings surprise decile -5..+5)

    Textual variable builders (read Stage 2 outputs):
        ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder,
        AnalystQAUncertaintyBuilder, NegativeSentimentBuilder,
        CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder

Usage:
    from f1d.shared.variables import (
        EPSGrowthBuilder,
        StockReturnBuilder,
        MarketReturnBuilder,
        VolatilityBuilder,
        EarningsSurpriseBuilder,
        ManagerQAUncertaintyBuilder,
        ManifestFieldsBuilder,
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
from .ceo_qa_uncertainty import CEOQAUncertaintyBuilder
from .ceo_pres_uncertainty import CEOPresUncertaintyBuilder

# Compustat individual variable builders
from .size import SizeBuilder
from .bm import BMBuilder
from .lev import LevBuilder
from .roa import ROABuilder
from .current_ratio import CurrentRatioBuilder
from .rd_intensity import RDIntensityBuilder
from .eps_growth import EPSGrowthBuilder

# CRSP individual variable builders
from .stock_return import StockReturnBuilder
from .market_return import MarketReturnBuilder
from .volatility import VolatilityBuilder

# IBES variable builder
from .earnings_surprise import EarningsSurpriseBuilder

# Manifest fields (Stage 1)
from .manifest_fields import ManifestFieldsBuilder

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
    "CEOQAUncertaintyBuilder",
    "CEOPresUncertaintyBuilder",
    # Compustat variable builders (one column each)
    "SizeBuilder",
    "BMBuilder",
    "LevBuilder",
    "ROABuilder",
    "CurrentRatioBuilder",
    "RDIntensityBuilder",
    "EPSGrowthBuilder",
    # CRSP variable builders (one column each)
    "StockReturnBuilder",
    "MarketReturnBuilder",
    "VolatilityBuilder",
    # IBES variable builder
    "EarningsSurpriseBuilder",
    # Manifest fields (Stage 1)
    "ManifestFieldsBuilder",
]
