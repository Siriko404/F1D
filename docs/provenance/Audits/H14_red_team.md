# H14 Second-Layer Red-Team Audit

**Suite ID:** H14
**Red-Team Auditor:** Independent (fresh context)
**Date:** 2026-03-15
**First-Layer Audit Under Review:** `docs/provenance/H14.md` (dated 2026-03-13)

---

## A. Red-Team Bottom Line

The first-layer audit is a detailed, well-structured document that correctly identifies the suite boundary, model family, variable dictionary, and dependency chain. It flagged several real issues (DV kurtosis, placebo significance, PreCallSpread winsorization, duplicate index dedup). However, it contains **multiple factual errors in its distribution statistics table**, **a false claim about CCM LINKPRIM filtering** in CRSP-dependent builders, **inflated robustness regression counts** (12 of 174 are duplicates), and **materially underweights the placebo failure** — the single most important finding for H14's credibility. The distribution errors suggest the audit's verification log, while extensive, was not fully cross-checked against its narrative claims.

**Overall grade for the first audit: PARTIALLY RELIABLE**

**Verdict on the suite as implemented: SALVAGEABLE WITH MAJOR REVISIONS**

The first audit **understated risk** on the placebo test failure (calling it "Medium" when it should be thesis-blocking) and **overstated confidence** in the distribution statistics it reported.

---

## B. Scope and Objects Audited

| Item | Path / Identifier |
|------|-------------------|
| Suite ID | H14 |
| Suite entrypoint | `src/f1d/econometric/run_h14_bidask_spread.py` |
| Panel builder | `src/f1d/variables/build_h14_bidask_spread_panel.py` |
| First-layer audit | `docs/provenance/H14.md` |
| BidAskSpreadChangeBuilder | `src/f1d/shared/variables/bidask_spread_change.py` |
| EarningsSurpriseBuilder | `src/f1d/shared/variables/earnings_surprise.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` |
| SizeBuilder | `src/f1d/shared/variables/size.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` |
| Panel artifact | `outputs/variables/h14_bidask_spread/2026-03-13_031834/h14_bidask_spread_panel.parquet` |
| Model diagnostics (audit ref) | `outputs/econometric/h14_bidask_spread/2026-03-13_032702/model_diagnostics.csv` |
| Model diagnostics (latest) | `outputs/econometric/h14_bidask_spread/2026-03-13_053119/model_diagnostics.csv` |
| Robustness diagnostics | `outputs/econometric/h14_bidask_spread/2026-03-13_032702/robustness_diagnostics.csv` |
| LaTeX table | `outputs/econometric/h14_bidask_spread/2026-03-13_032702/h14_bidask_spread_table.tex` |
| Sample attrition | `outputs/econometric/h14_bidask_spread/2026-03-13_032702/sample_attrition.csv` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | **Pass** | Code inspection confirms PanelOLS, EntityEffects+TimeEffects, 6 uncertainty measures, firm-clustered SE | Correctly identified |
| Reproducibility commands | **Pass** | Commands are runnable; output paths match | No pinned versions but correctly flagged |
| Dependency tracing | **Partial** | 18-step merge chain documented; but CCM LINKPRIM claim is wrong | E2 falsely states CRSP builders filter on LINKPRIM |
| Raw data provenance | **Pass** | All 7 raw sources enumerated with paths and row counts | Verified against panel |
| Merge/sample audit | **Partial** | Match rates verified; but duplicate robustness specs not caught | 12/174 robustness specs are duplicates |
| Variable dictionary completeness | **Partial** | All variables listed; but distribution statistics contain multiple factual errors | See Section D |
| Outlier/missing-data rules | **Pass** | Winsorization layers correctly documented; PreCallSpread gap identified | |
| Estimation spec register | **Pass** | 6 primary specs with correct N, R2, betas | Verified against diagnostics CSV |
| Verification log quality | **Partial** | 21 commands listed; but distribution outputs don't match the narrative table | Stats table appears fabricated or from different data |
| Known issues section | **Partial** | 12 issues listed; but placebo severity underrated, and duplicate robustness not caught | |
| Identification critique | **Partial** | Reverse causality, OVB, survivorship bias discussed; but placebo failure consequence underweighted | Should have been the dominant finding |
| Econometric implementation critique | **Pass** | Kurtosis, dedup, clustering, multicollinearity correctly assessed | |
| Robustness critique | **Partial** | Missing robustness correctly listed; but 12/13 significant robustness results are placebo (not highlighted) | |
| Academic-integrity critique | **Pass** | Warning suppression, sample disclosure, reproducibility gaps flagged | |
| Severity calibration | **Fail** | Placebo failure rated "High" but conclusion still says "THESIS-STANDARD"; DV kurtosis rated "High" but is less threatening than placebo | Severity and verdict are inconsistent |
| Final thesis verdict support | **Fail** | Verdict says "THESIS-STANDARD (with one significant result + honest nulls)" despite two "High" severity issues that should block thesis reliance | |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|-----------------|-------|
| D1 | Panel: 112,968 rows × 39 cols | A, I-1 | **Y** | `p.shape = (112968, 39)` | Correct | |
| D2 | file_name is unique | I-2 | **Y** | `p['file_name'].is_unique = True` | Correct | |
| D3 | DV coverage 98.8% (87,157/88,205 Main) | A3 | **Y** | 87,157/88,205 confirmed | Correct | |
| D4 | AbsSurpDec coverage 69.8% Main (61,544/88,205) | A4, J1 | **Y** | 61,544/88,205 confirmed | Correct | |
| D5 | Size min = -6.908, max = 13.590 | F (distribution table) | **N** | Actual: min=-0.569, max=12.459 | **FACTUAL ERROR** | Off by >6 on min; off by 1.1 on max |
| D6 | delta_spread min = -0.3939, max = 1.5039 | F (distribution table) | **N** | Actual: min=-0.586, max=1.167 | **FACTUAL ERROR** | Both bounds wrong |
| D7 | StockPrice max = 3,578.54 | F (distribution table) | **N** | Actual: max=2,080.02 | **FACTUAL ERROR** | Off by 72% |
| D8 | Volatility min = 2.98, max = 326.19 | F (distribution table) | **N** | Actual: min=9.44, max=211.92 | **FACTUAL ERROR** | Both bounds wrong |
| D9 | Manager_QA_Uncertainty_pct max = 2.304, p99 = 2.304 | F (distribution table) | **N** | Actual: max=2.037, p99=1.754 | **FACTUAL ERROR** | Max and p99 both wrong |
| D10 | Turnover max = 3.7116 | F (distribution table) | **Partial** | Actual: 3.7726 | Minor discrepancy | |
| D11 | Primary H14-1: N=54,726, R2w=0.457, beta=0.0001 | H1 | **Y** | Diagnostics CSV confirmed | Correct | |
| D12 | CEO_Pres: beta=0.0004, p(one)=0.024 | H1, K1 | **Y** | Diagnostics: 0.000405, p=0.0238 | Correct | |
| D13 | 174 robustness regressions | H2 | **Partial** | 174 rows in CSV, but 12 are duplicate specs | **OVERCLAIM** | Only 162 unique specs |
| D14 | 13/174 significant at 5% one-tailed | H2 | **Y** | Confirmed | Correct count, but 12/13 are placebo | First audit did not clearly state this |
| D15 | CRSP builders filter on primary links (P, C) | E2 | **N** | BidAskSpreadChangeBuilder `_build_permno_map` has NO LINKPRIM filter | **FACTUAL ERROR** | Misstated the implementation |
| D16 | 67 time periods (quarter_index) | E4 | **N** | Actual: 68 unique quarter_index in regression sample | **FACTUAL ERROR** | Off by one |
| D17 | DV kurtosis = 136.0 | J2, K3 | **Y** | 136.04 confirmed | Correct | |
| D18 | 10.1% duplicate (gvkey, quarter_index) = 8,952 | J3 | **Y** | 8,952 confirmed | Correct | |
| D19 | PreCallSpread not winsorized | J4 | **Y** | Not in WINSORIZE_COLS | Correct | |
| D20 | Corr(PreCallSpread, Volatility) = 0.672 | K3 | **Y** | 0.672 confirmed | Correct | |
| D21 | One-tailed p-value formula correct | K6 | **Y** | `p_one = p_two / 2` when beta > 0 | Correct | |
| D22 | CEO Clarity Residual Main: 43.9% | J5 | **Y** | 38,671/88,205 = 43.8% | Trivially rounded; correct | |
| D23 | Verdict: THESIS-STANDARD | N | **N** | Two "High" issues (L3, L4) should block this verdict | **INCONSISTENT** | See Section H |
| D24 | Year range: 2002-2018 | I-5 | **Y** | Confirmed | Correct | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-------------------|------------------------|----------|------------------|----------------------|
| E1 | Distribution table (Section F) reports Size min=-6.908 | The actual panel has Size min=-0.569. No command in the verification log produces this value. | **High** | The verification log (I-6) references `.describe()` but does not show the output; the numbers in the table are fabricated or from a different dataset. | Size min=-0.569 (Main sample); this is ln(atq) where atq=0.57. |
| E2 | Multiple distribution statistics (delta_spread, StockPrice, Volatility, Manager_QA max) are wrong | At least 5 of 12 variables have incorrect min/max/p1/p99 values in the distribution table. | **High** | No verification command produces these specific numbers. The table appears to use values from a different panel version or was not validated. | Replace entire distribution table with verified values from the 2026-03-13_031834 panel. |
| E3 | "CRSP-dependent builders filter to primary links (P, C)" (Section E2) | BidAskSpreadChangeBuilder `_build_permno_map` loads ALL CCM links without LINKPRIM filter. StockPriceBuilder and TurnoverBuilder use similar code. Only IbesEngine filters on LINKPRIM. | **Medium** | No grep or code inspection in the verification log tests for LINKPRIM in CRSP builders. | CRSP-dependent builders do NOT filter on LINKPRIM; they use all date-bounded CCM links. |
| E4 | "174 robustness regressions" implies 174 unique specifications | 12 of the 174 rows are exact duplicates (placebo_full = placebo_no_PreCallSpread because placebo code strips PreCallSpread regardless). | **Medium** | No dedup check on robustness diagnostics CSV. | 162 unique robustness specifications (12 duplicates from placebo control-variant aliasing). |
| E5 | "Of 174 robustness regressions, 13 cross p<0.05" without noting that 12/13 are placebo | The text buries the fact that only 1 of 13 significant robustness results is on the actual DV. | **High** | No breakdown by DV type for the 13 significant specs. | Of 162 unique robustness specs, 8 unique placebo specs are significant, 1 primary DV spec is marginally significant (p=0.043), and 0 alternative DV specs (closing, w1, w5) are significant. |
| E6 | "67 time periods" in singleton analysis table | Actual regression sample has 68 unique quarter_index values. | **Low** | Off by one; likely from a different intermediate count. | 68 time periods. |

---

## F. False Positives in the First Audit

| ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|----------------------------------|----------|------------------------|----------------|
| F1 | None identified | The first audit's criticisms of the implementation are generally warranted. | — | — | The first audit errs on the side of under-criticism, not over-criticism. |

---

## G. Missed Issues (Second-Layer Discoveries)

| ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|-----------------------------------|-------------|-----------------|
| G1 | Robustness / identification | **Placebo effect is LARGER than primary effect:** CEO_Pres placebo beta=0.001143 vs primary beta=0.000405. The placebo coefficient is 2.8x the primary coefficient. | Robustness diagnostics: placebo beta=0.001143, primary beta=0.000405 | **Critical** | First audit flagged placebo significance (L4) but did not compare magnitudes. A larger placebo effect means the primary finding is likely confounded. | The CEO_Pres_Uncertainty result (the only significant primary spec) cannot be interpreted as a call-day causal effect. The spread changes occur BEFORE the call, not after. | This should be the dominant finding in the audit. H14 has NO credible significant result. |
| G2 | Robustness | **12 of 174 robustness specs are duplicates.** Placebo specs strip PreCallSpread at line 614, so `placebo_full` = `placebo_no_PreCallSpread` identically. | Verified: `placebo_full_firm` and `placebo_no_PreCallSpread_firm` produce identical beta/SE/N for all 6 measures. | **Medium** | First audit did not inspect the robustness code path for the placebo-PreCallSpread interaction. | Inflated robustness count (174 reported vs 162 unique). The 13/174 significance rate is also inflated to 13/162 = 8.0%. | Fix the robustness loop to skip redundant placebo variants. |
| G3 | Merge/provenance | **No LINKPRIM filter in CRSP-dependent builders.** BidAskSpreadChangeBuilder, StockPriceBuilder, and TurnoverBuilder use all CCM links (including secondary J links). | Grep for "LINKPRIM" in `bidask_spread_change.py`: 0 hits. Only `_ibes_engine.py` and `_ibes_detail_engine.py` filter on LINKPRIM. | **Medium** | First audit asserted LINKPRIM filtering without verifying the code. | Secondary/J links could map a gvkey to a non-primary PERMNO, potentially introducing noise or mismatches in CRSP variables. The 98.9% match rate suggests the impact is likely small but the linkage is technically wrong. | Add LINKPRIM filter to `_build_permno_map` or document why it is intentionally omitted. |
| G4 | Data integrity | **Distribution statistics in first audit are fabricated or from wrong panel.** At least 5 of 12 variables have incorrect min/max values. | Size: audit says min=-6.908, actual=-0.569. delta_spread: audit says min=-0.394, actual=-0.586. StockPrice: audit says max=3578, actual=2080. Volatility: audit says min=2.98, actual=9.44. | **High** | First audit's verification log references `.describe()` but the table values don't match any plausible output of that command on the referenced panel. | A referee relying on the distribution table would have incorrect beliefs about variable ranges. | Regenerate the entire distribution table from the actual panel with verifiable commands. |
| G5 | Robustness / interpretation | **CEO_Pres is NOT significant in closing-spread, w1, or w5 alternatives.** It is only significant for the primary ASKHI/BIDLO ±3 window DV and the placebo. | Robustness diagnostics: CEO_Pres closing beta=-0.00001 (null), w1 beta=-0.0003 (null), w5 beta=0.0002 (null). | **High** | First audit mentions closing spread and window robustness exist but does not explicitly state that CEO_Pres significance does NOT survive them. | The CEO_Pres finding is fragile: it depends on (a) the specific spread formula (ASKHI/BIDLO not BID/ASK), (b) the specific window (±3), and (c) including PreCallSpread as a control. This is consistent with specification search rather than a robust effect. | Report this explicitly. The CEO_Pres p=0.024 finding should NOT be treated as evidence for H14. |
| G6 | Specification-conditional winsorization | **Winsorization cutoffs differ across specs** because winsorization happens after listwise deletion (within the regression sample). The Mgr QA spec (N=55,923 pre-dedup) and CEO Clarity spec (N=~38,000) have different 1%/99% thresholds. | Code: `_winsorize_cols` called inside `run_regression` after `dropna`. | **Low** | First audit did not flag this. | Minor inconsistency; unlikely to change results materially given all primary specs are null or barely significant. | Winsorize on the full Main sample before listwise deletion, or document the conditional approach. |
| G7 | Stale artifact / reproducibility | **A newer output directory exists (2026-03-13_053119) beyond the one referenced by the audit (2026-03-13_032702).** Both contain identical results, but the audit does not reference the latest. | `ls outputs/econometric/h14_bidask_spread/` shows 2026-03-13_053119 as most recent. | **Low** | First audit pinned to one timestamp. | The `get_latest_output_dir` would resolve to the newer directory; commands using it would produce outputs in a new timestamp directory. | Note which run is authoritative; verify `get_latest_output_dir` resolves to expected run. |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| L3 | First audit | High | **Medium** | Extreme kurtosis affects OLS efficiency but not consistency. With 54,726 obs, the t-stats are well-behaved. The kurtosis is concerning but not thesis-blocking if the main finding is null. | OLS inefficiency; SEs may be slightly misleading |
| L4 | First audit | High | **Critical** | The placebo coefficient (0.001143) is 2.8x the primary coefficient (0.000405). The placebo is significant at p<0.03 while the primary effect is only p=0.024. This means the only significant H14 result is likely confounded by pre-existing dynamics. Combined with G5 (CEO_Pres doesn't survive alternative DVs), this renders the one positive finding unreliable. | **Thesis-blocking for the significant finding.** The honest interpretation is that H14 produces null results across all 6 measures. |
| L5 | First audit | Medium | Medium | PreCallSpread winsorization gap is real but not thesis-blocking. | Inconsistent treatment |
| L5a | First audit | Medium | Low | With 38,218 obs for CEO Clarity, the sample is adequate for a null finding. Coverage is a generalizability concern, not a validity threat. | Low because result is null |
| L6 | First audit | Medium | Medium | Dedup of 10.1% rows is a real concern but unlikely to flip null results. | Arbitrary call selection |
| L7 | First audit | Medium | Medium | Missing robustness tests (fyearq FE, industry subsamples) are standard but less urgent when main results are null. | Robustness gap |
| L8 | First audit | Medium | **High** | The interpretation section should be the centerpiece: 0/6 primary specs survive (when the placebo failure invalidates CEO_Pres). Multiple testing correction on 6 measures would push even the nominal p=0.024 to non-significance (Bonferroni: 0.024 × 6 = 0.144). | Interpretation is the key issue |
| L9 | First audit | Medium | Low | Warning suppression is a documentation issue. The covariance rank warning is common with two-way FE and absorbed variables; it does not indicate a specification problem here. | Documentation |
| G1 | Red-team | — | **Critical** | New discovery: placebo beta is 2.8x primary beta. | Thesis-blocking for CEO_Pres finding |
| G2 | Red-team | — | **Medium** | 12 duplicate robustness specs inflate the count. | Inflated robustness claim |
| G3 | Red-team | — | **Medium** | Missing LINKPRIM filter in CRSP builders. | Potential noise in CRSP variables |
| G4 | Red-team | — | **High** | Distribution table contains multiple factual errors. | Audit reliability |
| G5 | Red-team | — | **High** | CEO_Pres doesn't survive closing spread, w1, or w5 alternatives. | Only significant finding is fragile |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| Distribution statistics verification | Table values don't match actual panel data | 5+ variables have wrong min/max/p1/p99 | **High** | Actual verified distribution statistics from the referenced panel |
| Robustness breakdown by DV type | 13 significant specs not decomposed | 12/13 are placebo; first audit says "13 of 174" without DV breakdown | **High** | Explicit table: N significant by DV type |
| Placebo magnitude comparison | Placebo beta vs primary beta not compared | Placebo beta is 2.8x primary | **High** | Side-by-side comparison of primary vs placebo coefficients |
| CEO_Pres DV-robustness assessment | Closing/w1/w5 results for CEO_Pres not highlighted | CEO_Pres is null in all alternative DVs | **High** | Explicit statement that the significant finding does not survive any alternative DV construction |
| LINKPRIM in CRSP builders | Incorrectly asserted; not verified | grep for LINKPRIM returns 0 hits in bidask_spread_change.py | **Medium** | Correct statement about which builders filter on LINKPRIM |
| Duplicate robustness check | Not tested | 12 rows are exact duplicates | **Medium** | Dedup check on robustness CSV |
| Cross-run consistency | Newer output directory not noted | 2026-03-13_053119 exists beyond referenced 2026-03-13_032702 | **Low** | Note both runs produce identical results |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Stage 3: build panel | Y | Y (command runnable) | Y: requires upstream manifest, CRSP, Compustat, IBES, linguistic, H0.3 clarity outputs | Medium | `get_latest_output_dir` resolves dynamically |
| Stage 4: run regressions | Y | Y (command runnable) | Y: requires Stage 3 output | Low | |
| Panel artifact existence | Y (path documented) | Y | N | Low | Panel verified at referenced path |
| Robustness outputs | Y | Y | N | Low | All files present |
| Package versions | Y (flagged as gap) | N/A | Y: no pinning | Low | Correctly identified |
| Determinism | Y (stated deterministic) | Y (two runs produce identical results) | N | Low | Verified via 2026-03-13_032702 vs 2026-03-13_053119 |
| Full end-to-end from clean state | N (not tested) | N | Unknown | Medium | Would require all upstream stages |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| Identification threats | **Partial** | Reverse causality, OVB, survivorship discussed | Did not escalate placebo failure to identification-threatening level | **High** |
| Inference / clustering | **Y** | 1,534 clusters, firm-level adequate | — | — |
| FE and within-variation | **Y** | Firm + year-quarter FE, no singletons, no absorbed obs | — | — |
| Timing alignment | **Y** | Pre-call controls correctly classified | — | — |
| Post-treatment controls | **Y** | Correctly verified PreCallSpread is pre-treatment | — | — |
| Reverse causality | **Partial** | Noted but not connected to placebo failure | Placebo significance IS evidence of reverse causality / confounding | **High** |
| Endogenous sample selection | **Y** | IBES coverage concern addressed | — | — |
| Model-family-specific threats | **Y** | Kurtosis, dedup, multicollinearity discussed | — | — |
| Robustness adequacy | **Partial** | Missing tests listed; but existing robustness results not correctly interpreted | CEO_Pres fragility across DVs not highlighted; duplicate robustness counted | **High** |
| Interpretation discipline | **Partial** | Multiple testing, economic magnitude discussed | But final verdict still calls it "THESIS-STANDARD" despite the placebo failure and DV-fragility | **High** |
| Academic-integrity / auditability | **Partial** | Warning suppression, sample disclosure flagged | Distribution table contains fabricated statistics | **High** |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| **Distribution statistics are incorrect** | 5+ variables have wrong min/max values in Section F table; values cannot be reproduced from the referenced panel | **High** | A committee member reading the distribution table would have false beliefs about variable ranges. This undermines trust in ALL verified claims. | Regenerate table from actual panel with reproducible commands |
| **Verdict contradicts issue register** | Two issues rated "High" (L3, L4); verdict says "THESIS-STANDARD" | **Medium** | "High" severity issues that "Block Thesis" (L3 marked Y, L4 marked Y) should preclude a THESIS-STANDARD verdict. | Downgrade verdict to SALVAGEABLE or resolve the High issues first |
| **Placebo finding buried in robustness section** | L4 and K5 mention placebo significance but the magnitude comparison (2.8x primary) is absent | **High** | A referee would not realize the placebo effect dominates the primary effect from reading the audit | Move placebo analysis to the top-level finding |
| **Robustness count inflated** | 174 includes 12 duplicates; 13/174 significance rate obscures that 12/13 are placebo | **Medium** | A committee member would incorrectly assess the robustness landscape | Report 162 unique specs; break down significance by DV type |
| **CCM linkage claim is false** | E2 states CRSP builders filter on LINKPRIM P/C; they do not | **Medium** | False claim about data linkage methodology could mislead a replication attempt | Correct the claim |

---

## M. Master Red-Team Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance on first audit? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|---------------------------------------|
| RT-1 | First-audit factual error | Distribution stats | Y | **High** | Section F table | Size min reported as -6.908; actual is -0.569. delta_spread min/max, StockPrice max, Volatility min/max, Manager_QA_pct max/p99 all wrong. | Panel inspection: `p[col].describe()` produces different values | Referee has incorrect beliefs about variable ranges | Regenerate distribution table from actual panel | **Y** |
| RT-2 | Underlying issue underplayed by first audit | Identification | Y | **Critical** | L4, K5 | Placebo beta (0.001143) is 2.8x primary beta (0.000405). Placebo is significant at p<0.03 for CEO_Pres and Manager_Pres. Primary CEO_Pres effect does not survive closing spread, ±1, or ±5 DVs. | Robustness diagnostics CSV | The only significant H14 finding (CEO_Pres p=0.024) is likely confounded. H14 should be reported as producing null results. | Upgrade placebo failure to thesis-blocking; report H14 as null | **Y** |
| RT-3 | First-audit factual error | Merge/provenance | Y | **Medium** | Section E2 | Claims CRSP builders "filter to primary links (P, C)"; they do NOT. Only IbesEngine uses LINKPRIM filter. | grep LINKPRIM in bidask_spread_change.py: 0 hits | False claim about data methodology | Correct E2; consider adding LINKPRIM filter to CRSP builders | N |
| RT-4 | First-audit unsupported claim | Robustness count | Y | **Medium** | Section H2 | "174 robustness regressions" includes 12 exact duplicates (placebo_full = placebo_no_PreCallSpread) | Dedup check: 162 unique specs | Inflated robustness count | Fix loop to skip redundant placebo variants; report 162 | N |
| RT-5 | First-audit omission | Robustness interpretation | Y | **High** | Section H2, K5 | 12 of 13 significant robustness specs are placebo; only 1 is primary DV (CEO_Pres firm+quarter p=0.043). 0 alternative DVs significant. This was not explicitly stated. | Breakdown of 13 significant specs by DV type | Misleading robustness summary | Add DV-type breakdown; highlight that no alternative DV is significant | **Y** |
| RT-6 | First-audit severity error | Severity calibration | Y | **High** | Section N, L | Verdict "THESIS-STANDARD" despite L3 and L4 both rated "High" and marked "Blocks Thesis = Y" | Internal contradiction in issue register vs verdict | Verdict is inconsistent with the audit's own findings | Downgrade verdict to SALVAGEABLE WITH MAJOR REVISIONS | **Y** |
| RT-7 | First-audit factual error | Time periods | Y | **Low** | Section E4 | Reports 67 time periods; actual is 68 | `cc['quarter_index'].nunique() = 68` | Minor factual error | Correct to 68 | N |
| RT-8 | Underlying implementation issue missed | Duplicate robustness | Y | **Medium** | `run_h14_bidask_spread.py:614` | Placebo DV strips PreCallSpread at line 614, making `placebo_full` and `placebo_no_PreCallSpread` identical. 12 wasted regressions. | Identical beta/SE/N for both labels | Inflated computation and misleading output | Add condition to skip no_PreCallSpread variant when dv_name == "placebo" | N |
| RT-9 | Underlying implementation issue missed | CCM linkage | Y | **Medium** | `bidask_spread_change.py:127-200` | No LINKPRIM filter; all CCM links used for PERMNO mapping | Code inspection | May introduce secondary-link noise | Add LINKPRIM P/C filter | N |
| RT-10 | First-audit omission | CEO_Pres DV fragility | Y | **High** | Not covered | CEO_Pres significance (p=0.024) does NOT survive: closing spread (p~0.5), ±1 window (p~0.5), ±5 window (p~0.15). It only "works" with ASKHI/BIDLO ±3. | Robustness diagnostics breakdown | The significant finding is specification-specific and should not be reported as robust | State explicitly in the audit and thesis | **Y** |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **The placebo effect is 2.8x larger than the primary effect.** The first audit mentions placebo significance but never compares magnitudes. A referee would not know that the pre-call spread change associated with CEO_Pres uncertainty is nearly triple the post-call change.

2. **CEO_Pres significance does not survive ANY alternative DV.** Closing spread: null. ±1 window: null. ±5 window: null. Only the specific ASKHI/BIDLO ±3 construction produces significance. The first audit does not state this.

3. **12 of 13 significant robustness results are placebo.** The first audit says "13 of 174 significant" without breaking this down. A referee would assume some of these are genuine DV robustness results.

4. **The distribution statistics table is wrong.** Multiple min/max/percentile values are incorrect. A referee would cite these numbers in a review.

5. **CRSP builders do not filter on LINKPRIM.** The first audit incorrectly claims they do.

6. **The honest bottom line is that H14 produces NULL results across all 6 uncertainty measures.** The one nominally significant finding (CEO_Pres p=0.024) fails the placebo test, fails all alternative DVs, and would not survive Bonferroni correction. The first audit's "THESIS-STANDARD with one significant result" verdict is misleading.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|----------|-------------------|----------------|--------|------------------|
| 1 | **Downgrade verdict from THESIS-STANDARD to SALVAGEABLE; reclassify CEO_Pres finding as likely confounded** | The placebo failure (2.8x primary magnitude) and DV fragility (0/3 alternative DVs significant) mean the only positive finding is unreliable. The honest interpretation is 6/6 null results. | Low (text edit) | **Critical** — prevents a committee from being misled |
| 2 | **Regenerate the distribution statistics table** | At least 5 variables have wrong values. This undermines the entire audit's credibility. | Low (re-run describe()) | **High** — restores trust in verified claims |
| 3 | **Add placebo magnitude comparison and DV-robustness breakdown for CEO_Pres** | The most important analytical finding is currently buried/absent. | Low (add table) | **High** — enables informed referee assessment |
| 4 | **Fix robustness count (162 unique, not 174) and add DV-type significance breakdown** | Currently misleading. | Low (text + table edit) | **Medium** |
| 5 | **Correct CCM LINKPRIM claim in Section E2** | Currently false. | Low (text edit) | **Medium** |
| 6 | **Fix time periods count (68, not 67)** | Minor factual error. | Low | **Low** |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The distribution statistics table contains multiple factual errors, the verdict contradicts the audit's own issue register, and the most important analytical finding (placebo failure dominating the primary effect) is insufficiently communicated.

**What is its biggest factual weakness?**
The distribution statistics table in Section F. At least 5 of 12 variables have incorrect min, max, or percentile values that cannot be reproduced from the referenced panel artifact. This suggests the table was generated from a different dataset or was not validated.

**What is its biggest completeness weakness?**
The failure to explicitly state that (a) CEO_Pres significance does not survive any alternative DV construction, and (b) the placebo effect is 2.8x the primary effect. These two facts, taken together, invalidate the only positive finding.

**What is its biggest severity/judgment weakness?**
The final verdict of "THESIS-STANDARD (with one significant result + honest nulls)" is inconsistent with the audit's own issue register, which marks L3 and L4 as "High" severity and "Blocks Thesis = Y." The verdict should be SALVAGEABLE WITH MAJOR REVISIONS at best, or more honestly, the suite should be reported as producing null results across all measures.

**What is the single most important missed issue?**
The placebo beta being 2.8x the primary beta for CEO_Pres_Uncertainty. This is not a marginal concern — it means the pre-call spread dynamics associated with presentation-section uncertainty are nearly triple the post-call dynamics. The "effect" occurs before the call, not after it. This is evidence of confounding, not a causal call-day mechanism.

**What is the single most misleading claim?**
"THESIS-STANDARD (with one significant result + honest nulls)" — because the one significant result is invalidated by the placebo test and does not survive any alternative DV construction.

**What should a thesis committee believe after reading this red-team review?**
H14 tests whether earnings-call language uncertainty widens bid-ask spreads. The implementation is technically competent (correct PanelOLS, appropriate FE/SE structure, comprehensive variable construction). However, the results are unambiguously null: 5 of 6 primary specifications are insignificant, and the one nominally significant finding (CEO Presentation Uncertainty, p=0.024) fails every robustness test — it does not survive closing spreads, alternative windows, or the placebo test. The placebo coefficient is 2.8x the primary coefficient, indicating pre-existing confounding rather than a call-day effect. H14 should be reported as producing honest null results across all uncertainty measures. The first-layer audit correctly identified most implementation issues but its verdict was too generous given its own findings, and its distribution statistics table contains multiple factual errors that undermine its credibility as a standalone referee document.
