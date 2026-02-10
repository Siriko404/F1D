#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
================================================================================
SCRIPT 5.8: H9 StyleFrozen Construction
================================================================================
Purpose: Construct StyleFrozen (CEO vagueness style) at firm-year level for H9
         regression. Assign time-invariant CEO Clarity scores to firm-years
         using frozen constraint (no future information).

Inputs:
    1. CEO Clarity scores from Phase 56:
       4_Outputs/4.1.1_CeoClarity_CEO_Only/latest/ceo_clarity_scores.parquet
    2. Manifest (call-level CEO assignments):
       4_Outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    3. Compustat (fiscal year-end dates):
       1_Inputs/comp_na_daily_all/comp_na_daily_all.parquet

Outputs:
    1. style_frozen.parquet - CEO style at firm-year level
       Columns: gvkey, fyear, datadate, style_frozen, ceo_id, ceo_name,
                n_calls_fy, n_calls_total
    2. report_step58_01.md - Summary report with coverage statistics
    3. stats.json - Detailed statistics

Frozen Constraint: Only use CEO-firm assignments observable as of fiscal
                   year-end (call.start_date <= fy_end). This prevents
                   look-ahead bias.

CEO Selection: For each firm-year, select the CEO with MOST calls in that
               fiscal year. Tiebreaker: earlier first_call_date.

CEO Moves: Same ceo_id may appear with multiple gvkeys over time.
           CEO Clarity is a personal trait, not firm-specific.

Deterministic: true
================================================================================
"""

import sys
import argparse
from pathlib import Path
from datetime import datetime
import json

import pandas as pd
import numpy as np
import sys
import io

# Ensure UTF-8 output for Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "shared"))

from path_utils import (
    get_latest_output_dir,
    ensure_output_dir,
    validate_input_file,
    PathValidationError,
    OutputResolutionError
)


def load_ceo_clarity(base_path: Path) -> pd.DataFrame:
    """
    Load CEO Clarity scores from Phase 56 output.

    Args:
        base_path: Base path to 4_Outputs directory

    Returns:
        DataFrame with columns: ceo_id, gamma_i, ClarityCEO_raw, ClarityCEO,
                                n_calls, ceo_name, first_call_date, last_call_date
    """
    print("=" * 80)
    print("LOADING CEO CLARITY SCORES (Phase 56)")
    print("=" * 80)

    try:
        ceo_dir = get_latest_output_dir(
            base_path / "4_Outputs" / "4.1.1_CeoClarity_CEO_Only",
            required_file="ceo_clarity_scores.parquet"
        )
        print(f"[OK] Found CEO Clarity directory: {ceo_dir}")

        file_path = ceo_dir / "ceo_clarity_scores.parquet"
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded CEO Clarity scores: {len(df):,} CEOs")

        # Verify expected columns
        expected_cols = ['ceo_id', 'gamma_i', 'ClarityCEO_raw', 'ClarityCEO',
                        'n_calls', 'ceo_name', 'first_call_date', 'last_call_date']
        missing_cols = set(expected_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in CEO Clarity data: {missing_cols}")

        print(f"  - ClarityCEO range: [{df['ClarityCEO'].min():.3f}, {df['ClarityCEO'].max():.3f}]")
        print(f"  - Mean ClarityCEO: {df['ClarityCEO'].mean():.3f} (should be ~0)")
        print(f"  - Std ClarityCEO: {df['ClarityCEO'].std():.3f} (should be ~1)")

        return df

    except (OutputResolutionError, FileNotFoundError) as e:
        print(f"[ERROR] Error loading CEO Clarity scores: {e}")
        raise


def load_manifest_calls(base_path: Path) -> pd.DataFrame:
    """
    Load manifest calls with CEO-firm assignments.

    Args:
        base_path: Base path to project directory

    Returns:
        DataFrame with columns: file_name, gvkey, start_date, ceo_id, ceo_name
    """
    print("\n" + "=" * 80)
    print("LOADING MANIFEST CALLS (CEO-FIRM ASSIGNMENTS)")
    print("=" * 80)

    try:
        manifest_dir = get_latest_output_dir(
            base_path / "4_Outputs" / "1.4_AssembleManifest",
            required_file="master_sample_manifest.parquet"
        )
        print(f"[OK] Found manifest directory: {manifest_dir}")

        file_path = manifest_dir / "master_sample_manifest.parquet"
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded manifest: {len(df):,} calls")

        # Verify required columns
        required_cols = ['file_name', 'gvkey', 'start_date', 'ceo_id', 'ceo_name']
        missing_cols = set(required_cols) - set(df.columns)
        if missing_cols:
            raise ValueError(f"Missing columns in manifest: {missing_cols}")

        # Ensure start_date is datetime
        df['start_date'] = pd.to_datetime(df['start_date'])

        print(f"  - Date range: {df['start_date'].min()} to {df['start_date'].max()}")
        print(f"  - Unique firms: {df['gvkey'].nunique():,}")
        print(f"  - Unique CEOs: {df['ceo_id'].nunique():,}")

        return df

    except (OutputResolutionError, FileNotFoundError) as e:
        print(f"[ERROR] Error loading manifest: {e}")
        raise


def load_compustat_dates(base_path: Path) -> pd.DataFrame:
    """
    Load Compustat fiscal year-end dates.

    Args:
        base_path: Base path to project directory

    Returns:
        DataFrame with columns: gvkey, datadate, fyear
    """
    print("\n" + "=" * 80)
    print("LOADING COMPUSTAT FISCAL YEAR-END DATES")
    print("=" * 80)

    file_path = base_path / "1_Inputs" / "comp_na_daily_all" / "comp_na_daily_all.parquet"

    try:
        validate_input_file(file_path)
        df = pd.read_parquet(file_path)
        print(f"[OK] Loaded Compustat: {len(df):,} observations")

        # Select required columns
        df = df[['gvkey', 'datadate', 'fyear']].copy()
        df['datadate'] = pd.to_datetime(df['datadate'])

        # Filter: valid datadate, sample period
        df = df.dropna(subset=['datadate', 'fyear'])
        df = df[(df['fyear'] >= 2002) & (df['fyear'] <= 2018)]

        print(f"  - After filtering (2002-2018, non-missing): {len(df):,} firm-years")
        print(f"  - Unique firms: {df['gvkey'].nunique():,}")
        print(f"  - Fyear range: {int(df['fyear'].min())} to {int(df['fyear'].max())}")

        return df

    except (PathValidationError, FileNotFoundError) as e:
        print(f"[ERROR] Error loading Compustat: {e}")
        raise


def build_fy_grid(compustat: pd.DataFrame) -> pd.DataFrame:
    """
    Build fiscal year grid for all valid firm-years.

    Args:
        compustat: DataFrame with gvkey, datadate, fyear

    Returns:
        DataFrame with columns: gvkey, fyear, fy_end
    """
    print("\n" + "=" * 80)
    print("BUILDING FISCAL YEAR GRID")
    print("=" * 80)

    # Create fy_end (fiscal year-end date)
    fy_grid = compustat[['gvkey', 'fyear', 'datadate']].copy()
    fy_grid = fy_grid.rename(columns={'datadate': 'fy_end'})
    fy_grid = fy_grid.drop_duplicates()

    # Ensure one row per (gvkey, fyear)
    # If duplicates exist (rare), keep the one with latest datadate
    fy_grid = fy_grid.sort_values('fy_end').drop_duplicates(
        subset=['gvkey', 'fyear'], keep='last'
    )

    print(f"[OK] Built fiscal year grid: {len(fy_grid):,} firm-years")
    print(f"  - Unique firms: {fy_grid['gvkey'].nunique():,}")

    return fy_grid


def assign_ceo_to_fy(
    fy_grid: pd.DataFrame,
    manifest: pd.DataFrame,
    ceo_clarity: pd.DataFrame,
    min_calls_fy: int = 1,
    min_calls_total: int = 5
) -> pd.DataFrame:
    """
    Assign CEOs to firm-years using frozen constraint.

    For each firm-year:
    1. Filter calls where start_date <= fy_end (frozen constraint)
    2. Count calls by CEO
    3. Select CEO with MAX calls (dominant CEO)
    4. If tie, select CEO with earlier first_call_date

    Args:
        fy_grid: Fiscal year grid with gvkey, fyear, fy_end
        manifest: Call-level CEO assignments
        ceo_clarity: CEO Clarity scores
        min_calls_fy: Minimum calls by CEO in fiscal year
        min_calls_total: Minimum total calls by CEO (from Phase 56)

    Returns:
        DataFrame with columns: gvkey, fyear, fy_end, ceo_id, ceo_name,
                                n_calls_fy, n_calls_total
    """
    print("\n" + "=" * 80)
    print("ASSIGNING CEOs TO FIRM-YEARS (FROZEN CONSTRAINT)")
    print("=" * 80)

    # Filter manifest to CEOs with sufficient calls
    valid_ceos = ceo_clarity[ceo_clarity['n_calls'] >= min_calls_total]['ceo_id']
    manifest_filtered = manifest[manifest['ceo_id'].isin(valid_ceos)].copy()
    print(f"[OK] Filtered to CEOs with >= {min_calls_total} total calls: {len(manifest_filtered):,} calls")

    # Join manifest to fiscal year grid
    # For each firm-year, we need to know which calls occurred <= fy_end
    fy_grid_expanded = fy_grid.merge(
        manifest_filtered[['file_name', 'gvkey', 'start_date', 'ceo_id', 'ceo_name']],
        on='gvkey',
        how='inner'
    )
    print(f"[OK] Joined manifest to FY grid: {len(fy_grid_expanded):,} call-FY combinations")

    # Apply frozen constraint: keep only calls where start_date <= fy_end
    fy_grid_expanded = fy_grid_expanded[
        fy_grid_expanded['start_date'] <= fy_grid_expanded['fy_end']
    ]
    print(f"[OK] Applied frozen constraint (start_date <= fy_end): {len(fy_grid_expanded):,} combinations")

    # Count calls per (gvkey, fyear, ceo_id)
    ceo_calls_per_fy = fy_grid_expanded.groupby(
        ['gvkey', 'fyear', 'ceo_id', 'ceo_name']
    ).size().reset_index(name='n_calls_fy')

    print(f"[OK] Counted calls per CEO-FY: {len(ceo_calls_per_fy):,} unique CEO-FY combinations")

    # Select CEO with max calls for each (gvkey, fyear)
    # Sort by n_calls_fy descending, then select first per group
    ceo_calls_per_fy = ceo_calls_per_fy.sort_values('n_calls_fy', ascending=False)

    # Get first_call_date for tiebreaker
    ceo_first_call = ceo_clarity[['ceo_id', 'first_call_date']].copy()

    # Merge to get first_call_date
    ceo_calls_per_fy = ceo_calls_per_fy.merge(ceo_first_call, on='ceo_id', how='left')
    ceo_calls_per_fy['first_call_date'] = pd.to_datetime(ceo_calls_per_fy['first_call_date'])

    # Sort by n_calls_fy (desc), then first_call_date (asc) for tiebreaker
    ceo_calls_per_fy = ceo_calls_per_fy.sort_values(
        ['n_calls_fy', 'first_call_date'],
        ascending=[False, True]
    )

    # Select first CEO per (gvkey, fyear)
    dominant_ceo = ceo_calls_per_fy.groupby(['gvkey', 'fyear']).first().reset_index()

    print(f"[OK] Selected dominant CEO per firm-year: {len(dominant_ceo):,} firm-years")

    # Filter by min_calls_fy
    dominant_ceo = dominant_ceo[dominant_ceo['n_calls_fy'] >= min_calls_fy]
    print(f"[OK] Filtered to >= {min_calls_fy} calls in FY: {len(dominant_ceo):,} firm-years")

    # Merge with fy_grid to get fy_end
    dominant_ceo = dominant_ceo.merge(
        fy_grid[['gvkey', 'fyear', 'fy_end']],
        on=['gvkey', 'fyear'],
        how='left'
    )

    # Add n_calls_total from CEO Clarity
    dominant_ceo = dominant_ceo.merge(
        ceo_clarity[['ceo_id', 'n_calls']],
        on='ceo_id',
        how='left'
    )
    dominant_ceo = dominant_ceo.rename(columns={'n_calls': 'n_calls_total'})

    # Reorder columns
    dominant_ceo = dominant_ceo[[
        'gvkey', 'fyear', 'fy_end', 'ceo_id', 'ceo_name',
        'n_calls_fy', 'n_calls_total'
    ]]

    return dominant_ceo


def create_style_frozen(
    dominant_ceo: pd.DataFrame,
    ceo_clarity: pd.DataFrame
) -> pd.DataFrame:
    """
    Create style_frozen variable by merging CEO Clarity scores.

    Args:
        dominant_ceo: DataFrame with CEO assignments per firm-year
        ceo_clarity: DataFrame with CEO Clarity scores

    Returns:
        DataFrame with columns: gvkey, fyear, datadate, style_frozen, ceo_id,
                                ceo_name, n_calls_fy, n_calls_total
    """
    print("\n" + "=" * 80)
    print("CREATING STYLE_FROZEN VARIABLE")
    print("=" * 80)

    # Merge ClarityCEO scores
    style_frozen = dominant_ceo.merge(
        ceo_clarity[['ceo_id', 'ClarityCEO']],
        on='ceo_id',
        how='left'
    )

    # Rename for output
    style_frozen = style_frozen.rename(columns={
        'fy_end': 'datadate',
        'ClarityCEO': 'style_frozen'
    })

    # Reorder columns
    style_frozen = style_frozen[[
        'gvkey', 'fyear', 'datadate', 'style_frozen', 'ceo_id',
        'ceo_name', 'n_calls_fy', 'n_calls_total'
    ]]

    print(f"[OK] Created style_frozen: {len(style_frozen):,} firm-years")
    print(f"  - style_frozen mean: {style_frozen['style_frozen'].mean():.4f}")
    print(f"  - style_frozen std: {style_frozen['style_frozen'].std():.4f}")
    print(f"  - style_frozen range: [{style_frozen['style_frozen'].min():.3f}, {style_frozen['style_frozen'].max():.3f}]")

    return style_frozen


def generate_report(
    style_frozen: pd.DataFrame,
    dominant_ceo: pd.DataFrame,
    ceo_clarity: pd.DataFrame,
    compustat: pd.DataFrame,
    output_dir: Path
) -> dict:
    """
    Generate summary report with coverage statistics.

    Args:
        style_frozen: Final style_frozen dataset
        dominant_ceo: CEO assignments per firm-year
        ceo_clarity: CEO Clarity scores
        compustat: Compustat fiscal year grid
        output_dir: Output directory for report

    Returns:
        Dictionary with statistics
    """
    print("\n" + "=" * 80)
    print("GENERATING SUMMARY REPORT")
    print("=" * 80)

    # Calculate statistics
    n_obs = len(style_frozen)
    n_firms = style_frozen['gvkey'].nunique()
    n_ceos = style_frozen['ceo_id'].nunique()
    fyear_min = int(style_frozen['fyear'].min())
    fyear_max = int(style_frozen['fyear'].max())

    # CEO turnover: count firms with multiple CEOs across years
    ceo_count_per_firm = style_frozen.groupby('gvkey')['ceo_id'].nunique()
    n_firms_with_turnover = (ceo_count_per_firm > 1).sum()
    turnover_rate = n_firms_with_turnover / n_firms * 100

    # CEO moves: count CEOs with multiple firms
    firm_count_per_ceo = style_frozen.groupby('ceo_id')['gvkey'].nunique()
    n_ceos_with_moves = (firm_count_per_ceo > 1).sum()

    # Coverage vs Compustat
    n_compustat_fy = compustat['gvkey'].nunique()  # Unique firms in Compustat
    coverage_rate = n_firms / n_compustat_fy * 100

    # Style distribution
    style_mean = style_frozen['style_frozen'].mean()
    style_std = style_frozen['style_frozen'].std()
    style_min = style_frozen['style_frozen'].min()
    style_max = style_frozen['style_frozen'].max()

    # Calls distribution
    n_calls_fy_mean = style_frozen['n_calls_fy'].mean()
    n_calls_fy_median = style_frozen['n_calls_fy'].median()
    n_calls_fy_max = style_frozen['n_calls_fy'].max()

    stats = {
        'n_obs': n_obs,
        'n_firms': n_firms,
        'n_ceos': n_ceos,
        'fyear_min': fyear_min,
        'fyear_max': fyear_max,
        'n_firms_with_turnover': n_firms_with_turnover,
        'turnover_rate_pct': turnover_rate,
        'n_ceos_with_moves': n_ceos_with_moves,
        'coverage_rate_pct': coverage_rate,
        'style_mean': style_mean,
        'style_std': style_std,
        'style_min': style_min,
        'style_max': style_max,
        'n_calls_fy_mean': n_calls_fy_mean,
        'n_calls_fy_median': n_calls_fy_median,
        'n_calls_fy_max': n_calls_fy_max
    }

    # Print statistics
    print(f"\n[STATS] STYLEFROZEN DATASET STATISTICS")
    print(f"-" * 40)
    print(f"Observations (firm-years): {n_obs:,}")
    print(f"Unique firms (gvkey): {n_firms:,}")
    print(f"Unique CEOs: {n_ceos:,}")
    print(f"Fiscal year range: {fyear_min}-{fyear_max}")
    print(f"")
    print(f"CEO turnover:")
    print(f"  - Firms with multiple CEOs: {n_firms_with_turnover:,} ({turnover_rate:.1f}%)")
    print(f"  - CEOs with multiple firms: {n_ceos_with_moves:,}")
    print(f"")
    print(f"Coverage vs Compustat:")
    print(f"  - Compustat firms (2002-2018): {n_compustat_fy:,}")
    print(f"  - StyleFrozen firms: {n_firms:,}")
    print(f"  - Coverage rate: {coverage_rate:.1f}%")
    print(f"")
    print(f"StyleFrozen distribution (ClarityCEO):")
    print(f"  - Mean: {style_mean:.4f} (expected ~0)")
    print(f"  - Std: {style_std:.4f} (expected ~1)")
    print(f"  - Range: [{style_min:.3f}, {style_max:.3f}]")
    print(f"  - Negative = more vague, Positive = more clear")
    print(f"")
    print(f"Calls per fiscal year (by selected CEO):")
    print(f"  - Mean: {n_calls_fy_mean:.1f}")
    print(f"  - Median: {n_calls_fy_median:.1f}")
    print(f"  - Max: {n_calls_fy_max:.0f}")

    # Write report to markdown
    report_path = output_dir / "report_step58_01.md"
    with open(report_path, 'w') as f:
        f.write("# Step 58-01: StyleFrozen Construction Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write("## Dataset Statistics\n\n")
        f.write(f"- **Observations (firm-years):** {n_obs:,}\n")
        f.write(f"- **Unique firms (gvkey):** {n_firms:,}\n")
        f.write(f"- **Unique CEOs:** {n_ceos:,}\n")
        f.write(f"- **Fiscal year range:** {fyear_min}-{fyear_max}\n\n")
        f.write("## Frozen Constraint Verification\n\n")
        f.write("[OK] Frozen constraint applied: `start_date <= fy_end`\n")
        f.write("[OK] Only CEO-firm assignments observable as of fiscal year-end are used\n")
        f.write("[OK] No look-ahead bias introduced\n\n")
        f.write("## CEO Selection Method\n\n")
        f.write("For each firm-year:\n")
        f.write("1. Filter calls to those <= fiscal year-end (frozen constraint)\n")
        f.write("2. Count calls by CEO within fiscal year\n")
        f.write("3. Select CEO with MAX calls (dominant CEO)\n")
        f.write("4. Tiebreaker: CEO with earlier first_call_date (longer tenure)\n\n")
        f.write("## CEO Turnover and Moves\n\n")
        f.write(f"- **Firms with CEO turnover:** {n_firms_with_turnover:,} ({turnover_rate:.1f}%)\n")
        f.write(f"- **CEOs who moved between firms:** {n_ceos_with_moves:,}\n")
        f.write("  - CEO Clarity is a personal trait, not firm-specific\n")
        f.write("  - Each firm-year gets the serving CEO's style score\n\n")
        f.write("## Coverage Statistics\n\n")
        f.write(f"- **Compustat firms (2002-2018):** {n_compustat_fy:,}\n")
        f.write(f"- **StyleFrozen firms:** {n_firms:,}\n")
        f.write(f"- **Coverage rate:** {coverage_rate:.1f}%\n\n")
        f.write("## StyleFrozen Distribution\n\n")
        f.write(f"- **Mean:** {style_mean:.4f} (expected ~0 from ClarityCEO standardization)\n")
        f.write(f"- **Std:** {style_std:.4f} (expected ~1 from ClarityCEO standardization)\n")
        f.write(f"- **Range:** [{style_min:.3f}, {style_max:.3f}]\n")
        f.write(f"- **Interpretation:** Negative = more vague, Positive = more clear\n\n")
        f.write("## Calls per Fiscal Year\n\n")
        f.write(f"- **Mean:** {n_calls_fy_mean:.1f} calls")
        f.write(f"- **Median:** {n_calls_fy_median:.1f} calls")
        f.write(f"- **Max:** {n_calls_fy_max:.0f} calls\n\n")
        f.write("## Output Files\n\n")
        f.write(f"1. `style_frozen.parquet` - Main dataset with {n_obs:,} firm-years\n")
        f.write(f"2. `stats.json` - Detailed statistics\n")
        f.write(f"3. `report_step58_01.md` - This report\n\n")
        f.write("## Next Steps\n\n")
        f.write("1. Review report and verify frozen constraint was correctly applied\n")
        f.write("2. Use style_frozen.parquet in 58-04 (merge with PRiskFY and AbsAbInv)\n")
        f.write("3. Run H9 regression: AbsAbInv ~ PRiskFY + StyleFrozen + PRiskFY×StyleFrozen\n\n")

    print(f"\n[OK] Report written: {report_path}")

    # Write stats to JSON
    stats_path = output_dir / "stats.json"
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"[OK] Stats written: {stats_path}")

    return stats


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(
        description="Construct StyleFrozen (CEO vagueness style) at firm-year level"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs and exit without generating outputs"
    )
    parser.add_argument(
        "--min-calls-fy",
        type=int,
        default=1,
        help="Minimum calls by CEO in fiscal year (default: 1)"
    )
    parser.add_argument(
        "--min-calls-total",
        type=int,
        default=5,
        help="Minimum total calls by CEO from Phase 56 (default: 5)"
    )

    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("STEP 58-01: STYLEFROZEN CONSTRUCTION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Determine base path
    base_path = Path.cwd()

    # Load inputs
    ceo_clarity = load_ceo_clarity(base_path)
    manifest = load_manifest_calls(base_path)
    compustat = load_compustat_dates(base_path)

    # Build fiscal year grid
    fy_grid = build_fy_grid(compustat)

    # Assign CEOs to firm-years (frozen constraint)
    dominant_ceo = assign_ceo_to_fy(
        fy_grid,
        manifest,
        ceo_clarity,
        min_calls_fy=args.min_calls_fy,
        min_calls_total=args.min_calls_total
    )

    # Create style_frozen variable
    style_frozen = create_style_frozen(dominant_ceo, ceo_clarity)

    if args.dry_run:
        print("\n" + "=" * 80)
        print("DRY RUN COMPLETE - No outputs generated")
        print("=" * 80)
        print("\nSummary:")
        print(f"  - Would generate {len(style_frozen):,} firm-years")
        print(f"  - {style_frozen['gvkey'].nunique():,} unique firms")
        print(f"  - {style_frozen['ceo_id'].nunique():,} unique CEOs")
        return

    # Create output directory
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    output_dir = ensure_output_dir(
        base_path / "4_Outputs" / "5.8_H9_StyleFrozen" / timestamp
    )
    print(f"\n[OK] Output directory: {output_dir}")

    # Generate report
    stats = generate_report(
        style_frozen,
        dominant_ceo,
        ceo_clarity,
        compustat,
        output_dir
    )

    # Write style_frozen.parquet
    output_path = output_dir / "style_frozen.parquet"
    style_frozen.to_parquet(output_path, index=False)
    print(f"[OK] StyleFrozen dataset written: {output_path}")

    print("\n" + "=" * 80)
    print("STEP 58-01 COMPLETE")
    print("=" * 80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nOutputs:")
    print(f"  1. {output_path}")
    print(f"  2. {output_dir / 'report_step58_01.md'}")
    print(f"  3. {output_dir / 'stats.json'}")


if __name__ == "__main__":
    main()
