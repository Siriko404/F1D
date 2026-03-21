#!/usr/bin/env python3
"""
================================================================================
SHARED MODULE: Output Schema Validation
================================================================================
ID: shared/output_schemas
Description: Pandera schema definitions for validating script outputs.

Purpose: Provides schema validation for all Parquet/JSON outputs to ensure
         data quality and catch errors early in the pipeline.

Main Schemas:
    - LinguisticVariablesSchema: Validates linguistic_variables_*.parquet
    - FirmControlsSchema: Validates firm_controls_*.parquet
    - EventFlagsSchema: Validates event_flags_*.parquet
    - ManagerClaritySchema: Validates manager_clarity_scores.parquet
    - InvestmentResidualSchema: Validates H2_InvestmentResiduals.parquet
    - PRiskUncertaintySchema: Validates H2_PRiskUncertainty_Analysis.parquet

Usage:
    from f1d.shared.output_schemas import validate_linguistic_variables

    df = pd.read_parquet("output.parquet")
    validated_df = validate_linguistic_variables(df)

Dependencies:
    - pandera>=0.20.0

Author: Thesis Author
Date: 2026-02-15
================================================================================
"""

import logging
from typing import Any, Dict, List, Optional

import pandas as pd

# Pandera is optional - gracefully handle if not installed
try:
    import pandera as pa
    from pandera import Column, DataFrameSchema, Check
    from pandera.errors import SchemaError

    PANDERA_AVAILABLE = True
except ImportError:
    PANDERA_AVAILABLE = False
    DataFrameSchema = object  # type: ignore[misc,assignment]
    SchemaError = Exception  # type: ignore[misc,assignment]
    logging.warning(
        "Pandera not installed. Schema validation will be skipped. "
        "Install with: pip install pandera>=0.20.0"
    )

logger = logging.getLogger(__name__)


# ==============================================================================
# Schema Definitions
# ==============================================================================

if PANDERA_AVAILABLE:
    # Schema for linguistic_variables_*.parquet (Step 2.2)
    LinguisticVariablesSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "file_name": Column(str, nullable=False, unique=True),
            "start_date": Column(pa.DateTime, nullable=True),
            "gvkey": Column(str, nullable=True),
            "conm": Column(str, nullable=True),
            "sic": Column(str, nullable=True),
            # Linguistic variables (nullable - NaN means "no text in section")
            # These are pct columns, should be 0-100 range
            "Manager_QA_Uncertainty_pct": Column(
                float, nullable=True, checks=Check.ge(0.0)
            ),
        },
        strict=False,  # Allow additional columns
        coerce=True,
    )

    # Schema for firm_controls_*.parquet (Step 3.1)
    FirmControlsSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "file_name": Column(str, nullable=False),
            "gvkey": Column(str, nullable=True),
            "StockRet": Column(float, nullable=True),
            "MarketRet": Column(float, nullable=True),
            "EPS_Growth": Column(float, nullable=True),
            "SurpDec": Column(float, nullable=True),
            "Size": Column(float, nullable=True, checks=Check.gt(0.0)),
            "BM": Column(float, nullable=True, checks=Check.gt(0.0)),
            "BookLev": Column(float, nullable=True, checks=Check.ge(0.0)),
            "ROA": Column(float, nullable=True),
        },
        strict=False,
        coerce=True,
    )

    # Schema for event_flags_*.parquet (Step 3.3)
    EventFlagsSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "file_name": Column(str, nullable=False),
            "Takeover": Column(int, nullable=True, checks=Check.isin([0, 1])),
            "Duration": Column(float, nullable=True, checks=Check.ge(0.0)),
        },
        strict=False,
        coerce=True,
    )

    # Schema for manager_clarity_scores.parquet (Step 4.1)
    ManagerClaritySchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "ceo_id": Column(str, nullable=False),
            "ClarityManager": Column(float, nullable=True),
            "sample": Column(str, nullable=True),
        },
        strict=False,
        coerce=True,
    )

    # Schema for H2_InvestmentResiduals.parquet (Step 3.9)
    InvestmentResidualSchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "gvkey": Column(str, nullable=False),
            "year": Column(int, nullable=False),
            "InvestmentResidual": Column(float, nullable=True),
            "TobinQ_lag": Column(float, nullable=True),
            "SalesGrowth_lag": Column(float, nullable=True),
            "CashFlow": Column(float, nullable=True),
            "Size": Column(float, nullable=True),
            "Leverage": Column(float, nullable=True),
            "TobinQ": Column(float, nullable=True),
            "SalesGrowth": Column(float, nullable=True),
            "ff48_code": Column(int, nullable=True),
        },
        strict=False,
        coerce=True,
    )

    # Schema for H2_PRiskUncertainty_Analysis.parquet (Step 3.10)
    PRiskUncertaintySchema = DataFrameSchema(  # type: ignore[no-untyped-call]
        {
            "gvkey": Column(str, nullable=False),
            "year": Column(int, nullable=False),
            "InvestmentResidual": Column(float, nullable=True),
            "PRisk_x_Uncertainty": Column(float, nullable=True),
            "PRisk_std": Column(float, nullable=True),
            "Manager_QA_Uncertainty_pct_std": Column(float, nullable=True),
            "CashFlow": Column(float, nullable=True),
            "Size": Column(float, nullable=True),
            "Leverage": Column(float, nullable=True),
            "TobinQ": Column(float, nullable=True),
            "SalesGrowth": Column(float, nullable=True),
        },
        strict=False,
        coerce=True,
    )

else:
    # Placeholder schemas when pandera is not available
    LinguisticVariablesSchema = None  # type: ignore[assignment]
    FirmControlsSchema = None  # type: ignore[assignment]
    EventFlagsSchema = None  # type: ignore[assignment]
    ManagerClaritySchema = None  # type: ignore[assignment]
    InvestmentResidualSchema = None  # type: ignore[assignment]
    PRiskUncertaintySchema = None  # type: ignore[assignment]


# ==============================================================================
# Validation Functions
# ==============================================================================


def _validate_with_schema(
    df: pd.DataFrame,
    schema: Optional[DataFrameSchema],
    schema_name: str,
    warn_only: bool = True,
) -> pd.DataFrame:
    """
    Internal helper to validate a DataFrame against a schema.

    Args:
        df: DataFrame to validate
        schema: Pandera schema to validate against
        schema_name: Name of schema for logging
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame (or original if validation skipped/failed)

    Raises:
        SchemaError: If validation fails and warn_only=False
    """
    if not PANDERA_AVAILABLE:
        logger.debug(
            f"Skipping {schema_name} validation: pandera not installed"
        )
        return df

    if schema is None:
        logger.warning(f"Schema {schema_name} is not defined")
        return df

    try:
        validated_df = schema.validate(df, lazy=True)
        logger.info(f"{schema_name} validation passed: {len(df):,} rows")
        return validated_df
    except SchemaError as e:
        msg = f"{schema_name} validation failed: {e.failure_cases}"
        if warn_only:
            logger.warning(msg)
            return df
        else:
            logger.error(msg)
            raise


def validate_linguistic_variables(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate linguistic variables DataFrame.

    Args:
        df: DataFrame with linguistic variables
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, LinguisticVariablesSchema, "LinguisticVariablesSchema", warn_only
    )


def validate_firm_controls(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate firm controls DataFrame.

    Args:
        df: DataFrame with firm controls
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, FirmControlsSchema, "FirmControlsSchema", warn_only
    )


def validate_event_flags(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate event flags DataFrame.

    Args:
        df: DataFrame with event flags
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, EventFlagsSchema, "EventFlagsSchema", warn_only
    )


def validate_manager_clarity(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate manager clarity DataFrame.

    Args:
        df: DataFrame with manager clarity scores
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, ManagerClaritySchema, "ManagerClaritySchema", warn_only
    )


def validate_investment_residual(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate investment residuals DataFrame.

    Args:
        df: DataFrame with investment residuals
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, InvestmentResidualSchema, "InvestmentResidualSchema", warn_only
    )


def validate_prisk_uncertainty(
    df: pd.DataFrame, warn_only: bool = True
) -> pd.DataFrame:
    """
    Validate PRisk x Uncertainty DataFrame.

    Args:
        df: DataFrame with PRisk x Uncertainty analysis
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Validated DataFrame
    """
    return _validate_with_schema(
        df, PRiskUncertaintySchema, "PRiskUncertaintySchema", warn_only
    )


# ==============================================================================
# Generic Validation Helper
# ==============================================================================


def validate_output(
    df: pd.DataFrame,
    schema_name: str,
    required_columns: Optional[List[str]] = None,
    warn_only: bool = True,
) -> Dict[str, Any]:
    """
    Generic output validation with basic checks.

    Performs basic validation when schema validation is not available:
    - Checks required columns exist
    - Checks for empty DataFrame
    - Reports row/column counts

    Args:
        df: DataFrame to validate
        schema_name: Name of the output type for logging
        required_columns: List of required column names
        warn_only: If True, log warning on failure; if False, raise exception

    Returns:
        Dict with validation results
    """
    results: Dict[str, Any] = {
        "schema_name": schema_name,
        "valid": True,
        "n_rows": len(df),
        "n_cols": len(df.columns),
        "errors": [],
    }

    # Check for empty DataFrame
    if len(df) == 0:
        results["valid"] = False
        results["errors"].append("DataFrame is empty")

    # Check required columns
    if required_columns:
        missing = [c for c in required_columns if c not in df.columns]
        if missing:
            results["valid"] = False
            results["errors"].append(f"Missing columns: {missing}")

    # Log results
    if results["valid"]:
        logger.info(
            f"{schema_name} validation passed: {results['n_rows']:,} rows, "
            f"{results['n_cols']} columns"
        )
    else:
        msg = f"{schema_name} validation failed: {results['errors']}"
        if warn_only:
            logger.warning(msg)
        else:
            logger.error(msg)
            raise ValueError(msg)

    return results
