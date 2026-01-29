"""Check event flags and generate missing report"""
import pandas as pd
from pathlib import Path

output_dir = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\4_Outputs\3_Financial_Features\2025-12-26_204420")

# Check event flags columns
ef = pd.read_parquet(output_dir / "event_flags_2010.parquet")
print("Event flags columns:", ef.columns.tolist())
print("\nTakeover value counts:")
print(ef['Takeover'].value_counts())
if 'Takeover_Type' in ef.columns:
    print("\nTakeover_Type value counts:")
    print(ef['Takeover_Type'].value_counts(dropna=False))

# Check if all files exist
firm_files = list(output_dir.glob("firm_controls_*.parquet"))
market_files = list(output_dir.glob("market_variables_*.parquet"))
event_files = list(output_dir.glob("event_flags_*.parquet"))

print(f"\nFiles found:")
print(f"  firm_controls: {len(firm_files)}")
print(f"  market_variables: {len(market_files)}")
print(f"  event_flags: {len(event_files)}")
