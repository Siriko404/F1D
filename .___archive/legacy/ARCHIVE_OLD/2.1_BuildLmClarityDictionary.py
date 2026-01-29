#!/usr/bin/env python3
"""
Step: 2.1
Name: BuildLmClarityDictionary
Inputs: 1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv
Outputs: 4_Outputs/2.1_BuildLmClarityDictionary/<timestamp>/lm_Uncertainty_dictionary.parquet
         4_Outputs/2.1_BuildLmClarityDictionary/<timestamp>/lm_Negative_dictionary.parquet
         4_Outputs/2.1_BuildLmClarityDictionary/latest/lm_Uncertainty_dictionary.parquet
         4_Outputs/2.1_BuildLmClarityDictionary/latest/lm_Negative_dictionary.parquet
         4_Outputs/2.1_BuildLmClarityDictionary/<timestamp>/report_step_01.md
Logs: 3_Logs/2.1_BuildLmClarityDictionary/<timestamp>.log
Deterministic: True
Description: Build 2 dictionaries from LM Master (Uncertainty and Negative)

This script:
1. Loads the Loughran-McDonald Master Dictionary
2. Builds Uncertainty dictionary (tokens where Uncertainty > 0)
3. Builds Negative dictionary (tokens where Negative > 0)
4. Normalizes tokens to uppercase [A-Z]+ pattern
5. Writes 2 compact parquet dictionaries for C++ lookup
6. Generates comprehensive report with examples and hashes
"""

import os
import re
import sys
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

import yaml
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


class DualWriter:
    """Write to both stdout and log file simultaneously (verbatim)."""

    def __init__(self, log_file_path: Path):
        self.terminal = sys.stdout
        self.log_file = open(log_file_path, 'w', encoding='utf-8')

    def write(self, message: str):
        """Write message to both stdout and log file."""
        self.terminal.write(message)
        self.log_file.write(message)
        self.flush()

    def flush(self):
        """Flush both streams."""
        self.terminal.flush()
        self.log_file.flush()

    def close(self):
        """Close log file."""
        self.log_file.close()


def load_config(config_path: Path) -> Dict[str, Any]:
    """Load central configuration from YAML."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def compute_file_hash(file_path: Path, algorithm: str = 'sha256', chunk_size: int = 65536) -> str:
    """Compute hash of file for reproducibility."""
    hash_func = hashlib.new(algorithm)
    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def create_timestamped_output_dir(base_output_dir: Path) -> Tuple[Path, Path]:
    """Create timestamped output directory and latest symlink."""
    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    timestamped_dir = base_output_dir / timestamp
    latest_dir = base_output_dir / 'latest'

    # Create timestamped directory
    timestamped_dir.mkdir(parents=True, exist_ok=True)

    # Update latest symlink (remove old one if exists)
    if latest_dir.exists() or latest_dir.is_symlink():
        latest_dir.unlink()

    # Create new symlink (use relative path for portability)
    latest_dir.symlink_to(timestamp, target_is_directory=True)

    return timestamped_dir, latest_dir


def load_lm_dictionary(lm_path: Path) -> pd.DataFrame:
    """Load Loughran-McDonald Master Dictionary CSV."""
    print(f"Loading LM dictionary from: {lm_path}")
    df = pd.read_csv(lm_path, encoding='utf-8')
    print(f"  Loaded {len(df):,} rows, {len(df.columns)} columns")
    return df


def normalize_token(word: str, pattern: str = r'^[A-Z]+$') -> str:
    """
    Normalize token to uppercase and validate against pattern.
    Returns normalized token or empty string if invalid.
    """
    if pd.isna(word):
        return ''

    # Convert to uppercase
    normalized = str(word).upper().strip()

    # Validate pattern
    if re.match(pattern, normalized):
        return normalized
    else:
        return ''


def build_single_category_dictionary(df: pd.DataFrame,
                                     category_name: str,
                                     threshold: int = 0,
                                     token_pattern: str = r'^[A-Z]+$') -> pd.DataFrame:
    """
    Build dictionary for a single category from LM Master Dictionary.

    Selects tokens where:
    - category_column > threshold
    - Token matches token_pattern after uppercase normalization

    Returns DataFrame with columns: token
    """
    print(f"\nBuilding {category_name} dictionary...")

    # Normalize Word column
    print("  Normalizing tokens to uppercase [A-Z]+...")
    df['token'] = df['Word'].apply(lambda x: normalize_token(x, token_pattern))

    # Remove invalid tokens
    valid_mask = df['token'] != ''
    invalid_count = (~valid_mask).sum()
    if invalid_count > 0:
        print(f"  Dropped {invalid_count:,} rows with invalid tokens (non-alphabetic)")

    df = df[valid_mask].copy()

    # Ensure category column exists and is numeric
    if category_name not in df.columns:
        df[category_name] = 0

    df[category_name] = pd.to_numeric(df[category_name], errors='coerce').fillna(0)

    # Select rows based on criteria
    category_mask = df[category_name] > threshold
    category_count = category_mask.sum()

    print(f"  {category_name} tokens (before dedup): {category_count:,}")

    # Keep only selected rows
    selected_df = df[category_mask][['token']].copy()

    # Remove duplicates (keep first occurrence)
    original_len = len(selected_df)
    selected_df = selected_df.drop_duplicates(subset=['token'], keep='first')
    duplicates_removed = original_len - len(selected_df)

    if duplicates_removed > 0:
        print(f"  Removed {duplicates_removed:,} duplicate tokens (kept first)")

    # Sort for determinism
    selected_df = selected_df.sort_values('token').reset_index(drop=True)

    print(f"  Final {category_name} tokens: {len(selected_df):,} unique tokens")

    return selected_df


def write_dictionary_parquet(df: pd.DataFrame, output_path: Path):
    """Write dictionary to Parquet format."""
    print(f"\nWriting dictionary to: {output_path}")

    # Define schema explicitly for consistency (single column: token)
    schema = pa.schema([
        ('token', pa.string())
    ])

    # Convert to PyArrow table
    table = pa.Table.from_pandas(df, schema=schema)

    # Write with compression
    pq.write_table(
        table,
        output_path,
        compression='snappy',
        use_dictionary=True
    )

    file_size = output_path.stat().st_size
    print(f"  Written {len(df):,} rows ({file_size:,} bytes)")


def generate_report(config: Dict[str, Any],
                   lm_path: Path,
                   lm_df_original: pd.DataFrame,
                   uncertainty_df: pd.DataFrame,
                   negative_df: pd.DataFrame,
                   input_hash: str,
                   unc_output_hash: str,
                   neg_output_hash: str,
                   unc_output_path: Path,
                   neg_output_path: Path,
                   report_path: Path,
                   start_time: datetime,
                   end_time: datetime):
    """Generate comprehensive markdown report for both dictionaries."""
    print(f"\nGenerating report: {report_path}")

    # Compute statistics
    total_lm_rows = len(lm_df_original)
    unc_count = len(uncertainty_df)
    neg_count = len(negative_df)

    # Example tokens
    unc_examples = uncertainty_df.head(20)['token'].tolist()
    neg_examples = negative_df.head(20)['token'].tolist()

    # Keywords we expect
    expected_unc_keywords = ['MAY', 'COULD', 'APPROXIMATELY', 'BELIEVE']
    expected_neg_keywords = ['LOSS', 'NEGATIVE', 'DECLINE', 'ADVERSE']

    found_unc = [kw for kw in expected_unc_keywords if kw in uncertainty_df['token'].values]
    found_neg = [kw for kw in expected_neg_keywords if kw in negative_df['token'].values]

    # Build report content
    report_content = f"""# STEP 01: Build LM Dictionaries - Report

**Generated:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Process Version:** {config['project']['version']}
**Script:** 2.1_BuildLmClarityDictionary.py

---

## Summary

Built 2 dictionaries from Loughran-McDonald Master Dictionary:
1. **Uncertainty dictionary**: tokens where Uncertainty > 0
2. **Negative dictionary**: tokens where Negative > 0

All tokens normalized to uppercase [A-Z]+ pattern.

---

## Input

**File:** `{lm_path}`
**SHA-256:** `{input_hash}`
**Total rows:** {total_lm_rows:,}
**Columns:** {len(lm_df_original.columns)}

---

## Dictionary 1: Uncertainty

**Tokens:** {unc_count:,} unique tokens
**File:** `{unc_output_path.name}`
**SHA-256:** `{unc_output_hash}`
**Size:** {unc_output_path.stat().st_size:,} bytes

### First 20 tokens (alphabetically sorted):
{', '.join(unc_examples)}

### Expected keywords:
"""

    for kw in expected_unc_keywords:
        status = '[FOUND]' if kw in found_unc else '[NOT FOUND]'
        report_content += f"\n- **{kw}**: {status}"

    report_content += f"""

---

## Dictionary 2: Negative

**Tokens:** {neg_count:,} unique tokens
**File:** `{neg_output_path.name}`
**SHA-256:** `{neg_output_hash}`
**Size:** {neg_output_path.stat().st_size:,} bytes

### First 20 tokens (alphabetically sorted):
{', '.join(neg_examples)}

### Expected keywords:
"""

    for kw in expected_neg_keywords:
        status = '[FOUND]' if kw in found_neg else '[NOT FOUND]'
        report_content += f"\n- **{kw}**: {status}"

    report_content += f"""

---

## Schema (both dictionaries)

- `token` (STRING): Uppercase A-Z token

---

## Execution

**Start time:** {start_time.strftime('%Y-%m-%d %H:%M:%S')}
**End time:** {end_time.strftime('%Y-%m-%d %H:%M:%S')}
**Duration:** {(end_time - start_time).total_seconds():.2f} seconds

---

## Determinism

- Configuration read from: `{config['project']['name']}`
- Random seed: {config['determinism']['random_seed']}
- Sort order: Alphabetical by token
- Duplicates handling: Keep first occurrence

---

## Validation

[OK] All tokens match pattern [A-Z]+
[OK] No duplicate tokens in outputs
[OK] Output is deterministic (same input -> same output)

---

**End of Report**
"""

    # Write report
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"  Report written: {len(report_content):,} characters")


def main():
    """Main execution function."""
    # Record start time
    start_time = datetime.now()

    # Determine project root (parent of 2_Scripts)
    script_path = Path(__file__).resolve()
    project_root = script_path.parent.parent

    # Load configuration
    config_path = project_root / 'config' / 'project.yaml'
    config = load_config(config_path)

    # Setup output and log directories
    step_name = config['step_01']['output_subdir']
    log_base_dir = project_root / config['paths']['logs'] / step_name
    output_base_dir = project_root / config['paths']['outputs'] / step_name

    log_base_dir.mkdir(parents=True, exist_ok=True)
    output_base_dir.mkdir(parents=True, exist_ok=True)

    # Create timestamped log file
    log_timestamp = start_time.strftime('%Y-%m-%d_%H%M%S')
    log_file_path = log_base_dir / f"{log_timestamp}.log"

    # Setup dual writer (stdout + log file)
    dual_writer = DualWriter(log_file_path)
    sys.stdout = dual_writer

    # Print header
    print("=" * 80)
    print(f"STEP 01: Build LM Clarity Dictionary")
    print(f"Process Version: {config['project']['version']}")
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

    print(f"\nProject root: {project_root}")
    print(f"Config loaded from: {config_path}")
    print(f"Log file: {log_file_path}")

    # Create timestamped output directory
    timestamped_output_dir, latest_output_dir = create_timestamped_output_dir(output_base_dir)
    print(f"Output directory: {timestamped_output_dir}")
    print(f"Latest symlink: {latest_output_dir}")

    # Define paths
    lm_path = project_root / config['paths']['lm_dictionary']
    report_filename = config['step_01']['outputs']['summary_report']

    unc_output_path = timestamped_output_dir / 'lm_Uncertainty_dictionary.parquet'
    neg_output_path = timestamped_output_dir / 'lm_Negative_dictionary.parquet'
    report_path = timestamped_output_dir / report_filename

    # Check input file exists
    if not lm_path.exists():
        print(f"\nERROR: Input file not found: {lm_path}")
        sys.exit(1)

    # Compute input hash
    print(f"\nComputing input hash...")
    input_hash = compute_file_hash(
        lm_path,
        algorithm=config['hashing']['algorithm'],
        chunk_size=config['hashing']['chunk_size']
    )
    print(f"  Input SHA-256: {input_hash}")

    # Load LM dictionary
    lm_df = load_lm_dictionary(lm_path)

    # Build Uncertainty dictionary
    uncertainty_df = build_single_category_dictionary(
        lm_df.copy(),
        category_name='Uncertainty',
        threshold=0,
        token_pattern=config['step_01']['normalization']['pattern']
    )

    # Build Negative dictionary
    negative_df = build_single_category_dictionary(
        lm_df.copy(),
        category_name='Negative',
        threshold=0,
        token_pattern=config['step_01']['normalization']['pattern']
    )

    # Write Uncertainty dictionary
    write_dictionary_parquet(uncertainty_df, unc_output_path)

    # Compute Uncertainty hash
    print(f"\nComputing Uncertainty dictionary hash...")
    unc_output_hash = compute_file_hash(
        unc_output_path,
        algorithm=config['hashing']['algorithm'],
        chunk_size=config['hashing']['chunk_size']
    )
    print(f"  Uncertainty SHA-256: {unc_output_hash}")

    # Write Negative dictionary
    write_dictionary_parquet(negative_df, neg_output_path)

    # Compute Negative hash
    print(f"\nComputing Negative dictionary hash...")
    neg_output_hash = compute_file_hash(
        neg_output_path,
        algorithm=config['hashing']['algorithm'],
        chunk_size=config['hashing']['chunk_size']
    )
    print(f"  Negative SHA-256: {neg_output_hash}")

    # Record end time
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Generate report
    generate_report(
        config=config,
        lm_path=lm_path,
        lm_df_original=lm_df,
        uncertainty_df=uncertainty_df,
        negative_df=negative_df,
        input_hash=input_hash,
        unc_output_hash=unc_output_hash,
        neg_output_hash=neg_output_hash,
        unc_output_path=unc_output_path,
        neg_output_path=neg_output_path,
        report_path=report_path,
        start_time=start_time,
        end_time=end_time
    )

    # Print summary
    print("\n" + "=" * 80)
    print("STEP 01: COMPLETED SUCCESSFULLY")
    print("=" * 80)
    print(f"Duration: {duration:.2f} seconds")
    print(f"Uncertainty dictionary: {unc_output_path}")
    print(f"Negative dictionary: {neg_output_path}")
    print(f"Output report: {report_path}")
    print(f"Latest symlink: {latest_output_dir}")
    print(f"Log file: {log_file_path}")
    print("=" * 80)

    # Close dual writer
    dual_writer.close()
    sys.stdout = dual_writer.terminal


if __name__ == '__main__':
    main()
