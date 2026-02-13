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
Main Functions:
    -  Various financial calculation utilities

Dependencies:
    - Utility module for financial calculations
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

from typing import Dict, Union

import numpy as np
import pandas as pd

from f1d.shared.data_validation import FinancialCalculationError


def calculate_firm_controls(
    row: pd.Series, compustat_df: pd.DataFrame, year: int
) -> Dict[str, Union[float, int, None]]:
    """
    Calculate firm-level control variables from Compustat data.

    Args:
        row: DataFrame row with firm identifiers (gvkey, datadate)
        compustat_df: Compustat data with firm metrics
        year: Fiscal year for data selection

    Returns:
        Dictionary with: size (log assets), leverage, profitability,
        market_to_book, capex_intensity, r_intensity, dividend_payer

    Raises:
        FinancialCalculationError: If gvkey is missing or Compustat data not found for year
    """
    gvkey = row.get("gvkey")
    if gvkey is None:
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: missing gvkey in row. "
            f"Row columns: {list(row.index)}. "
            f"Year: {year}"
        )

    # Get firm's data for the year
    firm_data = compustat_df[
        (compustat_df["gvkey"] == gvkey) & (compustat_df["fyear"] == year)
    ]

    if firm_data.empty:
        available_years = (
            compustat_df[compustat_df["gvkey"] == str(gvkey).zfill(6)]["fyear"].unique()
            if "gvkey" in compustat_df.columns
            else []
        )
        raise FinancialCalculationError(
            f"Cannot calculate firm controls: no Compustat data found. "
            f"gvkey={gvkey}, year={year}. "
            f"Available years for this gvkey: {list(available_years)}. "
            f"Total Compustat records: {len(compustat_df)}"
        )

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

    Note:
        calculate_firm_controls() may raise FinancialCalculationError if
        gvkey is missing or Compustat data not found. The "if controls:"
        check in this function provides defensive programming, but callers
        should be aware that exceptions may be raised from the underlying function.
    """
    features = []

    for _, row in df.iterrows():
        year = row.get("year")
        if year is None:
            continue

        controls = calculate_firm_controls(row, compustat_df, year)
        if controls:
            # Create a dict from the row and update with controls
            row_dict = row.to_dict()
            row_dict.update(controls)
            features.append(row_dict)

    return pd.DataFrame(features)


def calculate_firm_controls_quarterly(
    row: pd.Series, compustat_df: pd.DataFrame, datadate: pd.Timestamp
) -> Dict[str, float]:
    """
    Calculate firm-level control variables from quarterly Compustat data.

    Uses quarterly Compustat variables (atq, ceqq, ltq, niq, etc.) instead of annual.
    Matches on gvkey and datadate.

    Args:
        row: DataFrame row with firm identifiers (gvkey, datadate)
        compustat_df: Quarterly Compustat data with firm metrics
        datadate: Date for data selection (typically call's start_date)

    Returns:
        Dictionary with: Size, BM, Lev, ROA, CurrentRatio, RD_Intensity

    Raises:
        FinancialCalculationError: If gvkey is missing or no data found before datadate
    """
    gvkey = row.get("gvkey")
    if gvkey is None:
        raise FinancialCalculationError(
            f"Cannot calculate quarterly firm controls: missing gvkey in row. "
            f"Row columns: {list(row.index)}. "
            f"Datadate: {datadate}"
        )

    # Get firm's data closest to or before the specified date
    # Using merge_asof logic would be more efficient, but this is row-wise
    compustat_df["datadate"] = pd.to_datetime(compustat_df["datadate"])
    firm_data = compustat_df[
        (compustat_df["gvkey"] == gvkey) & (compustat_df["datadate"] <= datadate)
    ].sort_values("datadate", ascending=False)

    if firm_data.empty:
        raise FinancialCalculationError(
            f"Cannot calculate quarterly firm controls: no Compustat data found. "
            f"gvkey={gvkey}, datadate={datadate}. "
            f"This may indicate CCM link table issue or data gap."
        )

    data = firm_data.iloc[0]

    # Size: log total assets (quarterly)
    size = np.log(data["atq"]) if data.get("atq") and data["atq"] > 0 else np.nan

    # Book-to-Market: book equity / market cap
    # BM: ceqq / (cshoq * prccq)
    bm = (
        data["ceqq"] / (data["cshoq"] * data["prccq"])
        if data.get("ceqq")
        and data["ceqq"] > 0
        and data.get("cshoq")
        and data.get("cshoq") > 0
        and data.get("prccq")
        and data["prccq"] > 0
        else np.nan
    )

    # Leverage: total liabilities / total assets (quarterly)
    # Lev: ltq / atq
    leverage = (
        data["ltq"] / data["atq"] if data.get("atq") and data["atq"] > 0 else np.nan
    )

    # Return on Assets: net income / total assets (quarterly)
    # ROA: niq / atq
    roa = data["niq"] / data["atq"] if data.get("atq") and data["atq"] > 0 else np.nan

    # Current Ratio: current assets / current liabilities
    # CurrentRatio: actq / lctq
    current_ratio = (
        data["actq"] / data["lctq"] if data.get("lctq") and data["lctq"] > 0 else np.nan
    )

    # R&D Intensity: R&D / total assets (quarterly, treat missing as 0)
    # RD_Intensity: xrdq / atq
    xrdq_val = data.get("xrdq")
    rd_intensity = (
        (xrdq_val if pd.notna(xrdq_val) else 0) / data["atq"]
        if data.get("atq") and data["atq"] > 0
        else np.nan
    )

    return {
        "Size": size,
        "BM": bm,
        "Lev": leverage,
        "ROA": roa,
        "CurrentRatio": current_ratio,
        "RD_Intensity": rd_intensity,
    }


def compute_financial_controls_quarterly(
    compustat_df: pd.DataFrame,
    winsorize: bool = True,
) -> pd.DataFrame:
    """
    Compute quarterly financial controls for all firms in Compustat DataFrame.

    Vectorized calculation using quarterly Compustat variables. Matches the pattern
    from 3.1_FirmControls.py for consistency with existing outputs.

    Args:
        compustat_df: Quarterly Compustat data with required columns
        winsorize: If True, winsorize at 1% and 99% (default: True)

    Returns:
        DataFrame with added control variables (Size, BM, Lev, ROA,
        EPS_Growth, CurrentRatio, RD_Intensity)

    Note:
        Requires columns: gvkey, datadate, atq, ceqq, cshoq, prccq, ltq, niq,
                         epspxq, actq, lctq, xrdq
    """
    # Ensure datadate is datetime
    compustat_df["datadate"] = pd.to_datetime(compustat_df["datadate"])

    # Sort by gvkey and datadate for lag calculations
    compustat_df = compustat_df.sort_values(["gvkey", "datadate"]).reset_index(
        drop=True
    )

    # Compute lagged EPS (4 quarters back for YoY)
    compustat_df["epspxq_lag4"] = compustat_df.groupby("gvkey")["epspxq"].shift(4)

    # Compute control variables
    # Size: ln(atq)
    compustat_df["Size"] = np.log(compustat_df["atq"].clip(lower=0.01))

    # Book-to-Market: ceqq / (cshoq * prccq)
    compustat_df["BM"] = compustat_df["ceqq"] / (
        compustat_df["cshoq"] * compustat_df["prccq"]
    )

    # Leverage: ltq / atq
    compustat_df["Lev"] = compustat_df["ltq"] / compustat_df["atq"]

    # ROA: niq / atq
    compustat_df["ROA"] = compustat_df["niq"] / compustat_df["atq"]

    # Current Ratio: actq / lctq
    compustat_df["CurrentRatio"] = compustat_df["actq"] / compustat_df["lctq"].replace(
        0, np.nan
    )

    # R&D Intensity: xrdq / atq (treat missing R&D as 0)
    compustat_df["RD_Intensity"] = compustat_df["xrdq"].fillna(0) / compustat_df["atq"]

    # EPS Growth: (EPS - EPS_lag4) / |EPS_lag4|
    mask = compustat_df["epspxq_lag4"].notna() & (compustat_df["epspxq_lag4"] != 0)
    compustat_df["EPS_Growth"] = np.nan
    compustat_df.loc[mask, "EPS_Growth"] = (
        compustat_df.loc[mask, "epspxq"] - compustat_df.loc[mask, "epspxq_lag4"]
    ) / compustat_df.loc[mask, "epspxq_lag4"].abs()

    # Winsorize extreme values if requested
    if winsorize:
        for col in [
            "Size",
            "BM",
            "Lev",
            "ROA",
            "EPS_Growth",
            "CurrentRatio",
            "RD_Intensity",
        ]:
            if compustat_df[col].notna().sum() > 0:
                p1, p99 = compustat_df[col].quantile([0.01, 0.99])
                compustat_df[col] = compustat_df[col].clip(lower=p1, upper=p99)

    return compustat_df
