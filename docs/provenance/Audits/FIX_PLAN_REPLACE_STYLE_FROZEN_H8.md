# H8 Systematic Fix Plan: Replace style_frozen with ClarityStyle_Realtime

**Purpose:** Replace the time-invariant `style_frozen` variable with the time-varying `ClarityStyle_Realtime` variable throughout the H8 Political Risk suite.

**Rationale:**
- `style_frozen` is time-invariant within CEO tenure → only 258/1,665 firms (15.5%) have within-firm variation
- With Firm FE, coefficients identified only from CEO turnover events → very low power
- `ClarityStyle_Realtime` varies call-to-call → much more identifying variation
- Both measure CEO communication clarity, but realtime captures evolving style

---

## FILES TO MODIFY

### 1. Panel Builder: `src/f1d/variables/build_h8_political_risk_panel.py`

**Current:**
```python
from f1d.shared.variables.ceo_clarity_style import CEOClarityStyleBuilder
# ...
"style_frozen": CEOClarityStyleBuilder(config),
```

**Change to:**
```python
from f1d.shared.variables.ceo_style_realtime import CEOStyleRealtimeBuilder
# ...
"ClarityStyle_Realtime": CEOStyleRealtimeBuilder(config),
```

**Also update:**
- Interaction term: `interact = PRiskFY × ClarityStyle_Realtime` (instead of `style_frozen`)
- Any references to `style_frozen` column name

### 2. Econometric Runner: `src/f1d/econometric/run_h8_political_risk.py`

**Current formula references:**
- `style_frozen` in regression formula
- `interact` (which uses style_frozen)

**Change to:**
- `ClarityStyle_Realtime` in regression formula
- Update interaction term reference

**Also update:**
- Diagnostics column names
- LaTeX table variable labels
- Summary statistics column names
- Any hardcoded references to `style_frozen`

### 3. Provenance Documentation: `docs/provenance/H8.md`

**Update sections:**
- A4) Main RHS and Controls: Replace `style_frozen` with `ClarityStyle_Realtime`
- F) Variable Dictionary: Replace row for `style_frozen`
- H) Estimation Spec Register: Update variable names
- J) Known Issues: Remove J.7 (FE absorption) — no longer applies with time-varying variable
- Add new Known Issue about higher missingness (44.5% vs 62.8%)

### 4. README.md

**Update H8 section:**
- Replace `StyleFrozen` with `ClarityStyle_Realtime`
- Update coverage statistics
- Update interpretation

### 5. LaTeX Table Template (if hardcoded)

Check if `run_h8_political_risk.py` has hardcoded variable labels in LaTeX output.

---

## EXECUTION STEPS

### Step 1: Identify All References

Search for all occurrences of `style_frozen` in the codebase:
```bash
grep -rn "style_frozen" src/f1d/variables/build_h8_political_risk_panel.py
grep -rn "style_frozen" src/f1d/econometric/run_h8_political_risk.py
grep -rn "style_frozen" docs/provenance/H8.md
grep -rn "StyleFrozen\|style_frozen" README.md
```

### Step 2: Modify Panel Builder

File: `src/f1d/variables/build_h8_political_risk_panel.py`

1. Update import statement
2. Update builder dictionary
3. Update interaction term creation
4. Update any column name references

### Step 3: Modify Econometric Runner

File: `src/f1d/econometric/run_h8_political_risk.py`

1. Update regression formula
2. Update required columns list
3. Update diagnostics column names
4. Update LaTeX table variable labels
5. Update summary statistics

### Step 4: Update Provenance Documentation

File: `docs/provenance/H8.md`

1. Update Section A4 (RHS variables)
2. Update Section F (Variable Dictionary)
3. Update Section H (Estimation Spec Register)
4. Update Section J (Known Issues)
5. Update Section I (Verification Log)

### Step 5: Update README

File: `README.md`

1. Find H8 section
2. Update variable names
3. Update statistics

### Step 6: Verification

After changes:
1. Run Stage 3: `python -m f1d.variables.build_h8_political_risk_panel`
2. Run Stage 4: `python -m f1d.econometric.run_h8_political_risk`
3. Verify output files exist and have correct column names
4. Check model_diagnostics.csv for new variable

---

## EXPECTED CHANGES IN RESULTS

| Metric | Before (style_frozen) | After (ClarityStyle_Realtime) |
|--------|----------------------|-------------------------------|
| Variable coverage | 62.8% (18,439/29,343) | ~55% (estimated) |
| Within-firm variation | 15.5% of firms | Much higher (call-to-call) |
| Missingness reason | CEO match + min 5 calls | Min 4 prior calls |
| Interpretation | CEO trait moderation | CEO state moderation |

---

## VERIFICATION CHECKLIST

After execution, verify:

- [ ] No remaining references to `style_frozen` in H8 code
- [ ] Panel builder imports `CEOStyleRealtimeBuilder`
- [ ] Panel contains `ClarityStyle_Realtime` column
- [ ] Regression formula uses `ClarityStyle_Realtime`
- [ ] Interaction term = `PRiskFY × ClarityStyle_Realtime`
- [ ] LaTeX table shows correct variable name
- [ ] H8.md documentation updated
- [ ] README.md updated
- [ ] Stage 3 runs without error
- [ ] Stage 4 runs without error
- [ ] model_diagnostics.csv has new coefficient names

---

## ROLLBACK PLAN

If issues arise:
```bash
git checkout -- src/f1d/variables/build_h8_political_risk_panel.py
git checkout -- src/f1d/econometric/run_h8_political_risk.py
git checkout -- docs/provenance/H8.md
git checkout -- README.md
```
