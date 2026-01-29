"""Generate missing report and variable_reference for Step 3"""
import pandas as pd
from pathlib import Path
import sys

# Add utils path
sys.path.insert(0, str(Path(__file__).parent / "2_Scripts" / "3_Financial"))
from importlib.util import spec_from_file_location, module_from_spec
utils_path = Path(__file__).parent / "2_Scripts" / "3_Financial" / "3.4_Utils.py"
spec = spec_from_file_location("utils", utils_path)
utils = module_from_spec(spec)
spec.loader.exec_module(utils)

output_dir = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\4_Outputs\3_Financial_Features\2025-12-26_204420")

# Load sample data for coverage stats
firm_files = list(output_dir.glob("firm_controls_*.parquet"))
market_files = list(output_dir.glob("market_variables_*.parquet"))
event_files = list(output_dir.glob("event_flags_*.parquet"))

# Aggregate for stats
all_firm = pd.concat([pd.read_parquet(f) for f in firm_files], ignore_index=True)
all_market = pd.concat([pd.read_parquet(f) for f in market_files], ignore_index=True)
all_event = pd.concat([pd.read_parquet(f) for f in event_files], ignore_index=True)

total_calls = len(all_firm)

# Generate report
report = f"""# Step 3: Financial Features Report

**Generated:** 2025-12-26_204420
**Output:** `{output_dir}`

## Summary

| Category | Files | Rows |
|----------|-------|------|
| Firm Controls | {len(firm_files)} | {len(all_firm):,} |
| Market Variables | {len(market_files)} | {len(all_market):,} |
| Event Flags | {len(event_files)} | {len(all_event):,} |

## Coverage

### Firm Controls (3.1)
| Variable | Coverage |
|----------|----------|
| Size | {all_firm['Size'].notna().sum():,} ({all_firm['Size'].notna().mean()*100:.1f}%) |
| BM | {all_firm['BM'].notna().sum():,} ({all_firm['BM'].notna().mean()*100:.1f}%) |
| Lev | {all_firm['Lev'].notna().sum():,} ({all_firm['Lev'].notna().mean()*100:.1f}%) |
| ROA | {all_firm['ROA'].notna().sum():,} ({all_firm['ROA'].notna().mean()*100:.1f}%) |
| EPS_Growth | {all_firm['EPS_Growth'].notna().sum():,} ({all_firm['EPS_Growth'].notna().mean()*100:.1f}%) |
| SurpDec | {all_firm['SurpDec'].notna().sum():,} ({all_firm['SurpDec'].notna().mean()*100:.1f}%) |
"""

intensity_cols = [c for c in all_firm.columns if c.startswith('shift_intensity')]
for col in intensity_cols:
    report += f"| {col} | {all_firm[col].notna().sum():,} ({all_firm[col].notna().mean()*100:.1f}%) |\n"

report += f"""
### Market Variables (3.2)
| Variable | Coverage |
|----------|----------|
| StockRet | {all_market['StockRet'].notna().sum():,} ({all_market['StockRet'].notna().mean()*100:.1f}%) |
| MarketRet | {all_market['MarketRet'].notna().sum():,} ({all_market['MarketRet'].notna().mean()*100:.1f}%) |
| Amihud | {all_market['Amihud'].notna().sum():,} ({all_market['Amihud'].notna().mean()*100:.1f}%) |
| Corwin_Schultz | {all_market['Corwin_Schultz'].notna().sum():,} ({all_market['Corwin_Schultz'].notna().mean()*100:.1f}%) |
| Delta_Amihud | {all_market['Delta_Amihud'].notna().sum():,} ({all_market['Delta_Amihud'].notna().mean()*100:.1f}%) |

### Event Flags (3.3)
| Variable | Coverage |
|----------|----------|
| Takeover | {(all_event['Takeover'] == 1).sum():,} takeovers out of {len(all_event):,} calls ({(all_event['Takeover']==1).mean()*100:.2f}%) |
| Takeover_Type (Friendly) | {(all_event['Takeover_Type'] == 'Friendly').sum():,} |
| Takeover_Type (Uninvited) | {(all_event['Takeover_Type'] == 'Uninvited').sum():,} |
"""

# Save report
with open(output_dir / "report_step3.md", 'w') as f:
    f.write(report)
print(f"Generated: report_step3.md")

# Generate variable reference
utils.generate_variable_reference(all_firm, output_dir / "variable_reference.csv")
print(f"Generated: variable_reference.csv")

# Update latest symlink
latest_dir = output_dir.parent / "latest"
utils.update_latest_symlink(latest_dir, output_dir)
print(f"Updated: latest symlink")
