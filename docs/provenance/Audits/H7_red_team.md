# H7 Second-Layer Red-Team Audit

**Generated:** 2026-03-15
**Suite ID:** H7
**Auditor posture:** Fresh-context, adversarial. First-layer audit treated as object to test, not source of truth.
**First-layer audit version:** `docs/provenance/H7.md` (dated 2026-03-12)
**Prior red-team version:** `docs/provenance/Audits/H7_red_team.md` (dated 2026-03-12) -- also audited
**Code version audited:** Current `run_h7_illiquidity.py`, `build_h7_illiquidity_panel.py`, all shared engines
**Latest output artifacts inspected:** `outputs/econometric/h7_illiquidity/2026-03-13_054310/`

---

## A. Red-Team Bottom Line

### Verdict on the First-Layer Audit

The H7.md first-layer audit contains **two thesis-grade factual errors** that fundamentally undermine its reliability as a referee document:

1. **Wrong DV throughout.** The audit identifies the dependent variable as `amihud_illiq` (inter-call Amihud level) in sections A3, F, H (all 7 spec rows), I2, J2, K2, K3, L1, L3, L4, L15, M, and N. The actual DV used in every regression is `delta_amihud` (post-call minus pre-call Amihud change, [+1,+3] - [-3,-1] trading days). This is not a labeling quibble -- `amihud_illiq` and `delta_amihud` are fundamentally different constructs with different distributional properties, different economic interpretations, and different identification implications.

2. **Fabricated "bad controls" issue rated High/blocking.** The audit's L1 issue (rated High severity, marked as "Blocks thesis-standard? Y") claims Volatility and StockRet "share the DV window" and "mechanically absorb DV variation." In reality, **Volatility and StockRet do not appear anywhere in `run_h7_illiquidity.py`**. They are not in `BASE_CONTROLS`. They are not used in any H7 regression. The audit fabricated a High-severity blocking issue out of variables that are merely present in the panel but never enter a regression formula. This error was then **confirmed at High severity** by the prior red-team audit (RT-06), which also failed to check `BASE_CONTROLS`.

These two errors together mean the audit's issue register, severity calibration, priority fix list, and final readiness statement are all built on a materially wrong foundation.

**Overall grade for first audit:** MATERIALLY FLAWED
*(Two fundamental factual errors: wrong DV identification, fabricated blocking issue. Core N/p-value claims verified against older artifacts but not current outputs.)*

**Suite as implemented:** SALVAGEABLE WITH MAJOR REVISIONS
*(DV `delta_amihud` is unwinsorized with extreme range [-99.6, 2678.2]; `pre_call_amihud` control also unwinsorized with max=267.8. Distributional issues more severe than first audit realized, but apply to the actual DV, not the one documented.)*

**Risk direction of first audit:** Mixed -- **overstated risk** via fabricated L1 (bad controls); **understated risk** by documenting the wrong DV and therefore mischaracterizing the distributional threat.

---

## B. Scope and Objects Audited

| Item | Path |
|---|---|
| Suite ID | H7 |
| Regression entrypoint | `src/f1d/econometric/run_h7_illiquidity.py` |
| Panel builder | `src/f1d/variables/build_h7_illiquidity_panel.py` |
| First-layer audit | `docs/provenance/H7.md` |
| Prior red-team audit | `docs/provenance/Audits/H7_red_team.md` |
| AmihudChangeBuilder | `src/f1d/shared/variables/amihud_change.py` |
| AmihudIlliqBuilder | `src/f1d/shared/variables/amihud_illiq.py` |
| CRSP engine | `src/f1d/shared/variables/_crsp_engine.py` |
| Clarity residual engine | `src/f1d/shared/variables/_clarity_residual_engine.py` |
| CEO clarity residual builder | `src/f1d/shared/variables/ceo_clarity_residual.py` |
| Panel utils | `src/f1d/shared/variables/panel_utils.py` |
| Winsorization module | `src/f1d/shared/variables/winsorization.py` |
| Latest diagnostics CSV | `outputs/econometric/h7_illiquidity/2026-03-13_054310/model_diagnostics.csv` |
| Latest robustness CSV | `outputs/econometric/h7_illiquidity/2026-03-13_054310/robustness_results.csv` |
| Latest LaTeX table | `outputs/econometric/h7_illiquidity/2026-03-13_054310/h7_illiquidity_table.tex` |
| Latest summary stats CSV | `outputs/econometric/h7_illiquidity/2026-03-13_054310/summary_stats.csv` |
| Latest sample attrition | `outputs/econometric/h7_illiquidity/2026-03-13_054310/sample_attrition.csv` |
| Regression output A3 | `outputs/econometric/h7_illiquidity/2026-03-13_054310/regression_Main_A3.txt` |

---

## C. Audit-of-Audit Scorecard

| Dimension | First-layer audit status | Evidence basis | Red-team note |
|---|---|---|---|
| Model / spec identification | **Fail** | First audit identifies DV as `amihud_illiq` throughout; actual DV is `delta_amihud` (`run_h7_illiquidity.py` L188, L201, L206; regression output header: "Dep. Variable: delta_amihud") | Fundamental misidentification of the dependent variable. All downstream claims about DV properties are about the wrong variable. |
| Reproducibility commands | **Pass** | Stage 3 + Stage 4 commands correct and runnable | Commands are accurate |
| Dependency tracing | **Partial** | Builder chain correct. But audit misidentifies which builder produces the actual DV (`AmihudChangeBuilder` for `delta_amihud`, not `AmihudIlliqBuilder` for `amihud_illiq`). | `amihud_illiq` is loaded by the panel but never enters a regression formula as DV |
| Raw data provenance | **Partial** | CRSP/CCM/Compustat sources identified. Raw row counts stated as verified but not independently reproduced. | Plausible |
| Merge / sample audit | **Pass** | Zero-delta enforcement verified at `build_h7_illiquidity_panel.py:137-142` | Correct |
| Variable dictionary completeness | **Fail** | Lists `amihud_illiq` as the DV; does not list `delta_amihud` or `pre_call_amihud` in the variable dictionary. Includes Volatility and StockRet as controls in the dictionary when they are not used in regressions. | Missing actual DV and actual control; includes phantom variables |
| Outlier / missing-data rules | **Fail** | Discusses winsorization of `amihud_illiq` at 1%/99% (correct for that variable). But actual DV `delta_amihud` is NOT winsorized (verified: no winsorization in `AmihudChangeBuilder`). `pre_call_amihud` also unwinsorized. Summary stats show delta_amihud range [-99.6, 2678.2]. | The audit's winsorization discussion applies to a variable not used as DV |
| Estimation spec register | **Fail** | All 7 spec rows list Outcome = `amihud_illiq`. Actual outcome is `delta_amihud`. N values (e.g., A3: 75,124) are from older run; latest run shows A3: 78,679. | Wrong DV, stale N counts |
| Verification log quality | **Partial** | 17 verification steps documented. Steps 5-6, 11, 17 report stats for `amihud_illiq`, not the actual DV. Step 14 robustness claims verified against older artifacts. | Verification targeted wrong variable for DV-specific checks |
| Known issues section | **Partial** | J1 (non-unique index), J4 (warning suppression), J5-J7 real. J2 (DV skewness) describes `amihud_illiq` skewness, not `delta_amihud` skewness. | J2 misattributed |
| Identification critique | **Fail** | K2 "Contemporaneous confounders" row claims Volatility/StockRet are "bad controls" sharing DV window. These are not in `BASE_CONTROLS` and not used in any regression. | Fabricated identification threat |
| Econometric implementation critique | **Fail** | K3 row 4 ("Volatility/StockRet as controls share DV window") is about phantom controls. K3 row 2 ("Extreme DV skewness") cites statistics for wrong variable. | Two of four K3 issues are wrong |
| Robustness critique | **Partial** | Robustness checks listed. Prior red-team correctly identified missing coefficient-direction reporting. | First audit improved by prior red-team feedback on direction |
| Academic-integrity critique | **Pass** | Warning suppression, stale artifacts, H0.3 dependency correctly flagged | Minor items handled |
| Severity calibration | **Fail** | L1 (bad controls) rated High and blocking -- entirely false positive. L3 (DV skewness) rated High based on wrong variable's statistics. L4 (no log-DV) recommends `log(1+amihud_illiq)` when actual DV is delta_amihud (a change variable; log-transforming changes is non-standard). | Severity structure built on incorrect premises |
| Final thesis verdict support | **Fail** | "Biggest threat: Untransformed DV + bad controls" -- bad controls do not exist; DV is misidentified. Priority fix #1 and #2 address non-existent problems. | Final verdict not supported by actual code |

---

## D. Claim Verification Matrix (First Audit Claims Tested)

| Claim ID | First-layer claim | Section | Verified? | Evidence checked | Red-team verdict | Notes |
|---|---|---|---|---|---|---|
| D1 | DV is `amihud_illiq` | A3, F, H | **N** | `run_h7_illiquidity.py` L188,201: formula uses `delta_amihud`; regression output header: "Dep. Variable: delta_amihud" | **VERIFIED ERROR IN FIRST AUDIT** | Fundamental DV misidentification throughout |
| D2 | Volatility and StockRet are controls sharing DV window | K2, K3, L1 | **N** | `run_h7_illiquidity.py` L97-105: `BASE_CONTROLS` = [Entire_All_Negative_pct, Analyst_QA_Uncertainty_pct, Size, Lev, ROA, TobinsQ, pre_call_amihud]. Grep for "Volatility" or "StockRet" in file: zero matches. | **VERIFIED FALSE POSITIVE IN FIRST AUDIT** | These variables are in the panel but never enter any regression formula |
| D3 | Panel: 112,968 rows, unique file_name | A1, I1 | **Y** | Panel builder outputs manifest-keyed panel; zero-delta enforcement at L137-142 | VERIFIED FACT | |
| D4 | Sample: Main=88,205 | I3 | **Y** | `assign_industry_sample()` at `panel_utils.py:46-73` verified | VERIFIED FACT | |
| D5 | A3: N=75,124, 1,831 firms | H | **N** | `model_diagnostics.csv` (latest run 2026-03-13): A3 n_obs=78,679, n_firms=1,845 | **VERIFIED ERROR: STALE ARTIFACT** | Audit used older run artifacts; current code produces different N |
| D6 | A1: N=56,218 | H | **N** | Latest: A1 n_obs=58,240, n_firms=1,626 | **VERIFIED ERROR: STALE ARTIFACT** | Same stale-artifact issue |
| D7 | B1: N=40,275 | H | **N** | Latest: B1 n_obs=38,214, n_firms=1,291 | **VERIFIED ERROR: STALE ARTIFACT** | B1 decreased (possibly H0.3 re-run changed residual coverage) |
| D8 | ALL coefficients insignificant | I13, K1 | **N** | Latest `model_diagnostics.csv`: A3 beta1_p_one=0.069 (10% level); B2 beta1_p_one=0.080. LaTeX table shows stars on A3 and B2 at 10% level. | **VERIFIED ERROR: STALE RESULT** | Current code produces marginally significant results for A3 and B2; audit's "uniformly null" conclusion is outdated |
| D9 | PanelOLS with EntityEffects + TimeEffects, drop_absorbed=True | A2, H | **Y** | `run_h7_illiquidity.py` L220-221 | VERIFIED FACT | |
| D10 | Entity-clustered SEs | A5, H | **Y** | `run_h7_illiquidity.py` L221: `cov_type="clustered", cluster_entity=True` | VERIFIED FACT | |
| D11 | One-tailed p-value formula | K6 | **Y** | `run_h7_illiquidity.py` L242: `p1_one = p1_two / 2 if beta1 > 0 else 1 - p1_two / 2` | VERIFIED FACT | |
| D12 | DV skewness = 13.5, kurtosis = 222 | I6, J2 | **N/A** | These statistics are for `amihud_illiq`, not the actual DV `delta_amihud`. `delta_amihud` has Mean=0.092, SD=12.62, range [-99.6, 2678.2] -- different distributional profile. | **VERIFIED: WRONG VARIABLE** | Statistics correctly computed for `amihud_illiq` but irrelevant to the actual DV |
| D13 | Zero-delta enforcement on merges | E1 | **Y** | `build_h7_illiquidity_panel.py` L137-142 | VERIFIED FACT | |
| D14 | Min 5 calls filter after listwise deletion | E2 | **Y** | `run_h7_illiquidity.py` L193-195 | VERIFIED FACT | |
| D15 | H7-C Wald test implementation | K1, A5 | **Y** | `run_h7_illiquidity.py` L440-454 | VERIFIED FACT | |
| D16 | `pre_call_amihud` used as control | Docstring | **Y** | `run_h7_illiquidity.py` L104: in `BASE_CONTROLS`. Regression output confirms "pre_call_amihud" parameter estimated. | VERIFIED FACT | First audit does not clearly document this as a control in its variable dictionary |
| D17 | delta_amihud = PostAmihud - PreAmihud | Docstring L17 | **Y** | `amihud_change.py` L360: `amihud["delta_amihud"] = amihud["post_call_amihud"] - amihud["pre_call_amihud"]` | VERIFIED FACT | Correctly constructed but not documented in first audit |
| D18 | delta_amihud window: +/-3 trading days | Docstring | **Y** | `amihud_change.py` L49: `self.window_days = config.get("window_days", 3)`. Trading-day positions used (L327-342). | VERIFIED FACT | Uses trading-day ranks, not calendar-day offsets |

---

## E. Unsupported, Overstated, or Weakly-Evidenced Claims in the First Audit

| Issue ID | Claim / statement | Why unsupported or weak | Severity | Missing evidence | Corrected formulation |
|---|---|---|---|---|---|
| E1 | "DV: `amihud_illiq`" (A3, F, H, throughout) | Actual DV is `delta_amihud`. Code formula at L201: `"delta_amihud ~ {iv_var} + ..."`. Regression output header: "Dep. Variable: delta_amihud". | **Critical** | Any inspection of `run_regression()` function or regression output | "DV: `delta_amihud` (change in Amihud illiquidity, post-call [+1,+3] minus pre-call [-3,-1] trading days)" |
| E2 | L1: "Volatility and StockRet... mechanically absorb DV variation" (K2, K3, L1) | Volatility and StockRet are not in `BASE_CONTROLS` and do not appear anywhere in `run_h7_illiquidity.py`. Zero grep matches. | **Critical** | Inspect `BASE_CONTROLS` list at L97-105 | Remove L1 entirely; Volatility and StockRet are not regression controls in H7 |
| E3 | "DV has extreme right skewness (skew=13.5, kurt=222)" (J2, K3, L3) | These statistics are for `amihud_illiq`, not the actual DV `delta_amihud`. The change variable has a different distribution (symmetric around zero with extreme tails). | **High** | Compute distribution statistics for `delta_amihud`, not `amihud_illiq` | "The actual DV `delta_amihud` has mean=0.092, SD=12.62, range [-99.6, 2678.2]; extreme dispersion and heavy tails but not necessarily right-skewed in the same way as levels" |
| E4 | M priority #1: "Add log-transformed DV: `log(1 + amihud_illiq)`" | The actual DV is a change variable (`delta_amihud`). Log-transforming a change that takes negative values is not standard. The appropriate transformation for extreme tails in a change variable would be winsorization or a rank transform. | **High** | Understand the DV before recommending transformations | "Winsorize `delta_amihud` at 1%/99% per year, or test a rank-transformed DV. Log transformation is not applicable to a signed change variable." |
| E5 | M priority #2: "Remove Volatility and StockRet from controls" | These are not controls. Nothing to remove. | **Critical** | Check `BASE_CONTROLS` | Remove this recommendation |
| E6 | "N obs A3 = 75,124" (H, E2, multiple places) | Latest run: A3 N=78,679. Audit used older artifacts. | **Medium** | Run current code or inspect latest output | "N values reflect the 2026-03-12_015407 run; current code may produce different sample sizes depending on upstream data state" |
| E7 | "ALL uncertainty coefficients are statistically insignificant" (I13, K1) | Latest run: A3 one-tailed p=0.069 (10% significant); B2 one-tailed p=0.080 (approaching 10%). LaTeX table shows stars. | **High** | Inspect current output artifacts | "Most coefficients are insignificant; A3 (Manager QA) shows marginal one-tailed significance at 10% (p=0.069) in the latest run" |

---

## F. False Positives in the First Audit

| Issue ID | First-audit criticism | Why it appears false / overstated | Evidence | Severity of audit error | Corrected view |
|---|---|---|---|---|---|
| F1 | L1 / K2 / K3: "Volatility and StockRet are bad controls sharing the DV window" (rated High, blocks thesis-standard) | Volatility and StockRet are NOT in `BASE_CONTROLS`. They do not appear anywhere in `run_h7_illiquidity.py`. The string "Volatility" has zero matches in the regression script. The string "StockRet" has zero matches. These variables exist in the panel (loaded by the builder) but are never used as regressors. | `run_h7_illiquidity.py` L97-105: `BASE_CONTROLS = ["Entire_All_Negative_pct", "Analyst_QA_Uncertainty_pct", "Size", "Lev", "ROA", "TobinsQ", "pre_call_amihud"]`. Grep verification: zero matches for "Volatility" or "StockRet" in the file. | **Critical** | Volatility and StockRet are irrelevant to H7 regressions. L1 should be deleted entirely. The "bad controls" narrative that pervades K2, K3, L1, M priorities, and the final readiness statement is unfounded. |
| F2 | L3: "DV (amihud_illiq) has extreme right skewness (13.5)" | The DV is `delta_amihud`, not `amihud_illiq`. The skewness statistics were computed for the wrong variable. While `delta_amihud` also has distributional problems (extreme range, heavy tails), they are different problems requiring different fixes. | `summary_stats.csv`: `delta_amihud` mean=0.092, SD=12.62, range [-99.6, 2678.2] -- this is a signed change variable, not a bounded-below level. | **High** | The DV has extreme dispersion but the characterization (right-skew, log-transform fix) is wrong for a change variable. The correct concern is extreme tails in both directions; the correct fix is winsorization or trimming, not log transformation. |
| F3 | L4: "No log-DV specification tested" (rated High, blocks thesis-standard) | A log transform of `delta_amihud` is nonsensical -- the variable takes negative values (range [-99.6, 2678.2]). The recommendation `log(1 + amihud_illiq)` would apply to a levels specification, but the code does not run a levels specification. | `amihud_change.py` L360: `delta_amihud = post - pre`, which can be negative. | **High** | Replace with: "DV `delta_amihud` has extreme tails; winsorize at 1%/99% or trim extreme observations. Consider also testing Amihud in levels with log transform as an alternative specification." |

---

## G. Missed Issues (Second-Layer Discoveries)

| Issue ID | Category | Description | Evidence | Severity | Why first audit missed it | Consequence | Recommended fix |
|---|---|---|---|---|---|---|---|
| G1 | Variable identification | First audit identifies DV as `amihud_illiq` throughout. Actual DV is `delta_amihud` (post-call minus pre-call Amihud change). These are economically different constructs: one is a level, the other is a change. | `run_h7_illiquidity.py` L188,201,206: formula = `"delta_amihud ~ ..."`. Regression output: "Dep. Variable: delta_amihud". First audit A3, F, H: all say `amihud_illiq`. | **Critical** | First audit likely read the panel builder docstring (which mentions `amihud_illiq` as the original DV before the delta_amihud refactor) and did not inspect the actual regression formula or output. | Every DV-related claim in the audit is about the wrong variable: distributional statistics, winsorization status, recommended transformations, identification implications. | Rewrite all DV references to `delta_amihud`; recompute distributional statistics; revise transformation recommendations. |
| G2 | Variable identification | `pre_call_amihud` is an actual control variable in BASE_CONTROLS but is not in the first audit's variable dictionary (section F) as a regression control. It only appears as a variable in the summary stats. | `run_h7_illiquidity.py` L104: `"pre_call_amihud"` in BASE_CONTROLS. Variable dictionary F lists it as "DV control" but not prominently as a regression variable. | **Medium** | Audit focused on `amihud_illiq` and missed the actual control structure. | A referee would not know that pre-call Amihud is a control -- this is a significant design choice (lagged-DV control in a change specification). | Add `pre_call_amihud` to the estimation spec register as a control; discuss its role. |
| G3 | Outlier/winsorization | `delta_amihud` is NOT winsorized. Range [-99.6, 2678.2] with SD=12.62 enters OLS raw. `pre_call_amihud` is also NOT winsorized (max=267.8). Both come from `AmihudChangeBuilder` which has no winsorization step. In contrast, `amihud_illiq` from `CRSPEngine` IS winsorized at 1%/99% per year. | `amihud_change.py`: zero matches for "winsor". `summary_stats.csv`: delta_amihud max=2678.2; pre_call_amihud max=267.8. `_crsp_engine.py` L445-447: only CRSP_RETURN_COLS are winsorized. | **Critical** | First audit thought the DV was `amihud_illiq` (which IS winsorized) and thus described the winsorization as adequate. The actual DV bypasses winsorization entirely. | Extreme observations dominate OLS. A single call with delta_amihud=2678 has leverage 212x the SD. This is the most serious specification issue. | Winsorize `delta_amihud` and `pre_call_amihud` at 1%/99% per year before regression, or add winsorization to `AmihudChangeBuilder`. |
| G4 | Stale artifacts | First audit's N counts (A3: 75,124; A1: 56,218; B1: 40,275) are from the 2026-03-12_015407 run. Latest run (2026-03-13_054310) shows A3: 78,679; A1: 58,240; B1: 38,214. Sample sizes changed by up to 5% between runs. The audit does not version-lock to a specific run. | Compare `model_diagnostics.csv` across runs. | **Medium** | First audit documented one run's outputs; code or data was subsequently updated. | Audit claims become unreliable as code evolves. | Pin the audit to a specific run timestamp; verify outputs match. |
| G5 | Result characterization | First audit claims "ALL uncertainty coefficients are statistically insignificant." Current run shows A3 one-tailed p=0.069 and B2 one-tailed p=0.080, both approaching or at 10% significance. LaTeX table shows stars (* for p<0.10) on A3 and B2. | `model_diagnostics.csv` (2026-03-13 run): A3 beta1_p_one=0.069; B2 beta1_p_one=0.080. `h7_illiquidity_table.tex`: A3=0.3285* and B2=0.0072*. | **High** | Audit was written against older run where all coefficients were insignificant. | A referee relying on the audit would believe H7 is a clean null. The current output suggests marginal evidence (at 10%) for Manager QA uncertainty increasing illiquidity. This requires discussion, not dismissal. | Update results to reflect current run; discuss marginal significance of A3 and B2. |
| G6 | DV construction | `delta_amihud` uses trading-day positions (not calendar days) for the pre/post windows. The first audit's discussion of calendar-day windows for the Amihud measure applies to `amihud_illiq` (via `_crsp_engine.py`), not to `delta_amihud` (via `AmihudChangeBuilder`). These two builders use different window definitions. | `amihud_change.py` L326-342: uses `pre_rank` and `post_rank` (rank-based trading day positions). `_crsp_engine.py` L361-366: uses `pd.Timedelta(days=N)` (calendar days). | **Medium** | First audit conflated the two Amihud constructs. | Window description in audit applies to wrong variable. `delta_amihud` uses +/-3 actual trading days; `amihud_illiq` uses calendar-day boundaries. | Document the correct window for `delta_amihud`: [-3,-1] and [+1,+3] trading days relative to the last trading date on or before call. |
| G7 | Prior red-team failure | The prior red-team audit (`docs/provenance/Audits/H7_red_team.md`) "confirmed" L1 (bad controls) at High severity in section H (RT-06) and section F1 ("No false positives identified"). It failed to check whether Volatility/StockRet are actually in `BASE_CONTROLS`. It also missed the DV misidentification. | Prior red-team H section: "L1 ... High -- confirmed"; F section: "No false positives identified." | **Critical** | Prior red-team inherited the first audit's framing without independently verifying the regression formula or control list. | Two layers of audit failed to catch the same errors, creating false confidence. | This red-team audit replaces both prior documents as the authoritative assessment. |

---

## H. Severity Recalibration

| Issue ID | Source | Original severity | Red-team severity | Why recalibrated | Thesis impact |
|---|---|---|---|---|---|
| L1 | First audit | High (blocking) | **DELETE -- FALSE POSITIVE** | Volatility/StockRet are not regression controls. Issue does not exist. | N/A |
| L2 | First audit | High | **Medium** | Non-unique panel index is real. PanelOLS handles it. Downgrade because it does not invalidate results. | N |
| L3 | First audit | High (blocking) | **REWRITE -- WRONG VARIABLE** | Statistics are for `amihud_illiq`, not `delta_amihud`. The actual DV has different problems (extreme tails, not right-skew). Replace with: "`delta_amihud` has extreme dispersion (SD=12.62, range [-99.6, 2678.2]); unwinsorized." Severity: **Critical** for the corrected formulation. | Y |
| L4 | First audit | High (blocking) | **REWRITE** | Log transform is inapplicable to a signed change variable. Replace with: "Winsorize `delta_amihud` at 1%/99% or test trimmed estimation." Severity: **High**. | Y |
| L5 | First audit | Medium | **Medium -- confirmed** | CEO_Clarity_Residual coverage issue is real. | N |
| L6 | First audit | Medium | **Medium -- confirmed** | Only firm + quarter FE; no alternatives tested. | N |
| L7 | First audit | Medium | **Low -- downgrade** | This issue applies to `amihud_illiq` (inter-call window), not `delta_amihud` (event-window). The actual DV uses a fixed +/-3 trading day window, not a variable-length inter-call window. | N |
| L8 | First audit | Medium | **Medium -- confirmed** | Entity-only clustering as primary; two-way in robustness. | N |
| L9 | First audit | Medium | **High -- upgrade** | No outlier sensitivity test AND the DV is unwinsorized with max/SD=212x. This is more severe than first audit realized because the DV has no winsorization at all. | Y |
| L10 | First audit | Medium | **Medium -- confirmed** | No placebo/falsification test. | N |
| L11-L17 | First audit | Low | **Low -- confirmed** | Minor issues accurately characterized. | N |
| G1 | Red-team | -- | **Critical** | DV misidentification throughout first audit. | Y |
| G3 | Red-team | -- | **Critical** | Unwinsorized DV and control with extreme values. | Y |
| G4 | Red-team | -- | **Medium** | Stale artifact problem. | N |
| G5 | Red-team | -- | **High** | Results characterization outdated; current run shows marginal significance. | Y |

---

## I. Completeness Gaps in the First Audit

| Missing / incomplete area | Why incomplete | Evidence | Severity | What should have been included |
|---|---|---|---|---|
| DV identification | Entire audit uses wrong variable (`amihud_illiq` instead of `delta_amihud`) | `run_h7_illiquidity.py` L201: formula uses `delta_amihud` | **Critical** | Correct DV name, construction (post - pre, +/-3 trading days), source builder (`AmihudChangeBuilder`), distributional properties |
| `pre_call_amihud` as control | Not documented as a regression control in spec register or identification section | `run_h7_illiquidity.py` L104: in `BASE_CONTROLS` | **Medium** | Document as lagged-DV control; discuss implications for change-specification identification |
| DV winsorization status | Audit assumes DV is winsorized (because `amihud_illiq` is); actual DV `delta_amihud` is not | `amihud_change.py`: no winsorization; `_crsp_engine.py` L445: only `CRSP_RETURN_COLS` winsorized | **Critical** | Flag that DV enters regression unwinsorized with extreme tails |
| `AmihudChangeBuilder` as DV source | Not traced or documented; audit traces only `AmihudIlliqBuilder` and `_crsp_engine.py` | `build_h7_illiquidity_panel.py` L103-104: `amihud_change: AmihudChangeBuilder(...)` | **High** | Trace the actual DV builder, its PERMNO mapping, window construction, and minimum-days filter |
| Current output state | Audit locked to older run; does not discuss possibility of changing results | `model_diagnostics.csv` (2026-03-13): different N, different p-values | **Medium** | Either pin to a specific run or note that results may vary with upstream changes |
| Alternative event window robustness | Panel builder creates `amihud_change_w5` (5-day window variant) but no regression uses it | `build_h7_illiquidity_panel.py` L106-108: `AmihudChangeBuilder({..., "window_days": 5, "column_suffix": "_w5"})` | **Low** | Note availability of alternative window; recommend testing as robustness |

---

## J. Reproducibility Red-Team Assessment

| Reproduction step | First audit documented it? | Verified? | Hidden dependency? | Risk | Red-team note |
|---|---|---|---|---|---|
| Stage 3: `python -m f1d.variables.build_h7_illiquidity_panel` | Y | Code path verified | H0.3 must have run for B-spec columns | Medium | If H0.3 absent, B-spec columns all-NaN; RuntimeError at L686-689 catches this |
| Stage 4: `python -m f1d.econometric.run_h7_illiquidity` | Y | Code path verified | Depends on "latest" Stage 3 output | Medium | `get_latest_output_dir()` picks most recent; stale artifacts possible |
| CRSP raw files in `inputs/CRSP_DSF/` | Y (implicit) | Not checked | Not in repo | High | Standard raw-data dependency |
| CCM linktable | Y (implicit) | Not checked | Not in repo | Medium | Required by `AmihudChangeBuilder._build_permno_map()` |
| H0.3 residual output | Y (noted) | Not checked | Must exist before Stage 3 | Medium | H0.3 command not in H7 docs |
| Output determinism | Y | Confirmed | None | N/A | PanelOLS is closed-form |
| Stale "latest" resolution | Y (L12) | Confirmed risk | `get_latest_output_dir()` | Medium | Outputs from different code versions coexist; 5 timestamped dirs found |
| AmihudChangeBuilder PERMNO mapping | Not documented | Code verified | Uses CCM date-bounded linkage independently of CRSPEngine | Low | Separate PERMNO mapping from CRSPEngine; potential for divergence if CCM data changes |

---

## K. Econometric and Thesis-Referee Meta-Audit

| Referee dimension | First audit adequate? | Why or why not | Missed or weak points | Severity |
|---|---|---|---|---|
| Identification threats | **Fail** | K2 fabricates a "bad controls" threat (Volatility/StockRet not in model). Misses the actual identification implication of using `pre_call_amihud` as a control in a change specification (effectively a lagged-DV control, which introduces Nickell bias in short panels). | Lagged-DV control in FE panel; Nickell bias | Medium |
| Inference / clustering | **Pass** | Firm clustering documented; adequate cluster count (1,845 in A3). | | |
| FE and within-variation | **Pass** | Non-unique index flagged; firm + quarter FE documented. | | |
| Timing alignment | **Partial** | Post-call window for DV is correct. But first audit describes the wrong window (inter-call calendar days for `amihud_illiq` vs event-window trading days for `delta_amihud`). | Window description wrong | Medium |
| Post-treatment controls | **Pass** | Compustat backward merge verified. | | |
| Reverse causality | **Pass** | DV is post-call; IV is at call time. Timing correct. | | |
| Endogenous sample selection | **Partial** | CEO identification gap flagged. But first audit does not discuss how `delta_amihud` missingness differs from `amihud_illiq` missingness (the change variable requires valid pre AND post windows). | | Low |
| Model-family-specific threats | **Fail** | DV distributional threat is about wrong variable. The actual DV `delta_amihud` is unwinsorized with extreme outliers -- more severe than described. | | Critical |
| Robustness adequacy | **Partial** | Robustness checks run. No test of DV winsorization sensitivity, no test of alternative event windows despite `_w5` being available in the panel. | | Medium |
| Interpretation discipline | **Partial** | Prior red-team corrected coefficient-direction issue. But "uniformly null" characterization is now outdated (A3, B2 marginally significant). | | High |
| Academic-integrity risks | **Partial** | Warning suppression flagged. But the bigger risk -- that the DV enters OLS unwinsorized with extreme leverage points -- is missed because the wrong DV was identified. | | Critical |

---

## L. Audit-Safety / Academic-Integrity Assessment of the First Audit

| Audit-safety risk in first audit | Evidence | Severity | Why it matters | Fix |
|---|---|---|---|---|
| DV misidentified throughout | All DV references say `amihud_illiq`; actual DV is `delta_amihud` | **Critical** | A thesis committee reading the audit would believe the DV is the Amihud illiquidity level. It is actually a change measure. This affects interpretation, identification assessment, and recommended fixes. | Correct all DV references |
| Fabricated blocking issue (L1) | Volatility/StockRet "bad controls" -- not in model | **Critical** | A referee would believe the model has a "bad controls" problem warranting revision. It does not. This creates unnecessary revision demand and distracts from real issues. | Delete L1 and all references to Volatility/StockRet as controls |
| Prior red-team failed to catch same errors | `Audits/H7_red_team.md` confirms L1 at High, misses DV error | **High** | Two audit layers agreeing on wrong facts creates strong false confidence | This audit supersedes both prior documents |
| DV distributional properties mischaracterized | Skewness/kurtosis statistics are for `amihud_illiq`, not `delta_amihud` | **High** | Recommended fix (log transform) is inapplicable to the actual DV; correct fix (winsorization) is never recommended | Recompute distributional stats for `delta_amihud`; recommend winsorization |
| Results outdated | "Uniformly null" vs current marginal significance for A3/B2 | **High** | Committee would believe no evidence for H7 exists. Current output suggests marginal evidence at 10% level for Manager QA uncertainty. | Update results; discuss implications of marginal significance |

---

## M. Master Red-Team Issue Register

| Issue ID | Type | Category | Verified? | Severity | Location | Description | Evidence | Consequence | Recommended fix | Blocks thesis-standard reliance on first audit? |
|---|---|---|---|---|---|---|---|---|---|---|
| RT2-01 | First-audit factual error | DV identification | Y | **Critical** | H7.md: A3, F, H (all rows), I2, I5-I6, J2, K2, K3, L1, L3, L4, L15, M, N | DV identified as `amihud_illiq` throughout; actual DV is `delta_amihud` | `run_h7_illiquidity.py` L188,201: `"delta_amihud ~ ..."`. Regression output: "Dep. Variable: delta_amihud" | All DV-related analysis (distributional, transformational, winsorization) applies to wrong variable | Rewrite all DV references; recompute distributional statistics for `delta_amihud` | **Y** |
| RT2-02 | First-audit false positive | Identification | Y | **Critical** | H7.md: K2, K3, L1, M #2, N | Fabricated "bad controls" issue: claims Volatility/StockRet are controls sharing DV window. They are not in BASE_CONTROLS and not in any regression. | `run_h7_illiquidity.py` L97-105: BASE_CONTROLS does not contain Volatility or StockRet. Grep: zero matches. | False blocking issue; distorts severity calibration and priority fixes | Delete L1; remove all Volatility/StockRet references from identification/controls discussion | **Y** |
| RT2-03 | Underlying implementation issue missed by first audit | Outlier/winsorization | Y | **Critical** | `amihud_change.py` | `delta_amihud` is NOT winsorized. Range [-99.6, 2678.2], SD=12.62. `pre_call_amihud` also unwinsorized (max=267.8). Both enter OLS raw. | `amihud_change.py`: zero "winsor" matches. `summary_stats.csv`: delta_amihud max=2678.2, pre_call_amihud max=267.8 | Extreme observations dominate OLS estimation; single outlier has leverage 212x SD | Add per-year 1%/99% winsorization to `delta_amihud` and `pre_call_amihud` before regression | **Y** |
| RT2-04 | First-audit false positive | Econometric spec | Y | **High** | H7.md: L3, L4, M #1 | DV skewness characterized using `amihud_illiq` statistics; log-DV recommendation inapplicable to signed change variable `delta_amihud` | `summary_stats.csv`: delta_amihud takes negative values; `log(1+x)` undefined for x<-1 | Recommended fix is wrong; correct fix (winsorization) never recommended | Replace log-DV recommendation with winsorization/trimming for `delta_amihud` | **Y** |
| RT2-05 | First-audit unsupported claim | Results | Y | **High** | H7.md: I13, K1, N | "ALL uncertainty coefficients are statistically insignificant" -- outdated. Current run: A3 p_one=0.069, B2 p_one=0.080; LaTeX table shows 10% stars. | `model_diagnostics.csv` (2026-03-13 run) and `h7_illiquidity_table.tex` | Audit overstates null-result certainty; committee would not know about marginal evidence | Update results to reflect current output; discuss marginal significance | **Y** |
| RT2-06 | First-audit factual error | Sample counts | Y | **Medium** | H7.md: H, E2 | N values from older run (A3: 75,124) differ from latest run (A3: 78,679) by ~5% | Compare `model_diagnostics.csv` across runs | Audit claims not reproducible from current code | Pin to specific run or update | N |
| RT2-07 | Underlying implementation issue missed by first audit | Identification | Y | **Medium** | `run_h7_illiquidity.py` L104 | `pre_call_amihud` is a lagged-DV control in a change specification with entity FE. This introduces Nickell (1981) bias in panels with short T. The first audit does not discuss this. | `pre_call_amihud` in BASE_CONTROLS; entity FE present; T varies by firm but many firms have <20 calls | Bias toward zero on the lagged-DV coefficient; potential attenuation of IV estimates | Discuss Nickell bias; consider Anderson-Hsiao or system-GMM as robustness | N |
| RT2-08 | First-audit omission | Variable dictionary | Y | **Medium** | H7.md F | Variable dictionary lists `amihud_illiq` as DV, `Volatility` and `StockRet` as controls, but omits `delta_amihud` (actual DV) and `pre_call_amihud` (actual control) | Compare F table with `BASE_CONTROLS` and regression formula | Referee cannot understand the actual model from the variable dictionary | Add `delta_amihud` and `pre_call_amihud`; remove phantom variables | **Y** |
| RT2-09 | Underlying implementation issue noted by first audit | Panel index | Y | **Medium** | `run_h7_illiquidity.py` L212-217 | Non-unique (gvkey, call_quarter_int) index. PanelOLS handles this but interpretation of entity/time FE affected. | Code warns on duplicates; structurally inherent when firms have multiple calls/quarter | FE demeaning treats same-quarter calls as sharing a time period; SE implications | Document; consider call-level time index | N |
| RT2-10 | First-audit omission | Robustness | Y | **Low** | `build_h7_illiquidity_panel.py` L106-108 | Alternative 5-day event window (`amihud_change_w5`) built in panel but never tested in regressions | Panel builder creates it; runner ignores it | Available robustness check not exploited | Add 5-day window specification to robustness battery | N |
| RT2-11 | Prior red-team failure | Audit chain | Y | **Critical** | `docs/provenance/Audits/H7_red_team.md` | Prior red-team confirmed fabricated L1 at High severity (RT-06), stated "No false positives identified" (F1), and missed DV misidentification | Prior audit H table, F table | Two audit layers agree on fundamental errors; dangerous for academic reliance | This audit replaces prior red-team | **Y** |

---

## N. What a Committee / Referee Would Still Not Know if They Read Only the First Audit

1. **That the DV is `delta_amihud` (a change measure), not `amihud_illiq` (a level).** This affects every aspect of interpretation: the economic question is "does vagueness change illiquidity around the call?" not "does vagueness predict illiquidity levels." The change specification controls for pre-call levels via `pre_call_amihud` and uses a +/-3 trading-day event window, not an inter-call window.

2. **That Volatility and StockRet are NOT regression controls.** The audit's "bad controls" critique (L1, rated High and blocking) is entirely fabricated. The actual controls are: Entire_All_Negative_pct, Analyst_QA_Uncertainty_pct, Size, Lev, ROA, TobinsQ, pre_call_amihud.

3. **That the DV `delta_amihud` is completely unwinsorized.** Range [-99.6, 2678.2] with SD=12.62. A single observation with delta_amihud=2678 has leverage 212x the standard deviation. The `pre_call_amihud` control is also unwinsorized (max=267.8). This is the actual most serious specification issue -- far more severe than the fabricated L1.

4. **That the "uniformly null" result is outdated.** Current code produces marginal one-tailed significance for A3 (Manager QA: beta=0.33, p=0.069) and B2 (Manager Clarity Residual: beta=0.007, p=0.080). The LaTeX table shows 10% significance stars. The null is not as clean as the audit claims.

5. **That log transformation is inapplicable to the actual DV.** `delta_amihud` takes negative values. The recommended fix `log(1+amihud_illiq)` applies to a different variable and a different specification.

---

## O. Priority Fixes to the First Audit

| Priority | Fix to first audit | Why it matters | Effort | Credibility gain |
|---|---|---|---|---|
| 1 | **Correct DV identification from `amihud_illiq` to `delta_amihud` throughout.** Update A3, F (variable dictionary), H (all spec rows), I2, I5-I6, J2, K2-K4, L1-L4, M, N. | Without this, every DV-related analysis is about the wrong variable. A referee would fundamentally misunderstand the model. | Medium -- many sections affected | **Critical** -- transforms audit from materially flawed to factually correct |
| 2 | **Delete L1 and all Volatility/StockRet "bad controls" references.** Remove from K2, K3, L1, M priority #2, N final statement. | Fabricated blocking issue distorts the entire severity structure and priority fix list. | Low -- text deletions | **Critical** -- removes the most misleading finding |
| 3 | **Add critical issue: unwinsorized DV and control.** Document that `delta_amihud` (range [-99.6, 2678.2]) and `pre_call_amihud` (max=267.8) enter OLS unwinsorized. Rate as Critical/blocking. | This is the actual most serious specification issue. Without winsorization, OLS estimates are dominated by extreme leverage points. | Low -- add new issue to register | **Critical** -- identifies the true blocking issue |
| 4 | **Replace log-DV recommendation with winsorization.** L4 should recommend winsorizing `delta_amihud` at 1%/99% per year, not log-transforming a signed change. | Log transform is mathematically inapplicable to the actual DV. Winsorization is the correct fix. | Low -- text edit | **High** -- correct recommendation |
| 5 | **Update results to current output.** A3: N=78,679, beta=0.33, p_one=0.069; B2: p_one=0.080. Note marginal significance at 10%. | "Uniformly null" characterization is outdated and potentially misleading. | Low -- update numbers | **High** -- honest reporting |
| 6 | **Add `AmihudChangeBuilder` to dependency chain and variable dictionary.** | The actual DV source is undocumented. | Medium | **Medium** |
| 7 | **Discuss `pre_call_amihud` as lagged-DV control and Nickell bias.** | Important identification consideration for panel FE with lagged DV. | Low | **Medium** |

---

## P. Final Red-Team Readiness Statement

**Can the first audit be trusted as a standalone referee-quality document?**
No. The first audit contains two fundamental factual errors -- wrong DV identification and fabricated blocking issue -- that permeate its analysis, severity calibration, and recommendations. A referee relying on the audit would (a) believe the model estimates Amihud illiquidity levels when it estimates changes, (b) believe there is a "bad controls" problem with Volatility/StockRet when these are not in the model, (c) miss that the actual DV is unwinsorized with extreme outliers, and (d) believe all results are null when current output shows marginal significance.

**Biggest factual weakness:**
The DV is `delta_amihud` (a signed change measure), not `amihud_illiq` (a bounded-below level). Every DV-related claim in the audit -- distributional statistics, winsorization status, recommended transformation, identification implications -- applies to the wrong variable.

**Biggest completeness weakness:**
The audit entirely omits that `delta_amihud` and `pre_call_amihud` are unwinsorized. This is the single most serious specification issue in the implementation.

**Biggest severity/judgment weakness:**
L1 (Volatility/StockRet "bad controls") is a fabricated High-severity blocking issue. It distorted the entire priority structure: priorities #1 and #2 in the referee fix list address nonexistent problems, while the actual critical issue (unwinsorized DV) was never identified.

**Single most important missed issue:**
The DV `delta_amihud` enters OLS completely unwinsorized with range [-99.6, 2678.2] and SD=12.62. A single extreme observation has leverage 212x the SD. This makes all coefficient estimates unreliable and is the true blocking issue for thesis-standard reliance.

**Single most misleading claim:**
K2/K3/L1: "Volatility and StockRet are computed over the SAME window as amihud_illiq... Including Volatility as a control absorbs the variation that the IV is trying to explain -- the 'bad control' problem." These variables are not in the model. This false positive was then confirmed by the prior red-team audit, creating two layers of fabricated agreement.

**What a thesis committee should believe after reading this red-team review:**
The H7 suite is a competently structured change-event study (delta_amihud around earnings calls with firm+quarter FE and entity-clustered SEs). The model specification is reasonable -- controls for pre-call Amihud, negative sentiment, analyst uncertainty, and standard financial variables. The critical implementation deficiency is that neither the DV nor the `pre_call_amihud` control is winsorized, allowing extreme leverage points to dominate estimation. Current output shows marginal evidence (10% level) that Manager QA uncertainty increases post-call illiquidity change (A3: beta=0.33, p=0.069; B2: beta=0.007, p=0.080). Before this result can be trusted, the DV and controls must be winsorized, and the committee must see distributional diagnostics for the actual variable being estimated. The first-layer audit and prior red-team audit should NOT be relied upon due to fundamental factual errors. This red-team audit supersedes both.

---

*End of H7 Second-Layer Red-Team Audit.*
*Auditor: Claude Opus 4.6 (1M context, fresh context) | Date: 2026-03-15*
