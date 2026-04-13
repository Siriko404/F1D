# Archived: Invalidated audit cycle (2026-04-02 / 2026-04-03)

**Status: INVALIDATED. Do not use any empirical conclusions from these files.**

## Why these files are here

The 2026-04-02/03 audit cycle produced a panel of robustness analyses (NoCEO
decomposition, UncAnsMgr-only single-IV, no-lagged-DV, CEO-presence probit,
PRisk AR(1)) and a 5-reviewer R2 panel that scored the thesis 64/100 (Minor
Revision). Every empirical conclusion in these reports depends on the central
manager-uncertainty measure family `UncAnsMgr` / `UncPreMgr` / `UncAnsNoCEO` /
`UncPreNoCEO`.

On 2026-04-09, the underlying speaker classifier was found to be broken:

- `src/f1d/text/build_linguistic_variables.py::flag_speakers()` applies a
  45-keyword substring regex with no word boundaries, no published precedent,
  and systematic false positives (sell-side analyst titles leaking into the
  "manager" group, `MD` matching "MD&A", `CA` matching "CASE", etc.).
- The keyword file `inputs/Manager_roles/managerial_roles_extracted.txt` has
  no provenance and contains non-corporate words (COACH, CAPTAIN, PROVOST,
  DEAN, RECTOR, GOVERNOR).
- Root cause audit: `memory/project_manager_classifier_audit_and_plan.md`.

Because every robustness analysis is a transformation of the broken measure,
the adversarial findings in these reports are not load-bearing and cannot be
cited. The associated outputs (11 robustness directories under
`outputs/econometric/h*/2026-04-03_*_{single_iv,no_lagged_dv,nonceo_decomp}`)
have been deleted. The CEO-presence probit and PRisk AR(1) scripts and outputs
have also been deleted.

## Why the files are kept at all

These reports document the rationale for several methodology improvements that
are still live in the pipeline:

1. **Two-way clustering** (firm x calendar-time) in all main runners
   (`cluster_time=True`) — Decision 7 in `revision_decisions.md`.
2. **DV mean row** in LaTeX tables — Decision 3.
3. **One-SD standardized effects** reporting — Decision 3.
4. **R-squared footnote** ("$R^2$ is overall, not within") — Decision 13.
5. **IV_NAMES bug fix** in `generate_thesis_tables.py` / `generate_all_tables.py`
   — found by `second_layer_audit.md`; the fix is correct regardless of
   whether UncAnsMgr itself is valid.

Keeping these reports archived (rather than deleting them outright) preserves
the provenance trail for those surviving improvements.

## What is NOT in this archive

- `nonceo_decomposition_audit.md` referenced `model_diagnostics.csv` files
  inside the now-deleted robustness output directories. Those CSVs are gone;
  the audit report text remains but its numerical claims can no longer be
  reverified against source data.

## File inventory

| File | Origin |
|---|---|
| `editorial_decision_package.md` | R1 editor panel package |
| `paper_review_findings_and_tables.md` | R1 reviewer panel findings |
| `revision_decisions.md` | Decisions 1-13 (most are invalidated; #3, #7, #13 remain as live methodology) |
| `editorial_decision_package_r2.md` | R2 editor panel package (64/100 Minor Revision) |
| `r2_rereview.md` | R2 reviewer panel re-review |
| `devils_advocate_rereview.md` | Adversarial reviewer — central "null across ALL 60 specs" claim was empirically wrong by 7 cells |
| `nonceo_decomposition_audit.md` | Second-layer audit that verified NoCEO counts and caught the DA's counting errors |
| `second_layer_audit.md` | Meta-audit that found the IV_NAMES bug in table generators |

## Do not reference

Do not cite any empirical finding, score, count, or decision from these files
in the thesis, the findings narrative, memory files, or downstream code.
Specifically: the "coverage artifact" framing, the R1-R8 / S1-S8 / N1-N7
revision roadmap, and the 64/100 score are all contingent on a measure that
is broken.
