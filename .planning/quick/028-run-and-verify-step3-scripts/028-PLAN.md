---
phase: quick-028
plan: 028
type: execute
wave: 1
depends_on: []
files_modified:
  - 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
  - 2_Scripts/3_Financial/3.1_FirmControls.py
  - 2_Scripts/3_Financial/3.2_MarketVariables.py
  - 2_Scripts/3_Financial/3.3_EventFlags.py
autonomous: true
user_setup: []

must_haves:
  truths:
    - "Step 3.0 script runs without import errors"
    - "Step 3.1 script runs without import errors and generates outputs"
    - "Step 3.2 script runs without import errors and generates outputs"
    - "Step 3.3 script runs without import errors and generates outputs"
    - "Output parquet files are created for each year"
    - "stats.json files are created with statistics"
    - "report_step_3_X.md markdown reports are created"
  artifacts:
    - path: "2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py"
      provides: "Step 3 orchestrator script"
      contains: "from shared.observability_utils import DualWriter"
    - path: "2_Scripts/3_Financial/3.1_FirmControls.py"
      provides: "Firm controls computation script"
      contains: "from shared.observability_utils import DualWriter"
    - path: "2_Scripts/3_Financial/3.2_MarketVariables.py"
      provides: "Market variables computation script"
      contains: "from shared.observability_utils import DualWriter"
    - path: "2_Scripts/3_Financial/3.3_EventFlags.py"
      provides: "Event flags computation script"
      contains: "from shared.observability_utils import DualWriter"
    - path: "4_Outputs/3_Financial_Features/{timestamp}/"
      provides: "Step 3 output directory with parquet files"
      contains: "firm_controls_*.parquet, market_variables_*.parquet, event_flags_*.parquet, stats.json, report_step_3_*.md"
  key_links:
    - from: "2_Scripts/3_Financial/3.1_FirmControls.py"
      to: "shared/observability_utils.py"
      via: "from shared.observability_utils import DualWriter"
      pattern: "from shared\\.observability_utils import"
    - from: "2_Scripts/3_Financial/3.2_MarketVariables.py"
      to: "shared/observability_utils.py"
      via: "from shared.observability_utils import DualWriter"
      pattern: "from shared\\.observability_utils import"
    - from: "2_Scripts/3_Financial/3.3_EventFlags.py"
      to: "shared/observability_utils.py"
      via: "from shared.observability_utils import DualWriter"
      pattern: "from shared\\.observability_utils import"
---

<objective>
Run ALL Step 3 scripts (3.0, 3.1, 3.2, 3.3) at full scale and verify their outputs

Purpose: Validate that all Step 3 financial feature scripts run correctly and produce complete outputs including parquet files, statistics, and markdown reports

Output: Functional Step 3 pipeline with verified outputs
</objective>

<execution_context>
@C:\Users\sinas\.claude\get-shit-done\workflows\execute-plan.md
@C:\Users\sinas\.claude\get-shit-done\templates\summary.md
</execution_context>

<context>
@.planning/STATE.md
@2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
@2_Scripts/3_Financial/3.1_FirmControls.py
@2_Scripts/3_Financial/3.2_MarketVariables.py
@2_Scripts/3_Financial/3.3_EventFlags.py
@2_Scripts/3_Financial/3.4_Utils.py
@2_Scripts/shared/observability_utils.py
</context>

<tasks>

<task type="auto">
  <name>Task 1: Fix import errors in Step 3 scripts</name>
  <files>2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py, 2_Scripts/3_Financial/3.1_FirmControls.py, 2_Scripts/3_Financial/3.2_MarketVariables.py, 2_Scripts/3_Financial/3.3_EventFlags.py</files>
  <action>
Fix the import errors in all Step 3 scripts. The scripts are trying to import `DualWriter` from `utils` (3.4_Utils.py), but `DualWriter` is actually in `shared/observability_utils.py`.

For each script (3.0, 3.1, 3.2, 3.3):
1. Keep the dynamic import for 3.4_Utils.py (needed for `generate_variable_reference`)
2. Change `from utils import DualWriter, generate_variable_reference` to `from utils import generate_variable_reference`
3. Add `from shared.observability_utils import DualWriter` after the shared.path_utils imports
4. Remove `get_latest_output_dir` from the utils import (already imported from shared.path_utils)

The pattern should be:
```python
# Dynamic import for 3.4_Utils.py
utils_path = Path(__file__).parent / "3.4_Utils.py"
spec = importlib.util.spec_from_file_location("utils", utils_path)
utils = importlib.util.module_from_spec(spec)
sys.modules["utils"] = utils
spec.loader.exec_module(utils)

from utils import generate_variable_reference

try:
    from shared.path_utils import (
        validate_output_path,
        ensure_output_dir,
        validate_input_file,
        get_latest_output_dir,
    )
except ImportError:
    # Fallback imports...

# Import DualWriter from shared.observability_utils
from shared.observability_utils import DualWriter
```

Do NOT modify 3.4_Utils.py - it only needs to export `generate_variable_reference`.
  </action>
  <verify>
Check that all scripts compile without errors:
```bash
python -m py_compile 2_Scripts/3_Financial/3.0_BuildFinancialFeatures.py
python -m py_compile 2_Scripts/3_Financial/3.1_FirmControls.py
python -m py_compile 2_Scripts/3_Financial/3.2_MarketVariables.py
python -m py_compile 2_Scripts/3_Financial/3.3_EventFlags.py
```
  </verify>
  <done>
All Step 3 scripts compile successfully without import errors
  </done>
</task>

<task type="auto">
  <name>Task 2: Run Step 3.1 script and verify outputs</name>
  <files>2_Scripts/3_Financial/3.1_FirmControls.py</files>
  <action>
Run the Step 3.1 script to generate firm controls outputs:

```bash
cd C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D
python 2_Scripts/3_Financial/3.1_FirmControls.py
```

The script will:
1. Load manifest from latest Step 1 output
2. Load Compustat, IBES, and CCCL input data
3. Compute firm control variables (Size, BM, Lev, ROA, EPS_Growth, SurpDec, shift_intensity)
4. Generate descriptive statistics using observability_utils
5. Write output parquet files (one per year) to timestamped directory
6. Write stats.json and report_step_3_1.md

Monitor the output for any errors during execution. The script should process all years in the manifest.
  </action>
  <verify>
After script completes, verify outputs exist:
```bash
LATEST_DIR=$(ls -t 4_Outputs/3_Financial_Features/ | head -1)
ls -lh 4_Outputs/3_Financial_Features/$LATEST_DIR/
cat 4_Outputs/3_Financial_Features/$LATEST_DIR/stats.json | head -50
head -100 4_Outputs/3_Financial_Features/$LATEST_DIR/report_step_3_1.md
```

Expected outputs:
- firm_controls_*.parquet files (one per year)
- stats.json with INPUT/PROCESS/OUTPUT statistics
- report_step_3_1.md with comprehensive markdown report
  </verify>
  <done>
Step 3.1 runs successfully and creates all expected output files (parquet files, stats.json, report_step_3_1.md)
  </done>
</task>

<task type="auto">
  <name>Task 3: Run Step 3.2 and 3.3 scripts and verify outputs</name>
  <files>2_Scripts/3_Financial/3.2_MarketVariables.py, 2_Scripts/3_Financial/3.3_EventFlags.py</files>
  <action>
Run the remaining Step 3 scripts to generate market variables and event flags:

```bash
cd C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D

# Run Step 3.2 (Market Variables)
python 2_Scripts/3_Financial/3.2_MarketVariables.py

# Run Step 3.3 (Event Flags)
python 2_Scripts/3_Financial/3.3_EventFlags.py
```

Each script will:
1. Load manifest from latest Step 1 output
2. Load respective input data (CRSP for 3.2, SDC for 3.3)
3. Compute financial variables
4. Generate descriptive statistics
5. Write output parquet files and reports to timestamped directories

Monitor each script for errors. Each should process all years independently.
  </action>
  <verify>
After both scripts complete, verify outputs exist in each timestamped directory:

```bash
# Check 3.2 outputs
LATEST_32=$(ls -t 4_Outputs/3_Financial_Features/ | head -1)
echo "=== Step 3.2 Outputs ==="
ls -lh 4_Outputs/3_Financial_Features/$LATEST_32/
cat 4_Outputs/3_Financial_Features/$LATEST_32/stats.json | head -50
head -100 4_Outputs/3_Financial_Features/$LATEST_32/report_step_3_2.md

# Check 3.3 outputs
LATEST_33=$(ls -t 4_Outputs/3_Financial_Features/ | head -1)
echo "=== Step 3.3 Outputs ==="
ls -lh 4_Outputs/3_Financial_Features/$LATEST_33/
cat 4_Outputs/3_Financial_Features/$LATEST_33/stats.json | head -50
head -100 4_Outputs/3_Financial_Features/$LATEST_33/report_step_3_3.md
```

Expected outputs for 3.2:
- market_variables_*.parquet files (one per year)
- stats.json with market variable statistics
- report_step_3_2.md with comprehensive markdown report

Expected outputs for 3.3:
- event_flags_*.parquet files (one per year)
- stats.json with event flag statistics
- report_step_3_3.md with comprehensive markdown report
  </verify>
  <done>
Both Step 3.2 and 3.3 run successfully and create all expected output files (parquet files, stats.json, markdown reports)
  </done>
</task>

</tasks>

<verification>
Overall verification checks:

1. All four Step 3 scripts (3.0, 3.1, 3.2, 3.3) compile without import errors
2. Step 3.1 generates firm controls parquet files, stats.json, and report_step_3_1.md
3. Step 3.2 generates market variables parquet files, stats.json, and report_step_3_2.md
4. Step 3.3 generates event flags parquet files, stats.json, and report_step_3_3.md
5. All output parquet files are non-empty and contain expected data
6. All stats.json files contain INPUT/PROCESS/OUTPUT sections
7. All markdown reports are complete with INPUT/PROCESS/OUTPUT sections and statistics
</verification>

<success_criteria>
- All Step 3 scripts run without errors
- All expected output files are created (parquet, stats.json, markdown reports)
- Outputs are valid and contain expected data structures
- Descriptive statistics are comprehensive and properly formatted
</success_criteria>

<output>
After completion, create `.planning/quick/028-run-and-verify-step3-scripts/028-SUMMARY.md`
</output>
