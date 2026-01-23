#!/usr/bin/env python3
"""Verify bitwise-identical outputs between backup and new run."""

import pandas as pd
from pathlib import Path
import sys

backup_dir = Path("4_Outputs/backup_before_optimization")
output_dir = Path("4_Outputs/2_Textual_Analysis/2.1_Tokenized/latest")

print("Verifying bitwise-identical outputs...")
print()

all_match = True

# Compare each linguistic_counts_*.parquet file
for year in range(2002, 2019):
    backup_file = backup_dir / f"linguistic_counts_{year}.parquet"
    output_file = output_dir / f"linguistic_counts_{year}.parquet"

    if not backup_file.exists():
        print(f"Skipping {year}: Backup file not found")
        continue

    if not output_file.exists():
        print(f"ERROR: Year {year}: Output file not found")
        all_match = False
        continue

    df_backup = pd.read_parquet(backup_file)
    df_output = pd.read_parquet(output_file)

    # Verify data equality
    if not df_backup.equals(df_output):
        print(f"ERROR: Year {year}: Outputs differ!")
        print(f"  Backup rows: {len(df_backup)}, Output rows: {len(df_output)}")
        print(
            f"  Backup cols: {len(df_backup.columns)}, Output cols: {len(df_output.columns)}"
        )
        all_match = False
    else:
        # Verify identical column order and dtypes
        if list(df_backup.columns) != list(df_output.columns):
            print(f"ERROR: Year {year}: Column order differs!")
            all_match = False
        elif not df_backup.dtypes.equals(df_output.dtypes):
            print(f"ERROR: Year {year}: Data types differ!")
            all_match = False

if all_match:
    print("[OK] All outputs are bitwise-identical")
    sys.exit(0)
else:
    print("\n[ERROR] Some outputs differ")
    sys.exit(1)
