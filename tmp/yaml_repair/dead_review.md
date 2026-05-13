# Dead entry triage

Recommendations for the 50 entries in YAML but not in any current spec.
Manual review required before pruning.

| Column | YAML entry | Ref | Recommend | Reason |
|---|---|---|---|---|
| `Analyst_QA_Negative_pct` | `analyst_qa_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Analyst_QA_Positive_pct` | `analyst_qa_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `BTM` | `btm` | wang2020, lee2016 | **REVIEW** | Module src/f1d/shared/variables/bm.py still exports this column — may be archived suite or future use. |
| `CEO_Pres_Negative_pct` | `ceo_pres_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CEO_Pres_Positive_pct` | `ceo_pres_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CEO_Pres_Weak_Modal_pct` | `ceo_pres_weak_modal` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CEO_QA_Negative_pct` | `ceo_qa_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CEO_QA_Positive_pct` | `ceo_qa_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CEO_QA_Weak_Modal_pct` | `ceo_qa_weak_modal` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `CurrentRatio` | `current_ratio` | lr2010 | **REVIEW** | Module src/f1d/shared/variables/current_ratio.py still exports this column — may be archived suite or future use. |
| `DebtChoice` | `debt_choice` | lr2010 | **REVIEW** | Module src/f1d/shared/variables/_compustat_engine.py still exports this column — may be archived suite or future use. |
| `EPSgrowth` | `eps_growth` | — | **REVIEW** | Module src/f1d/shared/variables/eps_growth.py still exports this column — may be archived suite or future use. |
| `ExternalFunding` | `external_funding` | lr2010 | **REVIEW** | Module src/f1d/shared/variables/_compustat_engine.py still exports this column — may be archived suite or future use. |
| `FracInt` | `frac_int` | dwz2021 | **REVIEW** | Module src/f1d/shared/variables/intangibility.py still exports this column — may be archived suite or future use. |
| `ILLIQ` | `amihud_illiq` | — | **REVIEW** | Module src/f1d/shared/variables/amihud_illiq.py still exports this column — may be archived suite or future use. |
| `Manager_Pres_Negative_pct` | `manager_pres_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Manager_Pres_Positive_pct` | `manager_pres_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Manager_Pres_Weak_Modal_pct` | `manager_pres_weak_modal` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Manager_QA_Negative_pct` | `manager_qa_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Manager_QA_Positive_pct` | `manager_qa_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `Manager_QA_Weak_Modal_pct` | `manager_qa_weak_modal` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `MarketRet` | `market_return` | — | **REVIEW** | Module src/f1d/shared/variables/market_return.py still exports this column — may be archived suite or future use. |
| `NonCEO_Manager_QA_Negative_pct` | `nonceo_manager_qa_negative` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `NonCEO_Manager_QA_Positive_pct` | `nonceo_manager_qa_positive` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `StockRet` | `stock_return` | — | **REVIEW** | Module src/f1d/shared/variables/stock_return.py still exports this column — may be archived suite or future use. |
| `Takeover` | `takeover_indicator` | — | **REVIEW** | Module src/f1d/shared/variables/takeover_indicator.py still exports this column — may be archived suite or future use. |
| `Takeover_Attitude` | `takeover_indicator` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `Takeover_Date` | `takeover_indicator` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `Takeover_Type` | `takeover_indicator` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `UncAnsCFO` | `cfo_qa_uncertainty` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `UncAnsNoCEO` | `nonceo_manager_qa_uncertainty` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `UncCall` | `entire_all_uncertainty` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `UncPreCFO` | `cfo_pres_uncertainty` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `UncPreNoCEO` | `nonceo_manager_pres_uncertainty` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `UncResCEO` | `ceo_clarity_residual` | — | **DROP** | Legacy sentiment/modal pct column (replaced by NegCall/positive consolidations or unused). |
| `UncResMgr` | `manager_clarity_residual` | dwz2021 (thesis extension to all managers) | **DROP** | Not used by any current spec; no module exporting it. |
| `ceo_id` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `ceo_name` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `dAA` | `daa` | ff2001 | **REVIEW** | Module src/f1d/shared/variables/asset_growth.py still exports this column — may be archived suite or future use. |
| `dispersion` | `dispersion` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `dispersion_lead` | `dispersion_lead` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `earnings_surprise_ratio` | `earnings_surprise_ratio` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `equitydelaycon` | `equitydelaycon` | hm2015 | **DROP** | Not used by any current spec; no module exporting it. |
| `ff12_code` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `ff12_name` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `file_name` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `gvkey` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |
| `lagged_dispersion` | `lagged_dispersion` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `prior_dispersion` | `prior_dispersion` | — | **DROP** | Not used by any current spec; no module exporting it. |
| `start_date` | `manifest` | — | **KEEP** | Manifest identifier column, not a regression variable. |