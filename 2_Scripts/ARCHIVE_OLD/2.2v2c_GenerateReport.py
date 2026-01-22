#!/usr/bin/env python3
"""
==============================================================================
STEP 2.2v2c: Generate Report for QA Manager Docs
==============================================================================
ID: 2.2v2c_GenerateReport
Description: Reads all qa_manager_docs parquet files and generates markdown
             report with statistics
Inputs:
    - 4_Outputs/2.2v2_ExtractQaManagerDocs/latest/qa_manager_docs_YYYY_QX.parquet
Outputs:
    - 4_Outputs/2.2v2_ExtractQaManagerDocs/latest/report_step_02.md
Schema: file_name, doc_text, approx_char_len, start_date
Deterministic: true
==============================================================================
"""

import sys
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
import hashlib

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
    output_base = root / config['paths']['outputs'] / "2.2v2_ExtractQaManagerDocs"
    latest_dir = output_base / "latest"

    if not latest_dir.exists():
        print("ERROR: Latest directory not found")
        sys.exit(1)

    # Collect all year-quarter parquet files
    year_start = config['data']['year_start']
    year_end = config['data']['year_end']

    year_quarter_stats = {}
    year_totals = {}
    total_docs = 0
    total_chars = 0

    for year in range(year_start, year_end + 1):
        year_totals[year] = {'docs': 0, 'chars': 0, 'quarters': {}}

        for quarter in range(1, 5):
            parquet_file = latest_dir / f"qa_manager_docs_{year}_Q{quarter}.parquet"
            if not parquet_file.exists():
                continue

            df = pd.read_parquet(parquet_file)

            stats = {
                'docs': len(df),
                'avg_chars': int(df['approx_char_len'].mean()) if len(df) > 0 else 0,
                'median_chars': int(df['approx_char_len'].median()) if len(df) > 0 else 0,
                'max_chars': int(df['approx_char_len'].max()) if len(df) > 0 else 0,
                'file_size_mb': parquet_file.stat().st_size / (1024**2),
                'sha256': calculate_file_hash(parquet_file)
            }

            year_quarter_stats[(year, quarter)] = stats
            year_totals[year]['quarters'][quarter] = len(df)
            year_totals[year]['docs'] += len(df)
            year_totals[year]['chars'] += df['approx_char_len'].sum()

            total_docs += len(df)
            total_chars += df['approx_char_len'].sum()

    # Generate markdown report
    report_path = latest_dir / "report_step_02.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# STEP 02: Extract QA Manager Docs - Report\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"**Process Version:** {config['project']['version']}\n")
        f.write(f"**Script:** 2.2v2_ExtractQaManagerDocs (Hybrid Python-C++-Python)\n\n")
        f.write("---\n\n")

        f.write("## Summary\n\n")
        f.write("Extracted managerial Q&A text from earnings call transcripts:\n")
        f.write("1. Filtered speaker turns to Q&A context only\n")
        f.write("2. Identified managerial speakers using role keywords and employer matching\n")
        f.write("3. Excluded non-managerial speakers (Analysts, Operators, etc.)\n")
        f.write("4. Aggregated text per transcript document\n\n")
        f.write(f"**Total documents:** {total_docs:,}\n")
        f.write(f"**Total characters:** {total_chars:,}\n")
        f.write(f"**Average characters per document:** {int(total_chars / total_docs) if total_docs > 0 else 0:,}\n\n")
        f.write("---\n\n")

        f.write("## Year-Quarter Statistics\n\n")

        for year in sorted(year_totals.keys()):
            if year_totals[year]['docs'] == 0:
                continue

            f.write(f"### Year {year}\n\n")
            f.write(f"**Total:** {year_totals[year]['docs']:,} documents\n\n")

            f.write("| Quarter | Documents | Avg Chars | Median Chars | Max Chars | File Size (MB) |\n")
            f.write("|---------|----------:|----------:|-------------:|----------:|---------------:|\n")

            for quarter in range(1, 5):
                if (year, quarter) not in year_quarter_stats:
                    continue
                stats = year_quarter_stats[(year, quarter)]
                f.write(f"| Q{quarter} | {stats['docs']:,} | {stats['avg_chars']:,} | ")
                f.write(f"{stats['median_chars']:,} | {stats['max_chars']:,} | ")
                f.write(f"{stats['file_size_mb']:.1f} |\n")

            f.write("\n")

        f.write("---\n\n")

        f.write("## File Checksums (SHA-256)\n\n")
        for (year, quarter) in sorted(year_quarter_stats.keys()):
            f.write(f"**{year}_Q{quarter}:** `{year_quarter_stats[(year, quarter)]['sha256']}`\n\n")

        f.write("---\n\n")

        f.write("## Processing Details\n\n")
        f.write("**Method:** Hybrid Python-C++-Python pipeline\n\n")
        f.write("**Python (2.2v2a):**\n")
        f.write("- Convert Parquet to JSON Lines format\n")
        f.write("- Orchestrate C++ processing\n")
        f.write("- Convert output back to Parquet\n")
        f.write("- Manage temporary file cleanup\n\n")
        f.write("**C++ (2.2v2b):**\n")
        f.write("- Filter to Q&A context\n")
        f.write("- Apply managerial speaker filter\n")
        f.write("- Aggregate text per document\n")
        f.write("- Pure stdlib implementation (no external dependencies)\n\n")

        f.write("**Managerial Filter Criteria:**\n")
        f.write("1. **Exclusions** (priority 1): Analyst, Operator, Editor, Moderator, ??\n")
        f.write("2. **Employer match** (priority 2): Speaker's employer matches company name\n")
        f.write(f"3. **Role keywords** (priority 3): {len(config['step_02']['managerial_roles'])} keywords ")
        f.write("(CEO, CFO, President, VP, Director, etc.)\n\n")

        f.write("---\n\n")

        f.write("## Determinism\n\n")
        f.write("- Unified Info duplicate resolution: deterministic sort by validation_timestamp, start_date\n")
        f.write("- Text aggregation: preserves speaker_number order\n")
        f.write("- Output sorting: alphabetical by file_name\n")
        f.write("- Year processing: sequential (2002→2018)\n\n")

        f.write("---\n\n")
        f.write("**End of Report**\n")

    print(f"Report generated: {report_path}")
    return report_path

if __name__ == "__main__":
    generate_report()
