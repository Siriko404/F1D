#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Financial Utilities
================================================================================
ID: shared/financial_utils
Description: Provides common financial metrics and control variable
             calculations from Compustat data. Handles missing data gracefully
             with NaN values.

Inputs:
    - pandas DataFrame with firm identifiers (gvkey, datadate)
    - Compustat DataFrame with firm financial metrics
    - Fiscal year for data selection

Outputs:
    - Dictionary with firm-level control variables
    - DataFrame with computed financial features

Deterministic: true
================================================================================
"""

import pandas as pd
import numpy as np


def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> dict:
    """
    Calculate firm-level control variables from Compustat data.

    Args:
        row: DataFrame row with firm identifiers (gvkey, datadate)
        compustat_df: Compustat data with firm metrics
        year: Fiscal year for data selection

    Returns:
        Dictionary with: size (log assets), leverage, profitability,
        market_to_book, capex_intensity, r_intensity, dividend_payer
    """
    gvkey = row.get("gvkey")
    if gvkey is None:
        return {}

    # Get firm's data for the year
    firm_data = compustat_df[
        (compustat_df["gvkey"] == gvkey) & (compustat_df["fyear"] == year)
    ]

    if firm_data.empty:
        return {}

    data = firm_data.iloc[0]

    # Size: log total assets
    size = np.log(data["at"]) if data.get("at") and data["at"] > 0 else np.nan

    # Leverage: total debt / total assets
    leverage = (
        (data["dlc"] + data["dltt"]) / data["at"]
        if data.get("at") and data["at"] > 0
        else np.nan
    )

    # Profitability: operating income / total assets
    profitability = (
        data["oibdp"] / data["at"] if data.get("at") and data["at"] > 0 else np.nan
    )

    # Market-to-book: market cap / book equity
    market_to_book = (
        (data["prcc_f"] * data["csho"]) / data["ceq"]
        if data.get("ceq")
        and data["ceq"] > 0
        and data.get("prcc_f")
        and data.get("csho")
        else np.nan
    )

    # Capex intensity: capex / total assets
    capex_intensity = (
        data["capx"] / data["at"] if data.get("at") and data["at"] > 0 else np.nan
    )

    # R&D intensity: R&D / total assets
    r_intensity = (
        data["xrd"] / data["at"] if data.get("at") and data["at"] > 0 else np.nan
    )

    # Dividend payer: indicator
    dividend_payer = 1 if data.get("dvc") and data["dvc"] > 0 else 0

    return {
        "size": size,
        "leverage": leverage,
        "profitability": profitability,
        "market_to_book": market_to_book,
        "capex_intensity": capex_intensity,
        "r_intensity": r_intensity,
        "dividend_payer": dividend_payer,
    }


def compute_financial_features(
    df: pd.DataFrame, compustat_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Compute financial features for all firms in dataset.

    Args:
        df: DataFrame with firm identifiers
        compustat_df: Compustat data with firm metrics

    Returns:
        DataFrame with added financial control variables
    """
    features = []

    for _, row in df.iterrows():
        year = row.get("year")
        if year is None:
            continue

        controls = calculate_firm_controls(row, compustat_df, year)
        if controls:
            row_copy = row.copy()
            row_copy.update(controls)
            features.append(row_copy)

    return pd.DataFrame(features)
