# F1D Econometric Pipeline — Master Refactor Plan

**Last updated:** 2026-02-20  
**Status:** Phase A complete. B.1 complete. H1 Cash Holdings complete (call-level, all red-team audit fixes applied, re-verified 2026-02-20). B.2–B.6 planned.

---

## Context and Architecture

The pipeline rewrites all old v1/v2 econometric scripts into a modern shared-variable-builder architecture. Every hypothesis test follows a two-stage pattern:

- **Stage 3** — Panel builder (`src/f1d/variables/build_<name>_panel.py`): loads the manifest + shared variable builders + merges into one parquet panel
- **Stage 4** — Hypothesis test (`src/f1d/econometric/test_<name>.py`): loads the panel, filters, runs OLS with fixed effects, extracts scores, outputs LaTeX + parquet

Shared infrastructure lives in:

```
src/f1d/shared/
  variables/          # One module per variable (base.py + named builders)
  config/             # get_config(), load_variable_config()
  latex_tables_accounting.py
  path_utils.py       # get_latest_output_dir()
  industry_utils.py   # parse_ff_industries() — FF12/FF48 mapping
  regression_helpers.py
config/variables.yaml # Central variable source configuration
```

### Canonical pattern — Manager Clarity as reference

`build_manager_clarity_panel.py` + `test_manager_clarity.py` are the gold-standard
implementation. All new scripts must match their structure, including:

- Explicit config path passed to `get_config()` and `load_variable_config()`
- Duplicate-row assertion before every merge (`ValueError` on fan-out)
- Column-conflict drop before every merge (gvkey, year, start_date)
- Reference entity excluded from `clarity_scores.parquet` (`is_reference` column)
- Global standardization of clarity scores across all samples (not per-sample)
- Metadata join (`ceo_name`, `n_calls`) into output parquet
- `entity_label` param passed to `make_accounting_table()`
- Full formula logged (no `[:80]` truncation)

### Architecture correction (2026-02-19)

Financial variable builders must **compute from raw inputs**, not read Stage 3 outputs.

**Correct architecture:**
- `CompustatControlsBuilder` (`compustat_controls.py`) — reads `inputs/comp_na_daily_all/`
  directly, computes Size, BM, Lev, ROA, CurrentRatio, RD_Intensity, EPS_Growth
- `CRSPReturnsBuilder` (`crsp_returns.py`) — reads `inputs/CRSP_DSF/` directly,
  computes StockRet, MarketRet, Volatility
- `EarningsSurpriseBuilder` (`earnings_surprise.py`) — reads `inputs/tr_ibes/` + CCM
  directly, computes SurpDec
- Single-column wrappers (EPSGrowthBuilder, StockReturnBuilder, MarketReturnBuilder)
  delegate to the above engines; they exist for backward API compatibility

**Panel builders call compute engines once each** (not individual thin-reader
wrappers) so Compustat and CRSP are each loaded only once per panel build.

**Exception:** Textual/linguistic variables continue reading from Stage 2 outputs
(`outputs/2_Textual_Analysis/2.2_Variables/`) — this is correct and unchanged.

---

## Bugs fixed across sessions (do NOT re-introduce)

| ID | Bug | Fix location |
|----|-----|-------------|
| FIX-1 | Column conflict on merge (`_x`/`_y` suffix blowup) | Both panel builders |
| FIX-2 | `get_config()` CWD-relative path fragility | Both panel builders |
| FIX-3 | Per-sample standardization of clarity scores | Both test scripts |
| FIX-4 | LaTeX "N Managers" hardcoded for CEO tables | `latex_tables_accounting.py` |
| FIX-5 | No duplicate detection before merge | Both panel builders |
| FIX-6 | Reference entity (gamma=0 artifact) in output parquet | Both test scripts |
| FIX-7 | Dead `hypothesis_tests:` section in `variables.yaml` | `config/variables.yaml` |
| FIX-8 | Formula log truncated at `[:80]` | Both test scripts |
| FIX-9 (reverted) | NaN `ff12_code` filter in regression prep — was wrong; real fix is FIX-10 | Both test scripts |
| FIX-10 | `parse_ff_industries()` missing FF12 catch-all (code 12 "Other") | `industry_utils.py`, `link_entities.py` |

---

## Completed work

### Phase A — Clarity score estimation (4.1, 4.1.1)

| Script | New location | Status | Notes |
|--------|-------------|--------|-------|
| `4.1_EstimateManagerClarity.py` | `build_manager_clarity_panel.py` + `test_manager_clarity.py` | ✅ Done | Pilot; all 10 audit fixes applied |
| `4.1.1_EstimateCeoClarity.py` | `build_ceo_clarity_panel.py` + `test_ceo_clarity.py` | ✅ Done | Mirrors Manager Clarity pattern |

**Verified output (post FF12 fix, post architecture correction):**

| Script | Main | Finance | Utility | Entities |
|--------|------|---------|---------|---------|
| Manager Clarity | 56,480 obs | — | — | 3,218 managers |
| CEO Clarity | 41,403 obs | — | — | 2,428 CEOs |

### Phase B.1 — Extended Controls Robustness (4.1.2)

| Script | New location | Status | Notes |
|--------|-------------|--------|-------|
| `4.1.2_EstimateCeoClarity_Extended.py` | `build_ceo_clarity_extended_panel.py` + `test_ceo_clarity_extended.py` | ✅ Done | 4 models; Main sample only |

**Verified output:**

| Model | N Obs | N Entities | R² | R² Extended |
|-------|-------|-----------|-----|-------------|
| Manager Baseline | 56,480 | 2,539 | 0.408 | — |
| Manager Extended | 55,166 | 2,492 | — | 0.410 |
| CEO Baseline | 41,403 | 1,976 | 0.345 | — |
| CEO Extended | 40,376 | 1,940 | — | 0.346 |

R² increases only marginally (+0.002) confirming CEO fixed effects are robust to extended controls.

---

## Phase B — Remaining v1 scripts (planned)

The following scripts remain to be refactored, in priority order.

### B.1 — CEO Clarity Extended Controls (4.1.2) ✅ DONE

**v1 source:** `src/f1d/econometric/v1/4.1.2_EstimateCeoClarity_Extended.py`

**Purpose:** Robustness check. Runs 4 regressions:
1. Manager baseline (same as 4.1 Main)
2. Manager extended (+`CurrentRatio`, `RD_Intensity`, `Volatility`)
3. CEO-only baseline (same as 4.1.1 Main)
4. CEO-only extended (+`CurrentRatio`, `RD_Intensity`, `Volatility`)

**New files to create:**
- `src/f1d/shared/variables/current_ratio.py` — `CurrentRatioBuilder`
- `src/f1d/shared/variables/rd_intensity.py` — `RDIntensityBuilder`
- `src/f1d/shared/variables/volatility.py` — `VolatilityBuilder`
- `src/f1d/variables/build_ceo_clarity_extended_panel.py` — Stage 3
- `src/f1d/econometric/test_ceo_clarity_extended.py` — Stage 4

**Variables needed (in addition to 4.1.1 variables):**
- `CurrentRatio` — from `firm_controls_{year}.parquet`
- `RD_Intensity` — from `firm_controls_{year}.parquet`
- `Volatility` — from `market_variables_{year}.parquet` (rolling std of returns)

**New `variables.yaml` entries:**
```yaml
current_ratio:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "firm_controls_{year}.parquet"
  column: "CurrentRatio"

rd_intensity:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "firm_controls_{year}.parquet"
  column: "RD_Intensity"

volatility:
  stage: 3
  source: "outputs/3_Financial_Features"
  file_pattern: "market_variables_{year}.parquet"
  column: "Volatility"
```

**LaTeX output:** Single table with 4 columns (Manager Baseline, Manager Extended, CEO Baseline, CEO Extended) for the Main sample only (robustness check).

**Key implementation note:** The 4 regressions share the same panel. Build one panel with all 12 variables (base + extended), then run 4 separate regressions against it. Do not build 4 separate panels.

---

### B.2 — CEO Clarity Regime Analysis (4.1.3)

**v1 source:** `src/f1d/econometric/v1/4.1.3_EstimateCeoClarity_Regime.py`

**Purpose:** Split-sample analysis by time regime. Runs CEO Clarity (4.1.1) separately for:
- Pre-crisis regime: 2002–2007
- Crisis regime: 2008–2009
- Post-crisis regime: 2010–2018

Tests whether the Clarity trait is stable across economic regimes or shifts with market stress.

**New files to create:**
- `src/f1d/econometric/test_ceo_clarity_regime.py` — Stage 4 only (reuses CEO Clarity panel from 4.1.1)

**No new Stage 3 panel needed** — loads the same `ceo_clarity_panel.parquet` from `build_ceo_clarity_panel.py`. Applies year filter inside Stage 4.

**LaTeX output:** 3-column table (Pre-Crisis, Crisis, Post-Crisis), Main sample only.

**Key implementation note:** The regime split is a filter on `year`, not a separate variable set. Reuse the Stage 3 panel from 4.1.1 directly.

---

### B.3 — CEO Tone (4.1.4)

**v1 source:** `src/f1d/econometric/v1/4.1.4_EstimateCeoTone.py`

**Purpose:** Estimate CEO "Tone" (Net Sentiment = Positive pct − Negative pct) as a persistent communication trait. Runs 3 models per industry sample:
- `ToneAll`: CEO FE on all-manager speech net sentiment
- `ToneCEO`: CEO FE on CEO-only speech net sentiment
- `ToneRegime`: CEO FE on non-CEO manager speech net sentiment

**New variables needed:**
- `CEO_Pres_NetSentiment_pct` — CEO positive minus negative in presentation
- `CEO_QA_NetSentiment_pct` — CEO positive minus negative in Q&A
- `Manager_Pres_NetSentiment_pct` — All-manager net sentiment in presentation
- `Entire_All_Positive_pct` — already in linguistic variables (check column name)
- `Entire_All_Negative_pct` — already loaded in 4.1

**New files to create:**
- `src/f1d/shared/variables/ceo_pres_net_sentiment.py`
- `src/f1d/shared/variables/ceo_qa_net_sentiment.py`
- `src/f1d/shared/variables/manager_pres_net_sentiment.py`
- `src/f1d/variables/build_ceo_tone_panel.py` — Stage 3
- `src/f1d/econometric/test_ceo_tone.py` — Stage 4

**Output:** `tone_scores.parquet` with `ToneCEO` scores. LaTeX table with 3 model columns × 3 samples.

---

### B.4 — Liquidity Regressions (4.2)

**v1 source:** `src/f1d/econometric/v1/4.2_LiquidityRegressions.py`

**Purpose:** Test whether CEO communication affects market liquidity around earnings calls using IV regression (2SLS). Uses CCCL `shift_intensity_sale_ff48` as instrument for time-varying Q&A uncertainty.

**Structure:**
- Phase 1: First stage — instrument validity (Q&A Uncertainty ~ CCCL)
- Phase 2: OLS (unadjusted)
- Phase 3: 2SLS (Q&A Uncertainty instrumented by CCCL)

**Inputs from prior stages (clarity scores already estimated):**
- `outputs/econometric/manager_clarity/latest/clarity_scores.parquet` — `ClarityManager`
- `outputs/econometric/ceo_clarity/latest/clarity_scores.parquet` — `ClarityCEO`

**New variables needed:**
- `shift_intensity_sale_ff48` — CCCL instrument (from `inputs/CCCL_instrument/`)
- `Amihud_Illiq` — Amihud illiquidity ratio (from `market_variables_{year}.parquet`)
- `BidAsk_Spread` — bid-ask spread (from `market_variables_{year}.parquet`)
- `TurnoverRatio` — from `market_variables_{year}.parquet`

**New files to create:**
- `src/f1d/shared/variables/cccl_instrument.py` — `CCCLInstrumentBuilder`
- `src/f1d/shared/variables/amihud_illiquidity.py`
- `src/f1d/variables/build_liquidity_panel.py` — Stage 3
- `src/f1d/econometric/test_liquidity.py` — Stage 4 (OLS + 2SLS)

**Key implementation note:** 2SLS requires `linearmodels` (`pip install linearmodels`). The CCCL instrument is precomputed at FF48×year level and must be merged on `(ff48_code, year)`, not `file_name`. Verify CCCL input path from `config/project.yaml`.

---

### B.5 — Takeover Hazards (4.3)

**v1 source:** `src/f1d/econometric/v1/4.3_TakeoverHazards.py`

**Purpose:** Test whether CEO Clarity and Q&A Uncertainty predict takeover probability using survival analysis.

**Models:**
- Model 1: Cox Proportional Hazards (all takeovers)
- Model 2: Fine-Gray Competing Risks (hostile/unsolicited)
- Model 3: Fine-Gray Competing Risks (friendly)

**Inputs from prior stages:**
- `clarity_scores.parquet` from 4.1 (Manager) and 4.1.1 (CEO)
- SDC M&A data: `inputs/SDC/sdc-ma-merged.parquet`
- Firm controls

**New files to create:**
- `src/f1d/shared/variables/takeover_indicator.py` — merge SDC data
- `src/f1d/variables/build_takeover_panel.py` — Stage 3
- `src/f1d/econometric/test_takeover_hazards.py` — Stage 4 (survival models)

**Key implementation note:** Survival analysis requires `lifelines` (`pip install lifelines`). The SDC data is a firm-year dataset, not call-level. The panel must be aggregated to firm-year before survival analysis.

---

### B.6 — Summary Statistics (4.4)

**v1 source:** `src/f1d/econometric/v1/4.4_GenerateSummaryStats.py`

**Purpose:** Generate final publication-quality summary statistics table across all variables used in the thesis.

**New files to create:**
- `src/f1d/econometric/generate_summary_stats.py`

**Key implementation note:** This depends on all prior stages being complete. Should be run last. Output is a single LaTeX `tabular` with panel A (linguistic variables) and panel B (financial controls).

---

## Implementation order

Run phases in this order — each phase depends on clarity scores from the previous:

```
Phase A (done):
  4.1  Manager Clarity    → clarity_scores.parquet (Manager)
  4.1.1 CEO Clarity       → clarity_scores.parquet (CEO)

Phase B (next):
  B.1  4.1.2 Extended Controls  (robustness; uses same panel inputs)
  B.2  4.1.3 Regime Analysis    (robustness; reuses CEO Clarity panel)
  B.3  4.1.4 CEO Tone           (new variable set; separate panel)
  B.4  4.2   Liquidity          (uses clarity scores from A; adds CCCL + IV)
  B.5  4.3   Takeover Hazards   (uses clarity scores from A; adds SDC data)
  B.6  4.4   Summary Statistics (runs last; depends on all prior outputs)
```

---

## Next immediate task: B.2 — CEO Clarity Regime Analysis (4.1.3)

### Pre-flight checks (run before starting)

```bash
# 1. Verify extended control columns exist in firm_controls parquet
python -c "
import pandas as pd
from pathlib import Path
from f1d.shared.path_utils import get_latest_output_dir
root = Path('.')
fc_dir = get_latest_output_dir(root / 'outputs' / '3_Financial_Features',
                               required_file='market_variables_2010.parquet')
fc = pd.read_parquet(fc_dir / 'firm_controls_2010.parquet')
mv = pd.read_parquet(fc_dir / 'market_variables_2010.parquet')
print('firm_controls columns:', list(fc.columns))
print('market_variables columns:', list(mv.columns))
"

# 2. Confirm column names for CurrentRatio, RD_Intensity, Volatility
```

### Task B.1.1 — Pre-flight: identify exact column names

Before writing any code, run the pre-flight check above and confirm:
- Exact column name for current ratio in `firm_controls_{year}.parquet`
- Exact column name for R&D intensity
- Exact column name for volatility (rolling return std)

If columns are missing from financial features, the v2 financial scripts (`src/f1d/financial/v2/`) may need to be run first to compute them.

### Task B.1.2 — Create extended variable builders

Create 3 new builders in `src/f1d/shared/variables/`:
- `current_ratio.py` — `CurrentRatioBuilder`
- `rd_intensity.py` — `RDIntensityBuilder`
- `volatility.py` — `VolatilityBuilder`

Pattern: copy `eps_growth.py` as template (same source, same structure, only column name differs).

Register all 3 in `src/f1d/shared/variables/__init__.py`.

Add entries to `config/variables.yaml`.

### Task B.1.3 — Build extended panel

Create `src/f1d/variables/build_ceo_clarity_extended_panel.py`.

Loads all 12 variables (base 9 from 4.1.1 + 3 extended). Saves single panel used by all 4 regressions.

### Task B.1.4 — Build Stage 4 test

Create `src/f1d/econometric/test_ceo_clarity_extended.py`.

Runs 4 regressions against the same panel:
1. Manager baseline: `Manager_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + C(year)`
2. Manager extended: same + `CurrentRatio + RD_Intensity + Volatility`
3. CEO baseline: `CEO_QA_Uncertainty_pct ~ C(ceo_id) + base_controls + C(year)`
4. CEO extended: same + `CurrentRatio + RD_Intensity + Volatility`

LaTeX output: 4-column table. Use `entity_label="N Managers/CEOs"` as appropriate per column.

### Task B.1.5 — Run and verify

```bash
python -m f1d.variables.build_ceo_clarity_extended_panel
python -m f1d.econometric.test_ceo_clarity_extended
```

Check that observation counts for baseline models match 4.1 and 4.1.1 exactly (same filter chain). Extended models will have fewer obs due to additional missingness in `CurrentRatio`, `RD_Intensity`, `Volatility`.

### Task B.1.6 — Commit

```bash
git add src/f1d/shared/variables/current_ratio.py \
        src/f1d/shared/variables/rd_intensity.py \
        src/f1d/shared/variables/volatility.py \
        src/f1d/shared/variables/__init__.py \
        src/f1d/variables/build_ceo_clarity_extended_panel.py \
        src/f1d/econometric/test_ceo_clarity_extended.py \
        config/variables.yaml
git commit -m "feat: implement 4.1.2 CEO Clarity Extended Controls robustness"
```

---

## Checklist for each new script pair

Before marking any script pair done, verify all of the following:

- [ ] Stage 3 panel: zero delta on every variable merge (no row fan-out)
- [ ] Stage 3 panel: zero NaN in `ff12_code` (upstream fix guarantees this)
- [ ] Stage 3 panel: sample counts match expected (Main >> Finance > Utility)
- [ ] Stage 4 test: complete-cases count is reasonable (check per-variable missingness)
- [ ] Stage 4 test: reference entity excluded from output parquet
- [ ] Stage 4 test: global standardization log printed (mean, std, N entities)
- [ ] Stage 4 test: LaTeX entity label is correct for the test
- [ ] Stage 4 test: full formula printed (no truncation)
- [ ] Config path: explicit root-relative path passed to `get_config()`
- [ ] No type errors (run `pyright src/f1d/econometric/test_<name>.py`)
- [ ] Committed to git

---

## Key file locations

| Purpose | Path |
|---------|------|
| Manifest (Stage 1 output) | `outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet` |
| Linguistic variables (Stage 2) | `outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet` |
| Financial features (Stage 3) | `outputs/3_Financial_Features/latest/firm_controls_{year}.parquet` |
| Market variables (Stage 3) | `outputs/3_Financial_Features/latest/market_variables_{year}.parquet` |
| Manager clarity scores | `outputs/econometric/manager_clarity/latest/clarity_scores.parquet` |
| CEO clarity scores | `outputs/econometric/ceo_clarity/latest/clarity_scores.parquet` |
| CCCL instrument | `inputs/CCCL_instrument/` (check exact path in `config/project.yaml`) |
| SDC M&A data | `inputs/SDC/sdc-ma-merged.parquet` |
| FF12 classification | `inputs/FF1248/Siccodes12.zip` |
| FF48 classification | `inputs/FF1248/Siccodes48.zip` |

---

---

## H1 — Cash Holdings Regression (v2 hypothesis)

**Status:** COMPLETE (2026-02-20, post red-team audit + all fixes applied)

**Hypothesis:**
- H1a: beta1 > 0 — Higher speech uncertainty -> more cash hoarding (precautionary motive)
- H1b: beta3 < 0 — Leverage attenuates uncertainty-cash relationship (debt discipline)

**Model:** `CashHoldings_{t+1} = b0 + b1*Unc_c + b2*Lev_c + b3*(Unc_c x Lev_c) + g*Controls + Firm FE + Year FE + e`

### Files created

| File | Purpose |
|------|---------|
| `src/f1d/shared/variables/cash_holdings.py` | `CashHoldingsBuilder` -> `CashHoldings` (cheq/atq from Compustat) |
| `src/f1d/shared/variables/tobins_q.py` | `TobinsQBuilder` -> `TobinsQ` ((atq+cshoq*prccq-ceqq)/atq) |
| `src/f1d/shared/variables/capex_intensity.py` | `CapexIntensityBuilder` -> `CapexAt` (capxy/atq) |
| `src/f1d/shared/variables/dividend_payer.py` | `DividendPayerBuilder` -> `DividendPayer` (binary, dvy>0) |
| `src/f1d/shared/variables/ocf_volatility.py` | `OCFVolatilityBuilder` -> `OCF_Volatility` (rolling 5yr std, min 3, oancfy/atq) |
| `src/f1d/shared/variables/manager_qa_weak_modal.py` | 6th uncertainty measure |
| `src/f1d/shared/variables/ceo_qa_weak_modal.py` | 6th uncertainty measure |
| `src/f1d/shared/variables/manager_pres_weak_modal.py` | 6th uncertainty measure |
| `src/f1d/shared/variables/ceo_pres_weak_modal.py` | 6th uncertainty measure |
| `src/f1d/variables/build_h1_cash_holdings_panel.py` | Stage 3: call-level -> firm-year, creates CashHoldings_lead |
| `src/f1d/econometric/test_h1_cash_holdings.py` | Stage 4: 72 regressions (6 measures x 4 specs x 3 samples), LaTeX |

### Engine extensions (purely additive to `_compustat_engine.py`)

Added Compustat columns: `cheq`, `capxy`, `dvy`, `oancfy`, `cshoq`, `prccq`, `ceqq`, `fyearq`

Added computed variables: `CashHoldings`, `TobinsQ`, `CapexAt`, `DividendPayer`, `OCF_Volatility`

Bugs fixed during implementation and variable-formula audit:
- `capxq` does NOT exist in `comp_na_daily_all.parquet` -> use `capxy` (annual CapEx)
- `_compute_ocf_volatility()` forgot to include `datadate` in slice before sorting by it
- **TobinsQ formula**: was `(mkvaltq+ltq)/atq` (`mkvaltq` has 41% missing rate);
  fixed to `(atq+cshoq*prccq-ceqq)/atq` (only 0.9% missing, r=0.9999 correlation). Recovered +4,223 obs.
- **DividendPayer**: was `dvpq>0` (preferred dividends, quarterly — wrong variable, only 9.7% payers);
  fixed to `dvy>0` (annual common dividends, ~45% payers). `dvpq` removed from engine.
- **OCF_Volatility window**: was 4-year rolling, min 2 obs; fixed to 5-year rolling, min 3 obs (matches v2 design)

### Verified output (UPDATED 2026-02-20: post red-team audit, all fixes applied)

**Red-team audit fixes applied before final run:**
- CRITICAL-1: CapexAt now uses Q4-only `capxy` joined by `gvkey+fyearq` (was raw cumulative YTD)
- CRITICAL-2: DividendPayer now uses Q4-only `dvy` joined by `gvkey+fyearq` (same fix)
- CRITICAL-3: variables.yaml corrected (TobinsQ, DividendPayer, CapexAt, OCF_Volatility formulas)
- CRITICAL-4: `sys.stdout.reconfigure()` guarded with `hasattr` check
- CRITICAL-5: CashHoldings_lead now uses end-of-year proxy (last call per firm-year, not mean)
- MAJOR-1: Firm-clustered SEs (`cov_type="cluster"`) replacing HC1 (Moulton problem fix)
- MAJOR-2: Global mean-centering dropped; raw Uncertainty and Lev; interaction = Uncertainty * Lev
- MAJOR-9: Year-gap validation in lead construction (gap-year leads set to NaN)
- GAP-5: CashHoldings (contemporaneous) removed from control variables
- GAP-7: Custom `_save_latex_table()` replaces `make_accounting_table()` for H1 output
- MINOR-2: capex_intensity.py metadata string corrected to `"Compustat/capxy_Q4/atq"`
- MINOR-4: regression meta returned as plain dict (not attached as model attribute)

**Stage 3** (112,968 call-level rows — identical to manager_clarity, ceo_clarity, ceo_tone):

| Sample | Total calls | Calls with valid lead |
|--------|------------|----------------------|
| Main | 88,205 | 80,722 |
| Finance | 20,482 | 18,635 |
| Utility | 4,281 | 3,948 |

- 9,663 calls without valid lead (last-year per firm: 2,495 firm-years; year-gaps: 261; no Compustat match: remainder)
- All 19 variable merges: zero row delta (confirmed)
- CashHoldings_lead = last call's CashHoldings per firm-year (closest to year-end); year-gap leads set to NaN

**Stage 4** (18 regressions — 6 measures x 3 samples, firm-clustered SEs):

| Sample | N calls (Manager QA) | N firms | N calls (CEO QA) | N firms | H1a | H1b |
|--------|----------------------|---------|------------------|---------|-----|-----|
| Main | 72,353 | 1,744 | 52,961 | 1,533 | 0/6 | 1/6 |
| Finance | 3,455 | 85 | 2,303 | 70 | 2/6 | 1/6 |
| Utility | 3,486 | 81 | 2,143 | 71 | 2/6 | 3/6 |

**Total: H1a 4/18 significant, H1b 4/18 significant (one-tailed p<0.05)**

Notable results (post-fix):
- Finance/Manager_QA_Uncertainty: b1=0.0433 (SE=0.0217), p_one=0.023 H1a=YES; b3=-0.0563 (SE=0.0315), p_one=0.037 H1b=YES
- Finance/CEO_QA_Uncertainty: b1=0.0339 (SE=0.0197), p_one=0.042 H1a=YES
- Utility/CEO_QA_Uncertainty: b1=0.0226 (SE=0.0101), p_one=0.013 H1a=YES; b3=-0.0306 (SE=0.0140), p_one=0.014 H1b=YES
- Utility/Manager_QA_Weak_Modal: b1=0.0514 (SE=0.0171), p_one=0.001 H1a=YES; b3=-0.0692 (SE=0.0236), p_one=0.002 H1b=YES
- Main sample: all null results (consistent with high firm-FE R² ~0.82 absorbing most variation)
- R-squared: Main ~0.82, Finance ~0.79, Utility ~0.68 (firm FE absorbs most firm-level cash variation)
- ValueWarning on rank-deficient cluster covariance for small Finance/Utility samples is benign (known statsmodels artefact; coefficients are correct)

### Design decisions (UPDATED 2026-02-20: post red-team audit)

- **Unit of observation**: individual earnings call (file_name) -- identical to manager_clarity, ceo_clarity, ceo_tone
- **CashHoldings_lead at call level**: end-of-year proxy = CashHoldings from the last call (latest start_date)
  per firm-year t+1, merged back to all calls in year t. Year-gap leads set to NaN (CRITICAL-5 + MAJOR-9 fix).
- **Regression engine**: `statsmodels OLS + firm-clustered SEs` (groups=gvkey). HC1 replaced due to Moulton problem:
  CashHoldings_lead is identical for all calls in the same firm-year, so HC1 over-counts independent observations.
- **Fixed effects**: `C(gvkey) + C(year)` firm and year dummies -- consistent with other tests
- **6 uncertainty measures**: Manager_QA_Uncertainty_pct, CEO_QA_Uncertainty_pct, Manager_QA_Weak_Modal_pct,
  CEO_QA_Weak_Modal_pct, Manager_Pres_Uncertainty_pct, CEO_Pres_Uncertainty_pct
- **Interaction term**: Uncertainty * Lev (raw, no pre-centering; firm FE absorbs within-firm means; MAJOR-2 fix)
- **18 total regressions**: 6 uncertainty measures x 3 samples
- **One-tailed tests**: H1a p1 = p2/2 if b1 > 0; H1b p1 = p2/2 if b3 < 0; else p1 = 1 - p2/2
- **DividendPayer**: binary, excluded from winsorization in engine; uses Q4-only dvy (CRITICAL-2 fix)
- **CapexAt**: uses Q4-only capxy / atq (CRITICAL-1 fix -- capxy is YTD cumulative, Q4 = full-year)
- **OCF_Volatility**: rolling 5-year std (min 3 obs) computed on annual panel (last obs per gvkey-fyearq), then joined back
- **Min calls filter**: >= 5 calls per firm (mirrors >= 5 calls per manager in other tests)
- **CashHoldings (contemporaneous)**: excluded from controls per v2 design (GAP-5 fix)

### Audit: N-count discrepancy investigation (CLOSED 2026-02-20)

**Question:** Why does H1 Main regression have N≈72,353 calls while manager_clarity has N≈57,796?

**Answer:** The H1 panel includes all calls with valid CashHoldings lead (6 uncertainty measures share the same
panel; Manager QA Uncertainty has the most complete cases because it has fewer NaNs than CEO-specific measures).
The manager_clarity panel is filtered to calls where a *manager* spoke (excluding CEO-only calls and analyst-only
calls), whereas H1 uses all calls for the firm. This is correct: H1 is a firm-level phenomenon measured at the
call level; it does not require a specific speaker.

**On 9,663 calls without valid lead:**
- 2,495 firm-years are the last year per firm (no year t+1 exists) → lead is NaN by design
- 261 firm-years have a year gap (firm missing year t+1 but present in t+2) → lead nulled (MAJOR-9 fix)
- Remainder: no Compustat match → CashHoldings always NaN → lead always NaN → dropped

**Conclusion:** No bug. All discrepancies are explained by correct design decisions.
The N=72,353 (Main/Manager_QA_Uncertainty) is correct and defensible.

---

## Archived: original 4.1.1 implementation plan

The detailed task-by-task implementation plan for the initial CEO Clarity (4.1.1)
refactor (Tasks 1–8 with full code listings) was recorded in the original plan file.
That work is now complete. This master plan supersedes it.

Key decisions from that session preserved here:
- CEO Clarity uses `CEO_QA_Uncertainty_pct` (not `Manager_QA_Uncertainty_pct`) as DV
- CEO Clarity uses `CEO_Pres_Uncertainty_pct` (not `Manager_Pres_Uncertainty_pct`) as speech control
- Entity fixed effects column in regression formula is still `C(ceo_id)` for both tests
  (the column `ceo_id` exists in the manifest for all managers, including CEOs)
- `ClarityCEO = -gamma_i` standardized globally; `ClarityManager = -gamma_i` standardized globally
- Both scripts deposit to separate output trees (`ceo_clarity/`, `manager_clarity/`)
