# Thesis Draft — Decisions Log

**Current phase:** Phase 5 audit — philosophy-framed, dialogue-based. Hard reset 2026-04-14. Audit design finalized. **7 / 37 suites audited.** H1 + H4a + H4b + H12 + H12b + H13 KEEP, H16 DROP-flagged (revisit) 2026-04-14/15. Q1 was reworded at the H1 boundary then the rewording was locked mid-audit (narrative decided post-audit). Rules 21-23 added 2026-04-15 during H12 dialogue. Next suite: H17.

---

## 1. Philosophy of the audit

### 1.1 What the thesis is actually arguing

Thesis: "Uncertainty in Language and Corporate Outcomes." Novel IV = speech uncertainty measured from earnings-call language (Manager Q&A primarily, via `UncAnsMgr`). Claim: this measure carries information about corporate behavior and outcomes beyond what standard financial controls capture.

### 1.2 The central risk

The central risk is NOT statistical significance. With 112,968 calls across 2,429 firms (2002-2018), p-values are cheap. The central risk is **"so what?"** A skeptical committee reader's default is:

> "Cheap p-values on a noisy linguistic measure, hand-picked hypotheses, publication-bias machine, no mechanism, nothing load-bearing for how we understand firms."

The audit exists to defend against that default. Every kept suite must earn its place by answering a question a skeptical reader will genuinely ask. Not because it's significant. Not because it was in some prior canonical list. Because without it the thesis has a gap a committee member will point at.

### 1.3 Reader-questions the thesis must defend against

| # | Question | Role |
|---|---|---|
| Q1 | **Within a firm, does management Q&A linguistic uncertainty covary with contemporaneous corporate financial state (cash, leverage, payout, investment, buybacks, financing mix) in the direction predicted by precautionary / conservative financial behavior?** | Foundation. The thesis's novel IV must first be shown to track corporate financial conservatism under within-firm identification; without this the thesis fails at step 1. Claim is **association under firm FE, not causal prediction** — verified timing convention (Compustat `datadate ≤ call start_date` via backward `merge_asof` in `_compustat_engine.match_to_manifest`, lines 1402-1409) rules out clean causal direction either way. |
| Q2 | Does the effect run through a plausible channel, or is it black-box correlation? | Mechanism. Without channel evidence the effect is a curiosity, not a contribution. |
| Q3 | Is the market actually listening / using the information? | Information content. If market ignores it, the measure is noise. |
| Q4 | Is the IV just a proxy for macro conditions / business cycle? | Construct validation + endogeneity. If macro EPU drives it, we're measuring macro not firms. |
| Q5 | Does the effect matter economically, not just statistically? | Magnitude. Cross-cutting sweep, addressed at end of audit, not per-suite. |
| Q6 | Is this cherry-picking / fishing? | Transparency. Addressed via honest reporting of boundaries, nulls, and CEO/Pre parallel measures inside each Q1-Q4 suite. Not a separate cluster. |

**Q1 revision history:** Q1 was originally worded as *"Does speech uncertainty actually predict what firms DO?"*. Reworded at the H1 dialogue boundary (2026-04-14) after the user pushed back on the "predict" verb and I linear-read `src/f1d/shared/variables/_compustat_engine.py` lines 1383-1417 and `panel_utils.attach_fyearq` to verify the timing convention. The verified convention (backward `merge_asof`, Compustat `datadate ≤ call `start_date`) means contemporaneous regressions are associations between a firm's just-ended reporting quarter state and concurrent management language; neither prediction nor causal direction is identifiable from this data. The revised Q1 asks only for within-firm association, which is the strongest defensible version given the timing. Reframing of other Qs remains provisional — will be revisited as subsequent suites are audited per the user directive "as we proceed with reading the results we have, find the best frame to claim as strong as possible".

Every kept suite maps to exactly **one** of Q1-Q4 (or a new Q7+ named and justified during dialogue). Q5 + Q6 are cross-cutting and addressed differently.

### 1.4 The audit verdict types

- **KEEP** — maps to a reader-question, the cells honestly answer that question, no other suite answers it better.
- **DROP** — no reader-question it uniquely answers, or question is already answered elsewhere, or cells don't support the claimed answer. Lives in fishing deck / future work.
- **REFRAME** — cells answer a different question than originally framed; the new question is still load-bearing; keep with adjusted narrative role.

---

## 2. How the audit runs

### 2.1 Not a rubric

A rubric-based audit ("N/12 sig + firm FE + extended controls = Main-tier") produces mechanical verdicts that collapse under adversarial questioning. A committee member asks "why that threshold?" and the edifice wobbles. Rubrics are what I reach for because they look defensible, not because they actually defend anything. The thesis does NOT need rubrics.

### 2.2 Per-suite dialogue (5 steps)

For each suite in the audit order:

1. **I read cells plain.** LaTeX cell facts only. No interpretive labels.
2. **I name the reader-question** the suite is proposed to answer (from §1.3 Q1-Q4, or a new Q7+ justified on the spot).
3. **I argue honestly** whether the cells actually answer that Q, including the adversarial counter-argument a skeptic would raise against KEEP.
4. **User pushes back** adversarially: "that's not what a skeptic would ask", "Q already answered elsewhere", "cells answer a weaker version", "sample restriction kills external validity", etc.
5. **We converge** on KEEP / DROP / REFRAME. If we can't converge, the suite is flagged for advisor review at the phase boundary.

### 2.3 The only non-generic principle

**Every KEEP verdict must have a named reader-question and an honest argument that the cells answer it.** Everything else is per-suite judgment informed by cell facts, the thesis's epistemic structure, and what a skeptical reader would genuinely ask.

### 2.4 Discipline carry-overs (still in force)

- **UncAnsMgr is the sole hypothesis channel.** CEO / UncPreMgr / UncPreCEO are secondary measures reported in tables but NOT positive hypothesis channels. Aligned secondary → 1-line supportive cite. Contradicting → "measurement concerns" flag, no rescue narrative. (`feedback_ceo_noisy_mgr_central.md`)
- **No rescue narratives.** Contradictions logged, never rescued with sub-theories. (`feedback_audit_first_no_narrative.md`)
- **Read-tool-linear only.** No Grep / pattern search / shortcut on `outputs/all_tables.tex` or runner source. (`feedback_phase5_methodology.md` rule 6)
- **Pre-audit canonical reads mandatory** before touching any suite: `DECISIONS.md` + `PROGRESS.md` + `memory/project_phase5_audit_progress.md` + `memory/feedback_phase5_philosophy.md` + `memory/feedback_phase5_methodology.md` + `memory/feedback_ceo_noisy_mgr_central.md` + `memory/feedback_audit_first_no_narrative.md`.
- **Concise default.** Lead with the answer. Tables over prose paragraphs. (`feedback_concise_default.md`)
- **No mid-audit rubric creation.** If I catch myself inventing a threshold to justify a verdict, stop — the verdict must rest on the reader-question argument, not a number.

---

## 3. Audit order — by reader-question cluster

Walk Q1 → Q2 → Q3 → Q4. Within each cluster, suites are audited in the order below. Cluster assignment is provisional — if cells in a suite clearly answer a different Q, the suite is re-clustered during dialogue with an explicit argument.

### Q1 cluster — direct outcomes (10 suites)

Does speech uncertainty predict what firms DO?

H1 (cash) → H4a (book leverage) → H4b (debt-to-capital) → H12 (payout ratio) → H12b (payer dummy) → H13 (capex) → H16 (R&D) → H17 (repurchases) → H19b (Chang external funding) → H20b (Chang debt choice)

First in audit order.

### Q2 cluster — channel / mechanism (6 suites)

Does the effect run through a plausible channel?

H1.1 (TSIMM × cash) → H1.1b (binary TSIMM × cash) → H1.2 (rating constraint × cash) → H13.1 (TSIMM × capex) → H13.2 (capex lead horizon) → H22 (Hoberg-Maksimovic equity delay constraint)

### Q3 cluster — information content / market listening (14 suites)

Is the market actually listening?

H5 (analyst dispersion) → H7 / H7b / H7c / H7d / H7e (Amihud illiquidity, 5 suites) → H14 / H14b / H14c / H14d / H14e (bid-ask spread, 5 suites) → H18 (CCCL LPM) → H18b (CCCL Logit) → H21 (SEC letters fwd count)

### Q4 cluster — construct validation / reverse direction (7 suites)

Is the IV just a macro proxy?

H11 (PRisk contemp) → H11-Lag1 / H11-Lag2 (PRisk lags) → H23 (TSIMM firm-year) → H24 (US EPU) → H24b (Global EPU) → H25 (GPR)

**7 suites.**

### Totals

Q1 (10) + Q2 (6) + Q3 (14) + Q4 (7) = **37 suites** matching GAT entries. Q5 + Q6 cross-cutting, handled at end.

### Edge-case flags (decide during dialogue)

- **H5 (dispersion)**: provisionally Q3 (info content via analyst channel). Alternative: Q1 (direct outcome on analyst disagreement). Decide when H5 dialogue opens.
- **H22 (equity delay constraint)**: provisionally Q2 (constraint channel). Alternative: Q1 (direct outcome on a financial-structure variable). Decide when H22 dialogue opens.
- **H19b / H20b (financing-mix)**: provisionally Q1 (direct outcome). Alternative: Q3 (information content via financing decisions reflecting market awareness). Decide at audit time.

---

## 4. Per-suite audit records

### 4.0 Shape

Each audited suite produces **two things**:

**(a) One row** in the summary table below (§4.1) — 7 columns, populated at dialogue step (v).

**(b) One block** (§4.2+) — the fuller narrative per suite: DV, N, FE ladder, tail, cluster, key cell facts, reader-question argument, verdict, rationale. Dialogue transcript (adversarial counter-arguments, user pushback) lives in chat history + git log, NOT in the block.

### 4.1 Summary table (7 columns)

| suite_id | DV | N_range | reader_Q | key_cell_fact | verdict | rationale |
|---|---|---|---|---|---|---|
| H1 | CashRatio (cols 1-6); CashRatio_lead (cols 7-12, robustness) | 59,440–65,128 | Q1 (provisional) | UncAnsMgr 6/6 positive-significant on contemp CashRatio, including the toughest Firm+YQ+ExtCtrl spec (β=0.0034**); lead DV collapses to 1/6 on UncAnsMgr and the only surviving lead cell uses Ind FE not Firm FE | KEEP | Within-firm contemporaneous association between cash-holdings and management Q&A uncertainty delivered on the primary IV under the toughest FE ladder; lead collapse, CEO-lead > Mgr-lead inversion, and UncPreMgr firm-FE sign flip logged as cross-cutting limitations in §5, not rescued |
| H4a | Leverage (cols 1-6); Leverage_lead (cols 7-12) | 59,447–65,132 | Q1 (provisional) | UncAnsMgr 0/6 null on contemp Leverage (mixed signs); 6/6 negative-significant on Leverage_lead including Firm+YQ+ExtCtrl (β=-0.0064**); secondary measures (CEO, UncPreCEO, UncPreMgr) all null on both DVs, no inversions to flag | KEEP | Within-firm forward association between book leverage and management Q&A uncertainty delivered on the primary IV at the lead-horizon under all FE ladders; contemp-null vs lead-6/6 pattern is the inverse of H1 and noted as a factual observation in §5.4 (no interpretive commitment — narrative built post-audit) |
| H4b | DebtToCapital (cols 1-6); DebtToCapital_lead (cols 7-12) | 59,190–64,895 | Q1 (provisional) | UncAnsMgr 0/6 null on contemp DebtToCapital (mixed signs); 5/6 negative-significant on DebtToCapital_lead including Firm+Yr+ExtCtrl (col 10 β=-0.0079*) but NOT col 12 Firm+YQ+ExtCtrl (-0.0069 null); secondary measures all null on both DVs | KEEP | Primary-IV forward-horizon association on lead DV under 5 of 6 FE ladders; contemp-null vs lead-5/6 tracks H4a leverage pattern but weakens slightly at the toughest YQ-FE spec; clean IV hierarchy, no flags |
| H12 | PayoutRatio_q (cols 1-6); PayoutRatio_q_lead_qtr (cols 7-12) | 44,624–47,651 | Q1 (provisional) | UncAnsMgr 0/12, UncAnsCEO 0/12, UncPreCEO 0/12; UncPreMgr 6/12 sig β<0 — all 6 sig cells under industry FE (cols 1, 3, 5 contemp + 7, 9, 11 lead), firm-FE 0/6 across both DVs. Within-firm 0/24 across all 4 IVs. Lagged_DV ≈ 0.25 ind / 0.07 firm — drastically lower persistence than H1/H4a/H4b | KEEP | Within-firm zero across all 4 IVs; cross-sectional industry-FE-only loading on scripted-language UncPreMgr; mixed pattern recorded as informative empirical fact for post-audit synthesis. First suite catalogued under rules 21+22+23 (no Q-filter, no null-sign reading, no magnitude-as-signal) |
| H12b | DivPayerQ (cols 1-6); DivPayerQ_lead1 (cols 7-12) | 60,175–64,145 | Q1 (provisional) | UncAnsCEO 0/12, UncPreCEO 0/12; UncAnsMgr 1/12 sig β<0 (col 6 Firm+YQ+ExtCtrl contemp only); UncPreMgr 6/12 sig β<0 — all 6 sig cells industry-FE (cols 1, 3, 5 contemp + 7, 9, 11 lead), firm-FE 0/6. Within-firm 1/24 (the UncAnsMgr col 6 only). Lagged_DV ≈ 0.91 ind / 0.70 firm — high persistence (sticky payer status, opposite of PayoutRatio_q's 0.07) | KEEP | Cross-sectional UncPreMgr industry-FE pattern repeats for the 3rd DV (after H1 cash, H12 payout — generalized in §5.5); one within-firm UncAnsMgr cell at the toughest spec is the only firm-FE survivor across all 4 IVs |
| H13 | Capex (cols 1-6); Capex_lead (cols 7-12) | 58,897–65,105 | Q1 (provisional) | **TWO-TAILED** (different from prior Q1 directional suites). UncPreCEO 0/12; **UncAnsCEO 3/12 sig β>0 — all 3 under FIRM FE contemp (cols 2, 4, 6)**; **UncAnsMgr 4/12 sig β>0 — all 4 under INDUSTRY FE (col 3 contemp + 7, 9, 11 lead)**; UncPreMgr 1/12 sig β<0 (col 11 lead). Cross-IV FE-strata split: CEO firm-FE / Mgr industry-FE, both β>0. Lagged_DV ≈ 0.74 ind / 0.32 firm contemp; 0.64 ind / 0.09 firm lead | KEEP | First suite with cross-IV FE-strata split — UncAnsCEO carries within-firm signal that UncAnsMgr does not, UncAnsMgr carries cross-sectional signal that UncAnsCEO does not, both positive. UncPreMgr 1 sig cell opposite direction. Two-tailed exploratory spec per `feedback_moderation_tails.md`. New §5.7 entry on FE-strata split |
| H16 | RDSales (cols 1-6); RDSales_lead (cols 7-12) | 58,970–65,086 | Q1 (provisional) | **TWO-TAILED**. **0/48 sig across all 4 IVs × all 12 cells** — first complete-null suite in the audit. Lagged_DV ≈ 0.71 ind / 0.34 firm contemp; 0.51 ind / 0.05 firm lead | **DROP (provisional, flagged for revisit)** | Per rule 21 explicit DROP criterion ("all-null"). User decision 2026-04-15: provisional DROP, revisit at end-of-audit if a strong reason to keep emerges (e.g., narrative needs an honest null on R&D for completeness). New §5.8 entry on first complete-null suite |

### 4.2 Per-suite blocks

_Populated during audit. One block per suite. Template at the bottom of this section._

### H1 — Speech Uncertainty and Cash Holdings

- **DV**: `CashRatio` (cols 1-6); `CashRatio_lead` (cols 7-12, reported as robustness / lead-spec check)
- **N**: 59,440–65,128 (main sample, ex financials and utilities)
- **FE ladder** (repeats per DV): (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl
- **Tail**: one-tailed, β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact**: UncAnsMgr is positive-significant in all 6 contemporaneous CashRatio specs (β range 0.0033-0.0072), including the most-demanding Firm+YQ+ExtCtrl spec (col 6, β=0.0034**). Lead DV collapses for the primary IV (1/6 sig: only col 9, which uses Industry FE + Year FE + Ext Controls). UncPreMgr shows an industry-FE vs firm-FE sign flip (col 3: +.0033**; col 4: -.0029 null). UncAnsCEO is null on contemporaneous CashRatio but weakly positive on 4/6 lead specs — the measurement-concern inversion flagged in §5. Lagged_DV ≈ 0.85 (ind) / 0.63 (firm) on Cash; ≈ 0.71 / 0.22 on Cash_lead.
- **Reader-question**: Q1 provisional — same loose frame as H4a / H4b (narrative decided post-audit, no commitment here). Original draft committed to "contemporaneous cash-holdings channel of corporate financial conservatism" at the H1 dialogue but that wording is superseded by the mid-audit narrative-discipline lock (2026-04-14).
- **Argument**: The six UncAnsMgr contemporaneous cells deliver the strongest within-firm association-claim the cash family can produce under the toughest identification (Firm FE + Year-Quarter FE + Extended Controls). Magnitudes are modest: **UncAnsMgr is a winsorized percentage, not a standardized IV** (sd ≈ 0.33, mean ≈ 0.82 per `summary_stats.csv`). Using the col 6 Firm+YQ+ExtCtrl β=0.0034, a 1-SD increase in UncAnsMgr yields ΔCashRatio ≈ 0.0034 × 0.33 ≈ 0.0011 (~0.11 pp) — about 0.67% of the CashRatio mean of 0.17. The direction is consistently positive and survives all six FE ladders, which is what Q1-association requires. The lead-spec collapse does not block KEEP because Q1 is not a prediction claim. The verified timing convention (Compustat `datadate ≤ call start_date`, backward `merge_asof`) means the regression is structurally an association between a firm's just-ended reporting-quarter state and the concurrent earnings-call language — neither a causal "language → cash" nor a clean "cash → language" claim is identifiable from this data, and the thesis does not need one.
- **Verdict**: **KEEP**.
- **Rationale**: H1 delivers the cash-holdings channel of the Q1 financial-conservatism association under the primary (Mgr Q&A) IV and the toughest FE ladder. The limitations (lead collapse, CEO-lead > Mgr-lead inversion on CashRatio_lead, UncPreMgr FE sign flip) are disclosed honestly and logged as cross-cutting §5 flags, not rescued with sub-narratives. This is the first suite populated under the revised Q1-as-association frame.

### H4a — Speech Uncertainty and Book Leverage

- **DV**: `Leverage` (cols 1-6); `Leverage_lead` (cols 7-12)
- **N**: 59,447–65,132 (main sample, ex financials and utilities)
- **FE ladder**: identical to H1 — (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl, repeating for each DV
- **Tail**: one-tailed, **β<0** for IVs (opposite direction from H1 tail; confirmed from `all_tables.tex` line 330 notes block)
- **Cluster**: firm-level
- **Key cell fact**: UncAnsMgr contemporaneous cells are 0/6 null with mixed signs (-0.0002 to -0.0018, max sig = none). UncAnsMgr lead cells are **6/6 negative-significant**: -0.0050*, -0.0073**, -0.0074**, -0.0069**, -0.0049*, -0.0064**, including the toughest Firm+YQ+ExtCtrl (col 12, β=-0.0064**). All secondary measures (UncAnsCEO, UncPreCEO, UncPreMgr) are null on both DVs across all 12 cells — cleaner IV hierarchy than H1 (no CEO/Mgr inversion, no UncPreMgr sign flip). Lagged_DV = 0.94 (ind) / 0.76 (firm) on contemp Leverage — extreme persistence, much stickier than CashRatio (0.85 / 0.63). CashRatio is included as a control and is negative-significant across the panel (e.g., col 2 β=-0.0297***).
- **Reader-question**: Q1 provisional — within-firm association between management Q&A linguistic uncertainty and corporate financial-decision outcomes (narrative frame to be decided post-audit, not committed here).
- **Argument**: Primary IV delivers 6/6 negative-significant cells on the lead DV across all six FE ladders. Direction is consistent with a within-firm forward association between language uncertainty and book leverage; no rescue narrative required because no per-suite framing is being committed. Contemp-null vs lead-6/6 is the inverse of the H1 pattern — noted as a factual observation, not explained.
- **Verdict**: **KEEP**.
- **Rationale**: Primary-IV cells deliver a within-firm forward-horizon association on the lead DV under the toughest FE ladder, with a clean IV hierarchy (no secondary-measure contradictions). No narrative commitment made here; post-audit synthesis decides how H1-contemp / H4a-lead fit into the final thesis frame.

### H4b — Speech Uncertainty and Debt-to-Capital

- **DV**: `DebtToCapital` (cols 1-6); `DebtToCapital_lead` (cols 7-12)
- **N**: 59,190–64,895 (main sample, ex financials and utilities)
- **FE ladder**: identical to H1 / H4a
- **Tail**: one-tailed, β<0 for IVs (line 396 notes block)
- **Cluster**: firm-level
- **Key cell fact**: UncAnsMgr contemp 0/6 null (mixed signs, .0002 to -.0020). UncAnsMgr lead 5/6 negative-significant: -.0087*, -.0077*, -.0154***, -.0079*, -.0085*, -.0069 — note the toughest spec (col 12 Firm+YQ+ExtCtrl, -.0069) is **null but narrow-miss** (p_one=0.1045, just above the 10% threshold) where H4a col 12 was sig at β=-0.0064** (p_one=0.0287). Secondary measures (UncAnsCEO, UncPreCEO, UncPreMgr) all null on both DVs across all 12 cells. Lagged_DV ≈ 0.93 ind / 0.79 firm on contemp DebtToCapital. CashRatio included as control (negative-significant, e.g., col 2 β=-0.0674***).
- **Reader-question**: Q1 provisional — same loose frame as H1 / H4a.
- **Argument**: Primary IV delivers 5/6 negative-significant lead cells across FE ladders. Pattern tracks H4a leverage almost exactly (same inverse contemp/lead asymmetry) but weakens at the toughest Firm+YQ+ExtCtrl spec. No narrative commitment; factual pattern is consistent with H4a.
- **Verdict**: **KEEP**.
- **Rationale**: Forward-horizon within-firm association delivered on 5 of 6 lead specs, clean IV hierarchy, no flags. The weakening at col 12 vs H4a is a factual observation to carry forward (not a basis to DROP). Debt-to-capital and book leverage are correlated measures of the same underlying construct — disclosed as such for post-audit synthesis.

### H12 — Speech Uncertainty and Quarterly Payout Ratio

- **DV**: `PayoutRatio_q` (cols 1-6); `PayoutRatio_q_lead_qtr` (cols 7-12)
- **N**: 44,624–47,651 (main sample, ex financials and utilities)
- **FE ladder** (repeats per DV): (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl
- **Tail**: one-tailed, β<0 for IVs (line 1029 notes block); two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (catalogued per rules 21+22+23: sig-pattern observables only, no β values on IV cells, no sign-talk on null cells):
    - **UncAnsMgr**: 0/12 sig
    - **UncAnsCEO**: 0/12 sig
    - **UncPreCEO**: 0/12 sig
    - **UncPreMgr**: **6/12 sig β<0** — sig cells are 1, 3, 5 (contemp industry-FE) and 7, 9, 11 (lead industry-FE). All 6 sig cells under industry FE; firm-FE cells 0/6 across both DVs.
    - **FE-ladder survival across all 4 IVs × both DVs**: industry-FE cells 6/24 sig (all UncPreMgr); firm-FE cells 0/24 sig.
    - **Lagged_DV** (rule 23 structural exception, allowed because it describes DV adjustment-speed not an IV effect): ≈ 0.25 (ind FE) / **0.07 (firm FE)** on contemp PayoutRatio_q; ≈ 0.23 (ind) / **0.04 (firm)** on lead. Drastically lower than H1 CashRatio (0.85/0.63), H4a Leverage (0.94/0.76), H4b DebtToCapital (0.93/0.79). Quarter-to-quarter persistence under firm FE is near-zero on this DV. Recorded in §5.6.
- **Reader-question**: Q1 (provisional). Per rule 21, Q wording is a placeholder; this block describes the empirical pattern, not a Q-answer match.
- **Argument**: The cataloguing IS the argument. Within-firm variation (firm-FE cells across all 4 IVs and both DVs) shows zero association between any speech-uncertainty measure and quarterly payout ratio. Cross-sectional (between-firm, industry-FE) variation shows scripted-language UncPreMgr loading negatively on payout ratio, 6/6 sig cells consistent direction. The within-firm-zero / cross-sectional-PreMgr-only split is the informative content. UncPreMgr's industry-FE-only pattern echoes the §5.2 measurement-concerns flag from H1 — the cross-sectional shape is now seen on two distinct DVs (cash, payout) and is generalized in §5.5.
- **Verdict**: **KEEP — informative mixed pattern**.
- **Rationale**: Under rules 21+22+23, KEEP is the default verdict for any informative empirical pattern. H12 has two distinct informative facts: (a) within-firm zero across all 4 IVs and both DVs, and (b) cross-sectional industry-FE-only UncPreMgr negative loading consistent across 6 cells. Both are recorded for post-audit synthesis; whether either fact maps to a final reader-Q wording is a synthesis decision deferred per the narrative-discipline lock. **First suite catalogued under rules 21-23**, added during this dialogue after three user corrections (provisional Q treated as filter; null signs treated as evidence; β magnitudes treated as audit signal). Incident: `log/incidents/2026-04-14_h12-filter-by-fixed-Q.md`.

### H12b — Speech Uncertainty and Dividend Payer Indicator (Hoberg-Prabhala 2009 analog)

- **DV**: `DivPayerQ` (cols 1-6); `DivPayerQ_lead1` (cols 7-12)
- **N**: 60,175–64,145 (main sample, ex financials and utilities)
- **FE ladder**: identical to H1/H4a/H4b/H12 (Ind+Yr → Firm+YQ+ExtCtrl ladder, repeats per DV)
- **Tail**: one-tailed, β<0 for IVs (line 1095 notes block); two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rules 21+22+23):
    - **UncAnsCEO**: 0/12 sig
    - **UncPreCEO**: 0/12 sig
    - **UncAnsMgr**: **1/12 sig** — col 6 only (Firm+YQ+ExtCtrl contemp), β<0 matches tail. The only firm-FE survivor across all 4 IVs in this suite.
    - **UncPreMgr**: **6/12 sig β<0** — sig cells are 1, 3, 5 (contemp ind-FE) + 7, 9, 11 (lead ind-FE). All under industry FE; firm-FE 0/6.
    - **FE-ladder survival across all 4 IVs × both DVs**: industry-FE 6/24 sig (all UncPreMgr); firm-FE **1/24 sig** (the UncAnsMgr col 6).
    - **Lagged_DV** (rule 23 structural): ≈ 0.91 (ind) / **0.70 (firm)** contemp; ≈ 0.91 (ind) / 0.72 (firm) lead. **High persistence** — DivPayerQ is sticky binary payer-status, structurally opposite of PayoutRatio_q (firm 0.07).
- **Reader-question**: Q1 (provisional, placeholder per rule 21).
- **Argument**: Cross-sectional UncPreMgr industry-FE-only pattern is now seen on a third distinct DV (H1 cash, H12 payout, H12b payer indicator) with the same shape: 6/6 sig industry-FE cells β<0, 0/6 firm-FE. Generalized in §5.5. UncAnsMgr's single firm-FE sig cell at the toughest spec (col 6 Firm+YQ+ExtCtrl) is a tiny within-firm signal — present, but not a strong pattern. CEO measures null on both DVs.
- **Verdict**: **KEEP — informative mixed pattern**.
- **Rationale**: Two informative facts: (a) cross-sectional UncPreMgr industry-FE pattern extends to a third DV, and (b) one within-firm UncAnsMgr cell at the toughest spec. KEEP per rule 21 — informative pattern, not all-null.

### H13 — Speech Uncertainty and Capital Expenditure

- **DV**: `Capex` (cols 1-6); `Capex_lead` (cols 7-12)
- **N**: 58,897–65,105 (main sample, ex financials and utilities)
- **FE ladder**: identical to prior Q1 suites
- **Tail**: **TWO-TAILED** (line 1161 notes block — different from prior Q1 directional suites). H13 was deliberately set up as exploratory per `feedback_moderation_tails.md` (parent-child asymmetry: H13 two-tailed, H13.1 one-tailed)
- **Cluster**: firm-level
- **Key cell fact** (rules 21+22+23):
    - **UncAnsCEO**: **3/12 sig β>0** — all 3 sig cells under **firm FE contemp** (col 2 = Firm+Yr, col 4 = Firm+Yr+ExtCtrl, col 6 = Firm+YQ+ExtCtrl). Lead 0/6 null.
    - **UncPreCEO**: 0/12 sig
    - **UncAnsMgr**: **4/12 sig β>0** — all 4 sig cells under **industry FE** (col 3 = Ind+Yr+ExtCtrl contemp; cols 7, 9, 11 = industry-FE lead specs). Firm-FE 0/6 across both DVs.
    - **UncPreMgr**: **1/12 sig β<0** — col 11 (Ind+YQ+ExtCtrl lead). Industry FE.
    - **FE-ladder survival across all 4 IVs × both DVs**: industry-FE **5/24 sig** (UncAnsMgr 4 + UncPreMgr 1); firm-FE **3/24 sig** (UncAnsCEO 3, all contemp).
    - **Cross-IV FE-strata split** (NEW pattern): UncAnsCEO carries within-firm contemp signal (3 cells β>0). UncAnsMgr carries cross-sectional signal (4 cells β>0, mostly lead). Two primary IVs hit DIFFERENT FE strata with the SAME positive direction.
    - **Lagged_DV** (rule 23 structural): ≈ 0.74 (ind) / 0.32 (firm) contemp; ≈ 0.64 (ind) / 0.09 (firm) lead. Moderate persistence (between PayoutRatio_q's 0.07 and CashRatio's 0.63).
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: First Q1 suite with non-zero firm-FE signal beyond the toughest-spec single-cell pattern (H12b col 6). UncAnsCEO has 3 sig firm-FE contemp cells (β>0); UncAnsMgr has 4 sig industry-FE cells (β>0). Two primary IVs split FE strata. UncPreMgr has 1 sig lead cell β<0 — opposite direction from the Mgr/CEO pattern. Two-tailed spec means no directional prediction; both positive findings are exploratory observations, not tail-violations.
- **Verdict**: **KEEP — informative mixed pattern with cross-IV FE-strata split**.
- **Rationale**: First suite where UncAnsCEO carries within-firm signal that UncAnsMgr does not (and vice versa for industry-FE). The cross-IV FE-strata split is a new structural observation different from H1/H4a/H4b/H12/H12b. Logged in §5.7. Per `feedback_ceo_noisy_mgr_central.md`, UncAnsCEO is a secondary measure — but here it carries within-firm signal the primary IV does not. Measurement-concerns flag in OPPOSITE direction from §5.1 (where CEO-lead > Mgr-lead inverted breadth on cash lead).

### H16 — Speech Uncertainty and R&D Investment Intensity

- **DV**: `RDSales` (cols 1-6); `RDSales_lead` (cols 7-12)
- **N**: 58,970–65,086 (main sample, ex financials and utilities)
- **FE ladder**: identical to prior Q1 suites
- **Tail**: **TWO-TAILED** (line 1690 notes block)
- **Cluster**: firm-level
- **Key cell fact** (rules 21+22+23):
    - **UncAnsCEO**: 0/12 sig
    - **UncPreCEO**: 0/12 sig
    - **UncAnsMgr**: 0/12 sig
    - **UncPreMgr**: 0/12 sig
    - **0/48 sig across all 4 IVs × all 12 cells.** First complete-null suite in the audit.
    - **Lagged_DV** (rule 23 structural): ≈ 0.71 (ind) / 0.34 (firm) contemp; ≈ 0.51 (ind) / 0.05 (firm) lead. Moderate ind / low firm persistence.
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: Speech uncertainty is silent on R&D investment intensity under any IV (CEO or Mgr; Ans or Pre), any FE ladder (industry or firm), any horizon (contemp or lead). Per rule 21 explicit DROP criterion, "all-null" is reserved-for-DROP. R&D investment does not covary with management or CEO speech uncertainty. The cleanest null in the audit so far. A possible reading is that R&D is a long-horizon, sticky, multi-year decision insensitive to quarterly speech-uncertainty fluctuations, but that is post-audit synthesis material — not interpreted here.
- **Verdict**: **DROP (provisional, flagged for revisit)**.
- **Rationale**: Per rule 21 explicit DROP criterion. **User decision 2026-04-15** (verbatim): *"for RD, we will decide later if we had a very good reason to keep it, but for now, flag it as drop"*. Reasons to potentially revisit at synthesis: (a) a clean null is a kind of finding that constrains narrative scope ("speech uncertainty does not move R&D investment under any identification"), (b) if the post-audit thesis frame needs an honest null on R&D for completeness or balance, KEEP-as-honest-null may be preferred. Default DROP unless a strong reason emerges. New §5.8 entry on the first complete-null suite.

---

_Template for subsequent suites:_

```
### H<id> — <title>

- **DV**: <name>
- **N**: <range>
- **FE ladder**: <ind/firm/YQ combinations>
- **Tail**: <one-tailed β<direction> / two-tailed>
- **Cluster**: <firm-only / two-way>
- **Key cell fact**: <the single most load-bearing observation>
- **Reader-question**: Q<n> — <short restatement>
- **Argument**: <1-2 sentence honest case that cells answer the Q>
- **Verdict**: KEEP / DROP / REFRAME
- **Rationale**: <final 1-2 sentence reasoning after dialogue>
```

---

## 5. Cross-cutting observations

_Populated as patterns emerge across suites. Each entry is a factual flag, not a narrative — entries accumulate during the audit and are revisited in the final synthesis._

### 5.1 CEO-lead > Mgr-lead inversion on cash (first seen in H1)

- **Observation**: On `CashRatio_lead` (cols 7-12 of H1), UncAnsCEO carries 4/6 positive-significant cells at the 10% level (cols 7, 10, 11, 12; p_one values 0.0811, 0.0943, 0.0971, 0.0909 per spec JSON), while UncAnsMgr carries only 1/6 (col 9 only; p_one=0.0316 — 5% level **). This is a reversal in *breadth* of the thesis hierarchy (`UncAnsMgr` primary per `feedback_ceo_noisy_mgr_central.md`): on the forward-looking cash spec, the *secondary* IV hits more cells than the primary. **Depth precision:** the single Mgr-lead cell (p=0.0316) is statistically stronger than any individual CEO-lead cell (all at 0.08-0.10), so the inversion is about *breadth*, not *depth*. The only surviving Mgr lead cell uses Ind FE + Year FE + Ext Ctrl (col 9), not Firm FE.
- **Status**: Measurement-concerns flag, not rescued. Consistent with `feedback_ceo_noisy_mgr_central.md` treatment of contradicting secondary patterns. Revisit after the full Q1 cluster (H4a through H20b) to see whether the inversion is cash-specific or repeats on other conservatism channels.
- **Loaded from**: H1 (2026-04-14).

### 5.2 UncPreMgr industry-FE vs firm-FE sign flip on cash (first seen in H1)

- **Observation**: On `CashRatio` (H1), UncPreMgr is positive-significant under Industry FE + Extended Controls (col 3, β=+0.0033**) and flips to negative-null under Firm FE + Extended Controls (col 4, β=-0.0029). The same flip pattern appears on `CashRatio_lead` (col 9 positive-sig vs col 10 negative-null).
- **Status**: Measurement-concerns flag, not rescued. Consistent with the "scripted/IR-vetted obfuscation" caveat on `UncPreMgr` in `feedback_ceo_noisy_mgr_central.md`. Possible reading: UncPreMgr loading is driven by cross-sectional industry composition rather than within-firm variation; firm-FE eats the cross-sectional component. Not a rescue — just a factual direction for the flag.
- **Loaded from**: H1 (2026-04-14).

### 5.3 Timing convention (verified 2026-04-14)

- **Observation**: The Compustat-to-call match is `pd.merge_asof(left=call start_date, right=Compustat datadate, direction="backward", by=gvkey)` in `src/f1d/shared/variables/_compustat_engine.py` lines 1402-1409. Each call gets the most recent Compustat quarterly record with `datadate ≤ call start_date`. For a typical Q2 earnings call on ~August 5, the attached CashRatio is from the June 30 balance sheet — physically measured ~36 days *before* the language is spoken. Same convention is used in `panel_utils.attach_fyearq` for fiscal-year attachment.
- **Status**: Not a bug — it's the standard accounting-econometric convention that treats same-reporting-period variables as contemporaneous. But it constrains what any Q1 result can claim: within-firm-quarter covariance reflects a shared latent firm-period condition; causal direction (language→state or state→language) is not identifiable from this data. Q1 was reworded at the H1 boundary to an association framing because of this constraint. Carry this caveat through all Q1/Q2/Q3 suites and any future causal-direction claims.
- **Loaded from**: H1 (2026-04-14, linear-read investigation of `_compustat_engine.match_to_manifest`).

### 5.4 Contemp-vs-lead DV asymmetry (first seen across H1 / H4a)

- **Observation**: H1 CashRatio shows UncAnsMgr 6/6 sig on contemporaneous DV and 1/6 sig on lead DV. H4a Leverage shows the inverse pattern: 0/6 null on contemp, 6/6 sig on lead. Both primary-IV directions are consistent with one-tailed predictions. Lagged_DV values line up with this asymmetry: Cash is 0.85 ind / 0.63 firm (moderate persistence), Leverage is 0.94 ind / 0.76 firm (extreme persistence).
- **Status**: Factual pattern, not interpreted here. A narrative explanation (e.g., "DV adjustment-speed heterogeneity: liquid positions respond within-quarter, sticky balance-sheet items respond on a fiscal-annual horizon") would be a rescue if committed during audit. Log only; revisit during post-audit synthesis when all 37 suites have been read and the pattern's generality or specificity can be assessed.
- **Loaded from**: H1 + H4a (2026-04-14).

### 5.5 UncPreMgr industry-FE cross-sectional loading repeats across DVs (H1 → H12 → H12b)

- **Observation**: H1 CashRatio (§5.2 above) showed UncPreMgr industry-FE-only sig pattern with firm-FE sign flip. H12 PayoutRatio_q showed the same shape: 6/6 sig industry-FE cells, 0/6 firm-FE. **H12b DivPayerQ (added 2026-04-15) is the third DV showing the same shape**: UncPreMgr 6/6 sig β<0 industry-FE cells (cols 1, 3, 5 contemp + 7, 9, 11 lead), 0/6 sig firm-FE. The pattern is now seen on **three distinct DVs** spanning cash holdings, quarterly payout ratio, and binary payer indicator — consistent shape across financial domains.
- **Status**: Cross-DV factual pattern. Per `feedback_ceo_noisy_mgr_central.md`, UncPreMgr is a secondary measure with known measurement concerns (scripted/IR-vetted obfuscation; cross-sectional loading is consistent with industry composition driving the result rather than within-firm linguistic variation). Do NOT build positive narrative around it here. Log only; revisit at end-of-audit synthesis. The Q1 cluster has 3 more direct-outcome suites pending (H17, H19b, H20b) — by end of Q1 we'll know if this is a Q1-wide pattern or DV-specific.
- **Loaded from**: H1 + H12 + H12b (2026-04-14/15).

### 5.6 PayoutRatio_q quarter-to-quarter persistence is near-zero under firm FE (H12)

- **Observation**: H12 Lagged_DV ≈ 0.07 (firm FE, contemp) and ≈ 0.04 (firm FE, lead). Compare H1 CashRatio Lagged_DV ≈ 0.63 firm; H4a Leverage ≈ 0.76 firm; H4b DebtToCapital ≈ 0.79 firm. Payout ratio has drastically lower quarter-to-quarter persistence under within-firm identification than the cash and leverage DVs already audited.
- **Status**: Structural property of the DV, not an effect claim. Per rule 23 of `feedback_phase5_methodology.md`, this is a Lagged_DV observation that is allowed in the §4.2 record because it describes the DV's adjustment-speed, not an IV effect. A possible reading is "payout decisions are near-discrete events, not sticky balance sheet stocks" but that interpretation is post-audit synthesis material — log only here. Revisit when comparing across all 10 Q1 suites at end-of-audit, alongside the §5.4 contemp-vs-lead asymmetry pattern.
- **Loaded from**: H12 (2026-04-15).

### 5.7 Cross-IV FE-strata split: UncAnsCEO firm-FE / UncAnsMgr industry-FE on Capex (H13)

- **Observation**: H13 Capex is the first Q1 suite where the two primary IVs hit DIFFERENT FE strata with the SAME direction. UncAnsCEO has 3/6 sig contemp cells under firm FE (cols 2, 4, 6) all β>0; UncAnsMgr has 4/6 sig cells (1 contemp + 3 lead) under industry FE (cols 3, 7, 9, 11) all β>0. Cross-IV split: CEO firm-FE / Mgr industry-FE / both β>0. UncPreMgr has 1 sig lead cell β<0 (col 11) — opposite direction. UncPreCEO null. H13 is two-tailed (no directional prediction).
- **Status**: New structural pattern not seen in H1/H4a/H4b/H12/H12b (which had EITHER cross-sectional UncPreMgr OR clean primary-IV pattern). H13 has a cross-IV FE-strata split. Per `feedback_ceo_noisy_mgr_central.md`, UncAnsCEO is a secondary measure — but here it carries within-firm signal the primary UncAnsMgr does not. Measurement-concerns flag in OPPOSITE direction from §5.1 (where CEO-lead > Mgr-lead inverted breadth on cash lead). Do NOT interpret here. Log only; revisit at end-of-audit synthesis.
- **Loaded from**: H13 (2026-04-15).

### 5.8 First complete-null suite: speech uncertainty silent on R&D investment (H16)

- **Observation**: H16 RDSales is the first audited suite with **0/48 sig cells across all 4 IVs × all 12 spec cells**. UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr all null on both contemp and lead RDSales, under industry FE and firm FE alike, with and without extended controls, with Year FE or Year-Quarter FE. Two-tailed spec. Lagged_DV moderate (0.71 ind / 0.34 firm).
- **Status**: Clean null across every cell. Per rule 21 explicit DROP criterion ("all-null"). User decision 2026-04-15: provisionally flag as DROP, revisit at end-of-audit if a strong reason to keep emerges (e.g., narrative needs an honest null on R&D for completeness, or the null becomes load-bearing as a falsification pre-registered prediction). Possible reading: R&D investment is a long-horizon, sticky, multi-year decision insensitive to quarterly speech-uncertainty fluctuations — but that interpretation is post-audit synthesis material.
- **Loaded from**: H16 (2026-04-15).

### 5.9 Queued observations (to populate as audit proceeds)

- UncAnsMgr robustness pattern across the Q1 cluster — where firm-FE survives, where it dies.
- Sample-size bands and what they imply for generalizability (H22 annual, H5 IBES Detail, H20b Chang sample).
- Q5 economic magnitude sweep (cross-cutting, at end of audit).

---

## Appendix A. Carry-over pipeline bug list (code fixes already applied, historical reference)

Recorded in git commits c46e655 → bf9f366 (2026-04-14 architectural rewrite + LaTeX audit fixes). Detailed record in `memory/project_draft_playing_it_safe.md` and `memory/project_completed_milestones.md`. Not reproduced here — the audit proceeds assuming these are stable.
