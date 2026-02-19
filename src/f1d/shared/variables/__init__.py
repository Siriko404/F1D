"""Shared variable builders for F1D project.

This package provides standardized variable builders that load data from
various pipeline stages (Stage 1 manifest, Stage 2 text, Stage 3 financial)
and return consistent VariableResult objects.

Usage:
    from f1d.shared.variables import (
        ManagerQAUncertaintyBuilder,
        ManifestFieldsBuilder,
        load_variable_config,
    )

    config = load_variable_config()
    builder = ManagerQAUncertaintyBuilder(config["manager_qa_uncertainty"])
    result = builder.build(range(2002, 2019), root_path)
"""

from .base import (
    VariableBuilder,
    VariableResult,
    VariableStats,
    stats_to_dict,
    stats_list_to_dataframe,
)
from .manager_qa_uncertainty import ManagerQAUncertaintyBuilder
from .manager_pres_uncertainty import ManagerPresUncertaintyBuilder
from .analyst_qa_uncertainty import AnalystQAUncertaintyBuilder
from .negative_sentiment import NegativeSentimentBuilder
from .ceo_qa_uncertainty import CEOQAUncertaintyBuilder
from .ceo_pres_uncertainty import CEOPresUncertaintyBuilder
from .stock_return import StockReturnBuilder
from .market_return import MarketReturnBuilder
from .eps_growth import EPSGrowthBuilder
from .earnings_surprise import EarningsSurpriseBuilder
from .manifest_fields import ManifestFieldsBuilder

__all__ = [
    # Base classes
    "VariableBuilder",
    "VariableResult",
    "VariableStats",
    "stats_to_dict",
    "stats_list_to_dataframe",
    # Text variables (Stage 2)
    "ManagerQAUncertaintyBuilder",
    "ManagerPresUncertaintyBuilder",
    "AnalystQAUncertaintyBuilder",
    "NegativeSentimentBuilder",
    "CEOQAUncertaintyBuilder",
    "CEOPresUncertaintyBuilder",
    # Financial variables (Stage 3)
    "StockReturnBuilder",
    "MarketReturnBuilder",
    "EPSGrowthBuilder",
    "EarningsSurpriseBuilder",
    # Manifest fields (Stage 1)
    "ManifestFieldsBuilder",
]
