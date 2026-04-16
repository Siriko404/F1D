# Thesis Draft — Decisions Log

**Current phase:** Phase 5 audit — philosophy-framed, dialogue-based. Hard reset 2026-04-14. Audit design finalized. **37 / 37 SUITES AUDITED — Q1 + Q2 + Q3 + Q4 COMPLETE — full audit cataloguing finished 2026-04-16.** Q1 (10): 8 KEEP + H16 DROP-flagged + H20b DROP. Q2 (6): all KEEP (H22 sample-size flag). Q3 (14): all KEEP — 11 clean KEEP + H7/H14/H14d KEEP near-null flags. **Q4 (7) — FINAL cluster: all KEEP** — H11 / H11-Lag1 / H11-Lag2 / H24b 8/8 sig β>0 (broadest loading) + H24 6/8 + H23 4/8 ind-heavy + H25 1/8 near-null. Rules 21-24 in force. **Q4 notable findings**: H11-series tiny-magnitude flag (β=0.0001-0.0003, negative firm-FE Adj R², no Lagged_DV); H24b 8/8 (inverts pre-restructure wrong-sign); H24 vs H24b Mgr-Pre DV heterogeneity (US EPU null, GEPU sig); H23 UncPreCEO firm-FE survival = fourth UncPreCEO sig instance (§5.24); H25 GPR near-null = fifth near-null suite (§5.27). §5.23-5.27 added. **Total audit DROPs**: 2 (H16 Q1 DROP-flagged-for-revisit + H20b Q1 DROP) out of 37. **Next phase: Q5 economic-magnitude sweep + post-audit synthesis**.

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
| H1.1 | CashRatio (4 cols, contemp only) | 73,707 (Mgr-only + TSIMM; +8.6K vs H1 because no 4-IV CEO bottleneck) | Q2 (provisional) | `UncAnsMgr_c` **4/4 sig β>0** (re-confirms H1 on broader sample); `z_log_TotalSimilarity` 4/4 sig β>0; **`UncAnsMgr_c × zlogTSIMM` 0/4 null** — TSIMM continuous interaction does not moderate | KEEP | Main IV re-confirms H1; continuous TSIMM interaction null across all 4 FE ladders — first negative interaction result in Q2 |
| H1.1b | CashRatio (4 cols) | 73,707 (same as H1.1) | Q2 (provisional) | `UncAnsMgr_c` **4/4 sig β>0**; `HighTSIMM` 2/4 sig β>0 ind contemp; **`UncAnsMgr_c × HighTSIMM` 0/4 null** | KEEP | Redundant null with H1.1 — binary version also fails to find interaction; the null is robust to functional form |
| H1.2 | CashRatio (4 cols) | 67,544 (Mgr-only + rating coverage) | Q2 (provisional) | `UncAnsMgr_c` **4/4 sig β>0**; `BelowIG × UncAnsMgr_c` 0/4 null; `IG × UncAnsMgr_c` 0/4 null; **`Unrated × UncAnsMgr_c` 4/4 sig β>0** — first sig interaction in H1 family. `lnAssets` col 1 ind sign flip anomaly | KEEP | Only sig interaction in H1 moderation family. Unrated-firm subgroup shows 4/4 interaction sig β>0 across all FE ladders; rated-but-below-IG null |
| H13.1 | Capex (cols 1-4); Capex_lead (cols 5-8) | 73,673 contemp / 69,580 lead | Q2 (provisional) | `UncAnsMgr_c` 4/8 sig β>0 ind-only (firm 0/4 null); `z_log_TotalSimilarity` 6/8 sig β>0; **`UncAnsMgr_c × zlogTSIMM` 8/8 sig β>0 including all 4 firm-FE cells** — highest interaction sig rate in audit | KEEP | 8/8 interaction sig including firm-FE survival. First moderation pattern with within-firm identification. Strongest channel evidence in Q1+Q2 audit so far |
| H13.2 | Capex_lead / _lead2 / _lead3 / _lead4 (16 cols: 4 horizons × 4 FE) | 58,897 (h1) → 41,091 (h4), shrinks with horizon | Q2 (provisional, **cluster-fit flag: re-cluster to Q1?**) | **TWO-TAILED**. UncAnsCEO 0/16 null; UncPreCEO 0/16 null; `UncAnsMgr` **10/16 sig β>0** across all 4 lead horizons (mostly industry-FE); UncPreMgr 1/16 sig β<0. **Capex firm-FE Lagged_DV turns NEGATIVE at h2-h4 (+0.087 at h1 → −0.06 to −0.08 at h2-h4)** — new DV-class observation | KEEP (flag re-cluster) | Sustained cross-sectional UncAnsMgr effect on capex out to 4 quarters; firm-FE null beyond contemp. Structurally a Q1-extended suite, not a moderation test — re-cluster question deferred to synthesis |
| H22 | EquityDelayCon_lead (4 cols, firm-year) | 8,564–8,621 (firm-year, small-sample class alongside H20b DROP precedent) | Q2 (provisional; edge: Q1 vs Q2 per §3) | `UncAnsCEO` **2/4 sig β>0** — cols 1, 3 industry-FE only (firm-FE 0/2 null); `UncPreCEO` 0/4 null; `UncAnsMgr` 0/4 null; `UncPreMgr` 0/4 null. Lagged_DV ≈ 0.66 ind / 0.18 firm. Very high ind-FE R² (0.49) but near-zero firm-FE R² (0.04) | KEEP (sample-size watch flag) | Rule 21 KEEP default for informative pattern (UncAnsCEO 2/4 sig industry-FE β>0). Firm-year ~8.6K places H22 in H20b small-sample class — user DROP override available if generalizability ruled out at synthesis. Cluster edge-case Q1 vs Q2 deferred. New §5.17 |
| H5 | DISP (cols 1-6); DISP_lead (cols 7-12) | 18,406–20,069 (IBES Detail coverage ~1/3 of Q1 Main cash panel) | Q3 (provisional; edge: Q1 vs Q3 per §3) | `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` **6/12 sig β>0 — all 6 industry-FE cells both DVs** (cross-sectional only, firm-FE 0/6); `UncPreMgr` **12/12 sig β>0 — every cell incl firm-FE (first full-ladder UncPreMgr survival in audit)**. Lagged_DV ≈ 0.63 ind / 0.38 firm contemp; 0.58 / 0.31 lead | KEEP | Two Mgr channels: UncAnsMgr cross-sectional-only (matches §5.5 pattern); **UncPreMgr 12/12 including firm-FE — strongest UncPreMgr in audit, further breaks §5.5 after H17**. Analyst market listens to scripted-presentation language at least as strongly as Q&A. Edge-case Q1 vs Q3 held. New §5.14 |
| H7 | DeltaILLIQ (cols 1-6); DeltaILLIQ_lead1 (cols 7-12) | 60,182–63,736 | Q3 (provisional) | `UncAnsCEO` 0/12 null; `UncPreCEO` **1/12 sig β>0** (col 2 firm+yr contemp only); `UncAnsMgr` 0/12 null; `UncPreMgr` 0/12 null. **1/48 sig — near-complete null**. Lagged_DV 0/12 null (change variable mean-reverts). **R² 0.001–0.005** (near-zero explanatory power) | KEEP (near-null flag) | Rule 21 KEEP default (1 sig cell technically informative). Near-null at R²≈0.003 parallels H16 R&D 0/48. User-override to DROP-flag available if "change-variable illiquidity uninformative" becomes the synthesis read. Level-vs-change contrast with H7b/H7c in §5.16 |
| H7b | PostCallAmihud (cols 1-6); PostCallAmihud_lead1 (cols 7-12) | 60,182–63,736 (same panel as H7) | Q3 (provisional) | `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead), industry-FE + ExtCtrl only. Lagged_DV 0.71/0.61 ind / 0.60/0.39 firm — high persistence (level variable, opposite of H7 change variable) | KEEP | Level-variant of H7 on same panel. Primary IV null; UncPreMgr 2/12 sig industry-FE + ExtCtrl only (cross-sectional-only matching §5.5). Level-vs-change structural contrast with H7 logged §5.16 |
| H7c | BGTLevel_Amihud (cols 1-6); BGTLevel_Amihud_lead1 (cols 7-12) | 60,256–63,806 | Q3 (provisional) | `UncAnsCEO` **6/12 sig β>0 — ALL 6 contemp cells across all FE ladders incl 3 firm-FE** (cols 2, 4, 6); lead 0/6 null. `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` 1/12 sig β>0 (col 9 lead ind+yr+ext only). **First 6/6 UncAnsCEO contemp-all-FE in audit** — breadth + firm-FE depth. Lagged_DV 0.78/0.67 | KEEP (measurement-concerns flag: CEO inverts primary hierarchy) | Rule 21 informative pattern. Deepest CEO-channel signal in audit — echoes §5.1 H1 CEO-lead inversion but goes DEEPER (contemp + firm-FE survival, 3 firm cells). Per feedback_ceo_noisy_mgr_central flagged as measurement concerns, not rescued. New §5.15 |
| H7d | BGTDelta_Amihud (cols 1-6); BGTDelta_Amihud_lead1 (cols 7-12) — 25-day change window [+1,+25]-[-25,-1] | 60,036–63,537 | Q3 (provisional) | `UncAnsCEO` 0/12 null; `UncPreCEO` **4/12 sig β>0 — cols 7, 9, 11, 12 (lead-horizon only: 3 ind + 1 firm col 12)**; `UncAnsMgr` **1/12 sig β>0** (col 1 ind+yr contemp only); `UncPreMgr` 0/12 null. **5/48 sig**. Lagged_DV 12/12 sig ~0.15–0.18 (moderate persistence, weaker than H7c/H7e levels). R² 0.022–0.039 (between H7 0.003 and H7b/H7c 0.45+) | KEEP | Rule 21 informative pattern. 25-day change variant carries modestly more signal than 3-day change (H7 1/48) but far less than 25-day level (H7c 6/6 contemp CEO). UncPreCEO lead-horizon cluster is distinctive. §5.16 level-vs-change nuance: mid-horizon change carries some signal, short-horizon change doesn't |
| H7e | BGTAvg_Amihud (cols 1-6); BGTAvg_Amihud_lead1 (cols 7-12) — 51-day symmetric average [-25,+25] | 60,256–63,816 | Q3 (provisional) | `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead), industry-FE + ExtCtrl only (same pattern as H7b). Lagged_DV 12/12 sig **~0.80 ind / 0.70 firm** (highest persistence so far); R² **0.64–0.65 / 0.48–0.50 — highest firm-FE R² in audit** | KEEP | Rule 21 informative pattern (2 sig UncPreMgr cells matching §5.5 / H7b). **H7e does NOT replicate H7c's 6/6 contemp UncAnsCEO pattern** — the symmetric 51-day average (including pre-call) loses the signal that the post-call-only 25-day window carries. Suggests H7c's CEO signal is specific to the [0,+25] post-call-only window. §5.15 scope observation flagged |
| H14 | DSPREAD change (cols 1-6); DSPREAD_lead1 (cols 7-12) — Lee (2016) 3-day spread change [+1,+3]-[-3,-1] | 44,132–63,972 (N drops ~30% with extended controls) | Q3 (provisional) | `UncAnsCEO` 0/12 null; `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` **1/12 sig β>0** (col 6 firm+yq+ext contemp only). **1/48 sig — near-complete null**. Lagged_DV 5/12 mixed (small-magnitude firm β<0, col 9 β>0). **R² 0.001–0.009** (near-zero explanatory power). DSPREAD rescaled ×10⁴ per notes block | KEEP (near-null flag) | Rule 21 KEEP default (1 sig cell). **§5.16 hypothesis CONFIRMED on bid-ask spread side**: H14 change variant mirrors H7 DeltaILLIQ near-null almost exactly (1/48 vs 1/48, R² 0.001–0.009 vs 0.001–0.005). Near-null twin of H7; user-override to DROP available |
| H14b | PostCallSpread (cols 1-6); PostCallSpread_lead1 (cols 7-12) — Lee (2016) 3-day level [+1,+3] | 60,368–63,972 | Q3 (provisional) | `UncAnsCEO` **3/12 sig β>0 — cols 8, 10, 12 firm-FE lead cells only** (contemp 0/6 null, ind-lead 0/3 null); `UncPreCEO` 0/12 null; `UncAnsMgr` **2/12 sig β>0** — cols 3, 9 (ind+yr+ext contemp + lead only); `UncPreMgr` **3/12 sig β>0** — col 2 (firm+yr contemp) + col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead). **8/48 sig**. Lagged_DV 12/12 ~0.61 ind / 0.43 firm. R² 0.53–0.56 / 0.29–0.33. PostCallSpread rescaled ×10⁴ | KEEP (CEO firm-FE lead flag) | Level variant of H14 on same panel. **Novel UncAnsCEO pattern**: 3/3 firm-FE lead cells (cols 8, 10, 12) — distinct from §5.1 H1 (lead ind), §5.7 H13 (contemp firm), §5.15 H7c (contemp all FE). Fourth CEO-inversion instance on liquidity. §5.16 level-vs-change holds. New §5.18 |
| H14c | BGTLevel_Spread (cols 1-6); BGTLevel_Spread_lead1 (cols 7-12) — BGT 25-day level [0,+25] | 44,092–63,899 (N drops ~30% with extended controls) | Q3 (provisional) | `UncAnsCEO` **5/12 sig β>0 — cols 7, 8, 9, 10, 12 ALL lead-horizon cells** (2 ind cols 7, 9 + 3 firm cols 8, 10, 12); contemp 0/6 null. `UncPreCEO` **3/12 sig β>0 — cols 1, 2, 4 contemp only** (ind+yr + firm+yr + firm+yr+ext) — **first UncPreCEO sig pattern in audit**. `UncAnsMgr` **2/12 sig β>0** — cols 3, 9. `UncPreMgr` **4/12 sig β>0** — cols 3, 9, 10, 12. **14/48 sig — richest liquidity suite in audit**. Lagged_DV ~0.75 ind / 0.65 firm; R² **0.72–0.78 / 0.56–0.59 — highest R² in audit**. Rescaled ×10⁴ | KEEP (multiple flags) | Rule 21 informative pattern. **Two novel observations**: (a) UncAnsCEO loads 5/6 on LEAD horizon (OPPOSITE to H7c's 6/6 contemp) — same BGT 25-day window, different market DV, opposite horizon loading; (b) **first UncPreCEO sig pattern in audit** — 3/3 contemp cells β>0. New §5.18 (joint with H14b) |
| H14d | BGTDelta_Spread (cols 1-6); BGTDelta_Spread_lead1 (cols 7-12) — BGT 25-day spread delta [+1,+25]-[-25,-1] | 43,282–62,480 (~30% ext drop) | Q3 (provisional) | `UncAnsCEO` **1/12 sig β>0** (col 8 firm+yr lead only); `UncPreCEO` 0/12 null; `UncAnsMgr` 0/12 null; `UncPreMgr` 0/12 null. **1/48 near-null**. Lagged_DV 3/12 sig firm-FE small β<0 (mean reversion). R² **0.002–0.012** (near-zero). Rescaled ×10⁴ | KEEP (near-null flag) | Rule 21 KEEP default (1 sig cell). **Contrast with H7d** (BGTDelta_Amihud 5/48 sig): same 25-day change window on Amihud carries modest signal, on spreads does not. Window × DV asymmetry. New §5.20 |
| H14e | BGTAvg_Spread (cols 1-6); BGTAvg_Spread_lead1 (cols 7-12) — BGT 51-day symmetric spread [-25,+25] | 44,100–63,936 (~30% ext drop) | Q3 (provisional) | `UncAnsCEO` **2/12 sig β>0** — cols 7 (ind+yr lead), 8 (firm+yr lead); `UncPreCEO` **3/12 sig β>0 — cols 1, 2, 4 contemp only** (same pattern as H14c — **second UncPreCEO sig contemp suite**); `UncAnsMgr` **1/12 sig β>0** (col 9 ind+yr+ext lead only); `UncPreMgr` **3/12 sig β>0** — cols 3, 9, 12. **9/48 sig**. Lagged_DV 12/12 sig **~0.85 ind / 0.73 firm** — highest persistence in audit; R² **0.60–0.83 (ind reaches 0.83 — highest R² in audit)**. Rescaled ×10⁴ | KEEP | Rule 21 informative pattern. **Contrast with H7e**: H7e (51-day Amihud avg) has 2/48 only UncPreMgr; H14e 9/48 incl UncPreCEO 3/3 contemp — **51-day symmetric window LOSES H7c Amihud signal completely but PARTIALLY PRESERVES H14c spread signal**. Cross-DV asymmetry. §5.20 + §5.21 |
| H18 | CCCL (6 cols, LPM, 1 DV) | 64,172–66,886 | Q3 (provisional) | `UncAnsCEO` 0/6 null; `UncPreCEO` 0/6 null; `UncAnsMgr` 0/6 null; `UncPreMgr` **2/6 sig β>0** — cols 1, 2 (ind+yr + firm+yr, no extended controls); cols 3-6 with ext null. **2/24 sig**. Lagged_DV 3/6 sig firm-FE β<0 (mean reversion, binary DV). **R² 0.000–0.001 near-zero** (binary CCCL DV, LPM struggles) | KEEP | Rule 21 informative pattern (2 sig cells, robust to LPM/Logit per H18b). Primary `UncAnsMgr` null. Only UncPreMgr signal, extended-control sensitive. New §5.22 |
| H18b | CCCL Logit (2 cols, ind+yr only — firm FE not supported) | 64,172–66,886 | Q3 (provisional) | `UncAnsCEO` 0/2 null; `UncPreCEO` 0/2 null; `UncAnsMgr` 0/2 null; `UncPreMgr` **2/2 sig β>0** — col 1 (ind+yr) + col 2 (ind+yr+ext). Pseudo R² 0.089 / 0.090. Logit variant of H18 without firm FE | KEEP | Logit robustness check for H18. UncPreMgr ind-only pattern **robust to functional form**: LPM 2/6 (no-ext cells) + Logit 2/2 (both cols). CEO measures null in both. §5.22 |
| H21 | SEC_Letters_fwd (6 cols, 1 DV) | 64,172–66,886 | Q3 (provisional) | `UncAnsCEO` 0/6 null; `UncPreCEO` **3/6 sig β>0 — cols 1, 3, 5 industry-FE only** (firm-FE 0/3 null); `UncAnsMgr` 0/6 null; `UncPreMgr` 0/6 null. **3/24 sig**. **Third UncPreCEO sig suite** (H14c → H14e → H21). Lagged_DV 3/6 sig firm-FE β<0 (mean reversion). R² 0.004–0.005 near-zero | KEEP | Rule 21 informative pattern. UncPreCEO 3/3 industry-FE contemp. **Third UncPreCEO sig instance in audit** — all three on information-channel DVs (H14c/H14e spread levels + H21 SEC letter count). §5.21 UncPreCEO recurring pattern |
| H11 | 4 speech DVs (UncAnsMgr / UncAnsCEO / UncPreMgr / UncPreCEO) × ind+Yr / firm+Yr FE (8 cols) — **REVERSE direction: speech is LHS** | 65,394–77,758 | Q4 (provisional) | `PRisk_t` **8/8 sig β>0** across all 4 DVs × both FE strata (β=0.0001–0.0003). **No Lagged_DV control in spec** (shared with H23; only H24/H24b/H25 macro-monthly include it — §5.25). Firm-FE Adj R² **NEGATIVE** (-0.002 to -0.006) — within-firm fit near-zero. Controls: UncQue 8/8 sig, NegCall 8/8 sig, lnAssets 4/8 sig β<0 ind-only (FE-strata split), TobinsQ 2/8 sig β<0 cols 1-2 (UncAns DVs ind-only), **ROA 5/8 sig β>0** (cols 1-3 ind + 5-6 firm; cols 4, 7, 8 null), CashRatio 3/8 mixed (col 3 ind β>0 UncPreMgr + cols 5, 6 firm β>0 UncAns), DivDummy 3/8 sig (col 3 ind β<0 UncPreMgr + cols 7, 8 firm β<0 UncPre), FirmMat 4/8 sig (cols 3, 4 ind + 5, 6 firm), EarnVol 0/8 null. UncPreMgr as control on UncAnsMgr DV cols: 2/2 sig β>0 (cols 1, 5). UncPreCEO as control on UncAnsCEO DV cols: 2/2 sig β>0 (cols 2, 6) | KEEP (tiny-magnitude flag) | Rule 21 KEEP default for full-ladder informative pattern. Primary IV loads on every speech DV under both FE strata — broadest informative pattern in the Q4 cluster so far. Tiny β + negative firm-FE Adj R² logged as §5.23 flag; magnitude is a Q5 downstream concern not an audit-verdict input |
| H11-Lag1 | Same 4 speech DVs × 8 cols | 63,049–75,014 | Q4 (provisional) | `PRisk_{t-1}` **8/8 sig β>0** — identical pattern to H11 contemp. Firm-FE magnitudes marginally smaller (round to β=0.0000 but three-star sig). No Lagged_DV. Controls near-identical to H11 | KEEP | Lag-1 replication of H11 contemp. Same 8/8 survival, same tiny magnitudes, same structural caveats (no Lagged_DV + negative Adj R² under firm FE). §5.23 applies |
| H11-Lag2 | Same 4 speech DVs × 8 cols | 62,674–74,561 | Q4 (provisional) | `PRisk_{t-2}` **8/8 sig β>0**, col 6 (firm-FE UncAnsCEO) drops to ** from ***; all other 7 cells still ***. No Lagged_DV. Controls near-identical to H11/H11-Lag1 | KEEP | Lag-2 replication of H11 — slight attenuation at one cell, same 8/8 breadth otherwise. Logged as factual observation, not interpreted. §5.23 applies |
| H23 | 4 speech DVs × ind+Yr / firm+Yr FE (8 cols, **firm-fiscal-year panel**) | 18,447–20,774 | Q4 (provisional) | `z(log(TSIMM))` **4/8 sig β>0** — ind col 1 UncAnsMgr β=0.0090** / col 3 UncPreMgr β=0.0297*** / col 4 UncPreCEO β=0.0304***; firm col 8 UncPreCEO β=0.0302***. **UncPreCEO is the only DV with firm-FE survival** — **fourth UncPreCEO sig suite** in audit (after H14c/H14e/H21 in Q3; §5.24). UncAnsCEO 0/2 null on ind and firm. **No Lagged_DV in spec** (shared with H11-series — §5.25 firm-level construct IVs). Firm-year panel ≈20K parallels H22 class. Controls: UncQue 7/8 sig (col 8 null), NegCall 8/8 sig, lnAssets 4/8 ind-only β<0, TobinsQ 2/8 ind-only β<0 (cols 1, 2), **ROA 6/8 sig β>0** (cols 1-4 ind + 5, 6 firm; cols 7, 8 firm null), CashRatio 3/8 mixed (col 4 ind β<0 UncPreCEO + cols 5, 6 firm β>0 UncAns), DivDummy 2/8 sig β<0 (col 3 ind + col 7 firm UncPreMgr), FirmMat 5/8 sig β>0 (cols 1, 2, 4 ind + 5, 6 firm), EarnVol 0/8 null. UncPreMgr control 2/2 sig β>0 (cols 1, 5); UncPreCEO control 2/2 sig β>0 (cols 2, 6) | KEEP (small-panel flag) | Rule 21 informative pattern. Ind-FE pattern delivers; firm-FE collapses except via UncPreCEO. Fourth UncPreCEO sig instance extends §5.21 beyond Q3 information DVs (§5.24). Small firm-year panel logged alongside H22/H20b — sample-size generalizability watch |
| H24 | 4 speech DVs × ind+Cal.Yr / firm+Cal.Yr FE (8 cols). **DV column order Mgr-QA / Mgr-Pre / CEO-QA / CEO-Pre** (different from H11/H23; line 2237) | 59,676–75,142 | Q4 (provisional) | `log(US EPU)_t` **6/8 sig β>0** — hits Mgr-QA 2/2, CEO-QA 2/2, CEO-Pre 2/2; **Mgr-Pre 0/2 null** (cols 2 + 6 — only DV not responding to US EPU). β=0.0117–0.0239. Lagged_DV 8/8 sig — highest persistence on Mgr-Pre ind 0.68 / firm 0.42, lowest on CEO-QA firm 0.11. Two-way cluster (firm, cal_yr_qtr). Cal.Year FE via other_effects. R² 0.17 / 0.48 / 0.14 / 0.29 ind; 0.04 / 0.19 / 0.03 / 0.08 firm. Controls: UncQue 8/8 sig, NegCall 8/8 sig, lnAssets 4/8 ind-only β<0, TobinsQ 2/8 ind-only β<0 (UncAns DVs), ROA 7/8 sig β>0, CashRatio 3/8 sig β>0, DivDummy 3/8 sig β<0, FirmMat 3/8 sig, EarnVol 0/8 null | KEEP | Rule 21 informative pattern. Mgr-Pre null is a DV-specific non-response to US EPU — logged as §5.26 Q4 DV-heterogeneity flag alongside H24b contrast (H24b hits Mgr-Pre 2/2). §5.23 broad external-loading instance |
| H24b | Same 8-col structure as H24 (same panel, `other_effects=cal_yr`) | 59,676–75,142 | Q4 (provisional) | `log(GEPU)_t` **8/8 sig β>0** — all 4 DVs × both FE strata. β=0.0124–0.0309. **Inverts the pre-restructure wrong-sign GEPU finding** per `project_h24_h24b_h25_macro_uncertainty.md` (prior spec without Cal.Year FE produced uniformly NEGATIVE GEPU coefficients — year-level confounders absorbed here). Broadest Q4 signal. Lagged_DV 8/8 sig near-identical to H24. Controls near-identical to H24 | KEEP | Rule 21 broadest informative pattern in Q4 (ties H11-series 8/8 breadth). Direction restored to β>0 after Cal.Year FE / other_effects spec fix. §5.23 broad external-loading; §5.26 DV-heterogeneity contrast — H24 vs H24b differ only on Mgr-Pre response (H24 null, H24b sig) |
| H25 | Same 8-col structure | 59,676–75,142 | Q4 (provisional) | `log(GPR)_t` **1/8 sig** — col 4 UncPreCEO ind+Cal.Yr β=0.0147*; all other 7 cells null. Lagged_DV 8/8 sig. Controls near-identical to H24/H24b | KEEP (near-null flag) | Rule 21 KEEP default (1 sig cell informative). Near-complete null joins H7/H14/H14d/H16 near-null family (§5.27, fifth instance). GPR does not meaningfully drive speech uncertainty after Cal.Year FE absorbs year-level confounders. User DROP override available at synthesis |

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

### H1.1 — Product Similarity-Moderated Cash Holdings

- **DV**: `CashRatio` (cols 1-4, contemp only)
- **N**: 73,707 (all 4 cols; Main sample; larger than H1's 65,128 because H1.1 requires only `UncAnsMgr` non-null, not all 4 IVs — see §5.13 CEO coverage explanation)
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+YQ, (4) Firm+YQ
- **Tail**: one-tailed β>0 main IV; two-tailed moderator and interaction
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsMgr_c` **4/4 sig β>0** (all cells incl firm-FE — re-confirms H1 main effect on broader Mgr-only sample). `z_log_TotalSimilarity` 4/4 sig β>0. **`UncAnsMgr_c × zlogTSIMM` 0/4 null** — interaction does not moderate at any FE ladder.
    - **Base controls**: `Leverage` 4/4 sig β<0; `lnAssets` 4/4 sig β<0; `TobinsQ` 4/4 sig β>0; `ROA` 4/4 sig β<0; `Capex` 4/4 sig β<0; `DivDummy` 2/4 sig β<0 (cols 1, 3 ind-only, FE-strata split); `sCFO` 2/4 sig β>0 (cols 1, 3 ind-only, FE-strata split).
    - **Extended controls**: `SalesGrowth` 4/4 sig β<0; `RDSales` 2/4 sig β>0 ind + 1 marginal firm; `CashFlowAt` 4/4 sig β>0; `DailyVola` 2/4 — **FE sign flip**: col 2 firm sig β<0, col 3 ind sig β>0.
    - **Lagged_DV** (rule 23 structural): 0.857 / 0.858 (ind); 0.665 / 0.666 (firm). Matches H1 structural persistence.
    - **R² / N**: 0.834 / 0.484 → 0.835 / 0.484. N = 73,707 (all 4 cols).
- **Reader-question**: Q2 (provisional, placeholder per rule 21).
- **Argument**: Main IV `UncAnsMgr_c` re-confirms H1 cash-uncertainty direction on the broader Mgr-only sample at higher N (+8.6K vs H1). Continuous `z_log_TotalSimilarity` moderator is sig β>0 as a standalone level effect. Interaction term is null 0/4 across all FE ladders — no evidence of TSIMM-moderated amplification. Under rule 21 the pattern is informative (main sig + interaction null is a valid empirical fact, not "all-null"). Per rule 18 no interpretive label is committed here; whether this is "failed channel" or "honest pre-registered null" is a synthesis decision.
- **Verdict**: **KEEP — main IV re-confirms H1, interaction null**.
- **Rationale**: Rule 21 KEEP default. Informative facts: (a) H1 main effect replicates on broader Mgr-only sample, (b) TSIMM continuous interaction is clean null — first negative interaction result in Q2.

### H1.1b — Binary Product Similarity-Moderated Cash Holdings

- **DV**: `CashRatio` (cols 1-4, contemp only)
- **N**: 73,707 (identical to H1.1 — same Mgr-only + TSIMM base, binary recode of moderator does not change sample)
- **FE ladder**: identical to H1.1
- **Tail**: one-tailed β>0 main IV; two-tailed moderator and interaction
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsMgr_c` **4/4 sig β>0**. `HighTSIMM` 2/4 sig β>0 (cols 1, 3 ind contemp only; firm 0/2 null). **`UncAnsMgr_c × HighTSIMM` 0/4 null**.
    - **Base controls**: `Leverage` 4/4 sig β<0; `lnAssets` 4/4 sig β<0; `TobinsQ` 4/4 sig β>0; `ROA` 4/4 sig β<0; `Capex` 4/4 sig β<0; `DivDummy` 2/4 sig β<0 (ind-only); `sCFO` 2/4 sig β>0 (ind-only).
    - **Extended controls**: `SalesGrowth` 4/4 sig β<0; `RDSales` 2/4 sig β>0 ind + 1 marginal firm; `CashFlowAt` 4/4 sig β>0; `DailyVola` 2/4 FE sign flip (col 2 firm β<0, col 3 ind β>0).
    - **Lagged_DV**: 0.862 / 0.863 (ind); 0.665 / 0.666 (firm).
    - **R² / N**: 0.833 / 0.484 → 0.834 / 0.484. N = 73,707.
- **Reader-question**: Q2 (provisional, placeholder).
- **Argument**: Binary-TSIMM version of H1.1. Main IV re-confirms H1; interaction null across all 4 cells. The binary functional form does not recover moderation that the continuous form also failed to find — the null is robust to functional form choice.
- **Verdict**: **KEEP — redundant null with H1.1**.
- **Rationale**: Rule 21 KEEP default. At synthesis, H1.1 + H1.1b likely collapse into a single "TSIMM does not moderate H1" observation regardless of continuous vs binary.

### H1.2 — Financial Constraint-Moderated Cash Holdings (Three-Category)

- **DV**: `CashRatio` (cols 1-4, contemp only)
- **N**: 67,544 (Mgr-only + rating coverage; rating filter loses ~6.2K vs H1.1's 73.7K)
- **FE ladder**: identical to H1.1/H1.1b
- **Tail**: one-tailed β>0 main IV; two-tailed moderators and interactions
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsMgr_c` **4/4 sig β>0**. `BelowIG` 1/4 sig β>0 (col 1 only). `Unrated` 1/4 sig β>0 (col 1 only). `UncAnsMgr_c × IG` 0/4 null. `UncAnsMgr_c × BelowIG` 0/4 null. **`UncAnsMgr_c × Unrated` 4/4 sig β>0** (first sig interaction in the H1 family).
    - **Base controls**: `Leverage` 4/4 sig β<0; `lnAssets` 4/4 sig — **FE × col sign flip**: col 1 ind sig β>0 (+0.0005**), cols 3, 5 ind sig β<0, firm cells all sig β<0. Anomaly flag; `TobinsQ` 4/4 sig β>0; `ROA` 4/4 sig β<0; `Capex` 4/4 sig β<0; `DivDummy` 3/4 sig β<0 (col 4 null); `sCFO` 2/4 sig β>0 (ind-only).
    - **Extended controls**: `SalesGrowth` 4/4 sig β<0; `RDSales` 4/4 sig β>0 (different from H1.1 where firm-FE was null); `CashFlowAt` 4/4 sig β>0; `DailyVola` FE-mixed.
    - **Lagged_DV**: 0.864 / 0.867 (ind); 0.656 / 0.657 (firm).
    - **R² / N**: 0.831 / 0.469 → 0.832 / 0.469. N = 67,544.
- **Reader-question**: Q2 (provisional, placeholder).
- **Argument**: 3-category rating indicator (IG reference / BelowIG / Unrated) interacted with main IV. Main IV sig as in H1 family. Of the 3 interaction terms: IG-interaction 0/4 null, BelowIG-interaction 0/4 null, **Unrated-interaction 4/4 sig β>0**. Per rule 18 no interpretive label is committed here; the Unrated-interaction 4/4 pattern is the empirical fact — whether it maps to a "constraint channel" narrative is a synthesis decision.
- **Verdict**: **KEEP — only sig interaction in H1 family**.
- **Rationale**: Unrated × UncAnsMgr_c interaction is 4/4 sig β>0 across all FE ladders including firm-FE. First positive interaction result in Q2 cluster. The BelowIG null is also informative (rated-but-below-IG shows no amplification, only unrated firms do).

### H13.1 — Product Similarity-Moderated Capital Expenditure

- **DV**: `Capex` (cols 1-4 contemp); `Capex_lead` (cols 5-8)
- **N**: 73,673 contemp / 69,580 lead (Mgr-only + TSIMM coverage on H13 panel)
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+YQ, (4) Firm+YQ × 2 DVs
- **Tail**: one-tailed β>0 main IV; two-tailed moderator and interaction (parent H13 is two-tailed but H13.1 child is one-tailed per `feedback_moderation_tails.md`)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsMgr_c` 4/8 sig β>0 — cols 1, 3, 5, 7 (all industry-FE; firm-FE 0/4 null). `z_log_TotalSimilarity` 6/8 sig β>0 (mostly). **`UncAnsMgr_c × zlogTSIMM` 8/8 sig β>0 — every cell including all 4 firm-FE cells.** Highest interaction sig rate in Q1+Q2 audit so far.
    - **Base controls**: `lnAssets` 8/8 sig β<0 (mostly); `TobinsQ` 8/8 sig β>0; `ROA` 8/8 sig — **direction split**: cols 1-6 contemp β<0, cols 7-8 lead β>0 firm-FE, mixed under industry-FE; `Leverage` 6/8 sig (contemp all, lead firm-only); `CashRatio` 5/8 sig β<0; `DivDummy` 2/8 sig β<0 (lead only); `sCFO` 6/8 sig β<0.
    - **Extended controls**: `SalesGrowth` 8/8 sig β>0; `RDSales` 8/8 sig β>0; `CashFlowAt` 8/8 sig β>0; `DailyVola` 8/8 sig — **sign flip across horizon**: cols 1-4 contemp β>0 (mostly), cols 5-8 lead β<0.
    - **Lagged_DV**: 0.731 / 0.734 (ind contemp); 0.624 / 0.625 (ind lead); 0.333 / 0.335 (firm contemp); 0.094 / 0.097 (firm lead). Tracks H13 parent persistence.
    - **R² / N**: contemp 0.620 / 0.156 → 0.623 / 0.159; lead 0.494 / 0.071 → 0.497 / 0.070. N = 73,673 contemp / 69,580 lead.
- **Reader-question**: Q2 (provisional, placeholder).
- **Argument**: Capex × log TSIMM interaction is sig in all 8 cells including firm-FE. Main IV sig only under industry-FE (firm-FE null), consistent with H13 parent. Interaction survives firm-FE in all 4 firm cells — within-firm identification confirmed. Per rule 18 no mechanism label committed; the 8/8 interaction pattern is the empirical fact.
- **Verdict**: **KEEP — highest interaction sig rate in audit**.
- **Rationale**: 8/8 sig interaction including all 4 firm-FE cells. First moderation pattern with within-firm survival in the audit. Strong candidate for the Q2 narrative scope, subject to synthesis.

### H13.2 — Speech Uncertainty and Capital Expenditure — Lead Horizons

- **DV**: `Capex_lead`, `Capex_lead2`, `Capex_lead3`, `Capex_lead4` (16 cols: 4 horizons × 4 FE ladders each)
- **N**: 58,897 (h1) → 52,648 (h2) → 46,679 (h3) → 41,091 (h4). Sample shrinks with horizon due to fiscal-year consecutiveness requirement.
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+YQ, (4) Firm+YQ × 4 horizons
- **Tail**: **TWO-TAILED** (line 1289 notes block)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue — native 4-IV structure extended to 4 horizons, NOT centered-IV moderation):
    - **IVs**: `UncAnsCEO` 0/16 null. `UncPreCEO` 0/16 null. `UncAnsMgr` **10/16 sig β>0** — cols 1, 3, 5, 7, 9, 10, 11, 12, 13, 15 (mostly industry-FE across all 4 horizons; cols 10, 12 firm-FE at h2). Sustained positive sig across 4 lead horizons, predominantly cross-sectional. `UncPreMgr` 1/16 sig β<0 (col 3 lead1 only).
    - **Base controls** (compact cross-horizon summary):
        - `lnAssets`: mixed signs by horizon; firm-FE negative throughout
        - `TobinsQ`: 8/8 sig β>0 at h1, declining to 4/8 at h4 (weakens with horizon)
        - `ROA`: strong contemp β<0 at h1, direction/FE shifts at longer horizons
        - `Leverage`: **sign flip by horizon** — h1 lead null/negative, h2-h4 ind sig β>0 + firm sig β<0
        - `CashRatio`: mostly null across horizons (2/16 sig)
        - `DivDummy`: h1 cols 1, 3 sig β<0; h2-4 mostly null
        - `sCFO`: **sign flip across horizons** — h1 firm sig β<0; h2 contemp sig β>0; h3-h4 firm sig β>0. Major anomaly flag.
    - **Extended controls**: SalesGrowth 8/8 sig β>0 h1+h2, weakening h3-h4; RDSales sig β>0 h1-h3, declining h4; CashFlowAt 8/8 sig β>0 all horizons; DailyVola mixed sign by horizon.
    - **Lagged_DV** (rule 23 structural): 
        - h1: 0.640 / 0.625 (ind); **+0.087 / +0.088 (firm)**
        - h2: 0.563 / 0.565 (ind); **−0.035 / −0.034 (firm)**
        - h3: 0.521 / 0.518 (ind); **−0.077 / −0.078 (firm)**
        - h4: 0.497 / 0.494 (ind); **−0.064 / −0.063 (firm)**
        - **Capex turns mean-reverting under firm-FE at horizons 2-4** — new DV-class observation.
    - **R² / N**: h1 contemp 0.496 / 0.070 → 0.501 / 0.068; h4 0.361 / 0.016 → 0.366 / 0.016. N = 58,897 → 41,091 (collapsing with horizon).
- **Reader-question**: Q2 (provisional, placeholder). **Cluster-fit flag**: H13.2 is structurally a multi-horizon extension of H13 (same 4 IVs, same DV class) not a moderation test. Synthesis-time decision: stay in Q2 ("channel = temporal depth") or re-cluster to Q1-extended.
- **Argument**: UncAnsMgr positive cross-sectional effect on capex (seen in H13 parent) persists out to 4 lead quarters (10/16 sig). Firm-FE within-firm effect is null beyond contemp — the persistence is cross-sectional. Capex Lagged_DV turning negative under firm-FE at h2+ is a new DV-class observation (candidate for a new §5 entry at Q2 close).
- **Verdict**: **KEEP — persistent cross-sectional effect across 4 horizons; flag for Q1 re-cluster**.
- **Rationale**: Rule 21 KEEP default for informative pattern. UncAnsMgr 10/16 sig across 4 horizons is empirically informative. Cluster-reassignment question deferred to synthesis — the suite fits Q1-extended more naturally than Q2 moderation.

### H22 — Speech Uncertainty and Equity Financing Constraints (Hoberg-Maksimovic)

- **DV**: `EquityDelayCon_lead` (4 cols, lead only — firm-year panel)
- **N**: 8,564–8,621 (firm-year, small-sample class alongside H20b DROP precedent ~3-14K)
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl (no YQ variant — annual panel)
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **2/4 sig β>0** — cols 1, 3 (industry-FE only; firm-FE 0/2 null). `UncPreCEO` 0/4 null. `UncAnsMgr` 0/4 null. `UncPreMgr` 0/4 null. Primary IV null; secondary UncAnsCEO is the only sig pattern, industry-FE only.
    - **Base controls**: `lnAssets` — **sign flip across cols**: col 1 sig β>0 (ind+yr), col 3 sig β<0 (ind+yr+ext), cols 2, 4 firm null. Anomaly flag. `TobinsQ` 0/4 null. `ROA` 1/4 sig β<0 (col 1 only). `Leverage` 0/4 null. `Capex` 0/4 null. `CashRatio` **3/4 sig β>0** — cols 1, 2, 3 (col 4 firm+yr+ext null). `DivDummy` 0/4 null. `sCFO` 2/4 sig β<0 — cols 2, 4 firm-FE only (FE-strata split).
    - **Extended controls** (cols 3, 4): `SalesGrowth` 1/2 sig β>0 (col 3 ind only). `RDSales` 1/2 sig β>0 (col 3 ind only). `CashFlowAt` 0/2 null. `DailyVola` 1/2 sig β>0 (col 4 firm only).
    - **Lagged_DV** (rule 23 structural): 0.660 / 0.181 / 0.664 / 0.184. Moderate ind persistence; low firm persistence (~0.18). Lower firm-FE persistence than Q1 balance-sheet stocks.
    - **R² / N**: 0.491 / 0.041 / 0.491 / 0.043. **Very high ind-FE R² (~0.49) but near-zero firm-FE R² (~0.04)** — spec has almost no within-firm explanatory power. N = 8,621 (cols 1, 2) / 8,564 (cols 3, 4).
- **Reader-question**: Q2 (provisional, placeholder per rule 21). **Cluster edge-case still open**: Q2 (constraint channel) vs Q1 (direct outcome on financial-structure variable) per §3. Structurally H22 has 4 native IVs (not a moderation test), closer to Q1 shape; reclassification deferred to synthesis.
- **Argument**: Primary `UncAnsMgr` null. `UncAnsCEO` 2/4 sig β>0 industry-FE only is the only informative IV pattern. Firm-FE 0/4 across all IVs — within-firm null. Small firm-year sample (~8.6K, similar class to H20b DROP precedent). Firm-FE R² near zero (0.04) — spec has almost no within-firm explanatory power on equity-delay constraint. Per rule 21 informative pattern (UncAnsCEO 2/4) → KEEP default; sample-size concern flagged separately.
- **Verdict**: **KEEP (sample-size watch flag)**.
- **Rationale**: Rule 21 KEEP default for informative pattern. Sample size puts H22 in H20b's small-N firm-year class — user may choose DROP if the small panel makes the suite not generalizable to the broader call-level story. Cluster edge-case (Q1 vs Q2) deferred to synthesis. New §5.17 entry on small-N firm-year class.

### H5 — Speech Uncertainty and Analyst Forecast Dispersion (Wang 2020)

- **DV**: `DISP` (cols 1-6); `DISP_lead` (cols 7-12)
- **N**: 18,406–20,069 (IBES Detail coverage ≈ 1/3 of Q1 Main cash panel)
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl × 2 DVs
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` 0/12 null. `UncAnsMgr` **6/12 sig β>0** — all 6 industry-FE cells (cols 1, 3, 5, 7, 9, 11), firm-FE 0/6 both DVs. Cross-sectional only (matches §5.5). `UncPreMgr` **12/12 sig β>0** — every cell across both DVs and all FE ladders **including all 6 firm-FE cells**. **First full-ladder UncPreMgr survival in the audit.**
    - **Base controls**: `lnAssets` 0/12 null. `TobinsQ` 12/12 sig β<0 (consistent). `ROA` 12/12 sig β<0 (consistent). `Leverage` 12/12 sig β>0 (consistent). `Capex` **3/12 sig β<0 — cols 2, 4, 6 firm-FE contemp only** (firm-FE-only FE-strata split). `DivDummy` **6/12 sig β<0 — all 6 industry-FE cells, firm-FE 0/6** (FE-strata split). `sCFO` 11/12 sig β>0 (col 2 null; rest sig).
    - **Extended controls** (cols 3-6, 9-12): `SurpDec` 6/8 sig β<0 (mostly industry-FE). `Loss` 8/8 sig β>0 (consistent). `UncQue` 0/8 null. `NegCall` 8/8 sig β>0 (consistent).
    - **Lagged_DV** (rule 23 structural): contemp 0.648 / 0.388 / 0.628 / 0.372 / 0.631 / 0.376; lead 0.593 / 0.310 / 0.579 / 0.302 / 0.584 / 0.309. Moderate ind (~0.63/0.58); intermediate firm (~0.38/0.31). DISP is a moderately persistent dispersion measure.
    - **R² / N**: contemp 0.488 / 0.204 → 0.501 / 0.223 → 0.503 / 0.223; lead 0.431 / 0.158 → 0.452 / 0.179 → 0.458 / 0.180. Moderate ind R² (~0.49); moderate firm R² (~0.19–0.22). N = 20,069 → 19,124 → 19,355 → 18,406.
- **Reader-question**: Q3 (provisional, placeholder per rule 21). **Cluster edge-case still open**: Q3 (info content via analyst channel) vs Q1 (direct outcome on analyst disagreement) per §3. Analyst dispersion is structurally a market-side DV (analyst behavior in response to firm information), closer to Q3 shape. Defer to synthesis.
- **Argument**: Two Mgr-side channels deliver on analyst dispersion. `UncAnsMgr` 6/12 sig β>0 all industry-FE (cross-sectional only, matching §5.5 pattern). `UncPreMgr` **12/12 sig β>0** — every cell across both DVs and all FE ladders including all 6 firm-FE cells. This is the **strongest UncPreMgr pattern in the audit**, further breaking the §5.5 cross-sectional-only generalization after H17 first broke it on repurchases. CEO measures null on both.
- **Verdict**: **KEEP — strongest UncPreMgr in audit + cross-sectional UncAnsMgr signal**.
- **Rationale**: Rule 21 KEEP default. Two informative facts: (a) UncAnsMgr cross-sectional-only (industry-FE 6/6, firm-FE 0/6), (b) **UncPreMgr 12/12 sig across all FE ladders including firm-FE — first full-ladder UncPreMgr survival in audit**. The §5.5 generalization is now broken twice (H17 partial, H5 full). Per feedback_ceo_noisy_mgr_central, UncPreMgr is a secondary measure — do not build narrative here. New §5.14 entry.

### H7 — Speech Uncertainty and 3-Day Post-Call Illiquidity Change ($\Delta$Amihud)

- **DV**: `DeltaILLIQ` = Amihud[+1,+3] − Amihud[-3,-1] (cols 1-6); `DeltaILLIQ_lead1` (cols 7-12)
- **N**: 60,182–63,736
- **FE ladder**: identical to H5 (6 × 2 DVs)
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` **1/12 sig β>0** (col 2 firm+yr contemp only). `UncAnsMgr` 0/12 null. `UncPreMgr` 0/12 null. **1/48 sig — near-complete null.**
    - **Base controls**: `lnAssets` 12/12 sig β>0 (consistent). `TobinsQ` 12/12 sig β>0 (consistent). `ROA` 2/12 sig β>0 — cols 7, 8 lead only (weak). `Leverage` 2/12 sig β<0 — cols 2, 4 firm-FE contemp only. `Capex` 4/12 sig β>0 — cols 1, 5, 7, 11 (mixed FE). `DivDummy` 1/12 sig β<0 (col 9 only). `sCFO` 1/12 sig β<0 (col 8 only).
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` 5/8 sig β<0 — col 3 contemp + cols 9-12 lead. `StockPrice` 7/8 sig β<0 (col 3 null). `Turnover` 8/8 sig β>0 (consistent). `UncQue` 1/8 sig β<0 (col 3 only).
    - **Lagged_DV** (rule 23 structural): **0/12 null across all cells** — change variable mean-reverts completely. Values 0.022 / -0.012 / 0.028 / -0.009 / 0.026 / -0.009 / 0.012 / -0.022 / 0.017 / -0.018 / 0.016 / -0.018.
    - **R² / N**: contemp 0.004 / 0.001 → 0.005 / 0.001; lead 0.004 / 0.001 → 0.005 / 0.002. **R² 0.001–0.005 across all cells — model has near-zero explanatory power on DeltaILLIQ.** Adj R² often negative under firm-FE. N = 63,736 → 60,182 → 63,313 → 61,060.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: Primary IV `UncAnsMgr` null. Only 1 sig cell across 48 IV cells (UncPreCEO col 2 firm+yr contemp). R² near-zero (0.001–0.005) — DeltaILLIQ is a change variable dominated by sampling noise; spec has almost no within-firm explanatory power. Comparable in breadth to H16 R&D complete-null (0/48) — H7 is 1/48 sig.
- **Verdict**: **KEEP (near-null flag)**.
- **Rationale**: Rule 21 KEEP default (1 sig cell technically informative pattern). But near-complete-null + near-zero R² puts H7 in H16 R&D comparison class: functionally the spec is uninformative on change-variable illiquidity. User-override to DROP-flag available (parallel to H16 decision) if "change-variable illiquidity uninformative" becomes the synthesis read. Contrast with H7b/H7c (level variants, same panel) shows level structure carries the weak UncPreMgr / strong UncAnsCEO signals while change structure does not. New §5.16 entry.

### H7b — Speech Uncertainty and 3-Day Post-Call Amihud Illiquidity Level

- **DV**: `PostCallAmihud` = Amihud[+1,+3] level (cols 1-6); `PostCallAmihud_lead1` (cols 7-12)
- **N**: 60,182–63,736 (same panel as H7)
- **FE ladder**: identical to H5/H7
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` 0/12 null. `UncAnsMgr` 0/12 null. `UncPreMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead). Both industry-FE + extended controls only (cross-sectional-only matching §5.5).
    - **Base controls**: `lnAssets` 12/12 sig β<0 (consistent — larger firms more liquid). `TobinsQ` 11/12 sig β<0 (col 8 null). `ROA` 12/12 sig β<0 (consistent). `Leverage` 1/12 sig β>0 (col 2 firm+yr contemp only). `Capex` 10/12 sig β<0 (cols 2, 4 firm contemp null). `DivDummy` **7/12 sig with FE sign flip** — cols 3, 5 ind contemp β>0; cols 2, 6, 8, 10, 12 firm β<0. Anomaly flag. `sCFO` 10/12 sig β<0 (cols 2, 8 null).
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` 8/8 sig β>0 (larger vol → more illiquidity). `StockPrice` 8/8 sig (small-magnitude positive). `Turnover` 8/8 sig β<0 (more turnover → more liquidity). `UncQue` 6/8 sig β<0 (cols 3, 9 null).
    - **Lagged_DV** (rule 23 structural): contemp 0.710 / 0.609 / 0.693 / 0.591 / 0.694 / 0.594; lead 0.728 / 0.626 / 0.717 / 0.611 / 0.717 / 0.613. **High persistence — ind ~0.70, firm ~0.60**. Level variable (opposite of H7 change variable which had 0/12 null Lagged_DV).
    - **R² / N**: contemp 0.541 / 0.390 → 0.545 / 0.395; lead 0.546 / 0.395 → 0.544 / 0.392. Much higher than H7 (level variant R² ~0.39-0.55 vs change variant R² ~0.003). N = 63,736 → 60,182 → 63,313 → 61,060.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: Level variant of H7 on same panel. Primary `UncAnsMgr` null. `UncPreMgr` 2/12 sig β>0 — both cells industry-FE + extended controls (cols 3, 9). Cross-sectional-only pattern matching §5.5. CEO measures null. Contrast with H7: same panel, same IVs, same FE ladders, but H7b has high Lagged_DV and R², while H7 has zero persistence and near-zero R². Structural difference between level and change DVs.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern (2 sig UncPreMgr cells). Weaker than H5/H7c but not null. Level-vs-change structural contrast with H7 logged in §5.16.

### H7c — Speech Uncertainty and BGT (2018) 25-Day Post-Call Amihud Level

- **DV**: `BGTLevel_Amihud` = Amihud[0,+25] level with day 0 included (cols 1-6); `BGTLevel_Amihud_lead1` (cols 7-12)
- **N**: 60,256–63,806
- **FE ladder**: identical to H5/H7/H7b
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **6/12 sig β>0 — ALL 6 contemp cells across all FE ladders including 3 firm-FE cells** (cols 1, 2, 3, 4, 5, 6). Lead 0/6 null. **First 6/6 UncAnsCEO contemp-all-FE pattern in the audit** — breadth + firm-FE depth. `UncPreCEO` 0/12 null. `UncAnsMgr` 0/12 null. `UncPreMgr` 1/12 sig β>0 — col 9 (ind+yr+ext lead only).
    - **Base controls**: `lnAssets` 12/12 sig β<0 (consistent). `TobinsQ` 5/12 sig β<0 — cols 1, 3, 5, 7, 11 (all industry-FE; firm-FE 0/6 null — FE-strata split). `ROA` 12/12 sig β<0 (consistent). `Leverage` 2/12 sig β<0 — cols 3, 10 only. `Capex` 10/12 sig β<0 (cols 2, 4 null). `DivDummy` **6/12 sig with FE sign flip** — cols 3, 5 ind β>0; cols 2, 8, 10, 12 firm β<0. Anomaly flag. `sCFO` 2/12 sig β<0 — cols 4, 6 firm-FE contemp only.
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` 8/8 sig β>0. `StockPrice` 8/8 sig (small positive). `Turnover` 8/8 sig β<0. `UncQue` 4/8 sig β<0 — cols 3, 4, 5, 6 contemp; lead 0/4 null.
    - **Lagged_DV** (rule 23 structural): contemp 0.790 / 0.680 / 0.774 / 0.661 / 0.777 / 0.665; lead 0.786 / 0.678 / 0.783 / 0.668 / 0.784 / 0.672. **Very high persistence** (ind ~0.78, firm ~0.67) — matches H7b level.
    - **R² / N**: contemp 0.621 / 0.451 → 0.622 / 0.454; lead 0.623 / 0.456 → 0.619 / 0.451. High R² across all cells. N = 63,806 → 60,256 → 63,351 → 61,099.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: **6/6 UncAnsCEO contemp cells sig β>0 across all FE ladders including 3 firm-FE cells (cols 2, 4, 6)** — the deepest CEO-channel signal in the audit so far. Primary `UncAnsMgr` null. The pattern inverts the thesis IV hierarchy (primary=Mgr, CEO=secondary) per `feedback_ceo_noisy_mgr_central.md`. `UncPreMgr` 1/12 sig lead only. Per rule 18 no mechanism label is committed.
- **Verdict**: **KEEP (measurement-concerns flag — CEO inverts primary hierarchy)**.
- **Rationale**: Rule 21 KEEP default for informative pattern. **6/6 UncAnsCEO contemp-all-FE is the deepest CEO signal in audit** — echoes §5.1 H1 CEO-lead > Mgr-lead breadth inversion on cash but goes DEEPER (contemp horizon + firm-FE survival, 3 firm-FE cells). Per feedback_ceo_noisy_mgr_central logged as measurement concerns, not rescued. New §5.15 entry.

### H7d — Speech Uncertainty and BGT-Window 25-Day Amihud Delta ([+1,+25]-[-25,-1])

- **DV**: `BGTDelta_Amihud` (cols 1-6); `BGTDelta_Amihud_lead1` (cols 7-12)
- **N**: 60,036–63,537
- **FE ladder**: identical to H5/H7/H7b/H7c (6 × 2 DVs)
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` **4/12 sig β>0** — cols 7 (ind+yr lead), 9 (ind+yr+ext lead), 11 (ind+yq+ext lead), 12 (firm+yq+ext lead). **All 4 in lead horizon; 3 industry-FE + 1 firm-FE (col 12).** `UncAnsMgr` **1/12 sig β>0** (col 1 ind+yr contemp only). `UncPreMgr` 0/12 null.
    - **Base controls**: `lnAssets` 12/12 sig β>0 (consistent). `TobinsQ` 12/12 sig β>0 (consistent). `ROA` 3/12 sig β<0 — cols 1, 2 contemp ind/firm + col 9 ind+yr+ext lead. `Leverage` 7/12 sig β<0 — cols 1-6 contemp (all FE) + col 8 firm+yr lead. `Capex` 1/12 sig β<0 (col 3 ind+yr+ext contemp only). `DivDummy` 2/12 sig β<0 — cols 9, 11 lead industry-FE + ext only. `sCFO` 1/12 sig β<0 (col 3 only).
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` **6/8 sig with horizon sign flip** — contemp cols 4, 6 β>0; lead cols 9, 10, 11, 12 β<0. Anomaly. `StockPrice` 7/8 sig β<0 (col 3 null). `Turnover` **4/8 sig β>0 — all 4 lead cells only** (contemp 0/4 null; horizon split). `UncQue` 0/8 null.
    - **Lagged_DV** (rule 23 structural): 0.164 / 0.141 / 0.172 / 0.147 / 0.170 / 0.149 / 0.178 / 0.156 / 0.172 / 0.153 / 0.174 / 0.155. **12/12 sig ~0.14–0.18 — moderate persistence** (weaker than H7b/H7c/H7e levels but stronger than H7 3-day change 0/12 null).
    - **R² / N**: contemp 0.030 / 0.022 → 0.032 / 0.025; lead 0.034 / 0.026 → 0.038 / 0.031. Low but not near-zero (between H7 0.003 and H7b 0.55). N = 63,537 → 60,036 → 63,066 → 60,826.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: 25-day change variant on Amihud illiquidity. Primary `UncAnsMgr` 1/12 (col 1 only). `UncPreCEO` 4/12 sig lead-horizon industry-FE + col 12 firm-FE cluster — first UncPreCEO cluster in the audit. Compared to H7 (3-day change near-null 1/48) and H7c (25-day level 6/12 contemp UncAnsCEO all-FE), H7d sits in between: 5/48 sig, R² 0.02–0.04, change variable on the longer window. The window length matters more than level vs change for this DV.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern. §5.16 level-vs-change nuance: the 25-day-window change variant carries modest signal (5/48) while the 3-day change is near-null (1/48) — window length matters. Distinctive UncPreCEO lead-horizon cluster (4/12 cols 7, 9, 11, 12) is new and noted in §5.18.

### H7e — Speech Uncertainty and BGT-Window 25-Day Amihud Average ([-25,+25], 51-day symmetric)

- **DV**: `BGTAvg_Amihud` (cols 1-6); `BGTAvg_Amihud_lead1` (cols 7-12)
- **N**: 60,256–63,816
- **FE ladder**: identical to H5/H7/H7b/H7c/H7d
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` 0/12 null. `UncAnsMgr` 0/12 null. `UncPreMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead). Both industry-FE + extended controls only (cross-sectional-only matching §5.5 and identical to H7b pattern).
    - **Base controls**: `lnAssets` 12/12 sig β<0. `TobinsQ` **9/12 sig β<0** (cols 8, 10, 12 null — firm-FE leads). `ROA` 12/12 sig β<0. `Leverage` **4/12 sig β<0** — cols 3, 9, 10, 12 only. `Capex` **10/12 sig β<0** (cols 2, 6 null). `DivDummy` **6/12 sig with FE sign flip** — cols 3, 5, 9 ind β>0; cols 8, 10, 12 firm β<0. Anomaly. `sCFO` **3/12 sig β<0** — cols 4, 6, 10 firm-FE cells only.
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` 8/8 sig β>0. `StockPrice` 8/8 sig (small positive). `Turnover` 8/8 sig β<0. `UncQue` 2/8 sig β<0 — cols 5, 6 (ind+yq+ext + firm+yq+ext contemp only).
    - **Lagged_DV** (rule 23 structural): contemp 0.799 / 0.701 / 0.787 / 0.689 / 0.790 / 0.693; lead 0.805 / 0.708 / 0.797 / 0.699 / 0.799 / 0.701. **12/12 sig ~0.80 ind / 0.70 firm — highest persistence in audit so far**.
    - **R² / N**: contemp 0.647 / 0.496 → 0.649 / 0.500; lead 0.644 / 0.494 → 0.642 / 0.492. **Highest R² in liquidity family so far (0.64–0.65 ind / 0.48–0.50 firm)**. N = 63,816 → 60,256 → 63,397 → 61,136.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: 51-day symmetric average (including pre-call window). Primary `UncAnsMgr` null. `UncPreMgr` 2/12 sig β>0 pattern identical to H7b (cols 3, 9 ind+yr+ext only). **No UncAnsCEO 6/6 contemp pattern** — the 51-day symmetric average does NOT carry the H7c 25-day post-call-only CEO signal. The disappearance when pre-call is included suggests H7c's signal is specific to the post-call-only window structure.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern (2 sig UncPreMgr cells). H7e's disappearance of the H7c CEO 6/6 contemp pattern is a window-specificity observation for §5.15 scope.

### H14 — Speech Uncertainty and Lee (2016) 3-Day Bid-Ask Spread Change ($\Delta$DSPREAD)

- **DV**: `DSPREAD` = Lee (2016) [+1,+3]-[-3,-1] change (cols 1-6); `DSPREAD_lead1` (cols 7-12). **Rescaled by 10⁴ for readability** per notes block.
- **N**: 44,132–63,972 (extended-control merge drops ~30% of sample)
- **FE ladder**: identical to H7/H7b/H7c family
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/12 null. `UncPreCEO` 0/12 null. `UncAnsMgr` 0/12 null. `UncPreMgr` **1/12 sig β>0** (col 6 firm+yq+ext contemp only). **1/48 sig — near-complete null**, parallel to H7 DeltaILLIQ (also 1/48).
    - **Base controls**: `lnAssets` **10/12 sig β>0** (cols 10, 12 firm-FE lead null). `TobinsQ` **6/12 sig β>0** — cols 1, 2, 5, 7, 8, 11. `ROA` 2/12 sig β<0 — cols 1, 7. `Leverage` 3/12 sig β<0 — cols 1, 5, 7. `Capex` 2/12 sig β>0 — cols 5, 11. `DivDummy` 0/12 null. `sCFO` **9/12 sig β>0** — cols 1, 4, 5, 6, 7, 9, 10, 11, 12 (mostly ind+ext).
    - **Extended controls** (cols 3-6, 9-12): `StockPrice` **5/8 sig β<0** — cols 3, 5, 6, 9, 11 (col 4, 10, 12 null). `Turnover` 8/8 sig β>0. `DailyVola` **5/8 sig β<0** — col 3 + cols 9, 10, 11, 12. `AbsSurpDec` **4/8 sig β<0** — cols 3, 5 + cols 9, 11 (all industry-FE).
    - **Lagged_DV** (rule 23 structural): 0.014 / **-0.017* firm** / 0.017 / **-0.023** firm** / 0.013 / **-0.023** firm** / 0.013 / **-0.019* firm** / **0.022* ind** / -0.016 / 0.019 / -0.016. **5/12 sig, mixed-sign and near-zero values** — firm-FE cells mostly small negative, col 9 ind+yr+ext lead small positive, rest null. Change variable mean-reverts (similar to H7 0/12 null).
    - **R² / N**: contemp 0.005 / 0.001 → 0.007 / 0.001; lead 0.006 / 0.001 → 0.009 / 0.002. **R² 0.001–0.009 — near-zero explanatory power**, parallel to H7 (0.001–0.005). **N drops ~30% when extended controls added** (63,972 → 44,132 contemp; 63,554 → 44,640 lead) — external liquidity data merge coverage.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: Bid-ask spread change variant. Primary `UncAnsMgr` null. Only 1 sig cell across 48 IV cells. R² near-zero (0.001–0.009). Parallels H7 DeltaILLIQ (1/48, R² 0.001–0.005) almost exactly — both 3-day change variants on the same panel fail to carry speech-uncertainty signal. §5.16 level-vs-change hypothesis confirmed on the spread family.
- **Verdict**: **KEEP (near-null flag)**.
- **Rationale**: Rule 21 KEEP default (1 sig cell). §5.16 confirmed on spread side: H14 near-null twin of H7. User-override to DROP-flag available.

### H14b — Speech Uncertainty and Lee (2016) 3-Day Post-Call Bid-Ask Spread Level

- **DV**: `PostCallSpread` = Lee (2016) [+1,+3] level (cols 1-6); `PostCallSpread_lead1` (cols 7-12). **Rescaled by 10⁴**.
- **N**: 60,368–63,972 (same panel as H14, same ~30% extended-control drop)
- **FE ladder**: identical to H14
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **3/12 sig β>0 — cols 8, 10, 12 firm-FE lead cells only** (contemp 0/6 null; lead-ind 0/3 null). **Novel UncAnsCEO FE/horizon signature: all 3 sig cells are firm-FE lead.** `UncPreCEO` 0/12 null. `UncAnsMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead), industry-FE + ExtCtrl only. `UncPreMgr` **3/12 sig β>0** — col 2 (firm+yr contemp) + col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead). **8/48 sig total.**
    - **Base controls**: `lnAssets` 12/12 sig β<0 (consistent — larger firms tighter spreads). `TobinsQ` **11/12 sig β<0** (col 9 null). `ROA` 12/12 sig β<0. `Leverage` **10/12 sig β>0** (cols 3, 9 null). `Capex` **10/12 sig β<0** (cols 3, 9 null). `DivDummy` **7/12 sig with FE sign flip** — cols 3, 5 ind β>0; cols 2, 4, 6, 8, 10, 12 firm β<0. Anomaly. `sCFO` **4/12 sig β>0 — cols 2, 8, 10, 12 firm-FE cells only**.
    - **Extended controls** (cols 3-6, 9-12): `DailyVola` 8/8 sig β>0. `StockPrice` **6/8 sig with FE sign flip** — cols 3, 9 ind β<0; cols 4, 6, 10, 12 firm β>0. Anomaly. `Turnover` 8/8 sig β<0. `UncQue` **5/8 sig mixed** — cols 3, 9 ind β>0; cols 4, 5, 6 β<0. Anomaly.
    - **Lagged_DV** (rule 23 structural): contemp 0.615 / 0.454 / 0.591 / 0.413 / 0.563 / 0.409; lead 0.613 / 0.447 / 0.612 / 0.416 / 0.590 / 0.425. **12/12 sig ~0.60 ind / 0.43 firm** (intermediate persistence, lower than H7b/H7c/H7e Amihud levels).
    - **R² / N**: contemp 0.539 / 0.294 → 0.554 / 0.313; lead 0.547 / 0.292 → 0.555 / 0.303. Moderate-high R² (0.53–0.56 ind / 0.29–0.33 firm). N = 63,972 → 60,368 → 63,554 → 61,257.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: Level variant of H14 on same panel. Primary `UncAnsMgr` 2/12 sig industry-FE + ext (cols 3, 9, cross-sectional-only matching §5.5). **UncAnsCEO 3/3 firm-FE lead cells sig β>0** — novel signature distinct from prior CEO inversions: §5.1 H1 (cash lead ind-FE), §5.7 H13 (capex contemp firm-FE), §5.15 H7c (Amihud contemp all-FE). H14b is the first lead-horizon firm-FE-only CEO pattern. `UncPreMgr` 3/12 mixed (2 contemp + 1 lead ind+ext). §5.16 level-vs-change confirmed.
- **Verdict**: **KEEP (CEO firm-FE lead flag)**.
- **Rationale**: Rule 21 informative pattern. Fourth CEO-inversion instance on liquidity family, with a novel horizon/FE signature. New §5.18 documents the CEO-inversion sub-class pattern across liquidity suites.

### H14c — Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Level ([0,+25])

- **DV**: `BGTLevel_Spread` (cols 1-6); `BGTLevel_Spread_lead1` (cols 7-12). **Rescaled by 10⁴**.
- **N**: 44,092–63,899 (~30% extended-control drop)
- **FE ladder**: identical to H7c (BGT 25-day Amihud)
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **5/12 sig β>0 — cols 7, 8, 9, 10, 12 ALL lead-horizon cells** (2 ind cols 7, 9 + 3 firm cols 8, 10, 12); contemp 0/6 null (col 11 lead also null). **OPPOSITE horizon to H7c's 6/6 contemp UncAnsCEO**. `UncPreCEO` **3/12 sig β>0 — cols 1, 2, 4 contemp cells** (ind+yr + firm+yr + firm+yr+ext); lead 0/6 null. **First UncPreCEO sig pattern in the audit**. `UncAnsMgr` **2/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead) — same pattern as H7b/H7e/H14b. `UncPreMgr` **4/12 sig β>0** — col 3 (ind+yr+ext contemp) + cols 9, 10, 12 (ind+yr+ext lead + firm+yr+ext lead + firm+yq+ext lead). **14/48 sig — richest liquidity suite in audit**.
    - **Base controls**: `lnAssets` 12/12 sig β<0. `TobinsQ` **12/12 sig with sign anomaly** — col 9 sig β>0 (+0.101**), other 11 sig β<0. Col 9 sign flip anomaly. `ROA` 12/12 sig β<0. `Leverage` 5/12 sig mixed — col 1 β>0, col 2 β>0, col 7 β>0, col 8 β>0, col 9 β<0. Anomaly. `Capex` 3/12 sig β<0 — cols 7, 8, 10 (lead cells only). `DivDummy` 4/12 sig mixed — cols 3, 5 ind β>0 contemp + col 8 firm β<0 lead. `sCFO` 4/12 sig β>0 — cols 2, 4, 6, 8 firm-FE cells only.
    - **Extended controls** (cols 3-6, 9-12): `StockPrice` **6/8 sig with FE sign flip** — col 3 ind β<0 + col 4 β<0 + col 6 null + col 9 ind β<0 + col 10 firm β>0 + col 12 firm β>0 (3 β<0 + 2 β>0 mixed). Anomaly. `Turnover` 8/8 sig β<0. `DailyVola` 8/8 sig β>0. `AbsSurpDec` **2/8 sig mixed** — col 5 β<0 contemp + col 9 β>0 lead.
    - **Lagged_DV** (rule 23 structural): contemp 0.814 / 0.703 / 0.733 / 0.631 / 0.733 / 0.642; lead 0.805 / 0.681 / 0.754 / 0.611 / 0.760 / 0.648. **12/12 sig ~0.75 ind / 0.65 firm — very high persistence**.
    - **R² / N**: contemp 0.778 / 0.585 → 0.730 / 0.557; lead 0.774 / 0.567 → 0.723 / 0.530. **Highest R² in audit** (0.72–0.78 ind / 0.53–0.59 firm). N = 63,899 → 44,092 → 63,443 → 44,569.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: 25-day BGT level on bid-ask spread. **Three distinct IV patterns**: (a) `UncAnsCEO` 5/6 lead cells sig β>0 across both ind and firm FE — OPPOSITE horizon to H7c's 6/6 contemp on Amihud (same 25-day window, different market DV, opposite horizon loading); (b) **`UncPreCEO` 3/3 contemp cells sig β>0** — first UncPreCEO sig pattern in the audit (breaks the "UncPreCEO always null" baseline seen in all prior suites); (c) `UncAnsMgr` + `UncPreMgr` cross-sectional-only pattern matching §5.5. Richest liquidity signal in audit (14/48).
- **Verdict**: **KEEP (multiple flags)**.
- **Rationale**: Rule 21 informative pattern. Three cross-cutting observations surface: (a) H14c vs H7c horizon split on same BGT 25-day window (different DVs, different horizons); (b) first UncPreCEO sig pattern in audit; (c) H14c has highest R² and richest IV signal of any liquidity suite. All three flagged in new §5.18 (joint H14b/H14c liquidity-family CEO structures) and §5.19 (first UncPreCEO).

### H14d — Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Delta ([+1,+25]-[-25,-1])

- **DV**: `BGTDelta_Spread` (cols 1-6); `BGTDelta_Spread_lead1` (cols 7-12). **Rescaled by 10⁴** per notes block.
- **N**: 43,282–62,480 (ext-control merge drops ~30%)
- **FE ladder**: identical to H7/H7b/H7c/H7d/H7e/H14/H14b/H14c family (6 × 2 DVs)
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **1/12 sig β>0** (col 8 firm+yr lead only). `UncPreCEO` 0/12 null. `UncAnsMgr` 0/12 null. `UncPreMgr` 0/12 null. **1/48 near-null**.
    - **Base controls**: `lnAssets` **11/12 sig β>0** (col 3 null). `TobinsQ` **11/12 sig β>0** (col 3 null). `ROA` **7/12 sig β<0** — cols 1, 2, 4, 9, 10, 11, 12. `Leverage` **7/12 sig β<0** — cols 1, 2, 4, 5, 6, 7, 8. `Capex` **6/12 sig β>0** — cols 1, 2, 4, 5, 6, 7. `DivDummy` **2/12 sig β>0** — cols 4, 6 only. `sCFO` **7/12 sig β>0** — cols 2, 4, 6, 9, 10, 11, 12.
    - **Extended controls** (cols 3-6, 9-12): `StockPrice` **6/8 sig mixed-sign** — col 3 β>0 + cols 6, 9, 10, 11, 12 β<0. `Turnover` **7/8 sig β>0** (col 6 null). `DailyVola` **7/8 sig with horizon sign flip** — cols 4, 5, 6 contemp β>0 + cols 9, 10, 11, 12 lead β<0. `AbsSurpDec` **4/8 sig β<0** — all 4 contemp (cols 3, 4, 5, 6).
    - **Lagged_DV** (rule 23 structural): -0.006 / **-0.033** / 0.010 / **-0.023** / 0.019 / -0.013 / -0.002 / **-0.028** / 0.018 / -0.011 / 0.019 / -0.010. **3/12 sig firm-FE small β<0** (mean reversion, near-zero). Change variable.
    - **R² / N**: contemp 0.005 / 0.004 → 0.006 / 0.006; lead 0.003 / 0.003 → 0.007 / 0.006. **R² 0.002–0.012 near-zero**. N = 62,480 → 43,282 → 62,029 → 43,750.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: 25-day change variant on bid-ask spreads. Primary `UncAnsMgr` null. Only 1 sig cell (UncAnsCEO col 8 firm+yr lead). R² 0.002–0.012 (near-zero). **Contrast with H7d** (BGTDelta_Amihud 5/48 sig including 4 UncPreCEO lead-horizon cells): the same 25-day change window on Amihud carries modest signal, on spreads does not. Window-DV asymmetry.
- **Verdict**: **KEEP (near-null flag)**.
- **Rationale**: Rule 21 KEEP default (1 sig cell). H14d is a second near-null in the spread family after H14 3-day change (1/48), both near-null on change variants. §5.20 new entry: BGT 25-day window × DV asymmetry (Amihud carries H7d signal, Spread does not).

### H14e — Speech Uncertainty and BGT-Window 25-Day Bid-Ask Spread Average ([-25,+25], 51-day symmetric)

- **DV**: `BGTAvg_Spread` (cols 1-6); `BGTAvg_Spread_lead1` (cols 7-12). **Rescaled by 10⁴**.
- **N**: 44,100–63,936 (ext-control merge drops ~30%)
- **FE ladder**: identical to H14d
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` **2/12 sig β>0** — cols 7 (ind+yr lead), 8 (firm+yr lead). Contemp 0/6 null. `UncPreCEO` **3/12 sig β>0 — cols 1, 2, 4 contemp only** (ind+yr + firm+yr + firm+yr+ext) — **same pattern as H14c**. Lead 0/6 null. **Second UncPreCEO sig contemp suite.** `UncAnsMgr` **1/12 sig β>0** (col 9 ind+yr+ext lead only — same col 9 pattern as H7b/H7e/H14b/H14c). `UncPreMgr` **3/12 sig β>0** — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead) + col 12 (firm+yq+ext lead). **9/48 sig.**
    - **Base controls**: `lnAssets` 12/12 sig β<0. `TobinsQ` **11/12 sig β<0** (col 9 null). `ROA` 12/12 sig β<0. `Leverage` **5/12 sig mixed** — cols 1, 2 β>0 contemp + col 8 β>0 firm lead + col 9 β<0 ind lead (sign flip across FE × horizon). `Capex` **2/12 sig β<0** — cols 7, 8 lead only. `DivDummy` **5/12 sig mixed** — cols 3, 5, 9, 11 ind β>0 + col 8 firm β<0. `sCFO` **1/12 sig β>0** (col 8 firm+yr lead only).
    - **Extended controls** (cols 3-6, 9-12): `StockPrice` **4/8 sig mixed** — cols 3, 4 contemp β<0 + cols 10, 12 firm lead β>0. `Turnover` 8/8 sig β<0. `DailyVola` 8/8 sig β>0. `AbsSurpDec` **3/8 sig mixed** — col 5 β<0 + col 9 β>0 + col 11 β<0.
    - **Lagged_DV** (rule 23 structural): contemp 0.856 / 0.765 / 0.782 / 0.694 / 0.779 / 0.699; lead 0.841 / 0.734 / 0.789 / 0.667 / 0.802 / 0.708. **12/12 sig ~0.85 ind / 0.73 firm — highest persistence in audit**.
    - **R² / N**: contemp 0.826 / 0.663 → 0.786 / 0.638; lead 0.818 / 0.641 → 0.787 / 0.625. **R² 0.60–0.83 — highest industry-FE R² in audit (0.83)**. N = 63,936 → 44,100 → 63,509 → 44,600.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: 51-day symmetric average on bid-ask spreads. `UncPreCEO` 3/3 contemp cells sig β>0 — same pattern as H14c (second UncPreCEO contemp sig suite). `UncAnsCEO` 2/12 sig β>0 cols 7, 8 lead. `UncAnsMgr` + `UncPreMgr` cross-sectional-only cells. **Contrast with H7e** (51-day Amihud avg, 2/48 only UncPreMgr ind+ext): 51-day symmetric window LOSES the H7c Amihud contemp UncAnsCEO signal completely but PARTIALLY PRESERVES the H14c spread UncPreCEO contemp signal. 51-day-window behavior is DV-specific.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern. 9/48 sig — second-richest spread suite after H14c's 14/48. Highest R² in the audit (0.83 ind). Cross-DV window asymmetry extends §5.20 observation. UncPreCEO contemp pattern repeats from H14c → §5.21.

### H18 — Speech Uncertainty and SEC Comment Letters (CCCL, LPM)

- **DV**: `CCCL` (binary, 1 DV, 6 cols — no lead variant in this suite)
- **N**: 64,172–66,886
- **FE ladder**: (1) Ind+Yr, (2) Firm+Yr, (3) Ind+Yr+ExtCtrl, (4) Firm+Yr+ExtCtrl, (5) Ind+YQ+ExtCtrl, (6) Firm+YQ+ExtCtrl
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/6 null. `UncPreCEO` 0/6 null. `UncAnsMgr` 0/6 null. `UncPreMgr` **2/6 sig β>0** — cols 1 (ind+yr) + 2 (firm+yr), both without extended controls. Cols 3-6 (with ExtCtrl) 0/4 null — extended controls absorb the signal.
    - **Base controls**: `lnAssets` **5/6 sig with FE sign flip** — cols 1, 3, 5 ind β<0 + cols 4, 6 firm β>0 (col 2 firm no-ext null). Anomaly flag. `TobinsQ` 0/6 null. `ROA` 0/6 null. `Leverage` 0/6 null. `Capex` 0/6 null. `CashRatio` **3/6 sig β<0** — cols 2, 4, 6 firm-FE only (FE-strata split). `DivDummy` 0/6 null. `sCFO` 0/6 null.
    - **Extended controls** (cols 3-6): `SalesGrowth` 0/4 null. `RDSales` **2/4 sig β<0** — cols 3, 5 ind-FE only. `CashFlowAt` 0/4 null. `DailyVola` **2/4 sig β<0** — cols 4, 6 firm-FE only.
    - **Lagged_DV** (rule 23 structural): -0.003 / **-0.0297** / -0.003 / **-0.0306** / -0.003 / **-0.0306**. **3/6 sig firm-FE β<0** (mean reversion on binary CCCL DV). Ind cells null.
    - **R² / N**: 0.000 / 0.001 / 0.000 / 0.001 / 0.000 / 0.001. **R² 0.000–0.001 — essentially zero explanatory power**. LPM on binary CCCL (rare event, low base rate). N = 66,886 → 64,172.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: LPM on binary CCCL (SEC comment letter received). Primary `UncAnsMgr` null. Only `UncPreMgr` sig — 2/6 cells (cols 1, 2 ind+yr and firm+yr, both without extended controls). With extended controls (cols 3-6) the UncPreMgr signal disappears. Near-zero R² reflects rare-event LPM difficulty. Robustness to functional form checked in H18b (Logit variant).
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern (2 sig cells). Extended-control sensitivity noted — RDSales / DailyVola absorb the UncPreMgr signal. §5.22 entry on CCCL DV class (near-zero LPM R², rare-event binary DV).

### H18b — Speech Uncertainty and SEC Comment Letters (Logit Robustness Check)

- **DV**: `CCCL` (binary, 1 DV, 2 cols — logit statsmodels does not support firm FE)
- **N**: 64,172–66,886 (same panel as H18)
- **FE ladder**: (1) Ind+Yr, (2) Ind+Yr+ExtCtrl. No firm FE.
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/2 null. `UncPreCEO` 0/2 null. `UncAnsMgr` 0/2 null. `UncPreMgr` **2/2 sig β>0** — col 1 (ind+yr) + col 2 (ind+yr+ext). Both cells sig — **UncPreMgr signal robust in Logit even with extended controls**, unlike H18 LPM where ExtCtrl absorbed it.
    - **Base controls**: `lnAssets` 1/2 sig β<0 (col 2 only). `TobinsQ` 0/2 null. `ROA` 0/2 null. `Leverage` 0/2 null. `Capex` 0/2 null. `CashRatio` 0/2 null. `DivDummy` 0/2 null. `sCFO` 0/2 null.
    - **Extended controls** (col 2 only): `SalesGrowth` 0/1 null. `RDSales` 0/1 null (contrast with H18 where ind-FE cols 3, 5 were sig β<0). `CashFlowAt` 0/1 null. `DailyVola` 0/1 null.
    - **Lagged_DV** (rule 23 structural): -0.002 / -0.003. 0/2 null.
    - **Pseudo R²**: 0.089 / 0.090. Moderate pseudo R² (much higher than H18 LPM's 0.000–0.001). N = 66,886 / 64,172.
- **Reader-question**: Q3 (provisional, placeholder per rule 21). H18b is a robustness check for H18, not an independent DV test.
- **Argument**: Logit statsmodels variant of H18 without firm FE (logit does not support firm fixed effects in statsmodels). `UncPreMgr` 2/2 sig β>0 — both ind-FE cells (with and without ExtCtrl). **Robustness to functional form confirmed**: LPM H18 had UncPreMgr sig in cols 1, 2 ind+yr no-ext; Logit H18b has UncPreMgr sig in both ind cells. CEO measures null in both. `UncAnsMgr` null in both.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern. Logit robustness check confirms H18's UncPreMgr ind-FE pattern is robust to functional form choice (LPM vs Logit). §5.22.

### H21 — Speech Uncertainty and SEC Comment Letter Count

- **DV**: `SEC_Letters_fwd` (count, 1 DV, 6 cols)
- **N**: 64,172–66,886 (same panel as H18)
- **FE ladder**: identical to H18
- **Tail**: one-tailed β>0 for IVs; two-tailed for controls
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **IVs**: `UncAnsCEO` 0/6 null. `UncPreCEO` **3/6 sig β>0 — cols 1, 3, 5 industry-FE only** (firm-FE 0/3 null). **Third UncPreCEO sig suite in audit** (after H14c + H14e; all three on information/market-side DVs). `UncAnsMgr` 0/6 null. `UncPreMgr` 0/6 null. **3/24 sig.**
    - **Base controls**: `lnAssets` **6/6 sig with FE sign flip** — cols 1, 3, 5 ind β<0 + cols 2, 4, 6 firm β>0. Anomaly flag. `TobinsQ` **3/6 sig β<0 — industry-FE only** (firm-FE 0/3 null). `ROA` **2/6 sig β<0** — cols 1, 2 (no ext). `Leverage` **6/6 sig β>0 — all cells**. `Capex` 0/6 null. `CashRatio` **3/6 sig β<0 — firm-FE only** (cols 2, 4, 6). `DivDummy` **3/6 sig β<0 — industry-FE only** (cols 1, 3, 5). `sCFO` **1/6 sig β<0** (col 6 only).
    - **Extended controls** (cols 3-6): `SalesGrowth` 0/4 null. `RDSales` 0/4 null. `CashFlowAt` 0/4 null. `DailyVola` **3/4 sig β>0** (col 6 null).
    - **Lagged_DV** (rule 23 structural): 0.004 / **-0.0647** / 0.004 / **-0.0661** / 0.005 / **-0.0652**. **3/6 sig firm-FE β<0** (mean reversion on count DV).
    - **R² / N**: 0.004 / 0.005 / 0.004 / 0.005 / 0.004 / 0.005. **R² 0.004–0.005 — near-zero**. N = 66,886 → 64,172.
- **Reader-question**: Q3 (provisional, placeholder per rule 21).
- **Argument**: SEC comment letter forward count DV (distinct from H18's binary CCCL received indicator). `UncPreCEO` 3/6 sig β>0 — all 3 industry-FE cells (cols 1, 3, 5), firm-FE 0/3 null. **Third UncPreCEO sig instance in audit** (after H14c BGT spread level 3/3 contemp + H14e BGT spread 51-day 3/3 contemp). All three on information-channel / market-side DVs. CEO primary UncAnsCEO null. Primary `UncAnsMgr` null. `UncPreMgr` 0/6 null — opposite direction from H18/H18b where UncPreMgr was sig. Different Pre measures load on different information DVs.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern (3 sig UncPreCEO cells). UncPreCEO recurring signal is now a cross-suite pattern (H14c, H14e, H21). §5.21 entry.

### H11 — Political Risk and Speech Uncertainty (Hassan, Hollander, van Lent, Tahoun 2019 PRisk)

- **DV**: 4 speech measures as parallel DVs across columns — `UncAnsMgr` (cols 1, 5), `UncAnsCEO` (cols 2, 6), `UncPreMgr` (cols 3, 7), `UncPreCEO` (cols 4, 8). **REVERSE direction**: speech is LHS; PRisk is RHS. Contemp only (no lead spec).
- **N**: 77,658 / 65,394 / 77,758 / 65,760 per DV (larger than Q1-Q3 Main panels; ~77K on Mgr DVs, ~65K on CEO DVs reflecting the CEO coverage gap per `reference_ceo_coverage_gap.md`)
- **FE ladder**: (1-4) Industry FE + Year FE across 4 DVs; (5-8) Firm FE + Year FE across 4 DVs. No extended controls variant. No year-quarter FE variant. **No Lagged_DV control in spec** (shared with H23; both firm-level construct IVs — §5.25). Only H24/H24b/H25 (macro-monthly IVs) include Lagged_DV.
- **Tail**: one-tailed β>0 for IV; two-tailed for controls (line 849)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue, re-read 2026-04-16):
    - **Primary IV**: `PRisk_t` **8/8 sig β>0** — all 4 DVs × both FE strata. β = 0.0002 / 0.0001 / 0.0002 / 0.0003 (ind); 0.0001 / 0.0001 / 0.0001 / 0.0002 (firm). All *** at p<0.01. Broadest IV pattern in Q4 cluster (tied with H11-Lag1, H11-Lag2, H24b).
    - **Base controls**: `UncQue` **8/8 sig β>0** (cols 1-4 ind β≈0.02-0.05; cols 5-8 firm β≈0.008-0.04). `NegCall` **8/8 sig β>0** (all cells). `lnAssets` **4/8 sig β<0 — all 4 ind cells (β≈-0.02 to -0.03), firm-FE 0/4 null** (FE-strata split). `TobinsQ` **2/8 sig β<0 — cols 1, 2 ind UncAns DVs only**; cols 3, 4 ind (UncPre DVs) null; firm 0/4 null. `ROA` **5/8 sig β>0** — cols 1, 2, 3 ind (β≈0.07-0.10) + cols 5, 6 firm (β≈0.06); col 4 ind (UncPreCEO) null 0.0477, cols 7, 8 firm (UncPre DVs) null. `CashRatio` **3/8 sig — mixed location**: col 3 ind UncPreMgr β=0.0923*** + cols 5, 6 firm UncAnsMgr/UncAnsCEO β>0 sig. `DivDummy` **3/8 sig β<0** — col 3 ind UncPreMgr β=-0.0481*** + cols 7, 8 firm UncPre DVs β≈-0.02. `FirmMat` **4/8 sig β>0** — cols 3, 4 ind (β≈0.002-0.004) + cols 5, 6 firm (β≈0.003). `EarnVol` **0/8 null**.
    - **Same-call Pre controls** (structural — added to UncAns DV cols only to control for within-call Pre correlation): `UncPreMgr` appears in cols 1 + 5 (UncAnsMgr DV cols), **2/2 sig β>0** (β=0.1637*** ind, 0.1174*** firm). `UncPreCEO` appears in cols 2 + 6 (UncAnsCEO DV cols), **2/2 sig β>0** (β=0.1786*** ind, 0.1078*** firm).
    - **Lagged_DV**: **NOT PRESENT in this spec.** Structural observation — no DV persistence control, unlike every other Q4 suite.
    - **R² / N**: **R² 0.066 / 0.057 / 0.053 / 0.043 (ind)**; **0.026 / 0.021 / 0.018 / 0.023 (firm)**. **Adj R² on 3 of 4 firm-FE cells is NEGATIVE** (0.002 / -0.006 / -0.005 / -0.004). N: Mgr DVs 77,658 / 77,758; CEO DVs 65,394 / 65,760.
- **Reader-question**: Q4 (provisional, placeholder per rule 21) — construct validation / reverse-direction test.
- **Argument**: PRisk loads 8/8 with β>0 on every speech DV under both FE strata. The thesis's speech IV is at minimum partly correlated with firm-level political risk exposure (Hassan-Hollander-van Lent-Tahoun 2019 measure). Magnitudes are very small (β≈0.0001-0.0003) and firm-FE Adj R² runs negative on 3 of 4 cells — the within-firm explanatory contribution of PRisk is nearly zero even though the coefficient is statistically distinguishable from zero at 112K-call N. Spec does NOT include Lagged_DV so DV persistence is unabsorbed. Pattern is an informative empirical fact about IV-construct overlap; Q-answer interpretation deferred to post-audit synthesis.
- **Verdict**: **KEEP** (tiny-magnitude + no-Lagged-DV flags for §5.23 / §5.25).
- **Rationale**: Rule 21 KEEP default for full-ladder informative pattern. Magnitudes and R²-weakness are Q5 economic-significance concerns downstream of the audit; they do not reduce the factual record of 8/8 sig cells. Two structural flags filed at cross-cutting §5.23 (tiny-magnitude broad-loading) and §5.25 (H11-series no-Lagged-DV spec difference from H23/H24/H24b/H25).

### H11-Lag1 — Political Risk (1-Qtr Lag) and Speech Uncertainty

- **DV**: Same 4 speech DVs as H11 (UncAnsMgr / UncAnsCEO / UncPreMgr / UncPreCEO across 8 cols)
- **N**: 74,918 / 63,049 / 75,014 / 63,399 per DV (smaller than H11 by ~3K, lag requirement drops head-of-panel observations)
- **FE ladder**: Identical to H11 — Ind+Yr cols 1-4, Firm+Yr cols 5-8. No ExtCtrl, no YQ FE, no Lagged_DV.
- **Tail**: one-tailed β>0 for IV
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `PRisk_{t-1}` **8/8 sig β>0** — same full-ladder survival as H11 contemp. β = 0.0001 / 0.0001 / 0.0001 / 0.0002 (ind); 0.0000 / 0.0000 / 0.0001 / 0.0001 (firm). All *** at p<0.01. Firm-FE magnitudes round to 0.0000 under four-decimal display but retain three-star significance.
    - **Base controls**: Near-identical to H11 (values within 0.001-0.005 across cells). `UncQue` 8/8 sig, `NegCall` 8/8 sig, `lnAssets` 4/8 ind-only β<0 (FE-strata split), `TobinsQ` 2/8 ind-only β<0 (cols 1, 2), `ROA` **6/8 sig** — cols 1, 2, 3 ind + 5, 6 firm + col 8 firm β=0.0455* sig (new vs H11 contemp col 8 null); cols 4, 7 null. `CashRatio` 3/8 mixed (col 3 ind UncPreMgr + cols 5, 6 firm UncAns). `DivDummy` 3/8 sig β<0 (col 3 ind + cols 7, 8 firm). `FirmMat` **3/8 sig β>0** — col 3 ind β=0.0059*** + col 5 firm β=0.0028* + col 6 firm β=0.0039** (col 4 ind 0.0021 null). `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig (cols 1, 5 β=0.1693*** / 0.1219***). `UncPreCEO` 2/2 sig (cols 2, 6 β=0.1821*** / 0.1122***).
    - **Lagged_DV**: NOT PRESENT.
    - **R² / N**: **R² 0.063 / 0.055 / 0.049 / 0.036 (ind)**; **0.022 / 0.018 / 0.014 / 0.016 (firm)**. Adj R² on all 4 firm-FE cells NEGATIVE (-0.002 / -0.009 / -0.011 / -0.012). N: Mgr DVs 74,918 / 75,014; CEO DVs 63,049 / 63,399.
- **Reader-question**: Q4 (provisional).
- **Argument**: Lag-1 replication of H11's contemp pattern. Same 8/8 breadth, same tiny magnitudes, same near-zero firm-FE explanatory power. Structurally identical caveats.
- **Verdict**: **KEEP**.
- **Rationale**: Lag replication confirms the external-loading pattern is not contemp-only; same §5.23 / §5.25 flags apply.

### H11-Lag2 — Political Risk (2-Qtr Lag) and Speech Uncertainty

- **DV**: Same 4 speech DVs
- **N**: 74,467 / 62,674 / 74,561 / 63,022 (slightly smaller than H11-Lag1 by ~450 calls)
- **FE ladder**: Identical to H11
- **Tail**: one-tailed β>0 for IV
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `PRisk_{t-2}` **8/8 sig β>0**. β = 0.0001 / 0.0001 / 0.0001 / 0.0001 (ind, all ***); 0.0000 / 0.0000 / 0.0000 / 0.0000 (firm). **Col 6 (firm UncAnsCEO) drops to ** from *** — only cell in H11-series weakening below the p<0.01 bar.** All other 7 cells remain ***.
    - **Base controls**: Near-identical to H11 / H11-Lag1. `UncQue` 8/8 sig, `NegCall` 8/8 sig, `lnAssets` 4/8 ind-only β<0, `TobinsQ` 2/8 ind-only β<0 (cols 1, 2), `ROA` **6/8 sig** (cols 1-3 ind + 5, 6 firm + col 8 firm β=0.0464* sig; cols 4, 7 null). `CashRatio` **3/8 mixed** (col 3 ind UncPreMgr + cols 5, 6 firm UncAns, unchanged from lags). `DivDummy` **3/8 sig β<0** (col 3 ind*** + col 7 firm* + col 8 firm*). `FirmMat` **3/8 sig** (col 3 ind** + col 5 firm* + col 6 firm**). `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig (cols 1, 5 β=0.1707*** / 0.1247***). `UncPreCEO` 2/2 sig (cols 2, 6 β=0.1827*** / 0.1138***).
    - **Lagged_DV**: NOT PRESENT.
    - **R² / N**: **R² 0.063 / 0.055 / 0.048 / 0.035 (ind)**; **0.023 / 0.019 / 0.013 / 0.015 (firm)**. Adj R² firm cells all NEGATIVE. N: Mgr DVs 74,467 / 74,561; CEO DVs 62,674 / 63,022.
- **Reader-question**: Q4 (provisional).
- **Argument**: Lag-2 replication with one cell attenuation (col 6 firm UncAnsCEO drops *** → **). All other cells retain H11 pattern. Logged as factual observation, not interpreted.
- **Verdict**: **KEEP**.
- **Rationale**: Minor attenuation at one cell across 2-quarter lag horizon; 8/8 breadth preserved. §5.23 / §5.25 flags apply.

### H23 — Product-Market Competition and Speech Uncertainty (TSIMM firm-year)

- **DV**: Same 4 speech DVs (8 cols: 4 ind+yr, 4 firm+yr). **Unit of observation: firm-fiscal-year** (line 2222) — small-sample class parallel to H22 / H20b.
- **N**: 20,768 / 18,447 / 20,774 / 18,492 per DV (firm-year, ~1/4 of Main call panel)
- **FE ladder**: (1-4) Ind FE + Year FE across 4 DVs; (5-8) Firm FE + Year FE. No ExtCtrl, no YQ FE. **No Lagged_DV in spec** (shared with H11-series — both firm-level construct IVs, §5.25).
- **Tail**: one-tailed β>0 for IV (line 2219)
- **Cluster**: firm-level
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `z(log(TSIMM))` **4/8 sig β>0** — col 1 UncAnsMgr ind β=0.0090** + col 3 UncPreMgr ind β=0.0297*** + col 4 UncPreCEO ind β=0.0304*** + col 8 UncPreCEO firm β=0.0302***. Col 2 UncAnsCEO ind null; cols 5-7 firm null on UncAnsMgr / UncAnsCEO / UncPreMgr. **UncPreCEO is the only DV with firm-FE survival** (2/2 sig β>0).
    - **Cross-suite note**: H23 is the **fourth suite with significant UncPreCEO loading** in the audit (prior: H14c, H14e, H21 — all Q3 information DVs). H23 is the first Q4 UncPreCEO instance; direction β>0 matches H14c/H14e/H21 direction. §5.24.
    - **Base controls**: `UncQue` **7/8 sig β>0** (col 8 0.0084 null). `NegCall` **8/8 sig β>0**. `lnAssets` **4/8 sig β<0** — all 4 ind cells (FE-strata split), firm 0/4 null. `TobinsQ` **2/8 sig β<0** (cols 1, 2 ind UncAns DVs). `ROA` **6/8 sig β>0** — cols 1-4 ind + 5, 6 firm; col 7 null 0.0064, col 8 null 0.0241. `CashRatio` **3/8 mixed** — col 4 ind UncPreCEO β=-0.0803** (β<0) + col 5 firm UncAnsMgr β=0.0589*** + col 6 firm UncAnsCEO β=0.0524* (both β>0). `DivDummy` **2/8 sig β<0** (col 3 ind UncPreMgr*** + col 7 firm UncPreMgr*). `FirmMat` **5/8 sig β>0** (cols 1, 2, 4 ind + 5, 6 firm). `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig (cols 1, 5 β=0.1943*** / 0.1418***). `UncPreCEO` 2/2 sig (cols 2, 6 β=0.2491*** / 0.1687***).
    - **Lagged_DV**: **NOT PRESENT.** H23 runner does NOT include Lagged_DV in the spec — shared structural feature with H11-series. Only the macro-monthly suites (H24/H24b/H25) include Lagged_DV. See §5.25 for the refined structural split.
    - **R² / N**: **R² 0.104 / 0.103 / 0.064 / 0.050 (ind)**; **0.038 / 0.038 / 0.017 / 0.021 (firm)**. **Adj R² firm cells ALL NEGATIVE (-0.045 / -0.050 / -0.067 / -0.068)**. N: firm-year ~20K (Mgr DVs) / ~18K (CEO DVs).
- **Reader-question**: Q4 (provisional).
- **Argument**: TSIMM product-market similarity loads on speech uncertainty 4/8 industry-FE heavy and collapses under firm-FE except via UncPreCEO. The one firm-FE survivor is UncPreCEO (col 8 β=0.0302***), which extends the Q3 UncPreCEO recurring pattern (§5.21 H14c/H14e/H21) into Q4. Small firm-year panel (~20K) parallels H22 / H20b small-N class.
- **Verdict**: **KEEP** (small-panel + UncPreCEO-fourth-instance flags).
- **Rationale**: Rule 21 informative pattern. Ind-FE delivers on 3 DVs; firm-FE delivers only via UncPreCEO. Fourth UncPreCEO sig instance widens §5.21 → §5.24 (spans Q3 information DVs + Q4 reverse direction). Small firm-year N logged alongside H22/H20b — sample-size override at synthesis.

### H24 — US Economic Policy Uncertainty and Speech Uncertainty (BBD US EPU)

- **DV**: 4 speech DVs in **DIFFERENT column order** from H11/H23 — cols 1-4: UncAnsMgr / UncPreMgr / UncAnsCEO / UncPreCEO (Ind+Cal.Yr FE); cols 5-8 same order (Firm+Cal.Yr FE) per line 2237.
- **N**: 74,013 / 75,142 / 59,676 / 60,503 per DV (call-level)
- **FE ladder**: (1-4) Industry FE + **Calendar Year FE via `other_effects=cal_yr`**; (5-8) Firm FE + Calendar Year FE. **No TimeEffects and no Year-Quarter FE** (per `feedback_macro_iv_handling.md` — TimeEffects absorbs the monthly macro IV).
- **Tail**: one-tailed β>0 for IV
- **Cluster**: **two-way clustered (firm, cal_yr_qtr)** per line 2280
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `log(US EPU)_t` (calendar-month match, not aggregated) **6/8 sig β>0** — col 1 UncAnsMgr ind β=0.0141** + col 3 UncAnsCEO ind β=0.0117* + col 4 UncPreCEO ind β=0.0211*** + col 5 UncAnsMgr firm β=0.0147** + col 7 UncAnsCEO firm β=0.0138** + col 8 UncPreCEO firm β=0.0239***. **Col 2 UncPreMgr ind β=0.0065 null AND col 6 UncPreMgr firm β=0.0071 null — UncPreMgr is the only DV not responding to US EPU**. By DV: UncAnsMgr 2/2 sig, UncAnsCEO 2/2 sig, UncPreMgr 0/2 null, UncPreCEO 2/2 sig.
    - **Base controls**: `UncQue` **8/8 sig β>0**. `NegCall` **8/8 sig β>0**. `lnAssets` **4/8 sig β<0** — all 4 ind cells; firm 0/4 null (FE-strata split). `TobinsQ` **2/8 sig β<0** — cols 1, 3 ind (UncAns DVs under the new column ordering). `ROA` **7/8 sig β>0** — col 6 firm UncPreMgr null (β=0.0125), all others sig. `CashRatio` **3/8 sig β>0** — col 2 ind UncPreMgr β=0.0325*** + col 5 firm UncAnsMgr β=0.0534*** + col 7 firm UncAnsCEO β=0.0604***. `DivDummy` **3/8 sig β<0** — col 2 ind UncPreMgr β=-0.0167*** + col 6 firm UncPreMgr β=-0.0101* + col 8 firm UncPreCEO β=-0.0157*. `FirmMat` **3/8 sig β>0** — col 2 ind UncPreMgr β=0.0021*** + col 5 firm UncAnsMgr β=0.0027* + col 7 firm UncAnsCEO β=0.0039**. `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig β>0 on cols 1 + 5 (UncAnsMgr DV cols): 0.1223*** / 0.1126***. `UncPreCEO` 2/2 sig β>0 on cols 3 + 7 (UncAnsCEO DV cols): 0.1384*** / 0.1043***.
    - **Lagged_DV**: **8/8 sig β>0** (structural, rule 23 magnitudes allowed). Ind: 0.3333 / 0.6755 / 0.2986 / 0.5176. Firm: 0.1367 / 0.4185 / 0.1103 / 0.2626. Highest persistence on UncPreMgr ind 0.68 / firm 0.42; lowest on UncAnsCEO firm 0.11. UncPreMgr's high persistence is a structural feature of the DV — the scripted-presentation measure is very sticky, which may explain why macro monthly shocks don't register as easily.
    - **R² / N**: **R² 0.171 / 0.484 / 0.141 / 0.292 (ind)**; **0.041 / 0.186 / 0.030 / 0.084 (firm)**. Adj R² firm on UncPreMgr col 6 is 0.166 (positive) — unlike H11-series where Adj R² runs negative. Lagged_DV presence explains the R² lift. N: 74,013 / 75,142 / 59,676 / 60,503.
- **Reader-question**: Q4 (provisional).
- **Argument**: US EPU loads on 3 of 4 speech DVs under both FE strata; UncPreMgr is the sole non-responder. Primary IV `UncAnsMgr` hits 2/2 under both FE strata — the thesis's central speech measure covaries with monthly US EPU. The UncPreMgr null is a DV-heterogeneity observation, not a problem for the audit record.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 informative pattern — 6/8 sig β>0 with primary IV hit. UncPreMgr non-response logged at §5.26 DV-heterogeneity for contrast with H24b (which hits UncPreMgr 2/2). §5.23 broad external-loading instance.

### H24b — Global Economic Policy Uncertainty and Speech Uncertainty (GEPU)

- **DV**: Same 4 speech DVs in same column order as H24 (Mgr-QA / Mgr-Pre / CEO-QA / CEO-Pre)
- **N**: 74,013 / 75,142 / 59,676 / 60,503 per DV — **identical to H24** (same panel, same filters)
- **FE ladder**: Identical to H24 (Ind/Firm × Cal.Yr via other_effects)
- **Tail**: one-tailed β>0 for IV
- **Cluster**: two-way (firm, cal_yr_qtr)
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `log(GEPU)_t` (calendar-month match) **8/8 sig β>0 — ALL cells sig** under both FE strata. β: 0.0234*** / 0.0131* / 0.0178* / 0.0271*** (ind); 0.0242** / 0.0124* / 0.0212** / 0.0309*** (firm). **Broadest IV pattern in Q4 (ties H11-series 8/8).** All 4 DVs hit under both FE strata.
    - **Important note**: The project memory `project_h24_h24b_h25_macro_uncertainty.md` records that **prior to the Cal.Year FE restructure, GEPU produced uniformly NEGATIVE coefficients** — the "wrong-sign" was driven by year-to-year confounders. The current Cal.Year-FE-via-other_effects spec absorbs those confounders and reveals the positive relationship. This flip is a spec-design effect, not a data effect.
    - **Base controls**: Near-identical to H24 (within 0.0001-0.0002). `UncQue` 8/8 sig, `NegCall` 8/8 sig, `lnAssets` 4/8 sig β<0 ind-only, `TobinsQ` 2/8 sig β<0 (cols 1, 3 UncAns ind), `ROA` 7/8 sig (col 6 UncPreMgr firm null), `CashRatio` 3/8 sig β>0 (cols 2 ind + 5, 7 firm), `DivDummy` 3/8 sig β<0 (cols 2, 6, 8), `FirmMat` 3/8 sig (cols 2, 5, 7), `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig β>0 cols 1, 5 (0.1223*** / 0.1126***). `UncPreCEO` 2/2 sig β>0 cols 3, 7 (0.1384*** / 0.1043***). Near-identical to H24 (same panel).
    - **Lagged_DV**: **8/8 sig β>0**, near-identical to H24 values.
    - **R² / N**: **R² 0.171 / 0.484 / 0.141 / 0.292 (ind)**; **0.041 / 0.186 / 0.031 / 0.084 (firm)**. N identical to H24.
- **Reader-question**: Q4 (provisional).
- **Argument**: GEPU loads on every speech DV under every FE stratum. Unlike H24 (US EPU), GEPU hits UncPreMgr 2/2 under both FE strata (ind 0.0131* / firm 0.0124*). H24 vs H24b contrast: same panel, same spec, two different macro IVs, one hits UncPreMgr and one does not. US EPU → Mgr-Pre null, Global EPU → Mgr-Pre sig.
- **Verdict**: **KEEP**.
- **Rationale**: Rule 21 broadest informative pattern in Q4 (ties H11-series 8/8). The sign-flip from prior spec is a methodology-corrected artifact logged in project memory, not rescued here. §5.23 broad external-loading + §5.26 DV-heterogeneity contrast with H24.

### H25 — Geopolitical Risk and Speech Uncertainty (GPR)

- **DV**: Same 4 speech DVs in same column order as H24/H24b
- **N**: 74,013 / 75,142 / 59,676 / 60,503 per DV (same panel as H24/H24b)
- **FE ladder**: Identical to H24 / H24b
- **Tail**: one-tailed β>0 for IV
- **Cluster**: two-way (firm, cal_yr_qtr)
- **Key cell fact** (rule 24 full-row catalogue):
    - **Primary IV**: `log(GPR)_t` **1/8 sig** — only col 4 UncPreCEO ind+Cal.Yr β=0.0147* (p<0.10). All other 7 cells null. Col 1 UncAnsMgr ind β=-0.0112 null; col 2 UncPreMgr ind β=0.0073 null; col 3 UncAnsCEO ind β=-0.0059 null; col 5 UncAnsMgr firm β=-0.0119 null; col 6 UncPreMgr firm β=0.0067 null; col 7 UncAnsCEO firm β=-0.0058 null; col 8 UncPreCEO firm β=0.0118 null (close to threshold but p>0.10, per rule 22 the direction of a null cell is not evidence).
    - **Base controls**: Near-identical to H24 / H24b (same panel). `UncQue` 8/8 sig, `NegCall` 8/8 sig, `lnAssets` 4/8 sig β<0 ind-only, `TobinsQ` 2/8 sig β<0 ind UncAns, `ROA` 7/8 sig β>0 (col 6 null), `CashRatio` 3/8 sig β>0 (col 2 ind + 5, 7 firm), `DivDummy` 3/8 sig β<0 (cols 2, 6, 8), `FirmMat` 3/8 sig (cols 2, 5, 7), `EarnVol` 0/8 null.
    - **Same-call Pre controls**: `UncPreMgr` 2/2 sig β>0 (cols 1, 5). `UncPreCEO` 2/2 sig β>0 (cols 3, 7).
    - **Lagged_DV**: **8/8 sig β>0**, near-identical to H24/H24b.
    - **R² / N**: R² 0.171 / 0.484 / 0.141 / 0.292 (ind); 0.041 / 0.186 / 0.030 / 0.084 (firm). N same as H24/H24b.
- **Reader-question**: Q4 (provisional).
- **Argument**: GPR does not meaningfully drive speech uncertainty after absorbing year-level confounders via Cal.Year FE. The one sig cell (col 4 UncPreCEO ind β=0.0147*) is near the threshold and industry-FE only; not a pattern. Near-null status parallels H7 (1/48), H14 (1/48), H14d (1/48), H16 (0/48) — fifth near-null suite in the audit.
- **Verdict**: **KEEP** (near-null flag).
- **Rationale**: Rule 21 KEEP default (1 sig cell technically informative). Practical interpretation: GPR is a poor driver of speech uncertainty — useful as a null finding for construct-validation narrative (not every macro-uncertainty proxy loads on the IV). Logged at §5.27 fifth-near-null-instance. User DROP override available at synthesis.

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

### 5.13 CEO coverage gap explains H1 vs H1.1/H1.1b/H1.2 sample differences (2026-04-15)

- **Observation**: H1.1 and H1.1b have N=73,707 vs H1's N=65,128 — H1.1 is LARGER than its parent H1. Initially looked like a panel-drift smoking gun, but empirical verification + runner source reading shows it is runner-side complete-case filtering, not panel drift.
- **Empirical verification** (on `h1_cash_holdings_panel.parquet`):
    - Whole panel: 112,968 calls
    - `UncAnsMgr` non-missing: 108,517 (96.1%)
    - **`UncAnsCEO` non-missing: 90,947 (80.5%)** — CEO bottleneck
    - `UncPreMgr` non-missing: 111,151 (98.4%)
    - **`UncPreCEO` non-missing: 91,169 (80.7%)**
    - Main sample: 88,205 (post financials + utilities exclusion)
    - Main + 4-IV non-null: 70,086
    - Main + `UncAnsMgr` non-null: 84,729
    - **Gap = ~14,643 calls (~17% of Main sample) lost to CEO speaker ID missing**
    - Main + 4-IV + base controls + CashRatio: 67,000 → H1 actual 65,128 (further loss to Lagged_DV + min-calls-per-firm)
    - Main + Mgr-only + base controls + CashRatio: 80,238 → H1.1 actual 73,707 (further loss to TSIMM coverage + centering)
- **Runner source evidence**:
    - Both `run_h1_cash_holdings.py` and `run_h1_1_cash_tsimm.py` load **the same parquet file** (`h1_cash_holdings_panel.parquet`). Zero panel drift possible between H1 and H1.1.
    - H1 runner (`run_h1_cash_holdings.py` line 86-90): `KEY_IVS = ["UncAnsCEO", "UncPreCEO", "UncAnsMgr", "UncPreMgr"]`. Line 311: `complete_mask = df[required].notna().all(axis=1)` — requires all 4 IVs non-null.
    - H1.1 runner (`run_h1_1_cash_tsimm.py` line 74-76, 170-176): `IV = "UncAnsMgr"`. Loads only `UncAnsMgr` from the panel (NOT the other 3 IVs). Merges TNIC3 TSIMM from `inputs/TNIC3HHIdata/TNIC3HHIdata.txt`. Complete-case filter requires only `UncAnsMgr` + TSIMM non-null.
- **Explanation of H1 vs H1.1/H1.1b/H1.2 sample gap**:
    - H1 (65,128) is CEO-bottlenecked because the 4-IV complete-case filter drops the ~17% of calls with missing CEO speaker ID.
    - H1.1/H1.1b (73,707) are Mgr-only — no CEO bottleneck. They lose ~6.5K to TNIC3 TSIMM coverage.
    - H1.2 (67,544) is Mgr-only + rating coverage — loses ~6.2K more than H1.1 to rating data filter (IG/BelowIG/Unrated classification requirement).
- **Generalization**: Every Q1 4-IV suite uses the same `KEY_IVS = {UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO}` set and complete-case filter. **Every Q1 4-IV regression is CEO-bottlenecked** by the same ~17% missingness. Any Mgr-only moderation suite runs on a broader sample than its 4-IV parent.
- **Implication for cross-suite comparisons**:
    - H1.1 main-effect re-confirmation of H1 is on a LARGER sample (73.7K vs 65.1K) — **stronger H1 evidence**, not weaker.
    - Cross-suite sample differences should be decomposed into (a) panel-coverage differences, (b) IV-set differences, (c) merged-data-source differences. Only (a) could indicate panel drift.
- **Panel-consistency TODO status**: H1 vs H1.1 is resolved (same panel file, runner-side filter). Whether the OTHER panel builders (H4, H12, H13, etc.) produce bit-identical values for shared variables when filtered to common `(gvkey, fyearq)` keys is still open. Deferred TODO remains in `memory/project_phase5_audit_progress.md`.
- **Status**: Factual observation, not a narrative. Use this to interpret sample differences during synthesis.
- **Loaded from**: Q2 batch 1 audit (H1.1 cataloguing), runner source reads, empirical panel analysis 2026-04-15.

### 5.14 UncPreMgr full-ladder survival on analyst dispersion (H5) — §5.5 broken at scale

- **Observation**: H5 DISP has **UncPreMgr 12/12 sig β>0** across both DVs (contemp + lead) and all 6 FE ladders (Ind+Yr / Firm+Yr / Ind+Yr+Ext / Firm+Yr+Ext / Ind+YQ+Ext / Firm+YQ+Ext). This is the **first full-ladder UncPreMgr survival in the audit**. §5.5 (cross-sectional-only UncPreMgr on cash/payout/payer) was first broken by H17 (7/12 including 3 firm-FE contemp cells). H5 breaks it further at 12/12 — every cell including firm-FE. UncAnsMgr on H5 is 6/12 sig all industry-FE (cross-sectional only, matching the original §5.5 pattern shape). CEO measures both null.
- **Status**: Cross-suite factual pattern. Per `feedback_ceo_noisy_mgr_central.md`, UncPreMgr is a secondary measure with scripted/IR-vetted language concerns. The full-ladder survival on an analyst-dispersion DV is structurally different from the original §5.5 cash/payout/payer pattern — here UncPreMgr goes firm-FE AND industry-FE with both contemp and lead DVs. Do not interpret here; revisit at synthesis. Two possible readings (synthesis only): (a) analyst market is listening to scripted-presentation uncertainty at least as strongly as Q&A uncertainty; (b) DISP is mechanically correlated with prepared-segment textual features.
- **Loaded from**: H5 (2026-04-15).

### 5.15 UncAnsCEO contemp-all-FE on BGT 25-day Amihud (H7c) — deepest CEO inversion in audit

- **Observation**: H7c BGT 25-day Amihud has **UncAnsCEO 6/6 sig β>0 on contemp cells across all FE ladders including 3 firm-FE cells (cols 2, 4, 6)**. Lead horizon 0/6 null. Primary `UncAnsMgr` 0/12 null. `UncPreMgr` 1/12 sig (lead only). **Deepest CEO-channel signal in the audit so far** — breadth (6/6 contemp) + firm-FE depth (3 cells). §5.1 flagged H1 CEO-lead > Mgr-lead breadth inversion on cash (4 cells, lead horizon, all industry-FE); §5.7 flagged H13 capex CEO firm-FE contemp (3 cells); §5.15 (H7c) is the deepest: 6 contemp cells across both FE strata, with 3 firm-FE survivors, on a market-liquidity DV.
- **Status**: Measurement-concerns flag per `feedback_ceo_noisy_mgr_central.md`. CEO-carrying-signal-that-Mgr-does-not is now seen three times: §5.1 (H1 cash lead breadth) / §5.7 (H13 capex contemp firm-FE strata split) / §5.15 (H7c BGT Amihud contemp all-FE). Each instance goes deeper than the last. Do not rescue with a "CEO speaks through BGT window" or "25-day window captures CEO-specific market impact" narrative. Log only; revisit at synthesis. Possible interpretive frames deferred: (a) 25-day window is longer than 3-day, may capture a different information-absorption horizon where CEO attributes load; (b) market-side DVs respond to CEO-specific signaling more than balance-sheet DVs. Both are synthesis decisions.
- **Loaded from**: H7c (2026-04-15).

### 5.16 Level-vs-change liquidity DV structural contrast (H7 vs H7b/H7c)

- **Observation**: H7 (DeltaILLIQ = change variable, ΔAmihud[+1,+3]-[-3,-1]) has **R² 0.001–0.005** and **Lagged_DV 0/12 null** (complete mean reversion) — the model has near-zero explanatory power on change-variable illiquidity. H7b (PostCallAmihud level [+1,+3]) has **R² 0.39–0.55** and **Lagged_DV 12/12 sig ~0.59–0.72** — strong persistence on the same panel, same IVs, same FE ladders. H7c (BGT 25-day Amihud level [0,+25]) has **R² 0.45–0.62** and **Lagged_DV 12/12 sig ~0.66–0.79** — also strong persistence. IVs also split: H7 is 1/48 sig (near-null); H7b is 2/12 sig UncPreMgr industry-FE with ExtCtrl only; H7c is 6/12 UncAnsCEO contemp all-FE (§5.15).
- **Status**: Structural property of the DV class, not an effect claim. Change variables (H7 ΔAmihud) are dominated by sampling noise at the 3-day post-call window; level variables (H7b PostCallAmihud, H7c BGT 25-day Amihud) carry signal. Any liquidity-channel narrative should use level DVs, not the change DV. Parallel in structure to §5.10 positive-vs-negative-persistence DV class distinction (stock vs flow DVs). **Cross-cluster implication**: H14 family (bid-ask spread) likely has the same change-vs-level split — watch for it during H14 dialogue. H7 near-null DROP-flag pending user decision (parallel to H16 R&D 0/48 decision).
- **Loaded from**: H7 + H7b + H7c (2026-04-15).

### 5.17 Small-N firm-year / special-sample panel class (H22 + H20b precedent)

- **Observation**: H22 EquityDelayCon_lead is a firm-year panel with N = 8,564–8,621 — same small-sample class as H20b ChangDebtChoice (3,404–13,666, Chang external-financing-event restricted sample). Both substantially smaller than the call-level Q1/Q2/Q3 panels (~60–70K). Both have primary IV `UncAnsMgr` null. H20b was DROPped per rule 21 "empirically uninterpretable" (opposite-direction Pre split + Chang restriction). H22 has 2/4 UncAnsCEO industry-FE sig β>0 and no opposite-direction splits — slightly cleaner than H20b but still small-N firm-year with near-zero firm-FE R² (0.04). H5 IBES Detail panel (18–20K) is intermediate in size between Main call-level and the small-N class — not quite in this flag zone but worth noting for generalizability sweeps.
- **Status**: Factual observation on sample-size heterogeneity in the audit. Small-N / special-sample suites create generalizability questions distinct from the main-panel suites — different sampling frames → different inference populations. User DROP override for H22 remains on the table if small-N firm-year generalizability is ruled out at synthesis (parallel to H20b precedent). For any future small-panel suites (H18b logit, H21 SEC letters, H23 firm-year TSIMM, H24/H24b/H25 macro-IV suites) same consideration applies. Revisit at end-of-audit.
- **Loaded from**: H22 (2026-04-15). Precedent: H20b (2026-04-15, §5.10 + DROP verdict).

### 5.18 Liquidity-family CEO-inversion structures + BGT 25-day horizon split (H7c/H14b/H14c) + first UncPreCEO sig (H14c)

- **Observation**: After Q3 batch 2 (H7d/H7e/H14/H14b/H14c), the liquidity family carries a growing catalogue of CEO-inversion sub-patterns plus a new UncPreCEO sig pattern. Catalogue:
    - **H7c BGT 25-day Amihud**: `UncAnsCEO` **6/6 contemp** cells sig β>0 all FE (incl 3 firm-FE). Lead 0/6 null. (Logged in §5.15.)
    - **H14b 3-day post-call spread level**: `UncAnsCEO` **3/3 firm-FE lead** cells sig β>0 (cols 8, 10, 12). Contemp 0/6 null. Lead-ind 0/3 null. Novel: first lead-horizon firm-FE-only CEO pattern.
    - **H14c BGT 25-day spread**: `UncAnsCEO` **5/6 lead** cells sig β>0 (cols 7-10, 12; 2 ind + 3 firm). Contemp 0/6 null. **OPPOSITE horizon to H7c's 6/6 contemp on Amihud — same BGT 25-day post-call window, different market DV, opposite horizon loading.**
    - **H14c also has the first UncPreCEO sig pattern in the audit**: 3/3 contemp cells sig β>0 (cols 1, 2, 4 — ind+yr / firm+yr / firm+yr+ext). All prior suites (H1–H14b, H22, H5, H7–H7e) had UncPreCEO 0/12 null.
- **Cross-catalogue with prior CEO-inversion observations**:
    - §5.1 H1 cash `CashRatio_lead`: `UncAnsCEO` 4/6 lead cells sig β>0 — all industry-FE (firm-FE 0/3).
    - §5.7 H13 capex `Capex`: `UncAnsCEO` 3/3 firm-FE contemp cells sig β>0.
    - §5.15 H7c BGT Amihud (above).
    - H14b (above).
    - H14c (above).
    - Five distinct CEO-inversion signatures now seen across audit. Each has a different horizon × FE combination (lead-ind, contemp-firm, contemp-all-FE, lead-firm-only, lead-all-FE).
- **Status**: Cross-suite factual pattern. Per `feedback_ceo_noisy_mgr_central.md`, UncAnsCEO / UncPreCEO are secondary measures with performative / IR-vetted concerns; CEO-inversion instances are measurement-concerns flags, not positive hypothesis channels. Do NOT build a "CEO speaks through market-liquidity DVs" rescue narrative. The growing catalogue is the record; interpretation is synthesis-time. Two notable sub-observations deferred:
    - **H7c vs H14c horizon split** on the same BGT 25-day window: Amihud contemp / Spread lead. Possible synthesis question: which liquidity DV responds at which horizon to CEO language? Not answered here.
    - **H14c first UncPreCEO sig pattern**: after 19 prior suites with UncPreCEO 0/12 null in each, H14c has 3/12 sig β>0 contemp on a BGT 25-day post-call spread DV. This is the first empirical deviation from the "UncPreCEO baseline null" pattern. Synthesis question deferred.
- **Loaded from**: H7c (§5.15 existing) + H14b + H14c (2026-04-15, Q3 batch 2). Incorporates H1 §5.1 + H13 §5.7 catalogue cross-reference.

### 5.19 §5.16 level-vs-change confirmed on bid-ask spread family (H14/H14b/H14c)

- **Observation**: §5.16 documented the level-vs-change R² split on H7 (DeltaILLIQ 0.001–0.005 / 0/12 sig Lagged_DV) vs H7b/H7c (PostCallAmihud and BGTLevel_Amihud, R² 0.39–0.62 / 12/12 sig Lagged_DV). Q3 batch 2 replicates the split on bid-ask spreads:
    - **H14 DSPREAD change [+1,+3]-[-3,-1]**: R² 0.001–0.009; Lagged_DV mostly near-zero; **1/48 sig** (near-complete null, parallel to H7 1/48). Near-null twin of H7.
    - **H14b PostCallSpread level [+1,+3]**: R² 0.29–0.56; Lagged_DV 12/12 sig ~0.60 ind / 0.43 firm; 8/48 sig.
    - **H14c BGTLevel_Spread [0,+25]**: R² 0.56–0.78; Lagged_DV 12/12 sig ~0.75 ind / 0.65 firm; 14/48 sig (richest liquidity suite).
    - **H7d BGTDelta_Amihud 25-day change**: R² 0.02–0.04; Lagged_DV 12/12 sig ~0.15–0.18; 5/48 sig. **Mid-horizon change variant carries some signal — nuances the pure level-vs-change split.**
    - **H7e BGTAvg_Amihud 51-day symmetric average**: R² 0.48–0.65; Lagged_DV 12/12 sig ~0.80/0.70 (highest persistence in audit); 2/48 sig (only UncPreMgr cross-sectional cells). **51-day symmetric includes pre-call window — does NOT replicate H7c's 6/6 contemp UncAnsCEO pattern**, suggesting the CEO signal is specific to the post-call-only window structure.
- **Status**: Structural property of the DV class — change variables on short (3-day) windows are dominated by sampling noise and carry no IV signal; level variables and longer-window change variables carry signal. Any liquidity-channel narrative should use level DVs. H7 and H14 remain near-null flagged; user DROP override available for both.
- **Refinement to §5.16**: The hypothesis "level vs change" is refined to "level vs short-window change vs longer-window change". Short-window change (H7, H14) is near-null; longer-window change (H7d 25-day) carries modest signal; levels (H7b/H7c/H7e/H14b/H14c) carry full signal. Window length interacts with change/level structure.
- **Loaded from**: Q3 batch 2 (2026-04-15). Extends §5.16.

### 5.20 BGT 25-day window × DV asymmetry (H7d/H14d + H7e/H14e cross-DV signal divergence)

- **Observation**: The BGT 25-day post-call window produces DIFFERENT IV signal strength across market-liquidity DVs (Amihud illiquidity vs Lee 2016 bid-ask spread), even on the same panel and same window definition:
    - **25-day change variants** ([+1,+25]-[-25,-1]):
        - **H7d BGTDelta_Amihud**: 5/48 sig (UncPreCEO 4/12 lead horizon cluster + UncAnsMgr 1/12 contemp). R² 0.02–0.04.
        - **H14d BGTDelta_Spread**: 1/48 sig (UncAnsCEO 1/12 col 8 only). R² 0.002–0.012.
        - **Gap**: Amihud carries modest 25-day change signal (primarily UncPreCEO lead-horizon cluster); Spread 25-day change is near-null. Same window, same panel, same IV definitions — different DV sensitivity.
    - **51-day symmetric average variants** ([-25,+25]):
        - **H7e BGTAvg_Amihud**: 2/48 sig (UncPreMgr 2/12 ind+ext only). **Does NOT replicate H7c's 6/6 contemp UncAnsCEO pattern** — the 51-day symmetric window (including pre-call) loses the H7c signal entirely.
        - **H14e BGTAvg_Spread**: 9/48 sig (UncPreCEO 3/3 contemp same as H14c + UncPreMgr 3 + UncAnsCEO 2 + UncAnsMgr 1). **Partially preserves the H14c pattern** — UncPreCEO 3/3 contemp cells survive the pre-call inclusion.
        - **Gap**: 51-day symmetric window LOSES the H7c Amihud CEO signal but PRESERVES the H14c spread UncPreCEO signal. DV-specific window sensitivity.
- **Status**: Cross-DV factual pattern. Per `feedback_ceo_noisy_mgr_central.md`, do not build "Amihud is more responsive than Spread to CEO-change language" or "Spread UncPreCEO is more robust to pre-call inclusion than Amihud UncAnsCEO" narratives here. Log only. At synthesis the DV-window-sensitivity question is relevant: **different liquidity DVs (Amihud vs bid-ask spread) have DIFFERENT underlying information absorption structures even when measured on the same panel with the same post-call window**. Possible implications (deferred): (a) Amihud is price-impact-based, Spread is transaction-cost-based — different channels may drive each; (b) pre-call symmetry affects different channels differently. Both synthesis decisions.
- **Refinement to §5.16 / §5.19**: The level-vs-change hierarchy must also be decomposed by liquidity DV. Spread changes are always near-null regardless of window (H14 3-day 1/48, H14d 25-day 1/48); Amihud changes carry some signal at 25-day window (H7d 5/48). Levels are relatively more stable across DVs but still show DV-specific CEO horizon patterns (§5.18 H7c contemp vs H14c lead).
- **Loaded from**: Q3 batch 3 (2026-04-15). Extends §5.16/§5.19.

### 5.21 UncPreCEO recurring sig pattern on information-channel DVs (H14c, H14e, H21)

- **Observation**: §5.18 noted H14c as the **first UncPreCEO sig pattern in the audit** (3/3 contemp cells cols 1, 2, 4 ind+yr / firm+yr / firm+yr+ext). After Q3 batch 3:
    - **H14c (BGTLevel_Spread 25-day [0,+25])**: UncPreCEO 3/3 contemp cells sig β>0.
    - **H14e (BGTAvg_Spread 51-day [-25,+25])**: UncPreCEO 3/3 contemp cells sig β>0 — same cols (1, 2, 4) as H14c, preserved under 51-day symmetric window.
    - **H21 (SEC_Letters_fwd count)**: UncPreCEO **3/6 sig β>0 — cols 1, 3, 5 industry-FE only** (firm-FE 0/3 null). Different FE pattern from H14c/H14e (H21 is ind-only contemp; H14c/H14e include firm-FE).
- **Status**: Cross-suite factual pattern. UncPreCEO is a secondary measure per `feedback_ceo_noisy_mgr_central.md` (known performative / scripted concerns); before this batch it was 0/12 null in 19 prior suites. Now three suites show UncPreCEO sig in contemp cells — all three on information / market-side DVs (bid-ask spread levels + SEC letter count). Do NOT rescue with a "CEO scripted opening carries information about SEC risk" narrative. Log only; revisit at synthesis. Two possible readings deferred: (a) scripted CEO-prepared remarks correlate with heightened information-absorption by the market and/or SEC follow-up attention; (b) the sig cells are contemp-ind-FE only (except H14c firm col 2, 4), consistent with §5.5 cross-sectional loading interpretation extended to CEO-Pre.
- **Cross-reference with prior UncPre patterns**: UncPreMgr has been seen on cash/payout/payer (§5.5 cross-sectional loading) and H5 analyst dispersion (§5.14 full-ladder including firm-FE) and H17 repurchases (§5.9 partial firm-FE survival). Now UncPreCEO adds a third Pre-measure sub-pattern on information DVs. The "Pre measures carry information content that Ans measures do not" question is a synthesis hypothesis.
- **Loaded from**: H14c (Q3 batch 2, 2026-04-15 — first instance) + H14e + H21 (Q3 batch 3, 2026-04-15).

### 5.22 CCCL DV class: near-zero LPM R² + logit robustness + UncPreMgr-only signal (H18, H18b)

- **Observation**: H18 LPM and H18b Logit both test the same DV (`CCCL` = binary indicator of SEC comment letter received) on the same panel. Findings:
    - **H18 LPM**: R² **0.000–0.001 essentially zero**. Primary `UncAnsMgr` 0/6 null. Only `UncPreMgr` 2/6 sig β>0 — cols 1, 2 (ind+yr + firm+yr, no extended controls). Cols 3-6 with ExtCtrl null. Extended controls (RDSales cols 3, 5 ind β<0; DailyVola cols 4, 6 firm β<0) absorb the UncPreMgr signal. Lagged_DV 3/6 sig firm-FE β<0 (mean reversion on binary DV).
    - **H18b Logit** (ind+yr only, 2 cols — logit statsmodels does not support firm FE): Pseudo R² 0.089 / 0.090 (much higher than LPM 0.000). `UncPreMgr` 2/2 sig β>0 — col 1 + col 2 (ind+yr + ind+yr+ext). **Both cells** sig including with ExtCtrl, unlike H18 LPM where ExtCtrl absorbed the ind-FE signal. Logit recovers the signal that LPM with firm FE loses.
- **Status**: Two structural observations on the CCCL DV class:
    - **(a) Near-zero LPM R²**: binary DV with low base rate (rare event) is inherently hard for LPM to fit. CCCL H18 R² 0.000–0.001 is the second-worst in the audit after H16 R&D 0.004–0.007 firm-FE. Logit pseudo R² 0.09 recovers explanatory power that LPM cannot.
    - **(b) Robustness to functional form**: UncPreMgr is sig on CCCL under both LPM (ind-FE, no-ext, cols 1, 2) and Logit (ind-FE, both cols, with and without ext). CEO measures null under both. UncAnsMgr null under both. **The CCCL signal is robust to LPM↔Logit but not robust to firm FE or (in LPM) extended controls.** Limited-scope signal.
- **Cross-reference**: H21 (SEC_Letters_fwd count DV) on same panel has UncPreCEO 3/6 ind-FE sig and UncPreMgr 0/6 null. Binary receipt (H18/H18b) loads on UncPreMgr; count (H21) loads on UncPreCEO. Different SEC-risk language markers load on different information-content DVs. Synthesis observation deferred.
- **Loaded from**: H18 + H18b (2026-04-15, Q3 batch 3). Cross-reference: H21 (same batch).

### 5.23 Q4 external-uncertainty broad-loading + tiny-magnitude on speech DVs (H11 family + H24b)

- **Observation**: Five Q4 suites exhibit broad positive loading of external-uncertainty IVs on speech-uncertainty measures:
    - **H11** `PRisk_t`: 8/8 sig β>0 all 4 speech DVs × both FE strata (β=0.0001–0.0003). Tiny magnitudes; firm-FE Adj R² NEGATIVE (-0.002 to -0.006).
    - **H11-Lag1** `PRisk_{t-1}`: 8/8 sig β>0 same pattern (firm-FE cells round to β=0.0000 at 4dp).
    - **H11-Lag2** `PRisk_{t-2}`: 8/8 sig β>0, col 6 (firm UncAnsCEO) drops to ** from ***.
    - **H24** `log(US EPU)_t`: 6/8 sig β>0 — UncPreMgr 0/2 null, all other DVs 2/2 sig.
    - **H24b** `log(GEPU)_t`: **8/8 sig β>0** — all 4 DVs × both FE strata; **broadest macro-IV signal in the audit**. Inverts pre-restructure wrong-sign GEPU finding (Cal.Year FE via other_effects absorbs year-level confounders).
    - **H23** `z(log(TSIMM))`: 4/8 sig β>0 — industry-FE heavy; firm-FE only via UncPreCEO col 8 (§5.24).
    - **H25** `log(GPR)_t`: 1/8 sig only (§5.27 near-null class).
- **Observation (tiny-magnitude subset)**: H11 / H11-Lag1 / H11-Lag2 all show statistically significant 8/8 coefficients with β ≈ 0.0001–0.0003. At 112K-call N, p-values cross α=0.01 easily even when the coefficient's within-firm explanatory contribution is near zero (3 of 4 firm-FE Adj R² cells negative). This is the classic "cheap p-values on very small effects" pattern the audit philosophy (`DECISIONS.md §1.2`) warns about. **Load-bearing for Q5 economic-magnitude sweep**: the H11 external-loading finding is statistically robust but economically marginal in within-firm terms; the construct-validation narrative needs to be built on the H24 / H24b within-firm magnitudes (β≈0.01–0.03, ≈100× larger than PRisk) rather than the H11 magnitudes.
- **Status**: Informative empirical record for the post-audit synthesis. Tiny magnitudes are a downstream Q5 concern; they do not reduce the audit-record breadth. The cross-cluster implication is that **speech uncertainty is partly a reflection of external (political, competitive, macro) uncertainty exposure** — the question is whether there is residual speech-specific variation after absorbing those, which is the Q4 construct-validation reader question in its provisional form.
- **Loaded from**: H11 / H11-Lag1 / H11-Lag2 / H23 / H24 / H24b / H25 (2026-04-16, Q4 batch).

### 5.24 UncPreCEO fourth sig instance — H23 extends §5.21 from Q3 information DVs to Q4 construct validation

- **Observation**: H23 col 8 (firm-FE UncPreCEO DV) has `z(log(TSIMM))` β=0.0302*** sig β>0 — making it the **fourth suite** in the audit with a significant UncPreCEO pattern. Prior instances (§5.21):
    - **H14c** — UncPreCEO 3/3 contemp ind-FE β>0 on BGT 25-day spread level
    - **H14e** — UncPreCEO 3/3 contemp ind-FE β>0 on BGT 51-day symmetric spread average
    - **H21** — UncPreCEO 3/3 ind-FE β>0 on SEC comment letter count
    - **H23** — UncPreCEO 2/2 (ind col 4 + **firm col 8**) β>0 on TSIMM firm-year (new 2026-04-16)
- **Status**: The UncPreCEO pattern now spans Q3 (information/market-side DVs) and Q4 (construct validation / firm-year reverse direction). H23 is the first instance with **firm-FE survival on UncPreCEO**; prior 3 were all ind-FE only. Direction (β>0) is consistent across all 4 instances. Worth noting: H23's UncPreCEO firm-FE survival is on a firm-year panel (~18K) — the sample is restricted, which may contribute to the firm-FE identification power.
- **Status**: Not a mechanism claim — logged as a measurement-pattern observation. UncPreCEO is a secondary measure per `feedback_ceo_noisy_mgr_central.md`; the pattern is catalogued, not theorized. §5.21 + §5.24 together are the UncPreCEO observation thread for synthesis review.
- **Loaded from**: H23 (2026-04-16). Cross-reference: §5.21 (Q3 cluster).

### 5.25 Q4 structural split — firm-level construct IVs (no Lagged_DV) vs macro-monthly IVs (Lagged_DV)

- **Observation**: Q4 suites split into two spec classes on Lagged_DV inclusion:
    - **No Lagged_DV (firm-level construct IVs)**: H11 / H11-Lag1 / H11-Lag2 (PRisk) + **H23** (TSIMM firm-year). These runners use the form `UncAnsMgr ~ IV + UncQue + NegCall + base_controls [+ same-call Pre for Ans DVs] + EntityEffects + TimeEffects`. No DV persistence term.
    - **Has Lagged_DV (macro-monthly IVs)**: H24 (US EPU) / H24b (GEPU) / H25 (GPR). These runners include `Lagged_DV` as a control, which shows 8/8 sig β>0 values 0.11–0.68 (highest on UncPreMgr ind 0.68 / firm 0.42, lowest on UncAnsCEO firm 0.11).
- **Status**: The split tracks **IV type**, not arbitrary spec choice. Firm-level construct IVs (PRisk, TSIMM) run without Lagged_DV; macro-monthly aggregated IVs (EPU, GEPU, GPR) include Lagged_DV. The speech DVs (UncAnsMgr etc.) are known to be persistent within firm per H24's Lagged_DV cells (0.11–0.68 range showing substantial within-call DV autocorrelation). H11 / H23's tiny β and negative firm-FE Adj R² are partly a consequence of running an IV on a DV whose own lag is unabsorbed. **Comparison of H11 PRisk or H23 TSIMM magnitudes to H24/H24b macro magnitudes is not apples-to-apples** because the two classes differ on Lagged_DV inclusion. This is a Q5 / synthesis concern, not a mid-audit rescue.
- **Status**: Not rescue narrative — factual spec-difference observation. Logged for synthesis. Worth investigating at synthesis: whether adding Lagged_DV to H11/H23 specs (robustness check) would attenuate the 8/8 and 4/8 IV patterns, given the high DV persistence.
- **Loaded from**: H11 / H11-Lag1 / H11-Lag2 / H23 / H24 / H24b / H25 (2026-04-16, Q4 batch). Corrected from initial draft after advisor verification 2026-04-16 — H23 was initially (incorrectly) listed as having Lagged_DV.

### 5.26 Macro-IV DV-heterogeneity — H24 vs H24b differ only on UncPreMgr response

- **Observation**: H24 and H24b run on the same panel (74,013 / 75,142 / 59,676 / 60,503 per DV), same spec (ind/firm × Cal.Year FE via other_effects, two-way clustering), same sample filters. Only the IV differs (US EPU vs GEPU). Result:
    - **H24** (US EPU): Mgr-QA 2/2 sig, Mgr-Pre 0/2 null, CEO-QA 2/2 sig, CEO-Pre 2/2 sig. 6/8 total.
    - **H24b** (GEPU): Mgr-QA 2/2 sig, Mgr-Pre 2/2 sig, CEO-QA 2/2 sig, CEO-Pre 2/2 sig. 8/8 total.
    - The only DV that differs is `UncPreMgr`: null under US EPU, sig under GEPU.
- **Status**: H25 (GPR) on the same panel hits 0/2 on UncPreMgr. So UncPreMgr's macro responsiveness appears highest on GEPU, null on US EPU + GPR. Pattern: the scripted-presentation manager measure responds to global EPU but not to domestic EPU or GPR.
- **Status**: Logged as factual DV-heterogeneity observation. Not rescued — the differential response is an empirical fact. Possible readings at synthesis: (i) international-exposure channel of scripted guidance responds to global but not domestic EPU; (ii) UncPreMgr is noisy and responds sporadically to the broadest IV. Decision deferred to synthesis.
- **Loaded from**: H24 vs H24b contrast (2026-04-16, Q4 batch).

### 5.27 Near-null suite class expanded — fifth instance (H25 GPR on speech DVs)

- **Observation**: Five suites now catalogued with "near-null" patterns (≤1/N total sig cells and R² near zero):
    - **H7** DeltaILLIQ 3-day change: 1/48 sig, R² 0.001–0.005 (§5.16)
    - **H14** DSPREAD 3-day change: 1/48 sig, R² 0.001–0.009 (§5.19)
    - **H14d** BGTDelta_Spread 25-day: 1/48 sig, R² 0.002–0.012 (§5.20)
    - **H16** RDSales (Q1): 0/48 sig, R² ≈0.005 firm-FE lead (complete-null; §5.8)
    - **H25** `log(GPR)_t` macro (NEW): 1/8 sig, R² same as H24/H24b panel ~0.17 / 0.48 / 0.14 / 0.29 ind / 0.04 / 0.19 / 0.03 / 0.08 firm (**but this R² is driven by controls and Lagged_DV, NOT by GPR — GPR contributes near-nothing beyond the controls**)
- **Status**: Near-null is KEEP-default per rule 21 (1 sig cell is informative), but at synthesis the user has DROP override available. Five near-null suites cluster observations:
    - H7 / H14 / H14d share a structural feature: all three are CHANGE variables (post-minus-pre spread/illiquidity) on thin-daily-data DVs where change variants mean-revert (§5.16 / §5.19 / §5.20).
    - H16 is a DIFFERENT structural reason: R&D is a sticky flow, near-zero firm-FE variation within quarters over short horizons.
    - H25 is a DIFFERENT structural reason again: GPR is a geopolitical measure that does not meaningfully drive call-level speech uncertainty after Cal.Year FE absorbs year-level confounders. Contrast with H24 / H24b on the same panel / same spec (6/8 and 8/8 sig respectively) — confirms this is about GPR specifically, not the spec.
- **Status**: The near-null class is an important finding for the thesis — it delineates WHERE speech uncertainty does NOT correlate with external measures. Provides honest non-cherry-picked reporting for construct validation. Do not DROP as a group; user decision at synthesis.
- **Loaded from**: H25 (2026-04-16). Cross-reference: §5.8 (H16), §5.16 (H7), §5.19 (H14), §5.20 (H14d).

---

## Appendix A. Carry-over pipeline bug list (code fixes already applied, historical reference)

Recorded in git commits c46e655 → bf9f366 (2026-04-14 architectural rewrite + LaTeX audit fixes). Detailed record in `memory/project_draft_playing_it_safe.md` and `memory/project_completed_milestones.md`. Not reproduced here — the audit proceeds assuming these are stable.
