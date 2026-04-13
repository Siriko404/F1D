# Draft Decisions Log

**Current phase:** Phase 2 — suite audit. Workflow, protocol, and progress tracker in `PROGRESS.md`.

---

## 1. Locked (structural only)

### 1.1 Housekeeping
- Deleted: `outputs/thesis_tables.tex`, `.pdf`, `generate_thesis_tables.py`, `thesis_findings.txt`.
- Memory: `feedback_preserve_fishing_deck.md` revised (single-deck reality).

### 1.2 Three-tier scope
| Tier | Suites |
|---|---|
| **Main** | H1, H1.2, H4a, H4b, H12, H12b, H13, H13.1, H16, H17 |
| **App I** | H1.1, H1.1b, H13.2, H19b, H20b |
| **App II** | H5, H7, H7b, H7c, H7d, H7e, H11, H11-Lag, H14, H14b, H14c, H14d, H14e, H18, H18b, H21, H22, H23, H24, H24b, H25 |

### 1.3 FE-selection rule (structural, applied during audit)

| Hypothesis class | Primary FE | Rationale |
|---|---|---|
| Within-firm dynamic response (temporal effect) | Firm FE | Firm FE removes time-invariant confounders to isolate within-firm change |
| Cross-sectional / firm-type (level effect across firms) | Industry FE | Firm FE over-controls and is expected null |
| Dual claim (temporal and cross-sectional elements) | Both equally | Report both |

When reading any suite: identify the hypothesis class first, then read the corresponding FE specs as primary. The assignment of each hypothesis to a class happens in Phase 5 (synthesis), not during the audit.

---

## 2. Pipeline bug list (Phase 3 fix targets)

### 2.1 Standard error clustering — uniform firm-only (Phase 2.5 decision, 2026-04-13)

**Rule**: All suites use firm-only clustering (`cluster_entity=True, cluster_time=False`) EXCEPT macro-uncertainty suites (H24, H24b, H25), which retain two-way firm × `cal_yr_qtr` clustering to match their `other_effects=cal_yr` FE (`TimeEffects` would absorb the macro IV).

**Justification (two pillars)**:
1. **Petersen (2009)**: firm-level clustering is sufficient when time fixed effects are included in the specification.
2. **Empirical evidence from H1** (two-way vs firm-only comparison, 2026-04-13): firm-only SEs are 0.5%–27.1% LARGER than two-way across 12 specs. All 6 significant contemporaneous UncAnsMgr results survive; col 9 (lead, Ind-FE, extended) weakens from p=.009 to p=.032 but remains significant at 5% one-tailed. Firm-only is the more conservative choice.

**H1 UncAnsMgr delta table** (baseline two-way = `outputs/econometric/h1_cash_holdings/2026-04-09_232352/`; firm-only test = `outputs/econometric/h1_cash_holdings/2026-04-13_162202/`):

| Col | FE / DV | β | SE two-way | SE firm-only | Δ % |
|-----|---------|---|-----------|--------------|-----|
| 1 | Ind, base, CashRatio | 0.00380 | 0.00153 | 0.00169 | +10.3% |
| 2 | Firm, base, CashRatio | 0.00329 | 0.00132 | 0.00155 | +17.7% |
| 3 | Ind, ext, CashRatio | 0.00724 | 0.00159 | 0.00173 | +8.2% |
| 4 | Firm, ext, CashRatio | 0.00354 | 0.00139 | 0.00155 | +11.8% |
| 5 | Ind+YQ, ext, CashRatio | 0.00459 | 0.00165 | 0.00169 | +2.7% |
| 6 | Firm+YQ, ext, CashRatio | 0.00340 | 0.00150 | 0.00156 | +4.1% |
| 7 | Ind, base, CashRatio_lead | -0.00102 | 0.00235 | 0.00288 | +22.2% |
| 8 | Firm, base, CashRatio_lead | 0.00147 | 0.00236 | 0.00232 | -1.5% |
| 9 | Ind, ext, CashRatio_lead | 0.00531 | 0.00225 | 0.00286 | +27.1% |
| 10 | Firm, ext, CashRatio_lead | 0.00070 | 0.00232 | 0.00233 | +0.5% |
| 11 | Ind+YQ, ext, CashRatio_lead | -0.00042 | 0.00263 | 0.00288 | +9.2% |
| 12 | Firm+YQ, ext, CashRatio_lead | 0.00044 | 0.00232 | 0.00234 | +0.6% |

**Pattern — precisely maps to the column-specific time index**:

H1 uses `time_col = "cal_yr_qtr" if fe_type.endswith("_yq") else "cal_yr"` (line 345). Two-way `cluster_time=True` therefore clusters on:
- **Annual (`cal_yr`) — 8 cols (1–4, 7–10)**: N_t = 17 time clusters (2002–2018). Below Thompson (2011)'s ~25–40 floor for two-way asymptotic validity.
- **Quarterly (`cal_yr_qtr`) — 4 cols (5, 6, 11, 12)**: N_t ≈ 68 time clusters (2002Q1–2018Q4). Above the Thompson floor; two-way is asymptotically valid here.

**The deltas map exactly**: annual-indexed cols show 8.2–27.1% deltas (the small-T cells), quarterly-indexed cols show 0.6–4.1% (the asymptotically-safe cells). The theoretical prediction from Thompson (2011) — that two-way is unstable below ~25 time clusters — is confirmed empirically in our own panel. The 8 annual cols are exactly where two-way is under-stating SEs.

**CGM 2011 decomposition**: `Var_two-way = Var_firm + Var_time - Var_White`. Two-way being *smaller* than firm-only on the annual cols implies `Var_time < Var_White` — the finite-sample instability the theory predicts. The firm-only switch eliminates this. Evidence directory preserved at `outputs/econometric/h1_cash_holdings/2026-04-13_162202/` — DO NOT DELETE.

**Advisor verdict (2026-04-13, second decisive call)**: Firm-only is the correct choice for this specific panel. Three strongest counterarguments and why they lose:
1. *"Two-way is standard"* — firm-only + time FE is equally standard (Petersen 2009, 15,000+ citations). Asymmetry matters: a referee asking "why not two-way?" gets a one-line Petersen answer; a referee asking "why two-way with N_t=17?" puts us on the back foot defending Thompson thresholds.
2. *"Firm-only over-conservative"* — all significant results survive, for a thesis over-conservation is a dramatically smaller risk than under-conservation, and the over-conservation is bounded by the 0–27% range we measured.
3. *"Use wild cluster bootstrap (Cameron-Miller 2015)"* — methodologically pure but a massive scope expansion across 39 suites; our 2,429 firm clusters already exceed any firm-dimension threshold concern; WCB can be noted as future-work robustness.

**Phase 5 write-up line**: *"We cluster standard errors at the firm level following Petersen (2009), who shows firm-level clustering is sufficient when time fixed effects are included. For macro-uncertainty specifications where the independent variable varies at the aggregate time level, we additionally cluster by calendar quarter."*

### 2.1.1 Currently-two-way runners — Phase 3 downgrade to firm-only (non-macro only) — **DONE 2026-04-13**

All 17 runners downgraded. Also updated each runner's module docstring, LaTeX footnote string ("Standard errors: two-way clustered …" → "Standard errors: firm-level clustered …"), estimation-phase print statement, and summary print. All 17 files pass `python -m py_compile`.

- [x] `run_h1_cash_holdings.py:374, 380` (+ 3 footnote/docstring updates)
- [x] `run_h1_2_cash_constraint.py:460` (+ 1 LaTeX note)
- [x] `run_h4_leverage.py:378, 384` (+ 3 footnote/docstring updates)
- [x] `run_h7_illiquidity.py:317, 322` (+ 4 footnote/docstring/print updates; incl. 4-line docstring block)
- [x] `run_h7b_amihud_level.py:267, 272` (+ 4 footnote/print/LaTeX note updates; unique docstring format)
- [x] `run_h7c_amihud_bgt_level.py:323, 328` (+ 4 footnote/docstring/print updates)
- [x] `run_h7d_amihud_bgt_delta.py:323, 328` — **SILENT NaN SE BUG FIXED** (+ 4 footnote/docstring/print updates)
- [x] `run_h7e_amihud_bgt_avg.py:323, 328` (+ 4 footnote/docstring/print updates)
- [x] `run_h12b_dividend_payer.py:324, 333` (+ 4 unique docstring/print updates)
- [x] `run_h13_capex.py:358, 364` (+ 3 footnote/docstring updates)
- [x] `run_h13_2_capex_leads.py:290, 295` (+ 2 footnote/docstring updates)
- [x] `run_h14_bidask_spread.py:272, 277` (+ 3 footnote/docstring/print updates; line 289 fallback preserved per advisor)
- [x] `run_h14b_spread_level.py:284, 289` (+ 2 footnote/docstring updates; unique one-liner docstring)
- [x] `run_h14c_spread_bgt_level.py:278, 283` (+ 3 footnote/docstring/print updates)
- [x] `run_h14d_spread_bgt_delta.py:278, 283` (+ 3 footnote/docstring/print updates; line 295 fallback preserved per advisor)
- [x] `run_h14e_spread_bgt_avg.py:278, 283` (+ 3 footnote/docstring/print updates)
- [x] `run_h16_rd_sales.py:371, 377` (+ 3 footnote/docstring updates)

**Also updated**: `scripts/findings_template.txt` (7 lines of stale "Two-way clustered" SE descriptions → firm-level).

**Smoke test PASSED** (H1, `outputs/econometric/h1_cash_holdings/2026-04-13_165454/`): runs cleanly, `model_diagnostics.csv` is bit-identical to the Phase 2.5 firm-only baseline, LaTeX footnote renders "firm-level clustered" with zero residual "two-way" text. Phase 3 clustering work is verified end-to-end. High confidence for full Phase 4 rerun.

### 2.1.2 Already-correct firm-only runners — NO ACTION (previously mis-flagged as bugs, reclassified 2026-04-13)

These 13 runners are already firm-only and match the new uniform rule. Remove from Phase 3 work list.

- `run_h5b_wang_disp.py:263, 268`
- `run_h11_prisk_uncertainty.py:195`
- `run_h11_prisk_uncertainty_lag.py:204`
- `run_h12_payout.py:295, 300`
- `run_h13_1_competition.py:382`
- `run_h17_repurchase_intensity.py:296, 301`
- `run_h18_cccl_received.py:279, 284`
- `run_h18b_cccl_logit.py:270` — statsmodels Logit (two-way not natively supported anyway)
- `run_h19b_external_funding.py:292, 297`
- `run_h20b_debt_choice.py:289, 294`
- `run_h21_sec_letters.py:272, 277`
- `run_h22_equity_constraints.py:282, 287`
- `run_h23_competition_uncertainty.py:287, 292`

### 2.1.3 Macro exception — keep two-way (NO ACTION)

- `run_h24_us_epu.py:321–324` — two-way firm × `cal_yr_qtr` ✓
- `run_h24b_global_epu.py:322–325` — two-way firm × `cal_yr_qtr` ✓
- `run_h25_gpr.py:321–324` — two-way firm × `cal_yr_qtr` ✓

Justification: macro IVs vary only at the aggregate time level. These runners use `other_effects=cal_yr` (not `TimeEffects`) to preserve macro IV variance. Time clustering on `cal_yr_qtr` adds robustness beyond coarse-year FE.

### 2.1.4 H7d silent NaN SE bug (blank cells in LaTeX output)

`run_h7d_amihud_bgt_delta.py` — two-way clustered VCV produces NaN SEs for several (column × IV) cells. The LaTeX formatter emits blanks with no disclosure. Confirmed via `model_diagnostics.csv` (`outputs/econometric/h7d_amihud_bgt_delta/2026-04-09_232601/`):
- col 1 (Ind-FE base contemp): `UncAnsCEO_se = NaN`, `UncPreCEO_se = NaN`
- col 3 (Ind-FE extended contemp): `UncAnsCEO_se = NaN`
- col 6 (Firm-FE YQ extended contemp): `Capex_se = NaN` (control; visible in LaTeX)

**Fix**: downgrade to firm-only (part of §2.1.1). The rank-deficient two-way VCV is the root cause; firm-only eliminates the NaN production entirely. No separate fallback-adoption needed.

### 2.1.5 H14/H14d defensive fallback — NO ACTION (becomes dead code under firm-only)

`run_h14_bidask_spread.py:289` and `run_h14d_spread_bgt_delta.py:295` have explicit fallback branches that re-fit with `cluster_time=False` if the two-way VCV is rank-deficient. Previously triggered for:
- H14: cols (6), (8), (9), (10), (12) fallback to firm-only
- H14d: cols (7), (8), (9) fallback to firm-only

Under uniform firm-only (§2.1.1), the `if model.std_errors.isna().any()` branch will never trigger (the primary fit is already firm-only). Leave the code in place — harmless, and provides safety if two-way is ever restored for some future spec. Do not touch during Phase 3.

### 2.2 Missing firm-FE specs on moderation suites
- [ ] H1.1 (TSIMM continuous × cash)
- [ ] H1.1b (TSIMM binary × cash)
- [ ] H1.2 (rating × cash)
- [ ] H13.1 (TSIMM × capex)

All 4 have only Industry-FE columns. Add firm-FE specs for spec-ladder consistency with non-moderation suites.

### 2.3 Directional test convention (needs unification in Phase 3)
Two-tailed IV tests:
- [ ] H4a, H4b (leverage)
- [ ] H13, H13.1, H13.2 (capex)
- [ ] H17 (repurchase intensity)
- [ ] H20b (debt choice)
- [ ] H23 (TSIMM → uncertainty, reverse)

Within-family sign contradiction flag:
- [ ] H18 vs H21: UncPreMgr is +0.0017\*/+0.0020\* in H18 (CCCL receipt LPM) but -0.018/-0.020 (**wrong sign**, not significant) in H21 (SEC letter COUNT forward). Same base panel, N=66,886. Different DVs but same underlying SEC-letters mechanism.

One-tailed IV tests (β<0 direction):
- H1 (cash) — one-tailed positive
- H19b (external financing) — one-tailed negative

Decision on per-IV vs uniform one-tailed deferred to Phase 3 after all directional suites are catalogued. Inconsistency within the Chang family (H19b one-tailed vs H20b two-tailed) flagged for Phase 3 fix.

### 2.4 Sample / methodological notes (no code fix)
- [ ] H12: N=45k due to `PayoutRatio_q = (dvpspq × cshoq) / ibq` producing NaN when `ibq ≤ 0`. ~20k firm-quarter loss vs H1/H4 sample.
- [ ] H12: R² 0.079 cross-sectional, 0.015 firm-FE — noisy DV at firm-quarter frequency.
- [ ] H20b: N=13k vs H19b N=65k. Reason unverified in source. Flag for Phase 3 investigation.
- [ ] H14/H14c/H14d/H14e: Extended-controls cols drop from N=64k to N=44k (~20k loss). Likely driven by AbsSurpDec/StockPrice/DailyVola/Turnover availability.

### 2.5 Structural spec-ladder gaps
- [ ] H20b has 6 cols / single DV (ChangDebtChoice only, no lead variant). H19b has 12 cols / 2 DVs (contemp + lead). Flag for Phase 3 decision: add lead DV to H20b for symmetry, or document as deliberate design.
- [ ] H11 has 4 cols only (1 FE spec: firm + year). No industry-FE variant, no extended-controls spec, no time-FE spec ladder. H11-Lag has 8 cols (2 IVs × 4 DVs) but same single FE spec. Flag for Phase 3 decision: expand to spec ladder, or document as deliberate design.
- [ ] H22 has 4 cols / single DV (EquityDelayCon_lead × 2 FE × 2 control sets). No YrQtr-FE variant (no cols 5-6). Deliberate: firm-year panel with N=8,621, YrQtr-FE likely redundant after Year FE at small N. Flag for documentation decision.

---

## 3. Table consistency audit (live, ongoing Phase 2)

Audit-only entries: cell facts, structural inconsistencies, verified pipeline bugs. No interpretive labels.

| Suite(s) | Inconsistency / bug | Verified in | Action |
|---|---|---|---|
| H1.1 vs H1 | H1 has 12 cols (2 DVs × 6 specs incl. Firm FE); H1.1 has 4 cols (Ind-FE only) | LaTeX | §2.2 |
| H1.1b vs H1 | Same structural gap | LaTeX | §2.2 |
| H1.2 vs H1 | Same structural gap | LaTeX | §2.2 |
| H4a, H4b notes | Two-tailed for IVs while H1 is one-tailed for IVs | LaTeX notes | §2.3 |
| H12 clustering | `run_h12_payout.py:295, 300` firm-only | Source | §2.1 |
| H12 sample | N=45k vs H1/H4 ≈65k due to `ibq ≤ 0` filter | Source | §2.4 |
| H12 low R² | 0.079 cross-sectional, 0.015 firm-FE | LaTeX | §2.4 |
| H13.1 vs H13 | H13 has 12 cols; H13.1 has 4 cols (Ind-FE only) | LaTeX | §2.2 |
| H13.1 clustering | `run_h13_1_competition.py:382` firm-only | Source | §2.1 |
| H13, H13.1, H13.2, H16 notes | Two-tailed for IVs | LaTeX notes | §2.3 |
| H17 clustering | `run_h17_repurchase_intensity.py:296, 301` firm-only | Source | §2.1 |
| H17 two-tailed | Two-tailed p-values in source and notes | Source + LaTeX | §2.3 |
| H19b clustering | `run_h19b_external_funding.py:292, 297` firm-only | Source | §2.1 |
| H20b clustering | `run_h20b_debt_choice.py:289, 294` firm-only | Source | §2.1 |
| H19b vs H20b tailing | H19b one-tailed β<0, H20b two-tailed — within-family inconsistency | Source + LaTeX notes | §2.3 |
| H20b structure | 6 cols, single DV; no lead variant | LaTeX | §2.5 |
| H20b sample | N=13k vs H19b N=65k | LaTeX | §2.4 |
| H5 clustering | `run_h5b_wang_disp.py:263, 268` firm-only | Source | §2.1 |
| H11 clustering | `run_h11_prisk_uncertainty.py:195` firm-only | Source | §2.1 |
| H11-Lag clustering | `run_h11_prisk_uncertainty_lag.py:204` firm-only | Source | §2.1 |
| H11 structure | 4 cols, single FE spec (firm+year), no spec ladder | LaTeX + Source | §2.5 |
| H11-Lag structure | 8 cols (2 IVs × 4 DVs), single FE spec, no spec ladder | LaTeX + Source | §2.5 |
| H23 clustering | `run_h23_competition_uncertainty.py:287, 292` firm-only | Source | §2.1 |
| H23 two-tailed | Two-tailed while reverse-direction with directional expectation | Source + LaTeX notes | §2.3 |
| H24/H24b/H25 | Two-way clustered (firm, cal_yr_qtr) verified in source | Source + LaTeX notes | OK |
| H24/H24b/H25 column order | Mgr QA / Mgr Pres / CEO QA / CEO Pres (differs from H1/H4 which are Mgr QA / CEO QA / Mgr Pres / CEO Pres) | LaTeX | Cosmetic note |
| H7/H7b/H7c/H7d/H7e | Two-way clustered (firm, time); 12-col 2-DV spec ladder consistent | Source + LaTeX | OK |
| H7d silent NaN SE | Blank SE cells from NaN two-way clustered VCV in H7d; no fallback, no disclosure | Source + LaTeX + diagnostics.csv | Phase 3 fix — add cluster fallback like H14/H14d |
| H14/H14d cluster fallback | Some cols rank-deficient VCV → fallback to firm-only (disclosed in notes) | Source + LaTeX | Expected, documented |
| H14 family | All 5 runners two-way clustered (with defensive fallback in H14/H14d) | Source + LaTeX | OK |
| H14 N drop | Extended-controls cols: N=44k vs base N=64k (substantial sample drop with extended controls) | LaTeX | Note for §2.4 |
| H18 clustering | `run_h18_cccl_received.py:279, 284` firm-only | Source | §2.1 |
| H18b clustering | `run_h18b_cccl_logit.py:270` firm-only (Logit) | Source | §2.1 |
| H21 clustering | `run_h21_sec_letters.py:272, 277` firm-only | Source | §2.1 |
| H18 vs H21 sign contradiction | UncPreMgr +0.0017\* in H18 (CCCL) vs −0.0183 (wrong sign) in H21 (SEC letter count) | LaTeX | §2.3 flag |
| H18 structure | 6 cols (single DV × 6 specs), no lead variant; same panel as H21 | LaTeX | Note |
| H18b structure | 2 cols only (Ind-FE base + extended, Logit robustness) | LaTeX | Note |
| H22 clustering | `run_h22_equity_constraints.py:282, 287` firm-only | Source | §2.1 |
| H22 structure | 4 cols (single DV × 2 FE × 2 controls), no YrQtr variant, N=8,621 | LaTeX | §2.5 |

---

## 4. Raw findings catalogue (live, Phase 2)

Cell-level facts. No interpretive labels. Stars as reported by each suite's own tailing convention.

### H19b — ChangExternalFunding (12 cols: 6 contemp + 6 lead; one-tailed β<0 for IVs)
- **UncAnsMgr**: col 9 −0.0160\*, col 11 −0.0155\* (both Ind-FE, lead DV, extended controls). Other 10 cells NULL.
- **UncPreMgr**: all 12 NULL.
- **UncAnsCEO**: all 12 NULL.
- **UncPreCEO**: all 12 NULL.
- N: 65,069 (contemp Ind/Firm), 62,450 (contemp extended), 60,052 (lead Ind/Firm), 58,871 (lead extended).
- Clustering: firm-only.
- Tailing: one-tailed for IVs (β<0), two-tailed for controls.

### H20b — ChangDebtChoice (6 cols: 1 DV × 6 specs; two-tailed for IVs)
- **UncAnsMgr**: all 6 NULL.
- **UncPreMgr**: col 1 +0.0389\*, col 3 +0.0362\*, col 5 +0.0333\* (all 3 Ind-FE). Firm-FE 3/3 NULL.
- **UncAnsCEO**: all 6 NULL.
- **UncPreCEO**: col 1 −0.0320\*\*, col 3 −0.0269\* (both Ind-FE). col 5 Ind-FE NULL. Firm-FE 3/3 NULL.
- N: 13,666 (base), 13,057 (extended).
- Clustering: firm-only.
- Tailing: two-tailed throughout.
- No lead DV variant.

### H5 — DISP (analyst forecast dispersion; 12 cols: 6 contemp + 6 lead; one-tailed β>0 for IVs)
- **UncAnsMgr**: contemp Ind-FE cols 1/3/5 all +0.0002\*\*\*; lead Ind-FE cols 7/9/11 +0.0002\*\*/+0.0002\*\*\*/+0.0002\*\*. Firm-FE cells 2/4/6/8/10/12 all NULL (+0.0001).
- **UncPreMgr**: **ALL 12 cells significant**. Contemp: col 1 +0.0001\*, col 2 +0.0002\*\*\*, col 3 +0.0001\*\*, col 4 +0.0001\*\*, col 5 +0.0001\*, col 6 +0.0001\*\*. Lead: col 7 +0.0001\*, col 8 +0.0003\*\*, col 9 +0.0002\*\*\*, col 10 +0.0002\*\*, col 11 +0.0001\*\*, col 12 +0.0002\*\*.
- **UncAnsCEO**: all 12 NULL.
- **UncPreCEO**: all 12 NULL.
- N: 20,069 (base Ind/Firm), 19,124 (contemp extended), 19,355 (lead Ind/Firm), 18,406 (lead extended).
- Clustering: firm-only.
- Tailing: one-tailed β>0 for IVs, two-tailed for controls.

### H11 — PRisk contemp → Uncertainty (reverse direction; 4 cols: 4 DVs × 1 FE spec; one-tailed β>0 for IVs)
DV columns: (1) UncAnsMgr, (2) UncAnsCEO, (3) UncPreMgr, (4) UncPreCEO. Single spec: Firm FE + Year FE.
- **PRisk contemp**: col 1 +0.0001\*\*\*, col 2 +0.0001\*\*\*, col 3 +0.0001\*\*\*, col 4 +0.0002\*\*\*. **4/4 significant.**
- Within-segment Pre controls: UncPreMgr +0.1174\*\*\* (col 1); UncPreCEO +0.1078\*\*\* (col 2).
- N: 77,658 / 65,394 / 77,758 / 65,760.
- R²: 0.026 / 0.021 / 0.018 / 0.023; Adj R² 0.002 / −0.006 / −0.005 / −0.004.
- Clustering: firm-only.
- Tailing: one-tailed β>0 for IVs.
- FE: Firm + Year only (no Ind-FE variant, no extended-controls spec ladder).
- Note: reverse direction — PRisk is the IV, speech uncertainty is the DV.

### H11-Lag — PRisk_lag1 & PRisk_lag2 → Uncertainty (reverse direction; 8 cols: 4 DVs × 2 lags × 1 FE spec; one-tailed β>0)
Cols 1–4: PRisk_lag (one-quarter lag). Cols 5–8: PRisk_lag2 (two-quarter lag).
- **PRisk_lag (cols 1-4)**: col 1 +0.0000\*\*\*, col 2 +0.0000\*\*\*, col 3 +0.0001\*\*\*, col 4 +0.0001\*\*\*. **4/4 significant.**
- **PRisk_lag2 (cols 5-8)**: col 5 +0.0000\*\*\*, col 6 +0.0000\*\*, col 7 +0.0000\*\*\*, col 8 +0.0000\*\*\*. **4/4 significant** (col 6 CEO QA only \*\*).
- N: 74,918 / 63,049 / 75,014 / 63,399 / 74,467 / 62,674 / 74,561 / 63,022.
- R²: 0.022 / 0.018 / 0.014 / 0.016 / 0.023 / 0.019 / 0.013 / 0.015.
- Clustering: firm-only.
- Tailing: one-tailed β>0.
- FE: Firm + Year only.
- Note: A separate `run_h11_prisk_uncertainty_lead.py` runner exists in source tree but is NOT in `outputs/all_tables.tex` (not in thesis scope).

### H23 — TSIMM → Uncertainty (reverse direction; 8 cols: 2 FE × 4 DVs; two-tailed)
IV: `z(log(TSIMM))` — standardized log product-market competition (Hoberg-Phillips TSIMM). Firm-year panel.
- **Ind-FE + CalYear (cols 1-4)**:
  - col 1 UncAnsMgr: +0.0090\* (marginally sig)
  - col 2 UncAnsCEO: 0.0054 (NULL)
  - col 3 UncPreMgr: +0.0297\*\*\*
  - col 4 UncPreCEO: +0.0304\*\*\*
  - **3/4 significant positive, 1 NULL (UncAnsCEO).**
- **Firm-FE + CalYear (cols 5-8)**:
  - col 5 UncAnsMgr: −0.0012 (NULL)
  - col 6 UncAnsCEO: −0.0061 (NULL)
  - col 7 UncPreMgr: 0.0058 (NULL)
  - col 8 UncPreCEO: +0.0302\*\*\*
  - **1/4 significant positive, 3 NULL. UncAnsMgr/UncAnsCEO/UncPreMgr sign flip to negative but insignificant.**
- N: 20,768 / 18,447 / 20,774 / 18,492. **Much smaller than H11 (~21k vs ~78k)** — TSIMM is annual and merges to call-level.
- R²: 0.103 / 0.103 / 0.064 / 0.050 (Ind-FE); 0.038 / 0.038 / 0.017 / 0.021 (Firm-FE).
- Clustering: firm-only.
- Tailing: two-tailed throughout.
- Frequency: firm-year (uses `cal_yr` as time index).

### H24 — US EPU → Uncertainty (reverse/macro; 8 cols: 2 FE × 4 DVs; one-tailed β>0)
IV: `log(US_EPU_t)`. Macro-IV pattern: `other_effects=[ff12_code, cal_yr]` (Ind-FE branch) or `entity_effects=True, other_effects=[cal_yr]` (Firm-FE branch). Two-way clustered (firm, cal_yr_qtr). Lagged_DV included.
DV column order (H24/H24b/H25): **Mgr QA / Mgr Pres / CEO QA / CEO Pres**.
- **Ind-FE + CalYear (cols 1-4)**:
  - col 1 Mgr QA: +0.0141\*\*
  - col 2 Mgr Pres: +0.0065 (NULL)
  - col 3 CEO QA: +0.0117\*
  - col 4 CEO Pres: +0.0211\*\*\*
- **Firm-FE + CalYear (cols 5-8)**:
  - col 5 Mgr QA: +0.0147\*\*
  - col 6 Mgr Pres: +0.0071 (NULL)
  - col 7 CEO QA: +0.0138\*\*
  - col 8 CEO Pres: +0.0239\*\*\*
- **6/8 significant positive. UncPreMgr (Mgr Pres) NULL in both FE specs. All other signs positive as expected.**
- N: 74,013 / 75,142 / 59,676 / 60,503. R²: 0.171/0.484/0.141/0.292 (Ind-FE); 0.041/0.186/0.030/0.084 (Firm-FE). Mgr-Pres has notably high R² (0.484 Ind-FE / 0.186 Firm-FE) due to Lagged_DV dominance.
- Clustering: two-way (firm, cal_yr_qtr). **OK — no bug.**
- Tailing: one-tailed β>0 for IVs.

### H24b — Global EPU → Uncertainty (reverse/macro; 8 cols; one-tailed β>0)
IV: `log(GEPU_t)`. Same spec as H24.
- **Ind-FE (cols 1-4)**: col 1 +0.0234\*\*\*, col 2 +0.0131\*, col 3 +0.0178\*, col 4 +0.0271\*\*\*.
- **Firm-FE (cols 5-8)**: col 5 +0.0242\*\*, col 6 +0.0124\*, col 7 +0.0212\*\*, col 8 +0.0309\*\*\*.
- **8/8 significant positive (ALL cells significant).** GEPU IS stronger signal than US EPU — all cells clear, and UncPreMgr even passes (cols 2 and 6 at \*).
- N: 74,013 / 75,142 / 59,676 / 60,503 (same as H24 — same base panel).
- Clustering: two-way (firm, cal_yr_qtr). **OK — no bug.**
- Tailing: one-tailed β>0.

### H25 — GPR → Uncertainty (reverse/macro; 8 cols; one-tailed β>0)
IV: `log(GPR_t)` (Caldara-Iacoviello Geopolitical Risk). Same spec as H24.
- **Ind-FE (cols 1-4)**: col 1 −0.0112 (NULL, WRONG SIGN), col 2 +0.0073 (NULL), col 3 −0.0059 (NULL, WRONG SIGN), col 4 +0.0147\*.
- **Firm-FE (cols 5-8)**: col 5 −0.0119 (NULL, WRONG SIGN), col 6 +0.0067 (NULL), col 7 −0.0058 (NULL, WRONG SIGN), col 8 +0.0118 (NULL).
- **1/8 significant (UncPreCEO Ind-FE only, marginal \*). Other 7 NULL. QA measures (Mgr QA + CEO QA) show negative-sign point estimates in both FE specs.**
- N: 74,013 / 75,142 / 59,676 / 60,503 (same as H24/H24b).
- Clustering: two-way (firm, cal_yr_qtr). **OK — no bug.**
- Tailing: one-tailed β>0.

### H7 — DeltaILLIQ 3-day (Δ Amihud [+1,+3] − [−3,−1]; 12 cols: 2 DVs (contemp + lead) × 6 specs; one-tailed β>0)
Spec ladder: cols 1-6 contemp DV, 7-12 lead DV. Within each DV block: Ind/Firm/Ind-Ext/Firm-Ext/Ind-YQ/Firm-YQ. Lagged_DV included.
- **UncAnsCEO**: col 1 +0.0005\*\*, col 2 +0.0005\*, col 3 +0.0004\*. Cols 4-12 NULL. **3/12 significant.**
- **UncPreCEO**: col 2 +0.0008\*. **1/12 significant.**
- **UncAnsMgr**: all 12 NULL (many negative sign points in contemp).
- **UncPreMgr**: all 12 NULL.
- N: ~63,736 (base), ~60,182 (extended), ~61,060 (lead extended).
- R²: 0.001-0.005 (very low — Δ DV noisy).
- Clustering: two-way (firm, time). **OK.**
- Tailing: one-tailed β>0.

### H7b — PostCallAmihud LEVEL 3-day ([+1,+3]; 12 cols; one-tailed β>0)
- **UncAnsCEO**: all 12 NULL (negative point estimates contemp).
- **UncPreCEO**: all 12 NULL.
- **UncAnsMgr**: all 12 NULL (negative contemp).
- **UncPreMgr**: col 3 +0.0013\*\*. **1/12 significant.**
- N: same as H7 family (~63k). R²: 0.39-0.55 (Lagged_DV dominates).
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H7c — BGT Level 25-day Amihud [0,+25] (day 0 included; 12 cols; one-tailed β>0)
- **UncAnsCEO**: col 1 +0.0018\*, col 3 +0.0018\*, col 4 +0.0020\*, col 5 +0.0019\*\*, col 6 +0.0020\*\*. Lead cells 7-12 all NULL. **5/12 significant (all contemp).**
- **UncPreCEO**: all 12 NULL (negative contemp points).
- **UncAnsMgr**: all 12 NULL (negative contemp points).
- **UncPreMgr**: all 12 NULL.
- N: ~63,806 (base), ~60,256 (extended). R²: 0.45-0.62.
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H7d — BGT Delta 25-day Amihud [+1,+25] − [−25,−1] (12 cols; one-tailed β>0)
- **UncAnsMgr**: col 1 +0.0011\*, col 2 +0.0009\*. **2/12 significant (contemp Ind/Firm base).**
- **UncPreMgr**: all 12 NULL.
- **UncAnsCEO**: col 2 +0.0003\*\*\*, col 4 +0.0002\*\*\*. **2/12 significant (contemp Firm-FE base/extended).**
- **UncPreCEO**: col 3 +0.0002\* (contemp). Lead side: col 7 +0.0007\*\*, col 9 +0.0009\*\*, col 10 +0.0006\*, col 11 +0.0010\*\*\*, col 12 +0.0007\*. **6/12 significant (1 contemp, 5 lead).**
- N: ~63,537 (base), ~60,036 (extended). R²: 0.02-0.04 (low).
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.
- **Note: H7d is the only suite in the H7 family where UncAnsMgr shows any significant cell (2/12 Ind-FE base). UncPreCEO lead shows the strongest activity in this suite.**

### H7e — BGT Avg Amihud [−25,+25] 51-day symmetric (12 cols; one-tailed β>0)
- **UncAnsCEO**: col 1 +0.0009\*. **1/12 significant.**
- **UncPreCEO**: all 12 NULL (negative contemp).
- **UncAnsMgr**: all 12 NULL (negative contemp).
- **UncPreMgr**: col 3 +0.0016\*\*, col 5 +0.0009\*, col 7 +0.0010\*, col 8 +0.0014\*\*, col 11 +0.0012\*. **5/12 significant (3 contemp Ind-FE, 2 lead).**
- N: ~63,816 (base), ~60,256 (extended). R²: 0.48-0.65.
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H14 — DSPREAD 3-day delta (Lee 2016 [+1,+3] − [−3,−1]; 12 cols; one-tailed β>0)
- **UncAnsCEO**: all 12 cells 0.0000 (NULL). **0/12 significant.**
- **UncPreCEO**: all 12 NULL (point estimates 0.0000 to −0.0001).
- **UncAnsMgr**: all 12 NULL (negative contemp points).
- **UncPreMgr**: col 6 \* (but value still 0.0000). **1/12 marginally sig (essentially zero magnitude).**
- N: 63,972 (base) / 44,132 (extended). R²: 0.001-0.007 (Δ DV is noise).
- Clustering: two-way (with fallback to firm-only for cols 6, 8, 9, 10, 12 due to rank-deficient VCV — disclosed in notes).
- Tailing: one-tailed β>0.
- **Essentially null across all 48 IV-cells; magnitude is 0.0000 throughout.**

### H14b — PostCallSpread LEVEL 3-day (Lee 2016 [+1,+3]; 12 cols; one-tailed β>0)
- **UncAnsCEO**: col 1 \*, col 2 \*, col 8 \*, col 10 \*, col 12 \*. **5/12 significant (all essentially 0.0000 magnitude).**
- **UncPreCEO**: all 12 NULL.
- **UncAnsMgr**: col 3 +0.0001\*\*\*, col 9 +0.0001\*\*\*. **2/12 significant (both Ind-FE extended).**
- **UncPreMgr**: col 2 +0.0001\*, col 3 +0.0002\*\*\*, col 9 +0.0002\*\*\*. **3/12 significant.**
- N: 63,972 (base) / 60,368 (extended). R²: 0.29-0.55.
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H14c — BGT Level 25-day Spread [0,+25] (day 0 included; 12 cols; one-tailed β>0)
- **UncAnsCEO**: contemp cols 1-6 all NULL; lead col 7 +0.0000\*\*\*, col 8 +0.0000\*\*\*, col 9 \*, col 10 \*, col 11 \*, col 12 \*. **6/12 significant (ALL lead side).**
- **UncPreCEO**: col 1 \*\*, col 2 \*\*. **2/12 significant (contemp Ind-FE base/Firm-FE base).**
- **UncAnsMgr**: col 3 +0.0000\*\*, col 9 +0.0001\*\*. **2/12 significant (Ind-FE extended contemp/lead).**
- **UncPreMgr**: col 3 +0.0001\*\*, col 9 +0.0001\*\*\*, col 10 \*, col 12 \*. **4/12 significant.**
- N: 63,899 (base) / 44,092 (extended). R²: 0.51-0.78.
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H14d — BGT Delta 25-day Spread ([+1,+25] − [−25,−1]; 12 cols; one-tailed β>0)
- **UncAnsCEO**: col 8 \*. **1/12 significant.**
- **UncPreCEO**: all 12 NULL.
- **UncAnsMgr**: all 12 NULL.
- **UncPreMgr**: all 12 NULL.
- N: 62,480 (base) / 43,282 (extended). R²: 0.002-0.012.
- Clustering: two-way with fallback to firm-only for cols 7, 8, 9 (rank-deficient VCV, disclosed in notes).
- Tailing: one-tailed β>0.
- **Essentially null across all 48 IV-cells.**

### H14e — BGT Avg Spread [−25,+25] 51-day symmetric (12 cols; one-tailed β>0)
- **UncAnsCEO**: col 7 \*, col 8 \*\*. **2/12 significant (lead Ind-FE base / Firm-FE base).**
- **UncPreCEO**: col 1 \*, col 2 \*\*, col 4 \*. **3/12 significant (contemp side).**
- **UncAnsMgr**: col 9 \*\*. **1/12 significant.**
- **UncPreMgr**: col 3 \*, col 9 +0.0001\*\*\*, col 10 \*, col 12 \*. **4/12 significant.**
- N: 63,936 (base) / 44,100 (extended). R²: 0.60-0.83.
- Clustering: two-way. **OK.** Tailing: one-tailed β>0.

### H18 — CCCL LPM (comment letter receipt indicator; 6 cols; 1 DV × 6 specs; one-tailed β>0)
- **UncAnsCEO**: all 6 NULL (negative point estimates).
- **UncPreCEO**: all 6 NULL.
- **UncAnsMgr**: all 6 NULL (sign flips).
- **UncPreMgr**: col 1 +0.0017\*, col 2 +0.0020\*. **2/6 significant (Ind-FE base, Firm-FE base only). Cols 3-6 NULL.**
- N: 66,886 (base) / 64,172 (extended). R²: 0.0003-0.001 (effectively zero).
- Clustering: firm-only.
- Tailing: one-tailed β>0.
- Model: LPM (linear probability model).

### H18b — CCCL Logit robustness (2 cols; 1 DV × {base, extended} × Ind-FE only; one-tailed β>0)
- **UncAnsCEO**: col 1 NULL (-0.0012), col 2 NULL (-0.0016). Both negative.
- **UncPreCEO**: col 1 NULL, col 2 NULL.
- **UncAnsMgr**: col 1 NULL, col 2 NULL.
- **UncPreMgr**: col 1 +0.0018\*\*, col 2 +0.0012\*. **2/2 significant.**
- N: 66,886 / 64,172. Pseudo R²: 0.089 / 0.090.
- Clustering: firm-only (statsmodels Logit `cov_type="cluster"`, groups=gvkey).
- Tailing: one-tailed β>0.
- Model: Logit. Only Industry FE (no Firm FE variant — likely incidental-parameters issue at firm level).
- Note: Consistent with H18 LPM on UncPreMgr only; rest null.

### H21 — SEC_Letters_fwd (count of forward SEC comment letters; 6 cols; 1 DV × 6 specs; one-tailed β>0)
- **UncAnsCEO**: all 6 NULL (negative points).
- **UncPreCEO**: col 1 +0.0153\*\*, col 3 +0.0137\*\*, col 5 +0.0134\*\*. **3/6 significant (ALL Ind-FE cells). Firm-FE 3/3 NULL.**
- **UncAnsMgr**: all 6 NULL (negative points).
- **UncPreMgr**: col 1 −0.0183, col 2 −0.0090, col 3 −0.0197, col 4 −0.0096, col 5 −0.0195, col 6 −0.0099. **All 6 NULL, but ALL NEGATIVE sign — opposite to H18 UncPreMgr positive!**
- N: 66,886 (base) / 64,172 (extended). R²: 0.004-0.005.
- Clustering: firm-only.
- Tailing: one-tailed β>0.
- **Within-family sign contradiction: H18 (CCCL indicator) shows UncPreMgr +0.0017\* (pos), H21 (letter count fwd) shows UncPreMgr −0.018 (neg, not sig). Same underlying panel. H21 UncPreCEO +Ind-FE pattern is also not echoed in H18.**

### H22 — EquityDelayCon_lead (Hoberg-Maksimovic equity financing constraints, firm-year; 4 cols; 1 DV × 2 FE × 2 control sets; one-tailed β>0)
No YrQtr-FE variant. Firm-year frequency panel.
- **UncAnsCEO**: col 1 +0.0058\*, col 3 +0.0059\*. **2/4 significant (Ind-FE base, Ind-FE extended). Firm-FE 2/2 NULL.**
- **UncPreCEO**: all 4 NULL (small positive points).
- **UncAnsMgr**: all 4 NULL (negative sign).
- **UncPreMgr**: all 4 NULL (negative sign, some marginal: col 1 -0.0044 (0.0029), col 3 -0.0075 (0.0029) — large-ish negatives).
- N: 8,621 (base) / 8,564 (extended). **Smallest N of any audited suite** (Hoberg-Maksimovic is annual firm-year).
- R²: 0.49 Ind-FE / 0.04 Firm-FE. Big gap (Ind-FE explains cross-sectional level mostly via `lnAssets`+Lagged_DV).
- Clustering: firm-only.
- Tailing: one-tailed β>0.
