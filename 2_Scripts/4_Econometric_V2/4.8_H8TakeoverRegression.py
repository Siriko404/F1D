#!/usr/bin/env python3
"""
==============================================================================
STEP 4.8: H8 Takeover Regression
==============================================================================
ID: 4.8_H8TakeoverRegression
Description: Logistic regressions for H8 (Speech Uncertainty -> Takeover
             Target Probability). Tests whether vague managers face higher
             takeover likelihood.

Model Specification:
    logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty_t + gamma*Controls
                                  + Firm FE + Year FE

Hypothesis Tests:
    H8a: beta1 > 0 (Higher uncertainty -> Higher takeover probability)

Econometric Standards:
    - Model: Logistic regression with firm and year FE
    - SE: Clustered at firm level
    - DV: Forward-looking (t+1) for causal interpretation
    - Alternative: Cox proportional hazards (if feasible)

Inputs:
    - 4_Outputs/3_Financial_V2/latest/H8_Takeover.parquet

Outputs:
    - 4_Outputs/4_Econometric_V2/{timestamp}/H8_Regression_Results.parquet
    - 4_Outputs/4_Econometric_V2/{timestamp}/H8_RESULTS.md
    - 4_Outputs/4_Econometric_V2/{timestamp}/stats.json

Deterministic: true
==============================================================================
"""

import sys
import os
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np
import yaml
import json
import time
import subprocess
import warnings

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
from shared.path_utils import (
    validate_output_path,
    ensure_output_dir,
    validate_input_file,
    get_latest_output_dir,
)

from shared.observability_utils import (
    DualWriter,
    compute_file_checksum,
    print_stat,
    analyze_missing_values,
    print_stats_summary,
    save_stats,
    get_process_memory_mb,
    calculate_throughput,
)

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

# ==============================================================================
# Configuration
# ==============================================================================


def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "project.yaml"
    if config_path.exists():
        validate_input_file(config_path, must_exist=True)
        with open(config_path, "r") as f:
            return yaml.safe_load(f)
    return {}


def get_git_sha():
    """Get current git commit SHA for reproducibility"""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


# Uncertainty measures (4 total available in H8_Takeover.parquet)
UNCERTAINTY_MEASURES = [
    'Manager_QA_Uncertainty_pct',
    'CEO_QA_Uncertainty_pct',
    'Manager_Pres_Uncertainty_pct',
    'CEO_Pres_Uncertainty_pct',
]

# Control variables (available in H8_Takeover.parquet)
CONTROL_VARS = [
    'Volatility', 'StockRet'
]

# Regression specifications
SPECS = {
    'primary': {'include_fe': True, 'cluster': 'firm'},
    'pooled': {'include_fe': False, 'cluster': 'firm'},
}

# ==============================================================================
# Path Setup
# ==============================================================================


def setup_paths(timestamp):
    """Set up all required paths"""
    root = Path(__file__).parent.parent.parent

    # Resolve H8 output directory
    h8_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_V2",
        required_file="H8_Takeover.parquet",
    )

    paths = {
        "root": root,
        "h8_file": h8_dir / "H8_Takeover.parquet",
    }

    # Output directory
    output_base = root / "4_Outputs" / "4_Econometric_V2"
    paths["output_dir"] = output_base / timestamp
    ensure_output_dir(paths["output_dir"])

    # Log directory
    log_base = root / "3_Logs" / "4_Econometric_V2"
    ensure_output_dir(log_base)
    paths["log_file"] = log_base / f"{timestamp}_H8.log"

    return paths


# ==============================================================================
# Data Loading
# ==============================================================================


def load_h8_data(h8_path):
    """
    Load H8 takeover data.

    Args:
        h8_path: Path to H8_Takeover.parquet

    Returns:
        DataFrame with takeover variables, uncertainty measures, and controls
    """
    print("\nLoading H8 takeover data...")

    df = pd.read_parquet(h8_path)
    print(f"  Loaded H8: {len(df):,} observations")

    # Ensure gvkey is string
    df['gvkey'] = df['gvkey'].astype(str).str.zfill(6)

    # Set MultiIndex for panel data
    df = df.set_index(['gvkey', 'year'])

    print(f"  Firms: {df.index.get_level_values('gvkey').nunique():,}")
    print(f"  Years: {df.index.get_level_values('year').min()}-{df.index.get_level_values('year').max()}")

    # Check takeover variation
    takeover_rate = df['takeover_fwd'].mean()
    takeover_events = df['takeover_fwd'].sum()
    print(f"  Takeover events (t+1): {takeover_events:,}")
    print(f"  Takeover rate: {takeover_rate:.2%}")

    if takeover_events == 0:
        print("  WARNING: No takeover events in sample!")
        print("  Logistic regression requires variation in dependent variable")

    return df


# ==============================================================================
# Logit Regression
# ==============================================================================


def run_h8_logit(df, uncertainty_var, dv_col='takeover_fwd',
                 controls=None, include_fe=True):
    """
    Run single H8 logistic regression.

    Specification:
        logit(P(Takeover_{t+1}=1)) = beta0 + beta1*Uncertainty + Controls + FE

    Args:
        df: Dataset with gvkey, year, DV, IV, controls (MultiIndex)
        uncertainty_var: Name of uncertainty IV
        dv_col: Name of dependent variable (binary)
        controls: List of control variable names
        include_fe: Whether to include firm and year FE

    Returns:
        dict with coefficients, SEs, p-values, diagnostics
    """
    import statsmodels.api as sm
    from statsmodels.stats.multitest import multipletests

    # Prepare data
    iv_vars = [uncertainty_var]
    if controls:
        iv_vars.extend([c for c in controls if c in df.columns])

    # Drop rows with missing IV or controls
    model_df = df[[dv_col] + iv_vars].dropna()
    model_df = model_df.copy()

    # Reset index to access gvkey and year for clustering and FE
    model_df = model_df.reset_index()

    # Add intercept
    X = model_df[iv_vars].copy()
    X = sm.add_constant(X)
    y = model_df[dv_col]

    # Add firm and year FE if requested
    if include_fe:
        # Use firm dummies and year dummies
        firm_dummies = pd.get_dummies(
            model_df['gvkey'],
            prefix='firm',
            drop_first=True
        )
        year_dummies = pd.get_dummies(
            model_df['year'],
            prefix='year',
            drop_first=True
        )
        X = pd.concat([X, firm_dummies, year_dummies], axis=1)

    # Check for variation in DV
    if y.sum() == 0 or y.sum() == len(y):
        return {
            'uncertainty_var': uncertainty_var,
            'coefficient': np.nan,
            'se': np.nan,
            'p_two_sided': np.nan,
            'p_one_sided': np.nan,
            'odds_ratio': np.nan,
            'or_ci_lower': np.nan,
            'or_ci_upper': np.nan,
            'n': len(model_df),
            'n_firms': model_df['gvkey'].nunique(),
            'n_takeovers': int(y.sum()),
            'pseudo_r2': np.nan,
            'converged': False,
            'error': 'No variation in dependent variable'
        }

    # Fit logit with clustered SE
    try:
        logit_model = sm.Logit(y, X)
        results = logit_model.fit(
            cov_type='cluster',
            cov_kwds={'groups': model_df['gvkey']},
            disp=False,
            maxiter=100
        )

        # Extract uncertainty coefficient
        if uncertainty_var not in results.params:
            return {
                'uncertainty_var': uncertainty_var,
                'coefficient': np.nan,
                'se': np.nan,
                'p_two_sided': np.nan,
                'p_one_sided': np.nan,
                'odds_ratio': np.nan,
                'or_ci_lower': np.nan,
                'or_ci_upper': np.nan,
                'n': len(model_df),
                'n_firms': model_df['gvkey'].nunique(),
                'n_takeovers': int(y.sum()),
                'pseudo_r2': np.nan,
                'converged': False,
                'error': f'{uncertainty_var} not in results.params'
            }

        coef = results.params[uncertainty_var]
        se = results.bse[uncertainty_var]
        p_two = results.pvalues[uncertainty_var]
        p_one = p_two / 2 if coef > 0 else 1 - p_two / 2  # H8a: beta > 0

        # Calculate odds ratio
        odds_ratio = np.exp(coef)
        or_ci_lower = np.exp(coef - 1.96 * se)
        or_ci_upper = np.exp(coef + 1.96 * se)

        return {
            'uncertainty_var': uncertainty_var,
            'coefficient': coef,
            'se': se,
            'p_two_sided': p_two,
            'p_one_sided': p_one,
            'odds_ratio': odds_ratio,
            'or_ci_lower': or_ci_lower,
            'or_ci_upper': or_ci_upper,
            'n': len(model_df),
            'n_firms': model_df['gvkey'].nunique(),
            'n_takeovers': int(y.sum()),
            'pseudo_r2': results.prsquared,
            'converged': True,
            'error': None
        }
    except Exception as e:
        return {
            'uncertainty_var': uncertainty_var,
            'coefficient': np.nan,
            'se': np.nan,
            'p_two_sided': np.nan,
            'p_one_sided': np.nan,
            'odds_ratio': np.nan,
            'or_ci_lower': np.nan,
            'or_ci_upper': np.nan,
            'n': len(model_df),
            'n_firms': model_df['gvkey'].nunique(),
            'n_takeovers': int(y.sum()) if 'y' in locals() else 0,
            'pseudo_r2': np.nan,
            'converged': False,
            'error': str(e)
        }


def run_all_regressions(df, uncertainty_measures, control_vars, specs):
    """
    Run all H8 regressions.

    Args:
        df: Dataset with MultiIndex (gvkey, year)
        uncertainty_measures: List of uncertainty IV names
        control_vars: List of control variable names
        specs: Dict of specification configurations

    Returns:
        List of regression result dicts
    """
    results = []

    for spec_name, spec_config in specs.items():
        print(f"\nRunning specification: {spec_name}")

        for iv in uncertainty_measures:
            print(f"  IV: {iv}...")

            result = run_h8_logit(
                df,
                iv,
                dv_col='takeover_fwd',
                controls=control_vars,
                include_fe=spec_config['include_fe']
            )

            result['spec'] = spec_name
            results.append(result)

            if result['converged']:
                print(f"    Coef: {result['coefficient']:.4f}, SE: {result['se']:.4f}, "
                      f"p (one-tailed): {result['p_one_sided']:.4f}, OR: {result['odds_ratio']:.2f}")
            else:
                print(f"    ERROR: {result['error']}")

    return results


def apply_fdr_correction(results_list):
    """
    Apply FDR correction to primary specification results.

    Args:
        results_list: List of regression result dicts

    Returns:
        Modified results_list with p_fdr added
    """
    from statsmodels.stats.multitest import multipletests

    # Filter to primary spec results
    primary_results = [r for r in results_list if r['spec'] == 'primary' and r['converged']]

    if not primary_results:
        print("\nWARNING: No converged primary results for FDR correction")
        return results_list

    # Extract p-values
    p_values = [r['p_one_sided'] for r in primary_results]

    # Apply FDR correction (Benjamini-Hochberg)
    reject, pvals_corrected, _, _ = multipletests(
        p_values,
        alpha=0.05,
        method='fdr_bh'
    )

    # Add FDR-corrected p-values to results
    primary_idx = 0
    for i, result in enumerate(results_list):
        if result['spec'] == 'primary' and result['converged']:
            results_list[i]['p_fdr'] = pvals_corrected[primary_idx]
            results_list[i]['fdr_reject'] = reject[primary_idx]
            primary_idx += 1

    return results_list


# ==============================================================================
# Output Functions
# ==============================================================================


def save_regression_results(results_list, output_dir):
    """
    Save regression results to parquet.

    Args:
        results_list: List of regression result dicts
        output_dir: Output directory path

    Returns:
        Path to saved parquet file
    """
    output_file = output_dir / "H8_Regression_Results.parquet"

    df_results = pd.DataFrame(results_list)

    # Reorder columns
    col_order = [
        'spec', 'uncertainty_var', 'coefficient', 'se',
        'p_two_sided', 'p_one_sided', 'p_fdr', 'fdr_reject',
        'odds_ratio', 'or_ci_lower', 'or_ci_upper',
        'n', 'n_firms', 'n_takeovers', 'pseudo_r2',
        'converged', 'error'
    ]

    # Only include columns that exist
    col_order = [c for c in col_order if c in df_results.columns]
    df_results = df_results[col_order]

    df_results.to_parquet(output_file, index=False)
    print(f"\nSaved regression results to: {output_file}")

    return output_file


def generate_h8_results_report(results_list, sample_stats, timestamp):
    """
    Generate H8 results report in markdown.

    Special focus on odds ratios for interpretation.

    Args:
        results_list: List of regression result dicts
        sample_stats: Dict with sample statistics
        timestamp: Execution timestamp

    Returns:
        Markdown report string
    """
    report = "# H8 Regression Results: Speech Uncertainty -> Takeover Target Probability\n\n"

    # Executive summary
    primary_results = [r for r in results_list if r['spec'] == 'primary' and r['converged']]
    n_sig = sum(1 for r in primary_results if r['p_one_sided'] < 0.05)
    n_fdr = sum(1 for r in primary_results if r.get('p_fdr', 1) < 0.05)

    report += f"**Date:** {timestamp}\n"
    report += f"**Sample:** {sample_stats['n_obs']:,} firm-years, {sample_stats['n_firms']:,} firms\n"
    report += f"**Years:** {sample_stats['year_range']}\n"
    report += f"**Takeover events:** {sample_stats['n_takeovers']}\n"
    report += f"**Takeover rate:** {sample_stats['takeover_rate']:.2%}\n\n"

    report += "## Executive Summary\n\n"
    report += f"**Hypothesis H8a:** Higher speech uncertainty predicts HIGHER takeover probability (beta > 0)\n\n"
    report += f"**Conclusion:** "
    if n_fdr >= 4:
        report += "SUPPORTED - Strong evidence\n"
    elif n_fdr >= 2:
        report += "WEAKLY SUPPORTED - Moderate evidence\n"
    elif n_fdr >= 1:
        report += "MIXED - Limited evidence\n"
    else:
        report += "NOT SUPPORTED - No consistent evidence\n"

    report += f"\n**Significant measures (p < 0.05, one-tailed):** {n_sig}/{len(primary_results)}\n"
    report += f"**After FDR correction:** {n_fdr}/{len(primary_results)}\n\n"

    # Primary spec results table
    report += "## Primary Specification Results\n\n"
    report += "| Uncertainty Measure | Beta | SE | Odds Ratio | 95% CI OR | p (one-tailed) | FDR | Significant? |\n"
    report += "|---------------------|------|----|------------|-----------|----------------|-----|--------------|\n"

    for r in primary_results:
        sig = "Yes" if r['p_one_sided'] < 0.05 else "No"
        fdr_sig = "Yes" if r.get('p_fdr', 1) < 0.05 else "No"
        or_ci = f"[{r['or_ci_lower']:.2f}, {r['or_ci_upper']:.2f}]"
        report += f"| {r['uncertainty_var']} | {r['coefficient']:.4f} | {r['se']:.4f} | {r['odds_ratio']:.2f} | {or_ci} | {r['p_one_sided']:.4f} | {fdr_sig} | {sig} |\n"

    # Interpretation guide
    report += "\n### Interpretation\n\n"
    report += "Odds ratios > 1.0 indicate higher takeover probability per unit increase in uncertainty.\n"
    report += "For example, OR = 1.05 means 5% higher odds of takeover for each 1% increase in uncertainty.\n\n"

    # Pooled spec results (if available)
    pooled_results = [r for r in results_list if r['spec'] == 'pooled' and r['converged']]
    if pooled_results:
        report += "## Pooled Specification Results (No Fixed Effects)\n\n"
        report += "| Uncertainty Measure | Beta | SE | Odds Ratio | 95% CI OR | p (one-tailed) | Significant? |\n"
        report += "|---------------------|------|----|------------|-----------|----------------|--------------|\n"

        for r in pooled_results:
            sig = "Yes" if r['p_one_sided'] < 0.05 else "No"
            or_ci = f"[{r['or_ci_lower']:.2f}, {r['or_ci_upper']:.2f}]"
            report += f"| {r['uncertainty_var']} | {r['coefficient']:.4f} | {r['se']:.4f} | {r['odds_ratio']:.2f} | {or_ci} | {r['p_one_sided']:.4f} | {sig} |\n"

    # Warnings
    if sample_stats['n_takeovers'] < 100:
        report += "\n### Warnings\n\n"
        report += f"- **Low takeover events:** Only {sample_stats['n_takeovers']} takeover events in sample "
        report += f"(expected minimum: 100)\n"
        report += "- This limits statistical power and may affect reliability of estimates\n"

    if sample_stats['takeover_rate'] < 0.005:
        report += f"- **Low takeover rate:** {sample_stats['takeover_rate']:.2%} is below expected range (0.5%-5%)\n"
        report += "- H7 sample period (2002-2004) is very short, limiting takeover events\n"

    return report


def save_results_report(report, output_dir):
    """
    Save results report to markdown.

    Args:
        report: Markdown report string
        output_dir: Output directory path

    Returns:
        Path to saved markdown file
    """
    output_file = output_dir / "H8_RESULTS.md"

    with open(output_file, 'w') as f:
        f.write(report)

    print(f"Saved results report to: {output_file}")
    return output_file


# ==============================================================================
# Main Execution
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description="H8 Takeover Regression - Test whether speech uncertainty predicts takeover likelihood"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate prerequisites and exit without processing"
    )
    return parser.parse_args()


def check_prerequisites(paths):
    """Check that required inputs exist"""
    print("Checking prerequisites...")

    ok = True
    if not paths["h8_file"].exists():
        print(f"  [ERROR] H8 data not found: {paths['h8_file']}")
        ok = False
    else:
        print(f"  [OK] H8 data: {paths['h8_file']}")

    return ok


def main():
    """Main execution"""
    args = parse_arguments()

    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    paths = setup_paths(timestamp)

    # Handle dry-run mode
    if args.dry_run:
        print("=" * 60)
        print("STEP 4.8: H8 Takeover Regression - DRY RUN")
        print(f"Timestamp: {timestamp}")
        print("=" * 60)

        prereq_ok = check_prerequisites(paths)
        if prereq_ok:
            print("\n[OK] All prerequisites validated")
            print("\nWould compute:")
            print("  - Logistic regressions (4 uncertainty measures x 2 specs)")
            print("  - Firm and year fixed effects")
            print("  - Firm-clustered standard errors")
            print("  - FDR correction across measures")
            print(f"\nOutput would be written to: {paths['output_dir']}")
            sys.exit(0)
        else:
            print("\n[ERROR] Prerequisites not met")
            sys.exit(1)

    # Check prerequisites before processing
    prereq_ok = check_prerequisites(paths)
    if not prereq_ok:
        print("\n[ERROR] Prerequisites not met. Exiting.")
        sys.exit(1)

    # Setup logging
    dual_writer = DualWriter(paths["log_file"])
    sys.stdout = dual_writer

    print("=" * 60)
    print("STEP 4.8: H8 Takeover Regression")
    print(f"Timestamp: {timestamp}")
    print("=" * 60)

    # Initialize statistics
    start_time = time.perf_counter()
    start_iso = datetime.now().isoformat()
    mem_start = get_process_memory_mb()
    memory_readings = [mem_start["rss_mb"]]

    stats = {
        "step_id": "4.8_H8TakeoverRegression",
        "timestamp": timestamp,
        "git_sha": get_git_sha(),
        "input": {"files": [], "checksums": {}, "total_rows": 0},
        "processing": {
            "n_regressions": 0,
            "n_converged": 0,
            "n_significant": 0,
        },
        "output": {"files": [], "checksums": {}, "final_rows": 0},
        "sample_stats": {},
        "results": [],
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
        "memory": {
            "start_mb": mem_start["rss_mb"],
            "end_mb": 0.0,
            "peak_mb": 0.0,
            "delta_mb": 0.0,
        },
    }

    # ========================================================================
    # Load Data
    # ========================================================================

    print("\nLoading data...")

    print("\nH8 Takeover Data:")
    stats["input"]["files"].append(str(paths["h8_file"]))
    stats["input"]["checksums"][paths["h8_file"].name] = compute_file_checksum(paths["h8_file"])
    h8_df = load_h8_data(paths["h8_file"])
    stats["input"]["total_rows"] = len(h8_df)

    # Sample statistics
    sample_stats = {
        "n_obs": len(h8_df),
        "n_firms": h8_df.index.get_level_values('gvkey').nunique(),
        "year_range": f"{h8_df.index.get_level_values('year').min()}-{h8_df.index.get_level_values('year').max()}",
        "n_takeovers": int(h8_df['takeover_fwd'].sum()),
        "takeover_rate": float(h8_df['takeover_fwd'].mean()),
    }
    stats["sample_stats"] = sample_stats

    # ========================================================================
    # Run Regressions
    # ========================================================================

    print("\n" + "=" * 60)
    print("Running H8 Logistic Regressions")
    print("=" * 60)

    results = run_all_regressions(
        h8_df,
        UNCERTAINTY_MEASURES,
        CONTROL_VARS,
        SPECS
    )

    stats["processing"]["n_regressions"] = len(results)
    stats["processing"]["n_converged"] = sum(1 for r in results if r['converged'])
    stats["processing"]["n_significant"] = sum(
        1 for r in results
        if r['converged'] and r['p_one_sided'] < 0.05
    )

    print(f"\nRegressions completed: {len(results)}")
    print(f"  Converged: {stats['processing']['n_converged']}")
    print(f"  Significant (p < 0.05, one-tailed): {stats['processing']['n_significant']}")

    # ========================================================================
    # Apply FDR Correction
    # ========================================================================

    print("\n" + "=" * 60)
    print("Applying FDR Correction (Benjamini-Hochberg)")
    print("=" * 60)

    results = apply_fdr_correction(results)

    n_fdr_sig = sum(
        1 for r in results
        if r['spec'] == 'primary' and r.get('p_fdr', 1) < 0.05
    )
    print(f"Primary spec significant after FDR: {n_fdr_sig}/{len(UNCERTAINTY_MEASURES)}")

    # ========================================================================
    # Prepare Output
    # ========================================================================

    print("\n" + "=" * 60)
    print("Preparing Output")
    print("=" * 60)

    # Save regression results
    results_file = save_regression_results(results, paths["output_dir"])
    stats["output"]["files"].append(results_file.name)
    stats["output"]["checksums"][results_file.name] = compute_file_checksum(results_file)

    # Generate and save report
    report = generate_h8_results_report(results, sample_stats, timestamp)
    report_file = save_results_report(report, paths["output_dir"])
    stats["output"]["files"].append(report_file.name)
    stats["output"]["checksums"][report_file.name] = compute_file_checksum(report_file)

    # Print report to console
    print("\n" + report)

    # ========================================================================
    # Finalize Statistics
    # ========================================================================

    end_time = time.perf_counter()
    end_iso = datetime.now().isoformat()
    mem_end = get_process_memory_mb()

    stats["timing"]["end_iso"] = end_iso
    stats["timing"]["duration_seconds"] = end_time - start_time
    stats["memory"]["end_mb"] = mem_end["rss_mb"]
    stats["memory"]["peak_mb"] = max(memory_readings)
    stats["memory"]["delta_mb"] = mem_end["rss_mb"] - mem_start["rss_mb"]
    stats["output"]["final_rows"] = len(results)  # Number of regression results

    # Store detailed results
    stats["results"] = results

    # ========================================================================
    # Write Stats
    # ========================================================================

    save_stats(stats, paths["output_dir"])
    print(f"\nSaved: stats.json")

    # ========================================================================
    # Summary
    # ========================================================================

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    print(f"H8 Takeover Regression completed")
    print(f"  Sample: {sample_stats['n_obs']:,} obs, {sample_stats['n_firms']:,} firms")
    print(f"  Takeover events: {sample_stats['n_takeovers']}")
    print(f"  Takeover rate: {sample_stats['takeover_rate']:.2%}")
    print(f"  Regressions: {stats['processing']['n_converged']}/{stats['processing']['n_regressions']} converged")
    print(f"  Significant (p < 0.05): {stats['processing']['n_significant']}")
    print(f"  After FDR: {n_fdr_sig}")

    print(f"\nOutputs saved to: {paths['output_dir']}")
    print(f"Log saved to: {paths['log_file']}")

    print_stats_summary(stats)

    print("\n" + "=" * 60)
    print("STEP 4.8 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
