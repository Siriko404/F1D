#!/usr/bin/env python3
"""
Test script for entire_call dataset
Runs Step 2.2 for entire_call dataset only for specific test years
"""

import subprocess
import sys
import json
from pathlib import Path
import pandas as pd

# Test years
TEST_YEARS = [2003, 2010, 2017]
DATASET = "entire_call"

def main():
    root = Path(__file__).parent.parent

    # Paths
    input_dir = root / "1_Inputs"
    output_dir = root / "4_Outputs" / "2.2_ExtractFilteredDocs" / "test_entire_call"
    unified_info_path = input_dir / "Unified-info.parquet"
    cpp_exe = root / "2_Scripts" / "2.2v2b_ProcessManagerDocs.exe"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Testing {DATASET} dataset for years: {TEST_YEARS}")
    print("=" * 70)

    for year in TEST_YEARS:
        print(f"\n### Processing Year {year} ###")

        # Input/output paths
        speaker_data_file = input_dir / f"speaker_data_{year}.parquet"
        json_speaker_data = output_dir / f"speaker_data_{year}.json"
        json_unified_info = output_dir / f"unified_info_{year}.json"
        json_output = output_dir / f"{DATASET}_docs_{year}.json"
        parquet_output = output_dir / f"{DATASET}_docs_{year}.parquet"

        # Check if speaker data exists
        if not speaker_data_file.exists():
            print(f"  SKIP: {speaker_data_file.name} not found")
            continue

        # Step 1: Convert speaker data to JSON
        print(f"  Converting {speaker_data_file.name} to JSON...")
        df_speaker = pd.read_parquet(speaker_data_file)
        with open(json_speaker_data, 'w', encoding='utf-8') as f:
            for _, row in df_speaker.iterrows():
                json.dump(row.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        print(f"    Wrote {len(df_speaker):,} speaker turns to JSON")

        # Step 2: Convert unified info to JSON
        print(f"  Converting Unified-info.parquet to JSON...")
        df_unified = pd.read_parquet(unified_info_path)
        with open(json_unified_info, 'w', encoding='utf-8') as f:
            for _, row in df_unified.iterrows():
                json.dump(row.to_dict(), f, ensure_ascii=False)
                f.write('\n')
        print(f"    Wrote {len(df_unified):,} unified info records to JSON")

        # Step 3: Run C++ processor
        print(f"  Running C++ processor for {DATASET}...")
        cmd = [
            str(cpp_exe),
            str(year),
            DATASET
        ]

        env = {
            "SPEAKER_DATA_JSON": str(json_speaker_data),
            "UNIFIED_INFO_JSON": str(json_unified_info),
            "OUTPUT_JSON": str(json_output)
        }

        # Note: The C++ exe expects specific file paths - let me check its implementation
        print(f"    Command: {' '.join(cmd)}")
        print(f"    Note: C++ exe uses hardcoded paths, need to adapt")

        # For now, just report what would happen
        print(f"  Would create: {parquet_output}")
        print(f"  Status: Setup complete, C++ integration pending")

    print("\n" + "=" * 70)
    print("Test setup complete")
    print(f"Output directory: {output_dir}")

if __name__ == "__main__":
    main()
