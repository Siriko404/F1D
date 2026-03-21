# H14 Second-Layer Red-Team Audit (Post-Redesign)

**Suite ID:** H14
**Red-Team Auditor:** Independent (fresh context, second-layer)
**Date:** 2026-03-18
**First-Layer Audit Under Review:** `docs/provenance/H14.md` (dated 2026-03-17, post-redesign)
**Prior Red-Team Audit:** `docs/provenance/Audits/H14_red_team.md` (dated 2026-03-15, pre-redesign -- now stale)

---

## A. Red-Team Bottom Line

The first-layer audit document (`docs/provenance/H14.md`) is a concise, well-structured provenance record for the redesigned H14 suite. It correctly identifies the model family (PanelOLS), the 4 simultaneous uncertainty IVs, the 4-column specification grid (2 FE types x 2 control sets), and the Lee (2016) DV construction. However, the audit has several material weaknesses: (1) it presents results from a stale pre-redesign run (6 IVs, N=37,657) that are no longer producible by the current code, (2) it does not document the inconsistent CCM LINKPRIM filtering across CRSP-dependent builders within the suite, (3) it omits discussion of multi-call-per-fiscal-year indexing implications, and (4) the bug-fix table contains one claim that contradicts verifiable code.

**Overall grade for the first audit: PARTIALLY RELIABLE**

**Verdict on the suite as implemented: CONDITIONALLY THESIS-READY**

The implementation is technically sound after the redesign. The 4-column design is clean, the Lee (2016) DV construction is correctly implemented using closing BID/ASK quotes, and the control set is appropriate for the microstructure literature. The main risk is that the audit documents stale results and has not been refreshed with a new run. Once a fresh run is executed, the audit must be updated with actual results before thesis submission.

---

## B. Scope and Objects Audited

| Item | Path / Identifier |
|------|-------------------|
| Suite ID | H14 |
| Suite entrypoint | `src/f1d/econometric/run_h14_bidask_spread.py` |
| Panel builder | `src/f1d/variables/build_h14_bidask_spread_panel.py` |
| First-layer audit | `docs/provenance/H14.md` |
| BidAskSpreadChangeBuilder | `src/f1d/shared/variables/bidask_spread_change.py` |
| StockPriceBuilder | `src/f1d/shared/variables/stock_price.py` |
| TurnoverBuilder | `src/f1d/shared/variables/turnover.py` |
| VolatilityBuilder | `src/f1d/shared/variables/volatility.py` |
| EarningsSurpriseBuilder | `src/f1d/shared/variables/earnings_surprise.py` |
| BookLevBuilder | `src/f1d/shared/variables/book_lev.py` |
| CRSPEngine | `src/f1d/shared/variables/_crsp_engine.py` |
| CompustatEngine | `src/f1d/shared/variables/_compustat_engine.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` |
| Winsorization | `src/f1d/shared/variables/winsorization.py` |
| Prior red-team audit (stale) | `docs/provenance/Audits/H14_red_team.md` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|-----------|-------------------|----------------|---------------|
| Model/spec identification | **Pass** | Code inspection confirms PanelOLS, 4 IVs, 4 columns, 2 FE x 2 controls | Correctly identified |
| DV construction documentation | **Pass** | Lee (2016) formula, closing BID/ASK, [-3,-1] to [+1,+3] trading days | Verified against `bidask_spread_change.py` |
| IV documentation | **Pass** | 4 uncertainty measures correctly listed with coverage rates | Consistent with code |
| Control variable documentation | **Pass** | 8 base + 4 extended controls correctly listed with definitions | Verified against runner and builder code |
| FE implementation | **Pass** | Industry FE via `other_effects`, Firm FE via `EntityEffects`, both with `TimeEffects` | Code verified at lines 298-316 |
| SE specification | **Pass** | `cov_type="clustered", cluster_entity=True` documented as firm-clustered | Code verified at lines 311, 316 |
| P-value methodology | **Pass** | One-tailed formula: `p_two/2 if beta > 0 else 1-p_two/2` | Code verified at lines 343-344 |
| Bug-fix documentation | **Partial** | 9 bugs listed; 8 verified correct, 1 contains a claim contradicted by code | See D7 |
| Winsorization documentation | **Pass** | Pooled 1%/99% for CRSP-derived; per-year for Compustat/CRSPEngine | Verified against `winsorization.py` and `_crsp_engine.py` |
| Results documentation | **Partial** | Results are from pre-redesign run (6 IVs); audit honestly flags this but no fresh results exist | Stale results cannot be verified against current code |
| Reproducibility commands | **Pass** | Two-step pipeline documented and runnable | Verified |
| Output file documentation | **Pass** | All expected output files listed for both stages | Consistent with code |
| Sample filter documentation | **Pass** | FF12 not in {8, 11} filter documented and verified | Code line 214-218 |
| MIN_CALLS_PER_FIRM documentation | **Missing** | Not mentioned in the audit | Code has `MIN_CALLS_PER_FIRM = 5` at line 121; this materially affects sample size |
| Merge strategy documentation | **Missing** | Left-join merge with zero-row-delta enforcement not documented | Builder enforces this at line 168-169 |
| CCM linkage consistency | **Missing** | No discussion of LINKPRIM filtering differences across builders | See G2 |

---

## D. Claim Verification Matrix

| ID | First-layer claim | Section | Verified? | Evidence | Red-team verdict | Notes |
|----|-------------------|---------|-----------|----------|-----------------|-------|
| D1 | DV: DSPREAD = mean(RelSpread[+1,+3]) - mean(RelSpread[-3,-1]) using closing quotes | A | **Y** | `bidask_spread_change.py` lines 339-349, 411-434: closing BID/ASK used; renamed to DSPREAD at builder line 181 | **VERIFIED FACT** | Correctly describes Lee (2016) construction |
| D2 | RelSpread_d = 2*(ASK-BID)/(ASK+BID) | A | **Y** | Code line 346: `2 * (ASK - BID) / (ASK + BID)` | **VERIFIED FACT** | |
| D3 | 4 simultaneous IVs: CEO_QA/Pres_Uncertainty_pct, Manager_QA/Pres_Uncertainty_pct | B | **Y** | `KEY_IVS` list at runner lines 87-91 matches | **VERIFIED FACT** | |
| D4 | Base controls: Size, TobinsQ, ROA, BookLev, CapexAt, DividendPayer, OCF_Volatility, PreCallSpread | C | **Y** | `BASE_CONTROLS` at runner lines 96-105 matches exactly | **VERIFIED FACT** | |
| D5 | Extended controls: Base + StockPrice, Turnover, Volatility, AbsSurpDec | C | **Y** | `EXTENDED_CONTROLS` at runner lines 107-112 matches | **VERIFIED FACT** | |
| D6 | Turnover = VOL / (SHROUT * 1000) | C | **Y** | `turnover.py` line 233: `VOL / (SHROUT * 1000)` | **VERIFIED FACT** | |
| D7 | Bug fix: "LINKPRIM not filtered in CCM linkage" -- "Added linkprim in [P,C] filter" | F | **Partial** | BidAskSpreadChangeBuilder DOES have LINKPRIM filter (lines 144, 159-161). But StockPriceBuilder and TurnoverBuilder do NOT. | **VERIFIED FACT for BidAskSpreadChangeBuilder; incomplete for suite** | The fix was applied to the DV builder but not to all CRSP-dependent builders in the suite |
| D8 | Bug fix: "DV used ASKHI/BIDLO; switched to closing BID/ASK" | F | **Y** | Code computes both but `delta_spread_closing` is renamed to DSPREAD at builder line 181 | **VERIFIED FACT** | |
| D9 | Bug fix: "Calendar year-quarter time FE -> fyearq_int (fiscal year)" | F | **Y** | Runner line 295: `set_index(["gvkey", "fyearq_int"])`; builder lines 195-197: `fyearq_int = floor(fyearq)` | **VERIFIED FACT** | |
| D10 | Bug fix: "Deduplication on calendar quarter removed (PanelOLS handles non-unique multi-index)" | F | **Y** | No dedup code in runner; PanelOLS does handle duplicate multi-index entries | **VERIFIED FACT** | But implications of multiple calls per firm per fiscal year not discussed |
| D11 | N=37,657 calls, 1,276 firms | A, E | **Unverifiable** | These are from the pre-4IV run. Current code with 4 IVs will produce different N. The audit itself flags this. | **VERIFIED as honestly disclosed stale data** | Audit says "A fresh run is needed" |
| D12 | Panel: 112,968 rows, 34 columns | I | **Unverifiable without running** | Code is consistent with producing a panel of this size; column count depends on builder output | **UNVERIFIED** | Would need a fresh run to confirm |
| D13 | PreCallSpread is pre-call relative spread level [-3,-1] | C | **Y** | `pre_call_spread_closing` renamed to `PreCallSpread` at builder line 182; computed from pre-window at `bidask_spread_change.py` lines 413-414 | **VERIFIED FACT** | |
| D14 | Industry FE via PanelOLS `other_effects=ff12_code` with `entity_effects=False, time_effects=True` | D | **Y** | Runner lines 302-310 match exactly | **VERIFIED FACT** | |
| D15 | Firm FE via `PanelOLS.from_formula` with `EntityEffects + TimeEffects` | D | **Y** | Runner lines 313-315 match | **VERIFIED FACT** | |
| D16 | SEs: firm-clustered | A | **Y** | `cov_type="clustered", cluster_entity=True` at lines 311, 316 | **VERIFIED FACT** | |
| D17 | P-values: one-tailed (H14: beta > 0) | A | **Y** | Code lines 343-344: `p_one = p_two / 2 if beta > 0 else 1 - p_two / 2` | **VERIFIED FACT** | Correct one-tailed conversion |
| D18 | Winsorization: DSPREAD, PreCallSpread pooled 1%/99% at panel builder | G | **Y** | Builder lines 202-203: `winsorize_pooled(panel, ["DSPREAD", "PreCallSpread", "StockPrice", "Turnover", "AbsSurpDec"])` | **VERIFIED FACT** | |
| D19 | Winsorization: Volatility per-year by CRSPEngine | G | **Y** | `_crsp_engine.py` lines 445-447: `winsorize_by_year(result_with_year, CRSP_RETURN_COLS)` | **VERIFIED FACT** | But Volatility for H14 comes from VolatilityBuilder which reads from CRSPEngine.get_data(), not get_raw_daily_data(). The per-year winsorization covers Volatility. Confirmed. |
| D20 | Winsorization: Compustat controls per-year | G | **Y** | CompustatEngine applies per-year winsorization | **VERIFIED FACT** | |
| D21 | Results: CEO Clarity Residual strongly significant (pre-4IV run) | E | **Not code-verifiable** | Clarity residuals removed from current code; results are from historical run | **VERIFIED as honestly disclosed stale data** | |
| D22 | Bug fix: "PreCallSpread not winsorized -- Added to winsorization at panel builder level" | F | **Y** | Builder line 202: PreCallSpread is in `winsorize_cols` list | **VERIFIED FACT** | |
| D23 | Within-R-squared 0.327-0.349 (pre-4IV) | E | **Unverifiable** | From stale run | **UNVERIFIED** | |
| D24 | Sample: Main only (FF12 not in {8, 11}) | A | **Y** | Runner line 214: `~panel["ff12_code"].isin([8, 11])` | **VERIFIED FACT** | |

---

## E. Unsupported/Overstated Claims

| ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|----|-------------------|------------------------|----------|------------------|----------------------|
| E1 | Results table (Section E) presents specific beta, significance, and R-squared values | These are from a pre-redesign run with 6 IVs. Current code has 4 IVs and different sample composition. The audit flags this but still presents the table prominently. | **Medium** | No fresh run results exist. The "expected ~57K" sample estimate is unsupported. | Remove or clearly section-off stale results; mark them as "HISTORICAL ONLY -- NOT REPRODUCIBLE FROM CURRENT CODE" |
| E2 | "Expected ~57K due to removal of clarity residual coverage requirement" (Section E) | This sample size estimate has no supporting calculation. Removing the clarity residual coverage constraint could produce any number between 37K and 100K+ depending on which variables are binding. | **Low** | No computation backing the estimate | Remove the estimate or provide a clear calculation |
| E3 | Bug fix table claims "LINKPRIM not filtered in CCM linkage -- Added linkprim in [P,C] filter" | This is only true for BidAskSpreadChangeBuilder. StockPriceBuilder and TurnoverBuilder (both H14-specific CRSP builders) still do NOT filter on LINKPRIM. The bug fix was incomplete. | **Medium** | No verification that ALL CRSP-dependent builders in the suite have the filter | Correct to: "Added LINKPRIM filter to BidAskSpreadChangeBuilder (DV). StockPriceBuilder and TurnoverBuilder still use all CCM links." |
| E4 | "First 7 are thesis-consistent (shared across H1/H4/H5 base sets)" | BookLev uses `BookLevBuilder` (from `book_lev.py`) in H14, but the claim of "thesis consistency" is only valid if all suites use the identical definition. The existence of both `LevBuilder` (lev.py) and `BookLevBuilder` (book_lev.py) -- both computing `(dlcq+dlttq)/atq` -- suggests an unnecessary duplication that could drift. | **Low** | No cross-suite comparison of which builder each suite uses | Add note that BookLev and Lev are functionally identical builders |

---

## F. False Positives

| ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|----|----------------------|----------------------------------|----------|------------------------|----------------|
| F1 | None identified | The first-layer audit is largely descriptive (provenance document) rather than critical. It does not make false claims about problems -- its weakness is that it does not identify problems rather than falsely identifying them. | -- | -- | -- |

---

## G. Missed Issues

| ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed | Consequence | Recommended fix |
|----|----------|-------------|----------|----------|-----------------------------------|-------------|-----------------|
| G1 | Sample construction | **MIN_CALLS_PER_FIRM = 5 filter not documented.** The runner drops all firms with fewer than 5 calls from the regression sample. This is a material sample restriction that could exclude smaller or newer firms. | Runner line 121: `MIN_CALLS_PER_FIRM = 5`; applied at line 254 | **Medium** | Audit does not mention this filter anywhere in sections A-I | Committee would not know about this survivorship-type filter. It could bias results toward larger, longer-listed firms. | Document in Section A and sample attrition chain |
| G2 | Merge/provenance | **Inconsistent LINKPRIM filtering across CRSP builders.** BidAskSpreadChangeBuilder filters CCM links to LINKPRIM in {P, C} (lines 159-161). StockPriceBuilder and TurnoverBuilder do NOT filter on LINKPRIM -- they use all date-bounded CCM links. This means the DV (DSPREAD) and PreCallSpread use primary-link PERMNOs while StockPrice and Turnover may use secondary-link PERMNOs. | StockPriceBuilder `_build_permno_map` (stock_price.py lines 96-101): only loads linkdt, linkenddt -- no linkprim. TurnoverBuilder identical pattern. | **Medium** | Audit does not discuss CCM linkage consistency across builders | DV and controls may use different PERMNOs for the same firm-call, introducing measurement noise. Impact is likely small (secondary links are rare) but constitutes a methodological inconsistency. | Either add LINKPRIM filter to all CRSP builders or document why it is intentionally omitted for controls |
| G3 | Econometric specification | **Multiple calls per firm per fiscal year with fyearq_int time FE.** The time index is fiscal year (not fiscal year-quarter). With quarterly earnings calls, most firms have ~4 calls per fiscal year sharing the same time FE. This means: (a) the "time FE" only absorbs annual macro shocks, not quarterly seasonality, (b) within-R-squared may understate the explanatory power of quarterly patterns. | Runner line 295: `set_index(["gvkey", "fyearq_int"])`. With ~4 calls per firm per year, the multi-index has substantial duplication. | **Medium** | Audit describes `fyearq_int` as time FE but does not discuss the quarterly-seasonality gap | A referee might ask why year FE rather than year-quarter FE. Quarter-level FE would better control for seasonal earnings-call patterns and macroeconomic quarter effects. | Document rationale for fiscal-year (not quarter) FE; consider adding fiscal quarter FE as a robustness check |
| G4 | Variable construction | **Volatility comes from a different CRSP window than DSPREAD.** VolatilityBuilder uses CRSPEngine.get_data() which computes volatility over the inter-call window [prev_call+1 day, call-5 days] (requiring 10 trading days). DSPREAD uses [-3,-1] and [+1,+3] around the call. The volatility control therefore measures a different time horizon than the DV. | `volatility.py` uses `engine.get_data()` which calls `_compute_returns_for_manifest` with window_start/window_end defined by prev/next call dates. `bidask_spread_change.py` uses [-3,-1]/[+1,+3] around the call. | **Low** | Not discussed | This is actually a feature, not a bug -- using pre-call volatility as a control is standard. But the audit should note the different time horizons for clarity. | Add note in Section C about the volatility measurement window |
| G5 | Reproducibility | **No fresh results exist.** The audit presents pre-redesign results (6 IVs, N=37,657) that cannot be reproduced by the current code (4 IVs). The audit honestly discloses this but the implication is that the suite has NOT been verified end-to-end post-redesign. | Section E note: "A fresh run is needed to update these results" | **High** | The audit was written during the redesign before a fresh run could complete. This is a timing issue, not an oversight. | Committee cannot evaluate H14 results until a fresh run is executed. The stale results include clarity residuals that no longer exist in the code. | Execute fresh run immediately; update Section E with actual results |
| G6 | Winsorization | **Winsorization computed on full panel (112K rows) including Finance/Utility, but regression uses Main sample only.** Winsorization percentiles include observations that are excluded from the regression sample. | Builder lines 202-203: winsorize on full panel. Runner line 214: filter to Main. | **Low** | Not discussed | Winsorization cutoffs are influenced by Finance/Utility firms' spread characteristics, which may differ from Main-sample firms. Impact is likely minimal. | Note this in Section G or winsorize after sample filtering |
| G7 | Event window | **Minimum valid days threshold is window-dependent, not constant.** `min_pre = max(1, w-1)` for window size w=3 means min_pre=2, min_post=2. This means a call with only 2 of 3 pre-window trading days still gets a DSPREAD value. | `bidask_spread_change.py` lines 300-302: `min_pre = max(1, w - 1)` | **Low** | Not documented | With 2/3 valid days, the pre-window average is noisier. Standard practice is to require at least w days. This is a minor relaxation that increases coverage at the cost of precision. | Document the minimum-days rule in Section A |
| G8 | Academic integrity | **The pre-4IV results section includes CEO Clarity Residual, which showed positive significance.** This finding (positive beta for clarity -> wider spreads, opposite to theory) is theoretically puzzling and was dropped from the current code. The audit does not explain WHY clarity residuals were removed. | Section E results table shows CEO Clarity with 4/4 sig | **Low** | Audit presents the stale results without explaining the methodological rationale for removing clarity residuals from the redesigned suite | A referee might wonder if clarity was removed because it produced embarrassing results (p-hacking concern). The rationale should be stated. | Add brief note explaining why clarity residuals were removed (theoretical focus, parsimony, etc.) |

---

## H. Severity Recalibration

| ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|----|--------|-------------------|-------------------|------------------|---------------|
| G1 | Red-team | -- | **Medium** | MIN_CALLS_PER_FIRM=5 is standard in panel FE estimation; omission from documentation is a completeness gap, not a methodological flaw | Documentation gap |
| G2 | Red-team | -- | **Medium** | LINKPRIM inconsistency across builders is a real but likely low-impact issue; secondary CCM links are rare for well-covered firms | Methodological inconsistency; small impact |
| G3 | Red-team | -- | **Medium** | Fiscal-year FE is a defensible choice but should be documented with rationale | Specification choice gap |
| G5 | Red-team | -- | **High** | No fresh results mean the suite has not been verified post-redesign. This is the most material gap. | Cannot evaluate H14 findings |
| G6 | Red-team | -- | **Low** | Full-panel winsorization vs Main-sample winsorization is unlikely to change results materially | Negligible impact |
| E1 | First audit | -- | **Medium** | Stale results are honestly flagged but still prominently presented | Potential confusion |
| E3 | First audit | -- | **Medium** | Incomplete LINKPRIM fix documentation | Misleading provenance |

---

## I. Completeness Gaps

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|--------------------------|----------------|----------|----------|-------------------------------|
| MIN_CALLS_PER_FIRM filter | Not mentioned anywhere | Runner line 121: `MIN_CALLS_PER_FIRM = 5` | **Medium** | Document the filter and its rationale in Section A |
| CCM LINKPRIM consistency across builders | Not discussed | StockPriceBuilder and TurnoverBuilder lack LINKPRIM filter | **Medium** | Document which builders use LINKPRIM and why |
| Multi-call-per-fiscal-year implications | Not discussed | `set_index(["gvkey", "fyearq_int"])` with ~4 calls/firm/year | **Medium** | Discuss why fiscal-year (not quarter) FE is used |
| Fresh results from current code | Honestly flagged as missing | No fresh run post-redesign | **High** | Execute fresh run and update Section E |
| Merge strategy (zero-row-delta enforcement) | Not documented | Builder line 168-169 raises ValueError on merge row delta | **Low** | Mention in pipeline documentation |
| Minimum valid trading days rule | Not documented | `min_pre = max(1, w-1)` = 2 of 3 days minimum | **Low** | Document in Section A DV construction |
| Rationale for removing clarity residuals | Not documented | Clarity removed from 6-IV to 4-IV design without explanation | **Low** | Brief note in Section F bug fixes |
| Summary statistics verification | No distribution statistics table | Audit has no variable-level summary stats | **Low** | Add descriptive statistics table for key variables |
| Sample attrition chain | Only output listed, not documented in audit | `sample_attrition.csv` listed in outputs but no attrition discussion | **Medium** | Document expected attrition stages: full panel -> Main filter -> DV non-null -> complete cases -> min calls |

---

## J. Reproducibility Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|-------------------|------------------------|-----------|-------------------|------|---------------|
| Stage 3: build panel | Y (pipeline section H) | Y (command correct) | Y: requires manifest, CRSP, Compustat, IBES, linguistic engine outputs | Medium | `get_latest_output_dir` resolves dynamically |
| Stage 4: run regressions | Y (pipeline section H) | Y (command correct) | Y: requires Stage 3 output | Low | |
| Configuration files | Not mentioned | Not verified | Y: `config/project.yaml`, `config/variables.yaml` | Medium | Builder reads these at lines 321-322 |
| Package versions | Not mentioned | N/A | Y: no pinning | Low | linearmodels, pandas, numpy versions not specified |
| Determinism | Not tested | Not verified | Unknown | Low | PanelOLS is deterministic |
| Full end-to-end from clean state | N (not tested) | N | Y: all upstream stages needed | High | Would need manifest builder, CRSP/Compustat/IBES downloads |
| Output directory resolution | Not documented | Y | Y: `get_latest_output_dir` uses filesystem timestamps | Low | Could resolve to wrong run if multiple outputs exist |

---

## K. Econometric Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|-------------------|----------------------|----------------|----------------------|----------|
| DV construction | **Y** | Lee (2016) correctly cited; closing BID/ASK confirmed; trading-day windows verified | Minimum valid days threshold (2/3) not documented | **Low** |
| IV definition | **Y** | 4 uncertainty measures from LinguisticEngine Stage 2 | Coverage rates noted (70-97%) | -- |
| Identification strategy | **Partial** | Horse-race design is standard; but no discussion of endogeneity threats specific to H14 | No placebo test in current code; no IV/instrument discussion; reverse causality not addressed (firms with wider spreads may host calls with more uncertain language due to market stress) | **Medium** |
| FE structure | **Y** | Industry/Firm + FiscalYear correctly implemented | Fiscal-year vs fiscal-quarter FE choice not justified | **Medium** |
| Clustering | **Y** | Firm-clustered SEs appropriate for call-level panel | | -- |
| Control variable adequacy | **Y** | PreCallSpread as lagged-DV control is the key design choice; microstructure controls (StockPrice, Turnover, Volatility) appropriate | No institutional ownership or analyst coverage controls | **Low** |
| Post-treatment bias | **Y** | All controls are pre-treatment (pre-call or contemporaneous accounting) | PreCallSpread [-3,-1] is same window as pre-call spread in DV; this is a lagged-DV control, which is defensible but could mechanically reduce estimated effects | **Low** |
| Robustness design | **Missing** | No robustness tests in current code (removed during redesign) | Prior code had 174-spec grid including placebo; current code has none. This is a significant regression. | **High** |
| Multiple testing | **Not addressed** | 4 IVs tested simultaneously but no Bonferroni/FDR discussion | With 4 IVs x 4 specs = 16 tests, a 5% threshold yields ~1 expected false positive | **Medium** |
| Economic significance | **Not addressed** | No discussion of economic magnitude of coefficients | Coefficients in the 0.0001-0.0005 range; economic interpretation unclear | **Medium** |

---

## L. Audit-Safety Assessment

| Audit-safety risk | Evidence | Severity | Why it matters | Fix |
|-------------------|----------|----------|----------------|-----|
| **Stale results presented as primary findings** | Section E explicitly states "pre-4IV run" but the table is the only results table in the document | **High** | A reader skimming the audit might take these as current results. CEO Clarity Residual findings (4/4 sig) are especially misleading since clarity is no longer in the code. | Run the current code and replace the results table, or clearly section-off stale results with a header like "STALE -- DO NOT CITE" |
| **Bug-fix table overstates LINKPRIM fix scope** | Section F says "Added linkprim in [P,C] filter" without noting it was only added to BidAskSpreadChangeBuilder | **Medium** | A reader would believe all CRSP builders have LINKPRIM filtering; StockPriceBuilder and TurnoverBuilder do not | Correct the bug-fix description to scope the fix to the DV builder only |
| **No robustness tests in redesigned code** | Previous version had 174-spec grid; current version has none | **Medium** | The redesign simplified the specification grid but also removed all robustness infrastructure including placebo tests | Plan for robustness additions post-redesign |
| **No discussion of prior red-team findings** | Prior red-team audit (Audits/H14_red_team.md) identified critical issues including placebo failure; current audit does not reference or address these | **Low** | The prior red-team is now stale (pre-redesign) so this is partially excused, but the thesis committee should know what issues existed and how the redesign addressed them | Add brief note referencing prior audit and how redesign addresses its findings |

---

## M. Master Issue Register

| ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis reliance? |
|----|------|----------|-----------|----------|----------|-------------|----------|-------------|-----------------|------------------------|
| RT-1 | Audit completeness gap | Results | Y | **High** | Section E | No fresh results from current 4-IV code; stale 6-IV results cannot be reproduced | Code has 4 IVs; results table has 6 IVs | Cannot evaluate H14 hypothesis with current code output | Run fresh pipeline; update results | **Y** (until fresh run) |
| RT-2 | Audit omission | Sample construction | Y | **Medium** | Not in audit | MIN_CALLS_PER_FIRM=5 filter not documented | Runner line 121 | Committee unaware of this sample restriction | Add to Section A | N |
| RT-3 | Implementation inconsistency | CCM linkage | Y | **Medium** | bidask_spread_change.py vs stock_price.py, turnover.py | BidAskSpreadChangeBuilder has LINKPRIM filter; StockPriceBuilder and TurnoverBuilder do not | Code inspection of `_build_permno_map` in each builder | DV and controls may use different PERMNOs for same firm | Add LINKPRIM to all builders or document rationale | N |
| RT-4 | Audit factual error | Bug-fix table | Y | **Medium** | Section F | "Added linkprim filter" overstates scope -- only added to DV builder | StockPriceBuilder/TurnoverBuilder lack LINKPRIM | Misleading provenance claim | Correct scope description | N |
| RT-5 | Audit completeness gap | Econometric specification | Y | **Medium** | Not in audit | Fiscal-year FE with ~4 calls per firm per year not discussed | set_index(["gvkey", "fyearq_int"]) | Referee would ask about quarterly seasonality control | Document rationale; consider quarter FE robustness | N |
| RT-6 | Design regression | Robustness | Y | **Medium** | Not in code | All robustness tests (placebo, alternative windows, alternative DVs) removed in redesign | No robustness/placebo code in current runner | No robustness evidence available for thesis | Plan and implement robustness tests | N (if results are null) |
| RT-7 | Audit completeness gap | Sample attrition | Y | **Medium** | Not in audit body | Attrition stages not documented in the audit text (only listed as output file) | `generate_attrition_table` at runner line 724 produces file but audit doesn't discuss | Committee doesn't see attrition chain | Add attrition summary to audit | N |
| RT-8 | Audit presentation | Stale results | Y | **Medium** | Section E | Pre-4IV results including CEO Clarity prominently displayed; could mislead | Clarity residuals removed from current code | Reader might cite stale CEO Clarity finding | Mark as "HISTORICAL ONLY" or remove | N |

---

## N. What Committee Would Not Know

1. **No post-redesign results exist.** The audit presents results from a prior version of the code with 6 IVs. The current code has 4 IVs and will produce different sample sizes and coefficients. A committee member reading the audit would see results that cannot be reproduced from the current code.

2. **Firms with fewer than 5 calls are excluded.** The `MIN_CALLS_PER_FIRM = 5` filter is applied at the runner level but not documented in the audit. This could bias the sample toward larger, longer-listed firms.

3. **LINKPRIM filtering is inconsistent across CRSP builders.** The DV (DSPREAD) uses primary CCM links only, while the extended controls (StockPrice, Turnover) use all CCM links. This means the same firm-call could be mapped to different PERMNOs for different variables.

4. **Fiscal-year time FE means quarterly seasonality is not absorbed.** With ~4 calls per firm per fiscal year, the fiscal-year FE does not control for within-year seasonal patterns in bid-ask spreads or earnings-call uncertainty.

5. **All robustness tests were removed in the redesign.** The prior version had a 174-specification robustness grid including placebo tests. The current code has zero robustness tests. The prior red-team audit found that the only significant finding (CEO_Pres, p=0.024) failed the placebo test (placebo beta 2.8x primary) and did not survive alternative DV constructions.

6. **The prior red-team audit raised thesis-blocking concerns.** The Audits/H14_red_team.md (dated 2026-03-15) found that the old H14 produced null results across all measures when the placebo failure was properly accounted for. The redesign addressed some issues (removed clarity residuals, simplified specification grid) but the fundamental question -- does uncertainty predict spread changes? -- has not been re-evaluated with fresh results.

---

## O. Priority Fixes

| Priority | Fix | Why it matters | Effort | Credibility gain |
|----------|-----|----------------|--------|------------------|
| 1 | **Execute fresh run of current 4-IV pipeline and update Section E results** | The audit cannot be evaluated without current results. This is the single most important gap. | Medium (run pipeline ~5-10 min) | **Critical** |
| 2 | **Document MIN_CALLS_PER_FIRM=5 filter in Section A** | Material sample restriction omitted from documentation | Low (text edit) | **Medium** |
| 3 | **Correct bug-fix table (Section F) to scope LINKPRIM fix to BidAskSpreadChangeBuilder only** | Currently overstates the scope of the fix | Low (text edit) | **Medium** |
| 4 | **Add LINKPRIM filter to StockPriceBuilder and TurnoverBuilder or document why omitted** | Methodological inconsistency within the suite | Low (code edit) | **Medium** |
| 5 | **Add discussion of fiscal-year vs fiscal-quarter FE choice** | Referee will ask about this | Low (text addition) | **Medium** |
| 6 | **Plan and implement robustness tests (placebo, alternative windows, alternative spread formula)** | Redesign removed all robustness infrastructure; critical for thesis credibility | Medium-High (code) | **High** |
| 7 | **Add sample attrition chain to audit body** | Standard thesis documentation requirement | Low (copy from output file) | **Low** |
| 8 | **Mark stale pre-4IV results clearly or remove them** | Prevent confusion about current findings | Low (text edit) | **Low** |

---

## P. Final Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
Not yet. The audit is well-structured and technically accurate on most implementation claims, but it presents stale results from a prior code version and omits several material details (MIN_CALLS_PER_FIRM filter, LINKPRIM inconsistency, fiscal-year FE rationale). The most critical gap is the absence of fresh results from the redesigned 4-IV code.

**What is its biggest factual weakness?**
The bug-fix table (Section F) overstates the LINKPRIM fix scope. BidAskSpreadChangeBuilder has the LINKPRIM filter, but StockPriceBuilder and TurnoverBuilder do not. This is a verifiable factual error in the audit.

**What is its biggest completeness weakness?**
No fresh results from the current code. The entire Section E results table is from a pre-redesign run with 6 IVs that cannot be reproduced by the current 4-IV code. A committee cannot evaluate H14 without current results.

**What is its biggest severity/judgment weakness?**
The audit presents the stale CEO Clarity Residual finding (4/4 significant with positive coefficient, contrary to theory) without explaining why clarity was removed from the redesigned code. This could raise p-hacking concerns if not addressed.

**What is the single most important action item?**
Execute a fresh run of the redesigned 4-IV pipeline and update Section E with actual results. Until this is done, the audit is incomplete and the suite cannot be evaluated.

**What should a thesis committee believe after reading this red-team review?**
The H14 implementation is technically competent after the redesign. The Lee (2016) DV construction is correctly implemented using closing BID/ASK quotes, the 4-IV horse-race design is clean, and the 4-column specification grid (2 FE x 2 controls) follows the thesis-standard pattern. However, the suite has NOT been run post-redesign, so no current results exist. The prior version of H14 (with 6 IVs) produced essentially null results across all measures -- the one nominally significant finding (CEO_Pres, p=0.024) failed the placebo test and did not survive alternative DV constructions (per the prior red-team audit). The redesigned suite may produce different results due to the smaller IV set and potentially larger sample, but this cannot be evaluated until a fresh run is executed. The committee should treat H14 as "pending fresh results" and should be prepared for the possibility that the results remain null, consistent with the prior version's findings.
