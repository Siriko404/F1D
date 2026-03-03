# Systematic Fix Plan & Execution Prompt: H3 — Payout Policy

**Purpose:** This prompt instructs an AI agent to systematically plan and execute fixes for all remaining issues in the H3 suite.
**Source audit:** `docs/provenance/AUDIT_REVERIFICATION_H3.md`
**Target agent:** Any capable AI coding assistant with file read, edit, write, and bash execution capabilities.
**Expected output:**
1. Fixes implemented in codebase
2. Final verification report at `docs/provenance/FIX_VERIFICATION_H3.md`

---

## META-INSTRUCTIONS FOR THE AGENT

You are a diligent software engineer tasked with fixing ALL remaining issues in the H3 suite. Your job is to:

1. **PLAN BEFORE YOU CODE** — Read each issue, understand the fix required, and create a detailed fix plan
2. **EXECUTE SYSTEMATICALLY** — Fix issues one at a time, in priority order (BLOCKER → MAJOR → MINOR)
3. **VERIFY AFTER EACH FIX** — Run targeted verification commands to confirm the fix works
4. **DO NO HARM** — Do not break existing functionality; run tests if available
5. **DOCUMENT EVERYTHING** — Record what you changed, why, and how you verified it

### Non-Negotiable Rules

1. **ONE FIX AT A TIME.** Complete each fix fully (code change + verification) before moving to the next.

2. **PRESERVE EXISTING BEHAVIOR.** Only change what is necessary to fix the specific issue. Do not refactor, optimize, or "improve" unrelated code.

3. **VERIFY, DON'T ASSUME.** After each fix, run a specific verification command to prove the fix works.

4. **NO ORPHANED CHANGES.** Every code change must have a corresponding verification that proves it addresses the issue.

5. **ATOMIC COMMITS.** Group related changes logically. Each distinct fix should be a separate commit if using git.

6. **ZERO HALLUCINATION.** If you cannot implement a fix (missing dependency, unclear requirement), state "BLOCKED" with the reason.

---

## PHASE 0: CONTEXT GATHERING

Before fixing anything, gather context:

```bash
# Record git state
git rev-parse HEAD
git status

# Identify latest output directories
ls -la outputs/variables/h3_payout_policy/ | tail -5
ls -la outputs/econometric/h3_payout_policy/ | tail -5

# Read the source audit to understand all issues
cat docs/provenance/AUDIT_REVERIFICATION_H3.md
```

---

## PHASE 1: FIX LEDGER

The following issues must be fixed, in priority order:

### BLOCKER (MUST FIX)

| ID | Issue | Location | Fix Description |
|----|-------|----------|-----------------|
| B1 | LaTeX table missing star legend | `run_h3_payout_policy.py` → `_save_latex_table()` | Add `* p<0.10, ** p<0.05, *** p<0.01 (one-tailed tests)` to table notes |

### MAJOR (SHOULD FIX)

| ID | Issue | Location | Fix Description |
|----|-------|----------|-----------------|
| M1 | Machine-readable variable lineage JSON missing | Create new file | Create `variable_lineage.json` with formula, source fields, timing, code_reference for each variable |
| M2 | LaTeX table missing explicit sample filter | `run_h3_payout_policy.py` → `_save_latex_table()` | Add "Sample restricted to firms with dividend payments in trailing 5 years (is_div_payer_5yr==1)" |

### MINOR (NICE TO HAVE)

| ID | Issue | Location | Fix Description |
|----|-------|----------|-----------------|
| m1 | LaTeX table missing N firms row | `run_h3_payout_policy.py` → `_save_latex_table()` | Add "Firms" row showing n_firms per column |
| m2 | `rsquared_adj` column mislabeled | `run_h3_payout_policy.py` line 286 | Rename to `rsquared_inclusive` |
| m3 | Summary stats missing sample period | `run_h3_payout_policy.py` → summary stats function | Add "Sample period: 2002--2018" |
| m4 | Summary stats missing winsorization note | `run_h3_payout_policy.py` → summary stats function | Add "All continuous variables winsorized at 1st/99th percentile per year" |
| m5 | Summary stats missing N varies note | `run_h3_payout_policy.py` → summary stats function | Add "N varies across variables due to missing data" |
| m6 | Stage 3/4 run.log files missing | Stage 3/4 runners | Add logging to capture console output |
| m7 | Interaction centering not documented | `H3.md` provenance | Add note that interaction uses uncentered raw product |

---

## PHASE 2: FIX IMPLEMENTATION PROTOCOL

For each issue, follow this exact protocol:

### Fix Protocol

```
## Fix [ID]: [Title]

**Priority:** [BLOCKER/MAJOR/MINOR]
**Issue:** [What's wrong]
**Location:** [Exact file and function/line]
**Fix:** [What to change]

### Pre-Fix State

**Command to inspect current state:**
```bash
[exact command]
```

**Current output:**
```
[exact output showing the issue]
```

### Implementation

**File(s) modified:** [list]
**Change made:**
```diff
[exact diff or description of change]
```

### Post-Fix Verification

**Verification command:**
```bash
[exact command to prove fix works]
```

**Expected output:**
```
[what the output should show after fix]
```

**Actual output:**
```
[what you actually got]
```

**Status:** [FIXED / FAILED / BLOCKED]
**If FAILED/BLOCKED:** [explanation]
```

---

## PHASE 3: DETAILED FIX SPECIFICATIONS

### Fix B1: Add Star Legend to LaTeX Table

**File:** `src/f1d/econometric/run_h3_payout_policy.py`
**Function:** `_save_latex_table()` (or equivalent LaTeX generation code)

**Current state:** Table notes do not include significance threshold legend.
**Required change:** Add the following line to the table notes:
```latex
* $p<0.10$, ** $p<0.05$, *** $p<0.01$ (one-tailed tests).
```

**Verification:**
```bash
grep -i "p<0\|star" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex
# Expected: match found with the star legend
```

---

### Fix M1: Create Variable Lineage JSON

**File:** Create `outputs/variables/h3_payout_policy/variable_lineage.json` (or add to Stage 3 output generation)

**Current state:** No machine-readable variable definitions exist.
**Required change:** Create JSON file with structure:
```json
{
  "suite": "H3",
  "generated_at": "TIMESTAMP",
  "variables": {
    "div_stability_lead": {
      "paper_label": "Dividend Stability (t+1)",
      "type": "Continuous",
      "formula": "-StdDev(payout_ratio_lag) over trailing 5 fiscal years (1826D, min_periods=3), shifted forward 1 fiscal year",
      "source_fields": ["dvy", "iby", "gvkey", "fyearq"],
      "winsorization": "1%/99% per year at CompustatEngine",
      "timing": "t+1 fiscal year",
      "code_reference": "_compustat_engine.py:857-865 + build_h3_payout_policy_panel.py:106-111"
    },
    "payout_flexibility_lead": {
      "paper_label": "Payout Flexibility (t+1)",
      "type": "Continuous",
      "formula": "% of years with |Delta DPS| > 5% of prior DPS over trailing 5 years, shifted forward 1 fiscal year",
      "source_fields": ["dps", "gvkey", "fyearq"],
      "winsorization": "1%/99% per year at CompustatEngine",
      "timing": "t+1 fiscal year",
      "code_reference": "_compustat_engine.py:868-878 + build_h3_payout_policy_panel.py:106-111"
    },
    "Manager_QA_Uncertainty_pct": {
      "paper_label": "Manager Q&A Uncertainty",
      "type": "Continuous",
      "formula": "Manager_QA_Uncertainty_count / Manager_QA_total_tokens * 100",
      "source_fields": ["transcript tokens", "LM dictionary"],
      "winsorization": "Upper 99th per year at LinguisticEngine",
      "timing": "At call date",
      "code_reference": "manager_qa_uncertainty.py"
    }
    // ... add all other variables used in H3
  }
}
```

**Verification:**
```bash
ls outputs/variables/h3_payout_policy/*/variable_lineage.json
# Expected: file exists
python -c "import json; j=json.load(open('outputs/variables/h3_payout_policy/*/variable_lineage.json')); print(len(j['variables']))"
# Expected: number of variables defined
```

---

### Fix M2: Add Explicit Sample Filter to LaTeX Table Notes

**File:** `src/f1d/econometric/run_h3_payout_policy.py`
**Function:** `_save_latex_table()` or equivalent

**Current state:** Table notes do not explicitly state the dividend payer filter.
**Required change:** Add the following to table notes:
```latex
Sample restricted to firms with dividend payments in trailing 5 years (is\_div\_payer\_5yr==1).
```

**Verification:**
```bash
grep -i "dividend.*payer\|is_div_payer\|trailing 5 year" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex
# Expected: match found
```

---

### Fix m1: Add N Firms Row to LaTeX Table

**File:** `src/f1d/econometric/run_h3_payout_policy.py`
**Function:** `_save_latex_table()` or equivalent

**Current state:** Table shows Observations but not Firms count.
**Required change:** Add "Firms" row after Observations row, using `n_firms` from meta dict.

**Verification:**
```bash
grep -i "firms\|n_firms" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex
# Expected: "Firms" row with numbers like "922" for Main/DS column
```

---

### Fix m2: Rename rsquared_adj Column

**File:** `src/f1d/econometric/run_h3_payout_policy.py`
**Line:** ~286

**Current code:**
```python
"rsquared_adj": float(model.rsquared_inclusive),
```

**Required change:**
```python
"rsquared_inclusive": float(model.rsquared_inclusive),
```

**Verification:**
```bash
grep "rsquared_inclusive" outputs/econometric/h3_payout_policy/*/model_diagnostics.csv
# Expected: column header shows rsquared_inclusive
```

---

### Fix m3-m5: Enhance Summary Stats Table Notes

**File:** `src/f1d/econometric/run_h3_payout_policy.py`
**Function:** Summary stats LaTeX generation

**Current state:** Notes only say "This table reports summary statistics..."
**Required change:** Add to notes:
```latex
Sample period: 2002--2018. All continuous variables winsorized at 1st/99th percentile per year. N varies across variables due to missing data.
```

**Verification:**
```bash
grep -i "2002\|winsor\|missing" outputs/econometric/h3_payout_policy/*/summary_stats.tex
# Expected: matches for all three additions
```

---

### Fix m6: Add run.log Capture

**File:** `src/f1d/variables/build_h3_payout_policy_panel.py` and `src/f1d/econometric/run_h3_payout_policy.py`

**Current state:** Console output not captured to file.
**Required change:** Add logging handler to capture print() statements to `run.log`.

**Implementation pattern:**
```python
import sys
from pathlib import Path

def setup_logging(out_dir: Path):
    """Capture stdout to run.log file."""
    log_file = out_dir / "run.log"
    class Tee:
        def __init__(self, *files):
            self.files = files
        def write(self, text):
            for f in self.files:
                f.write(text)
        def flush(self):
            for f in self.files:
                f.flush()

    sys.stdout = Tee(sys.stdout, open(log_file, 'w'))
```

**Verification:**
```bash
ls outputs/variables/h3_payout_policy/*/run.log
ls outputs/econometric/h3_payout_policy/*/run.log
# Expected: files exist with content
```

---

### Fix m7: Document Interaction Centering

**File:** `docs/provenance/H3.md`

**Current state:** No documentation about interaction term centering.
**Required change:** Add note in Section F.3 or relevant section:
```markdown
**Note on interaction centering:** The interaction term `Uncertainty_x_Lev` is computed as the uncentered raw product `Uncertainty * Lev`. This means beta1 represents the effect of Uncertainty when Lev=0, not at mean leverage. Centering does not affect the interaction coefficient (beta3) interpretation.
```

**Verification:**
```bash
grep -i "uncentered\|centering" docs/provenance/H3.md
# Expected: match found
```

---

## PHASE 4: REGENERATION & FINAL VERIFICATION

After all code fixes are implemented:

### Step 1: Regenerate Stage 4 Outputs

```bash
python -m f1d.econometric.run_h3_payout_policy
```

### Step 2: Run Full Verification Suite

```bash
# Verify all fixes
echo "=== B1: Star Legend ==="
grep -i "p<0" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex

echo "=== M1: Variable Lineage JSON ==="
ls outputs/variables/h3_payout_policy/*/variable_lineage.json

echo "=== M2: Sample Filter in Notes ==="
grep -i "dividend.*payer\|trailing 5" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex

echo "=== m1: N Firms Row ==="
grep -i "^Firms" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex

echo "=== m2: rsquared_inclusive Column ==="
head -1 outputs/econometric/h3_payout_policy/*/model_diagnostics.csv | grep "rsquared_inclusive"

echo "=== m3-m5: Summary Stats Notes ==="
grep -i "2002\|winsor\|missing" outputs/econometric/h3_payout_policy/*/summary_stats.tex

echo "=== m6: run.log Files ==="
ls outputs/variables/h3_payout_policy/*/run.log
ls outputs/econometric/h3_payout_policy/*/run.log

echo "=== m7: Centering Documentation ==="
grep -i "uncentered" docs/provenance/H3.md
```

### Step 3: Cross-Artifact Consistency Check

```python
# Verify consistency after regeneration
import pandas as pd
from glob import glob

# Get latest outputs
diag_path = sorted(glob('outputs/econometric/h3_payout_policy/*/model_diagnostics.csv'))[-1]
tex_path = sorted(glob('outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex'))[-1]

diag = pd.read_csv(diag_path)

# Check Main/DS/Mgr_QA
row = diag[(diag['sample']=='Main') & (diag['dv']=='div_stability_lead') & (diag['uncertainty_measure']=='Manager_QA_Uncertainty_pct')].iloc[0]

print(f"beta1: {row['beta1']:.4f}")
print(f"beta3: {row['beta3']:.4f}")
print(f"n_obs: {int(row['n_obs'])}")
print(f"n_firms: {int(row['n_firms'])}")
print(f"within_r2: {row['within_r2']:.4f}")

# Verify these match the LaTeX table
```

---

## PHASE 5: OUTPUT DOCUMENT FORMAT

Your final output MUST be written to:
```
docs/provenance/FIX_VERIFICATION_H3.md
```

### Required Document Structure

```markdown
# Fix Verification Report: H3 — Payout Policy

**Fix date:** [YYYY-MM-DD]
**Agent:** [AI model identifier]
**Source audit:** docs/provenance/AUDIT_REVERIFICATION_H3.md
**Git commit before fixes:** [hash]
**Git commit after fixes:** [hash]

---

## 1) Executive Summary

| Metric | Count |
|--------|-------|
| Total issues addressed | 10 |
| Issues FIXED | XX |
| Issues BLOCKED | XX |
| Issues SKIPPED | XX |

### All BLOCKERs Resolved?
[YES/NO - explain if NO]

---

## 2) Fix Ledger

| ID | Issue | Status | Verification Command | Result |
|----|-------|--------|---------------------|--------|
| B1 | Star legend | FIXED | `grep ...` | Match found |
| M1 | Variable lineage | FIXED | `ls ...` | File exists |
| ... | ... | ... | ... | ... |

---

## 3) Detailed Fix Reports

### Fix B1: Star Legend
[Full pre/post verification]

### Fix M1: Variable Lineage JSON
[Full pre/post verification]

[... continue for all fixes ...]

---

## 4) Regeneration Results

**Stage 4 rerun command:**
```bash
python -m f1d.econometric.run_h3_payout_policy
```

**New output directory:** [timestamp]

**Cross-artifact consistency:**
| Check | Status | Evidence |
|-------|--------|----------|
| LaTeX vs diagnostics coef | PASS | [evidence] |
| LaTeX vs diagnostics N | PASS | [evidence] |
| LaTeX vs diagnostics R² | PASS | [evidence] |

---

## 5) Remaining Issues

[List any issues that could not be fixed, with explanation]

---

## 6) Confidence Assessment

| Aspect | Confidence | Justification |
|--------|------------|---------------|
| All fixes implemented correctly | HIGH/MED/LOW | ... |
| No regressions introduced | HIGH/MED/LOW | ... |
| Paper-ready status achieved | HIGH/MED/LOW | ... |

---

## 7) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | ... | ... | ... |

---

## 8) Final Verdict

**H3 Suite Status: [PAPER-READY / NOT PAPER-READY]**

[Summary of what was achieved and what remains]
```

---

## BEGIN FIX IMPLEMENTATION NOW

Start with PHASE 0: Gather context. Then proceed through each fix in priority order (B1 → M1 → M2 → m1 → m2 → m3-m5 → m6 → m7).

For each fix:
1. Inspect current state
2. Implement the fix
3. Verify the fix works
4. Document in the fix report

Do not skip any issue. If you cannot fix something, document why.
