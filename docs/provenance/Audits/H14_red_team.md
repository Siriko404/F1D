# Second-Layer Red-Team Audit: H14 — Language Uncertainty and Bid-Ask Spread Change

**Audit ID:** H14_red_team
**Date:** 2026-03-12
**Auditor:** Claude Code (claude-sonnet-4-6) — fresh context, adversarial posture
**Method:** Independent code inspection + claim-by-claim verification against source

---

## A. Red-Team Bottom Line

The first-layer H14 audit is **well-constructed overall** but contains one verifiable factual error in its description of the Clarity Residual skip mechanism, two medium-severity missed econometric concerns (panel index non-uniqueness risk; bad-control risk from AbsSurprise and PreCallSpread), and one overconfident inference claim. The audit's identification of the ASKHI/BIDLO spread proxy deficiency, the reverse causality threat, and the robustness deficit are all correct and appropriately prioritized.

The first audit **predominantly understated risk** in two areas it did not cover: (1) the composite panel index `(gvkey, quarter_index)` uniqueness was not verified, which is a correctness prerequisite for PanelOLS; (2) AbsSurprise and PreCallSpread are potential bad controls that attenuate the uncertainty coefficient, which partially explains the null result and was not raised.

**Overall grade for the first-layer audit:** **PARTIALLY RELIABLE**
The core facts (model family, FE spec, formula, variable construction, null result) are verified correct. One factual error in the code-path description exists. Two material econometric concerns are absent.

**Suite as implemented:** **SALVAGEABLE WITH MAJOR REVISIONS**
The null result may be genuine, but the non-standard spread proxy (ASKHI/BIDLO daily range) and absence of robustness tests mean it cannot be defended at thesis standard without revision.

**Risk direction:** Mixed — mostly understated risk on identification/bad-controls; minor overstated risk on SE adequacy.

---

## B. Scope and Objects Audited

| Item | Path |
|---|---|
| Suite ID | H14 |
| Suite entrypoint | `src/f1d/econometric/run_h14_bidask_spread.py` |
| Panel builder | `src/f1d/variables/build_h14_bidask_spread_panel.py` |
| First-layer audit | `docs/provenance/H14.md` (480 lines, 2026-03-12) |
| DV builder | `src/f1d/shared/variables/bidask_spread_change.py` |
| Clarity residual engine | `src/f1d/shared/variables/_clarity_residual_engine.py` |
| CEO clarity residual builder | `src/f1d/shared/variables/ceo_clarity_residual.py` |
| Manager clarity residual builder | `src/f1d/shared/variables/manager_clarity_residual.py` |
| Stock price builder | `src/f1d/shared/variables/stock_price.py` |
| Panel utilities | `src/f1d/shared/variables/panel_utils.py` (assign_industry_sample, attach_fyearq) |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer status | Evidence basis | Red-team note |
|---|---|---|---|
| Model/spec identification | **Pass** | Run script lines 80–105, formula at line 198–202; verified PanelOLS, EntityEffects+TimeEffects, 6 measures | Correct |
| Reproducibility commands | **Partial** | Commands documented; but `latest` symlink resolution makes runs non-deterministic; H0.3 dependency for specs 5–6 not reproducible from H14 alone | First audit flags this; no new finding |
| Dependency tracing | **Partial** | All builders listed; CCM code duplication across 3 CRSP builders not noted; `get_latest_output_dir` exception-type gap not noted | See RT-MI-02, RT-UC-01 |
| Raw data provenance | **Pass** | CRSP, CCM, Compustat, IBES, manifest all documented with paths | Correct |
| Merge/sample audit | **Pass** | Zero-row-delta enforcement verified (lines 143–147); many-to-many risk documented as absent | Correct |
| Variable dictionary completeness | **Pass** | All 16 variables documented with formula, timing, source | Correct |
| Outlier/missing-data rules | **Partial** | DV not winsorized flagged correctly; AbsSurprise bad-control risk missing; PreCallSpread reverse-causality absorption not mentioned | See RT-MI-03, RT-MI-04 |
| Estimation spec register | **Pass** | All 6 specs with N, clusters, FE documented | Correct |
| Verification log quality | **Pass** | 17 commands documented with outputs; N counts and betas verified | Correct |
| Known issues section | **Pass** | 7 issues (J1–J7) documented; all verified as genuine | Correct |
| Identification critique | **Partial** | Reverse causality and OVB flagged; bad-control mechanism through AbsSurprise and PreCallSpread not raised | See RT-MI-03, RT-MI-04 |
| Econometric implementation critique | **Partial** | FE/SE structure verified correct; panel index non-uniqueness not checked | See RT-MI-01 |
| Robustness critique | **Pass** | Correctly rated as inadequate; 10 missing robustness items enumerated | Correct |
| Academic-integrity critique | **Pass** | Clarity Residual stale artifact, no manifest linking Stage 3→4, ASKHI/BIDLO disclosure | Correct |
| Severity calibration | **Partial** | L1 (ASKHI/BIDLO) and L2 (reverse causality) correctly at High; SE claim overconfident; RT-MI-01 missing entirely | See RT-OS-01 |
| Final thesis verdict support | **Pass** | "NOT THESIS-STANDARD AS IMPLEMENTED" verdict justified by issue register | Correct |

---

## D. Claim Verification Matrix

| Claim ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|---|---|---|---|---|---|---|
| CL-01 | Estimator is `PanelOLS` with `drop_absorbed=True` | A2 | Y | `run_h14_bidask_spread.py` lines 214–215 | VERIFIED FACT | Exact code confirmed |
| CL-02 | Formula: `delta_spread ~ {IV} + Size + StockPrice + Turnover + Volatility + PreCallSpread + AbsSurprise + EntityEffects + TimeEffects` | A2 | Y | Lines 198–202 | VERIFIED FACT | |
| CL-03 | Time FE uses `quarter_index = year * 4 + quarter` | A2, A5 | Y | `prepare_regression_data()` lines 161; `build_h14_bidask_spread_panel.py` lines 156–160 | VERIFIED FACT | |
| CL-04 | Clustering: `cov_type="clustered"`, `cluster_entity=True` | A5 | Y | Line 215 | VERIFIED FACT | |
| CL-05 | delta_spread = `2*(ASKHI−BIDLO)/(ASKHI+BIDLO)` using daily high ask / low bid | A3, F | Y | `bidask_spread_change.py` lines 6–9, 280–287 | VERIFIED FACT | |
| CL-06 | Pre/post windows: ±3 trading days; min 2 valid days each window | A3, F | Y | `bidask_spread_change.py` lines 31–32, 324–325, 344–349 | VERIFIED FACT | |
| CL-07 | 6 uncertainty measures in `UNCERTAINTY_MEASURES` list | A4 | Y | `run_h14_bidask_spread.py` lines 97–105 | VERIFIED FACT | Docstring says "(4)" — first audit correctly flags as J1 |
| CL-08 | Listwise deletion via `dropna(subset=required)` BEFORE min-calls filter | E2 | Y | `run_regression()` lines 187–191 | VERIFIED FACT | |
| CL-09 | Min-calls filter: `call_counts >= 5` applied AFTER listwise deletion | A4, E2 | Y | Lines 189–191 | VERIFIED FACT | |
| CL-10 | Zero-row-delta enforcement in panel builder | E1 | Y | `build_h14_bidask_spread_panel.py` lines 143–147 | VERIFIED FACT | |
| CL-11 | `StockPriceBuilder` rename `"stock_price"→"StockPrice"` is no-op (J2) | J, F | Y | `stock_price.py` line 229: `combined.rename(columns={"PRC": "StockPrice"})` returns `StockPrice` directly | VERIFIED FACT | No-op confirmed; builder returns `StockPrice` already |
| CL-12 | AbsSurprise double-abs is redundant (J3) | J | Y | `ceo_clarity_residual.py` already abs; `build_h14_bidask_spread_panel.py` line 173 applies again | VERIFIED FACT | |
| CL-13 | Clarity Residual builders catch `FileNotFoundError` and return empty DataFrame | B, K7 | Y | `ceo_clarity_residual.py` lines 41–52; `manager_clarity_residual.py` lines 41–52 | VERIFIED FACT (mechanism correct); VERIFIED ERROR (skip pathway wrong) | The builder DOES catch FileNotFoundError and return empty DataFrame — first audit is correct on that. But first audit wrongly says specs skip via `if uncertainty_var not in df_sample.columns` — see RT-FE-01 |
| CL-14 | `_skip_winsorization = True` in `CEOClarityResidualBuilder` | G | Y | `ceo_clarity_residual.py` line 36 | VERIFIED FACT | |
| CL-15 | No winsorization of delta_spread, Turnover, Volatility, StockPrice | G | Y | No winsor calls in `run_h14_bidask_spread.py` or `build_h14_bidask_spread_panel.py` | VERIFIED FACT | |
| CL-16 | `assign_industry_sample`: Finance if ff12_code==11; Utility if ff12_code==8; else Main | A4 | Y | `panel_utils.py` lines 67–73 | VERIFIED FACT | NaN codes default to Main (np.select default) — correctly stated |
| CL-17 | `attach_fyearq` called in panel builder; `fyearq` not used in Stage 4 | C, J | Y | `build_h14_bidask_spread_panel.py` line 163; panel load in run script lists explicit columns that do not include `fyearq` | VERIFIED FACT | |
| CL-18 | All 6 specs null: β ≈ 0, all p(one-tailed) > 0.45 | I, K1 | Y (artifact) | `model_diagnostics.csv` run 2026-03-10_215618 referenced | VERIFIED (trust artifact) | Not independently re-run (no execution possible), but artifact path documented |
| CL-19 | 1,340–1,587 clusters (adequate for cluster inference) | K3 | Y | N_clusters by spec in Section E2 table | VERIFIED FACT (count) — overclaimed (adequacy) | See RT-OS-01 |
| CL-20 | Specs 5-6 "skip" via `if uncertainty_var not in df_sample.columns` | B, K7 | N | `ceo_clarity_residual.py` lines 41–52; merge logic in builder | VERIFIED ERROR IN FIRST AUDIT | See RT-FE-01 |
| CL-21 | `attach_fyearq` asserts file_name uniqueness; raises ValueError if <80% match | C | Y | `panel_utils.py` lines 117–128, 109–111 | VERIFIED FACT | Important guard not flagged by first audit as a positive data quality control |
| CL-22 | ClarityResidualEngine `get_latest_output_dir` searches `outputs/econometric/ceo_clarity_extended/` | D, K7 | Y | `_clarity_residual_engine.py` lines 43–46 | VERIFIED FACT | |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| Issue ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|---|---|---|---|---|---|
| RT-OS-01 | "Firm-clustered SEs with 1,340–1,587 clusters are adequately large for cluster inference. No concern about SE underestimation." (Section K3) | "No concern" is too strong. The claim correctly identifies adequate cluster count for within-firm serial correlation, but ignores cross-sectional dependence (e.g., market-wide liquidity shocks during 2008 crisis affecting all firms simultaneously). One-way firm clustering does not address this. | Low-Medium | Petersen (2009) / Cameron & Miller (2015) both note that if residuals are correlated within time periods as well as within entities, one-way entity clustering can under-estimate SEs. The audit does not test for time-period correlation in residuals. | "Firm-clustered SEs with 1,340+ clusters are adequate to address within-firm serial correlation. Cross-sectional dependence (time-period correlation) is unaddressed and may cause SE underestimation under market-wide liquidity shocks. Double-clustering (firm + year-quarter) should be tested." |
| RT-OS-02 | "NaN if H0.3 not run" in Section E1 notes for Clarity Residual merges (e.g., "62.4% missing if H0.3 not run") | The 62.4% figure is for when H0.3 IS run (valid observations in full panel); the claim conflates missingness when H0.3 is run versus when it is not. If H0.3 has not been run, the entire column would be NaN (100% missing), not 62.4%. The first audit acknowledges this in Section D but the E1 table phrasing is ambiguous. | Low | Distinguish: (a) missingness when H0.3 IS available but some file_names lack a residual match (62.4% / 48.8%); vs (b) missingness when H0.3 HAS NOT been run (100%). | Clarify: "62.4% missing is the observed rate when H0.3 has been run; 100% missing if H0.3 has not been run at all." |
| RT-OS-03 | Section B states specs 5–6 "will silently fall back to empty DataFrames" | "Silent" is misleading. The engine logs `print(f"ClarityResidualEngine: Loading from {output_dir}")` before raising. The builders print nothing additional on catch, but the build loop prints each builder name. The panel build does not raise an error, so "no error raised" is correct — but the process is not entirely silent. | Low | No explicit "WARNING: Clarity Residual not found" is emitted — the silent aspect refers to no error/warning printed to stderr, which is accurate for the catch path | Refine to: "Builders return empty DataFrame with no stderr warning; the build continues without notification that specs 5–6 will be empty." |

---

## F. False Positives in the First Audit

| Issue ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|---|---|---|---|---|---|
| No material false positives identified. | All issues J1–J7 and L1–L14 verified as genuine. | — | — | — | — |

---

## G. Missed Issues (Second-Layer Discoveries)

| Issue ID | Category | Description | Evidence | Severity | Why first audit missed/underplayed it | Consequence | Recommended fix |
|---|---|---|---|---|---|---|---|
| RT-MI-01 | Econometric implementation | **Panel index non-uniqueness risk.** PanelOLS requires unique `(entity, time)` pairs. The index is `(gvkey, quarter_index)`. If any firm has ≥2 calls in the same quarter, the index is non-unique. The first audit verifies `file_name` uniqueness (0 duplicates) and cell counts by spec, but does NOT verify that `(gvkey, quarter_index)` is unique. With ~46.5 calls per firm over ~40 active quarters, most firms average exactly 1 call/quarter, but edge cases exist (special calls, restated transcripts, annual shareholder meetings). `linearmodels.PanelOLS` with a non-unique multi-index produces incorrect FE estimates without raising an error. | `run_regression()` lines 211–214; `run_h14_bidask_spread.py`. `panel["file_name"].duplicated().sum()` = 0 confirmed, but `(gvkey, quarter_index)` uniqueness NOT verified in code or first audit verification log. | **Medium** | First audit verified file_name uniqueness but did not extend the check to the composite panel index required by PanelOLS. | If duplicates exist, FE partitioning is incorrect; within-R² and clustered SEs may be unreliable. If no duplicates exist (likely), no impact — but this must be verified. | `assert df_reg.set_index(["gvkey","quarter_index"]).index.is_unique`, log count of duplicates before PanelOLS call |
| RT-MI-02 | Data provenance / merge integrity | **CCM permno_map built independently by 3 separate builders.** `BidAskSpreadChangeBuilder`, `StockPriceBuilder`, and `TurnoverBuilder` each independently run `_build_permno_map()` against the CCM file. While the code appears identical in the two inspected builders, a divergence (e.g., from a future code update to one builder) could silently assign different permnos to the same call for different variables. The first audit notes "each builds permno_map independently" but does not flag the cross-builder consistency risk. | Code inspection: `bidask_spread_change.py` lines 94–167; `stock_price.py` lines 80–153. Both have identical `_build_permno_map` logic. TurnoverBuilder not independently inspected here. | **Low-Medium** | The first audit describes the builders without checking for silent divergence risk between builders. | If builders disagree on permno for a given call, DV (delta_spread) uses a different PERMNO than controls (StockPrice, Turnover). Cross-variable contamination. | Centralize permno_map into CRSPEngine or manifest; add assertion that StockPrice/Turnover/BidAsk permnos match per file_name |
| RT-MI-03 | Identification / bad controls | **AbsSurprise as potential bad control.** AbsSurprise is the absolute earnings surprise for the SAME announcement being discussed in the call. If the causal chain is: earnings shock → manager uses uncertain language + market widens spreads, then controlling for AbsSurprise removes the primary mechanism of interest, biasing the uncertainty coefficient toward zero. This is a textbook bad-control problem. The first audit flags AbsSurprise's IBES coverage gap (24.8% missing, causing ~25k obs dropped) but does NOT flag its role as a potential mechanism control that absorbs the causal channel. | Study design: `BASE_CONTROLS` in `run_h14_bidask_spread.py` line 87–94; AbsSurprise formula: `|ACTUAL−MEANEST|/|MEANEST|`. AbsSurprise and uncertainty language are determined jointly at the earnings announcement — they are not causally separated. | **Medium** | First audit focuses on AbsSurprise as a coverage/missing-data issue, not as an identification threat. The bad-control framing is absent from Section K2. | If AbsSurprise absorbs the earnings-news channel, the uncertainty coefficient measures only the component of uncertainty orthogonal to the surprise. This may explain null results. Removing AbsSurprise from the spec is an important robustness check. | Run spec 1 without AbsSurprise; compare coefficient and N. Document if AbsSurprise inclusion vs. exclusion changes results materially. |
| RT-MI-04 | Identification / bad controls | **PreCallSpread as partial absorber of reverse-causality channel.** PreCallSpread = mean spread over [-3,-1] trading days. If firms facing anticipated spread widening (e.g., pre-announcement illiquidity) simultaneously speak more uncertainly on the call, PreCallSpread captures the pre-call liquidity state that reverse-causes uncertainty. Controlling for it partially neutralizes the reverse-causality threat but also absorbs the signal, biasing uncertainty coefficient toward zero. The first audit flags reverse causality in K2 but does not discuss PreCallSpread's role in this mechanism. | `BASE_CONTROLS` includes `PreCallSpread`; reverse causality concern is Section K2. The two are not connected in the first audit. | **Low-Medium** | First audit mentions reverse causality and PreCallSpread in separate sections without connecting them. | If high-illiquidity firms (high PreCallSpread) have more uncertain language, the FE+PreCallSpread regression removes this signal. The null result could partially reflect over-controlling. | Run sensitivity without PreCallSpread; document the trade-off (reverse causality control vs. coefficient attenuation). |
| RT-MI-05 | Reproducibility / exception handling | **`get_latest_output_dir` exception type is not guaranteed `FileNotFoundError`.** When `ceo_clarity_extended` directory does not exist at all (first-time run or clean environment), `get_latest_output_dir` may raise something other than `FileNotFoundError` (e.g., `NotADirectoryError`, custom `ValueError`, or `OSError`). Both Clarity Residual builders only catch `FileNotFoundError`. A different exception type propagates up and crashes the entire Stage 3 panel build — not silently returning empty. The first audit does not inspect `get_latest_output_dir`'s exception behavior. | `_clarity_residual_engine.py` line 46: `return get_latest_output_dir(base_dir)`. Builders: `ceo_clarity_residual.py` lines 41–52: only `except FileNotFoundError`. `get_latest_output_dir` not inspected. | **Low-Medium** | First audit only reads the builder-level catch, not the upstream `get_latest_output_dir` implementation. | In a clean environment without H0.3 output, Stage 3 could crash rather than silently omit specs 5–6, making the fallback behavior unreliable. | Broaden catch in builders to `except (FileNotFoundError, OSError, ValueError)` or inspect and document what `get_latest_output_dir` raises on missing directory. |
| RT-MI-06 | Variable construction | **Possible NaN propagation in spread mean when trading days have NaN BIDLO/ASKHI.** In `_process_year_calls`, spread is set to NaN for days with ASKHI=0 or BIDLO=0. The aggregation `pre_call_spread=("spread","mean")` uses pandas default which skips NaN — so a 3-day pre-window with 2 valid days and 1 NaN gives a 2-day mean. If `pre_n_valid ≥ 2`, this passes the minimum-days filter and produces a valid DV. This behavior is correct but is not documented in the first audit's variable dictionary entry for `delta_spread`. | `bidask_spread_change.py` lines 279–287 (spread NaN for invalid CRSP rows); lines 328–336 (mean aggregation). `MIN_PRE_DAYS = MIN_POST_DAYS = 2`. | **Low** | First audit verifies min-days logic but does not describe that the mean uses the valid-day subset (not requiring all 3 days). | No material error; behavior is reasonable. But the DV formula in the paper should state "mean over up to 3 trading days, requiring ≥2 with valid CRSP bid-ask quotes." | Add note to variable dictionary entry: "Spread mean computed over available valid-quote days; min 2 required per window; may use 2 or 3 days." |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|---|---|---|---|---|---|
| L1 (ASKHI/BIDLO spread proxy) | First audit | High | **High** (confirmed) | Non-standard spread measure; daily range ≠ effective spread; confirmed material | Yes — primary DV validity concern |
| L2 (reverse causality) | First audit | High | **High** (confirmed) | Correctly flagged; enhanced by RT-MI-04 (PreCallSpread as absorber) | Yes |
| L3 (no robustness tests) | First audit | High | **High** (confirmed) | Robustness deficit is accurately described | Yes |
| L4 (no winsorization DV/controls) | First audit | Medium | **Medium** (confirmed) | Turnover max 20× p99 is material; null result partially insulates but OLS is sensitive | Yes (for credibility) |
| L5 (Clarity Residuals cross-suite dependency) | First audit | Medium | **Medium** (confirmed) | Correctly flagged | Partial |
| L6 (docstring count "(4)" vs. 6) | First audit | Medium | **Medium → Low-Medium** | Downgrade: purely documentary error; no estimation impact; low referee risk | No |
| L7 (no multiple-testing correction) | First audit | Medium | **Low** (downgrade) | All null; correction irrelevant when no tests are significant; noted for future use only | No (currently) |
| L8 (one-way clustering only) | First audit | Medium | **Medium** (confirmed, enhanced by RT-OS-01) | RT-OS-01 adds cross-sectional dependence concern during crisis periods | Yes |
| L9 (no-op StockPrice rename) | First audit | Low | **Low** (confirmed) | | No |
| L10 (AbsSurprise double-abs) | First audit | Low | **Low** (confirmed) | | No |
| L11 (latest-dir reproducibility) | First audit | Low | **Low** (confirmed) | | No |
| L12 (asymmetric winsorization) | First audit | Low | **Low** (confirmed) | | No |
| L13 (Finance/Utility excluded) | First audit | Low | **Low** (confirmed) | | No |
| L14 (min-calls post-listwise) | First audit | Low | **Low** (confirmed) | | No |
| **RT-MI-01** (panel index non-uniqueness) | Red-team | — | **Medium** | PanelOLS correctness prerequisite; not verified by first audit; unverified in code | Yes if duplicates exist |
| **RT-MI-02** (CCM cross-builder permno) | Red-team | — | **Low-Medium** | Implementation redundancy; identical logic reduces risk but not eliminated | Low |
| **RT-MI-03** (AbsSurprise bad control) | Red-team | — | **Medium** | Mechanism control concern; may explain null result | Yes |
| **RT-MI-04** (PreCallSpread absorbs reverse causality) | Red-team | — | **Low-Medium** | Exacerbates reverse-causality concern from L2; partially explains null | Yes (for interpretation) |
| **RT-MI-05** (exception type in ClarityResidualEngine) | Red-team | — | **Low-Medium** | Reproducibility in clean environments | No |
| **RT-MI-06** (NaN propagation in spread mean) | Red-team | — | **Low** | Behavior correct but undocumented | No |
| **RT-FE-01** (skip mechanism description error) | Red-team | — | **Low** (factual error in first audit) | Code path incorrectly described; practical outcome identical | No |
| **RT-OS-01** (SE adequacy overclaim) | Red-team | — | **Low-Medium** (overstatement in first audit) | "No concern" too strong; cross-sectional dependence unaddressed | Partial |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|---|---|---|---|---|
| Panel index uniqueness verification | Verification log (Section I) verifies `file_name` uniqueness but not `(gvkey, quarter_index)` uniqueness. PanelOLS requires unique composite index. | `run_regression()` line 211: `df_reg.set_index(["gvkey","quarter_index"])`. Check not in verification log. | Medium | Add: `assert df_reg.set_index(["gvkey","quarter_index"]).index.is_unique` or `df_reg.duplicated(["gvkey","quarter_index"]).sum()` to verification log |
| AbsSurprise bad-control analysis | K2 (identification threats) lists reverse causality and OVB but does not frame AbsSurprise as a mechanism control | K2 table; `BASE_CONTROLS` in run script | Medium | Section on bad controls: discuss whether AbsSurprise, PreCallSpread, or Volatility could absorb the uncertainty→liquidity channel |
| Cross-builder CCM permno consistency | Section C lists all builders but doesn't test whether BidAskSpreadChangeBuilder, StockPriceBuilder, and TurnoverBuilder produce identical permno assignments | Section C; builders share code but are independent instances | Low-Medium | Add a single verification: join the output file_name→permno from DV builder vs. controls builder and check zero discrepancies |
| `get_latest_output_dir` behavior on missing directory | Section K7 documents builder's `FileNotFoundError` catch but doesn't verify what `get_latest_output_dir` itself raises when the base directory is absent | `_clarity_residual_engine.py` line 46 | Low-Medium | Read `path_utils.get_latest_output_dir`; document what exception it raises for absent directory |
| Volatility inter-call window boundary | Section F documents Volatility as `std(RET)*sqrt(252)*100` over `[prev_call_date+5, call_date-5]` but does not verify what happens for the first call per firm (no prior call exists) | `volatility.py` referenced; first-call edge case not discussed | Low | Document first-call handling in variable dictionary entry |
| Finance/Utility subsample sensitivity | Section K5 robustness table flags Finance and Utility as untested, but doesn't explicitly state the spec count difference (CONFIG only runs "Main") | `run_h14_bidask_spread.py` CONFIG line 83 | Low | State explicitly in the robustness table that Finance/Utility specs were designed and classified but deliberately not estimated |
| `attach_fyearq` 80% match-rate guard | First audit notes fyearq is added and unused, but does not document that `attach_fyearq` has a built-in data quality guard (raises ValueError if <80% rows match Compustat) | `panel_utils.py` lines 109–111 | Low | Positive: document that the 80% guard was triggered/passed during the panel build run as a data quality signal |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented? | Verified? | Hidden dependency? | Risk | Red-team note |
|---|---|---|---|---|---|
| `python -m f1d.variables.build_h14_bidask_spread_panel` | Y | Partial (code only; not executed) | Yes — requires master_sample_manifest.parquet, CRSP, CCM, Compustat, IBES data files | Medium | Commands are correct as written; all dependencies documented |
| `python -m f1d.econometric.run_h14_bidask_spread` | Y | Partial | Yes — requires Stage 3 output under `latest/`; H0.3 output for specs 5–6 | Medium | Documented; `latest` symlink means re-running Stage 3 changes Stage 4 results |
| H0.3 (CEO Clarity Extended) run before specs 5–6 | Partial — mentioned in B, K7, C | Partial | Yes — undocumented in Stage 4 script header | Medium | H14 docstring does not list H0.3 as a prerequisite; only in provenance doc |
| Stage 3 panel timestamp used for Stage 4 run | Not recorded | Not verifiable | Yes — `get_latest_output_dir` resolves dynamically | Medium | Stage 4 manifest records panel_file path but not Stage 3 directory timestamp |
| H0.3 residual file timestamp used | Not recorded | Not verifiable | Yes — resolved by `get_latest_output_dir` | Medium | No version hash in H14 manifest for H0.3 output |
| Python / package versions | Yes (Python 3.9–3.13, pandas, pyarrow, linearmodels) | Not verified | Yes — `linearmodels` version affects cluster SE computation behavior | Low | Specific linearmodels version not pinned |
| Random seed | Y — "not used in H14 pipeline" | Y — no stochastic components in PanelOLS | No | Low | Correctly documented |
| CRSP BIDLO/ASKHI availability rate | Flagged as UNVERIFIED (J6) | N | N/A | Low-Medium | J6 correctly flags this as unverified; a 1.1% missingness rate on delta_spread is low but underlying cause unverified |
| Row count by stage | Y — 12 verified counts in Section I | Y (artifacts) | No | Low | Verification log is thorough |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|---|---|---|---|---|
| Identification threats | **Partial** | Reverse causality and OVB correctly flagged | AbsSurprise bad-control mechanism absent; PreCallSpread absorption of reverse causality channel absent | Medium |
| Inference / clustering | **Partial** | Firm-clustered adequacy claim correct on cluster count; overconfident on SE adequacy | Cross-sectional dependence during market-wide episodes (e.g., 2008) not addressed; double-clustering not demanded | Low-Medium |
| FE and within-variation | **Pass** | PanelOLS EntityEffects+TimeEffects; quarter_index correct; drop_absorbed verified | None material | N/A |
| Timing alignment | **Pass** | Pre-call vs. post-call windows correctly analyzed; call_ref_date mechanics documented | Trading-day rank vs. calendar-day hybrid correctly described | N/A |
| Post-treatment controls | **Partial** | AbsSurprise flagged for coverage gap; not flagged as post-treatment/bad control | AbsSurprise is determined simultaneously with the call; acts as mechanism control | Medium |
| Reverse causality | **Partial** | Flagged at High severity; IV or falsification recommended | PreCallSpread's role in absorbing the reverse-causality channel not noted | Low-Medium |
| Endogenous sample selection | **Pass** | IBES coverage gap (24.8%) documented; noted as non-random selection of covered firms | | N/A |
| Model-family-specific threats | **Pass** | Panel OLS has limited additional threats; PH/survival threats N/A; attrition documented | | N/A |
| Robustness adequacy | **Pass** | Correctly rates robustness as inadequate (K5 table); 10 gaps enumerated | | N/A |
| Interpretation discipline | **Pass** | Causal language discouraged; null result clearly stated; economic magnitudes noted as negligible | | N/A |
| Academic-integrity risks | **Pass** | Stale artifact, no manifest linking, ASKHI/BIDLO disclosure all addressed | Exception-type gap for ClarityResidualEngine not noted | Low |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|---|---|---|---|---|
| **Skip mechanism description error (RT-FE-01):** First audit states specs 5–6 skip via `if uncertainty_var not in df_sample.columns`. Actual skip occurs via `len(df_reg) < 100` after `dropna` eliminates all NaN rows. The column IS present (all NaN) after the left merge with an empty DataFrame. | `ceo_clarity_residual.py` lines 41–52 (catch returns empty DataFrame with column names); `build_h14_bidask_spread_panel.py` lines 130–148 (left merge preserves column names); `run_regression()` line 194 (`len(df_reg) < 100` exit). | **Low** | A future auditor inspecting only the first audit's skip description would have the wrong code path. This matters if diagnosing why a spec doesn't appear in outputs. | Correct to: "Column IS present post-merge (all NaN); skip occurs at `len(df_reg) < 100` guard in `run_regression()`." |
| **Overconfident SE claim:** "No concern about SE underestimation" in K3 is stated as a fact rather than a qualified judgment | Section K3 | Low-Medium | If a committee member reads this as a certified result, they may not demand double-clustering robustness | Reformulate: "Firm-clustered SEs are adequate for within-firm serial correlation; time-series cross-sectional dependence is unverified and double-clustering is recommended as robustness." |
| **"Silently" fallback characterization is partially misleading:** The fallback behavior is not fully silent (print statement before raise in engine; no stderr warning on catch) | Section B; `_clarity_residual_engine.py` line 56 | Low | Creates ambiguity about whether the absence of specs 5–6 in an output would be detectable | Clarify the exact logging behavior on this code path |
| **No runtime verification for Clarity Residual fallback path:** The first audit documents the fallback behavior based on code reading, not on actually triggering it with a missing H0.3 output | Section B, K7 | Low | Code-path reasoning could miss exception type issues (see RT-MI-05) | Explicitly run with H0.3 output removed to verify behavior; document result |
| **Verification log cross-references artifact, not live run:** Section I item 11 references `model_diagnostics.csv` run 2026-03-10_215618. No hash or checksum of the artifact is provided. | Section I row 11 | Low | A stale or regenerated artifact could differ from what was reviewed. A future auditor cannot verify the artifact independently without running the suite. | Record file hash of `model_diagnostics.csv` in verification log |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis-standard reliance on first audit? |
|---|---|---|---|---|---|---|---|---|---|---|
| RT-FE-01 | First-audit factual error | Code path description | Y | Low | Section B, K7 | Clarity Residual skip described as `if uncertainty_var not in df_sample.columns`; actual skip is via `len(df_reg) < 100` after NaN drop | `ceo_clarity_residual.py` L41–52; `run_regression()` L194 | Misleads code auditors about skip mechanism | Correct section B and K7 descriptions | No |
| RT-OS-01 | First-audit unsupported claim | Inference / SEs | Y | Low-Medium | K3 | "No concern about SE underestimation" — overclaims adequacy of one-way firm clustering | Study design; Petersen (2009) | Committee may not demand double-clustering robustness | Reformulate to qualified judgment | No |
| RT-OS-02 | First-audit unsupported claim | Data provenance | Y | Low | E1 table, D | "62.4% missing if H0.3 not run" conflates two missingness scenarios | Builder code | Minor misrepresentation of expected missingness | Clarify two distinct scenarios in E1 | No |
| RT-MI-01 | Underlying implementation issue missed by first audit | Econometric implementation | N (UNVERIFIED) | Medium | `run_regression()` L211 | `(gvkey, quarter_index)` panel index uniqueness not verified before PanelOLS call | PanelOLS multi-index requirement; verification log omits this check | If duplicate indices exist, FE estimates are incorrect | Add uniqueness assertion to verification log and pre-estimation code | Y (if duplicates exist) |
| RT-MI-02 | Underlying implementation issue missed by first audit | Data provenance / merge integrity | Y (partially) | Low-Medium | `bidask_spread_change.py`; `stock_price.py` | CCM permno_map built independently by 3 builders; cross-builder permno consistency not verified | Identical code in 2 of 3 builders inspected; TurnoverBuilder not confirmed | If permno divergence, DV and controls linked to different firms | Centralize permno_map; add cross-builder consistency assertion | No |
| RT-MI-03 | Underlying implementation issue missed by first audit | Identification / bad controls | Y | Medium | `run_h14_bidask_spread.py` L87–94; K2 | AbsSurprise is determined simultaneously with the call; controlling for it removes the earnings-news mechanism | Study design | Uncertainty coefficient biased toward zero; null result partially explained by over-controlling | Run spec 1 without AbsSurprise as robustness | No (first audit is silent; does not block reliance, but weakens interpretation) |
| RT-MI-04 | Underlying implementation issue missed by first audit | Identification / bad controls | Y | Low-Medium | K2; `BASE_CONTROLS` | PreCallSpread partially absorbs reverse-causality channel; not discussed | Study design; `BASE_CONTROLS` includes `PreCallSpread` | Uncertainty coefficient biased toward zero via over-controlling for reverse causality | Run sensitivity without PreCallSpread; document trade-off | No |
| RT-MI-05 | Unverified but material concern | Reproducibility / exception handling | N (UNVERIFIED) | Low-Medium | `_clarity_residual_engine.py` L46 | `get_latest_output_dir` exception type when base directory absent may not be `FileNotFoundError`; builders only catch `FileNotFoundError` | Builder code; `get_latest_output_dir` not inspected | Stage 3 crash in clean environment instead of silent fallback | Inspect `get_latest_output_dir`; broaden catch or document | No |
| RT-MI-06 | Underlying implementation issue missed by first audit | Variable construction | Y | Low | `bidask_spread_change.py` L328–336 | Spread mean computed over valid-quote days only (pandas skips NaN); may use 2 or 3 days; undocumented | Code | No estimation error; DV formula in paper may be misquoted as requiring 3 days | Document in variable dictionary: "mean over ≥2 valid-quote days" | No |
| L1 | Underlying implementation issue | Measurement validity | Y | High | `bidask_spread_change.py` L6–9, L280–287 | ASKHI/BIDLO daily range ≠ effective spread; overstates spread levels for high-volatility days | Code | Results not comparable to TAQ-based literature | Replace with Amihud illiq or closing bid-ask | Yes |
| L2 | Underlying implementation issue | Identification | Y | High | K2; study design | Reverse causality unaddressed (no IV or natural experiment) | Study design | β estimate may be biased | IV strategy or falsification test | Yes |
| L3 | Underlying implementation issue | Robustness | Y | High | K5; code | No alternative event windows, spread measures, FE structures, or falsification | Code; K5 | Window-specific and measure-specific null result cannot be generalized | Add ±1 and ±5 day windows; Amihud robustness; double-clustering | Yes |
| L4 | Underlying implementation issue | Econometric | Y | Medium | `run_h14_bidask_spread.py` L187 | No winsorization of DV (max=1.17), Turnover (max=3.77, 20×p99), Volatility (max=218%) | Verification log | Extreme observations influence OLS; null result could reflect outlier dilution | Winsorize at 1%/99% | Yes |
| L5 | Underlying implementation issue | Reproducibility | Y | Medium | `_clarity_residual_engine.py` | Specs 5–6 depend on H0.3 output resolved by `get_latest_output_dir`; stale artifact risk | Code | Non-reproducible from H14 alone | Snapshot H0.3 residual file hash in H14 manifest | Partial |
| L6 | Documentation gap | Documentation | Y | Low | `run_h14_bidask_spread.py` L24–26 | Docstring says "(4)" uncertainty measures; code has 6 | Code | Misleads future auditors | Fix docstring | No |
| L8 | Underlying implementation issue underplayed | Inference | N | Medium | `run_h14_bidask_spread.py` L215 | One-way firm clustering; cross-sectional dependence unaddressed | Study design | SEs may be too liberal under market-wide episodes | Test double-clustering | Partial |

---

## N. What a Committee / Referee Would Still Not Know After Reading Only the First Audit

1. **Whether `(gvkey, quarter_index)` pairs are unique** — the PanelOLS correctness prerequisite was not verified. A referee cannot know if the FE estimates are internally valid without this check.

2. **That AbsSurprise may be a bad control** — the first audit presents it as an identification control for earnings news, not as a mechanism control that could absorb the uncertainty→liquidity channel. A referee would not know to ask "does removing AbsSurprise change the result?"

3. **That PreCallSpread's inclusion partially neutralizes the reverse-causality concern while simultaneously biasing the uncertainty coefficient toward zero** — the first audit discusses reverse causality and PreCallSpread in isolation, not as a linked trade-off.

4. **That the "silently fall back" and "skip via column absence" description of specs 5–6 is factually wrong** — the column IS present post-merge (all NaN); the skip is via the row-count guard.

5. **That `get_latest_output_dir` may raise something other than `FileNotFoundError`** — in a clean environment without H0.3 output, the panel build might crash rather than silently omit specs 5–6.

6. **That the daily high-low spread (ASKHI/BIDLO) systematically overstates effective spreads on high-volatility days** — the first audit flags this correctly (L1) but a referee reading only the first audit would know this was raised and flagged, so this is adequately documented. (Not a gap; included for completeness.)

7. **That no formal test of panel balance was performed** — the first audit documents observation counts by spec but does not test whether the unbalanced panel structure affects inference (e.g., via survivorship in the ≥5 call filter).

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|---|---|---|---|---|
| 1 | Add panel index uniqueness check: `df_reg.duplicated(["gvkey","quarter_index"]).sum()` to verification log (Section I); add assertion note before PanelOLS call | PanelOLS correctness prerequisite; currently unverified | Low (run one command) | High — closes a silent correctness risk |
| 2 | Add AbsSurprise bad-control analysis to Section K2 | Mechanism control concern explains null result; needed for referee-quality identification section | Low (analysis) | High — substantially strengthens identification critique |
| 3 | Add PreCallSpread reverse-causality absorption to Section K2 | Links reverse causality threat to specific control variable; actionable via sensitivity run | Low (analysis) | Medium-High |
| 4 | Correct Section B and K7 Clarity Residual skip mechanism | Factual error; currently misleads code auditors | Low (text edit) | Low but necessary for accuracy |
| 5 | Qualify SE claim in K3: replace "No concern about SE underestimation" with qualified statement about cross-sectional dependence | Overclaim; double-clustering should be recommended | Low (text edit) | Low-Medium |
| 6 | Add `get_latest_output_dir` exception type verification (read `path_utils.py`) to reproducibility section | Close the exception-handling gap for Clarity Residuals | Low | Low-Medium |
| 7 | Add cross-builder CCM permno consistency check to verification log | Closes silent divergence risk between DV and controls | Low (run comparison) | Low-Medium |
| 8 | Record file hash of `model_diagnostics.csv` artifact in verification log | Provides tamper-resistant reference for null result | Low | Low |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
**Substantially yes, with targeted corrections.** The core facts — model family, formula, FE structure, variable construction, data provenance, null result, and primary identification concerns — are verified correct. The two priority-1 gaps (panel index uniqueness and AbsSurprise bad-control analysis) must be addressed before the document is definitively referee-grade.

**What is its biggest factual weakness?**
The mischaracterization of the Clarity Residual skip mechanism (Section B, K7): the column IS present in the panel (all NaN), not absent. The skip occurs via the `len(df_reg) < 100` guard, not via `if uncertainty_var not in df_sample.columns`. While the practical outcome is identical, this is a factual description error in the code-path analysis.

**What is its biggest completeness weakness?**
The panel index uniqueness verification is absent from the verification log. PanelOLS requires unique `(gvkey, quarter_index)` pairs; the first audit verified `file_name` uniqueness but not the composite panel index. This is the only unverified correctness prerequisite for the FE estimator.

**What is its biggest severity/judgment weakness?**
The "No concern about SE underestimation" claim in Section K3 overstates the adequacy of one-way firm clustering. Cross-sectional dependence during market-wide liquidity events (2008 financial crisis falls within the 2002–2018 sample) is unaddressed and could produce upward-biased t-statistics. The correct claim is that the cluster count is adequate — not that SE underestimation is impossible.

**What is the single most important missed issue?**
The AbsSurprise bad-control problem (RT-MI-03). AbsSurprise is simultaneously determined with the call and controls for the earnings-news mechanism through which uncertainty language may affect spreads. If the true channel is: high uncertainty → earnings surprise interpretation by market → spread widening, then including AbsSurprise as a control absorbs the mechanism. Running spec 1 without AbsSurprise is a low-effort, high-value robustness check that should be in the first audit.

**What is the single most misleading claim?**
The claim that specs 5–6 "will silently fall back to empty DataFrames" with the skip via `if uncertainty_var not in df_sample.columns` is misleading in its specific detail. The builders DO return empty DataFrames (correct), but the column IS created in the panel (all NaN), and the skip via `not in df_sample.columns` would NOT trigger — the skip actually happens in `run_regression()` via the row-count guard. A future auditor following the first audit's code-path guidance would not trace the actual execution path.

**What should a thesis committee believe after reading this red-team review?**
The H14 first-layer audit is a credible, well-evidenced provenance document that correctly identifies the most material threats to the suite's validity (non-standard spread proxy, reverse causality, robustness deficit, null result). The specific code-path error on Clarity Residual skipping, the missing panel index uniqueness check, and the AbsSurprise bad-control omission are concrete improvements needed before the audit is definitively referee-grade. The null result across all 6 specifications is internally valid conditional on the ASKHI/BIDLO spread measure; whether it holds with a standard effective-spread measure (Amihud or TAQ-based) is the single most important unresolved empirical question for the thesis.
