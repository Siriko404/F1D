# Compaction Handoff — Boasiako Eq 1 SHIPPED + Chen Phase 1C in progress

**Date**: 2026-05-09
**Master HEAD**: `ae6050d` (10 atomic commits this session)
**Plan**: `~/.claude/plans/staggered-firm-cascade.md` v2 (ratified 2026-05-09)
**Audit memo**: `tmp/boasiako_chen_plan_audit_findings_2026_05_09.md` (af9bcfb73742b167c)
**Spec anchor**: `tmp/3did_replication_v2_2026_05_08.md` Sections B + C
**Phase 1A summary**: `outputs/econometric/h1_5_disclosure_law_did/<latest>/report_step4_H1_5_disclosure_law_did.md`

## Read-FIRST after /compact

1. This file
2. `~/.claude/plans/staggered-firm-cascade.md` (plan v2 — 23 audit findings resolved)
3. `~/.claude/projects/<id>/memory/project_session_2026_05_09_boasiako_chen_phase1.md` (durable memory)
4. `git log --oneline -15` to re-orient

## Current state

**Phase 1A Boasiako Eq 1**: COMPLETE (6/6 tasks shipped + 14/14 cells produced)
**Phase 1C Chen**: 3/8 tasks shipped (C0 bridge, C1 FF48, C2 treatment); 5 tasks remaining (C3 controls, C4 industry CF vol FF48, C5 PSM, C6 PS_DEMAND, C7 runner)

## 10 atomic commits this session (`5438450` → `ae6050d`)

```
5438450  Phase 1A [#A2 _compustat_annual_reader]      shared utility, decimal-trap+loc=USA
3f7adb8  Phase 1A [#A3 ff49_industry_classifier]      Ken French SIC ranges
5bac756  Phase 1A [#A4 boasiako_disclosure_law_treatment]  Y+1 staggered, 46+4-never-treated states
1c2895c  Phase 1A [#A5 boasiako_eq1_controls]         11 controls + winsorize
ba377ae  Phase 1A [#A6 boasiako_industry_cf_vol]      FF49 industry-MEAN, 10y σ, ≥3y floor
de5bda4  Phase 1A [#A7 run_h1_5_disclosure_law_did]   14-cell runner — DECISION-GATE FIRED but Sina PROCEED
10d50b4  Phase 1C [#C0 chen_aa_to_gvkey_bridge]       NEW v2 audit C1 critical
f57f651  Phase 1C [#C1 ff48_industry_classifier]      Ken French Siccodes48
ae6050d  Phase 1C [#C2 chen_restatement_treatment]    3-variant classifier (A/B/C); Variant B=263 vs Chen 270
```

## Phase 1A headline result (decision-gate fired but PROCEED ratified)

```
COL  DV               TREATMENT       FE                              N      BETA    P_ONE    SIG
1    cash             Disclosure_Law  industry+state+year (BASELINE) 49,402 +0.0262   0.012   **
2    cash             Disclosure_Law  firm+year                      49,402 +0.0580  <0.001  ***
3    cash             Disclosure_Law  ind+state+year excl CA         41,160 +0.0110   0.232   NS
4    cash             Disclosure_Law  ind+state+year excl 2007-09    37,970 +0.0317   0.022   **
5    UncResCEO_c      Disclosure_Law  industry+state+year             9,709 +0.0082   0.216   NS
6    UncResCEO_c      Disclosure_Law  firm+year                       9,709 +0.0061   0.310   NS
7    UncResCEO_c      Disclosure_Law  ind+state+year excl CA          8,174 +0.0015   0.455   NS
8    UncResCEO_c      Disclosure_Law  ind+state+year excl crisis      7,399 +0.0105   0.141   NS
9-14 UncResCEO_c × {Small/Young/NonDiv} × DL × {ind+state+year, firm+year}  ALL NULL
```

**Interpretation**:
- Direction ✓ correct (positive cash); statistical sig ✓ in 3/4 cash cells; CA-exclusion behavior ✓ matches paper (β drops to NS); crisis-exclusion behavior ✓ matches paper.
- **Magnitude**: F1D col 1 +0.0262 vs paper +0.0076 = **3.4× larger**; col 2 +0.058 vs paper +0.0056 = **10× larger**. Outside ±20% decision-gate tolerance.
- Speech null in all 10 specs — pattern matches Brexit/Trump/Redistricting (4-for-4 NULL).
- **Sina decision 2026-05-09**: PROCEED to Chen (treat as loose qualitative replication; magnitude divergence documented).

**Magnitude divergence candidates** (NOT diagnosed yet — defer to optional iter 2):
- F1D Compustat-only universe vs paper's CRSP-Compustat-MERGED (smaller universe → cleaner sample)
- CF formula Bates 2009 interpretation vs paper's exact Compustat fields (audit M3 deviation)
- Winsorization scope or partition cutoff interpretation differences

## Phase 1C empirical baseline (post-C2)

```
EMPIRICAL VARIANT COUNTS (post-bridge + first-only dedup + Chen-window + SIC excl):
   Variant A   IRREG=75    ERROR=1813   audit predicted 89
   Variant B   IRREG=263   ERROR=1625   audit predicted 311 ★ closest to Chen 270 (3% off)
   Variant C   IRREG=266   ERROR=1622   audit predicted 315
   TOTAL = 1888 first-restatement firms
```

Variant B at 263 vs Chen target 270 = **3% off** — strong empirical match. Plan v2 expected primary winner = B; confirmed.

## Sina decisions ratified this session

| Decision | Lock | When |
|---|---|---|
| Q1 Chen classifier | 3-variant sensitivity table (A/B/C) | 2026-05-09 |
| Q2 Boasiako scope (v1) | BOTH Eq 1 + Eq 2 | 2026-05-09 |
| Q2 Boasiako scope (v2 OVERRIDE) | Eq 1 ONLY (audit C2: PRC unreachable) | 2026-05-09 (post-audit) |
| Q3 Speech channel partitions | INCLUDE on UncResCEO_c | 2026-05-09 |
| Q4 Cash robustness ladder | SKIP per Brexit pattern | 2026-05-09 |
| Plan v2 ratification | Approve as written | 2026-05-09 |
| Phase 1A decision-gate (post-baseline) | PROCEED to Chen (loose replication) | 2026-05-09 |

## Critical learnings (do NOT re-litigate)

1. **AA Audit Analytics has NO gvkey field** — only `company_fkey` = CIK. CCM bridge MANDATORY (audit C1). Implemented in Task C0; retention 44.6% (below audit's 60-70% expectation; possibly different scope).

2. **PRC data unreachable** — Boasiako Online Appendix has only PDF, privacyrights.org requires purchase, Wayback 4-5d brittle. Phase 1B ABORTED.

3. **linearmodels.PanelOLS max-2-effects limit** — for industry+state+year FE (3 dimensions), use `time_effects=True (year) + other_effects=ff49 (industry) + state DUMMIES added to exog`. drop_absorbed=True handles collinearity.

4. **Trump `_fit_one()` cross-cutting refactor was DEAD WEIGHT** (audit M0a) — runners clone Brexit (which has its OWN _fit_one), not Trump. Bake clusters_col DIRECTLY into new clones at clone time.

5. **Datetime sentinel for LINKENDDT='E'** — use `2099-12-31` not `9999-12-31` (datetime64[ns] max ≈ 2262-04-11; 9999 overflows).

6. **Boasiako CF formula = Bates 2009 interpretation** — `(OIBDP-XINT-TXT-DVC)/AT`; spec wording "earnings after interest, dividends, and taxes but before depreciation" is non-standard (audit M3 deviation).

7. **F1D Compustat Annual reader applies decimal.Decimal trap guard** (Brexit Phase 1 lesson) + `loc=='USA'` filter (audit M7). Universal pre-req for all Boasiako/Chen builders.

8. **Magnitude divergence in Boasiako Eq 1** (3-10× larger than paper) — DOCUMENTED but not diagnosed. Sina ratified PROCEED.

9. **Speech null pattern is now 4-for-4** (Brexit, Trump, Redistricting, Boasiako). Story B speech-validation requires Chen as last hope.

## Files created this session (12 source + 6 tests)

### Phase 1A (6 tasks):
- src/f1d/shared/_compustat_annual_reader.py
- src/f1d/shared/variables/ff49_industry_classifier.py
- src/f1d/shared/variables/boasiako_disclosure_law_treatment.py
- src/f1d/shared/variables/boasiako_eq1_controls.py
- src/f1d/shared/variables/boasiako_industry_cf_vol.py
- src/f1d/econometric/run_h1_5_disclosure_law_did.py

### Phase 1C (3 tasks so far):
- src/f1d/shared/variables/chen_aa_to_gvkey_bridge.py
- src/f1d/shared/variables/ff48_industry_classifier.py
- src/f1d/shared/variables/chen_restatement_treatment.py

### Tests:
- tests/test_compustat_annual_reader.py (7 PASS)
- tests/test_ff49_industry_classifier.py (7 PASS)
- tests/test_boasiako_disclosure_law_treatment.py (8 PASS)
- tests/test_boasiako_eq1_controls.py (5 PASS)
- tests/test_boasiako_industry_cf_vol.py (5 PASS)
- tests/test_chen_aa_to_gvkey_bridge.py (7 PASS + 1 SKIP)
- tests/test_ff48_industry_classifier.py (5 PASS)
- tests/test_chen_restatement_treatment.py (9 PASS)

**Total: 53 tests PASS + 1 SKIP across 8 test files.**

## Phase 1C remaining (5 tasks)

Per plan v2 + plan-deviation log:

1. **C3** `chen_baseline_controls.py` — 8 vars per spec C3 (Q SIZE CF NWC LEV SIGMA NSEG AGE)
   - DV-different from Boasiako: CF=#OANCF/#AT (NOT Bates 2009)
   - Q=(#AT+(#PRCC_F·#CSHO−#CEQ))/#AT
   - NWC=(#ACT−#CHE−#LCT+#DLC)/#AT (audit-corrected)

2. **C4** `chen_industry_cf_vol_ff48.py` — distinct from Boasiako:
   - FF48 (not FF49)
   - industry-MEDIAN (not industry-MEAN)
   - 10y window, ≥3y floor

3. **C5** `chen_psm_matching.py` — adapts brexit_psm_matching template:
   - 1:1 NN no-replace WITHIN FF48 industry (vs Brexit pure NN)
   - Audit M2 small-industry fallback: if pool <5 → widen to nearest FF12
   - Audit V4 NO caliper; force 1:1; flag if median |p_t-p_c| >0.10
   - X1∪X2∪X3 covariate set; t-3..t-1 predictor avg; year-0 score

4. **C6** `chen_ps_demand.py` — composite mean of percentile ranks:
   - IND_STDCF (FF48 industry-MEDIAN OCF σ over 10y)
   - IND_STDQ  (FF48 industry-MEDIAN Q σ over 10y)
   - NEG_IND_CORR (-1 × corr of industry-MEDIAN CF, industry-MEDIAN Q over 10y)
   - Audit V2: percentile rank applied AFTER -1× flip

5. **C7** `run_h1_5_restatement_did.py` — biggest task ~2.5d:
   - Per-cell + Wald-difference structure (audit M1; NOT interaction-term)
   - 24 cells × 3 variants = 72 cells
   - clusters_col='matched_pair_year' baked into Brexit-cloned _fit_one() (audit M0a pattern)
   - Audit M5 pre-flight: estimate UncResCEO_c sample at year-0 ± 3; flag if <150 firm-events

## After /compact, next-session checklist

1. Read this file FIRST
2. Read `~/.claude/projects/<id>/memory/project_session_2026_05_09_boasiako_chen_phase1.md` (durable memory)
3. Read MEMORY.md index for current state
4. Re-orient: `git log --oneline -15`
5. Re-read plan v2 if needed: `~/.claude/plans/staggered-firm-cascade.md`
6. Re-read audit memo: `tmp/boasiako_chen_plan_audit_findings_2026_05_09.md`
7. Continue Phase 1C task C3 (`chen_baseline_controls.py`) per plan v2 module spec

## Phase 1A vs Brexit pattern comparison

| Dimension | Brexit (shipped) | Boasiako Eq 1 (this session) |
|---|---|---|
| Decision-gate | None (16/16 ran clean) | TRIGGERED (3-10× magnitude); Sina PROCEED |
| Cash result | DiD_10K SIG (β=+0.062 to +0.072) | Disclosure_Law SIG (β=+0.026 to +0.058) |
| Speech result | NULL (one-tail POS) | NULL (one-tail POS) |
| Pattern | Cash sig + speech null | Cash sig + speech null + magnitude divergence |
| Story B implication | Cash-only doesn't validate joint indicator | Same; speech-validation defer to Chen |

## Open questions / next-session decisions

1. **Phase 1A magnitude divergence** — defer diagnostic to optional iter 2 OR investigate now? Sina ratified PROCEED but root-cause unresolved.
2. **Chen Phase 1C remaining** — continue C3 → C7 in next session.
3. **§III.E.4 prose update** — Phase 2 separate session; needs to frame Boasiako magnitude divergence + speech null + 4-for-4 null pattern.
4. **Brexit Phase 1 iter 2 robustness** — still optional ~3hr; not started.

## Status summary

```
Master HEAD       ae6050d
Phase 1A          COMPLETE 6/6 (decision-gate fired; Sina PROCEED)
Phase 1C          IN PROGRESS 3/8
Total commits     10 atomic this session
Total tests       53 PASS + 1 SKIP across 8 files
Time elapsed      ~2 hours work (much faster than plan v2's ~25-day estimate)
Tree status       clean (2 pre-existing M files unrelated to session)

Awaiting: Sina direction post-/compact (continue C3 vs alternative).
```

**End of compaction handoff.**
