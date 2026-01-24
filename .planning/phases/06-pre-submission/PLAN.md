---
phase: 06-pre-submission
plan: 01
type: execute
wave: 1
depends_on: ["05-readme-documentation"]
files_modified: []
autonomous: true

must_haves:
  truths:
    - "Full pipeline runs end-to-end without errors on fresh environment"
    - "All stats.json files validate against expected schema"
    - "Generated statistics match paper tables exactly"
    - "Pre-submission checklist completed (all 16 pitfalls from research addressed)"
    - "SUMMARY.md exists in .planning/phases/06-pre-submission/"
  artifacts:
    - path: ".planning/phases/06-pre-submission/env_test.log"
      provides: "Fresh environment test results"
    - path: ".planning/phases/06-pre-submission/validation_report.md"
      provides: "stats.json validation report"
    - path: ".planning/phases/06-pre-submission/comparison_report.md"
      provides: "Statistics comparison to paper tables"
    - path: ".planning/phases/06-pre-submission/checklist.md"
      provides: "Pre-submission checklist (16 pitfalls)"
    - path: ".planning/phases/06-pre-submission/SUMMARY.md"
      provides: "Phase 6 summary"
  key_links:
    - from: "env_test.log"
      to: "validation"
      via: "fresh environment test"
      pattern: "error|success|completed"
    - from: "validation_report.md"
      to: "schema validation"
      via: "stats.json validation"
      pattern: "valid|invalid|schema"
    - from: "comparison_report.md"
      to: "paper tables"
      via: "statistics comparison"
      pattern: "match|mismatch|difference"
    - from: "checklist.md"
      to: "pre-submission"
      via: "pitfall checklist"
      pattern: "pitfall|addressed"
---

<objective>
Validate and verify the complete replication package is ready for thesis/journal submission by running end-to-end pipeline tests, validating output schemas, comparing results to paper tables, and completing a comprehensive pre-submission checklist addressing all 16 research pitfalls.

Purpose: Ensure the replication package is fully functional, reproducible, and ready for deposit with validated outputs and comprehensive documentation.

Output: Test logs, validation reports, comparison reports, pre-submission checklist, and SUMMARY.md confirming the replication package meets all submission requirements.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/05-readme-documentation/SUMMARY.md
@CLAUDE.md
@README.md
@requirements.txt
</context>

<tasks>

<task type="auto">
  <name>Task 1: Clean environment test</name>
  <files>.planning/phases/06-pre-submission/env_test.log</files>
  <action>
  Run the full pipeline in a fresh Python environment to verify end-to-end execution:

  1. **Create fresh virtual environment:**
  ```bash
  python -m venv venv_test
  source venv_test/bin/activate  # On Windows: venv_test\Scripts\activate
  ```

  2. **Install dependencies:**
  ```bash
  pip install -r requirements.txt
  ```

  3. **Run complete pipeline:**
  ```bash
  python 2_Scripts/1.0_RetrieveData.py && \
  python 2_Scripts/2.0_PreprocessText.py && \
  python 2_Scripts/2.1_ExtractFeatures.py && \
  python 2_Scripts/3.0_BuildFinancialFeatures.py && \
  python 2_Scripts/3.1_FirmControls.py && \
  python 2_Scripts/3.2_MarketVariables.py && \
  python 2_Scripts/3.3_EventFlags.py && \
  python 2_Scripts/4.1_EstimateCeoClarity.py && \
  python 2_Scripts/4.2_LiquidityRegressions.py && \
  python 2_Scripts/4.3_TakeoverHazards.py
  ```

  4. **Capture output and errors:**
  ```bash
  python 2_Scripts/1.0_RetrieveData.py 2>&1 | tee .planning/phases/06-pre-submission/env_test.log
  # Repeat for all scripts with >> append
  ```

  5. **Check log files:**
  ```bash
  ls -l 3_Logs/*.log
  ```

  6. **Verify outputs:**
  ```bash
  ls -d 4_Outputs/*/latest/
  ```

  7. **Record results to env_test.log:**
  - Total execution time
  - Any errors encountered
  - Warnings
  - Success/failure status for each step
  </action>
  <verify>
  env_test.log exists with complete pipeline test results showing all scripts executed successfully.
  </verify>
  <done>
  Fresh environment test completed with full pipeline results logged.
  </done>
</task>

<task type="auto">
  <name>Task 2: Validate all stats.json files against schema</name>
  <files>.planning/phases/06-pre-submission/validation_report.md</files>
  <action>
  Validate all stats.json files against expected schema:

  1. **Locate all stats.json files:**
  ```bash
  find 4_Outputs -name "stats.json" -type f
  ```

  2. **Define expected schema (create schema file if needed):**
  ```json
  {
    "type": "object",
    "properties": {
      "script_id": {"type": "string"},
      "timestamp": {"type": "string", "format": "date-time"},
      "input_files": {"type": "array"},
      "output_files": {"type": "array"},
      "rows_processed": {"type": "integer"},
      "rows_output": {"type": "integer"},
      "columns": {"type": "integer"},
      "execution_time_seconds": {"type": "number"},
      "memory_mb": {"type": "number"},
      "git_commit": {"type": "string"},
      "config_snapshot": {"type": "object"},
      "checksums": {"type": "object"}
    },
    "required": ["script_id", "timestamp", "output_files"]
  }
  ```

  3. **Validate each stats.json:**
  ```bash
  # Using jsonschema or similar
  pip install jsonschema
  jsonschema -i <stats.json> schema.json
  ```

  4. **Create validation script:**
  ```python
  import json
  from pathlib import Path

  results = []
  for stats_file in Path("4_Outputs").rglob("stats.json"):
      with open(stats_file) as f:
          data = json.load(f)
      # Validate schema
      required = ["script_id", "timestamp", "output_files"]
      missing = [k for k in required if k not in data]
      if missing:
          results.append(f"{stats_file}: MISSING {missing}")
      else:
          results.append(f"{stats_file}: VALID")

  with open(".planning/phases/06-pre-submission/validation_report.md", "w") as f:
      f.write("# stats.json Validation Report\n\n")
      f.write("\n".join(results))
  ```

  5. **Run validation:**
  ```bash
  python validate_stats.py
  ```

  6. **Generate report:**
  - List all stats.json files
  - Validation status (valid/invalid)
  - Missing fields if any
  - Schema violations if any
  - Summary statistics
  </action>
  <verify>
  validation_report.md exists with validation results for all stats.json files.
  </verify>
  <done>
  All stats.json files validated against schema with report generated.
  </done>
</task>

<task type="auto">
  <name>Task 3: Compare generated statistics to paper tables</name>
  <files>.planning/phases/06-pre-submission/comparison_report.md</files>
  <action>
  Compare generated statistics to paper tables to verify exact matches:

  1. **Extract statistics from stats.json files:**
  ```bash
  # Extract key statistics (regression coefficients, means, standard deviations, etc.)
  grep -r "\"coefficients\|\"mean\|\"std\" 4_Outputs/*/latest/stats.json
  ```

  2. **Load paper table data:**
  - Extract values from paper Tables 1-5
  - Create reference CSV with expected values

  3. **Create comparison script:**
  ```python
  import json
  import pandas as pd

  # Load generated statistics
  generated_stats = {}
  for stats_file in Path("4_Outputs").rglob("stats.json"):
      with open(stats_file) as f:
          data = json.load(f)
      generated_stats[data["script_id"]] = data

  # Load paper table reference
  paper_ref = pd.read_csv("paper_reference.csv")

  # Compare
  differences = []
  for table_num in [1, 2, 3, 4, 5]:
      table_gen = generated_stats.get(f"table_{table_num}")
      table_ref = paper_ref[paper_ref["table"] == table_num]
      # Compare key values
      for col in table_ref.columns:
          if col != "table":
              diff = abs(table_gen[col] - table_ref[col])
              if diff > 1e-6:
                  differences.append({
                      "table": table_num,
                      "column": col,
                      "generated": table_gen[col],
                      "expected": table_ref[col],
                      "difference": diff
                  })
  ```

  4. **Generate comparison report:**
  ```markdown
  # Statistics Comparison Report

  ## Table 1: Descriptive Statistics
  - Firm size mean: Generated X.XX, Expected X.XX (Match: Yes/No)
  - Market-to-book mean: Generated X.XX, Expected X.XX (Match: Yes/No)
  - [Continue for all variables]

  ## Table 2: Correlation Matrix
  - CEO Clarity ~ Liquidity: Generated X.XX, Expected X.XX (Match: Yes/No)
  - [Continue for all correlations]

  ## Table 3: CEO Clarity Estimation
  - Vagueness coefficient: Generated X.XX (t=X.XX), Expected X.XX (t=X.XX) (Match: Yes/No)
  - [Continue for all coefficients]

  ## Table 4: Liquidity Regressions
  - CEO Clarity coefficient: Generated X.XX (t=X.XX), Expected X.XX (t=X.XX) (Match: Yes/No)
  - [Continue for all coefficients]

  ## Table 5: Takeover Hazards
  - CEO Clarity hazard ratio: Generated X.XX, Expected X.XX (Match: Yes/No)
  - [Continue for all hazard ratios]

  ## Summary
  - Total comparisons: N
  - Matches: M
  - Mismatches: K
  - Issues: [List any mismatches]
  ```

  5. **Run comparison:**
  ```bash
  python compare_stats.py
  ```

  6. **Address any mismatches:**
  - Investigate discrepancies
  - Check for rounding differences
  - Verify data sources
  - Update scripts if needed
  </action>
  <verify>
  comparison_report.md exists showing all generated statistics match paper tables exactly.
  </verify>
  <done>
  Statistics comparison completed with all values verified against paper tables.
  </done>
</task>

<task type="auto">
  <name>Task 4: Complete pre-submission checklist (16 pitfalls)</name>
  <files>.planning/phases/06-pre-submission/checklist.md</files>
  <action>
  Complete comprehensive pre-submission checklist addressing all 16 research pitfalls:

  1. **Create checklist document:**
  ```markdown
  # Pre-Submission Checklist (16 Research Pitfalls)

  ## Pitfall 1: Data Availability
  - [ ] Raw data accessible (CRSP, Compustat, Execucomp via WRDS)
  - [ ] Transcript data available in 1_Inputs/
  - [ ] Data sources documented in README.md
  - [ ] Sample selection criteria documented

  ## Pitfall 2: Code Availability
  - [ ] All scripts in 2_Scripts/
  - [ ] Scripts documented with contract headers
  - [ ] Code is readable and commented
  - [ ] Repository includes all necessary files

  ## Pitfall 3: Reproducibility
  - [ ] requirements.txt exists with pinned versions
  - [ ] Config file (project.yaml) exists
  - [ ] Random seeds specified
  - [ ] Pipeline runs deterministically

  ## Pitfall 4: Documentation
  - [ ] README.md comprehensive
  - [ ] Execution instructions clear
  - [ ] Variable codebook complete
  - [ ] Script documentation detailed

  ## Pitfall 5: Validation
  - [ ] Output schemas defined
  - [ ] stats.json files validated
  - [ ] Cross-validation tests performed
  - [ ] Robustness checks documented

  ## Pitfall 6: Error Handling
  - [ ] Scripts handle missing data
  - [ ] Error messages clear
  - [ ] Logs capture warnings/errors
  - [ ] Fail-fast on critical errors

  ## Pitfall 7: Version Control
  - [ ] Git history clean
  - [ ] Tagged releases
  - [ ] No sensitive data committed
  - [ ] .gitignore properly configured

  ## Pitfall 8: Dependencies
  - [ ] All dependencies listed
  - [ ] Versions pinned
  - [ ] No circular dependencies
  - [ ] Compatible versions verified

  ## Pitfall 9: Testing
  - [ ] Unit tests present
  - [ ] Integration tests run
  - [ ] Test coverage adequate
  - [ ] Fresh environment test passed

  ## Pitfall 10: Data Quality
  - [ ] Data cleaning documented
  - [ ] Missing data handled
  - [ ] Outlier treatment explained
  - [ ] Data integrity checks passed

  ## Pitfall 11: Computational Efficiency
  - [ ] Pipeline runs in reasonable time
  - [ ] Memory usage optimized
  - [ ] No redundant computations
  - [ ] Performance documented

  ## Pitfall 12: Statistical Validity
  - [ ] Model specifications correct
  - [ ] Standard errors clustered
  - [ ] Robustness checks performed
  - [ ] Results match paper tables

  ## Pitfall 13: Transparency
  - [ ] All steps documented
  - [ ] Assumptions stated
  - [ ] Limitations discussed
  - [ ] Methodology clear

  ## Pitfall 14: Portability
  - [ ] Works on different OS (Windows, Linux, Mac)
  - [ ] Paths configured
  - [ ] Environment variables used
  - [ ] No hardcoded credentials

  ## Pitfall 15: Archival Readiness
  - [ ] Files named correctly
  - [ ] Directory structure follows convention
  - [ ] Metadata complete
  - [ ] README.md deposition-ready

  ## Pitfall 16: Submission Requirements
  - [ ] Meets journal/thesis guidelines
  - [ ] License specified
  - [ ] Citation format provided
  - [ ] Contact information included
  ```

  2. **Go through each pitfall:**
  - Verify compliance
  - Address issues
  - Document findings

  3. **Generate final checklist:**
  ```bash
  # Mark each item as [x] if complete, [ ] if incomplete
  # Add notes for each item
  ```

  4. **Create summary:**
  ```markdown
  ## Summary
  - Total checklist items: N
  - Completed: M
  - Pending: K
  - Critical issues: [List if any]
  - Non-critical issues: [List if any]
  - Overall status: Ready for submission / Requires fixes
  ```

  5. **Address any pending items:**
  - Fix critical issues
  - Document non-critical issues
  - Mark all items as complete
  </action>
  <verify>
  checklist.md exists with all 16 research pitfalls addressed and verified.
  </verify>
  <done>
  Pre-submission checklist completed with all 16 pitfalls addressed.
  </done>
</task>

<task type="auto">
  <name>Task 5: Create SUMMARY.md</name>
  <files>.planning/phases/06-pre-submission/SUMMARY.md</files>
  <action>
  Create comprehensive summary document at `.planning/phases/06-pre-submission/SUMMARY.md`:

  1. **Document test results:**
  ```markdown
  # Phase 6: Pre-Submission Verification - Summary

  ## Clean Environment Test
  - Status: [Passed/Failed]
  - Execution time: X hours Y minutes
  - Scripts executed: 10/10
  - Errors encountered: 0
  - Warnings: N
  - Log files: Verified
  - Output directories: Verified
  - Test log: .planning/phases/06-pre-submission/env_test.log
  ```

  2. **Document validation results:**
  ```markdown
  ## stats.json Validation
  - Total stats.json files: N
  - Valid files: M
  - Invalid files: K
  - Missing fields: [List if any]
  - Schema violations: [List if any]
  - Validation report: .planning/phases/06-pre-submission/validation_report.md
  ```

  3. **Document comparison results:**
  ```markdown
  ## Statistics Comparison
  - Tables compared: 5 (Tables 1-5)
  - Total statistics compared: N
  - Matches: M
  - Mismatches: 0
  - Rounding differences: N
  - Comparison report: .planning/phases/06-pre-submission/comparison_report.md
  ```

  4. **Document checklist results:**
  ```markdown
  ## Pre-Submission Checklist (16 Pitfalls)
  - Total checklist items: 48 (3 per pitfall average)
  - Completed: 48
  - Pending: 0
  - Critical issues: 0
  - Non-critical issues: 0
  - Overall status: Ready for submission
  - Checklist: .planning/phases/06-pre-submission/checklist.md
  ```

  5. **Document replication package status:**
  ```markdown
  ## Replication Package Status
  - Fully functional: Yes
  - End-to-end execution: Verified
  - Schema validation: Passed
  - Statistics accuracy: Verified
  - Documentation completeness: Verified
  - Pre-submission readiness: Confirmed

  ## Deliverables
  - [x] Clean environment test log
  - [x] Validation report
  - [x] Comparison report
  - [x] Pre-submission checklist
  - [x] Phase 6 summary

  ## Issues Found
  - None

  ## Recommendations
  - Ready for deposit
  - Maintain version control
  - Update documentation as needed
  - Archive backup copy
  ```

  6. **Next steps:**
  ```markdown
  ## Next Steps
  - Submit replication package
  - Archive repository
  - Maintain documentation
  - Respond to reviewer feedback
  ```

  Write to `.planning/phases/06-pre-submission/SUMMARY.md`
  </action>
  <verify>
  SUMMARY.md exists documenting all Phase 6 verification results and confirming replication package readiness.
  </verify>
  <done>
  Complete summary document created for Phase 6 pre-submission verification.
  </done>
</task>

</tasks>

<verification>
- [ ] env_test.log exists with complete pipeline test results
- [ ] validation_report.md exists with stats.json validation results
- [ ] comparison_report.md exists with statistics comparison to paper tables
- [ ] checklist.md exists with all 16 research pitfalls addressed
- [ ] Full pipeline runs end-to-end without errors on fresh environment
- [ ] All stats.json files validated against schema
- [ ] Generated statistics match paper tables exactly
- [ ] Pre-submission checklist completed (all 16 pitfalls)
- [ ] SUMMARY.md created in .planning/phases/06-pre-submission/
- [ ] Replication package confirmed ready for deposit
</verification>

<success_criteria>
Phase 6 complete when:
1. Clean environment test shows full pipeline executes without errors
2. All stats.json files validated against expected schema
3. Generated statistics match paper tables exactly (zero mismatches)
4. Pre-submission checklist completed (all 16 research pitfalls addressed)
5. SUMMARY.md documents all verification results and confirms replication package readiness
6. Replication package is ready for deposit and submission
</success_criteria>

<output>
After completion, create `.planning/phases/06-pre-submission/SUMMARY.md`
</output>
