"""Shared variable builders for F1D project.

This package provides standardized variable builders that load data from
various pipeline stages (Stage 1 manifest, Stage 2 text, raw financial inputs)
and return consistent VariableResult objects.

Financial variable builders compute directly from raw inputs:
  - CompustatControlsBuilder  → raw Compustat (Size, BM, Lev, ROA, CurrentRatio,
                                  RD_Intensity, EPS_Growth)
  - CRSPReturnsBuilder        → raw CRSP daily (StockRet, MarketRet, Volatility)
  - EarningsSurpriseBuilder   → raw IBES + CCM (SurpDec)

Single-column wrappers delegate to the above for callers that need one variable:
  - EPSGrowthBuilder          → delegates to CompustatControlsBuilder
  - StockReturnBuilder        → delegates to CRSPReturnsBuilder
  - MarketReturnBuilder       → delegates to CRSPReturnsBuilder

Textual variable builders read from Stage 2 outputs (linguistic_variables_{year}.parquet):
  - ManagerQAUncertaintyBuilder, ManagerPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder, NegativeSentimentBuilder,
    CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder

Usage:
    from f1d.shared.variables import (
        CompustatControlsBuilder,
        CRSPReturnsBuilder,
        EarningsSurpriseBuilder,
        ManagerQAUncertaintyBuilder,
        ManifestFieldsBuilder,
    )
    builder = CompustatControlsBuilder({})
    result = builder.build(range(2002, 2019), root_path)
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

# Financial variables — compute from raw inputs
from .compustat_controls import CompustatControlsBuilder, COMPUSTAT_COLS
from .crsp_returns import CRSPReturnsBuilder, CRSP_RETURN_COLS
from .earnings_surprise import EarningsSurpriseBuilder

# Single-column wrappers (delegate to above)
from .eps_growth import EPSGrowthBuilder
from .stock_return import StockReturnBuilder
from .market_return import MarketReturnBuilder

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
    # Financial variables — raw compute engines
    "CompustatControlsBuilder",
    "COMPUSTAT_COLS",
    "CRSPReturnsBuilder",
    "CRSP_RETURN_COLS",
    "EarningsSurpriseBuilder",
    # Single-column wrappers
    "EPSGrowthBuilder",
    "StockReturnBuilder",
    "MarketReturnBuilder",
    # Manifest fields (Stage 1)
    "ManifestFieldsBuilder",
]
