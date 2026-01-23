#!/usr/bin/env python3
"""
Generate baseline checksums for regression testing.

This script scans output directories for key files, computes SHA-256 checksums,
and saves them to tests/fixtures/baseline_checksums.json.

Usage:
    python tests/regression/generate_baseline_checksums.py
"""

import hashlib
import json
import pandas as pd
from pathlib import Path


def compute_dataframe_checksum(df: pd.DataFrame) -> str:
    """Compute SHA-256 checksum of a DataFrame."""
    return hashlib.sha256(
        pd.util.hash_pandas_object(df, index=False).values.tobytes()
    ).hexdigest()


def compute_file_checksum(filepath: Path) -> str:
    """Compute SHA-256 checksum of a Parquet file."""
    df = pd.read_parquet(filepath)
    return compute_dataframe_checksum(df)


def generate_baseline_checksums():
    """Generate baseline checksums from existing outputs."""
    # Define key output files to track
    key_outputs = {
        "step1_cleaned_metadata": "4_Outputs/1.1_CleanMetadata/latest/cleaned_metadata.parquet",
        "step3_financial_features": "4_Outputs/3_Financial_Features/3.0_BuildFinancialFeatures/latest/financial_features.parquet",
    }

    # Add Step 2 yearly outputs
    for year in range(2002, 2019):
        key_outputs[f"step2_linguistic_counts_{year}"] = (
            f"4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest/linguistic_counts_{year}.parquet"
        )

    # Compute checksums
    baseline_checksums = {}
    missing_files = []

    for key, file_path in key_outputs.items():
        path = Path(file_path)
        if path.exists():
            checksum = compute_file_checksum(path)
            baseline_checksums[key] = checksum
            print(f"[OK] {key}: {checksum[:32]}...")
        else:
            print(f"[SKIP] {key}: File not found ({file_path})")
            missing_files.append(key)

    # Add metadata
    import subprocess

    try:
        git_commit = subprocess.check_output(
            ["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        git_commit = None

    baseline_checksums["_metadata"] = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "git_commit": git_commit,
        "total_files": len([k for k in key_outputs.keys() if k not in missing_files]),
        "missing_files": missing_files,
    }

    # Save to JSON
    baseline_path = Path("tests/fixtures/baseline_checksums.json")
    baseline_path.parent.mkdir(parents=True, exist_ok=True)

    with open(baseline_path, "w") as f:
        json.dump(baseline_checksums, f, indent=2)

    print(f"\nBaseline checksums saved to: {baseline_path}")
    print(
        f"Total files: {len([k for k in baseline_checksums.keys() if not k.startswith('_')])}"
    )
    print(f"Missing files: {len(missing_files)}")
    if missing_files:
        print(
            f"Missing: {', '.join(missing_files[:5])}{'...' if len(missing_files) > 5 else ''}"
        )


if __name__ == "__main__":
    generate_baseline_checksums()
