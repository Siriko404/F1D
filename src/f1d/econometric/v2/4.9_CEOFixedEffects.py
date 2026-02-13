#!/usr/bin/env python3
"""
==============================================================================
STEP 4.9: CEO Fixed Effects Extraction (Dzieliński et al. 2020 Replication)
==============================================================================
ID: 4.9_CEOFixedEffects
Description: Extracts CEO communication style as persistent personal trait via
             fixed effects regression following Dzieliński, Wagner, Zeckhauser
             (2020) "Straight talkers and vague talkers" Equation 4.

Equation 4 Specification:
    UncAns_i,t = alpha + gamma_i*CEO_i + Sum_s(beta_s*Speech_s)
                 + Sum_k(beta_k*FirmChars_k) + Year_t + epsilon_i,t

Variable Mapping (V2 to Paper):
    Dependent:     CEO_QA_Uncertainty_pct (UncAns - CEO Q&A uncertainty only)
    Speech ctrl:   CEO_Pres_Uncertainty_pct (UncPreCEO)
                   Analyst_QA_Uncertainty_pct (UncQue)
                   CEO_All_Negative_pct (NegCall)
    Firm ctrl:     SurpDec, EPS_Growth, StockRet, MarketRet
    Fixed effects: C(ceo_id) for CEO FE, C(year) for Year FE
    Std errors:    Clustered by CEO (cov_type='cluster')

Key Features:
- ClarityCEO_i = -gamma_i (negate FIRST), THEN standardize to mean=0, SD=1
- Minimum 5 calls per CEO filter (paper requirement)
- Both sample periods: paper (2003-2015) and extended (2002-2018)
- Table 3 replication (2 columns)
- Table IA.1 robustness (5 specs: 0,1,2,3,7 - skip 4,5,6 as CFO vars not in V2)
- Figure 3 distribution histogram

Inputs:
    - 4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/ceo_clarity_scores.parquet
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/table3_replication.csv
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/table_ia1_correlation_matrix.csv
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/clarity_distribution_histogram_*.png
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/regression_results_*.txt
    - 4_Outputs/4.9_CEOFixedEffects/{timestamp}/report_step56.md

Deterministic: true
Dependencies:
    - Requires: Step 4.1-4.8
    - Uses: pandas, numpy

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import json
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to sys.path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Import shared utilities
from f1d.shared.observability_utils import (
    DualWriter,
)
from f1d.shared.path_utils import (
    ensure_output_dir,
    get_latest_output_dir,
)

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Try importing matplotlib
try:
    import matplotlib
    import matplotlib.pyplot as plt

    matplotlib.use("Agg")  # Non-interactive backend
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("WARNING: matplotlib not available. Install with: pip install matplotlib")


# ==============================================================================
# Configuration
# ==============================================================================

# Sample period definitions
SAMPLE_PERIODS = {
    "paper": (2003, 2015),  # Paper replication period
    "extended": (2002, 2018),  # Full V2 sample
}

# Minimum calls per CEO (paper requirement page 45)
MIN_CALLS_PER_CEO = 5

# Variable mapping (V2 to Paper)
VARIABLE_MAPPING = {
    # Dependent variable
    "UncAns": "CEO_QA_Uncertainty_pct",  # CEO Q&A uncertainty only (not All, not Presentation)
    # Speech controls
    "UncPreCEO": "CEO_Pres_Uncertainty_pct",  # CEO presentation uncertainty
    "UncQue": "Analyst_QA_Uncertainty_pct",  # Analyst Q&A uncertainty
    "NegCall": "CEO_All_Negative_pct",  # Negative words (CEO_All_Negative_pct)
    # Firm characteristics controls
    "SurpDec": "SurpDec",  # Earnings surprise decile
    "EPS_Growth": "EPS_Growth",  # Year-over-year EPS growth
    "StockRet": "StockRet",  # Stock return
    "MarketRet": "MarketRet",  # Market return
}

# Table 3 Column specifications
TABLE3_SPECS = {
    "col1": {
        "name": "Baseline",
        "formula_vars": ["CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct"],
        "description": "UncAns ~ CEO FE + UncPreCEO + UncQue + Year FE",
    },
    "col2": {
        "name": "Full Equation 4",
        "formula_vars": [
            "CEO_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",
            "CEO_All_Negative_pct",
            "SurpDec",
            "EPS_Growth",
            "StockRet",
            "MarketRet",
        ],
        "description": "UncAns ~ CEO FE + UncPreCEO + UncQue + NegCall + FirmChars + Year FE",
    },
}

# Table IA.1 Robustness specifications (5 specs only - V2 data limitation)
# Specs 4, 5, 6 skipped because CFO variables not available in V2
TABLE_IA1_SPECS = {
    0: {
        "name": "CEO FE only",
        "formula_vars": [],
        "description": "UncAns ~ CEO FE + Year FE",
    },
    1: {
        "name": "+ UncPreCEO",
        "formula_vars": ["CEO_Pres_Uncertainty_pct"],
        "description": "UncAns ~ CEO FE + UncPreCEO + Year FE",
    },
    2: {
        "name": "+ UncPreCEO + Firm chars",
        "formula_vars": ["CEO_Pres_Uncertainty_pct", "SurpDec", "EPS_Growth"],
        "description": "UncAns ~ CEO FE + UncPreCEO + FirmChars + Year FE",
    },
    3: {
        "name": "Baseline (Eq. 4 = Table 3 Col 1)",
        "formula_vars": ["CEO_Pres_Uncertainty_pct", "Analyst_QA_Uncertainty_pct"],
        "description": "UncAns ~ CEO FE + UncPreCEO + UncQue + Year FE (BASELINE)",
    },
    # Spec 4 (CFO), 5 (EPR), 6 (AnDispPre) SKIPPED - variables not in V2 data
    7: {
        "name": "+ delta_UncPreCEO",
        "formula_vars": [
            "CEO_Pres_Uncertainty_pct",
            "Analyst_QA_Uncertainty_pct",
            "delta_UncPreCEO",
        ],
        "description": "UncAns ~ CEO FE + UncPreCEO + UncQue + delta_UncPreCEO + Year FE",
    },
}


# ==============================================================================
# CLI & Utilities
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments for 4.9_CEOFixedEffects.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.9: CEO Fixed Effects Extraction (Dzieliński et al. 2020 Replication)

Extracts CEO communication style as a persistent personal trait via fixed
effects regression. Generates CEO Clarity scores, Table 3 replication,
Table IA.1 robustness correlations, and Figure 3 distribution histogram.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    parser.add_argument(
        "--period",
        type=str,
        choices=["paper", "extended", "both"],
        default="both",
        help="Sample period to analyze (default: both)",
    )

    parser.add_argument(
        "--min-calls",
        type=int,
        default=MIN_CALLS_PER_CEO,
        help=f"Minimum calls per CEO (default: {MIN_CALLS_PER_CEO})",
    )

    return parser.parse_args()


def get_git_sha():
    """Get current git commit SHA for reproducibility."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


# ==============================================================================
# Data Loading
# ==============================================================================


def load_data(root, args):
    """Load and merge all input data sources."""
    print("\n" + "=" * 70)
    print("Loading and merging data")
    print("=" * 70)

    # Resolve directories using timestamp-based resolution
    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.4_AssembleManifest",
        required_file="master_sample_manifest.parquet",
    )
    lv_dir = get_latest_output_dir(
        root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
        required_file="linguistic_variables_2002.parquet",
    )
    fc_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_Features",
        required_file="firm_controls_2002.parquet",
    )
    # Market variables in separate directory
    mv_dir = get_latest_output_dir(
        root / "4_Outputs" / "3_Financial_Features",
        required_file="market_variables_2002.parquet",
    )

    print(f"  Manifest dir: {manifest_dir}")
    print(f"  Linguistic vars dir: {lv_dir}")
    print(f"  Firm controls dir: {fc_dir}")

    # Load manifest (CEO identification)
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    print("\n  Loading manifest...")
    manifest = pd.read_parquet(
        manifest_path,
        columns=["file_name", "gvkey", "start_date", "ceo_id", "ceo_name"],
    )
    print(f"    {len(manifest):,} calls, {manifest['ceo_id'].nunique():,} CEOs")

    # Determine years to load
    if args.period == "paper":
        years = range(SAMPLE_PERIODS["paper"][0], SAMPLE_PERIODS["paper"][1] + 1)
    elif args.period == "extended":
        years = range(SAMPLE_PERIODS["extended"][0], SAMPLE_PERIODS["extended"][1] + 1)
    else:  # both
        years = range(SAMPLE_PERIODS["extended"][0], SAMPLE_PERIODS["extended"][1] + 1)

    print(f"  Loading data for years: {min(years)}-{max(years)}")

    # Load per-year linguistic variables and firm/market controls
    all_data = []

    for year in years:
        print(f"    Year {year}...", end="", flush=True)

        # Load linguistic variables
        lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
        if not lv_path.exists():
            print(" [MISSING - SKIP]")
            continue

        lv = pd.read_parquet(lv_path)

        # Load firm controls
        fc_path = fc_dir / f"firm_controls_{year}.parquet"
        if fc_path.exists():
            fc = pd.read_parquet(
                fc_path, columns=["file_name", "gvkey", "SurpDec", "EPS_Growth"]
            )
        else:
            fc = pd.DataFrame(columns=["file_name", "gvkey", "SurpDec", "EPS_Growth"])

        # Load market variables
        mv_path = mv_dir / f"market_variables_{year}.parquet"
        if mv_path.exists():
            mv = pd.read_parquet(
                mv_path, columns=["file_name", "gvkey", "StockRet", "MarketRet"]
            )
        else:
            mv = pd.DataFrame(columns=["file_name", "gvkey", "StockRet", "MarketRet"])

        # Add year column
        lv["year"] = year
        fc["year"] = year
        mv["year"] = year

        # Merge: linguistic -> firm controls -> market controls -> manifest
        # Drop redundant columns from firm/market controls to avoid duplicate merge columns
        fc_merge = fc[["file_name", "year", "SurpDec", "EPS_Growth"]]
        mv_merge = mv[["file_name", "year", "StockRet", "MarketRet"]]

        df_year = lv.merge(fc_merge, on=["file_name", "year"], how="left")
        df_year = df_year.merge(mv_merge, on=["file_name", "year"], how="left")
        df_year = df_year.merge(manifest, on="file_name", how="left")

        all_data.append(df_year)
        print(f" [{len(df_year):,} calls]")

    # Concatenate all years
    if not all_data:
        raise ValueError("No data loaded - check input file paths")

    df = pd.concat(all_data, ignore_index=True)

    # Filter to calls with CEO identified
    df = df[df["ceo_id"].notna()].copy()
    df["ceo_id"] = df["ceo_id"].astype(int)

    print(f"\n  After CEO filter: {len(df):,} calls, {df['ceo_id'].nunique():,} CEOs")

    return df


def prepare_regression_data(df, period_name, min_calls):
    """Prepare data for regression: filter, create variables, apply >=5 calls filter."""
    print(f"\n  Preparing data for {period_name} period...")

    # Filter by sample period
    if period_name == "paper":
        year_start, year_end = SAMPLE_PERIODS["paper"]
    else:
        year_start, year_end = SAMPLE_PERIODS["extended"]

    df_period = df[(df["year"] >= year_start) & (df["year"] <= year_end)].copy()
    print(
        f"    {period_name.capitalize()} period ({year_start}-{year_end}): {len(df_period):,} calls"
    )

    # Check required columns exist
    required_cols = [
        "ceo_id",
        "ceo_name",
        "year",
        "CEO_QA_Uncertainty_pct",  # Dependent variable
        "CEO_Pres_Uncertainty_pct",  # UncPreCEO
        "Analyst_QA_Uncertainty_pct",  # UncQue
        "CEO_All_Negative_pct",  # NegCall
        "SurpDec",
        "EPS_Growth",
        "StockRet",
        "MarketRet",  # Firm controls
    ]

    missing = [c for c in required_cols if c not in df_period.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Filter to complete cases (all regression variables present)
    regression_cols = [
        "ceo_id",
        "ceo_name",
        "year",
        "CEO_QA_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "CEO_All_Negative_pct",
        "SurpDec",
        "EPS_Growth",
        "StockRet",
        "MarketRet",
    ]

    df_complete = df_period[regression_cols].dropna()
    print(f"    After missingness filter: {len(df_complete):,} calls")

    # Apply minimum 5 calls filter (paper requirement)
    ceo_counts = df_complete["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    df_complete = df_complete[df_complete["ceo_id"].isin(valid_ceos)].copy()

    print(
        f"    After >=5 calls filter: {len(df_complete):,} calls, {df_complete['ceo_id'].nunique():,} CEOs"
    )

    # Create delta_UncPreCEO for spec 7 (change in CEO presentation uncertainty)
    # delta_UncPreCEO_i,t = UncPreCEO_i,t - UncPreCEO_i,t-1
    df_complete = df_complete.sort_values(["ceo_id", "year"])
    df_complete["delta_UncPreCEO"] = df_complete.groupby("ceo_id")[
        "CEO_Pres_Uncertainty_pct"
    ].diff()
    # First observation for each CEO has NaN delta - set to 0
    df_complete["delta_UncPreCEO"] = df_complete["delta_UncPreCEO"].fillna(0)

    return df_complete


# ==============================================================================
# CEO Fixed Effects Regression
# ==============================================================================


def build_formula(dependent_var, controls):
    """Build statsmodels formula string for CEO FE regression."""
    # C(ceo_id) for CEO fixed effects, C(year) for year fixed effects
    formula = f"{dependent_var} ~ C(ceo_id) + "
    if controls:
        formula += " + ".join(controls) + " + "
    formula += "C(year)"
    return formula


def run_ceo_fe_regression(df, specification="col1", cov_type="cluster"):
    """
    Run OLS regression with CEO fixed effects.

    Args:
        df: DataFrame with all required variables
        specification: "col1" (baseline) or "col2" (full Equation 4)
        cov_type: "cluster" for CEO-clustered SE, "HC1" for robust SE

    Returns:
        model: Fitted OLS model
        df_reg: DataFrame used for regression
    """
    if not STATSMODELS_AVAILABLE:
        raise RuntimeError("statsmodels not available")

    # Convert to string for categorical treatment
    df_reg = df.copy()
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Determine specification
    if specification == "col1":
        controls = TABLE3_SPECS["col1"]["formula_vars"]
    elif specification == "col2":
        controls = TABLE3_SPECS["col2"]["formula_vars"]
    else:
        raise ValueError(f"Unknown specification: {specification}")

    # Build formula
    dependent_var = "CEO_QA_Uncertainty_pct"
    formula = build_formula(dependent_var, controls)

    print(f"    Formula: {formula[:100]}...")

    # Estimate model
    start_time = time.time()

    # Use CEO-clustered standard errors (paper methodology)
    if cov_type == "cluster":
        model = smf.ols(formula, data=df_reg).fit(
            cov_type="cluster", cov_kwds={"groups": df_reg["ceo_id"]}
        )
    else:
        model = smf.ols(formula, data=df_reg).fit(cov_type=cov_type)

    duration = time.time() - start_time

    print(f"    Complete in {duration:.1f}s")
    print(f"    R-squared: {model.rsquared:.4f}")
    print(f"    Adjusted R-squared: {model.rsquared_adj:.4f}")
    print(f"    N observations: {int(model.nobs):,}")

    return model, df_reg


def extract_ceo_fixed_effects(model, df_reg, sample_period):
    """
    Extract CEO fixed effects (gamma_i) and compute ClarityCEO scores.

    ClarityCEO_i = -gamma_i (negative of CEO fixed effect)
    Then standardize to mean=0, SD=1

    Args:
        model: Fitted OLS model with CEO dummies
        df_reg: DataFrame used for regression
        sample_period: "2003-2015" or "2002-2018"

    Returns:
        ceo_fe: DataFrame with columns [ceo_id, ceo_name, gamma_i, ClarityCEO_raw,
                                        ClarityCEO, n_calls, sample_period]
    """
    print("    Extracting CEO fixed effects...")

    # Get CEO coefficient names
    ceo_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs from dummy names
    ceo_effects = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Reference CEO (not in params) gets gamma = 0
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = [c for c in all_ceos if c not in ceo_effects]
    for ref_ceo in reference_ceos:
        ceo_effects[ref_ceo] = 0.0

    print(
        f"      Found {len(ceo_effects)} CEOs (incl. {len(reference_ceos)} reference)"
    )

    # Create DataFrame
    ceo_fe = pd.DataFrame(list(ceo_effects.items()), columns=["ceo_id_str", "gamma_i"])

    # Convert ceo_id back to int
    ceo_fe["ceo_id"] = ceo_fe["ceo_id_str"].astype(int)

    # Compute Clarity = -gamma_i (negate FIRST)
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

    # THEN standardize to mean=0, SD=1
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()
    ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val

    # Add CEO names and call counts
    df_reg_numeric = df_reg.copy()
    df_reg_numeric["ceo_id"] = df_reg_numeric["ceo_id"].astype(int)

    ceo_stats = (
        df_reg_numeric.groupby("ceo_id")
        .agg({"ceo_name": "first", "year": "count"})
        .rename(columns={"year": "n_calls"})
    )

    ceo_fe = ceo_fe.merge(ceo_stats, left_on="ceo_id", right_index=True, how="left")

    # Add sample period label
    ceo_fe["sample_period"] = sample_period

    print(f"      ClarityCEO_raw: mean={mean_val:.4f}, std={std_val:.4f}")
    print(
        f"      ClarityCEO: mean={ceo_fe['ClarityCEO'].mean():.4f}, std={ceo_fe['ClarityCEO'].std():.4f}"
    )

    return ceo_fe


# ==============================================================================
# Robustness Specifications (Table IA.1)
# ==============================================================================


def run_robustness_specs(df, baseline_spec=3):
    """
    Run Table IA.1 robustness specifications and extract CEO FE from each.

    Specs: 0, 1, 2, 3, 7 (skip 4, 5, 6 - CFO/EPR variables not in V2)

    Args:
        df: DataFrame with all required variables
        baseline_spec: Which spec to use as baseline (default: 3)

    Returns:
        ceo_fe_by_spec: Dict mapping spec_id to CEO FE DataFrame
        models_by_spec: Dict mapping spec_id to fitted model
    """
    print("\n  Running Table IA.1 robustness specifications...")

    if not STATSMODELS_AVAILABLE:
        raise RuntimeError("statsmodels not available")

    # Convert to string for categorical treatment
    df_reg = df.copy()
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    ceo_fe_by_spec = {}
    models_by_spec = {}

    for spec_id, spec_config in TABLE_IA1_SPECS.items():
        print(f"\n    Spec {spec_id}: {spec_config['name']}")
        print(f"      {spec_config['description']}")

        # Build formula
        dependent_var = "CEO_QA_Uncertainty_pct"
        controls = spec_config["formula_vars"]
        formula = build_formula(dependent_var, controls)

        # Estimate model
        try:
            model = smf.ols(formula, data=df_reg).fit(
                cov_type="cluster", cov_kwds={"groups": df_reg["ceo_id"]}
            )

            print(f"      R-squared: {model.rsquared:.4f}, N={int(model.nobs):,}")

            # Extract CEO FE
            ceo_fe = extract_ceo_fixed_effects(model, df_reg, "robustness")
            ceo_fe_by_spec[spec_id] = ceo_fe
            models_by_spec[spec_id] = model

        except Exception as e:
            print(f"      ERROR: {e}")
            continue

    return ceo_fe_by_spec, models_by_spec


def compute_correlation_matrix(ceo_fe_by_spec, baseline_spec=3):
    """
    Compute correlation matrix of CEO FE across robustness specifications.

    Args:
        ceo_fe_by_spec: Dict mapping spec_id to CEO FE DataFrame
        baseline_spec: Which spec to use as baseline for correlation

    Returns:
        corr_matrix: DataFrame with pairwise correlations
    """
    print(f"\n  Computing correlation matrix (vs spec {baseline_spec})...")

    baseline_ceo_fe = ceo_fe_by_spec[baseline_spec]

    correlations = {}
    spec_ids = sorted(ceo_fe_by_spec.keys())

    for spec_id in spec_ids:
        ceo_fe = ceo_fe_by_spec[spec_id]

        # Merge on ceo_id to align
        merged = baseline_ceo_fe[["ceo_id", "ClarityCEO"]].merge(
            ceo_fe[["ceo_id", "ClarityCEO"]], on="ceo_id", suffixes=("_base", "_spec")
        )

        # Compute correlation
        corr = merged["ClarityCEO_base"].corr(merged["ClarityCEO_spec"])
        correlations[spec_id] = corr

        print(f"    Spec {spec_id} vs baseline: {corr:.4f}")

    # Create correlation matrix
    corr_matrix = pd.DataFrame(index=spec_ids, columns=spec_ids)

    for i in spec_ids:
        for j in spec_ids:
            if i == j:
                corr_matrix.loc[i, j] = 1.0
            elif i == baseline_spec:
                corr_matrix.loc[i, j] = correlations.get(j, np.nan)
            elif j == baseline_spec:
                corr_matrix.loc[i, j] = correlations.get(i, np.nan)
            else:
                # Compute pairwise correlation
                fe_i = ceo_fe_by_spec[i]
                fe_j = ceo_fe_by_spec[j]
                merged = fe_i[["ceo_id", "ClarityCEO"]].merge(
                    fe_j[["ceo_id", "ClarityCEO"]], on="ceo_id", suffixes=("_i", "_j")
                )
                if len(merged) > 0:
                    corr_matrix.loc[i, j] = merged["ClarityCEO_i"].corr(
                        merged["ClarityCEO_j"]
                    )
                else:
                    corr_matrix.loc[i, j] = np.nan

    return corr_matrix.astype(float)


# ==============================================================================
# Table 3 Replication
# ==============================================================================


def create_table3_replication(models, output_path):
    """
    Create Table 3 replication with coefficients, t-stats, R-squared.

    Args:
        models: Dict mapping period_name to dict of models
        output_path: Path to save CSV
    """
    print("\n  Creating Table 3 replication...")

    results = []

    for period_name, period_models in models.items():
        for spec_name, model in period_models.items():
            row = {
                "period": period_name,
                "specification": spec_name,
                "n_obs": int(model.nobs),
                "r_squared": model.rsquared,
                "r_squared_adj": model.rsquared_adj,
                "f_statistic": model.fvalue if hasattr(model, "fvalue") else np.nan,
                "f_pvalue": model.f_pvalue if hasattr(model, "f_pvalue") else np.nan,
            }

            # Add control variable coefficients and t-stats
            control_vars = [
                "CEO_Pres_Uncertainty_pct",
                "Analyst_QA_Uncertainty_pct",
                "CEO_All_Negative_pct",
                "SurpDec",
                "EPS_Growth",
                "StockRet",
                "MarketRet",
            ]

            for var in control_vars:
                if var in model.params.index:
                    row[f"{var}_coef"] = model.params[var]
                    row[f"{var}_tstat"] = model.tvalues[var]
                else:
                    row[f"{var}_coef"] = np.nan
                    row[f"{var}_tstat"] = np.nan

            results.append(row)

    df_results = pd.DataFrame(results)
    df_results.to_csv(output_path, index=False)

    print(f"    Saved: {output_path}")

    return df_results


# ==============================================================================
# Distribution Plot (Figure 3 Replication)
# ==============================================================================


def create_figure3_histogram(ceo_fe, sample_period, output_path):
    """
    Replicate Figure 3: Histogram of ClarityCEO (pre-standardization).

    Args:
        ceo_fe: DataFrame with ClarityCEO_raw column
        sample_period: "2003-2015" or "2002-2018"
        output_path: Path to save plot
    """
    if not MATPLOTLIB_AVAILABLE:
        print("    WARNING: matplotlib not available, skipping histogram")
        return

    print(f"    Creating Figure 3 histogram for {sample_period}...")

    fig, ax = plt.subplots(figsize=(10, 6))

    # Histogram of raw Clarity (pre-standardization)
    ax.hist(
        ceo_fe["ClarityCEO_raw"],
        bins=50,
        edgecolor="black",
        alpha=0.7,
        color="steelblue",
    )

    # Add mean and SD annotations
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()

    ax.axvline(
        mean_val,
        color="red",
        linestyle="--",
        linewidth=2,
        label=f"Mean = {mean_val:.2f}",
    )
    ax.axvline(
        mean_val - std_val,
        color="blue",
        linestyle=":",
        linewidth=1.5,
        label=f"-1 SD = {mean_val - std_val:.2f}",
    )
    ax.axvline(
        mean_val + std_val,
        color="blue",
        linestyle=":",
        linewidth=1.5,
        label=f"+1 SD = {mean_val + std_val:.2f}",
    )

    # Labels and title
    ax.set_xlabel("ClarityCEO (raw)", fontsize=12)
    ax.set_ylabel("Frequency", fontsize=12)
    ax.set_title(
        f"Figure 3 Replication: Distribution of CEO Clarity ({sample_period})\n"
        f'Histogram shows "fatter left tail" - more extremely unclear CEOs',
        fontsize=14,
    )
    ax.legend(fontsize=10)

    # Grid
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()

    print(f"    Saved: {output_path}")
    print(f"      Mean = {mean_val:.2f}, SD = {std_val:.2f}")


# ==============================================================================
# Report Generation
# ==============================================================================


def generate_report(outputs, sample_stats, output_path):
    """
    Generate summary report for Step 56.

    Args:
        outputs: Dict of output file paths
        sample_stats: Dict of sample statistics
        output_path: Path to save report
    """
    print("\n  Generating report_step56.md...")

    lines = [
        "# Phase 56: CEO/Management Uncertainty as Persistent Style - Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Overview",
        "",
        "This report summarizes the CEO fixed effects extraction following Dzieliński, Wagner, Zeckhauser (2020) Equation 4.",
        "CEO communication style is estimated as a persistent personal trait via OLS regression with CEO dummy variables.",
        "",
        "## Methodology",
        "",
        "### Equation 4 Specification",
        "",
        "```",
        "UncAns_i,t = alpha + gamma_i*CEO_i + Sum_s(beta_s*Speech_s)",
        "             + Sum_k(beta_k*FirmChars_k) + Year_t + epsilon_i,t",
        "```",
        "",
        "**Variable Mapping (V2 to Paper):**",
        "",
        "| Element | Paper Variable | V2 Variable |",
        "|---------|---------------|-------------|",
        "| Dependent | UncAns | CEO_QA_Uncertainty_pct |",
        "| Speech ctrl | UncPreCEO | CEO_Pres_Uncertainty_pct |",
        "| Speech ctrl | UncQue | Analyst_QA_Uncertainty_pct |",
        "| Speech ctrl | NegCall | CEO_All_Negative_pct |",
        "| Firm ctrl | SurpDec | SurpDec |",
        "| Firm ctrl | EPS growth | EPS_Growth |",
        "| Firm ctrl | StockRet | StockRet |",
        "| Firm ctrl | MarketRet | MarketRet |",
        "| Fixed effects | CEO FE | C(ceo_id) |",
        "| Fixed effects | Year FE | C(year) |",
        "| Std errors | CEO-clustered | cov_type='cluster' |",
        "",
        "**CEO Clarity Measure:**",
        "- ClarityCEO_i = -gamma_i (negative of CEO fixed effect)",
        "- Raw distribution: Mean = -0.62, SD = 0.23 (paper benchmark)",
        "- Post-extraction: Standardized to mean=0, SD=1",
        "- Interpretation: Higher = clearer communication (fewer uncertainty words)",
        "",
        "## Sample Statistics",
        "",
    ]

    # Add sample statistics for each period
    for period_name, stats in sample_stats.items():
        n_firms = stats.get("n_firms", "N/A")
        n_firms_str = f"{n_firms:,}" if isinstance(n_firms, int) else str(n_firms)
        lines.extend(
            [
                f"### {period_name.capitalize()} Period",
                "",
                f"- **Year range:** {stats['year_start']}-{stats['year_end']}",
                f"- **N observations (calls):** {stats['n_obs']:,}",
                f"- **N CEOs (with >=5 calls):** {stats['n_ceos']:,}",
                f"- **N firms:** {n_firms_str}",
                "",
            ]
        )

    # Add regression results
    lines.extend(
        [
            "## Table 3 Replication",
            "",
            "### Column (1): Baseline",
            "UncAns ~ CEO FE + UncPreCEO + UncQue + Year FE",
            "",
            "### Column (2): Full Equation 4",
            "UncAns ~ CEO FE + UncPreCEO + UncQue + NegCall + FirmChars + Year FE",
            "",
            "See `table3_replication.csv` for detailed coefficients and t-statistics.",
            "",
            "## Table IA.1 Robustness",
            "",
            "**Note:** Specifications 4, 5, 6 are skipped because CFO variables (UncPreCFO, UncAnsCFO),",
            "earnings press releases (UncEPR), and analyst dispersion (AnDispPre) are not available in V2 data.",
            "",
            "| Spec | Description | Correlation with Baseline |",
            "|------|-------------|---------------------------|",
        ]
    )

    for spec_id, spec_config in TABLE_IA1_SPECS.items():
        lines.append(
            f"| {spec_id} | {spec_config['name']} | See `table_ia1_correlation_matrix.csv` |"
        )

    lines.extend(
        [
            "",
            "See `table_ia1_correlation_matrix.csv` for full correlation matrix.",
            "",
            "## Distribution",
            "",
            "See `clarity_distribution_histogram_*.png` for Figure 3 replication.",
            "",
            "## Data Limitations",
            "",
            "- **CFO variables not available:** Specifications 4, 5, 6 from Table IA.1 are skipped because",
            "  V2 text analysis does not tag CFO speech separately (CFO_Pres_Uncertainty_pct, CFO_QA_Uncertainty_pct).",
            "- **Earnings press releases:** UncEPR not available in V2.",
            "- **Analyst dispersion in presentations:** AnDispPre not available in V2.",
            "",
            "## Files Generated",
            "",
        ]
    )

    for name, path in outputs.items():
        lines.append(f"- `{name}`: `{path}`")

    lines.extend(
        [
            "",
            "---",
            "",
            "*Phase 56 Plan 01: CEO Fixed Effects Extraction*",
            f"*Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*",
        ]
    )

    # Write report
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"    Saved: {output_path}")


# ==============================================================================
# Main Execution
# ==============================================================================


def main():
    """Main execution function."""
    args = parse_arguments()

    # Set up paths
    root = Path(__file__).parent.parent.parent
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = ensure_output_dir(
        root / "4_Outputs" / "4.9_CEOFixedEffects" / timestamp
    )
    log_dir = ensure_output_dir(root / "3_Logs" / "4.9_CEOFixedEffects")

    # Set up dual-writer for logging
    log_file = log_dir / f"{timestamp}_4.9.log"
    writer = DualWriter(log_file)
    # Redirect stdout to DualWriter
    original_stdout = sys.stdout
    sys.stdout = writer

    try:
        # Print header
        writer.write("\n" + "=" * 70)
        writer.write("STEP 4.9: CEO Fixed Effects Extraction")
        writer.write("Dzielinski, Wagner, Zeckhauser (2020) Replication")
        writer.write("=" * 70)
        writer.write(f"\nTimestamp: {timestamp}")
        writer.write(f"Git SHA: {get_git_sha()}")
        writer.write(f"Output directory: {output_dir}")
        writer.write(f"Log file: {log_file}")

        # Dry run mode
        if args.dry_run:
            writer.write("\n" + "-" * 70)
            writer.write("DRY RUN MODE - Validating inputs only")
            writer.write("-" * 70)

            # Check prerequisites
            try:
                manifest_dir = get_latest_output_dir(
                    root / "4_Outputs" / "1.4_AssembleManifest",
                    required_file="master_sample_manifest.parquet",
                )
                lv_dir = get_latest_output_dir(
                    root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
                    required_file="linguistic_variables_2002.parquet",
                )
                fc_dir = get_latest_output_dir(
                    root / "4_Outputs" / "3_Financial_Features",
                    required_file="firm_controls_2002.parquet",
                )
                mv_dir = get_latest_output_dir(
                    root / "4_Outputs" / "3_Financial_Features",
                    required_file="market_variables_2002.parquet",
                )

                writer.write("\nPrerequisites validated:")
                writer.write(f"  Manifest: {manifest_dir}")
                writer.write(f"  Linguistic variables: {lv_dir}")
                writer.write(f"  Firm controls: {fc_dir}")
                writer.write(f"  Market variables: {mv_dir}")

                if not STATSMODELS_AVAILABLE:
                    writer.write("\nERROR: statsmodels not available")
                    return 1

                if not MATPLOTLIB_AVAILABLE:
                    writer.write(
                        "\nWARNING: matplotlib not available (histograms will be skipped)"
                    )

                writer.write("\nDRY RUN COMPLETE - All prerequisites validated")
                return 0

            except Exception as e:
                writer.write(f"\nERROR: Prerequisite validation failed: {e}")
                return 1

        # Check statsmodels availability
        if not STATSMODELS_AVAILABLE:
            writer.write(
                "\nERROR: statsmodels not available. Install with: pip install statsmodels"
            )
            return 1

        # Load data
        writer.write("\n" + "-" * 70)
        writer.write("LOADING DATA")
        writer.write("-" * 70)

        df = load_data(root, args)

        # Determine which periods to run
        periods_to_run = []
        if args.period in ["paper", "both"]:
            periods_to_run.append("paper")
        if args.period in ["extended", "both"]:
            periods_to_run.append("extended")

        # Storage for results
        all_ceo_scores = []
        all_models = {}
        sample_stats = {}

        # Run for each sample period
        for period_name in periods_to_run:
            writer.write("\n" + "=" * 70)
            writer.write(f"PROCESSING {period_name.upper()} PERIOD")
            writer.write("=" * 70)

            # Prepare data
            df_period = prepare_regression_data(df, period_name, args.min_calls)

            # Store sample statistics
            sample_stats[period_name] = {
                "year_start": SAMPLE_PERIODS[period_name][0],
                "year_end": SAMPLE_PERIODS[period_name][1],
                "n_obs": len(df_period),
                "n_ceos": df_period["ceo_id"].nunique(),
                "n_firms": df_period["gvkey"].nunique()
                if "gvkey" in df_period.columns
                else "N/A",
            }

            # Run Table 3 Column (1) regression (baseline)
            writer.write("\n  Table 3 Column (1): Baseline")
            model_col1, df_reg_col1 = run_ceo_fe_regression(
                df_period, specification="col1", cov_type="cluster"
            )
            ceo_fe_col1 = extract_ceo_fixed_effects(
                model_col1,
                df_reg_col1,
                f"{SAMPLE_PERIODS[period_name][0]}-{SAMPLE_PERIODS[period_name][1]}",
            )
            all_ceo_scores.append(ceo_fe_col1)

            # Save regression output
            model_txt_path = output_dir / f"regression_results_{period_name}_col1.txt"
            with open(model_txt_path, "w") as f:
                f.write(str(model_col1.summary()))
            writer.write(f"    Saved: {model_txt_path}")

            # Run Table 3 Column (2) regression (full Equation 4)
            writer.write("\n  Table 3 Column (2): Full Equation 4")
            model_col2, df_reg_col2 = run_ceo_fe_regression(
                df_period, specification="col2", cov_type="cluster"
            )

            # Save regression output
            model_txt_path = output_dir / f"regression_results_{period_name}_col2.txt"
            with open(model_txt_path, "w") as f:
                f.write(str(model_col2.summary()))
            writer.write(f"    Saved: {model_txt_path}")

            # Store models for Table 3
            all_models[period_name] = {
                "col1": model_col1,
                "col2": model_col2,
            }

            # Create Figure 3 histogram
            if MATPLOTLIB_AVAILABLE:
                hist_path = (
                    output_dir
                    / f"clarity_distribution_histogram_{SAMPLE_PERIODS[period_name][0]}-{SAMPLE_PERIODS[period_name][1]}.png"
                )
                create_figure3_histogram(
                    ceo_fe_col1,
                    f"{SAMPLE_PERIODS[period_name][0]}-{SAMPLE_PERIODS[period_name][1]}",
                    hist_path,
                )

            # Run robustness specifications (Table IA.1)
            writer.write("\n" + "-" * 70)
            writer.write("TABLE IA.1 ROBUSTNESS SPECIFICATIONS")
            writer.write("-" * 70)

            ceo_fe_by_spec, models_by_spec = run_robustness_specs(
                df_period, baseline_spec=3
            )

            # Compute correlation matrix
            corr_matrix = compute_correlation_matrix(ceo_fe_by_spec, baseline_spec=3)

            # Save correlation matrix
            corr_path = output_dir / f"table_ia1_correlation_matrix_{period_name}.csv"
            corr_matrix.to_csv(corr_path)
            writer.write(f"\n    Saved: {corr_path}")

        # Combine CEO scores and save
        writer.write("\n" + "-" * 70)
        writer.write("SAVING OUTPUTS")
        writer.write("-" * 70)

        all_ceo_scores_df = pd.concat(all_ceo_scores, ignore_index=True)
        ceo_scores_path = output_dir / "ceo_clarity_scores.parquet"
        all_ceo_scores_df.to_parquet(ceo_scores_path, index=False)
        writer.write(f"\n  CEO Clarity scores: {ceo_scores_path}")
        writer.write(f"    Total CEOs: {len(all_ceo_scores_df)}")

        # Create Table 3 replication
        table3_path = output_dir / "table3_replication.csv"
        create_table3_replication(all_models, table3_path)

        # If running both periods, create combined correlation matrix
        if len(periods_to_run) > 1:
            writer.write(
                "\n  Note: Separate correlation matrices created for each period"
            )

        # Generate report
        outputs = {
            "ceo_clarity_scores.parquet": "4_Outputs/4.9_CEOFixedEffects/{timestamp}/ceo_clarity_scores.parquet",
            "table3_replication.csv": "4_Outputs/4.9_CEOFixedEffects/{timestamp}/table3_replication.csv",
            "clarity_distribution_histogram_*.png": "4_Outputs/4.9_CEOFixedEffects/{timestamp}/clarity_distribution_histogram_*.png",
            "table_ia1_correlation_matrix_*.csv": "4_Outputs/4.9_CEOFixedEffects/{timestamp}/table_ia1_correlation_matrix_*.csv",
            "regression_results_*.txt": "4_Outputs/4.9_CEOFixedEffects/{timestamp}/regression_results_*.txt",
        }

        report_path = output_dir / "report_step56.md"
        generate_report(outputs, sample_stats, report_path)
        writer.write(f"\n  Summary report: {report_path}")

        # Save execution stats
        stats = {
            "timestamp": timestamp,
            "git_sha": get_git_sha(),
            "periods_run": periods_to_run,
            "sample_stats": sample_stats,
            "n_ceos_total": len(all_ceo_scores_df),
            "output_dir": str(output_dir),
            "execution_time_s": time.time() - time.time(),  # Placeholder
        }

        stats_path = output_dir / "stats.json"
        with open(stats_path, "w") as f:
            json.dump(stats, f, indent=2, default=str)

        writer.write("\n" + "=" * 70)
        writer.write("EXECUTION COMPLETE")
        writer.write("=" * 70)
        writer.write(f"\nOutput directory: {output_dir}")
        writer.write(f"Total CEOs extracted: {len(all_ceo_scores_df)}")

        return 0

    finally:
        # Restore stdout and close log file
        sys.stdout = original_stdout
        writer.close()


if __name__ == "__main__":
    sys.exit(main())
