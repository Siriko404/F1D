# H8 Fix Execution Report: Replace style_frozen with ClarityStyle_Realtime

**Execution Date:** 2026-03-02
**Fix Plan:** `docs/provenance/FIX_PLAN_REPLACE_STYLE_FROZEN_H8.md`
**Status:** COMPLETED

---

## Summary

Successfully replaced the time-invariant `style_frozen` variable with the time-varying `ClarityStyle_Realtime` variable throughout the H8 Political Risk suite. This change improves identification with Firm Fixed Effects by providing more within-firm variation.

---

## Changes Made

### 1. Panel Builder: `src/f1d/variables/build_h8_political_risk_panel.py`

| Location | Before | After |
|----------|--------|-------|
| Line 59 (import) | `from f1d.shared.variables.ceo_clarity_style import CEOClarityStyleBuilder` | `from f1d.shared.variables.ceo_style_realtime import CEOStyleRealtimeBuilder` |
| Line 92 (agg_cols) | `"style_frozen"` | `"ClarityStyle_Realtime"` |
| Line 137-139 (create_interaction) | `df["interact"] = df["PRiskFY"] * df["style_frozen"]` | `df["interact"] = df["PRiskFY"] * df["ClarityStyle_Realtime"]` |
| Line 168 (builder dict) | `"style_frozen": CEOClarityStyleBuilder(...)` | `"ClarityStyle_Realtime": CEOStyleRealtimeBuilder(...)` |

**Additional updates:**
- Docstring updated to reflect new variable name and methodology
- Comments updated to reference `ClarityStyle_Realtime`

### 2. Econometric Runner: `src/f1d/econometric/run_h8_political_risk.py`

| Location | Before | After |
|----------|--------|-------|
| Line 101 (summary stats) | `{"col": "style_frozen", "label": "Style Frozen (Clarity)"}` | `{"col": "ClarityStyle_Realtime", "label": "Clarity Style (Realtime)"}` |
| Lines 157-170 (sanity checks) | `style_frozen` checks | `ClarityStyle_Realtime` checks |
| Lines 217-226 (required cols) | `"style_frozen"` | `"ClarityStyle_Realtime"` |
| Line 241 (formula) | `style_frozen` | `ClarityStyle_Realtime` |
| Lines 274-286 (coeff extraction) | `model.params.get("style_frozen", ...)` | `model.params.get("ClarityStyle_Realtime", ...)` |
| Lines 304-324 (meta dict) | `beta2_StyleFrozen` | `beta2_ClarityStyle_Realtime` |
| Lines 373-386 (LaTeX labels) | `"Style Frozen"` | `"Clarity Style (Realtime)"` |
| Lines 533-536 (interaction fallback) | `style_frozen` | `ClarityStyle_Realtime` |

**Additional updates:**
- Docstring updated with new formula
- Print statements updated
- LaTeX table variable labels updated

### 3. Provenance Documentation: `docs/provenance/H8.md`

- Section A4: Updated key independent variables
- Section C: Updated dependency chain and builder references
- Section E: Updated merge sequence table
- Section F: Updated variable dictionary with new ClarityStyle_Realtime row
- Section G: Updated missing data policy
- Section H: Updated estimation spec register with new results
- Section I: Updated verification log with new statistics
- Section J.1-J.2: Updated known issues (coverage and time-varying nature)
- Section J.4: Updated interaction term coverage
- **Removed** Section J.7: Limited within-firm variation issue (no longer applies)

### 4. README.md

Updated H8 section with:
- New model formula with `ClarityStyle_Realtime`
- New key variable descriptions
- Updated statistics from pipeline rerun
- Updated results table with new coefficients

---

## Pipeline Execution Results

### Stage 3 Output
- **Location:** `outputs/variables/h8_political_risk/2026-03-02_221100/`
- **Panel:** 29,343 firm-years, 14 columns
- **Duration:** 74.2 seconds

### Stage 4 Output
- **Location:** `outputs/econometric/h8_political_risk/2026-03-02_221240/`
- **Duration:** 0.5 seconds

---

## Before vs After Comparison

### Variable Coverage

| Metric | Before (style_frozen) | After (ClarityStyle_Realtime) | Change |
|--------|----------------------|-------------------------------|--------|
| Main variable coverage | 18,439 (62.8%) | 18,842 (64.2%) | +1.4 pp |
| Interaction coverage | 17,930 (61.1%) | 18,340 (62.5%) | +1.4 pp |
| Missing rate | 37.2% | 35.8% | -1.4 pp |

### Regression Sample

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| N observations | 15,721 | 15,998 | +277 |
| N firms | 1,665 | 1,943 | +278 |
| Within-R² | 0.0249 | 0.0250 | +0.0001 |

### Coefficient Results (Primary Spec)

| Coefficient | Before | After |
|-------------|--------|-------|
| β₁ (PRiskFY) | -8.1e-06 (p=0.212) | -9.3e-06 (p=0.198) |
| β₂ (Style) | -0.0077 (p=0.050) | -0.0003 (p=0.803) |
| β₃ (Interact) | 1.7e-06 (p=0.776) | -7.7e-08 (p=0.986) |
| **H8 Supported** | No | No |

---

## Key Findings

1. **Coverage improved slightly** (+1.4 percentage points) due to lower minimum call requirement (4 vs 5)

2. **Sample size increased** (+277 observations, +278 firms) due to improved coverage

3. **H8 still not supported** - the interaction coefficient remains not significant at conventional levels

4. **Within-firm variation issue resolved** - the time-varying nature of `ClarityStyle_Realtime` provides much more within-firm variation for identification with Firm FE

5. **β₂ coefficient changed dramatically** - from marginally significant (-0.0077, p=0.050) to null (-0.0003, p=0.803), suggesting the previous result may have been driven by the limited within-firm variation in the time-invariant `style_frozen`

---

## Output Files

### New Panel
- `outputs/variables/h8_political_risk/2026-03-02_221100/h8_political_risk_panel.parquet`
- `outputs/variables/h8_political_risk/2026-03-02_221100/summary_stats.csv`
- `outputs/variables/h8_political_risk/2026-03-02_221100/report_step3_h8.md`

### New Regression Output
- `outputs/econometric/h8_political_risk/2026-03-02_221240/h8_political_risk_table.tex`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/model_diagnostics.csv`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/regression_primary.txt`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/regression_main.txt`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/sanity_checks.txt`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/summary_stats.csv`
- `outputs/econometric/h8_political_risk/2026-03-02_221240/summary_stats.tex`

---

## Verification Checklist

- [x] No remaining references to `style_frozen` in H8 code (verified via grep)
- [x] Panel builder imports `CEOStyleRealtimeBuilder`
- [x] Panel contains `ClarityStyle_Realtime` column
- [x] Regression formula uses `ClarityStyle_Realtime`
- [x] Interaction term = `PRiskFY × ClarityStyle_Realtime`
- [x] LaTeX table shows correct variable name ("Clarity Style (Realtime)")
- [x] H8.md documentation updated
- [x] README.md updated
- [x] Stage 3 runs without error
- [x] Stage 4 runs without error
- [x] model_diagnostics.csv has new coefficient names (`beta2_ClarityStyle_Realtime`)

---

## Conclusion

The migration from `style_frozen` to `ClarityStyle_Realtime` was completed successfully. The new time-varying measure provides better identification properties with Firm Fixed Effects. However, H8 remains unsupported - CEO speech vagueness does not significantly moderate the political risk to abnormal investment relationship in this sample.
