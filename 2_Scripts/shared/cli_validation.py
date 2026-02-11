#!/usr/bin/env python3
"""
==============================================================================
SHARED MODULE: CLI Validation for Econometric Scripts
==============================================================================
ID: shared/cli_validation
Description: Provides argparse parsing and prerequisite validation functions for
             Step 4 econometric analysis scripts.

Inputs:
    None - This module provides functions for CLI validation

Outputs:
    - parse_arguments() - Returns parsed args from argparse
    - check_prerequisites_step4_clarity() - Validates 2.2, 3.1, 3.2 outputs
    - check_prerequisites_step4_liquidity() - Validates 4.1, 3.2 outputs
    - check_prerequisites_step4_takeover() - Validates 4.1, 3.3 outputs

Deterministic: true
Dependencies:
    - Utility module for CLI argument validation
    - Uses: argparse, sys

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse


def parse_arguments_4_1_step4_clarity():
    """Parse arguments for Step 4.1 CEO Clarity scripts."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.1: Estimate CEO Clarity

Estimates CEO clarity scores using panel regression with CEO
fixed effects. Regresses readability measures on CEO and firm
characteristics, extracting CEO-specific clarity coefficients.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--model",
        type=str,
        choices=["baseline", "extended", "regime"],
        default="baseline",
        help="Clarity model specification (default: baseline)",
    )

    return parser.parse_args()


def check_prerequisites_step4_clarity(root):
    """Validate prerequisites for Step 4.1 CEO Clarity scripts.

    Required steps:
        - 2.2_ConstructVariables: linguistic_variables.parquet
        - 3.1_FirmControls: firm_controls.parquet
        - 3.2_MarketVariables: market_variables.parquet
    """
    from shared.dependency_checker import validate_prerequisites

    required_files = {}
    required_steps = {
        "2.2_ConstructVariables": "linguistic_variables.parquet",
        "3.1_FirmControls": "firm_controls.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def parse_arguments_4_2_liquidity():
    """Parse arguments for Step 4.2 Liquidity Regressions."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.2: Liquidity Regressions

Test whether CEO/Manager communication affects market liquidity
around earnings calls. Uses CCCL shift intensity as instrument.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--specification",
        type=str,
        help="Regression specification (default: from config)",
    )

    return parser.parse_args()


def check_prerequisites_step4_liquidity(root):
    """Validate prerequisites for Step 4.2 Liquidity Regressions.

    Required steps:
        - 4.1_EstimateCeoClarity: ceo_clarity_scores.parquet
        - 3.2_MarketVariables: market_variables.parquet
    """
    from shared.dependency_checker import validate_prerequisites

    required_files = {}
    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


def parse_arguments_4_3_takeover():
    """Parse arguments for Step 4.3 Takeover Hazards."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.3: Takeover Hazards

Analyzes how CEO Clarity and Q&A Uncertainty predict takeover
probability using survival analysis.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites_step4_takeover(root):
    """Validate prerequisites for Step 4.3 Takeover Hazards.

    Required steps:
        - 4.1_EstimateCeoClarity: ceo_clarity_scores.parquet
        - 3.3_EventFlags: event_flags.parquet
    """
    from shared.dependency_checker import validate_prerequisites

    required_files = {}
    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.3_EventFlags": "event_flags.parquet",
    }

    validate_prerequisites(required_files, required_steps)
