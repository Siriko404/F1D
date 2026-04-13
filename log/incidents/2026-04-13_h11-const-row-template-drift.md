# Lessons Learned: H11/H11-Lag `const` Row — Template Drift

**Date:** 2026-04-13
**Severity:** Medium
**Status:** Resolved

## Incident Summary

During tier 2B/C/D spec expansion, I refactored `run_h11_prisk_uncertainty.py` and `run_h11_prisk_uncertainty_lag.py` to add a firm/industry FE dispatch. In the industry-FE branch I wrote:

```python
exog = df_panel[["PRisk"] + controls]
exog = exog.assign(const=1.0)   # ← NOT in template
model_obj = PanelOLS(
    dependent=df_panel[dv_var],
    exog=exog,
    entity_effects=False,
    time_effects=True,
    other_effects=df_panel["ff12_code"],
    drop_absorbed=True,
    check_rank=False,
)
```

The `assign(const=1.0)` added a constant column that PanelOLS estimated as a regression coefficient. Output regression files contained a `const` row with a finite coefficient; the moderation renderer in `generate_all_tables.py` parsed it as a control and added a row to `outputs/all_tables.tex`.

In the firm-FE branch I used `PanelOLS.from_formula(... + EntityEffects + TimeEffects)`, where the `1 +` intercept is absorbed by `EntityEffects` and does NOT appear as a coefficient row. So the `const` row was **asymmetrically populated**: filled in cols 1-4 (and 9-12 for H11-Lag) under industry FE, empty in cols 5-8 (and 13-16) under firm FE.

The H13.1 template I was copying does NOT add `const=1.0` — it passes `exog=df_panel[exog]` directly. I deviated from the template by adding speculative "symmetry-restoring" code based on incorrect reasoning about PanelOLS intercept handling.

**Smoke tests missed it** because they checked coefficient values and p-values on the IV (PRisk), not the full regression output. The bug was invisible until the user read the generated LaTeX table and noticed empty cells.

## Timeline

| Time | Action | Actor | Outcome |
|------|--------|-------|---------|
| ~17:55 | User: "continue" — start tier 2B (H11 refactor) | User | Task kicked off |
| ~17:55 | Read H13.1 as template for FE dispatch pattern | Claude | Copied the shape of `run_regression` branching |
| ~18:00 | Added `exog = exog.assign(const=1.0)` to H11 industry branch | Claude | **Template drift point** — deviated from H13.1 |
| ~18:01 | Smoke test H11 → "all PRisk p<0.01 significant" | Claude | Numerically correct, bug hidden |
| ~18:10 | Copied same industry-FE pattern (with `const=1.0`) to H11-Lag | Claude | Bug propagated |
| ~18:13 | Smoke test H11-Lag → "all lag1/lag2 p<0.01" | Claude | Same numerical success, bug still hidden |
| ~18:17 | Regenerated `all_tables.tex` + PDF | Claude | Published tables with const row |
| ~18:20 | Reported "PDF verified clean, only 1 pre-existing overfull hbox" | Claude | False-positive verification |
| ~18:35 | User: "we have some empty cells in several tables! read the latex file thoroughly" | User | Caught the bug |
| ~18:40 | Scanned `all_tables.tex` → found `const` rows in H11 (line 838) and H11-Lag (line 900) | Claude | Bug isolated |
| ~18:45 | Diffed H11 vs H13.1 — H13.1 has no `const=1.0`, H1.1 has no `const=1.0` | Claude | Confirmed template deviation |
| ~18:48 | User: "what's the const row? we didn't have it before" | User | Demanded explanation |
| ~18:50 | User: "/research-lessons-learned" | User | Triggered retrospective |

**Point of no return:** ~18:00, when I added `assign(const=1.0)` without checking if the template had it. From that moment, every subsequent smoke test and PDF render propagated the bug because the smoke test granularity was "does the IV coefficient exist and is it significant", not "does the regression output match the template's structure".

## Root Cause

**Template drift.** I copied a working reference implementation (H13.1's FE dispatch) but added speculative "safety" code (`assign(const=1.0)`) based on incorrect first-principles reasoning about how PanelOLS handles intercepts when `other_effects` and `time_effects` are present. The template did not need this addition, and my addition broke the template's contract.

5 Whys:
1. Why did the `const` row appear? Because I added `exog = exog.assign(const=1.0)` which PanelOLS estimated as a regression variable.
2. Why did I add that? Because I thought the industry-FE branch needed an explicit intercept to match the firm-FE branch, which uses `PanelOLS.from_formula("~ 1 + ...")`.
3. Why did I think so? Because I reasoned "the firm branch has `1 +` in the formula, so the industry branch should also have a constant, otherwise they're asymmetric".
4. Why didn't I verify the template? Because I pattern-matched H13.1's *shape* (direct PanelOLS constructor vs from_formula) but didn't diff the actual code line-by-line. I saw the shape and filled in the "missing" step from memory of how statsmodels OLS requires `add_constant`.
5. Why did I use memory-of-other-library-conventions instead of the actual template? Because there was no procedural rule telling me to diff additions against a reference template and justify any deviation before smoke-testing.

**The underlying mechanism:** PanelOLS + `other_effects` + `time_effects` absorbs the intercept via the fixed effects. No explicit constant column is needed. The `1 + ` in `from_formula` creates an Intercept that `EntityEffects` absorbs. In both branches, the intercept is absorbed — no constant regressor is required in either.

## Contributing Factors

| Category | Factor | Contribution |
|----------|--------|--------------|
| Process | No diff check between H11's industry-FE branch and H13.1 (template) before smoke test | Direct cause — a `diff` would have shown the extra `assign(const=1.0)` line |
| Technical | Smoke test checked only IV coefficient and p-value, not the list of variables in the output | Bug numerically invisible; template contract not verified |
| Human | First-principles reasoning overrode the reference template | Added speculative "symmetry" code without grounding in the library's actual behavior |
| Human | Library-convention contamination (statsmodels OLS requires `add_constant`; PanelOLS with FE does not) | I generalized from a different library's requirement |
| Process | Rush to complete tier 2B/C/D (3 tasks back-to-back) | No time spent on template diff; moved to H11-Lag within minutes |
| Communication | "Smoke test passed" report created false confidence that propagated through H11-Lag → PDF regeneration | User trusted my verification claim; bug reached PDF |
| Context | H11-Lag copied the H11 pattern without re-verification | Bug replicated without catching on second pass |

## Fixes Implemented

| Fix | Type | Location | Status |
|-----|------|----------|--------|
| Removed `exog = exog.assign(const=1.0)` from H11 industry-FE branch | Code | `src/f1d/econometric/run_h11_prisk_uncertainty.py` | Updated |
| Removed `exog = exog.assign(const=1.0)` from H11-Lag industry-FE branch | Code | `src/f1d/econometric/run_h11_prisk_uncertainty_lag.py` | Updated |
| Reran H11 and H11-Lag to regenerate outputs without const row | Execution | `outputs/econometric/h11_*/{timestamp}/` | Regenerated |
| Regenerated `all_tables.tex` and PDF | Execution | `outputs/all_tables.{tex,pdf}` | Regenerated |
| Created feedback memory: diff adapted runners against their template before smoke-testing | Rule (feedback memory) | `memory/feedback_template_diff_discipline.md` | Created |
| Updated MEMORY.md index with feedback entry | Documentation | `memory/MEMORY.md` | Updated |
| Wrote this incident report | Documentation | `log/incidents/2026-04-13_h11-const-row-template-drift.md` | Created |

## Prevention

The new `feedback_template_diff_discipline.md` rule encodes a 3-step procedure:

1. **Identify the template.** When adapting an existing runner (e.g., "copy H13.1's FE dispatch to H11"), name the exact file and function.
2. **Diff the adapted code against the template.** Every line of added/removed code must be justified. No speculative "safety" additions.
3. **Verify smoke-test granularity matches the risk.** If the change is structural (new FE branch, new DV), the smoke test must inspect the full regression output file, not just the IV coefficient.

The rule includes a red-flag list: template-drift smells that should trigger an explicit template diff before smoke-testing.

## Verification

**Test scenario (immediate):** After removing `assign(const=1.0)`, rerun H11 and H11-Lag, regenerate `all_tables.tex`, grep for `^const &` — should return 0 matches.

**Success criteria (immediate):** `grep -c "^const &" outputs/all_tables.tex` returns 0. H11 table has clean FE row structure with no spurious const row. H11-Lag same.

**Test scenario (procedural):** Next time I adapt a runner from a template, the memory entry for `feedback_template_diff_discipline.md` should surface. Before smoke-testing, I should produce a one-line justification for every deviation from the template.

**Success criteria (procedural):** Any future runner adaptation's PR description or commit message should include "Template: [path]. Deviations: [list with justification]".

**Review date:** 2026-04-27 (2 weeks). On review, check whether any runner adaptations happened in the interim and whether the deviation-justification discipline was followed.

## Lessons

1. **Copying a template means copying its deviations from your instinct, not just its shape.** A working reference is a reference because someone already solved the "how should this be structured" question. When you add code to the reference, you are claiming the reference is incomplete. That claim needs evidence, not a vague feeling of symmetry.

2. **Smoke tests verify what they're designed to verify.** A smoke test that checks `beta_prisk` p-value will not catch an extra coefficient row in the output. If the change is structural, the smoke test must include a structural check (e.g., "the list of parameters in the output matches the template's").

3. **Library conventions don't generalize across libraries.** statsmodels OLS requires `sm.add_constant`. PanelOLS with `other_effects` and `time_effects` does NOT. Generalizing "always add a constant" across libraries caused this bug. When using a library function, rely on its own documentation and its own working reference implementations, not on how other libraries in the same family behave.

4. **"Smoke test passed" is not "verified clean".** I reported "PDF verified clean, only 1 pre-existing overfull hbox" based on a grep for `Overfull` and `Error`. That report was based on pdflatex's compile status, not on the semantic correctness of the tables. A clean compile is necessary but not sufficient for a clean table. User-facing verification claims must name what was checked ("IV coefficients exist and are significant; table renders without pdflatex errors") rather than asserting broader cleanness.

5. **Rushing through a sequence of similar tasks is the ideal condition for a copy-paste bug.** Tier 2B/C/D was 3 back-to-back refactors of similar shape. The pattern "H11 worked, copy the same structure to H11-Lag" is exactly the condition under which a bug introduced in H11 propagates to H11-Lag without re-verification. The fix is not "slow down" (that's vague). The fix is "re-verify each copy against its own target, not against the previous copy".
