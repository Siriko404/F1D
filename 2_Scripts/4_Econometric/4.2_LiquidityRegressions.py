#!/usr/bin/env python3
"""
==============================================================================
STEP 4.2: Liquidity Regressions (OLS and 2SLS)
==============================================================================
ID: 4.2_LiquidityRegressions
Description: Test whether CEO/Manager communication affects market liquidity
             around earnings calls using IV regression.

Purpose:
    Test whether CEO/Manager communication affects market liquidity around
    earnings calls. Uses CCCL shift_intensity_sale_ff48 as instrument for
    Q&A Uncertainty (time-varying). Clarity enters as exogenous control.

Structure:
    Phase 1: First Stage - Instrument Validity (Q&A Uncertainty ~ CCCL)
    Phase 2: OLS Regressions (no instrument)
    Phase 3: 2SLS Regressions (Q&A Uncertainty instrumented)

Key Variables:
    - ClarityRegime: CEO fixed effect from 4.1 (Manager model) - EXOGENOUS
    - ClarityCEO: CEO fixed effect from 4.1.1 (CEO-only model) - EXOGENOUS
    - Manager_QA_Uncertainty_pct: Time-varying - ENDOGENOUS (instrumented)
    - CEO_QA_Uncertainty_pct: Time-varying - ENDOGENOUS (instrumented)
    - shift_intensity_sale_ff48: FF48 sales-weighted CCCL instrument

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - 4_Outputs/3_Financial_Features/latest/market_variables_{year}.parquet
    - 4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet (Regime)
    - 4_Outputs/4.1.1_CeoClarity_CEO_Only/latest/ceo_clarity_scores.parquet (CEO)

Outputs:
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/first_stage_results.txt
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/ols_regime.txt
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/ols_ceo.txt
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/iv_regime.txt
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/iv_ceo.txt
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/model_diagnostics.csv
    - 4_Outputs/4.2_LiquidityRegressions/{timestamp}/report_step4_2.md

Deterministic: true
Dependencies:
    - Requires: Step 3.3
    - Uses: shared.regression_utils, shared.panel_ols, linearmodels

Author: Thesis Author
Date: 2026-02-11
==============================================================================
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

# Add parent directory to path for shared module imports
script_dir = Path(__file__).parent.parent
sys.path.insert(0, str(script_dir))

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")


try:
    from shared.path_utils import (
        OutputResolutionError,
        ensure_output_dir,
        get_latest_output_dir,
        validate_input_file,
        validate_output_path,
    )
except ImportError:
    import sys as _sys

    _script_dir = Path(__file__).parent.parent
    _sys.path.insert(0, str(_script_dir))
    from shared.path_utils import (
        OutputResolutionError,
        get_latest_output_dir,
    )

import warnings

from shared.regression_validation import (
    validate_columns,
    validate_sample_size,
)

try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    from linearmodels.iv import IV2SLS

    STATSMODELS_AVAILABLE = True
    LINEARMODELS_AVAILABLE = True
except ImportError as e:
    print(f"WARNING: Missing package: {e}")
    STATSMODELS_AVAILABLE = False
    LINEARMODELS_AVAILABLE = False

from shared.observability_utils import (
    DualWriter,
    print_stat,
    print_stats_summary,
    save_stats,
)

warnings.filterwarnings("ignore", category=FutureWarning)

# Configuration
# ==============================================================================

CONFIG = {
    "year_start": 2002,
    "year_end": 2018,
    "dep_vars": ["Delta_Amihud", "Delta_Corwin_Schultz"],
    "instrument": "shift_intensity_sale_ff48",
    "linguistic_controls": ["Analyst_QA_Uncertainty_pct", "Entire_All_Negative_pct"],
    "firm_controls": [
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
        "Size",
        "BM",
        "Lev",
        "ROA",
        "CurrentRatio",
        "RD_Intensity",
        "Volatility",
    ],
    "samples": {"Main": {"exclude_ff12": [8, 11]}},
}


def parse_arguments():
    """Parse command-line arguments for 4.2_LiquidityRegressions.py."""
    parser = argparse.ArgumentParser(
        description="""
STEP 4.2: Liquidity Regressions

Estimates liquidity regressions using CEO clarity scores as
independent variable. Tests whether CEO clarity affects
stock liquidity and trading costs.
        """.strip(),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and prerequisites without executing",
    )

    return parser.parse_args()


def check_prerequisites(root):
    """Validate all required inputs and prerequisite steps exist."""
    from shared.dependency_checker import validate_prerequisites

    required_files = {}

    required_steps = {
        "4.1_EstimateCeoClarity": "ceo_clarity_scores.parquet",
        "3.2_MarketVariables": "market_variables.parquet",
    }

    validate_prerequisites(required_files, required_steps)


# Data Loading
def load_all_data(root):
    """Load and merge all required data."""
    print("\n" + "=" * 60)
    print("Loading data")
    print("=" * 60)

    manifest_dir = get_latest_output_dir(
        root / "4_Outputs" / "1.0_BuildSampleManifest",
        required_file="master_sample_manifest.parquet",
    )
    manifest_path = manifest_dir / "master_sample_manifest.parquet"
    manifest = pd.read_parquet(
        manifest_path,
        columns=[
            "file_name",
            "gvkey",
            "start_date",
            "ceo_id",
            "ff12_code",
            "ff48_code",
        ],
    )
    manifest["year"] = pd.to_datetime(manifest["start_date"]).dt.year
    print(f"  Manifest: {len(manifest):,} calls")

    all_ling = []
    for year in range(CONFIG["year_start"], CONFIG["year_end"] + 1):
        try:
            lv_dir = get_latest_output_dir(
                root / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables",
                required_file=f"linguistic_variables_{year}.parquet",
            )
            lv_path = lv_dir / f"linguistic_variables_{year}.parquet"
            lv = pd.read_parquet(lv_path)
            all_ling.append(lv)
        except OutputResolutionError:
            continue
    ling = pd.concat(all_ling, ignore_index=True)
    ling_cols = [
        "file_name",
        "Manager_QA_Uncertainty_pct",
        "CEO_QA_Uncertainty_pct",
        "Manager_Pres_Uncertainty_pct",
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ]
    ling_cols = [c for c in ling_cols if c in ling.columns]
    ling = ling[ling_cols].drop_duplicates("file_name")
    print(f"  Linguistic: {len(ling):,} calls")

    all_fc = []
    for year in range(CONFIG["year_start"], CONFIG["year_end"] + 1):
        try:
            fc_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"firm_controls_{year}.parquet",
            )
            fc_path = fc_dir / f"firm_controls_{year}.parquet"
            fc = pd.read_parquet(fc_path)
            all_fc.append(fc)
        except OutputResolutionError:
            continue
    firm = pd.concat(all_fc, ignore_index=True)
    fc_cols = ["file_name"] + [c for c in CONFIG["firm_controls"] if c in firm.columns]
    fc_cols.append(
        "shift_intensity_sale_ff48"
    ) if "shift_intensity_sale_ff48" in firm.columns else None
    fc_cols = [c for c in fc_cols if c is not None and c in firm.columns]
    firm = firm[fc_cols].drop_duplicates("file_name")
    print(f"  Firm controls: {len(firm):,} calls")

    all_mv = []
    for year in range(CONFIG["year_start"], CONFIG["year_end"] + 1):
        try:
            mv_dir = get_latest_output_dir(
                root / "4_Outputs" / "3_Financial_Features",
                required_file=f"market_variables_{year}.parquet",
            )
            mv_path = mv_dir / f"market_variables_{year}.parquet"
            mv = pd.read_parquet(mv_path)
            all_mv.append(mv)
        except OutputResolutionError:
            continue
    market = pd.concat(all_mv, ignore_index=True)
    mv_cols = [
        "file_name",
        "Delta_Amihud",
        "Delta_Corwin_Schultz",
        "Volatility",
        "StockRet",
        "MarketRet",
        "Amihud",
        "Corwin_Schultz",
    ]
    mv_cols = [c for c in mv_cols if c in market.columns]
    market = market[mv_cols].drop_duplicates("file_name")
    print(f"  Market variables: {len(market):,} calls")

    try:
        regime_dir = get_latest_output_dir(
            root / "4_Outputs" / "4.1_CeoClarity",
            required_file="ceo_clarity_scores.parquet",
        )
        regime_path = regime_dir / "ceo_clarity_scores.parquet"
        regime_clarity = pd.read_parquet(
            regime_path, columns=["ceo_id", "ClarityCEO", "sample"]
        )
        regime_clarity = regime_clarity.rename(columns={"ClarityCEO": "ClarityRegime"})
        regime_clarity["ceo_id"] = regime_clarity["ceo_id"].astype(str)
        print(f"  Regime Clarity: {len(regime_clarity):,} CEOs")
    except OutputResolutionError:
        regime_clarity = pd.DataFrame()
        print("  WARNING: Regime Clarity not found")

    try:
        ceo_dir = get_latest_output_dir(
            root / "4_Outputs" / "4.1.1_CeoClarity_CEO_Only",
            required_file="ceo_clarity_scores.parquet",
        )
        ceo_path = ceo_dir / "ceo_clarity_scores.parquet"
        ceo_clarity = pd.read_parquet(
            ceo_path, columns=["ceo_id", "ClarityCEO", "sample"]
        )
        ceo_clarity["ceo_id"] = ceo_clarity["ceo_id"].astype(str)
        print(f"  CEO Clarity: {len(ceo_clarity):,} CEOs")
    except OutputResolutionError:
        ceo_clarity = pd.DataFrame()
        print("  WARNING: CEO Clarity not found")

    df = manifest.copy()
    df = df.merge(ling, on="file_name", how="left")
    df = df.merge(firm, on="file_name", how="left")
    df = df.merge(market, on="file_name", how="left")

    df["ceo_id"] = df["ceo_id"].astype(str)
    if len(regime_clarity) > 0:
        # Assign industry sample for clarity matching
        df["sample_clarity"] = "Main"
        df.loc[df["ff12_code"] == 11, "sample_clarity"] = "Finance"
        df.loc[df["ff12_code"] == 8, "sample_clarity"] = "Utility"
        df = df.merge(
            regime_clarity[["ceo_id", "ClarityRegime", "sample"]],
            left_on=["ceo_id", "sample_clarity"],
            right_on=["ceo_id", "sample"],
            how="left",
            suffixes=("", "_regime"),
        )
    if len(ceo_clarity) > 0:
        df = df.merge(
            ceo_clarity[["ceo_id", "ClarityCEO", "sample"]],
            left_on=["ceo_id", "sample_clarity"],
            right_on=["ceo_id", "sample"],
            how="left",
            suffixes=("", "_ceo"),
        )

    print(f"\n  Combined: {len(df):,} calls")
    print(f"  With ClarityRegime: {df['ClarityRegime'].notna().sum():,}")
    print(f"  With ClarityCEO: {df['ClarityCEO'].notna().sum():,}")
    print(f"  With Instrument: {df['shift_intensity_sale_ff48'].notna().sum():,}")
    print(f"  With Delta_Amihud: {df['Delta_Amihud'].notna().sum():,}")

    return df


# Phase 1: First Stage (Instrument Validity)
def run_first_stage(df, out_dir):
    """Test instrument relevance for Q&A Uncertainty."""
    print("\n" + "=" * 60)
    print("PHASE 1: First Stage - Instrument Validity")
    print("=" * 60)

    results = []
    output_lines = []
    output_lines.append("=" * 80)
    output_lines.append("FIRST STAGE REGRESSIONS: Instrument Validity")
    output_lines.append("Instrument: shift_intensity_sale_ff48")
    output_lines.append("=" * 80 + "\n")

    for endog_var, label in [
        ("Manager_QA_Uncertainty_pct", "Manager Q&A Uncertainty"),
        ("CEO_QA_Uncertainty_pct", "CEO Q&A Uncertainty"),
    ]:
        if endog_var not in df.columns:
            continue

        output_lines.append(f"\n--- Endogenous: {label} ---")

        controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
        controls = [c for c in controls if c in df.columns and c != endog_var]

        all_vars = [endog_var, CONFIG["instrument"]] + controls + ["year"]
        reg_df = df[all_vars].dropna().copy()

        if len(reg_df) < 100:
            output_lines.append(f"  Insufficient observations: {len(reg_df)}")
            continue

        reg_df["year"] = reg_df["year"].astype(str)
        formula = (
            f"{endog_var} ~ {CONFIG['instrument']} + "
            + " + ".join(controls)
            + " + C(year)"
        )

        # Validate regression data before estimation
        try:
            required_columns = [endog_var, CONFIG["instrument"]] + controls + ["year"]
            validate_columns(reg_df, required_columns)
            validate_sample_size(reg_df, min_observations=100)
        except Exception as e:
            output_lines.append(f"  ERROR: Validation failed: {e}")
            continue

        try:
            model = smf.ols(formula, data=reg_df).fit(cov_type="HC1")

            inst = CONFIG["instrument"]
            coef = model.params.get(inst, np.nan)
            t_stat = model.tvalues.get(inst, np.nan)
            p_val = model.pvalues.get(inst, np.nan)
            f_stat = t_stat**2

            output_lines.append(f"  N = {int(model.nobs):,}")
            output_lines.append(f"  R-squared = {model.rsquared:.4f}")
            output_lines.append(f"  Instrument coefficient: {coef:.6f}")
            output_lines.append(f"  t-statistic: {t_stat:.2f}")
            output_lines.append(f"  p-value: {p_val:.4f}")
            output_lines.append(f"  F-statistic: {f_stat:.2f}")

            if f_stat >= 10:
                output_lines.append("  [OK] Strong instrument (F >= 10)")
            else:
                output_lines.append("  [WEAK] Weak instrument (F < 10)")

            results.append(
                {
                    "Endogenous": label,
                    "N": int(model.nobs),
                    "R2": model.rsquared,
                    "Instrument_Coef": coef,
                    "Instrument_tstat": t_stat,
                    "Instrument_pval": p_val,
                    "F_stat": f_stat,
                    "Strong": f_stat >= 10,
                }
            )

            with open(out_dir / "first_stage_full.txt", "a") as f:
                f.write(f"\n{'=' * 80}\nEndogenous: {label}\n{'=' * 80}\n")
                f.write(model.summary().as_text())
                f.write("\n")

        except Exception as e:
            output_lines.append(f"  ERROR: {e}")

    with open(out_dir / "first_stage_results.txt", "w") as f:
        f.write("\n".join(output_lines))
    print("  Saved: first_stage_results.txt")

    return results


# Phase 2: OLS Regressions
def run_ols_regression(
    df, dep_var, clarity_var, uncertainty_var, pres_unc_var, sample_name, out_file
):
    """Run OLS regression (no instrument)."""
    other_controls = (
        [clarity_var, pres_unc_var]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
    )
    other_controls = [
        c for c in other_controls if c in df.columns and c != uncertainty_var
    ]

    all_vars = [dep_var, uncertainty_var] + other_controls + ["year"]
    all_vars = [v for v in all_vars if v in df.columns]
    reg_df = df[all_vars].dropna().copy()

    if len(reg_df) < 100:
        return None

    reg_df["year"] = reg_df["year"].astype(str)

    rhs = []
    if clarity_var in reg_df.columns:
        rhs.append(clarity_var)
    if uncertainty_var in reg_df.columns:
        rhs.append(uncertainty_var)
    rhs += [c for c in other_controls if c in reg_df.columns and c not in rhs]
    formula = f"{dep_var} ~ " + " + ".join(rhs) + " + C(year)"

    try:
        required_columns = (
            [dep_var, clarity_var, uncertainty_var] + other_controls + ["year"]
        )
        validate_columns(reg_df, required_columns)
        validate_sample_size(reg_df, min_observations=100)
    except Exception as e:
        print(f"  ERROR: Validation failed: {e}")
        return None

    try:
        model = smf.ols(formula, data=reg_df).fit(cov_type="HC1")

        # Save full results
        with open(out_file, "a") as f:
            f.write(
                f"\n{'=' * 80}\nSample: {sample_name}\nDependent: {dep_var}\n{'=' * 80}\n"
            )
            f.write(model.summary().as_text())
            f.write("\n")

        return {
            "Sample": sample_name,
            "DepVar": dep_var,
            "N": int(model.nobs),
            "R2": model.rsquared,
            "Clarity_coef": model.params.get(clarity_var, np.nan),
            "Clarity_pval": model.pvalues.get(clarity_var, np.nan),
            "Uncertainty_coef": model.params.get(uncertainty_var, np.nan),
            "Uncertainty_pval": model.pvalues.get(uncertainty_var, np.nan),
        }
    except Exception as e:
        print(f"  ERROR in OLS: {e}")
        return None


# Phase 3: 2SLS Regressions
def run_iv_regression(
    df, dep_var, clarity_var, uncertainty_var, pres_unc_var, sample_name, out_file
):
    """Run 2SLS regression with Q&A Uncertainty instrumented."""
    if not LINEARMODELS_AVAILABLE:
        print("  WARNING: linearmodels not available for IV regression")
        return None

    controls = (
        [clarity_var, pres_unc_var]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
    )
    controls = [c for c in controls if c in df.columns]

    all_vars = [dep_var, uncertainty_var, CONFIG["instrument"]] + controls + ["year"]
    all_vars = [v for v in all_vars if v in df.columns]
    reg_df = df[all_vars].dropna().copy()

    if len(reg_df) < 100:
        return None

    for col in reg_df.columns:
        if col != "year":
            reg_df[col] = pd.to_numeric(reg_df[col], errors="coerce").astype(np.float64)

    reg_df = reg_df.dropna()

    if len(reg_df) < 100:
        return None

    year_dummies = pd.get_dummies(
        reg_df["year"].astype(str), prefix="year", drop_first=True
    ).astype(np.float64)
    reg_df = pd.concat([reg_df.drop("year", axis=1), year_dummies], axis=1)

    try:
        required_columns = [dep_var, uncertainty_var, CONFIG["instrument"]] + controls
        validate_columns(reg_df, required_columns)
        validate_sample_size(reg_df, min_observations=100)
    except Exception as e:
        print(f"  ERROR: Validation failed: {e}")
        return None

    try:
        y = reg_df[dep_var].astype(np.float64)

        exog_cols = [c for c in controls if c in reg_df.columns]
        exog_cols += [c for c in year_dummies.columns]
        exog_data = reg_df[exog_cols].astype(np.float64)
        exog = sm.add_constant(exog_data)

        endog = reg_df[[uncertainty_var]].astype(np.float64)

        instruments = reg_df[[CONFIG["instrument"]]].astype(np.float64)

        # Run IV2SLS
        model = IV2SLS(y, exog, endog, instruments).fit(cov_type="robust")

        # Calculate KP F-stat (first stage F)
        first_stage = sm.OLS(
            endog,
            sm.add_constant(
                pd.concat(
                    [instruments, exog.drop("const", axis=1, errors="ignore")], axis=1
                )
            ),
        ).fit()
        kp_f = first_stage.fvalue

        # Save full results
        with open(out_file, "a") as f:
            f.write(
                f"\n{'=' * 80}\nSample: {sample_name}\nDependent: {dep_var}\nEndogenous: {uncertainty_var}\nInstrument: {CONFIG['instrument']}\n{'=' * 80}\n"
            )
            f.write(str(model.summary))
            f.write(f"\n\nKleibergen-Paap F-stat: {kp_f:.2f}")
            if kp_f < 10:
                f.write(" (WEAK)")
            f.write("\n")

        return {
            "Sample": sample_name,
            "DepVar": dep_var,
            "N": int(model.nobs),
            "R2": model.rsquared,
            "KP_F": kp_f,
            "Clarity_coef": model.params.get(clarity_var, np.nan),
            "Clarity_pval": model.pvalues.get(clarity_var, np.nan),
            "Uncertainty_coef": model.params.get(uncertainty_var, np.nan),
            "Uncertainty_pval": model.pvalues.get(uncertainty_var, np.nan),
        }
    except Exception as e:
        print(f"  ERROR in IV: {e}")
        return None


def main():
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    root = Path(__file__).resolve().parents[2]
    out_dir = root / "4_Outputs" / "4.2_LiquidityRegressions" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)
    log_dir = root / "3_Logs" / "4.2_LiquidityRegressions" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    stats = {
        "step_id": "4.2_LiquidityRegressions",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "regressions": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    log_path = log_dir / f"step4_2_{timestamp}.log"
    dual_writer = DualWriter(log_path)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.2: Liquidity Regressions")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    df = load_all_data(root)

    stats["input"]["total_rows"] = len(df)
    stats["input"]["total_columns"] = len(df.columns)
    print_stat("Input rows", value=len(df))

    first_stage_results = run_first_stage(df, out_dir)

    ols_regime_file = out_dir / "ols_regime.txt"
    ols_ceo_file = out_dir / "ols_ceo.txt"
    iv_regime_file = out_dir / "iv_regime.txt"
    iv_ceo_file = out_dir / "iv_ceo.txt"

    for f in [ols_regime_file, ols_ceo_file, iv_regime_file, iv_ceo_file]:
        with open(f, "w") as fh:
            fh.write(f"Generated: {timestamp}\n")

    all_results = []

    for sample_name, sample_filter in CONFIG["samples"].items():
        print(f"\n{'#' * 80}")
        print(f"# SAMPLE: {sample_name}")
        print(f"{'#' * 80}")

        # Filter sample
        if "exclude_ff12" in sample_filter and sample_filter["exclude_ff12"]:
            df_sample = df[~df["ff12_code"].isin(sample_filter["exclude_ff12"])].copy()
        elif "include_ff12" in sample_filter and sample_filter["include_ff12"]:
            df_sample = df[df["ff12_code"].isin(sample_filter["include_ff12"])].copy()
        else:
            df_sample = df.copy()

        print(f"  Sample size: {len(df_sample):,} calls")

        # Capture filter stats
        stats["processing"][f"{sample_name}_filtered"] = len(df) - len(df_sample)

        # Phase 2 & 3 for each dependent variable
        for dep_var in CONFIG["dep_vars"]:
            if dep_var not in df_sample.columns:
                continue

            print(f"\n  --- {dep_var} ---")

            # Regime model
            print("    Regime OLS...")
            res = run_ols_regression(
                df_sample,
                dep_var,
                "ClarityRegime",
                "Manager_QA_Uncertainty_pct",
                "Manager_Pres_Uncertainty_pct",
                sample_name,
                ols_regime_file,
            )
            if res:
                res["Model"] = "OLS"
                res["Type"] = "Regime"
                all_results.append(res)

            print("    Regime IV...")
            res = run_iv_regression(
                df_sample,
                dep_var,
                "ClarityRegime",
                "Manager_QA_Uncertainty_pct",
                "Manager_Pres_Uncertainty_pct",
                sample_name,
                iv_regime_file,
            )
            if res:
                res["Model"] = "IV"
                res["Type"] = "Regime"
                all_results.append(res)

            # CEO model
            print("    CEO OLS...")
            res = run_ols_regression(
                df_sample,
                dep_var,
                "ClarityCEO",
                "CEO_QA_Uncertainty_pct",
                "CEO_Pres_Uncertainty_pct",
                sample_name,
                ols_ceo_file,
            )
            if res:
                res["Model"] = "OLS"
                res["Type"] = "CEO"
                all_results.append(res)

            print("    CEO IV...")
            res = run_iv_regression(
                df_sample,
                dep_var,
                "ClarityCEO",
                "CEO_QA_Uncertainty_pct",
                "CEO_Pres_Uncertainty_pct",
                sample_name,
                iv_ceo_file,
            )
            if res:
                res["Model"] = "IV"
                res["Type"] = "CEO"
                all_results.append(res)

    if all_results:
        diag_df = pd.DataFrame(all_results)
        diag_df.to_csv(out_dir / "model_diagnostics.csv", index=False)
        print("\n  Saved: model_diagnostics.csv")

        # Capture regression stats
        stats["regressions"]["first_stage"] = len(first_stage_results)
        stats["regressions"]["ols"] = len(
            [r for r in all_results if r["Model"] == "OLS"]
        )
        stats["regressions"]["iv"] = len([r for r in all_results if r["Model"] == "IV"])

    report_lines = [
        "# Step 4.2: Liquidity Regression Results",
        "",
        f"**Generated:** {timestamp}",
        "",
        "## First Stage Summary",
        "",
    ]
    for fs in first_stage_results:
        report_lines.append(
            f"- {fs['Endogenous']}: F={fs['F_stat']:.2f} ({'Strong' if fs['Strong'] else 'Weak'})"
        )

    report_lines.append("")
    report_lines.append("## Model Results")
    report_lines.append("")

    if all_results:
        results_df = pd.DataFrame(all_results)
        report_lines.append(
            results_df[["Model", "Type", "Sample", "DepVar", "N", "R2"]].to_markdown(
                index=False
            )
        )

    with open(out_dir / "report_step4_2.md", "w") as f:
        f.write("\n".join(report_lines))
    print("  Saved: report_step4_2.md")

    duration = (datetime.now() - start_time).total_seconds()
    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")
    print(f"Models run: {len(all_results)}")

    stats["output"]["final_rows"] = (
        sum([len(df[~df["ff12_code"].isin(CONFIG["samples"]["Main"]["exclude_ff12"])])])
        if "Main" in CONFIG["samples"]
        else len(df)
    )
    stats["output"]["files"] = [
        "first_stage_results.txt",
        "ols_regime.txt",
        "ols_ceo.txt",
        "iv_regime.txt",
        "iv_ceo.txt",
        "model_diagnostics.csv",
        "report_step4_2.md",
    ]
    stats["timing"]["end_iso"] = datetime.now().isoformat()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    print_stats_summary(stats)
    save_stats(stats, out_dir)

    dual_writer.close()
    sys.stdout = dual_writer.terminal

    return 0


if __name__ == "__main__":
    args = parse_arguments()
    root = Path(__file__).parent.parent.parent

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        check_prerequisites(root)
        # validate_prerequisites already prints "[OK] All prerequisites validated"
        sys.exit(0)

    check_prerequisites(root)
    sys.exit(main())
