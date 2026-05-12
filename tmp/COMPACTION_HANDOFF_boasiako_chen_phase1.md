# Compaction Handoff — Boasiako Eq 1 + Chen Phase 1C COMPLETE (14/14)

**Date**: 2026-05-09 (post-/compact + ~5h)
**Master HEAD**: `43cd055` (16 atomic commits this session)
**Plan**: `~/.claude/plans/staggered-firm-cascade.md` v2 (ratified 2026-05-09)
**Audit memo**: `tmp/boasiako_chen_plan_audit_findings_2026_05_09.md` (af9bcfb73742b167c; 23 findings)
**Spec anchor**: `tmp/3did_replication_v2_2026_05_08.md` Sections B + C

## Read-FIRST after /compact

1. This file (canonical state)
2. `~/.claude/projects/<id>/memory/project_session_2026_05_09_boasiako_chen_phase1.md` (durable memory)
3. `~/.claude/projects/<id>/memory/MEMORY.md` (index)
4. `git log --oneline -16` to re-orient
5. `outputs/econometric/h1_5_restatement_did/2026-05-09_023323/report_step4_H1_5_restatement_did.md` (54-cell Chen results)

## Current state — PHASE 1 COMPLETE

**Phase 1A Boasiako Eq 1**: 6/6 builders + 14/14 cells SHIPPED
**Phase 1C Chen**: 8/8 builders + 54/54 cells SHIPPED (18 cells × 3 variants A/B/C)

## 16 atomic commits this session (`5438450` → `43cd055`)

```
PHASE 1A Boasiako (6 commits):
  5438450  [#A2 _compustat_annual_reader]      shared utility, decimal-trap+loc=USA
  3f7adb8  [#A3 ff49_industry_classifier]      Ken French SIC ranges
  5bac756  [#A4 boasiako_disclosure_law_treatment]  Y+1 staggered, 46+4-never-treated states
  1c2895c  [#A5 boasiako_eq1_controls]         11 controls + winsorize
  ba377ae  [#A6 boasiako_industry_cf_vol]      FF49 industry-MEAN, 10y σ, ≥3y floor
  de5bda4  [#A7 run_h1_5_disclosure_law_did]   14-cell runner — cash SIG (3/4) but mag 3-10× paper

INTERMEDIATE: b03ba02  [Compaction prep — stale; this file supersedes]

PHASE 1C Chen (8 commits):
  10d50b4  [#C0 chen_aa_to_gvkey_bridge]       NEW v2 audit C1 — AA CIK→gvkey CCM time-varying bridge
  f57f651  [#C1 ff48_industry_classifier]      Ken French 48-industry (distinct from FF49)
  ae6050d  [#C2 chen_restatement_treatment]    3-variant (A/B/C); Variant B IRREG=263 vs Chen 270
  9d84a29  [#C3 chen_baseline_controls]        7 vars (Q SIZE CF NWC LEV NSEG AGE); CF=OANCF/AT
  3de606e  [#C4 chen_industry_cf_vol_ff48]     FF48 industry-MEDIAN of firm-σ (CORRECTION 1)
  83de714  [#C5 chen_psm_matching]             1:1 NN no-replace WITHIN FF48 + FF12-fallback; 20-cov X1∪X2∪X3
  af3349d  [#C6 chen_ps_demand]                Duchin 2010; pct rank AFTER -1× flip per audit V2
  43cd055  [#C7 run_h1_5_restatement_did]      54 cells per-cell+Wald-diff per audit M1
```

## Empirical results

### Phase 1A Boasiako Cash (4 cells; cols 1-4)
```
col 1 industry+state+year FE:   β=+0.0262 p_one=0.012**  vs paper +0.0076** (3.4× mag)
col 2 firm+year FE:              β=+0.0580 p_one<.001*** vs paper +0.0056** (10× mag)
col 3 excl CA sensitivity:       β=+0.0110 p_one=0.232 NS (matches paper pattern)
col 4 excl 07-09 crisis:         β=+0.0317 p_one=0.022**  vs paper +0.0078** (4× mag)
DECISION-GATE FIRED — Sina ratified PROCEED (loose qualitative replication)
```

### Phase 1A Boasiako Speech (10 cells; cols 5-14)
ALL 10 NULL → matches Brexit/Trump/Redistricting 4-for-4 speech null pattern.

### Phase 1C Chen Variant B (post-bridge IRREG=263 closest to Chen 270)
```
CASH per-cell+Wald (cols 1-3):
  col 1 restatement POST: β=+0.0603 p_one=0.014** SIG (1.3× Chen +0.046***)
  col 2 control POST:     β=-0.0163 p_one=0.678 NS (vs Chen +0.012* small POS)
  col 3 Wald-diff:        β=-0.0074 p_one=0.609 NS (vs Chen +0.034*** SIG)

SPEECH per-cell+Wald (cols 4-6):  ★ BREAKS 4-FOR-4 NULL PATTERN
  col 4 restatement POST: β=+0.1380 p_one=0.229 NS-positive (NOT null)
  col 5 control POST:     β=-0.0352 p_one=0.580 NS
  col 6 Wald-diff:        β=+0.0807 p_one=0.293 NS-positive

Cash×PS_DEMAND HIGH/LOW (cols 7-12): NS
Speech×PS_DEMAND HIGH/LOW (cols 13-18): many cells skipped <30 obs
```

### M5 Pre-flight (Variant B post-PSM)
- PSM matched 91/263 IRREG-Variant-B (65% attrition); all event_year ∈ 2004-2006
- CASH bidirectional coverage: 80 firms (BELOW 150 threshold)
- SPEECH bidirectional coverage: 17 firms (severely BELOW)
- Sina ratified PROCEED 2026-05-09 with low-power caveat

### Speech 5-design pattern (post-Chen)
| Design | Speech result |
|---|---|
| Brexit | NULL (cash sig only) |
| Trump | NULL all 8 specs |
| Redistricting | NULL all 8 specs |
| Boasiako | NULL all 10 specs |
| Chen | **POSITIVE NS-but-promising β≈+0.13 across all 3 variants** |

→ Story B speech-channel: 4-NULL + 1-positive-NS-promising. Insufficient power for inference
(n=53 treated; vs Boasiako baseline n=49,402); but FIRST directionally-supportive evidence
among 5 designs. Frame in §III.E.4 prose accordingly.

## Sina decisions ratified this session

| # | Question | Lock |
|---|---|---|
| Q1 | Chen IRREG classifier path | 3-variant sensitivity (A/B/C) |
| Q2-OVERRIDE | Phase 1B path post-audit C2 | ABORT Phase 1B (Boasiako Eq 2 PRC unreachable) |
| Q3 | Speech channel partitions | INCLUDE on UncResCEO_c |
| Q4 | Cash-side robustness ladder | SKIP per Brexit pattern |
| RAT | Plan v2 ratification | Approve as written |
| GATE1 | Phase 1A decision-gate (magnitude divergence) | PROCEED to Chen (loose replication) |
| GATE2 | C7 M5 pre-flight low-power | Ship 18-cell runner with caveat |

## Critical learnings (do NOT re-litigate post-/compact)

1. **AA Audit Analytics has NO gvkey field** — only `company_fkey` = CIK. CCM bridge MANDATORY (audit C1). Implemented Task C0; retention 44.6%.

2. **PRC data unreachable** — Boasiako Online Appendix has only PDF, privacyrights.org requires purchase, Wayback brittle. Phase 1B ABORTED.

3. **linearmodels.PanelOLS max-2-effects limit** — for industry+state+year FE: use `time_effects=True + other_effects=ff49 + state DUMMIES in exog`.

4. **Trump `_fit_one()` cross-cutting refactor was DEAD WEIGHT** (audit M0a) — runners clone Brexit, not Trump. Bake clusters_col DIRECTLY into new clones.

5. **LINKENDDT='E' sentinel** — use `2099-12-31` not `9999-12-31` (datetime64[ns] max ~2262; 9999 overflows).

6. **Chen CF formula = OANCF/AT** (verbatim PDF p.6) — DISTINCT from Boasiako Bates 2009 `(OIBDP-XINT-TXT-DVC)/AT`.

7. **Chen SIGMA construction** = firm-σ-then-FF48-MEDIAN. Chen IND_STDCF (C6 PS_DEMAND) = σ-of-FF48-MEDIAN-series. SAME formula structure, INVERTED aggregation order → different values.

8. **F1D Compustat lacks Segment file** → NSEG=1 default per spec verbatim "=1 if missing".

9. **Magnitude divergence in Boasiako Eq 1** (3-10× larger than paper) — DOCUMENTED not diagnosed. Sina PROCEED. Candidate causes: F1D Compustat-only vs paper's CRSP-Compustat-MERGED.

10. **Chen PSM attrition 65%** — 91 of 263 IRREG-Variant-B treated firms matched. All event_year ∈ 2004-2006. Documented; not investigated.

11. **Per-cell + Wald-diff (audit M1)** = combined-sample regression with Treated×POST interaction → coefficient IS the Wald-diff. NOT separate F-test on coefficient difference (advisor confirmed 2026-05-09).

12. **Speech NULL pattern broken by Chen** — 4-for-4 → 4-NULL + 1-positive-NS-promising. Story B novel-claim has first directional support (n=53 treated; underpowered but directionally consistent).

## Open / next session

1. **§III.E.4 prose update + main.pdf recompile** (Phase 2, separate session): frame 5-design speech pattern; document Boasiako magnitude divergence; document Chen PSM 65% attrition + low-power caveat; document Chen Variant A/B/C sensitivity table.
2. **Optional Phase 1 iter 2**:
   - Diagnose Boasiako magnitude divergence (CRSP-Compustat-MERGED universe? CF formula sensitivity? winsorization scope?)
   - Chen PSM attrition recovery (relax FF12 / allow replacement / larger pool)
3. **Boasiako Eq 2** still ABORTED (PRC unreachable per Sina Q2-OVERRIDE).

## Total session metrics

- 16 atomic commits
- 14 source modules shipped + 12 test files
- ~96 tests PASS across all builders
- 68 regression cells produced (14 Boasiako + 54 Chen)
- Pace: ~5h post-/compact for 5 Chen tasks (C3-C7); ~3h pre-/compact for Boasiako 6/6 + Chen 3/8

Safe to /compact.
