# Audit Re-Verification Prompt: H3 — Payout Policy

**Purpose:** This prompt instructs an AI auditor to perform a MANUAL, ONE-BY-ONE re-verification of all issues documented in prior audits of the H3 suite.
**Target agent:** Any capable AI coding assistant with file read and bash execution capabilities.
**Expected output:** `docs/provenance/AUDIT_REVERIFICATION_H3.md` — a complete, audit-ready document.

---

## META-INSTRUCTIONS FOR THE AUDITOR

You are an adversarial auditor. Your job is to verify, with ZERO TOLERANCE for hallucination, whether each documented issue in the H3 suite has been:
- **FIXED** — the problem no longer exists in the current codebase/artifacts
- **STILL PRESENT** — the problem persists exactly as documented
- **PARTIALLY FIXED** — some aspects resolved, others not
- **SUPERSEDED** — the underlying code/artifact has been restructured, making the original issue moot

### Non-Negotiable Rules

1. **NO BULK OPERATIONS.** You must verify each claim INDIVIDUALLY with a targeted, specific command or file read. A single command checking 10 things at once is FORBIDDEN.

2. **EVERY CLAIM GETS EVIDENCE.** You may not state "FIXED" or "STILL PRESENT" without providing the EXACT command you ran and the EXACT output you observed.

3. **NO ASSUMPTIONS.** Do not assume that because one file says X, another file must be consistent. Verify consistency explicitly.

4. **NO SKIPPING.** You must verify EVERY item in the claim ledger below. Mark N/A only if the artifact genuinely does not exist and was never created.

5. **PRESERVE CHAIN OF CUSTODY.** For each verification, note:
   - The exact file path(s) inspected
   - The exact line number(s) if applicable
   - The exact command executed
   - The exact output received
   - Timestamp or git commit if relevant

6. **ZERO HALLUCINATION.** If you cannot verify something (file missing, command fails, access denied), state "UNVERIFIABLE" with the reason. Do not guess.

---

## PHASE 1: CLAIM LEDGER EXTRACTION

Before verifying anything, extract and tabulate ALL claims from the following source documents:
- `docs/provenance/H3.md`
- `docs/provenance/AUDIT_H3.md`
- `docs/provenance/Paper_Artifacts_Audit_H3.md`

Create a CLAIM LEDGER with this structure:

| Claim ID | Source Doc | Claim Summary | Severity | Category | Location in Source |
|----------|------------|---------------|----------|----------|-------------------|
| C001 | AUDIT_H3.md | div_stability formula mismatch | MAJOR | Formula | Finding 1 |
| ... | ... | ... | ... | ... | ... |

Categories include: Formula, Output Artifact, Documentation, Test Coverage, Reproducibility, Table Notes, Column Label, Code Logic.

---

## PHASE 2: MANUAL ONE-BY-ONE VERIFICATION

For each claim in the ledger, execute the following protocol:

### Verification Protocol Per Claim

```
## Claim CXXX: [Title]

**Source:** [doc name], [section/line]
**Original finding:** [exact quote or summary]
**Severity:** [BLOCKER/MAJOR/MINOR/NOTE]

### Verification Attempt 1

**What I'm checking:** [specific assertion]
**File(s) to inspect:** [exact paths]
**Command executed:**
```bash
[exact command]
```
**Output observed:**
```
[exact output, truncated if long but preserving key evidence]
```
**Interpretation:** [your analysis of what this output means]

### Verification Attempt 2 (if needed)

[Repeat structure if first attempt inconclusive]

### Final Verdict

**Status:** [FIXED / STILL PRESENT / PARTIALLY FIXED / SUPERSEDED / UNVERIFIABLE]
**Confidence:** [HIGH / MEDIUM / LOW]
**Evidence summary:** [one sentence citing the key proof]
**Action needed:** [if STILL PRESENT or PARTIALLY FIXED, what specifically must be done]
```

---

## PHASE 3: CLAIMS TO VERIFY

The following claims MUST be verified individually. Do not deviate from this list. Do not add claims not documented in the source audits.

### GROUP A: Formula & Code Logic Claims

| ID | Claim | Source |
|----|-------|--------|
| A1 | `div_stability` formula in code (`_compustat_engine.py:857-865`) computes `-StdDev(lagged payout_ratio)` but docstring and provenance claim `-StdDev(Delta DPS)/\|Mean(DPS)\|` | AUDIT_H3.md Finding 1 |
| A2 | `payout_flexibility` formula uses `(delta_dps.abs() > 0.05 * dps_lag.abs())` — verify docstring matches | AUDIT_H3.md Open Gap #6 |
| A3 | Interaction term uses UNCENTERED raw product (`Uncertainty * Lev`), not centered | AUDIT_H3.md Finding 5 |

### GROUP B: Output Artifact Claims

| ID | Claim | Source |
|----|-------|--------|
| B1 | `run_manifest.json` does NOT exist in Stage 4 output directory | Paper_Artifacts_Audit Blocker #1 |
| B2 | Sample attrition table does NOT exist | Paper_Artifacts_Audit Major #4 |
| B3 | Machine-readable variable lineage JSON does NOT exist | Paper_Artifacts_Audit Major #6 |
| B4 | Stage 3 run log does NOT exist (only `report_step3_h3.md`) | Paper_Artifacts_Audit Layer A |
| B5 | Stage 4 run log does NOT exist | Paper_Artifacts_Audit Layer A |

### GROUP C: LaTeX Table Claims

| ID | Claim | Source |
|----|-------|--------|
| C1 | LaTeX table Within-R² is INFLATED (uses manual double-demeaned R² instead of linearmodels `rsquared_within`) | AUDIT_H3.md Finding 2 |
| C2 | Paper_Artifacts_Audit says C1 is RESOLVED — verify current LaTeX table uses correct `rsquared_within` | Paper_Artifacts_Audit Blocker #2 |
| C3 | LaTeX table missing SE clustering method note | Paper_Artifacts_Audit Blocker #3 |
| C4 | LaTeX table missing sample filter description (`is_div_payer_5yr==1`) | Paper_Artifacts_Audit Blocker #3 |
| C5 | LaTeX table missing min calls filter note (firms with <5 calls excluded) | Paper_Artifacts_Audit Blocker #3 |
| C6 | LaTeX table missing star legend (`* p<0.1, ** p<0.05, *** p<0.01`) | Paper_Artifacts_Audit Blocker #3 |
| C7 | LaTeX table missing N firms (only N observations shown) | Paper_Artifacts_Audit Notes Register #8 |

### GROUP D: Summary Stats Table Claims

| ID | Claim | Source |
|----|-------|--------|
| D1 | `summary_stats.tex` missing sample period (2002-2018) | Paper_Artifacts_Audit Minor #7 |
| D2 | `summary_stats.tex` missing winsorization note (1%/99% per year) | Paper_Artifacts_Audit Minor #7 |
| D3 | `summary_stats.tex` missing "N varies due to missing data" explanation | Paper_Artifacts_Audit Minor #7 |

### GROUP E: Diagnostic File Claims

| ID | Claim | Source |
|----|-------|--------|
| E1 | `model_diagnostics.csv` column `rsquared_adj` stores `model.rsquared_inclusive`, not adjusted R² — column is mislabeled | AUDIT_H3.md Finding 3, Paper_Artifacts_Audit Minor #8 |
| E2 | `model_diagnostics.csv` missing `#clusters` count | Paper_Artifacts_Audit Layer B |

### GROUP F: Documentation Claims

| ID | Claim | Source |
|----|-------|--------|
| F1 | `docs/provenance/H3.md` Section F.1 describes `div_stability` with wrong formula | AUDIT_H3.md Finding 1 |
| F2 | `README.md:303` says "H3b: 2/12 significant interactions" but actual is 3/36 | AUDIT_H3.md Finding 4 |

### GROUP G: Test Coverage Claims

| ID | Claim | Source |
|----|-------|--------|
| G1 | `test_h3_regression.py` assumes CENTERED interactions but actual runner uses UNCENTERED | AUDIT_H3.md Finding 5 |

### GROUP H: Cross-Artifact Consistency Claims

| ID | Claim | Source |
|----|-------|--------|
| H1 | LaTeX coefficients match `model_diagnostics.csv` exactly | AUDIT_H3.md Verification #21 |
| H2 | Regression txt coefficients match `model_diagnostics.csv` exactly | AUDIT_H3.md Verification #22 |
| H3 | Txt N matches CSV N exactly | AUDIT_H3.md Acceptance tests |

---

## PHASE 4: VERIFICATION COMMANDS REFERENCE

The following commands are SUGGESTED starting points. You MUST adapt them to the current state of the repository. Do NOT copy-paste blindly.

### File Existence Checks

```bash
# Check for run_manifest.json in latest Stage 4 output
ls -la outputs/econometric/h3_payout_policy/*/run_manifest.json

# Check for attrition table
ls -la outputs/econometric/h3_payout_policy/*/*attrition*
ls -la outputs/variables/h3_payout_policy/*/*attrition*

# Check for variable lineage JSON
ls -la outputs/variables/h3_payout_policy/*/*lineage*.json

# Check for Stage 3 log
ls -la outputs/variables/h3_payout_policy/*/*.log

# Check for Stage 4 log
ls -la outputs/econometric/h3_payout_policy/*/*.log
```

### Code Inspection Commands

```bash
# Read div_stability computation code
head -n 900 src/f1d/shared/variables/_compustat_engine.py | tail -n 50

# Read div_stability docstring
head -n 780 src/f1d/shared/variables/_compustat_engine.py | tail -n 30

# Read interaction term creation in runner
grep -n "Uncertainty_x_Lev" src/f1d/econometric/run_h3_payout_policy.py

# Read within_r2 computation
grep -n "within_r2\|rsquared" src/f1d/econometric/run_h3_payout_policy.py
```

### Data Verification Commands

```bash
# Verify panel shape
python -c "import pandas as pd; df=pd.read_parquet('outputs/variables/h3_payout_policy/*/h3_payout_policy_panel.parquet'); print(f'Rows: {len(df)}, Cols: {len(df.columns)}, file_name unique: {df.file_name.is_unique}')"

# Compare rsquared vs within_r2 in diagnostics
python -c "
import pandas as pd
from glob import glob
latest = sorted(glob('outputs/econometric/h3_payout_policy/*/model_diagnostics.csv'))[-1]
diag = pd.read_csv(latest)
print(diag[['sample','dv','uncertainty_measure','rsquared','within_r2']].head(10))
"

# Check LaTeX table for notes
grep -i "clustered\|dividend\|star\|p<0" outputs/econometric/h3_payout_policy/*/h3_payout_policy_table.tex

# Check summary_stats.tex for notes
cat outputs/econometric/h3_payout_policy/*/summary_stats.tex | tail -30
```

### Cross-Artifact Consistency Commands

```bash
# Compare LaTeX vs diagnostics for Main/DS/Mgr_QA
python -c "
import pandas as pd
from glob import glob

# Get latest diagnostics
diag_path = sorted(glob('outputs/econometric/h3_payout_policy/*/model_diagnostics.csv'))[-1]
diag = pd.read_csv(diag_path)

# Get Main/DS/Mgr_QA row
row = diag[(diag['sample']=='Main') & (diag['dv']=='div_stability_lead') & (diag['uncertainty_measure']=='Manager_QA_Uncertainty_pct')].iloc[0]

print(f'beta1: {row[\"beta1\"]:.4f}')
print(f'beta3: {row[\"beta3\"]:.4f}')
print(f'N: {int(row[\"n_obs\"])}')
print(f'rsquared: {row[\"rsquared\"]:.4f}')
print(f'within_r2: {row[\"within_r2\"]:.4f}')
"

# Read corresponding txt file
cat outputs/econometric/h3_payout_policy/*/regression_results_Main_div_stability_lead_Manager_QA_Uncertainty_pct.txt | head -30
```

---

## PHASE 5: OUTPUT DOCUMENT FORMAT

Your final output MUST be written to:
```
docs/provenance/AUDIT_REVERIFICATION_H3.md
```

### Required Document Structure

```markdown
# Audit Re-Verification Report: H3 — Payout Policy

**Audit date:** [YYYY-MM-DD]
**Auditor:** [AI model identifier]
**Source documents audited:**
- docs/provenance/H3.md
- docs/provenance/AUDIT_H3.md
- docs/provenance/Paper_Artifacts_Audit_H3.md

**Git commit at audit start:** [hash]
**Latest Stage 3 run:** [timestamp]
**Latest Stage 4 run:** [timestamp]

---

## 1) Executive Summary

| Metric | Count |
|--------|-------|
| Total claims verified | XX |
| Claims FIXED | XX |
| Claims STILL PRESENT | XX |
| Claims PARTIALLY FIXED | XX |
| Claims SUPERSEDED | XX |
| Claims UNVERIFIABLE | XX |

### Critical Blockers Remaining

[List any BLOCKER-severity issues still present]

---

## 2) Claim Ledger

[Full table from Phase 1]

---

## 3) Verification Results by Group

### GROUP A: Formula & Code Logic Claims

#### Claim A1: div_stability formula mismatch
[Full verification per Phase 2 protocol]

#### Claim A2: payout_flexibility formula
[Full verification]

#### Claim A3: Uncentered interaction terms
[Full verification]

### GROUP B: Output Artifact Claims
[... continue for all groups ...]

---

## 4) Cross-Artifact Consistency Matrix

| Check | Status | Evidence |
|-------|--------|----------|
| LaTeX vs diagnostics N | PASS/FAIL | [evidence] |
| LaTeX vs diagnostics coef | PASS/FAIL | [evidence] |
| Txt vs diagnostics N | PASS/FAIL | [evidence] |
| Txt vs diagnostics coef | PASS/FAIL | [evidence] |
| Provenance vs code formula | PASS/FAIL | [evidence] |

---

## 5) Summary of Remaining Issues

### BLOCKER (must fix before paper submission)
[List]

### MAJOR (should fix)
[List]

### MINOR (nice to have)
[List]

---

## 6) Recommended Actions

[Ordered list of specific, actionable fixes]

---

## 7) Command Log

| # | Command | Purpose | Result |
|---|---------|---------|--------|
| 1 | ... | ... | ... |

---

## 8) Confidence Assessment

| Aspect | Confidence | Justification |
|--------|------------|---------------|
| Formula verification | HIGH/MED/LOW | ... |
| Artifact existence | HIGH/MED/LOW | ... |
| Cross-artifact consistency | HIGH/MED/LOW | ... |
```

---

## PHASE 6: AUDITOR SELF-CHECK

Before submitting your report, verify:

- [ ] Every claim in the ledger has a verification section
- [ ] Every verification has EXACT command + EXACT output
- [ ] No "I believe" or "it seems" without evidence
- [ ] All file paths are absolute or clearly relative to project root
- [ ] Git commit hash is recorded
- [ ] Timestamps of latest runs are recorded
- [ ] Verdict (FIXED/STILL PRESENT/etc.) is explicit for each claim
- [ ] Summary sections accurately reflect detailed findings

---

## BEGIN AUDIT NOW

Start with PHASE 1: Extract the claim ledger. Then proceed through each verification systematically. Do not skip ahead. Do not assume. Verify everything.
