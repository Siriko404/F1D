# Thesis Draft — Decisions Log

**Current phase:** Phase 5 audit — philosophy-framed, dialogue-based. Hard reset 2026-04-14. Audit design finalized. **10 / 37 suites audited + RE-CATALOGUED under rule 24.** Q1 cluster COMPLETE: H1 + H4a + H4b + H12 + H12b + H13 + H17 + H19b KEEP; H16 DROP-flagged (revisit), H20b DROP. Q1 was reworded at the H1 boundary then the rewording was locked mid-audit (narrative decided post-audit). Rules 21-24 added 2026-04-15. **Rule 24 (record-scope ≠ verdict-scope) shifted §4.2 cataloguing to full-row format; Q1 retroactive REVERSED same day; all 10 §4.2 blocks now contain row-by-row catalogue (IVs + all controls + Lagged_DV + R²/N). See §5.12.** Next cluster: Q2 (channel/mechanism, 6 suites). Next suite: H1.1.

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
| H17 | RepurchaseIntensity (cols 1-6); RepurchaseIntensity_lead_qtr (cols 7-12) | 57,529–61,030 | Q1 (provisional) | **TWO-TAILED**. UncAnsCEO 0/12; UncPreCEO 1/12 sig β>0 (col 8 firm-FE lead); UncAnsMgr 4/12 sig β<0 (cols 1, 3, 5 contemp + col 7 lead, all industry-FE); **UncPreMgr 7/12 sig β>0 — cols 1, 3, 5 industry-FE contemp + cols 2, 4, 6 FIRM-FE contemp + col 7 industry-FE lead — first UncPreMgr firm-FE survival in audit, breaks §5.5 generalization**. UncAnsMgr (β<0) and UncPreMgr (β>0) opposite-direction on same DV. Lagged_DV ≈ 0.46 ind / 0.32 firm | KEEP | First suite breaking the §5.5 cross-sectional-only UncPreMgr pattern: UncPreMgr survives firm FE in 3 contemp cells. Mgr/PreMgr opposite-sign split on the same DV. New §5.9 entry |
| H19b | ChangExternalFunding (cols 1-6); ChangExternalFunding_lead (cols 7-12) | 60,052–65,069 | Q1 (provisional) | UncAnsCEO 0/12, UncPreCEO 0/12, UncPreMgr 0/12; UncAnsMgr 2/12 sig β<0 (cols 9 + 11, both Ind+ExtCtrl lead with year/yq variants — match tail). Lagged_DV ≈ +0.07 ind / **-0.07 firm** — first negative-persistence DV in the audit (mean reversion under firm FE) | KEEP | Weak primary-IV lead-horizon signal, 2/12 sig β<0 matching the H4a/H4b family direction at much lower breadth. Negative Lagged_DV under firm FE is structurally novel for the Chang (2006) financing-decision DV class. New §5.10 entry on negative-persistence DV class |
| H20b | ChangDebtChoice (cols 1-6); ChangDebtChoice_lead (cols 7-12) | **3,404–13,666 (Chang restricted sample, 4-15× smaller than other Q1 suites)** | Q1 (provisional) | **TWO-TAILED**. UncAnsCEO 0/12, UncAnsMgr 0/12; UncPreCEO 2/12 sig β<0 (cols 1, 3 industry-FE contemp); UncPreMgr 3/12 sig β>0 (cols 1, 3, 5 industry-FE contemp). **Pre-CEO and Pre-Mgr OPPOSITE directions on same DV** — first opposite-direction Pre split. Lead horizon 0/24 sig anywhere. Lagged_DV all-negative (mean reversion) | **DROP** | **User decision 2026-04-15** (verbatim): *"20b drop, since the findings are not clean and seems like a heaache"*. Per rule 21 "empirically uninterpretable" criterion: tiny restricted sample + primary IV null + Pre-CEO/Pre-Mgr opposite-direction sig cells + zero lead-horizon signal = no coherent finding. Negative Lagged_DV logged §5.10 alongside H19b for the DV-class observation |

### 4.2 Per-suite blocks

_Populated during audit. One block per suite. Template at the bottom of this section._

### H1 — Speech Uncertainty and Cash Holdings

- **DV**: `CashRatio` (cols 1-6); `CashRatio_lead` (cols 7-12, reported as robustness / lead-spec check)
- **N**: 59,440–65,128 (main sample, ex financials and utilities)
- **FE ladder** (repeats per DV): (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl
- **Tail**: one-tailed, β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsMgr` **7/12 sig β>0** (6/6 contemp all FE ladders cols 1-6 + col 9 lead ind+yr+ext only — strongest IV pattern in the suite); `UncAnsCEO` 4/12 sig β>0 (lead only — cols 7 ind+yr, 10 firm+yr+ext, 11 ind+yq+ext, 12 firm+yq+ext); `UncPreMgr` 2/12 sig β>0 (col 3 contemp ind+yr+ext, col 9 lead ind+yr+ext — both industry-FE only); `UncPreCEO` 0/12 null.
    - **Base controls**: `Leverage` 12/12 sig β<0 (cash-leverage substitution, no flag); `lnAssets` 11/12 sig β<0 + **1 sign-flip anomaly at col 9 ind+yq+ext lead (β=+0.0010**)** flag; `TobinsQ` 11/12 sig β>0 (col 8 firm+yr lead null); `ROA` 11/12 sig β<0 (col 2 firm+yr contemp null); `Capex` 12/12 sig β<0; `DivDummy` 6/12 sig β<0 — **all 6 industry-FE cells, firm-FE 0/6 (FE-strata split)**; `sCFO` 6/12 sig β>0 — **all 6 industry-FE cells, firm-FE 0/6 (FE-strata split)**.
    - **Extended controls** (cols 3-6, 9-12 only): `SalesGrowth` 8/8 sig β<0; `RDSales` 4/8 sig β>0 — **all 4 industry-FE only (FE-strata split)**; `CashFlowAt` 8/8 sig β>0; `DailyVola` 7/8 sig — **FE-strata sign flip**: 5 industry-FE sig β>0, 2 firm-FE sig β<0 (cols 4, 6).
    - **Lagged_DV** (rule 23 structural exception): 0.85 / 0.86 / 0.86 (ind contemp); 0.71 / 0.73 / 0.72 (ind lead); 0.63 / 0.64 / 0.64 (firm contemp); **0.22 / 0.23 / 0.23 (firm lead — collapse)**.
    - **R² / N**: contemp 0.819 / 0.452 → 0.823 / 0.458; lead 0.636 / 0.093 → 0.646 / 0.106. N = 65,128 (cols 1-2) → 62,504 (cols 3-6 contemp) → 60,619 (cols 7-8 lead) → 59,440 (cols 9-12 lead). Within-firm R² much lower than industry-FE R² across all specs.
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsMgr` **6/12 sig β<0 — all 6 lead cells** (cols 7-12 all FE ladders incl. Firm+YQ+ExtCtrl col 12 β=-0.0064**). Contemp 0/6 null. `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncPreMgr` 0/12 null. **Cleanest IV hierarchy in Q1 cluster** (no CEO/Mgr inversion, no PreMgr loading).
    - **Base controls**: `lnAssets` 12/12 sig β>0 (large firms more levered, consistent); `TobinsQ` 9/12 sig β>0 — **sign anomaly flag**: classic Q theory predicts β<0 (high Q → low leverage), positive sign here is unusual; `ROA` 12/12 sig β<0 (pecking order); `Capex` 6/12 sig β>0 — all 6 lead cells, contemp 0/6 (capex predicts higher future leverage); `DivDummy` 9/12 sig β>0 — cols 1, 3, 5 ind contemp + all 6 lead, firm contemp 0/3 null; `sCFO` 2/12 sig β<0 (cols 3, 5 ind contemp only); `CashRatio` (cross-DV) 12/12 sig β<0 (cash-leverage substitution).
    - **Extended controls** (cols 3-6, 9-12): `SalesGrowth` 6/8 sig β>0 — 4 contemp (cols 3-6) + 2 lead (cols 10, 12); `RDSales` 2/8 sig β<0 — cols 3, 5 ind contemp only (FE-strata split, ind only); `CashFlowAt` 8/8 sig β<0 (more cash flow → less leverage); `DailyVola` 7/8 sig β>0 (col 9 lead null).
    - **Lagged_DV** (rule 23 structural): **0.94 / 0.94 / 0.94 (ind contemp); 0.83 / 0.83 / 0.83 (ind lead); 0.76 / 0.75 / 0.75 (firm contemp); 0.38 / 0.37 / 0.37 (firm lead)**. **Very high persistence — much stickier than H1 cash** (firm lead 0.37-0.38 vs H1's 0.22-0.23).
    - **R² / N**: contemp 0.889 / 0.613 → 0.891 / 0.618; lead 0.714 / 0.175 → 0.716 / 0.185. N = 65,132 → 62,508 → 60,626 → 59,447. Lead within-firm R² very low (0.18).
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsMgr` **5/12 sig β<0** — cols 7, 8, 9, 10, 11 (lead, all FE ladders except col 12). **Col 12 Firm+YQ+ExtCtrl narrow miss** (β=-0.0069, p_one≈0.105 — slightly weaker than H4a col 12 β=-0.0064**). Contemp 0/6 null. `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncPreMgr` 0/12 null. Clean IV hierarchy.
    - **Base controls**: `lnAssets` 6/12 sig β>0 — **all 6 industry-FE cells, firm-FE 0/6 null (FE-strata split)**; `TobinsQ` 6/12 sig β>0 — **all 6 industry-FE cells, firm-FE 0/6 (FE-strata split)** + same Q-theory sign anomaly as H4a; `ROA` 12/12 sig β<0 (pecking order); `Capex` 3/12 sig β>0 — cols 7, 9, 11 lead industry-FE only, contemp 0/6 (industry-FE lead only); `DivDummy` 9/12 sig β>0 — cols 1, 3, 5 ind contemp + all 6 lead; `sCFO` 0/12 null; `CashRatio` (cross-DV) 12/12 sig β<0.
    - **Extended controls**: `SalesGrowth` 4/8 sig β>0 — all 4 contemp (cols 3-6); lead 0/4 null; `RDSales` 4/8 sig β<0 — cols 3, 5 contemp ind + 9, 11 lead ind (FE-strata split, ind only); `CashFlowAt` 4/8 sig β<0 — **firm-FE only** (cols 4, 6 contemp + 10, 12 lead — opposite FE-strata vs lnAssets/TobinsQ which are ind-only); `DailyVola` 8/8 sig β>0.
    - **Lagged_DV** (rule 23 structural): **0.93 / 0.92 / 0.92 (ind contemp); 0.80 / 0.80 / 0.79 (ind lead); 0.79 / 0.78 / 0.78 (firm contemp); 0.41 / 0.40 / 0.39 (firm lead)**. Very high persistence (similar to H4a leverage).
    - **R² / N**: contemp 0.867 / 0.620 → 0.869 / 0.620; lead 0.662 / 0.189 → 0.665 / 0.194. N = 64,895 → 62,286 → 60,363 → 59,190.
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsMgr` 0/12 null; `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncPreMgr` **6/12 sig β<0** — sig cells 1, 3, 5 (contemp ind-FE) + 7, 9, 11 (lead ind-FE). All 6 industry-FE; firm-FE 0/6 across both DVs. **FE-ladder survival across all 4 IVs × both DVs**: industry-FE 6/24 sig (all UncPreMgr); firm-FE 0/24 sig.
    - **Base controls**: `lnAssets` 9/12 sig — **FE-strata sign flip flag**: 6 industry-FE sig β>0 (cols 1, 3, 5, 7, 9, 11), 3 firm-FE contemp sig β<0 (cols 2, 4, 6), firm-FE lead null; `TobinsQ` 12/12 sig β>0; `ROA` 12/12 sig β<0; `Leverage` 3/12 sig β>0 — **firm-FE contemp only** (cols 2, 4, 6), ind 0/6, lead 0/6; `CashRatio` 8/12 sig — **horizon-FE split**: cols 2, 4, 6 contemp firm sig β<0, cols 8-12 lead mostly sig β>0 (sign flip across horizon); `Capex` 9/12 sig β<0 — cols 1-6 contemp + cols 7, 9, 11 lead (firm lead null); `sCFO` 5/12 sig β<0 — all 5 in industry-FE cells.
    - **Extended controls**: `SalesGrowth` 8/8 sig β<0 (strong consistent); `RDSales` 4/8 sig β<0 — cols 3, 5 contemp ind + 9, 11 lead ind (FE-strata split, ind only); `CashFlowAt` 6/8 sig — **FE-strata sign flip**: ind contemp + lead sig β>0 (3, 5, 9, 11), firm lead sig β<0 (10, 12); `DailyVola` 6/8 sig — **FE × horizon sign mix**: ind contemp + lead sig β<0 (3, 5, 9, 11), firm lead sig β>0 (10, 12).
    - **Lagged_DV** (rule 23 structural exception): **0.26 / 0.25 / 0.25 (ind contemp); 0.24 / 0.23 / 0.23 (ind lead); 0.073 / 0.069 / 0.071 (firm contemp); 0.039 / 0.035 / 0.036 (firm lead)**. **Drastically lower than H1/H4a/H4b** — payout near-zero quarter persistence under firm FE. Recorded §5.6.
    - **R² / N**: contemp 0.079 / 0.015 → 0.086 / 0.016; lead 0.064 / 0.010 → 0.070 / 0.012. **Very low R²** — payout much harder to predict than balance-sheet stocks. N = 47,651 → 45,779 → 45,466 → 44,624.
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` **1/12 sig β<0** — col 6 only (Firm+YQ+ExtCtrl contemp). The only firm-FE survivor across all 4 IVs. `UncPreMgr` **6/12 sig β<0** — all 6 industry-FE cells (1, 3, 5 contemp + 7, 9, 11 lead); firm-FE 0/6. **FE-ladder survival across all 4 IVs × both DVs**: industry-FE 6/24 sig (all UncPreMgr); firm-FE 1/24 sig (UncAnsMgr col 6 only).
    - **Base controls**: `lnAssets` 12/12 sig β>0 (large firms more likely to pay dividends); `TobinsQ` 8/12 sig β>0 (cols 1-7, 9 sig; cols 8, 10, 11, 12 null); `ROA` 10/12 sig β>0 (cols 4, 6 firm contemp null); `Leverage` 12/12 sig β<0 (levered firms less likely to pay); `CashRatio` 6/12 sig — **horizon-FE split**: cols 1, 3, 5 contemp ind sig β<0; cols 8, 10, 12 lead firm sig β>0; `Capex` 9/12 sig — **FE sign flip in contemp**: cols 1, 3, 5 ind contemp sig β<0; cols 2, 4, 6 firm contemp sig β>0; cols 7, 9, 11 ind lead sig β<0; firm lead null. Anomaly flag; `sCFO` 0/12 null.
    - **Extended controls**: `SalesGrowth` 4/8 sig β<0 — cols 3, 5, 6 contemp + col 9 lead; `RDSales` 4/8 sig β>0 — cols 3, 5 contemp ind + 9, 11 lead ind (FE-strata split, ind only); `CashFlowAt` 0/8 null (different from H12 which had splits); `DailyVola` 8/8 sig β<0.
    - **Lagged_DV** (rule 23 structural): **0.91 / 0.90 / 0.90 (ind contemp); 0.91 / 0.91 / 0.91 (ind lead); 0.70 / 0.69 / 0.69 (firm contemp); 0.72 / 0.72 / 0.72 (firm lead)**. **High persistence** (sticky payer status — structurally opposite of H12 PayoutRatio_q's 0.07).
    - **R² / N**: contemp 0.846 / 0.500 → 0.846 / 0.496; lead 0.859 / 0.536 → 0.860 / 0.537. High and stable. N = 64,145 → 61,535 → 61,359 → 60,175.
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 3/12 sig β>0 — **all 3 firm-FE contemp** (cols 2, 4, 6). Lead 0/6 null. `UncPreCEO` 0/12 null. `UncAnsMgr` 4/12 sig β>0 — **all 4 industry-FE** (col 3 contemp + cols 7, 9, 11 lead). Firm-FE 0/6 both DVs. `UncPreMgr` 1/12 sig β<0 — col 11 (ind+yq+ext lead) only. **Cross-IV FE-strata split**: UncAnsCEO firm-FE / UncAnsMgr industry-FE, both β>0 — two primary IVs in different FE strata with same direction.
    - **Base controls**: `lnAssets` 9/12 sig — **FE × col sign mix**: cols 3, 9 ind sig β>0; col 11 ind sig β<0; all 6 firm-FE cells sig β<0. Anomaly flag; `TobinsQ` 12/12 sig β>0 (consistent); `ROA` 10/12 sig — **strong sign anomaly**: cols 3-6 contemp sig β<0; cols 7-8, 10, 12 lead sig β>0; col 9, 11 ind lead sig β<0. FE × horizon sign mix; `Leverage` 9/12 sig β<0 — cols 1-6 contemp + 8, 10, 12 firm lead. Ind lead null; `CashRatio` 7/12 sig β<0 — 6 contemp + col 11 lead; `DivDummy` 8/12 sig — **FE sign flip**: ind cells (1, 5, 7, 9, 11) sig β<0; firm contemp (2, 4, 6) sig β>0; firm lead null; `sCFO` 9/12 sig β<0 — 6 contemp + 3 firm lead (8, 10, 12); ind lead null.
    - **Extended controls**: `SalesGrowth` 8/8 sig β>0 (consistent); `RDSales` 8/8 sig β>0 (small β=0.0008-0.0019); `CashFlowAt` 8/8 sig β>0 (large β=0.018-0.059); `DailyVola` 7/8 sig — **sign flip across horizon**: contemp positive (3, 4 sig +); lead all sig β<0 (9, 10, 11, 12). Col 6 sig β<0 contemp anomaly.
    - **Lagged_DV** (rule 23 structural): **0.76 / 0.74 / 0.74 (ind contemp); 0.65 / 0.64 / 0.64 (ind lead); 0.32 / 0.32 / 0.32 (firm contemp); 0.086 / 0.087 / 0.088 (firm lead)**. Moderate ind persistence; weak firm contemp; **near-zero firm lead** (similar to H12 PayoutRatio_q).
    - **R² / N**: contemp 0.617 / 0.144 → 0.626 / 0.150; lead 0.490 / 0.058 → 0.501 / 0.068. N = 65,105 → 62,482 → 60,090 → 58,897.
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
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` 0/12 null. **0/48 sig across all 4 IVs × all 12 cells — first complete-null suite in the audit.**
    - **Base controls**: `lnAssets` 7/12 sig β>0 — cols 1, 3, 4, 5, 6, 7, 11 (mostly contemp ind + firm + col 11 lead); `TobinsQ` 5/12 sig β>0 — cols 1, 3, 4, 5, 6 contemp only. Lead 0/6 null; `ROA` 3/12 sig β<0 — cols 1, 2 contemp + col 7 ind lead; `Leverage` 4/12 sig β<0 — cols 1, 2, 3, 5 contemp only. Lead 0/6 null; `CashRatio` 8/12 sig β>0 — cols 1, 2, 3, 5, 7, 8, 9, 11; `Capex` 4/12 sig — **sign anomaly**: col 1 sig β<0 (ind contemp); cols 3, 4, 5 sig β>0 (with ext). Anomaly flag; `DivDummy` 2/12 sig β<0 — cols 3, 5 contemp only; `sCFO` 0/12 null.
    - **Extended controls**: `SalesGrowth` 4/8 sig β<0 — cols 3, 4, 5, 6 contemp only. Lead 0/4 null; `CashFlowAt` 6/8 sig β<0 — cols 3, 4, 5, 6 contemp + 9, 11 lead ind; `DailyVola` 1/8 sig — col 6 only (firm+yq+ext contemp -0.0007**).
    - **Lagged_DV** (rule 23 structural): **0.66 / 0.74 / 0.74 (ind contemp); 0.52 / 0.51 / 0.51 (ind lead); 0.28 / 0.39 / 0.39 (firm contemp); 0.040 / 0.057 / 0.057 (firm lead — null at α=0.10)**. Cols 8, 10, 12 firm lead Lagged_DV null. Within-firm RDSales has near-zero own persistence at lead horizon.
    - **R² / N**: contemp 0.448 / 0.072 → 0.505 / 0.185; lead 0.252 / 0.004 → 0.259 / 0.007. **Very low R² firm contemp (0.07-0.18) and firm lead near-zero (0.004-0.007)** — within-firm R&D essentially unexplainable by the spec. N = 65,086 → 62,517 → 60,105 → 58,970.
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: Speech uncertainty is silent on R&D investment intensity under any IV (CEO or Mgr; Ans or Pre), any FE ladder (industry or firm), any horizon (contemp or lead). Per rule 21 explicit DROP criterion, "all-null" is reserved-for-DROP. R&D investment does not covary with management or CEO speech uncertainty. The cleanest null in the audit so far. A possible reading is that R&D is a long-horizon, sticky, multi-year decision insensitive to quarterly speech-uncertainty fluctuations, but that is post-audit synthesis material — not interpreted here.
- **Verdict**: **DROP (provisional, flagged for revisit)**.
- **Rationale**: Per rule 21 explicit DROP criterion. **User decision 2026-04-15** (verbatim): *"for RD, we will decide later if we had a very good reason to keep it, but for now, flag it as drop"*. Reasons to potentially revisit at synthesis: (a) a clean null is a kind of finding that constrains narrative scope ("speech uncertainty does not move R&D investment under any identification"), (b) if the post-audit thesis frame needs an honest null on R&D for completeness or balance, KEEP-as-honest-null may be preferred. Default DROP unless a strong reason emerges. New §5.8 entry on the first complete-null suite.

### H17 — Speech Uncertainty and Repurchase Intensity

- **DV**: `RepurchaseIntensity` (cols 1-6); `RepurchaseIntensity_lead_qtr` (cols 7-12)
- **N**: 57,529–61,030 (main sample, ex financials and utilities)
- **FE ladder**: identical to prior Q1 suites
- **Tail**: **TWO-TAILED** (line 1758 notes block — exploratory like H13/H16)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 0/12 null; `UncPreCEO` 1/12 sig β>0 — col 8 (firm+yr lead 0.0004*) only; `UncAnsMgr` **4/12 sig β<0** — cols 1, 3, 5 (industry-FE contemp) + col 7 (industry-FE lead). All industry-FE; firm-FE 0/6; `UncPreMgr` **7/12 sig β>0** — cols 1, 3, 5 (industry-FE contemp) + **cols 2, 4, 6 (firm-FE contemp)** + col 7 (ind lead). **First UncPreMgr firm-FE survival in the audit.** **FE survival across all 4 IVs × both DVs**: industry-FE 8/24 sig; firm-FE 4/24 sig (PreMgr 3 contemp + PreCEO 1 lead). **Direction split**: Mgr β<0 (4 cells); PreMgr β>0 (7 cells). Opposite signs same DV.
    - **Base controls**: `lnAssets` 9/12 sig β>0 — cols 1, 3, 5 ind contemp + all 6 lead. Cols 2, 4, 6 firm contemp null; `TobinsQ` 12/12 sig β>0 (consistent positive); `ROA` 12/12 sig β>0 (consistent positive); `Leverage` 9/12 sig β<0 — cols 2, 4, 6 firm contemp + all 6 lead. Cols 1, 3, 5 ind contemp null; `Capex` 6/12 sig — **FE sign flip**: cols 2, 4 firm contemp sig β>0; cols 3, 5 ind contemp sig β<0; cols 9, 11 ind lead sig β<0. Anomaly flag; `CashRatio` 12/12 sig — **FE sign mix in contemp**: ind contemp (1, 3, 5) sig β>0; firm contemp (2, 4, 6) sig β<0; all lead sig β>0; `DivDummy` 1/12 sig — col 2 only (firm+yr 0.0006*); `sCFO` 6/12 sig β<0 — cols 1, 3, 5, 7, 9, 11 (all industry-FE).
    - **Extended controls**: `SalesGrowth` 8/8 sig β<0 (consistent); `RDSales` 4/8 sig β>0 — cols 3, 5, 9, 11 (industry-FE only, FE-strata split); `CashFlowAt` 8/8 sig β>0 (consistent); `DailyVola` 8/8 sig β<0 (very small magnitudes ≈ 10^-5).
    - **Lagged_DV** (rule 23 structural): **0.47 / 0.46 / 0.45 (ind contemp); 0.36 / 0.35 / 0.35 (ind lead); 0.32 / 0.32 / 0.31 (firm contemp); 0.19 / 0.19 / 0.19 (firm lead)**. Moderate persistence; firm lead 0.19 (intermediate between H1 cash and H12 payout).
    - **R² / N**: contemp 0.300 / 0.117 → 0.309 / 0.119; lead 0.233 / 0.064 → 0.245 / 0.067. N = 61,030 → 58,550 → 58,610 → 57,529.
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: H17 RepurchaseIntensity is the first suite where the cross-sectional-only UncPreMgr pattern from §5.5 (H1/H12/H12b) does NOT hold — UncPreMgr survives firm FE in 3 contemp cells. The §5.5 generalization is now contradicted by H17 and needs re-scoping post-audit. Separately, UncAnsMgr (4 cells β<0) and UncPreMgr (7 cells β>0) carry opposite-direction signals on the same DV — a measurement-concerns flag per `feedback_ceo_noisy_mgr_central.md` (do NOT build narrative; log only). Two-tailed spec means no directional prediction.
- **Verdict**: **KEEP — informative mixed pattern with novel structure**.
- **Rationale**: Three informative facts: (a) **first UncPreMgr firm-FE survival in the audit**, (b) opposite-sign Mgr/PreMgr split on the same DV, (c) UncAnsMgr's clean 4-cell industry-FE β<0 pattern. KEEP per rule 21 — informative pattern. New §5.9 entry on the UncPreMgr firm-FE survival breaking the §5.5 generalization.

### H19b — Speech Uncertainty and External vs Internal Financing (Chang et al. 2006)

- **DV**: `ChangExternalFunding` (cols 1-6); `ChangExternalFunding_lead` (cols 7-12)
- **N**: 60,052–65,069 (main sample, ex financials and utilities)
- **FE ladder**: identical to prior Q1 suites
- **Tail**: one-tailed, β<0 for IVs (line 1959 notes block); two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` **2/12 sig β<0** — cols 9 (ind+yr+ext lead) + 11 (ind+yq+ext lead). Both industry-FE lead with extended controls; matches tail. `UncPreMgr` 0/12 null. **FE survival across all 4 IVs × both DVs**: industry-FE 2/24 sig (UncAnsMgr lead-only with ExtCtrl); firm-FE 0/24 sig.
    - **Base controls**: `lnAssets` 8/12 sig — cols 1, 3 contemp ind sig β<0; cols 7-12 all lead sig β<0 (firm lead very large -0.12). Cols 2, 4, 5, 6 contemp null; `TobinsQ` 12/12 sig β>0 (consistent); `ROA` 10/12 sig — **strong sign anomaly**: col 1 sig β<0 (ind+yr); cols 3-6 contemp sig β>0 (with ext); col 7 sig β<0 (ind+yr lead); cols 9-12 sig β>0. FE × spec sign flip; `Leverage` 12/12 sig — **lead FE sign flip**: contemp all β>0 (1-6); lead ind β>0 (7, 9, 11); lead firm β<0 (8, 10, 12). Anomaly flag; `Capex` 12/12 sig β>0 (very strong, β=0.65-1.00); `CashRatio` 8/12 sig β<0 — cols 3, 5, 7, 8, 9, 10, 11, 12; `DivDummy` 6/12 sig β>0 — all 6 firm-FE cells (2, 4, 6, 8, 10, 12). Ind 0/6 null; `sCFO` 5/12 sig β<0 — cols 4, 6, 8, 10, 12 firm-FE only (FE-strata split).
    - **Extended controls**: `SalesGrowth` 6/8 sig β>0 — 4 contemp (3-6) + 2 lead (9, 11); `RDSales` 4/8 sig β>0 — cols 4, 6 contemp firm + 9, 11 lead ind. Mixed FE; `CashFlowAt` 8/8 sig β<0 (strong consistent); `DailyVola` 1/8 sig — col 9 only (lead ind -0.0003*).
    - **Lagged_DV** (rule 23 structural): **+0.081 / +0.058 / +0.057 (ind contemp); +0.083 / +0.072 / +0.072 (ind lead); −0.071 / −0.085 / −0.085 (firm contemp); −0.035 / −0.036 / −0.036 (firm lead)**. **Sign flip across FE strata** — ind positive, firm negative. **First negative-persistence DV under firm FE** (mean reversion on the Chang external-funding measure). All sig.
    - **R² / N**: contemp 0.054 / 0.025 → 0.082 / 0.048; lead 0.033 / 0.031 → 0.040 / 0.031. **Low R²** — financing decisions hard to predict. N = 65,069 → 62,450 → 60,052 → 58,871.
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: Weak primary-IV lead-horizon signal — 2/12 UncAnsMgr sig cells, both industry-FE lead with extended controls, both β<0 matching the tail. No CEO measures, no UncPreMgr, no contemp signal. The lead-horizon β<0 direction echoes the H4a/H4b family pattern (lead-horizon negative on financing structure) but at much lower breadth (2/12 vs 5-6/12). Negative Lagged_DV under firm FE is structurally novel for the Chang (2006) financing-decision DV class.
- **Verdict**: **KEEP — weak but directionally consistent primary-IV lead-horizon signal**.
- **Rationale**: Tracks the H4a/H4b lead-horizon β<0 family direction at lower breadth. Small primary-IV signal (2/12) is informative for the cluster pattern even though the suite is not strong on its own. Negative Lagged_DV (mean reversion) is a new DV-class observation logged in §5.10. KEEP per rule 21 — informative pattern (matches family direction).

### H20b — Speech Uncertainty and Debt vs Equity Choice (Chang et al. 2006)

- **DV**: `ChangDebtChoice` (cols 1-6); `ChangDebtChoice_lead` (cols 7-12)
- **N**: **3,404–13,666** (Chang restricted sample — debt-vs-equity decisions among external-financing events; **4-15× smaller than other Q1 suites**)
- **FE ladder**: identical to prior Q1 suites
- **Tail**: **TWO-TAILED** (line 2027 notes block)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-15):
    - **IVs**: `UncAnsCEO` 0/12 null; `UncPreCEO` 2/12 sig β<0 — cols 1, 3 (industry-FE contemp); `UncAnsMgr` 0/12 null; `UncPreMgr` 3/12 sig β>0 — cols 1, 3, 5 (industry-FE contemp). **Direction conflict**: PreCEO β<0 vs PreMgr β>0 on same DV — **first opposite-direction Pre split in the audit**. **FE survival across all 4 IVs × both DVs**: industry-FE 5/24 sig (all contemp); firm-FE 0/24 sig. **Lead horizon 0/24 sig anywhere**.
    - **Base controls**: `lnAssets` 9/12 sig β>0 — cols 1-7, 9, 11. Cols 8, 10, 12 firm lead null; `TobinsQ` 9/12 sig β<0 — cols 1-6 contemp + 7, 9, 11 lead ind. Firm lead null; `ROA` 12/12 sig β>0 (consistent); `Leverage` 9/12 sig — **lead FE sign flip**: contemp all β>0 (1-6); lead ind null (7, 9, 11); lead firm sig β<0 (8, 10, 12). Anomaly flag; `Capex` 5/12 sig β>0 — cols 2-6 contemp only. Col 1 + lead 0/6 null; `CashRatio` 9/12 sig β<0 — cols 1-7, 9, 11. Cols 8, 10, 12 firm lead null; `DivDummy` 5/12 sig β>0 — cols 1, 2, 3, 5, 7; `sCFO` 6/12 sig β<0 — cols 1-6 contemp only. Lead 0/6 null.
    - **Extended controls**: `SalesGrowth` 4/8 sig β>0 — cols 3-6 contemp only. Lead 0/4 null; `RDSales` 0/8 null; `CashFlowAt` 5/8 sig β<0 — cols 4, 5, 6 contemp + 9, 11 lead ind; `DailyVola` 7/8 sig β<0 — cols 3, 5, 6, 9, 10, 11, 12. Col 4 null.
    - **Lagged_DV** (rule 23 structural): **−0.087 / −0.089 / −0.086 (ind contemp); −0.052 / −0.053 / −0.053 (ind lead); −0.050 / −0.056 / −0.056 (firm contemp); −0.013 / −0.017 / −0.018 (firm lead, mostly null)**. **All-negative Lagged_DV across all 12 cells** — strong mean reversion. Second negative-persistence DV after H19b. Cols 8, 10, 12 firm lead null.
    - **R² / N**: contemp 0.249 / 0.075 → 0.260 / 0.083; lead 0.231 / 0.056 → 0.254 / 0.066. **Tiny restricted sample**: N = 13,666 (cols 1-2) → 13,057 (cols 3-6) → 3,518 (cols 7-8 lead) → 3,404 (cols 9-12 lead). **4-15× smaller than other Q1 suites** due to Chang external-financing-event restriction.
- **Reader-question**: Q1 (provisional, placeholder).
- **Argument**: Three structural concerns: (a) sample is 4-15× smaller than other Q1 suites due to Chang's external-financing-event restriction, (b) primary IV UncAnsMgr is 0/12 null, (c) UncPreCEO (β<0) and UncPreMgr (β>0) carry opposite-direction sig cells on the same DV — measurement-concerns flag without a coherent reading. Lead horizon 0 sig anywhere. The pattern exists but is uninterpretable as a clean finding.
- **Verdict**: **DROP**.
- **Rationale**: **User decision 2026-04-15** (verbatim): *"20b drop, since the findings are not clean and seems like a heaache"*. Per rule 21, DROP is reserved for suites where no informative pattern exists OR where empirically uninterpretable. H20b's combination of (a) tiny restricted sample, (b) primary IV null, (c) Pre-CEO/Pre-Mgr opposite-direction sig cells, and (d) zero lead-horizon signal makes the suite empirically uninterpretable as a clean finding. The Chang sample restriction makes generalizability suspect even if the Pre pattern were clean. Logged §5.10 alongside H19b for the negative-persistence DV class observation.

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

### 5.9 UncPreMgr firm-FE survival on repurchases breaks §5.5 generalization (H17)

- **Observation**: §5.5 above (updated through H12b) generalized that UncPreMgr loads cross-sectionally (industry-FE) but not within-firm (firm-FE) across H1 cash, H12 payout, and H12b payer indicator. **H17 RepurchaseIntensity contradicts that generalization**: UncPreMgr is sig β>0 in 3 firm-FE contemp cells (cols 2, 4, 6) AND in 4 industry-FE cells (cols 1, 3, 5, 7), 7/12 sig total. This is the **first UncPreMgr firm-FE survival in the audit so far**. The §5.5 cross-sectional-only generalization does NOT hold for repurchases.
- **Status**: Factual cross-suite observation. Per `feedback_ceo_noisy_mgr_central.md`, UncPreMgr is a secondary measure with measurement concerns; do NOT interpret here. Possible implications for post-audit synthesis: (a) repurchase decisions may be more sensitive to scripted/IR-vetted language than other Q1 outcomes, (b) the §5.5 cross-sectional-only generalization needs to be re-scoped post-audit to "cash/payout/payer DVs" rather than "all Q1 DVs". Note: H17 also has UncAnsMgr (β<0, 4 cells industry-FE) AND UncPreMgr (β>0, 7 cells mixed FE) — the two Mgr measures hit OPPOSITE directions on the same DV, which is a separate measurement-concerns flag. Log only; revisit at synthesis.
- **Loaded from**: H17 (2026-04-15).

### 5.10 Negative-persistence DV class: Chang (2006) financing measures show mean reversion (H19b + H20b)

- **Observation**: H19b ChangExternalFunding and H20b ChangDebtChoice both show negative or near-zero Lagged_DV under firm FE — a structural property different from all prior Q1 DVs. Specifically:
    - **H19b**: Lagged_DV ≈ +0.07 (ind) / **-0.07 (firm)** contemp; +0.08 (ind) / -0.04 (firm) lead. Sign flip across FE strata.
    - **H20b**: Lagged_DV ≈ **-0.09 (ind) / -0.05 (firm)** contemp; -0.05 (ind) / -0.02 (firm) lead. **All-negative across all 12 cells**.
    Compare prior Q1 DVs: H1 Cash 0.85/0.63, H4a Leverage 0.94/0.76, H4b DebtToCapital 0.93/0.79, H12 PayoutRatio_q 0.25/0.07, H12b DivPayerQ 0.91/0.70, H13 Capex 0.74/0.32, H17 RepurchaseIntensity 0.46/0.32. All persistence-loaded (positive). H19b and H20b are the first DVs with negative or near-zero firm-FE persistence.
- **Status**: Structural property of the Chang (2006) financing-decision DV class. These DVs measure financing CHOICES (whether to use external funding; whether to issue debt vs equity), which are episodic decisions not stocks. Episodic decisions should mean-revert, not persist, so the negative Lagged_DV is consistent with the DV semantics. Not a bug. Implication: comparing IV signal across stock-DVs (H1/H4a/H4b/H12b/H17) and flow/decision-DVs (H19b/H20b) may not be apples-to-apples for any post-audit synthesis on within-firm signal strength. Log only; revisit at end-of-audit synthesis.
- **Loaded from**: H19b + H20b (2026-04-15).

### 5.11 Queued observations (to populate as audit proceeds)

- UncAnsMgr robustness pattern across the Q2/Q3/Q4 clusters — where firm-FE survives, where it dies.
- Sample-size bands and what they imply for generalizability (H22 annual, H5 IBES Detail, H20b Chang sample DROP precedent).
- Q5 economic magnitude sweep (cross-cutting, at end of audit).

### 5.12 Audit cataloguing format shift mid-Q1 → REVERSED same day: all Q1 re-catalogued under rule 24 full-row format (2026-04-15)

- **Observation**: Across all 10 Q1 cluster suites (H1, H4a, H4b, H12, H12b, H13, H16, H17, H19b, H20b), the per-suite §4.2 "Key cell fact" line had originally catalogued only the 4 IVs + Lagged_DV. Controls were read linearly per rule 6 when reading `outputs/all_tables.tex` but were not catalogued in the §4.2 record except in 2 incidental cases (H4a `CashRatio` β=-0.0297***, H4b `CashRatio` β=-0.0674***). The gap surfaced 2026-04-15 at the Q1→Q2 boundary when the user asked: *"are you telling me that you have not read the contorl behavior in each suite so far?"* and earlier issued: *"we must read ALL results in the suites for all variables in their tables!"*.
- **Root cause**: Rule 23 framed audit observables as IV-specific ("sig-star count + FE-ladder survival + sig-cell direction" for IVs). I conflated **verdict scope** (rule 21 — KEEP/DROP/REFRAME rests on IV × FE × DV informative pattern) with **record scope** (what gets catalogued in §4.2). Controls don't bear on the verdict, so I cut them from the record by default. Same root failure family as rule 21 (filtering through Q-target) and rule 22 (filtering through null-sign-as-signal).
- **Fix**: Rule 24 added 2026-04-15 to `feedback_phase5_methodology.md`. Every §4.2 block must catalogue every row of the regression table — IVs (or main+moderator+interaction for Q2 moderation suites), all controls, Lagged_DV, R²/N.
- **Q1 retroactive — REVERSED 2026-04-15**: Initial user decision was "no" on retroactive Q1 rework. **Reversed same day**: user directive *"read the first 10 suites again, with the new approach, 5 at a time"*. **All 10 Q1 suites re-catalogued under rule 24 full-row format** in 2 batches (batch 1: H1/H4a/H4b/H12/H12b; batch 2: H13/H16/H17/H19b/H20b). §4.2 "Key cell fact" lines now contain row-by-row catalogue for every Q1 suite. **Argument/Verdict/Rationale lines unchanged** (preserves prior session work; H1 magnitude paragraph still flagged for Q5 migration per rule 23).
- **What the re-catalogue surfaced** (controls-side observations not visible in the IV-only records):
    - **FE-strata splits** in controls were rampant across Q1 suites — `lnAssets`, `TobinsQ`, `RDSales`, `CashFlowAt`, `DivDummy`, `sCFO` all show industry-FE-only or firm-FE-only patterns on at least one DV. Suggests cross-sectional vs within-firm identification matters more than the IV-only audit indicated.
    - **Sign-flip anomalies** in controls: H1 `lnAssets` col 9; H1 `DailyVola` ind+ vs firm−; H4a/H4b `TobinsQ` Q-theory sign anomaly (β>0 not β<0); H12 `lnAssets` ind+/firm−; H12 `CashFlowAt` ind+/firm lead−; H12 `DailyVola` ind−/firm lead+; H12b `Capex` ind−/firm contemp+; H13 `lnAssets` mixed; H13 `ROA` FE × horizon × spec sign mix; H13 `DivDummy` ind−/firm contemp+; H17 `Capex` ind−/firm contemp+; H17 `CashRatio` ind+/firm contemp−; H19b `ROA` FE × spec sign flip; H19b `Leverage` lead ind+/firm−; H20b `Leverage` lead ind null/firm−.
    - **R² heterogeneity**: H1/H4a/H4b have very high industry-FE R² (0.82-0.89) and low firm-FE R² (0.45-0.62); H12 PayoutRatio_q has very low R² across the board (0.01-0.09); H16 RDSales has near-zero firm-FE lead R² (0.004-0.007); H19b/H20b Chang DVs also low R² (0.03-0.26). DV explainability varies massively across the cluster.
    - **Lagged_DV heterogeneity** (DV persistence): H1/H4a/H4b/H12b/H17 have positive persistence across all FE strata; H12 PayoutRatio_q firm-FE near-zero (0.07); H13 Capex firm-FE lead near-zero (0.09); H16 RDSales firm-FE lead near-zero (0.05); **H19b/H20b have NEGATIVE persistence under firm FE** (mean reversion; first occurrence in audit). The negative-persistence DV class is documented in §5.10.
- **Implication for synthesis**: All 10 Q1 suites now have full-row records. Cross-suite comparisons of controls (e.g., "where does TobinsQ Q-theory anomaly hit?") can be made directly from §4.2 without re-opening tables. Synthesis can use the §4.2 catalogue as the canonical empirical record.
- **Loaded from**: Q1→Q2 boundary 2026-04-15. Incident report: `log/incidents/2026-04-15_q1-controls-uncatalogued.md`. Re-catalogue commits: batch 1 `ad9def1`, batch 2 (this commit).

---

## Appendix A. Carry-over pipeline bug list (code fixes already applied, historical reference)

Recorded in git commits c46e655 → bf9f366 (2026-04-14 architectural rewrite + LaTeX audit fixes). Detailed record in `memory/project_draft_playing_it_safe.md` and `memory/project_completed_milestones.md`. Not reproduced here — the audit proceeds assuming these are stable.
