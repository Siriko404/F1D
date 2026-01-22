#!/usr/bin/env python3
"""
==============================================================================
STEP 2.3c: Generate Report for Token Counts
==============================================================================
ID: 2.3c_GenerateReport
Description: Reads all f1d_call parquet files and generates markdown report
             with token statistics and distributions
Inputs:
    - 4_Outputs/2.3_TokenizeAndCount/latest/f1d_call_YYYY.parquet
Outputs:
    - 4_Outputs/2.3_TokenizeAndCount/latest/report_step_03.md
Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
import hashlib
import json
from collections import Counter

def load_config():
    """Load configuration from project.yaml"""
    config_path = Path(__file__).parent.parent / "config" / "project.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def calculate_file_hash(file_path):
    """Calculate SHA-256 hash of file"""
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(65536):
            sha256.update(chunk)
    return sha256.hexdigest()

def generate_report():
    """Generate markdown report"""
    config = load_config()
    root = Path(__file__).parent.parent

    # Find latest directory
    output_base = root / config['paths']['outputs'] / "2.3_TokenizeAndCount"
    latest_dir = output_base / "latest"

    if not latest_dir.exists():
        print("ERROR: Latest directory not found")
        sys.exit(1)

    # Collect all year parquet files
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    year_stats = {}
    total_docs = 0
    total_tokens = 0
    total_hits = 0
    all_top_tokens = Counter()

    for year in range(year_start, year_end + 1):
        year_file = latest_dir / f"f1d_call_{year}.parquet"
        if not year_file.exists():
            continue

        df = pd.read_parquet(year_file)

        # Calculate stats
        year_total_tokens = df['total_word_tokens'].sum()
        year_total_hits = df['Clarity_hits'].sum()
        year_avg_f1d = (year_total_hits / year_total_tokens * 100) if year_total_tokens > 0 else 0

        year_stats[year] = {
            'docs': len(df),
            'total_tokens': year_total_tokens,
            'total_hits': year_total_hits,
            'avg_f1d': year_avg_f1d,
            'min_f1d': df['f1d_pct'].min(),
            'median_f1d': df['f1d_pct'].median(),
            'max_f1d': df['f1d_pct'].max(),
            'file_size_mb': year_file.stat().st_size / (1024**2),
            'sha256': calculate_file_hash(year_file)
        }

        total_docs += len(df)
        total_tokens += year_total_tokens
        total_hits += year_total_hits

        # Collect top tokens
        for idx, row in df.iterrows():
            top5_value = row['top5_matches']
            if top5_value is not None and not (isinstance(top5_value, float) and pd.isna(top5_value)):
                try:
                    # Handle both string (JSON) and already-parsed formats
                    if isinstance(top5_value, str):
                        top5_list = json.loads(top5_value)
                    else:
                        # Already parsed as list/array of dicts
                        top5_list = top5_value

                    for item in top5_list:
                        all_top_tokens[item['token']] += item['count']
                except Exception as e:
                    pass

    # Overall F1D
    overall_f1d = (total_hits / total_tokens * 100) if total_tokens > 0 else 0

    # Get top 10 most frequent tokens globally
    top10_global = all_top_tokens.most_common(10)

    # Generate markdown report
    report_path = latest_dir / "report_step_03.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# STEP 03: Tokenize & Count - Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Process Version:** {config['project']['version']}\n")
        f.write(f"**Script:** 2.3_TokenizeAndCount (Hybrid Python-C++-Python)\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("Tokenized managerial Q&A text and counted LM Clarity dictionary matches:\n")
        f.write("1. Normalized text to uppercase ASCII\n")
        f.write("2. Tokenized using `[A-Z]+` pattern\n")
        f.write("3. Counted tokens matching Clarity dictionary (Uncertainty ∪ Weak_Modal)\n")
        f.write("4. Computed F1D percentage: Clarity_hits / total_word_tokens\n")
        f.write("5. Tracked top 5 most frequent matched tokens per document\n\n")

        f.write(f"**Total documents:** {total_docs:,}\n")
        f.write(f"**Total word tokens:** {total_tokens:,}\n")
        f.write(f"**Total Clarity hits:** {total_hits:,}\n")
        f.write(f"**Overall F1D:** {overall_f1d:.4f}%\n\n")
        f.write("---\n\n")

        f.write("## Year Statistics\n\n")
        f.write("| Year | Documents | Total Tokens | Clarity Hits | Avg F1D% | Min F1D% | Median F1D% | Max F1D% | File Size (MB) |\n")
        f.write("|------|----------:|-------------:|-------------:|---------:|---------:|------------:|---------:|---------------:|\n")

        for year in sorted(year_stats.keys()):
            stats = year_stats[year]
            f.write(f"| {year} | {stats['docs']:,} | {stats['total_tokens']:,} | {stats['total_hits']:,} | ")
            f.write(f"{stats['avg_f1d']:.4f} | {stats['min_f1d']:.4f} | {stats['median_f1d']:.4f} | ")
            f.write(f"{stats['max_f1d']:.4f} | {stats['file_size_mb']:.1f} |\n")

        f.write("\n---\n\n")

        f.write("## Top 10 Most Frequent Clarity Tokens (Global)\n\n")
        f.write("| Rank | Token | Total Count | % of All Hits |\n")
        f.write("|-----:|:------|------------:|--------------:|\n")

        for i, (token, count) in enumerate(top10_global, 1):
            pct = (count / total_hits * 100) if total_hits > 0 else 0
            f.write(f"| {i} | {token} | {count:,} | {pct:.2f}% |\n")

        f.write("\n---\n\n")

        f.write("## File Checksums (SHA-256)\n\n")
        for year in sorted(year_stats.keys()):
            f.write(f"**f1d_call_{year}.parquet:** `{year_stats[year]['sha256']}`\n\n")

        f.write("---\n\n")

        f.write("## Processing Details\n\n")
        f.write("**Method:** Hybrid Python-C++-Python pipeline\n\n")

        f.write("**Python (2.3a):**\n")
        f.write("- Convert Parquet to JSON Lines format\n")
        f.write("- Orchestrate C++ processing\n")
        f.write("- Convert output back to Parquet\n")
        f.write("- Aggregate quarters to years\n")
        f.write("- Manage temporary file cleanup\n\n")

        f.write("**C++ (2.3b):**\n")
        f.write("- Text normalization: uppercase + non-letters → spaces\n")
        f.write("- Tokenization: extract `[A-Z]+` pattern\n")
        f.write("- Dictionary matching: O(1) lookup via unordered_set\n")
        f.write("- Top 5 tracking: deterministic sorting (count DESC, token ASC)\n")
        f.write("- Pure stdlib implementation (no external dependencies)\n\n")

        f.write("**Dictionary:**\n")
        f.write("- LM Uncertainty ∪ Weak_Modal words\n")
        f.write("- 297 unique tokens\n")
        f.write("- Case-sensitive matching (all uppercase)\n\n")

        f.write("---\n\n")

        f.write("## Determinism\n\n")
        f.write("- Dictionary: loaded into unordered_set (deterministic iteration)\n")
        f.write("- Top 5: sorted by (count DESC, token ASC) for tie-breaking\n")
        f.write("- File processing: sequential quarter order (2002_Q1 → 2018_Q4)\n")
        f.write("- Output sorting: alphabetical by file_name\n")
        f.write("- Year aggregation: quarters concatenated in order, then sorted by file_name\n\n")

        f.write("---\n\n")
        f.write("**End of Report**\n")

    print(f"Report generated: {report_path}")
    return report_path

if __name__ == "__main__":
    generate_report()
