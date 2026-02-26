# Variable Registry

Single source of truth for all econometric variables used in the Stage 3–4
pipeline. Every variable listed here is computed in exactly one Builder class
and one engine. No panel builder or econometric script recomputes formulas.

Generated: 2026-02-21  
Refactor status: canonical consolidation complete (see `panel_utils.py`).

---

## Shared Panel Helpers (`panel_utils.py`)

| Function | Purpose | Key design |
|---|---|---|
| `assign_industry_sample` | FF12 code → Finance / Utility / Main | `dtype=object` enforced; NaN → Main |
| `attach_fyearq` | call start_date → Compustat fyearq via merge_asof | explicit datetime coerce; file_name uniqueness guard; <50% match raises ValueError |

---

## Compustat Variables (`_compustat_engine.py` → `CompustatEngine`)

| Variable | Builder | Formula | Notes |
|---|---|---|---|
| `Size` | `SizeBuilder` | `ln(atq)` | |
| `BM` | `BMBuilder` | `ceqq / (cshoq * prccq)` | |
| `Lev` | `LevBuilder` | `(dlcq + dlttq) / atq` | FIX: Uses interest-bearing debt only (not total liabilities) |
| `ROA` | `ROABuilder` | `niq / atq` | |
| `CurrentRatio` | `CurrentRatioBuilder` | `actq / lctq` | Removed from H1 controls (~80% missing for FF12=11) |
| `RD_Intensity` | `RDIntensityBuilder` | `xrdq / atq` | |
| `EPS_Growth` | `EPSGrowthBuilder` | date-based YoY, robust to gaps | |
| `CashHoldings` | `CashHoldingsBuilder` | `cheq / atq` | |
| `TobinsQ` | `TobinsQBuilder` | `(atq + cshoq*prccq - ceqq) / atq` | |
| `CapexAt` | `CapexIntensityBuilder` | `capxy_Q4 / atq` | |
| `DividendPayer` | `DividendPayerBuilder` | `(dvy_Q4 > 0).astype(float)` | |
| `OCF_Volatility` | `OCFVolatilityBuilder` | rolling 5yr std (min 3) of `oancfy/atq_{t-1}` | FIX: Uses lagged assets per spec to avoid correlated measurement error |
| `CashFlow` | `CashFlowBuilder` | | |
| `SalesGrowth` | `SalesGrowthBuilder` | | |
| `InvestmentResidual` | `InvestmentResidualBuilder` | `INV_t ~ SG_{t-1}` | FF48-year OLS residual; >0=overinvestment |
| `DivStability` | `DivStabilityBuilder` | | |
| `IsDivPayer5yr` | `IsDivPayer5yrBuilder` | | |
| `PayoutFlexibility` | `PayoutFlexibilityBuilder` | | |
| `FCFGrowth` | `FCFGrowthBuilder` | | |
| `FirmMaturity` | `FirmMaturityBuilder` | | |
| `EarningsVolatility` | `EarningsVolatilityBuilder` | | |
| `LossDummy` | `LossDummyBuilder` | | |
| `PRiskFY` | `PRiskFYBuilder` | | |

---

## CRSP Variables (`_crsp_engine.py` → `CRSPEngine`)

| Variable | Builder | Formula | Notes |
|---|---|---|---|
| `StockRet` | `StockReturnBuilder` | compound return over call window | |
| `MarketRet` | `MarketReturnBuilder` | compound VWRETD over call window | |
| `Volatility` | `VolatilityBuilder` | annualized std over call window | |
| `AmihudIlliq` | `AmihudIlliqBuilder` | Amihud (2002) illiquidity ratio | |

---

## IBES Variables (`_ibes_engine.py` → `IBESEngine`)

| Variable | Builder | Formula | Notes |
|---|---|---|---|
| `SurpDec` | `EarningsSurpriseBuilder` | earnings surprise decile −5..+5 | |
| `EarningsSurpriseRatio` | `EarningsSurpriseRatioBuilder` | | |
| `DispersionLead` | `DispersionLeadBuilder` | | |
| `PriorDispersion` | `PriorDispersionBuilder` | | |

---

## Hassan/Textual Variables (`_hassan_engine.py` → Textual pipeline)

| Variable | Builder | Notes |
|---|---|---|
| `Manager_QA_Uncertainty_pct` | `ManagerQAUncertaintyBuilder` | |
| `Manager_Pres_Uncertainty_pct` | `ManagerPresUncertaintyBuilder` | |
| `CEO_QA_Uncertainty_pct` | `CEOQAUncertaintyBuilder` | |
| `CEO_Pres_Uncertainty_pct` | `CEOPresUncertaintyBuilder` | |
| `Manager_QA_Weak_Modal_pct` | `ManagerQAWeakModalBuilder` | |
| `CEO_QA_Weak_Modal_pct` | `CEOQAWeakModalBuilder` | |
| `Manager_Pres_Weak_Modal_pct` | `ManagerPresWeakModalBuilder` | |
| `CEO_Pres_Weak_Modal_pct` | `CEOPresWeakModalBuilder` | |
| `NonCEOMgr_QA_Uncertainty_pct` | `NonCEOManagerQAUncertaintyBuilder` | |
| `NonCEOMgr_Pres_Uncertainty_pct` | `NonCEOManagerPresUncertaintyBuilder` | |
| `CFO_QA_Uncertainty_pct` | `CFOQAUncertaintyBuilder` | |
| `Analyst_QA_Uncertainty_pct` | `AnalystQAUncertaintyBuilder` | |
| `NegativeSentiment` | `NegativeSentimentBuilder` | |
| `EntireAll_Uncertainty_pct` | `EntireAllUncertaintyBuilder` | |
| `Manager_QA_Positive_pct` | `ManagerQAPositiveBuilder` | |
| `Manager_QA_Negative_pct` | `ManagerQANegativeBuilder` | |
| `Manager_Pres_Positive_pct` | `ManagerPresPositiveBuilder` | |
| `Manager_Pres_Negative_pct` | `ManagerPresNegativeBuilder` | |
| `CEO_QA_Positive_pct` | `CEOQAPositiveBuilder` | |
| `CEO_QA_Negative_pct` | `CEOQANegativeBuilder` | |
| `CEO_Pres_Positive_pct` | `CEOPresPositiveBuilder` | |
| `CEO_Pres_Negative_pct` | `CEOPresNegativeBuilder` | |
| `NonCEOMgr_QA_Positive_pct` | `NonCEOManagerQAPositiveBuilder` | |
| `NonCEOMgr_QA_Negative_pct` | `NonCEOManagerQANegativeBuilder` | |
| `Analyst_QA_Positive_pct` | `AnalystQAPositiveBuilder` | |
| `Analyst_QA_Negative_pct` | `AnalystQANegativeBuilder` | |

---

## Other Builders

| Variable | Builder | Notes |
|---|---|---|
| `shift_intensity_sale_ff48` | `CCCLInstrumentBuilder` | CCCL IV (Hassan et al.) |
| `CEOClarityStyle` | `CEOClarityStyleBuilder` | CEO communication style |
| `CEOStyleRealtime` | `CEOStyleRealtimeBuilder` | Real-time style (H10) |
| `TakeoverIndicator` | `TakeoverIndicatorBuilder` | H9 takeover |

---

## Known Edge Cases / Registry Notes

- **Variable Audit Fixes (2026-02-25):**
  - `Lev`: Changed from `ltq/atq` (total liabilities) to `(dlcq+dlttq)/atq` (interest-bearing debt only) per spec. Prior implementation overstated leverage 2-3x for low-debt firms.
  - `OCF_Volatility`: Changed from `oancfy/atq` to `oancfy/atq_{t-1}` (lagged assets) per spec. Prior implementation introduced correlated measurement error.

- `Turn_Uncertainty_pct` in `build_h10_tone_at_top_panel.py`: uses `0.0`
  fallback (vs. `NaN` in all other uncertainty measures). Computed inline per
  speaker turn; not a `VariableBuilder`. Intentional design for Model 2.

- `run_h0_4_ceo_clarity_regime.py`: uses config-driven `isin` filter instead of
  `assign_industry_sample`. Intentional (regime-based sample, not FF12 split).

- `run_h8_political_risk.py`: uses `~isin([8, 11])` filter (excludes Finance and
  Utility from Main). Intentional structural difference.

- H9 (`build_h9_takeover_panel.py`): reads from
  `outputs/econometric/manager_clarity/` and `outputs/econometric/ceo_clarity/`.
  Must run after H0.1 and H0.2 (Stage 4 dependency).
