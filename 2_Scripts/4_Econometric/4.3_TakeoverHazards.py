#!/usr/bin/env python3
"""
==============================================================================
STEP 4.3: Takeover Hazards (Cox PH and Fine-Gray Competing Risks)
==============================================================================
Description: Analyzes how CEO Clarity and Q&A Uncertainty predict takeover
             probability using survival analysis.

Models:
    - Model 1: Cox Proportional Hazards (All Takeovers)
    - Model 2: Fine-Gray Competing Risks (Uninvited: Hostile + Unsolicited)
    - Model 3: Fine-Gray Competing Risks (Friendly: Friendly + Neutral)

Variables:
    - ClarityRegime: CEO Fixed Effect (time-invariant)
    - ClarityCEO: CEO-specific Fixed Effect
    - Manager_QA_Uncertainty_pct: Call-level vagueness

Inputs:
    - 4_Outputs/1.0_BuildSampleManifest/latest/master_sample_manifest.parquet
    - 4_Outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_*.parquet
    - 4_Outputs/4.1_CeoClarity/latest/ceo_clarity_scores.parquet
    - 4_Outputs/3_Financial_Features/latest/firm_controls_*.parquet
    - 1_Inputs/SDC/sdc-ma-merged.parquet

Outputs:
    - 4_Outputs/4.3_TakeoverHazards/TIMESTAMP/
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf

    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

# Import shared regression and reporting utilities
from shared.regression_utils import run_fixed_effects_ols
from shared.reporting_utils import (
    generate_regression_report,
    save_model_diagnostics,
    save_variable_reference,
)
from shared.symlink_utils import update_latest_link

from lifelines import CoxPHFitter
import warnings
import hashlib
import json

warnings.filterwarnings("ignore")

# ==============================================================================
# Configuration
# ==============================================================================

ROOT = Path(__file__).resolve().parents[2]

CONFIG = {
    # Key variables
    "clarity_var_regime": "ClarityRegime",
    "clarity_var_ceo": "ClarityCEO",
    "uncertainty_var": "Manager_QA_Uncertainty_pct",
    # Firm controls
    "firm_controls": ["Size", "BM", "Lev", "ROA"],
    # Observation window (days)
    "forward_window_days": 365,
    # Sample filter (exclude Finance and Utilities)
    "exclude_ff12": [8, 11],
}

# ==============================================================================
# Dual-write logging
# ==============================================================================


class DualWriter:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


# ==============================================================================
# Statistics Helpers
# ==============================================================================


def compute_file_checksum(filepath, algorithm="sha256"):
    """Compute checksum for a file."""
    h = hashlib.new(algorithm)
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting.

    Modes:
        - Delta mode (before/after): "  Label: 1,000 -> 800 (-20.0%)"
        - Value mode: "  Label: 1,000"
    """
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        if isinstance(v, float):
            print(f"{prefix}{label}: {v:,.2f}")
        elif isinstance(v, int):
            print(f"{prefix}{label}: {v:,}")
        else:
            print(f"{prefix}{label}: {v}")


def analyze_missing_values(df):
    """Analyze missing values per column."""
    missing = {}
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            missing[col] = {
                "count": int(null_count),
                "percent": round(null_count / len(df) * 100, 2),
            }
    return missing


def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)

    inp = stats["input"]
    out = stats["output"]
    delta = inp["total_rows"] - out["final_rows"]
    delta_pct = (delta / inp["total_rows"] * 100) if inp["total_rows"] > 0 else 0

    print(f"\n{'Metric':<25} {'Value':>15}")
    print("-" * 42)
    print(f"{'Input Rows':<25} {inp['total_rows']:>15,}")
    print(f"{'Output Rows':<25} {out['final_rows']:>15,}")
    print(f"{'Rows Removed':<25} {delta:>15,}")
    print(f"{'Removal Rate':<25} {delta_pct:>14.1f}%")
    print(f"{'Duration (seconds)':<25} {stats['timing']['duration_seconds']:>15.2f}")

    if stats["processing"]:
        print(f"\n{'Processing Step':<30} {'Removed':>10}")
        print("-" * 42)
        for step, count in stats["processing"].items():
            print(f"{step:<30} {count:>10,}")

    if stats.get("survival_models"):
        print(f"\n{'Survival Models':<30} {'Count':>10}")
        print("-" * 42)
        for model_type, count in stats["survival_models"].items():
            print(f"{model_type:<30} {count:>10,}")

    print("=" * 60)


def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / "stats.json"
    with open(stats_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: {stats_path.name}")


# ==============================================================================
# Data Loading
# ==============================================================================


class DualWriter:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, "w", encoding="utf-8")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def close(self):
        self.log.close()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_data():
    """Load and merge all required data sources."""
    print("=" * 60)
    print("Loading data")
    print("=" * 60)

    # 1. Manifest
    manifest_path = (
        ROOT
        / "4_Outputs"
        / "1.0_BuildSampleManifest"
        / "latest"
        / "master_sample_manifest.parquet"
    )
    df = pd.read_parquet(manifest_path)
    print(f"  Manifest: {len(df):,} calls")

    # Create CUSIP6 for SDC matching
    if "cusip" in df.columns:
        df["cusip6"] = df["cusip"].astype(str).str[:6]
    elif "ccm_cusip" in df.columns:
        df["cusip6"] = df["ccm_cusip"].astype(str).str[:6]
    else:
        df["cusip6"] = ""

    # 2. Linguistic Variables
    ling_dir = ROOT / "4_Outputs" / "2_Textual_Analysis" / "2.2_Variables" / "latest"
    ling_files = sorted(ling_dir.glob("linguistic_variables_*.parquet"))
    if ling_files:
        ling = pd.concat([pd.read_parquet(f) for f in ling_files], ignore_index=True)
        df = df.merge(
            ling.drop_duplicates("file_name"),
            on="file_name",
            how="left",
            suffixes=("", "_ling"),
        )
        print(
            f"  Linguistic: {ling['Manager_QA_Uncertainty_pct'].notna().sum():,} with Q&A Unc"
        )

    # 3. Firm Controls
    firm_dir = ROOT / "4_Outputs" / "3_Financial_Features" / "latest"
    firm_files = sorted(firm_dir.glob("firm_controls_*.parquet"))
    if firm_files:
        firm = pd.concat([pd.read_parquet(f) for f in firm_files], ignore_index=True)
        df = df.merge(
            firm.drop_duplicates("file_name"),
            on="file_name",
            how="left",
            suffixes=("", "_firm"),
        )
        print(f"  Firm Controls: {firm['Size'].notna().sum():,} with Size")

    # 4. CEO Clarity Scores (Regime)
    regime_path = (
        ROOT / "4_Outputs" / "4.1_CeoClarity" / "latest" / "ceo_clarity_scores.parquet"
    )
    if regime_path.exists():
        regime = pd.read_parquet(regime_path)
        # Create sample classification for matching
        df["sample_for_clarity"] = "Main"
        df.loc[df["ff12_code"] == 11, "sample_for_clarity"] = "Finance"
        df.loc[df["ff12_code"] == 8, "sample_for_clarity"] = "Utility"

        df["ceo_id"] = df["ceo_id"].astype(str)
        regime["ceo_id"] = regime["ceo_id"].astype(str)

        df = df.merge(
            regime[["ceo_id", "sample", "ClarityCEO"]].rename(
                columns={"ClarityCEO": "ClarityRegime"}
            ),
            left_on=["ceo_id", "sample_for_clarity"],
            right_on=["ceo_id", "sample"],
            how="left",
        )
        df.drop(columns=["sample"], inplace=True, errors="ignore")
        print(f"  ClarityRegime: {df['ClarityRegime'].notna().sum():,} calls")

    # 5. CEO Clarity Scores (CEO-only)
    ceo_path = (
        ROOT
        / "4_Outputs"
        / "4.1.1_CeoClarity_CEO_Only"
        / "latest"
        / "ceo_clarity_scores.parquet"
    )
    if ceo_path.exists():
        ceo_clarity = pd.read_parquet(ceo_path)
        ceo_clarity["ceo_id"] = ceo_clarity["ceo_id"].astype(str)
        df = df.merge(
            ceo_clarity[["ceo_id", "sample", "ClarityCEO"]],
            left_on=["ceo_id", "sample_for_clarity"],
            right_on=["ceo_id", "sample"],
            how="left",
        )
        df.drop(columns=["sample"], inplace=True, errors="ignore")
        print(f"  ClarityCEO: {df['ClarityCEO'].notna().sum():,} calls")

    # 6. SDC M&A Data - Multi-Tier Matching
    sdc_path = ROOT / "1_Inputs" / "SDC" / "sdc-ma-merged.parquet"
    if sdc_path.exists():
        sdc = pd.read_parquet(sdc_path)
        print(f"  SDC M&A: {len(sdc):,} total deals")

        # Filter to US public targets in our sample period
        sdc = sdc[sdc["Target Nation"] == "United States"]
        sdc = sdc[sdc["Target Public Status"] == "Public"]
        sdc["announce_date"] = pd.to_datetime(sdc["Date Announced"], errors="coerce")
        sdc = sdc[
            (sdc["announce_date"] >= "2002-01-01")
            & (sdc["announce_date"] <= "2018-12-31")
        ]
        print(f"  SDC (US Public 2002-2018): {len(sdc):,} deals")

        # Prepare SDC identifiers
        sdc = sdc.copy()
        sdc["target_cusip6"] = sdc["Target 6-digit CUSIP"].astype(str).str.strip()
        sdc["target_ticker"] = (
            sdc["Target Primary Ticker Symbol"].astype(str).str.upper().str.strip()
        )
        sdc["target_name_clean"] = (
            sdc["Target Full Name"].astype(str).str.upper().str.strip()
        )
        sdc["target_name_clean"] = sdc["target_name_clean"].str.replace(
            r"[^\w\s]", "", regex=True
        )
        sdc["announce_year"] = sdc["announce_date"].dt.year

        # Classify deal type (Uninvited = Hostile + Unsolicited; Friendly = Friendly + Neutral)
        sdc["deal_type"] = sdc["Deal Attitude"].apply(
            lambda x: "Uninvited"
            if str(x).lower() in ["hostile", "unsolicited"]
            else "Friendly"
        )

        # Prepare manifest identifiers
        df["start_date"] = pd.to_datetime(df["start_date"])
        df["call_year"] = df["start_date"].dt.year
        df["ticker_clean"] = df["company_ticker"].astype(str).str.upper().str.strip()
        df["name_clean"] = df["company_name"].astype(str).str.upper().str.strip()
        df["name_clean"] = df["name_clean"].str.replace(r"[^\w\s]", "", regex=True)

        # Build lookup sets
        ccm_cusips = set(df["cusip6"].unique())
        ccm_names = set(df["name_clean"].unique())

        # Build temporal ticker lookup (year -> set of tickers)
        from collections import defaultdict

        ticker_by_year = defaultdict(set)
        for _, row in df[["ticker_clean", "call_year"]].drop_duplicates().iterrows():
            ticker_by_year[row["call_year"]].add(row["ticker_clean"])

        # Multi-tier matching for SDC deals
        def match_sdc_to_ccm(row):
            """Return (matched_cusip6, match_type) or (None, None)"""
            # Tier 1: CUSIP6 exact match
            if row["target_cusip6"] in ccm_cusips:
                return row["target_cusip6"], "cusip"

            # Tier 2: Temporal ticker match (+/- 1 year)
            t = row["target_ticker"]
            y = row["announce_year"]
            if t and t != "NAN":
                for check_year in [y - 1, y, y + 1]:
                    if t in ticker_by_year.get(check_year, set()):
                        # Find matching cusip6 from manifest
                        matches = df[
                            (df["ticker_clean"] == t)
                            & (df["call_year"].between(y - 1, y + 1))
                        ]
                        if len(matches) > 0:
                            return matches.iloc[0]["cusip6"], "ticker"

            # Tier 3: Exact company name match (100% threshold)
            if row["target_name_clean"] in ccm_names:
                matches = df[df["name_clean"] == row["target_name_clean"]]
                if len(matches) > 0:
                    return matches.iloc[0]["cusip6"], "name"

            return None, None

        print("  Multi-tier SDC matching...")
        sdc[["matched_cusip6", "match_type"]] = sdc.apply(
            lambda row: pd.Series(match_sdc_to_ccm(row)), axis=1
        )

        # Report match statistics
        n_cusip = (sdc["match_type"] == "cusip").sum()
        n_ticker = (sdc["match_type"] == "ticker").sum()
        n_name = (sdc["match_type"] == "name").sum()
        n_total = sdc["matched_cusip6"].notna().sum()
        print(f"    Tier 1 (CUSIP6): {n_cusip} deals")
        print(f"    Tier 2 (Ticker): {n_ticker} deals")
        print(f"    Tier 3 (Exact Name): {n_name} deals")
        print(f"    Total Matched: {n_total} deals")

        # Match takeover events to calls
        df["Takeover"] = 0
        df["Takeover_Type"] = "None"

        matched_sdc = sdc[sdc["matched_cusip6"].notna()]
        matched_cusips = set(matched_sdc["matched_cusip6"].unique())

        print(f"  Matching {len(matched_sdc)} SDC deals to calls...")
        for cusip in matched_cusips:
            if pd.isna(cusip) or cusip == "":
                continue

            firm_calls_idx = df[df["cusip6"] == cusip].index
            firm_deals = matched_sdc[matched_sdc["matched_cusip6"] == cusip]

            if len(firm_deals) == 0:
                continue

            for idx in firm_calls_idx:
                call_date = df.loc[idx, "start_date"]
                window_end = call_date + pd.Timedelta(
                    days=CONFIG["forward_window_days"]
                )

                matching_deals = firm_deals[
                    (firm_deals["announce_date"] > call_date)
                    & (firm_deals["announce_date"] <= window_end)
                ]

                if len(matching_deals) > 0:
                    df.loc[idx, "Takeover"] = 1
                    df.loc[idx, "Takeover_Type"] = matching_deals.iloc[0]["deal_type"]

        print(f"  Takeover Events: {df['Takeover'].sum():,}")
        print(f"    Uninvited: {(df['Takeover_Type'] == 'Uninvited').sum():,}")
        print(f"    Friendly: {(df['Takeover_Type'] == 'Friendly').sum():,}")
    else:
        print(f"  WARNING: SDC file not found")
        df["Takeover"] = 0
        df["Takeover_Type"] = "None"

    # Create survival duration (in quarters within 1-year window)
    df["Duration"] = 4  # Default: survived full window
    df.loc[df["Takeover"] == 1, "Duration"] = 1  # Event occurred

    return df


# ==============================================================================
# Cox Proportional Hazards
# ==============================================================================


def run_cox_ph(df, event_col, covariates, title, out_file):
    """Run Cox Proportional Hazards model."""
    print(f"\n--- Cox PH: {title} ---")

    reg_df = df[["Duration", event_col] + covariates].dropna().copy()

    # Cast to float
    for c in reg_df.columns:
        reg_df[c] = pd.to_numeric(reg_df[c], errors="coerce")
    reg_df = reg_df.dropna()

    if len(reg_df) < 100:
        print(f"  Insufficient observations: {len(reg_df)}")
        return None

    n_events = int(reg_df[event_col].sum())
    if n_events < 10:
        print(f"  Insufficient events: {n_events}")
        return None

    print(f"  N = {len(reg_df):,}, Events = {n_events:,}")

    # Fit model
    cph = CoxPHFitter()
    cph.fit(reg_df, duration_col="Duration", event_col=event_col)

    print(f"  Concordance: {cph.concordance_index_:.4f}")

    # Write results
    with open(out_file, "a") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"{title}\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"N = {len(reg_df):,}, Events = {n_events:,}\n")
        f.write(f"Concordance Index: {cph.concordance_index_:.4f}\n\n")
        f.write(cph.summary.to_string())
        f.write("\n")

    # Print key results
    print(f"\n  Variable               HR        p-value")
    print(f"  {'-' * 45}")
    for var in covariates:
        if var in cph.summary.index:
            hr = cph.summary.loc[var, "exp(coef)"]
            p = cph.summary.loc[var, "p"]
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"  {var:20s} {hr:8.4f}   {p:.4f} {sig}")

    return cph


# ==============================================================================
# Fine-Gray Competing Risks
# ==============================================================================


def run_fine_gray(df, target_type, covariates, title, out_file):
    """
    Run Fine-Gray competing risks model.
    Uses simplified approach: extend duration for competing events.
    """
    print(f"\n--- Fine-Gray: {title} ---")

    reg_df = df[["Duration", "Takeover", "Takeover_Type"] + covariates].copy()

    # Cast to float
    for c in covariates:
        reg_df[c] = pd.to_numeric(reg_df[c], errors="coerce")
    reg_df = reg_df.dropna()

    if len(reg_df) < 100:
        print(f"  Insufficient observations: {len(reg_df)}")
        return None

    # Create event indicator for target type
    reg_df["Event"] = (reg_df["Takeover_Type"] == target_type).astype(int)
    n_events = int(reg_df["Event"].sum())

    if n_events < 10:
        print(f"  Insufficient events for {target_type}: {n_events}")
        return None

    # For competing events: extend duration (remain at risk)
    competing_type = "Friendly" if target_type == "Uninvited" else "Uninvited"
    reg_df["FG_Duration"] = reg_df["Duration"]
    competing_mask = reg_df["Takeover_Type"] == competing_type
    reg_df.loc[competing_mask, "FG_Duration"] = reg_df["Duration"].max() + 1

    print(f"  N = {len(reg_df):,}, Events ({target_type}) = {n_events:,}")

    # Fit model
    cph = CoxPHFitter()
    fit_df = reg_df[["FG_Duration", "Event"] + covariates]
    cph.fit(fit_df, duration_col="FG_Duration", event_col="Event")

    print(f"  Concordance: {cph.concordance_index_:.4f}")

    # Write results
    with open(out_file, "a") as f:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"{title}\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"N = {len(reg_df):,}, Events = {n_events:,}\n")
        f.write(f"Concordance Index: {cph.concordance_index_:.4f}\n\n")
        f.write(cph.summary.to_string())
        f.write("\n")

    # Print key results
    print(f"\n  Variable               SHR       p-value")
    print(f"  {'-' * 45}")
    for var in covariates:
        if var in cph.summary.index:
            hr = cph.summary.loc[var, "exp(coef)"]
            p = cph.summary.loc[var, "p"]
            sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
            print(f"  {var:20s} {hr:8.4f}   {p:.4f} {sig}")

    return cph


# ==============================================================================
# Main
# ==============================================================================


def main():
    start_time = datetime.now()
    start_iso = start_time.isoformat()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    # Setup output directories
    out_dir = ROOT / "4_Outputs" / "4.3_TakeoverHazards" / timestamp
    out_dir.mkdir(parents=True, exist_ok=True)

    log_dir = ROOT / "3_Logs" / "4.3_TakeoverHazards" / timestamp
    log_dir.mkdir(parents=True, exist_ok=True)

    # Initialize stats
    stats = {
        "step_id": "4.3_TakeoverHazards",
        "timestamp": timestamp,
        "input": {"files": [], "checksums": {}, "total_rows": 0, "total_columns": 0},
        "processing": {},
        "output": {"final_rows": 0, "final_columns": 0, "files": []},
        "missing_values": {},
        "survival_models": {},
        "timing": {"start_iso": start_iso, "end_iso": "", "duration_seconds": 0.0},
    }

    log_file = log_dir / f"step4_3_{timestamp}.log"
    dual_writer = DualWriter(log_file)
    sys.stdout = dual_writer

    print("=" * 80)
    print("STEP 4.3: Takeover Hazards")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load data
    df = load_data()

    # Capture input stats
    stats["input"]["total_rows"] = len(df)
    stats["input"]["total_columns"] = len(df.columns)
    print_stat("Input rows", value=len(df))

    # Filter to Main sample
    print("\n" + "=" * 60)
    print("Filtering to Main Sample")
    print("=" * 60)
    df_main = df[~df["ff12_code"].isin(CONFIG["exclude_ff12"])].copy()
    print(f"  Main Sample: {len(df_main):,} calls")
    print(f"  Takeovers: {df_main['Takeover'].sum():,}")
    print(f"    Uninvited: {(df_main['Takeover_Type'] == 'Uninvited').sum():,}")
    print(f"    Friendly: {(df_main['Takeover_Type'] == 'Friendly').sum():,}")

    # Capture filter stats
    stats["processing"]["sample_filter"] = len(df) - len(df_main)
    print_stat("Sample filtered rows", before=len(df), after=len(df_main))

    # Define covariates for Regime model
    covariates_regime = [
        CONFIG["clarity_var_regime"],
        CONFIG["uncertainty_var"],
    ] + CONFIG["firm_controls"]
    covariates_regime = [c for c in covariates_regime if c in df_main.columns]

    # Define covariates for CEO model
    covariates_ceo = [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]] + CONFIG[
        "firm_controls"
    ]
    covariates_ceo = [c for c in covariates_ceo if c in df_main.columns]

    results = []

    # ===========================================================================
    # MODEL 1: Cox PH - All Takeovers
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 1: Cox Proportional Hazards - All Takeovers")
    print("=" * 60)

    out_file = out_dir / "cox_ph_all.txt"
    out_file.write_text(f"Generated: {timestamp}\n")

    # Regime Model
    cph_all_regime = run_cox_ph(
        df_main,
        "Takeover",
        covariates_regime,
        "All Takeovers (Regime Clarity)",
        out_file,
    )
    if cph_all_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in cph_all_regime.summary.index:
                results.append(
                    {
                        "Model": "CPH_All",
                        "Type": "Regime",
                        "Variable": var,
                        "HR": cph_all_regime.summary.loc[var, "exp(coef)"],
                        "Coef": cph_all_regime.summary.loc[var, "coef"],
                        "Pval": cph_all_regime.summary.loc[var, "p"],
                        "N": int(cph_all_regime.event_observed.sum()),
                    }
                )

    # CEO Model
    cph_all_ceo = run_cox_ph(
        df_main, "Takeover", covariates_ceo, "All Takeovers (CEO Clarity)", out_file
    )
    if cph_all_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in cph_all_ceo.summary.index:
                results.append(
                    {
                        "Model": "CPH_All",
                        "Type": "CEO",
                        "Variable": var,
                        "HR": cph_all_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": cph_all_ceo.summary.loc[var, "coef"],
                        "Pval": cph_all_ceo.summary.loc[var, "p"],
                        "N": int(cph_all_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # MODEL 2: Fine-Gray - Uninvited (Hostile + Unsolicited)
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 2: Fine-Gray - Uninvited Takeovers")
    print("=" * 60)

    out_file_uninv = out_dir / "fine_gray_uninvited.txt"
    out_file_uninv.write_text(f"Generated: {timestamp}\n")

    fg_uninv_regime = run_fine_gray(
        df_main,
        "Uninvited",
        covariates_regime,
        "Uninvited (Regime Clarity)",
        out_file_uninv,
    )
    if fg_uninv_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in fg_uninv_regime.summary.index:
                results.append(
                    {
                        "Model": "FG_Uninvited",
                        "Type": "Regime",
                        "Variable": var,
                        "SHR": fg_uninv_regime.summary.loc[var, "exp(coef)"],
                        "Coef": fg_uninv_regime.summary.loc[var, "coef"],
                        "Pval": fg_uninv_regime.summary.loc[var, "p"],
                        "N": int(fg_uninv_regime.event_observed.sum()),
                    }
                )

    fg_uninv_ceo = run_fine_gray(
        df_main, "Uninvited", covariates_ceo, "Uninvited (CEO Clarity)", out_file_uninv
    )
    if fg_uninv_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in fg_uninv_ceo.summary.index:
                results.append(
                    {
                        "Model": "FG_Uninvited",
                        "Type": "CEO",
                        "Variable": var,
                        "SHR": fg_uninv_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": fg_uninv_ceo.summary.loc[var, "coef"],
                        "Pval": fg_uninv_ceo.summary.loc[var, "p"],
                        "N": int(fg_uninv_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # MODEL 3: Fine-Gray - Friendly (Friendly + Neutral)
    # ===========================================================================
    print("\n" + "=" * 60)
    print("MODEL 3: Fine-Gray - Friendly Takeovers")
    print("=" * 60)

    out_file_friend = out_dir / "fine_gray_friendly.txt"
    out_file_friend.write_text(f"Generated: {timestamp}\n")

    fg_friend_regime = run_fine_gray(
        df_main,
        "Friendly",
        covariates_regime,
        "Friendly (Regime Clarity)",
        out_file_friend,
    )
    if fg_friend_regime:
        for var in [CONFIG["clarity_var_regime"], CONFIG["uncertainty_var"]]:
            if var in fg_friend_regime.summary.index:
                results.append(
                    {
                        "Model": "FG_Friendly",
                        "Type": "Regime",
                        "Variable": var,
                        "SHR": fg_friend_regime.summary.loc[var, "exp(coef)"],
                        "Coef": fg_friend_regime.summary.loc[var, "coef"],
                        "Pval": fg_friend_regime.summary.loc[var, "p"],
                        "N": int(fg_friend_regime.event_observed.sum()),
                    }
                )

    fg_friend_ceo = run_fine_gray(
        df_main, "Friendly", covariates_ceo, "Friendly (CEO Clarity)", out_file_friend
    )
    if fg_friend_ceo:
        for var in [CONFIG["clarity_var_ceo"], CONFIG["uncertainty_var"]]:
            if var in fg_friend_ceo.summary.index:
                results.append(
                    {
                        "Model": "FG_Friendly",
                        "Type": "CEO",
                        "Variable": var,
                        "SHR": fg_friend_ceo.summary.loc[var, "exp(coef)"],
                        "Coef": fg_friend_ceo.summary.loc[var, "coef"],
                        "Pval": fg_friend_ceo.summary.loc[var, "p"],
                        "N": int(fg_friend_ceo.event_observed.sum()),
                    }
                )

    # ===========================================================================
    # Save Results
    # ===========================================================================
    print("\n" + "=" * 60)
    print("Saving Results")
    print("=" * 60)

    # Hazard ratios summary
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv(out_dir / "hazard_ratios.csv", index=False)
        print(f"  Saved: hazard_ratios.csv")

        # Capture survival model stats
        stats["survival_models"]["cox_ph_all"] = len(
            [r for r in results if r["Model"] == "CPH_All"]
        )
        stats["survival_models"]["fine_gray_uninvited"] = len(
            [r for r in results if r["Model"] == "FG_Uninvited"]
        )
        stats["survival_models"]["fine_gray_friendly"] = len(
            [r for r in results if r["Model"] == "FG_Friendly"]
        )

    # Event summary
    summary = {
        "Sample": "Main",
        "N_Calls": len(df_main),
        "N_Takeover": int(df_main["Takeover"].sum()),
        "N_Uninvited": int((df_main["Takeover_Type"] == "Uninvited").sum()),
        "N_Friendly": int((df_main["Takeover_Type"] == "Friendly").sum()),
        "Pct_Takeover": df_main["Takeover"].mean() * 100,
    }
    pd.DataFrame([summary]).to_csv(out_dir / "takeover_event_summary.csv", index=False)
    print(f"  Saved: takeover_event_summary.csv")

    # Update latest symlink
    update_latest_link(out_dir, out_dir.parent / "latest")
        print(f"  Created 'latest' copy")

    # Summary
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    # Final stats
    stats["output"]["final_rows"] = len(df_main)
    stats["output"]["final_columns"] = len(df_main.columns)
    stats["output"]["files"] = [
        "cox_ph_all.txt",
        "fine_gray_uninvited.txt",
        "fine_gray_friendly.txt",
        "hazard_ratios.csv",
        "takeover_event_summary.csv",
    ]
    stats["timing"]["end_iso"] = end_time.isoformat()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    # Save and print stats summary
    print_stats_summary(stats)
    save_stats(stats, out_dir)

    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == "__main__":
    main()
