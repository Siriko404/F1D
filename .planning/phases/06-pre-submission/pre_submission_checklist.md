# Pre-Submission Checklist

Use this checklist to verify all aspects of the project before final submission. Mark each item as complete with `[x]` once verified.

## 1. Data Provenance

- [ ] All input files documented in `data_sources.md`
- [ ] All `stats.json` files include input checksums
- [ ] Data sources properly cited in documentation
- [ ] Raw data files are immutable (no modifications)
- [ ] Data provenance chain is traceable from raw inputs to final outputs
- [ ] Any data transformations are documented and reproducible

## 2. Reproducibility

- [ ] All scripts have deterministic execution (seeds set, thread counts pinned)
- [ ] No hardcoded paths (all paths read from `config/project.yaml`)
- [ ] No data fabricated without explicit approval and documentation
- [ ] All outputs are timestamped in their respective directories
- [ ] Script execution order is deterministic (sorted inputs, no filesystem order dependencies)
- [ ] RNG seeds are logged in script headers
- [ ] Full pipeline can be reproduced on a fresh environment
- [ ] All config parameters are documented in `config/project.yaml`

## 3. Code Quality

- [ ] No `TODO`, `FIXME`, or `HACK` comments in production code
- [ ] All helper functions are inline (no shared modules that could break replication)
- [ ] Error handling is in place for all critical operations
- [ ] Logging uses DualWriter to both console and log files
- [ ] Script headers include: id, description, inputs/outputs, `deterministic: true`
- [ ] All scripts follow the naming convention: `2.<step>_<PascalCaseName>.<ext>`
- [ ] No commented-out code blocks in production scripts
- [ ] Variable names are descriptive and consistent across scripts
- [ ] Code follows the project's established patterns and conventions

## 4. Documentation

- [ ] `README.md` is comprehensive and up-to-date
- [ ] Variable codebook is complete and matches actual usage
- [ ] Execution instructions are copy-paste ready (no flags or manual setup)
- [ ] Pipeline diagram shows all steps with correct inputs/outputs
- [ ] `CLAUDE.md` instructions are concise and accurate
- [ ] Data sources are documented in `data_sources.md`
- [ ] All script headers accurately describe inputs and outputs
- [ ] Configuration options are documented in `config/project.yaml`
- [ ] Known limitations or assumptions are documented

## 5. Statistics

- [ ] All scripts generate `stats.json` files in their output directories
- [ ] All `stats.json` files validate against the schema
- [ ] Descriptive statistics match expected ranges and are reasonable
- [ ] Correlation matrix is generated for relevant variables
- [ ] Panel balance diagnostics are present (if panel data)
- [ ] Summary statistics tables are complete and consistent
- [ ] Missing data patterns are documented
- [ ] Outlier detection results are logged

## 6. Outputs

- [ ] All expected output files exist in `4_Outputs/`
- [ ] Output structure is consistent across all steps
- [ ] `latest/` symlinks are updated post-success for each step
- [ ] LaTeX files are properly formatted and compile
- [ ] CSV files have consistent encoding and delimiter
- [ ] Parquet files have consistent schema
- [ ] Output filenames follow the naming convention
- [ ] Output directories are timestamped correctly
- [ ] No temporary or intermediate files remain in output directories

## 7. Testing

- [ ] Full pipeline runs end-to-end without errors
- [ ] Fresh environment test passed (tested on clean machine)
- [ ] No dependencies missing from `requirements.txt`
- [ ] All imports are explicitly listed in requirements
- [ ] Scripts handle missing inputs gracefully with clear error messages
- [ ] Scripts validate inputs before processing
- [ ] All steps produce expected output file counts
- [ ] Log files are created and contain full execution traces
- [ ] Memory and runtime are reasonable for the data size

## 8. Academic Standards

- [ ] DCAS compliance verified:
  - **D**ata Collection: Documented in `data_sources.md`
  - **C**ollection Accessibility: Raw data is available or permissions documented
  - **A**nalysis Cleaning: All cleaning steps are reproducible
  - **S**tandards Analysis: Statistical methods are appropriate and documented
  - **R**esults: Results are reproducible and match expectations
- [ ] Code replicates paper methodology exactly
- [ ] Results match paper tables (within rounding)
- [ ] Variable names match paper notation (documented if different)
- [ ] Statistical assumptions are verified and documented
- [ ] Sensitivity analysis results are included (if applicable)
- [ ] Robustness checks are documented
- [ ] All analysis decisions are justified in documentation

## 9. Git and Version Control

- [ ] `.gitignore` is properly configured (excludes temporary files, logs with sensitive data)
- [ ] All committed files are necessary for reproduction
- [ ] Commit messages are clear and follow project conventions
- [ ] No sensitive data (API keys, credentials) in repository
- [ ] Repository structure matches the top-level requirements
  - Only `README.md`, `1_Inputs/`, `2_Scripts/`, `3_Logs/`, `4_Outputs/` at root

## 10. Environment

- [ ] `.claude/settings.json` is checked in with appropriate permissions
- [ ] `.claude/settings.local.json` exists for local overrides (git-ignored)
- [ ] Python version is documented and matches development environment
- [ ] All required system dependencies are documented
- [ ] Virtual environment setup instructions are provided
- [ ] Platform-specific differences are documented (Windows/Linux/macOS)

## 11. Final Verification

- [ ] Full pipeline has been run in its entirety at least once
- [ ] All log files are reviewed for warnings or errors
- [ ] Output files are visually inspected for correctness
- [ ] Documentation is reviewed for clarity and completeness
- [ ] Another researcher (if available) has reviewed the reproduction package
- [ ] Timeline for submission is documented (data collection, analysis, write-up dates)
- [ ] All stakeholder approvals (data access, ethics, etc.) are documented

---

## Quick Verification Command

Run this to verify the basic structure:

```bash
# Check top-level structure
ls -la | grep -E "^d|^-" | grep -E "README|1_|2_|3_|4_"

# Check all scripts follow naming convention
find 2_Scripts -name "*.py" -o -name "*.sh" | while read f; do
  [[ $f =~ ^2_Scripts/2\.[0-9]+_[A-Z] ]] || echo "Bad naming: $f"
done

# Check all outputs have stats.json
find 4_Outputs -type d -name "2.*" | while read d; do
  [[ -f "$d/stats.json" ]] || echo "Missing stats.json: $d"
done

# Check all scripts have contract headers
grep -L "deterministic:" 2_Scripts/*.py 2_Scripts/*.sh 2>/dev/null || echo "All scripts have headers"
```
