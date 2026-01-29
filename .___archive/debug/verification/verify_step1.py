#!/usr/bin/env python3
"""
==============================================================================
VERIFY STEP 1: Sample Manifest Pipeline Verification (SCRIPT-LEVEL)
==============================================================================
Compares inputs vs outputs for EACH Step 1 script individually:
    - 1.1_CleanMetadata: Unified-info.parquet -> metadata_cleaned.parquet
    - 1.2_LinkEntities: metadata_cleaned + CCM -> metadata_linked.parquet
    - 1.3_BuildTenureMap: Execucomp -> tenure_monthly.parquet
    - 1.4_AssembleManifest: metadata_linked + tenure_monthly -> master_sample_manifest.parquet

Outputs results to VERIFICATION_REPORT.md in project root.
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import numpy as np

ROOT = Path(__file__).resolve().parents[2]

# ==============================================================================
# Summary Statistics Functions
# ==============================================================================

def get_column_stats(df, col):
    """Get comprehensive stats for a single column."""
    series = df[col]
    stats = {
        'column': col,
        'dtype': str(series.dtype),
        'count': len(series),
        'null_count': int(series.isna().sum()),
        'null_pct': round(series.isna().mean() * 100, 2)
    }
    
    if pd.api.types.is_numeric_dtype(series) and not pd.api.types.is_bool_dtype(series):
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                stats['min'] = float(non_null.min())
                stats['max'] = float(non_null.max())
                stats['mean'] = round(float(non_null.mean()), 4)
                stats['median'] = round(float(non_null.median()), 4)
                stats['std'] = round(float(non_null.std()), 4) if len(non_null) > 1 else 0
                stats['p25'] = round(float(non_null.quantile(0.25)), 4)
                stats['p75'] = round(float(non_null.quantile(0.75)), 4)
            except:
                stats['min'] = stats['max'] = stats['mean'] = stats['median'] = stats['std'] = None
                stats['p25'] = stats['p75'] = None
        else:
            stats['min'] = stats['max'] = stats['mean'] = stats['median'] = stats['std'] = None
            stats['p25'] = stats['p75'] = None
    else:
        stats['unique'] = int(series.nunique())
        top_vals = series.value_counts().head(5)
        stats['top_5'] = ', '.join([f"{v}({c})" for v, c in top_vals.items()])
    
    return stats


def stats_to_markdown(stats_list, numeric=True):
    """Convert stats list to markdown table."""
    if numeric:
        lines = ["| Column | Type | Count | Null% | Min | Max | Mean | Median | Std |",
                 "|:-------|:-----|------:|------:|----:|----:|-----:|-------:|----:|"]
        for s in stats_list:
            if 'min' in s:
                lines.append(f"| `{s['column']}` | {s['dtype']} | {s['count']:,} | {s['null_pct']}% | "
                           f"{s.get('min', 'N/A')} | {s.get('max', 'N/A')} | {s.get('mean', 'N/A')} | "
                           f"{s.get('median', 'N/A')} | {s.get('std', 'N/A')} |")
    else:
        lines = ["| Column | Type | Count | Null% | Unique | Top 5 Values |",
                 "|:-------|:-----|------:|------:|-------:|:-------------|"]
        for s in stats_list:
            if 'unique' in s:
                top5 = s.get('top_5', '')[:50] + '...' if len(s.get('top_5', '')) > 50 else s.get('top_5', '')
                lines.append(f"| `{s['column']}` | {s['dtype']} | {s['count']:,} | {s['null_pct']}% | "
                           f"{s.get('unique', 'N/A')} | {top5} |")
    return '\n'.join(lines)


def get_latest_run(base_dir):
    """Get the most recent timestamped subdirectory."""
    if not base_dir.exists():
        return None
    subdirs = [d for d in base_dir.iterdir() if d.is_dir() and d.name != 'latest']
    if not subdirs:
        return None
    return sorted(subdirs, key=lambda x: x.name)[-1]


def analyze_file(path, name, results):
    """Analyze a parquet file and append to results."""
    if not path.exists():
        results.append(f"\n**{name}:** FILE NOT FOUND ({path})")
        return None
    
    df = pd.read_parquet(path)
    results.append(f"\n**{name}:** {len(df):,} rows × {len(df.columns)} columns")
    
    # Split columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = [c for c in df.columns if c not in numeric_cols]
    
    if numeric_cols:
        results.append("\n**Numeric Columns:**")
        numeric_stats = [get_column_stats(df, c) for c in numeric_cols[:10]]
        results.append(stats_to_markdown(numeric_stats, numeric=True))
    
    if cat_cols:
        results.append("\n**Categorical Columns:**")
        cat_stats = [get_column_stats(df, c) for c in cat_cols[:10]]
        results.append(stats_to_markdown(cat_stats, numeric=False))
    
    return df


def compare_schemas(input_df, output_df, results):
    """Compare input vs output schema."""
    if input_df is None or output_df is None:
        return
    
    input_cols = set(input_df.columns)
    output_cols = set(output_df.columns)
    
    added = sorted(output_cols - input_cols)
    removed = sorted(input_cols - output_cols)
    
    results.append(f"\n**Schema Changes:**")
    results.append(f"- Rows: {len(input_df):,} → {len(output_df):,} ({len(output_df)/len(input_df)*100:.1f}% retained)")
    results.append(f"- Columns added ({len(added)}): {', '.join(added[:10])}{'...' if len(added) > 10 else ''}")
    results.append(f"- Columns removed ({len(removed)}): {', '.join(removed[:10])}{'...' if len(removed) > 10 else ''}")


# ==============================================================================
# Script-Level Verification
# ==============================================================================

def verify_script_1_1(results):
    """Verify 1.1_CleanMetadata: Unified-info -> metadata_cleaned"""
    results.append("\n---\n## Script 1.1: CleanMetadata")
    results.append("\n**Purpose:** Clean Unified-info, deduplicate, filter for earnings calls (event_type='1'), date range 2002-2018")
    
    # Input
    results.append("\n### INPUT: Unified-info.parquet")
    input_path = ROOT / '1_Inputs' / 'Unified-info.parquet'
    input_df = analyze_file(input_path, "Unified-info.parquet", results)
    
    # Output
    results.append("\n### OUTPUT: metadata_cleaned.parquet")
    output_dir = get_latest_run(ROOT / '4_Outputs' / 'OLD' / '1.1_CleanMetadata')
    output_path = output_dir / 'metadata_cleaned.parquet' if output_dir else None
    output_df = analyze_file(output_path, "metadata_cleaned.parquet", results) if output_path else None
    
    compare_schemas(input_df, output_df, results)
    
    print(f"  1.1_CleanMetadata: {len(input_df):,} -> {len(output_df) if output_df is not None else 0:,}")
    return input_df, output_df


def verify_script_1_2(results, prev_output):
    """Verify 1.2_LinkEntities: metadata_cleaned + CCM -> metadata_linked"""
    results.append("\n---\n## Script 1.2: LinkEntities")
    results.append("\n**Purpose:** Link metadata to Compustat/CRSP via GVKEY matching (PERMNO, CUSIP, fuzzy name)")
    
    # Input 1: metadata_cleaned (from 1.1)
    results.append("\n### INPUT 1: metadata_cleaned.parquet (from 1.1)")
    if prev_output is not None:
        results.append(f"\n**From previous step:** {len(prev_output):,} rows")
    
    # Input 2: CCM
    results.append("\n### INPUT 2: CRSPCompustat_CCM.parquet")
    ccm_path = ROOT / '1_Inputs' / 'CRSPCompustat_CCM' / 'CRSPCompustat_CCM.parquet'
    ccm_df = analyze_file(ccm_path, "CRSPCompustat_CCM.parquet", results)
    
    # Output
    results.append("\n### OUTPUT: metadata_linked.parquet")
    output_dir = get_latest_run(ROOT / '4_Outputs' / 'OLD' / '1.2_LinkEntities')
    output_path = output_dir / 'metadata_linked.parquet' if output_dir else None
    output_df = analyze_file(output_path, "metadata_linked.parquet", results) if output_path else None
    
    if prev_output is not None and output_df is not None:
        compare_schemas(prev_output, output_df, results)
        if 'gvkey' in output_df.columns:
            gvkey_coverage = output_df['gvkey'].notna().mean() * 100
            results.append(f"- **GVKEY match rate:** {gvkey_coverage:.1f}%")
    
    print(f"  1.2_LinkEntities: {len(prev_output) if prev_output is not None else 0:,} -> {len(output_df) if output_df is not None else 0:,}")
    return output_df


def verify_script_1_3(results):
    """Verify 1.3_BuildTenureMap: Execucomp -> tenure_monthly"""
    results.append("\n---\n## Script 1.3: BuildTenureMap")
    results.append("\n**Purpose:** Build CEO tenure map from Execucomp (identify CEO periods per GVKEY)")
    
    # Input: Execucomp
    results.append("\n### INPUT: comp_execucomp.parquet")
    exec_path = ROOT / '1_Inputs' / 'Execucomp' / 'comp_execucomp.parquet'
    input_df = analyze_file(exec_path, "comp_execucomp.parquet", results)
    
    # Output
    results.append("\n### OUTPUT: tenure_monthly.parquet")
    output_dir = get_latest_run(ROOT / '4_Outputs' / 'OLD' / '1.3_BuildTenureMap')
    output_path = output_dir / 'tenure_monthly.parquet' if output_dir else None
    output_df = analyze_file(output_path, "tenure_monthly.parquet", results) if output_path else None
    
    if input_df is not None and output_df is not None:
        results.append(f"\n**Transformation:** {len(input_df):,} exec records -> {len(output_df):,} tenure-month records")
        if 'ceo_id' in output_df.columns:
            unique_ceos = output_df['ceo_id'].nunique()
            results.append(f"- **Unique CEOs:** {unique_ceos:,}")
    
    print(f"  1.3_BuildTenureMap: {len(input_df) if input_df is not None else 0:,} -> {len(output_df) if output_df is not None else 0:,}")
    return output_df


def verify_script_1_4(results, linked_df, tenure_df):
    """Verify 1.4_AssembleManifest: metadata_linked + tenure_monthly -> master_sample_manifest"""
    results.append("\n---\n## Script 1.4: AssembleManifest")
    results.append("\n**Purpose:** Merge linked metadata with CEO tenure, filter to CEOs with 5+ calls")
    
    # Input 1: metadata_linked
    results.append("\n### INPUT 1: metadata_linked.parquet (from 1.2)")
    if linked_df is not None:
        results.append(f"\n**From Step 1.2:** {len(linked_df):,} rows")
    
    # Input 2: tenure_monthly
    results.append("\n### INPUT 2: tenure_monthly.parquet (from 1.3)")
    if tenure_df is not None:
        results.append(f"\n**From Step 1.3:** {len(tenure_df):,} rows")
    
    # Output
    results.append("\n### OUTPUT: master_sample_manifest.parquet")
    # Check both OLD and new location
    output_path = ROOT / '4_Outputs' / '1.0_BuildSampleManifest' / 'latest' / 'master_sample_manifest.parquet'
    if not output_path.exists():
        output_dir = get_latest_run(ROOT / '4_Outputs' / 'OLD' / '1.4_AssembleManifest')
        output_path = output_dir / 'master_sample_manifest.parquet' if output_dir else None
    
    output_df = analyze_file(output_path, "master_sample_manifest.parquet", results) if output_path and output_path.exists() else None
    
    if linked_df is not None and output_df is not None:
        compare_schemas(linked_df, output_df, results)
        if 'ceo_id' in output_df.columns:
            ceo_coverage = output_df['ceo_id'].notna().mean() * 100
            unique_ceos = output_df['ceo_id'].nunique()
            results.append(f"- **CEO ID coverage:** {ceo_coverage:.1f}%")
            results.append(f"- **Unique CEOs in sample:** {unique_ceos:,}")
    
    print(f"  1.4_AssembleManifest: {len(linked_df) if linked_df is not None else 0:,} -> {len(output_df) if output_df is not None else 0:,}")
    return output_df


# ==============================================================================
# Main
# ==============================================================================

def main():
    start_time = datetime.now()
    
    print("=" * 80)
    print("VERIFICATION: Step 1 - Sample Manifest Pipeline (SCRIPT-LEVEL)")
    print("=" * 80)
    print(f"Timestamp: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    results.append("# Step 1: Sample Manifest Pipeline Verification")
    results.append(f"\n**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    results.append("\nThis report verifies EACH SCRIPT in Step 1 individually, showing inputs → outputs.\n")
    
    # Verify each script
    input_df, cleaned_df = verify_script_1_1(results)
    linked_df = verify_script_1_2(results, cleaned_df)
    tenure_df = verify_script_1_3(results)
    manifest_df = verify_script_1_4(results, linked_df, tenure_df)
    
    # Summary
    results.append("\n---\n## Summary")
    results.append("\n| Script | Input Rows | Output Rows | Retention |")
    results.append("|:-------|----------:|----------:|----------:|")
    
    if input_df is not None and cleaned_df is not None:
        results.append(f"| 1.1_CleanMetadata | {len(input_df):,} | {len(cleaned_df):,} | {len(cleaned_df)/len(input_df)*100:.1f}% |")
    if cleaned_df is not None and linked_df is not None:
        results.append(f"| 1.2_LinkEntities | {len(cleaned_df):,} | {len(linked_df):,} | {len(linked_df)/len(cleaned_df)*100:.1f}% |")
    if linked_df is not None and manifest_df is not None:
        results.append(f"| 1.4_AssembleManifest | {len(linked_df):,} | {len(manifest_df):,} | {len(manifest_df)/len(linked_df)*100:.1f}% |")
    
    # Write report
    report_path = ROOT / 'VERIFICATION_REPORT.md'
    report_content = '\n'.join(results)
    
    # Create or update existing
    header = "# Pipeline Verification Report\n\n"
    header += f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    header += "---\n\n"
    
    report_path.write_text(header + report_content, encoding='utf-8')
    print(f"\nReport written to: {report_path}")
    
    duration = (datetime.now() - start_time).total_seconds()
    print(f"Duration: {duration:.1f} seconds")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
