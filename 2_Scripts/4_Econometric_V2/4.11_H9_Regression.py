#!/usr/bin/env python3
"""
================================================================================
STEP 4.11: H9 Final Merge and Regression
================================================================================
ID: 4.11_H9_Regression
Description: Merges all H9 components (StyleFrozen, PRiskFY, AbsAbInv) into
             FINAL_PANEL and runs the H9 regression testing whether CEO style
             moderates the effect of policy risk on abnormal investment.

Purpose: Complete H9 data assembly and test the core hypothesis using OLS panel
         regression with firm and year fixed effects.

H9 Hypothesis: The effect of Hassan PRisk on abnormal investment is MODERATED
               by CEO communication clarity (interaction effect).

Model Specification:
    AbsAbInv_{i,t+1} = beta0 + beta1*PRiskFY_t + beta2*StyleFrozen_t
                      + beta3*(PRiskFY_t x StyleFrozen_t)
                      + gamma'*Controls_t
                      + FirmFE_i + YearFE_t + epsilon

Key Coefficient: beta3 (interaction term)
    - beta3 > 0: Vaguer CEOs show STRONGER PRisk -> abnormal investment
    - beta3 < 0: Vaguer CEOs show WEAKER PRisk -> abnormal investment
    - beta3 ≈ 0: CEO style does NOT moderate (meaningful null possible)

Inputs:
    - 4_Outputs/3_Financial_V2/3.11_H9_StyleFrozen/latest/style_frozen.parquet (CEO style)
    - 4_Outputs/3_Financial_V2/3.12_H9_PRiskFY/latest/priskfy.parquet (fiscal-year PRisk)
    - 4_Outputs/3_Financial_V2/3.13_H9_AbnormalInvestment/latest/abnormal_investment.parquet (DV + controls)

Outputs:
    - 4_Outputs/4_Econometric_V2/4.11_H9_Regression/{timestamp}/final_panel.parquet
    - 4_Outputs/4_Econometric_V2/4.11_H9_Regression/{timestamp}/h9_regression_results.csv
    - 4_Outputs/4_Econometric_V2/4.11_H9_Regression/{timestamp}/h9_regression_output.txt
    - 4_Outputs/4_Econometric_V2/4.11_H9_Regression/{timestamp}/report_step411_04.md
    - 4_Outputs/4_Econometric_V2/4.11_H9_Regression/{timestamp}/sanity_checks.txt

Declared Outputs:
    - final_panel: Merged dataset with all variables
    - regression_results: Coefficients, t-stats, p-values
    - sanity_checks: Mandatory verification of data quality

Deterministic: true
Dependencies:
    - Requires: Step 3.11, 3.12, 3.13
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
================================================================================
"""

import argparse
import gc
import io
import sys
import time
from datetime import datetime
from pathlib import Path

import pandas as pd

# Ensure UTF-8 output for Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
# Suppress warnings for cleaner output
import warnings

from shared.observability_utils import (
    get_process_memory_mb,
    save_stats,
)

# Import regression utilities
from shared.panel_ols import run_panel_ols
from shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
)

warnings.filterwarnings("ignore")

# ==============================================================================
# Configuration
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    paths = {
        "root": root,
        "style_frozen_base": root / "4_Outputs" / "3_Financial_V2" / "3.11_H9_StyleFrozen",
        "priskfy_base": root / "4_Outputs" / "3_Financial_V2" / "3.12_H9_PRiskFY",
        "abnormal_inv_base": root / "4_Outputs" / "3_Financial_V2" / "3.13_H9_AbnormalInvestment",
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2" / "4.11_H9_Regression"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2" / "4.11_H9_Regression"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_finalmerge.log"

    return paths


# ==============================================================================
# Data Loading Functions
# ==============================================================================


def load_style_frozen(style_frozen_base):
    """
    Load StyleFrozen (CEO style) dataset.

    Args:
        style_frozen_base: Base path to 3.11_H9_StyleFrozen output

    Returns:
        DataFrame with gvkey, fyear, style_frozen, ceo_id, etc.
    """
    print("\n" + "=" * 80)
    print("LOADING STYLEFROZEN (CEO VAGUENESS STYLE)")
    print("=" * 80)

    try:
        style_dir = get_latest_output_dir(
            style_frozen_base, required_file="style_frozen.parquet"
        )
        print(f"[OK] Found StyleFrozen directory: {style_dir.name}")

        file_path = style_dir / "style_frozen.parquet"
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded StyleFrozen: {len(df):,} firm-years")

        # Verify required columns
        required_cols = ["gvkey", "fyear", "style_frozen"]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in StyleFrozen: {missing_cols}")

        # Ensure gvkey is string and zero-padded
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

        # Ensure fyear is integer
        df["fyear"] = pd.to_numeric(df["fyear"], errors="coerce").astype("int64")

        print(f"  - GVKEY format: {df['gvkey'].iloc[0]} (zero-padded to 6 chars)")
        print(f"  - FYEAR dtype: {df['fyear'].dtype}")
        print(f"  - Unique firms: {df['gvkey'].nunique():,}")
        print(f"  - FYEAR range: {df['fyear'].min()}-{df['fyear'].max()}")
        print(f"  - StyleFrozen mean: {df['style_frozen'].mean():.4f} (should be ~0)")
        print(f"  - StyleFrozen std: {df['style_frozen'].std():.4f} (should be ~1)")

        return df

    except Exception as e:
        print(f"[ERROR] Error loading StyleFrozen: {e}")
        raise


def load_priskfy(priskfy_base):
    """
    Load PRiskFY (fiscal-year policy risk) dataset.

    Args:
        priskfy_base: Base path to 3.12_H9_PRiskFY output

    Returns:
        DataFrame with gvkey, fyear, PRiskFY, n_quarters_used
    """
    print("\n" + "=" * 80)
    print("LOADING PRISKFY (FISCAL-YEAR POLICY RISK)")
    print("=" * 80)

    try:
        prisk_dir = get_latest_output_dir(priskfy_base, required_file="priskfy.parquet")
        print(f"[OK] Found PRiskFY directory: {prisk_dir.name}")

        file_path = prisk_dir / "priskfy.parquet"
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded PRiskFY: {len(df):,} firm-years")

        # Verify required columns
        required_cols = ["gvkey", "fyear", "PRiskFY"]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in PRiskFY: {missing_cols}")

        # Ensure gvkey is string and zero-padded
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

        # Ensure fyear is integer
        df["fyear"] = pd.to_numeric(df["fyear"], errors="coerce").astype("int64")

        print(f"  - GVKEY format: {df['gvkey'].iloc[0]} (zero-padded to 6 chars)")
        print(f"  - FYEAR dtype: {df['fyear'].dtype}")
        print(f"  - Unique firms: {df['gvkey'].nunique():,}")
        print(f"  - FYEAR range: {df['fyear'].min()}-{df['fyear'].max()}")
        print(f"  - PRiskFY mean: {df['PRiskFY'].mean():.2f}")
        print(f"  - PRiskFY std: {df['PRiskFY'].std():.2f}")
        print(
            f"  - PRiskFY min/max: {df['PRiskFY'].min():.2f} / {df['PRiskFY'].max():.2f}"
        )

        return df

    except Exception as e:
        print(f"[ERROR] Error loading PRiskFY: {e}")
        raise


def load_abnormal_investment(abnormal_inv_base):
    """
    Load AbnormalInvestment (Biddle DV + controls) dataset.

    Args:
        abnormal_inv_base: Base path to 3.13_H9_AbnormalInvestment output

    Returns:
        DataFrame with gvkey, fyear, AbsAbInv, TotalInv, controls
    """
    print("\n" + "=" * 80)
    print("LOADING ABNORMAL INVESTMENT (BIDDLE DV + CONTROLS)")
    print("=" * 80)

    try:
        abinv_dir = get_latest_output_dir(
            abnormal_inv_base, required_file="abnormal_investment.parquet"
        )
        print(f"[OK] Found AbnormalInvestment directory: {abinv_dir.name}")

        file_path = abinv_dir / "abnormal_investment.parquet"
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded AbnormalInvestment: {len(df):,} firm-years")

        # Verify required columns
        required_cols = ["gvkey", "fyear", "AbsAbInv"]
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in AbnormalInvestment: {missing_cols}")

        # Control columns
        control_cols = ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t", "SalesGrowth"]
        existing_controls = [c for c in control_cols if c in df.columns]

        # Ensure gvkey is string and zero-padded
        df["gvkey"] = df["gvkey"].astype(str).str.zfill(6)

        # Ensure fyear is integer
        df["fyear"] = pd.to_numeric(df["fyear"], errors="coerce").astype("int64")

        print(f"  - GVKEY format: {df['gvkey'].iloc[0]} (zero-padded to 6 chars)")
        print(f"  - FYEAR dtype: {df['fyear'].dtype}")
        print(f"  - Unique firms: {df['gvkey'].nunique():,}")
        print(f"  - FYEAR range: {df['fyear'].min()}-{df['fyear'].max()}")
        print(f"  - AbsAbInv mean: {df['AbsAbInv'].mean():.4f}")
        print(f"  - AbsAbInv std: {df['AbsAbInv'].std():.4f}")
        print(f"  - Controls available: {existing_controls}")

        return df

    except Exception as e:
        print(f"[ERROR] Error loading AbnormalInvestment: {e}")
        raise


# ==============================================================================
# Merge and Filter Functions
# ==============================================================================


def merge_final_panel(style_df, prisk_df, abinv_df, verbose=True):
    """
    Merge all three components into FINAL_PANEL.

    Memory-efficient approach:
    1. Start with abnormal_investment as base (has DV + controls)
    2. Merge PRiskFY on (gvkey, fyear) - left join
    3. Merge style_frozen on (gvkey, fyear) - left join

    Args:
        style_df: StyleFrozen DataFrame
        prisk_df: PRiskFY DataFrame
        abinv_df: AbnormalInvestment DataFrame
        verbose: Print progress messages

    Returns:
        Merged DataFrame with all variables
    """
    print("\n" + "=" * 80)
    print("MERGING FINAL PANEL")
    print("=" * 80)

    # Start with abnormal_investment as base
    if verbose:
        print("\n[STEP 1] Base dataset: AbnormalInvestment")
        print(f"  - N_obs: {len(abinv_df):,}")
        print(f"  - N_firms: {abinv_df['gvkey'].nunique():,}")

    panel = abinv_df.copy()

    # Memory check
    mem_before = get_process_memory_mb()
    if verbose:
        print(
            f"  - Memory: {mem_before['rss_mb']:.1f} MB ({mem_before['percent']:.1f}%)"
        )

    gc.collect()

    # Merge PRiskFY
    if verbose:
        print("\n[STEP 2] Merging PRiskFY on (gvkey, fyear)")

    # Select only columns we need from PRiskFY
    prisk_cols = ["gvkey", "fyear", "PRiskFY", "n_quarters_used"]
    prisk_merge = prisk_df[prisk_cols].copy()

    n_before = len(panel)
    panel = pd.merge(
        panel, prisk_merge, on=["gvkey", "fyear"], how="left", validate="one_to_one"
    )
    n_after = len(panel)

    if verbose:
        print(f"  - N_obs before: {n_before:,}")
        print(f"  - N_obs after: {n_after:,}")
        print(
            f"  - PRiskFY matches: {panel['PRiskFY'].notna().sum():,} ({panel['PRiskFY'].notna().sum() / len(panel) * 100:.1f}%)"
        )

    gc.collect()

    # Merge StyleFrozen
    if verbose:
        print("\n[STEP 3] Merging StyleFrozen on (gvkey, fyear)")

    # Select only columns we need from StyleFrozen
    style_cols = ["gvkey", "fyear", "style_frozen", "ceo_id", "ceo_name", "n_calls_fy"]
    style_merge = style_df[style_cols].copy()

    n_before = len(panel)
    panel = pd.merge(
        panel, style_merge, on=["gvkey", "fyear"], how="left", validate="one_to_one"
    )
    n_after = len(panel)

    if verbose:
        print(f"  - N_obs before: {n_before:,}")
        print(f"  - N_obs after: {n_after:,}")
        print(
            f"  - style_frozen matches: {panel['style_frozen'].notna().sum():,} ({panel['style_frozen'].notna().sum() / len(panel) * 100:.1f}%)"
        )

    gc.collect()

    # Final memory check
    mem_after = get_process_memory_mb()
    if verbose:
        print("\n[MERGE COMPLETE]")
        print(f"  - Final N_obs: {len(panel):,}")
        print(f"  - Final N_firms: {panel['gvkey'].nunique():,}")
        print(
            f"  - Final N_ceos: {panel['ceo_id'].notna().sum() > 0 and panel['ceo_id'].nunique() or 0:,}"
        )
        print(f"  - Memory: {mem_after['rss_mb']:.1f} MB ({mem_after['percent']:.1f}%)")

    return panel


def apply_sample_filters(panel, verbose=True):
    """
    Apply sample filters to remove observations with missing values.

    Filters:
    1. DROP if AbsAbInv is missing
    2. DROP if PRiskFY is missing
    3. DROP if style_frozen is missing
    4. DROP if any control missing (ln_at_t, lev_t, cash_t, roa_t, mb_t, SalesGrowth)

    Args:
        panel: Merged panel DataFrame
        verbose: Print progress messages

    Returns:
        Filtered DataFrame
    """
    print("\n" + "=" * 80)
    print("APPLYING SAMPLE FILTERS")
    print("=" * 80)

    n_start = len(panel)
    print(f"\nStarting observations: {n_start:,}")

    filters = {}

    # Filter 1: AbsAbInv not missing
    filter_name = "AbsAbInv missing"
    n_before = len(panel)
    panel = panel.dropna(subset=["AbsAbInv"])
    n_after = len(panel)
    filters[filter_name] = n_before - n_after
    if verbose:
        print(f"\n[{filter_name}]")
        print(
            f"  - Dropped: {filters[filter_name]:,} ({filters[filter_name] / n_start * 100:.2f}%)"
        )

    # Filter 2: PRiskFY not missing
    filter_name = "PRiskFY missing"
    n_before = len(panel)
    panel = panel.dropna(subset=["PRiskFY"])
    n_after = len(panel)
    filters[filter_name] = n_before - n_after
    if verbose:
        print(f"\n[{filter_name}]")
        print(
            f"  - Dropped: {filters[filter_name]:,} ({filters[filter_name] / n_start * 100:.2f}%)"
        )

    # Filter 3: style_frozen not missing
    filter_name = "style_frozen missing"
    n_before = len(panel)
    panel = panel.dropna(subset=["style_frozen"])
    n_after = len(panel)
    filters[filter_name] = n_before - n_after
    if verbose:
        print(f"\n[{filter_name}]")
        print(
            f"  - Dropped: {filters[filter_name]:,} ({filters[filter_name] / n_start * 100:.2f}%)"
        )

    # Filter 4: Controls not missing
    control_cols = ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t", "SalesGrowth"]
    existing_controls = [c for c in control_cols if c in panel.columns]

    if verbose:
        print("\n[Control missingness check]")
        for col in existing_controls:
            n_missing = panel[col].isna().sum()
            print(
                f"  - {col}: {n_missing:,} missing ({n_missing / len(panel) * 100:.2f}%)"
            )

    # Drop observations with any missing control
    filter_name = "Controls missing"
    n_before = len(panel)
    panel = panel.dropna(subset=existing_controls)
    n_after = len(panel)
    filters[filter_name] = n_before - n_after
    if verbose:
        print(f"\n[{filter_name}]")
        print(
            f"  - Dropped: {filters[filter_name]:,} ({filters[filter_name] / n_start * 100:.2f}%)"
        )

    n_end = len(panel)
    total_dropped = n_start - n_end

    if verbose:
        print("\n[FILTER SUMMARY]")
        print(f"  - Starting N: {n_start:,}")
        print(f"  - Final N: {n_end:,}")
        print(
            f"  - Total dropped: {total_dropped:,} ({total_dropped / n_start * 100:.2f}%)"
        )
        print(f"  - Final N_firms: {panel['gvkey'].nunique():,}")
        print(
            f"  - Final N_ceos: {panel['ceo_id'].notna().sum() > 0 and panel['ceo_id'].nunique() or 0:,}"
        )
        print(f"  - FYEAR range: {panel['fyear'].min()}-{panel['fyear'].max()}")

    # Verify no missing values in key variables
    key_vars = ["AbsAbInv", "PRiskFY", "style_frozen"] + existing_controls
    missing_check = panel[key_vars].isna().sum()
    if verbose and missing_check.sum() > 0:
        print("\n[WARNING] Missing values remain:")
        print(missing_check[missing_check > 0])

    return panel, filters


def create_interaction_term(panel, verbose=True):
    """
    Create interaction term: PRiskFY * style_frozen

    This is the MODERATOR variable that tests whether CEO style
    affects the PRisk -> abnormal investment relationship.

    Args:
        panel: Filtered panel DataFrame
        verbose: Print progress messages

    Returns:
        DataFrame with interaction term added
    """
    print("\n" + "=" * 80)
    print("CREATING INTERACTION TERM")
    print("=" * 80)

    # Create interaction term
    panel["interact"] = panel["PRiskFY"] * panel["style_frozen"]

    if verbose:
        print("\nInteraction term: PRiskFY * style_frozen")
        print(f"  - Mean: {panel['interact'].mean():.4f}")
        print(f"  - Std: {panel['interact'].std():.4f}")
        print(f"  - Min: {panel['interact'].min():.4f}")
        print(f"  - Max: {panel['interact'].max():.4f}")
        print(
            f"  - Correlation with PRiskFY: {panel['interact'].corr(panel['PRiskFY']):.4f}"
        )
        print(
            f"  - Correlation with style_frozen: {panel['interact'].corr(panel['style_frozen']):.4f}"
        )

    return panel


# ==============================================================================
# Sanity Checks
# ==============================================================================


def run_sanity_checks(panel, output_dir=None):
    """
    Run mandatory sanity checks on final panel.

    Checks:
    a. PRiskFY Coverage: mean, SD, p1, p99, min/max fiscal years
    b. StyleFrozen Coverage: mean, SD, p1, p99, variance by firm
    c. DV and Controls: distributions, winsorization confirmation
    d. Biddle Cell Viability: fraction of (ind2, fyear) cells with N >= 30

    Args:
        panel: Final filtered panel
        output_dir: If provided, save sanity_checks.txt

    Returns:
        Dictionary with sanity check results
    """
    print("\n" + "=" * 80)
    print("RUNNING MANDATORY SANITY CHECKS")
    print("=" * 80)

    checks = {}
    lines = []

    # Header
    lines.append("=" * 80)
    lines.append("H9 FINAL PANEL - SANITY CHECKS")
    lines.append("=" * 80)
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    # Sample overview
    lines.append("SAMPLE OVERVIEW")
    lines.append("-" * 40)
    lines.append(f"N_obs: {len(panel):,}")
    lines.append(f"N_firms: {panel['gvkey'].nunique():,}")
    if "ceo_id" in panel.columns:
        lines.append(f"N_ceos: {panel['ceo_id'].nunique():,}")
    lines.append(f"FYEAR range: {panel['fyear'].min()}-{panel['fyear'].max()}")
    lines.append("")

    # Check a: PRiskFY Coverage
    print("\n[a] PRiskFY Coverage")
    lines.append("PRISKFY COVERAGE")
    lines.append("-" * 40)

    prisk_stats = {
        "mean": float(panel["PRiskFY"].mean()),
        "sd": float(panel["PRiskFY"].std()),
        "p1": float(panel["PRiskFY"].quantile(0.01)),
        "p99": float(panel["PRiskFY"].quantile(0.99)),
        "min": float(panel["PRiskFY"].min()),
        "max": float(panel["PRiskFY"].max()),
        "min_fyear": int(panel["fyear"].min()),
        "max_fyear": int(panel["fyear"].max()),
    }

    for key, val in prisk_stats.items():
        if key in ["min_fyear", "max_fyear"]:
            print(f"  - {key}: {val}")
            lines.append(f"{key}: {val}")
        else:
            print(f"  - {key}: {val:.4f}")
            lines.append(f"{key}: {val:.4f}")

    checks["prisk_coverage"] = prisk_stats
    lines.append("")

    # Check b: StyleFrozen Coverage
    print("\n[b] StyleFrozen Coverage")
    lines.append("STYLEFROZEN COVERAGE")
    lines.append("-" * 40)

    style_stats = {
        "mean": float(panel["style_frozen"].mean()),
        "sd": float(panel["style_frozen"].std()),
        "p1": float(panel["style_frozen"].quantile(0.01)),
        "p99": float(panel["style_frozen"].quantile(0.99)),
        "min": float(panel["style_frozen"].min()),
        "max": float(panel["style_frozen"].max()),
    }

    for key, val in style_stats.items():
        print(f"  - {key}: {val:.4f}")
        lines.append(f"{key}: {val:.4f}")

    # Check variance by firm (CEOs may move)
    if "ceo_id" in panel.columns:
        ceo_var = panel.groupby("ceo_id")["style_frozen"].var()
        n_ceos_with_var = (ceo_var > 0).sum()
        print(
            f"  - N_ceos with within-CEO variance > 0: {n_ceos_with_var} (should be 0)"
        )
        lines.append(f"N_ceos_with_variance>0: {n_ceos_with_var} (should be 0)")

    checks["style_coverage"] = style_stats
    lines.append("")

    # Check c: DV and Controls
    print("\n[c] DV and Controls")
    lines.append("DV AND CONTROLS")
    lines.append("-" * 40)

    dv_cols = [
        "AbsAbInv",
        "TotalInv",
        "SalesGrowth",
        "ln_at_t",
        "lev_t",
        "cash_t",
        "roa_t",
        "mb_t",
    ]
    existing_dv = [c for c in dv_cols if c in panel.columns]

    for col in existing_dv:
        stats = {
            "mean": float(panel[col].mean()),
            "sd": float(panel[col].std()),
            "p1": float(panel[col].quantile(0.01)),
            "p99": float(panel[col].quantile(0.99)),
        }
        print(
            f"  - {col}: mean={stats['mean']:.4f}, sd={stats['sd']:.4f}, p1={stats['p1']:.4f}, p99={stats['p99']:.4f}"
        )
        lines.append(
            f"{col}: mean={stats['mean']:.4f}, sd={stats['sd']:.4f}, p1={stats['p1']:.4f}, p99={stats['p99']:.4f}"
        )

    checks["dv_controls"] = {
        col: {"mean": float(panel[col].mean()), "sd": float(panel[col].std())}
        for col in existing_dv
    }
    lines.append("")

    # Check d: Biddle Cell Viability
    print("\n[d] Biddle Cell Viability")
    lines.append("BIDDLE CELL VIABILITY")
    lines.append("-" * 40)

    if "ind2" in panel.columns:
        cell_counts = panel.groupby(["ind2", "fyear"]).size()
        viable_cells = (cell_counts >= 30).sum()
        total_cells = len(cell_counts)
        pct_viable = viable_cells / total_cells * 100 if total_cells > 0 else 0

        print(f"  - Total (ind2, fyear) cells: {total_cells:,}")
        print(f"  - Cells with N >= 30: {viable_cells:,} ({pct_viable:.1f}%)")

        lines.append(f"Total cells: {total_cells:,}")
        lines.append(f"Cells with N >= 30: {viable_cells:,} ({pct_viable:.1f}%)")

        checks["biddle_viability"] = {
            "total_cells": int(total_cells),
            "viable_cells": int(viable_cells),
            "pct_viable": float(pct_viable),
        }
    else:
        print("  - ind2 column not available, skipping cell viability check")
        lines.append("ind2 column not available")

    lines.append("")
    lines.append("=" * 80)

    # Save to file if output_dir provided
    if output_dir:
        sanity_file = output_dir / "sanity_checks.txt"
        with open(sanity_file, "w") as f:
            f.write("\n".join(lines))
        print(f"\n[OK] Sanity checks saved to: {sanity_file}")

    return checks


# ==============================================================================
# Regression Functions
# ==============================================================================


def run_h9_regression(panel, model_type="primary", verbose=True):
    """
    Run H9 regression with interaction term.

    Model:
        AbsAbInv_{i,t+1} = beta0 + beta1*PRiskFY_t + beta2*StyleFrozen_t
                          + beta3*(PRiskFY_t x StyleFrozen_t)
                          + gamma'*Controls_t
                          + FirmFE_i + YearFE_t + epsilon

    Key coefficient: beta3 (interaction term)

    Args:
        panel: Filtered panel DataFrame
        model_type: 'primary' or 'robustness'
        verbose: Print progress messages

    Returns:
        Dictionary with regression results
    """
    print("\n" + "=" * 80)
    print(f"RUNNING H9 REGRESSION ({model_type.upper()})")
    print("=" * 80)

    # Define regression variables
    dependent = "AbsAbInv"

    # Independent variables
    exog = ["PRiskFY", "style_frozen", "interact"]

    # Control variables
    control_cols = ["ln_at_t", "lev_t", "cash_t", "roa_t", "mb_t", "SalesGrowth"]
    existing_controls = [c for c in control_cols if c in panel.columns]
    exog.extend(existing_controls)

    if verbose:
        print("\nModel Specification:")
        print(f"  - Dependent: {dependent}")
        print("  - Independent: PRiskFY, style_frozen, interact")
        print(f"  - Controls: {', '.join(existing_controls)}")
        print("  - Fixed Effects: Firm (gvkey), Year (fyear)")
        print("  - Std Errors: Clustered by gvkey (firm)")
        print("\nKey coefficient of interest:")
        print("  - beta3 (interact = PRiskFY * style_frozen)")

    # Prepare data for regression
    reg_data = panel.copy()

    # Add gvkey and fyear as columns for panel_ols (they will be used to set index)
    reg_data = reg_data.reset_index(drop=True)

    if verbose:
        print("\nRegression data:")
        print(f"  - N_obs: {len(reg_data):,}")
        print(f"  - N_firms: {reg_data['gvkey'].nunique():,}")
        print(f"  - N_years: {reg_data['fyear'].nunique():,}")

    # Run regression using shared panel_ols module
    try:
        result = run_panel_ols(
            df=reg_data,
            dependent=dependent,
            exog=exog,
            entity_col="gvkey",
            time_col="fyear",
            entity_effects=True,
            time_effects=True,
            industry_effects=False,
            cov_type="clustered",
            cluster_cols=None,  # Default to entity (firm) clustering
            check_collinearity=True,
            vif_threshold=5.0,
        )

        return result

    except Exception as e:
        print(f"\n[ERROR] Regression failed: {e}")
        raise


def format_regression_results(result, output_dir):
    """
    Extract and save regression results.

    Args:
        result: Result from run_panel_ols
        output_dir: Output directory for saving files

    Returns:
        DataFrame with formatted results
    """
    print("\n" + "=" * 80)
    print("FORMATTING REGRESSION RESULTS")
    print("=" * 80)

    # Extract coefficients
    coeffs = result["coefficients"].copy()
    coeffs["p_value"] = result["model"].pvalues
    coeffs["variable"] = coeffs.index

    # Reorder columns
    cols = ["variable", "Coefficient", "Std. Error", "t-stat", "p_value"]
    results_df = coeffs[cols].copy()

    # Reset index for cleaner output
    results_df = results_df.reset_index(drop=True)

    # Save to CSV
    results_csv = output_dir / "h9_regression_results.csv"
    results_df.to_csv(results_csv, index=False)
    print(f"[OK] Results saved to: {results_csv}")

    # Save full model summary to text file
    summary_file = output_dir / "h9_regression_output.txt"
    with open(summary_file, "w") as f:
        f.write(str(result["model"].summary))
    print(f"[OK] Full summary saved to: {summary_file}")

    return results_df


# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(panel, reg_result, sanity_checks, output_dir):
    """
    Generate summary report with interpretation of H9 findings.

    Args:
        panel: Final panel DataFrame
        reg_result: Regression result dictionary
        sanity_checks: Sanity check results
        output_dir: Output directory
    """
    print("\n" + "=" * 80)
    print("GENERATING SUMMARY REPORT")
    print("=" * 80)

    coeffs = reg_result["coefficients"]
    summary = reg_result["summary"]

    # Extract key coefficients
    beta1 = coeffs.loc["PRiskFY", "Coefficient"]
    beta1_se = coeffs.loc["PRiskFY", "Std. Error"]
    beta1_t = coeffs.loc["PRiskFY", "t-stat"]
    beta1_p = reg_result["model"].pvalues.loc["PRiskFY"]

    beta2 = coeffs.loc["style_frozen", "Coefficient"]
    beta2_se = coeffs.loc["style_frozen", "Std. Error"]
    beta2_t = coeffs.loc["style_frozen", "t-stat"]
    beta2_p = reg_result["model"].pvalues.loc["style_frozen"]

    beta3 = coeffs.loc["interact", "Coefficient"]
    beta3_se = coeffs.loc["interact", "Std. Error"]
    beta3_t = coeffs.loc["interact", "t-stat"]
    beta3_p = reg_result["model"].pvalues.loc["interact"]

    # Interpret beta3
    if beta3_p < 0.01:
        sig_level = "p < 0.01"
    elif beta3_p < 0.05:
        sig_level = "p < 0.05"
    elif beta3_p < 0.10:
        sig_level = "p < 0.10"
    else:
        sig_level = f"p = {beta3_p:.4f} (not significant)"

    if beta3 > 0 and beta3_p < 0.05:
        interpretation = f"""
**Interaction Effect: POSITIVE and SIGNIFICANT**

The coefficient beta3 = {beta3:.4f} ({sig_level}) indicates that CEOs with **vaguer communication styles**
(StyleFrozen < 0) show a **STRONGER** relationship between policy risk (PRiskFY) and abnormal investment.

- For CEOs with style_frozen at -1 SD (vague): PRiskFY effect = {beta1 + beta3 * -1:.4f}
- For CEOs with style_frozen at mean: PRiskFY effect = {beta1:.4f}
- For CEOs with style_frozen at +1 SD (clear): PRiskFY effect = {beta1 + beta3:.4f}

**Economic interpretation:** Vague CEOs amplify the effect of policy risk on abnormal investment,
potentially over-reacting to policy uncertainty or signaling more risk to stakeholders.
"""
    elif beta3 < 0 and beta3_p < 0.05:
        interpretation = f"""
**Interaction Effect: NEGATIVE and SIGNIFICANT**

The coefficient beta3 = {beta3:.4f} ({sig_level}) indicates that CEOs with **vaguer communication styles**
(StyleFrozen < 0) show a **WEAKER** relationship between policy risk (PRiskFY) and abnormal investment.

- For CEOs with style_frozen at -1 SD (vague): PRiskFY effect = {beta1 + beta3 * -1:.4f}
- For CEOs with style_frozen at mean: PRiskFY effect = {beta1:.4f}
- For CEOs with style_frozen at +1 SD (clear): PRiskFY effect = {beta1 + beta3:.4f}

**Economic interpretation:** Vague CEOs dampen the effect of policy risk on abnormal investment,
possibly because their vague communication masks true risk exposure or stakeholders discount
their speech.
"""
    else:
        interpretation = f"""
**Interaction Effect: NOT SIGNIFICANT**

The coefficient beta3 = {beta3:.4f} ({sig_level}) is **not statistically significant**.

**Economic interpretation:** CEO communication style does NOT moderate the relationship between
policy risk and abnormal investment. This is a **meaningful null finding** that suggests:

1. Policy risk affects abnormal investment through channels other than CEO communication style
2. Investment decisions may be driven by fundamentals rather than CEO rhetoric
3. The interaction effect may be too small to detect with the current sample size

**Conclusion:** H9 is NOT SUPPORTED. CEO vagueness does not significantly moderate the
PRisk -> abnormal investment relationship.
"""

    # Build report
    report_lines = [
        "# H9 Regression Results Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Hypothesis",
        "",
        "**H9:** The effect of Hassan PRisk on abnormal investment is MODERATED by CEO communication clarity.",
        "",
        "## Model Specification",
        "",
        "``",
        "AbsAbInv_{i,t+1} = beta0 + beta1*PRiskFY_t + beta2*StyleFrozen_t",
        "                  + beta3*(PRiskFY_t x StyleFrozen_t)",
        "                  + gamma'*Controls_t",
        "                  + FirmFE_i + YearFE_t + epsilon",
        "```",
        "",
        "## Sample Statistics",
        "",
        f"- N_obs: {len(panel):,}",
        f"- N_firms: {panel['gvkey'].nunique():,}",
        f"- N_ceos: {panel['ceo_id'].nunique():,}",
        f"- FYEAR range: {panel['fyear'].min()}-{panel['fyear'].max()}",
        "",
        "## Regression Results",
        "",
        "### Key Coefficients",
        "",
        "| Variable | Coefficient | Std.Error | t-stat | p-value |",
        "|----------|-------------|-----------|--------|---------|",
        f"| PRiskFY | {beta1:.4f} | {beta1_se:.4f} | {beta1_t:.2f} | {beta1_p:.4f} |",
        f"| StyleFrozen | {beta2:.4f} | {beta2_se:.4f} | {beta2_t:.2f} | {beta2_p:.4f} |",
        f"| **Interact (PRiskFY x StyleFrozen)** | **{beta3:.4f}** | **{beta3_se:.4f}** | **{beta3_t:.2f}** | **{beta3_p:.4f}** |",
        "",
        "Significance: *** p<0.01, ** p<0.05, * p<0.10",
        "",
        "### Interpretation of Beta3 (Interaction Term)",
        interpretation,
        "",
        "### Model Fit",
        "",
        f"- R-squared: {summary['rsquared']:.4f}",
        f"- R-squared (within): {summary['rsquared_within']:.4f}",
        f"- N_obs: {summary['nobs']:,}",
        "",
        "### Fixed Effects",
        "",
        f"- Firm FE: {summary['entity_effects']}",
        f"- Year FE: {summary['time_effects']}",
        f"- Covariance type: {summary['cov_type']}",
        "",
        "## Conclusion",
        "",
        "**H9 Result:**"
        + (" **SUPPORTED**" if beta3_p < 0.05 else " **NOT SUPPORTED**"),
        "",
        f"The interaction term (PRiskFY x StyleFrozen) is {'statistically significant' if beta3_p < 0.05 else 'not significant'} at the 5% level.",
        "",
        "---",
        "",
        "*Generated by 4.11_H9_Regression.py*",
    ]

    # Save report
    report_file = output_dir / "report_step411_04.md"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"[OK] Report saved to: {report_file}")
    print(interpretation)

    return report_file


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="H9 Final Merge and Regression",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Primary specification
  python 4.11_H9_Regression.py

  # Dry run (load data, skip regression)
  python 4.11_H9_Regression.py --dry-run

  # Robustness specification
  python 4.11_H9_Regression.py --model-type robustness
        """,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Load data and verify merge, but skip regression",
    )
    parser.add_argument(
        "--model-type",
        type=str,
        default="primary",
        choices=["primary", "robustness"],
        help="Model type (default: primary)",
    )

    args = parser.parse_args()

    # Generate timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")

    # Setup paths
    paths = setup_paths(timestamp)

    print("=" * 80)
    print("H9 FINAL MERGE AND REGRESSION")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Model type: {args.model_type}")
    print(f"Dry run: {args.dry_run}")
    print("=" * 80)

    start_time = time.time()

    # Collect statistics
    stats = {
        "input": {},
        "output": {},
        "processing": {},
        "timing": {},
    }

    try:
        # ---------------------------------------------------------------------
        # STEP 1: Load all components
        # ---------------------------------------------------------------------

        # Load StyleFrozen
        style_df = load_style_frozen(paths["style_frozen_base"])
        stats["input"]["style_frozen_obs"] = len(style_df)
        stats["input"]["style_frozen_firms"] = style_df["gvkey"].nunique()
        gc.collect()

        # Load PRiskFY
        prisk_df = load_priskfy(paths["priskfy_base"])
        stats["input"]["priskfy_obs"] = len(prisk_df)
        stats["input"]["priskfy_firms"] = prisk_df["gvkey"].nunique()
        gc.collect()

        # Load AbnormalInvestment
        abinv_df = load_abnormal_investment(paths["abnormal_inv_base"])
        stats["input"]["abinv_obs"] = len(abinv_df)
        stats["input"]["abinv_firms"] = abinv_df["gvkey"].nunique()
        gc.collect()

        # ---------------------------------------------------------------------
        # STEP 2: Merge into FINAL_PANEL
        # ---------------------------------------------------------------------

        panel = merge_final_panel(style_df, prisk_df, abinv_df)
        stats["output"]["merged_obs"] = len(panel)
        stats["output"]["merged_firms"] = panel["gvkey"].nunique()
        gc.collect()

        # ---------------------------------------------------------------------
        # STEP 3: Apply sample filters
        # ---------------------------------------------------------------------

        panel, filters = apply_sample_filters(panel)
        stats["output"]["final_obs"] = len(panel)
        stats["output"]["final_firms"] = panel["gvkey"].nunique()
        stats["processing"]["filters"] = filters
        gc.collect()

        # ---------------------------------------------------------------------
        # STEP 4: Create interaction term
        # ---------------------------------------------------------------------

        panel = create_interaction_term(panel)
        gc.collect()

        # ---------------------------------------------------------------------
        # STEP 5: Save final panel
        # ---------------------------------------------------------------------

        final_panel_path = paths["output_dir"] / "final_panel.parquet"
        panel.to_parquet(final_panel_path, index=False)
        print(f"\n[OK] Final panel saved to: {final_panel_path}")
        gc.collect()

        # ---------------------------------------------------------------------
        # STEP 6: Run sanity checks
        # ---------------------------------------------------------------------

        sanity_checks = run_sanity_checks(panel, paths["output_dir"])

        # ---------------------------------------------------------------------
        # STEP 7: Run regression (skip if dry-run)
        # ---------------------------------------------------------------------

        if args.dry_run:
            print("\n" + "=" * 80)
            print("DRY RUN COMPLETE - Skipping regression")
            print("=" * 80)
        else:
            reg_result = run_h9_regression(panel, model_type=args.model_type)
            format_regression_results(reg_result, paths["output_dir"])
            generate_report(panel, reg_result, sanity_checks, paths["output_dir"])

        # ---------------------------------------------------------------------
        # Timing and Statistics
        # ---------------------------------------------------------------------

        end_time = time.time()
        duration = end_time - start_time
        stats["timing"]["duration_seconds"] = duration

        print("\n" + "=" * 80)
        print("EXECUTION COMPLETE")
        print("=" * 80)
        print(f"Duration: {duration:.1f} seconds")

        # Save stats
        save_stats(stats, paths["output_dir"])

        # Memory check
        mem_final = get_process_memory_mb()
        print(
            f"Final memory: {mem_final['rss_mb']:.1f} MB ({mem_final['percent']:.1f}%)"
        )

        print("\nOutput files:")
        for f in paths["output_dir"].iterdir():
            print(f"  - {f.name}")

        return 0

    except Exception as e:
        print(f"\n[ERROR] Execution failed: {e}")
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
