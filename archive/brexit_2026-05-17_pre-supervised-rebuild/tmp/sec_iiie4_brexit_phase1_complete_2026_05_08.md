# Brexit DiD (H1.5.brexit_did) — Phase 1 Complete

**Date**: 2026-05-08 PM-late+9h
**Plan reference**: `~/.claude/plans/tender-popping-origami.md` (632 lines)
**Spec anchor**: `tmp/3did_replication_v2_2026_05_08.md` Section A (lines 74-960)
**Status**: BASELINE 16-cell SHIPPED; full-ladder robustness DEFERRED per Sina mid-Phase-1 decision (cash not novel claim, speech null - low marginal value).

---

## Executive summary

13 modules built, tested, atomic-committed. 16/16 baseline cells produced in 8.2s.

- **Cash response sig** on DiD_10K x Post (cols 5-8): β = +0.062 to +0.072 (all 4 FE; p_one = 0.014 to 0.049). Replicates Campello et al 2022 JFQA Table 8 cash result with smaller magnitude (Campello +0.357***) consistent with F1D-call-panel restriction + HIGH_10K classifier dilution.
- **Cash null** on DiD_BetaUK x Post (cols 1-4): β tiny / NS / wrong-sign in firm FE. F1D-relative tercile breakpoints (0.20/0.53) deviate from Campello universe-specific 0.28/0.68; within-firm β^UK ranking may not align with cross-firm classification on this measure.
- **Speech null** under one-tailed POS hypothesis (cols 9-16): DiD_BetaUK NS (β tiny), DiD_10K wrong-sign (treated firms show LESS speech-uncertainty post-Brexit; 2-tailed sig but excluded from headline reporting per H1's POS-hypothesis convention).

§III.E.4 narrative consistency: Brexit fits the Trump+Redistricting null pattern on speech; cash response confirms macro-shock can activate precautionary cash but does NOT validate F1D's joint-indicator (cash+speech) Story B. Story B validation must come from Boasiako or Chen.

---

## Modules shipped (13 + 4 inline-test files)

| # | Module | Status | Verification |
|---|--------|--------|--------------|
| #94 | CRITICAL-4 cluster SE refactor (Trump runner _fit_one) | ✅ | AST OK; backward-compat for Trump default |
| #95 | brexit_treatment_beta_uk.py + CLI | ✅ | 3,781 firms / 848 treated / 848 control / 9.6s |
| #96 | scripts/brexit/parse_10k_keywords.py ETL | ✅ | 9,270 filings / 47% gvkey-coverage / 226s |
| #97 | brexit_treatment_10k.py + CLI | ✅ | HIGH=2,847 / 0=261 / 0.04s |
| #98 | brexit_macro_controls.py + CLI | ✅ | 28/28 quarters / 0 NaN / 1.2s |
| #99 | brexit_consensus_eps.py + CLI | ✅ | 76K rows / 4,558 gvkeys / 10s |
| #100 | hoberg_phillips_fic100.py + CLI + 4 pytest | ✅ | 29,482 rows / 5,823 gvkeys / 95 industries / 0.4s |
| #101-104 | 4 Brexit-verbatim controls + CLI + 16 pytest | ✅ | 14.4s combined / 16/16 PASS |
| #105 | brexit_psm_matching.py + CLI | ✅ | 382+138 matched pairs / 1.9s |
| #106 | brexit_parallel_trends.py utility + 5 pytest | ✅ | F-stat function works on synthetic / 5/5 PASS |
| #107 | run_h1_5_brexit_did.py BASELINE 16 cells | ✅ | 8.2s / 16/16 cells / cash sig on DiD_10K |
| #108 | inline tests | ✅ | 25/25 PASS across builder + utility tests |
| #109 | EDITS (__init__.py + suite_render_order.yaml + _ibes_engine.py:45) | ✅ | imports OK |
| #110 | Phase 1 verification (THIS MEMO) | ✅ | reproducible 16/16 |

DEFERRED to Phase 1 iteration 2 (per Sina decision):
- Robustness 25 cells (Trump-excl + Cameron + Debt-Ceiling + PSM + parallel-trends)
- §III.E.4 prose update + main.pdf recompile (Phase 2, separate session per plan)

---

## Atomic commits (15 total this session)

```
3bd7715  CRITICAL-4 cluster SE refactor
dafeeea  beta^UK builder + CLI (PASS)
86107f0  10-K parser ETL (PASS, 9,270 filings)
ddc5d56  brexit_treatment_10k builder (PASS)
8c96a78  brexit_macro_controls builder (PASS, 28/28)
63260e5  brexit_consensus_eps builder (PASS, 76K rows)
0331fb1  advisor-flagged corrections (HIGH_10K rationale + beta^UK SE docstring)
c3050e4  hoberg_phillips_fic100 builder + 4 inline tests (PASS)
91fec15  4 Brexit-verbatim controls + 16 inline tests (PASS)
3f38fe1  brexit_psm_matching builder (PASS, 1:1 NN)
3d63918  brexit_parallel_trends utility + 5 inline tests (PASS)
f981a9e  run_h1_5_brexit_did 16-cell baseline (PASS, 8.3s, SIG on DiD_10K cash)
f24b200  EDITS - register builders + suite + IBES comment fix
```

Master HEAD: `f24b200`.

---

## Headline regression table (16-cell baseline)

```
col  dv             treatment   fe          n      beta     p_one  sig
 1   cash_brexit_dv DiD_BetaUK  industry    9138  +0.0064   nan    -
 2   cash_brexit_dv DiD_BetaUK  firm        9138  -0.0307   0.991  - (wrong-sign)
 3   cash_brexit_dv DiD_BetaUK  industry_yq 9138  +0.0074   nan    -
 4   cash_brexit_dv DiD_BetaUK  firm_yq     9138  -0.0306   0.991  - (wrong-sign)
 5   cash_brexit_dv DiD_10K     industry   21533  +0.0717   0.014  **
 6   cash_brexit_dv DiD_10K     firm       21533  +0.0624   0.049  **
 7   cash_brexit_dv DiD_10K     industry_yq 21533 +0.0712   0.015  **
 8   cash_brexit_dv DiD_10K     firm_yq    21533  +0.0625   0.049  **
 9   UncResCEO_c    DiD_BetaUK  industry    7063  -0.0052   0.581  -
10   UncResCEO_c    DiD_BetaUK  firm        7063  -0.0017   0.528  -
11   UncResCEO_c    DiD_BetaUK  industry_yq 7063  -0.0056   0.587  -
12   UncResCEO_c    DiD_BetaUK  firm_yq     7063  -0.0017   0.527  -
13   UncResCEO_c    DiD_10K     industry   16804  -0.0729   1.000  -  [2-tail sig wrong-sign; not reported]
14   UncResCEO_c    DiD_10K     firm       16804  -0.0613   0.996  -  [2-tail sig wrong-sign; not reported]
15   UncResCEO_c    DiD_10K     industry_yq 16804 -0.0729   1.000  -  [2-tail sig wrong-sign; not reported]
16   UncResCEO_c    DiD_10K     firm_yq    16804  -0.0612   0.996  -  [2-tail sig wrong-sign; not reported]
```

p_one = one-tailed POS test (H1's hypothesis is uniformly POS).

---

## Notable corrections during Phase 1 (advisor + evidence-based)

1. **HIGH_10K Campello-gap rationale** (advisor mid-review): My initial commit message claimed "F1D includes full SEC filer universe vs Campello Compustat" — WRONG. Both samples are Compustat-mapped. Diagnostic localizes mechanism: dropping "uncertainty"+"uncertain" reduces F1D HIGH=2,847 → 994 (much closer to Campello 807). n_brexit=0 across all 3,820 firms is CORRECT (2015 10-Ks pre-date the term's widespread use). Decision: KEEP 9-keyword pure tally per spec verbatim; document gap in plan-deviation log.
2. **β^UK SE column** (advisor): classical homoskedastic OLS — DIAGNOSTIC ONLY (treatment classifier reads only point estimate + tercile rank).
3. **Inline tests** (advisor): tests-as-you-go pattern adopted from #100 onward (NOT batched at #108). Caught the decimal.Decimal Compustat dtype issue at first run of #101-104.

---

## Plan-deviation log (key entries)

- Robustness ladder: FULL LADDER REVISED to BASELINE-ONLY per Sina mid-Phase-1 decision (cash result is Campello-replication, not F1D's novel claim; speech null kills joint-indicator validation; remaining robustness has low marginal value)
- Tercile breakpoints β^UK: F1D-relative (0.20/0.53) vs Campello (0.28/0.68) — universe-specific
- Consensus EPS standardization: within-firm z-score over firm's full IBES sample 2000-2025
- Cash DV: cheq / lag(atq - cheq) per Table 8 footer (BKS net-assets), distinct from F1D-canonical CashRatio

---

## Open / next session

1. **Boasiako DiD (H1.5.databreach_did)**: state-level data-breach laws staggered DiD per spec Section B (Boasiako-O'Connor Keefe 2020 EFM verbatim). May give the speech response F1D's joint-indicator Story B needs.
2. **Chen DiD (H1.5.restatement_did)**: firm-event restatement DiD per spec Section C. F1D-overlap 4 yrs caveat acknowledged.
3. **Brexit Phase 2** (separate session per plan): §III.E.4 prose update + main.pdf recompile. Notes:
   - Brexit cash sig framed as Campello-replication (not novel)
   - Brexit speech null framed alongside Trump+Redistricting null pattern
   - Set up triangulation: Boasiako/Chen carry the speech-validation lift
4. **Brexit Phase 1 iteration 2** (optional): if Sina wants robustness post-prose, Trump-excl + parallel-trends F-stats + PSM matched re-run all sit on top of existing infra (~3 hours total).

---

## Files written this session (gitignored not committed)

- `inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_daily.csv` (1,293 daily rows; needed for monthly realized vol computation in β^UK; previous monthly file was insufficient)
- `outputs/intermediate/brexit_10k_keyword_counts/<ts>/` (9,270 filings cache + parse_manifest)
- `outputs/variables/{brexit_treatment_beta_uk,brexit_treatment_10k,brexit_macro,brexit_consensus_eps,hoberg_phillips_fic100,brexit_tobins_q,brexit_sales_growth,brexit_stock_return,brexit_cash_flow,brexit_psm_matching}/<ts>/`
- `outputs/econometric/h1_5_brexit_did/<ts>/` (model_diagnostics.csv + report.md + suite_spec.json)
- 4 timestamped output dirs from end-to-end re-run.

---

## Verification artifacts

- 25 inline pytest cases PASS (4 FIC100 + 16 Brexit-verbatim controls + 5 parallel-trends)
- 14 regex unit-test cases PASS (12 strict + 2 with documented edge-case exceptions)
- Brexit runner produces deterministic 16/16 cells in 8.2s on second run.

---

**STATUS**: Phase 1 baseline COMPLETE. Awaiting Sina decision on next DiD (Boasiako vs Chen) or Phase 2 prose work.
