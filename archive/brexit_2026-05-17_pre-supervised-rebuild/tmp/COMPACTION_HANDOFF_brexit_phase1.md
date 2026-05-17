# Compaction Handoff — Brexit DiD Phase 1 Baseline Shipped (2026-05-08 → 2026-05-09 carry-over)

> **Future-Claude: read this FIRST after `/compact`.** Pairs with the durable
> memory file at `~/.claude/projects/<id>/memory/project_session_2026_05_08_v4_brexit_phase1_baseline_shipped.md`
> and the per-task summary at `tmp/sec_iiie4_brexit_phase1_complete_2026_05_08.md`.

## Bottom-line state

- **Brexit DiD H1.5.brexit_did Phase 1 BASELINE SHIPPED.** 16/16 baseline cells produced.
- **Master HEAD**: `dd4d212` (14 atomic commits this session). Tree-clean except for two pre-existing M files unrelated to this session (`.claude/settings.local.json`, `docs/Prompts/Red Team Plan Audit prompt.txt`).
- **All 17 plan tasks COMPLETE** (Tasks #94–#110 in the TaskList — see status block at end).

## The 14 commits (work units, in chronological order)

```
3bd7715  CRITICAL-4 cluster SE refactor (Trump runner _fit_one parameterized)
dafeeea  brexit_treatment_beta_uk.py + CLI (PASS, 3,781 firms / 9.6s)
86107f0  parse_10k_keywords.py ETL one-shot (PASS, 9,270 filings / 226s)
ddc5d56  brexit_treatment_10k.py + CLI (PASS, HIGH=2,847 / 0=261)
8c96a78  brexit_macro_controls.py + CLI (PASS, 28/28 quarters 0 NaN)
63260e5  brexit_consensus_eps.py + CLI (PASS, 76K rows / 4,558 gvkeys / 10s)
0331fb1  Advisor-flagged corrections (HIGH_10K rationale, beta^UK SE diagnostic-only)
c3050e4  hoberg_phillips_fic100.py + CLI + 4 inline tests (PASS, 95 industries)
91fec15  4 Brexit-verbatim controls + CLI + 16 inline tests (PASS, 14.4s combined)
3f38fe1  brexit_psm_matching.py + CLI (PASS, 382+138 matched pairs / 1.9s)
3d63918  brexit_parallel_trends.py utility + 5 inline tests (PASS)
f981a9e  run_h1_5_brexit_did.py 16-cell baseline (PASS, 8.3s, SIG on DiD_10K cash)
f24b200  EDITS — register builders + suite_render_order.yaml + IBES line 45 fix
dd4d212  Phase 1 verification — summary memo (THIS COMPACTION HANDOFF FILE WAS WRITTEN AFTER THIS)
```

## Headline finding

**Cash DiD_10K × Post: SIG on ALL 4 FE configurations.**
   β = +0.062 to +0.072 (cols 5–8), p_one = 0.014 to 0.049.
   Replicates Campello et al 2022 JFQA Table 8 (their +0.357***); F1D's 5×-smaller
   magnitude consistent with F1D-call-panel restriction + HIGH_10K classifier
   dilution (F1D 2,847 vs Campello 807).

**Cash DiD_BetaUK × Post: NS / wrong-sign in firm FE.**
   F1D-relative tercile breakpoints (0.20/0.53) deviate from Campello (0.28/0.68).
   Within-firm β^UK ranking may not align with cross-firm classification.

**Speech (UncResCEO_c) under one-tailed POS hypothesis: NS (all 8 cells).**
   - DiD_BetaUK: β tiny (-0.002 to -0.006), NS in both directions
   - DiD_10K: 2-tailed sig but WRONG-SIGN — under H1's uniformly-POS hypothesis
     convention, NOT REPORTED (Sina lock 2026-05-08).

## Sina's two key Phase-1 reframing decisions

**DECISION 1 (mid-Phase-1, after baseline 16/16 ran).**
> Sina: "do we still have to do these tests since speech was null? cash is already
> studied and is not our DiD main aim."

Translation: Cash response is a Campello-published finding (their headline). F1D's
novel claim is the *speech-as-precautionary-indicator* extension via UncResCEO_c
(Story B joint-indicator framing). Speech null on Brexit means Brexit DiD does NOT
validate F1D's novel claim. Robustness ladder for the cash result (which we don't
claim novelty on) has low marginal value.

**Action taken**: SKIP full-ladder robustness (Trump-excl + Cameron + Debt-Ceiling
+ PSM + parallel-trends — 25 cells worth). Ship Phase 1 as baseline-only. Plan
budget revised from 22.5d → ~half-day actual delivery.

**DECISION 2 (mid-Phase-1, on speech wrong-sign reading).**
> Sina: "two tailed is not supported by our hypothesis, so we dont even do it
> and dont report it."

Translation: H1 family hypothesis is uniformly one-tailed POS. The wrong-sign
2-tailed-sig DiD_10K speech result (cols 13-16) is not within hypothesis space;
we don't pivot to two-tailed reporting for non-hypothesis findings. Cells 13-16
exist in `model_diagnostics.csv` but are excluded from headline interpretation.

## Critical learnings (do NOT re-litigate after compact)

1. **n_brexit = 0 across all 3,820 firms is CORRECT** — 2015 10-Ks pre-date the
   Feb 2016 referendum announcement; "Brexit" rarely appeared in 2015 corporate
   disclosure. Treatment classification reads other 8 keywords primarily.

2. **HIGH_10K reproduction gap: F1D 2,847 vs Campello 807** — both samples are
   Compustat-mapped (LINKPRIM='P'). Diagnostic localizes mechanism: dropping
   "uncertainty"+"uncertain" from the tally reduces F1D HIGH to 994 (close to
   Campello's 807). Campello's published methodology likely had an undisclosed
   constraint (context-windowed proximity, or Item-scope restriction). Decision:
   KEEP 9-keyword pure-tally per spec verbatim.

3. **β^UK SE column is DIAGNOSTIC ONLY** — classical homoskedastic OLS. The
   treatment classifier reads only the point estimate + tercile rank (not SE),
   so heteroskedasticity-robust SE not implemented.

4. **CIK-to-gvkey structural cap = 47%** — SEC 10-K universe (~7,800 distinct
   CIKs in 2015) larger than Compustat (foreign issuers, RICs, smaller-cap not
   in CCM). 47% post-date-window-merge is structural max; not a bug.

5. **DAILY FTSE100 was NOT initially acquired** — previously had MONTHLY only,
   which is INSUFFICIENT for monthly realized vol (= std of intramonth daily
   returns). Re-fetched daily ^FTSE 2009-12-15 to 2015-01-30 (1,293 rows) from
   yfinance. Saved at `inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_daily.csv`
   (gitignored).

6. **Cluster SE refactor backward-compat** — Trump runner's CLUSTERING global
   already existed (line 153) but `_fit_one` hardcoded entity=True/time=False.
   Refactored to read CLUSTERING dict at fit time. Trump's default produces
   identical fit_kwargs (linearmodels treats omitted cluster_time as False).
   No Trump regression behavior change; unblocks Brexit's double-cluster +
   future Boasiako (state-cluster) + Chen (matched-pair-by-year cluster).

7. **Compustat decimal.Decimal dtype trap** — comp_na_daily_all stores numeric
   columns as object dtype with `decimal.Decimal` values. Caused TypeError in
   numpy quantile (1% winsorization) at first run of #101-104. Fix: `pd.to_numeric(col, errors='coerce')`
   before any arithmetic. Documented in 4 Brexit-verbatim control builders.

## Open / next session decisions

| Question | Status |
|---|---|
| Boasiako DiD (H1.5.databreach_did) — next? | Pending Sina direction. Phase 0 data acquired (NCSL HTML + Boasiako disclosure-law passage years 46-state CSV per `project_session_2026_05_08_v3_chen_locked_data_acquired.md`). Headline: β=+0.0076** SE 0.0031 with state-cluster SE. |
| Chen DiD (H1.5.restatement_did) — next? | Pending Sina direction. Phase 0 data acquired (AA financial restatements WRDS pull, 6,916 rows in Chen window 1997-Jun06). Headline: β_DiD = +0.034*** [p=.002] n=1,391/1,434, Table 3 Panel A cols 5-6. |
| §III.E.4 prose update + main.pdf recompile (Phase 2) — next? | Pending Sina direction. Per plan, separate session. Brexit-specific prose already drafted in mind: cash sig framed as Campello-replication (not novel), speech null framed alongside Trump+Redistricting null pattern. |
| Brexit Phase 1 iter 2 robustness — needed? | Sina decided NO. All infra exists if requested later (~3 hours total). |
| Brexit speech wrong-sign DiD_10K (cols 13-16) investigation — needed? | Sina decided NOT loadbearing under one-tailed POS hypothesis. Document in §III.E.4 prose if interesting; otherwise leave in diagnostics CSV only. |

## Key files (path index for fast lookup)

### Plan + spec
- `~/.claude/plans/tender-popping-origami.md` — 632-line plan + plan-deviation log (4 mid-session entries added)
- `tmp/3did_replication_v2_2026_05_08.md` — locked spec, Brexit Section A lines 74-960

### Phase 1 deliverables
- `tmp/sec_iiie4_brexit_phase1_complete_2026_05_08.md` — Phase 1 summary memo (committed dd4d212)
- `tmp/COMPACTION_HANDOFF_brexit_phase1.md` — THIS FILE

### 13 NEW source files (committed across 14 atomic commits)
**Builders** (`src/f1d/shared/variables/`):
- `brexit_treatment_beta_uk.py` — closed-form vectorized OLS
- `brexit_treatment_10k.py` — read 10-K cache + threshold
- `brexit_macro_controls.py` — 5 macros 1Q-lagged
- `brexit_consensus_eps.py` — IBES FPI=6 within-firm z-score
- `hoberg_phillips_fic100.py` — FIC100 via zipfile.open() in-place
- `brexit_tobins_q.py`, `brexit_sales_growth.py`, `brexit_stock_return.py`, `brexit_cash_flow.py` — 4 Campello-verbatim firm controls
- `brexit_psm_matching.py` — 1:1 NN no-replace propensity-matched
- `brexit_parallel_trends.py` — utility function (NOT a builder)

**Runner**: `src/f1d/econometric/run_h1_5_brexit_did.py` (559 LOC, 16-cell baseline)

**Scripts**: `scripts/brexit/{__init__.py, parse_10k_keywords.py, build_beta_uk.py, build_treatment_10k.py, build_macro_controls.py, build_consensus_eps.py, build_fic100.py, build_brexit_controls.py, build_psm.py}`

**Tests**: `tests/{test_hoberg_phillips_fic100.py, test_brexit_controls.py, test_brexit_parallel_trends.py}` (25 pytest cases)

**Edits**:
- `src/f1d/shared/variables/__init__.py` — 12 imports + 11 __all__ entries
- `config/suite_render_order.yaml` — H1.5.brexit_did added to suites: + thesis_suites:
- `src/f1d/shared/variables/_ibes_engine.py:45` — comment fix (cosmetic)
- `src/f1d/econometric/run_h1_5_trump_did.py` — _fit_one cluster SE refactor

### Output dirs (gitignored, durable on disk)
- `inputs/Brexit_replication/Yahoo_FTSE100/FTSE100_yfinance_daily.csv` (1,293 rows)
- `outputs/intermediate/brexit_10k_keyword_counts/<ts>/` — 9,270-filing cache
- `outputs/variables/{brexit_treatment_beta_uk,brexit_treatment_10k,brexit_macro,brexit_consensus_eps,hoberg_phillips_fic100,brexit_tobins_q,brexit_sales_growth,brexit_stock_return,brexit_cash_flow,brexit_psm_matching}/<ts>/` — builder outputs
- `outputs/econometric/h1_5_brexit_did/<ts>/` — runner outputs (model_diagnostics.csv, report.md, suite_spec.json)

## Plan-deviation log (key entries; full list in plan file)

| Item | Decision | Justification |
|---|---|---|
| HIGH_10K Campello-gap rationale | F1D 2,847 vs Campello 807 — gap NOT structural-universe; "uncertainty"/"uncertain" boilerplate inflation; KEEP verbatim 9-keyword pure-tally | Campello's actual implementation undisclosed; deviating would be unverifiable guess |
| β^UK SE column | classical homoskedastic OLS — DIAGNOSTIC ONLY | Treatment classifier reads point estimate + tercile rank only |
| Runner #107 budget | revised 1.5d → 3-4d during plan, but actual delivery ~3h since BASELINE-only ship | Sina mid-Phase-1 decision pared scope |
| Inline tests #100-#106 | adopted at-write-time pattern (NOT batched at #108) | Per advisor anti-pattern flag; caught Compustat decimal.Decimal bug |
| Robustness ladder (full) | DEFERRED entirely from MVP — cash isn't novel, speech null | Sina decision: Brexit DiD's marginal value to F1D thesis is reduced; remaining time better spent on Boasiako/Chen |
| Two-tailed reporting | NEVER report; H1 hypothesis is uniformly one-tailed POS | Sina lock 2026-05-08 |

## Phase 1 task status (frozen at compact)

```
#94  CRITICAL-4 cluster SE refactor                                    completed
#95  brexit_treatment_beta_uk + CLI                                    completed
#96  parse_10k_keywords.py ETL                                         completed
#97  brexit_treatment_10k + CLI                                        completed
#98  brexit_macro_controls + CLI                                       completed
#99  brexit_consensus_eps + CLI                                        completed
#100 hoberg_phillips_fic100 + CLI + 4 pytest                           completed
#101-104 4 Brexit-verbatim controls + CLI + 16 pytest                  completed (all 4)
#105 brexit_psm_matching + CLI                                         completed
#106 brexit_parallel_trends utility + 5 pytest                         completed
#107 run_h1_5_brexit_did.py BASELINE 16-cell                           completed (robustness 25 cells DEFERRED per Sina)
#108 inline tests (superseded by per-builder inline pattern)           completed
#109 EDITS (__init__ + suite_render_order + IBES)                      completed
#110 Phase 1 verification (THIS FILE WAS WRITTEN AFTER #110)           completed
```

## Last-mile verification artifacts

- AST parse + import all PASS
- Brexit runner reproducible 16/16 cells in 8.2s on second clean run post-EDITS (deterministic)
- 25 inline pytest cases ALL PASS
- `git log --oneline -14` shows clean atomic commits
- `git status` shows tree-clean except 2 pre-existing M files unrelated to this session

## Spawning Future-Claude after compact

If invoked with "where are we" or "continue" or no specific direction:
1. **Read this file FIRST**.
2. **Read** the durable memory at `~/.claude/projects/<id>/memory/project_session_2026_05_08_v4_brexit_phase1_baseline_shipped.md`.
3. **Read** MEMORY.md for the up-to-date index.
4. **Re-orient via** `git log --oneline -15` and `git status --short`.
5. **Ask Sina** which of the 5 next-session options to pursue (Boasiako / Chen / Phase 2 prose / iter 2 robustness / something else).
6. **Do NOT re-litigate** the Sina decisions: full-ladder skip, two-tailed suppress, HIGH_10K verbatim. These are LOCKED.

---

**THIS HANDOFF FILE WAS WRITTEN POST-#110 AS COMPACTION-PREP REQUEST FROM SINA. COMMIT HASH FOR THIS FILE WILL BE THE 15TH COMMIT.**
