# Financial V1: Original Financial Variable Construction

> **Note:** This folder contains legacy V1 scripts kept for reference. The active versions have been migrated to `src/f1d/financial/v1/` as part of the v6.1 architecture standard. New development should use the `f1d.financial.*` namespace imports.

## Purpose and Scope

This folder contains the original financial variable construction scripts for v1.0 analyses. These scripts create firm-level control variables and market measures used in the first set of econometric analyses examining CEO communication clarity and financial outcomes.

**Version:** V1 (Stable - no longer modified)
**Status:** LEGACY - Migrated to src/f1d/financial/v1/
**Prerequisites:** Step 2 (Text Processing) outputs
**Outputs:** `4_Outputs/3_Financial/`

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `3.0_BuildFinancialFeatures.py` | Build financial features from Compustat | Cash flow, leverage, size, Tobin's Q, etc. |
| `3.1_FirmControls.py` | Calculate firm control variables | Firm controls (cash flow, leverage, size, Tobin's Q) |
| `3.2_MarketVariables.py` | Calculate market-based variables | Stock returns, volatility from CRSP |
| `3.3_EventFlags.py` | Create event study flags | Earnings announcement dates, event windows |
| `3.4_Utils.py` | Utility functions for financial calculations | Helper functions |

---

## Variable Construction

### Firm Controls (3.1_FirmControls.py)

Standard firm-level control variables from Compustat:

| Variable | Formula | Compustat Fields | Description |
|----------|---------|------------------|-------------|
| Size | log(AT) | AT | Natural log of total assets |
| Leverage | (DLTT + DLC) / AT | DLTT, DLC, AT | Total debt / Total assets |
| CashFlow | OANCF / AT | OANCF, AT | Operating cash flow / Total assets |
| TobinsQ | (AT + ME - CEQ) / AT | AT, ME, CEQ | Market-to-book ratio |
| ROA | IB / AT | IB, AT | Return on assets |
| Capex | CAPX / AT | CAPX, AT | Capital expenditure intensity |
| R&D | XRD / AT | XRD, AT | R&D expense intensity (0 if missing) |
| DividendPayer | 1 if DVC > 0 else 0 | DVC | Dividend payer indicator |

**Notes:**
- All ratios winsorized at 1st and 99th percentiles
- Missing R&D set to 0 (consistent with accounting treatment)
- Fiscal year alignment via datadate

### Market Variables (3.2_MarketVariables.py)

Stock market measures from CRSP daily data:

| Variable | Formula | CRSP Fields | Description |
|----------|---------|-------------|-------------|
| StockRet | Annual stock return | RET | Buy-and-hold return over fiscal year |
| Volatility | StdDev(daily RET) * sqrt(252) | RET | Annualized stock return volatility |
| MarketCap | PRC * SHROUT | PRC, SHROUT | Market capitalization |
| BM_Ratio | BookEquity / MarketCap | BE, ME | Book-to-market ratio |

**Notes:**
- Daily returns aggregated to fiscal year periods
- Minimum 50 trading days required for volatility calculation
- Returns calculated from fiscal year end to prior fiscal year end

### Event Flags (3.3_EventFlags.py)

Event study timing variables:

| Variable | Description |
|----------|-------------|
| EADate | Earnings announcement date |
| EAWindow | [-1, +1] trading day window around EA |
| PreEAPeriod | [-60, -2] trading days before EA |
| PostEAPeriod | [+2, +60] trading days after EA |

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| Compustat Annual | `1_Inputs/compustat/` | Fundamentals (AT, DLTT, OANCF, etc.) |
| CRSP Daily | `1_Inputs/crsp/` | Stock returns (RET, PRC, SHROUT) |
| Sample Manifest | `4_Outputs/1_Sample/` | GVKEY-fiscal year mapping |

### Outputs

```
4_Outputs/3_Financial/
├── firm_controls.parquet      # Firm-level controls from Compustat
├── market_variables.parquet   # Stock returns and volatility from CRSP
├── event_flags.parquet        # Earnings announcement timing
└── stats.json                 # Variable distributions and diagnostics
```

### Logs

```
3_Logs/3_Financial/
├── 3.0_BuildFinancialFeatures_*.log
├── 3.1_FirmControls_*.log
├── 3.2_MarketVariables_*.log
└── 3.3_EventFlags_*.log
```

---

## Sample Construction

**Sample Period:** 2002-2018
**Firms:** ~1,500 firms
**Observations:** ~12,000 firm-year observations

**Inclusion Criteria:**
- Non-financial firms (SIC 6000-6999 excluded)
- Regulated utilities excluded (SIC 4900-4999)
- Positive total assets (AT > 0)
- Non-missing GVKEY and fiscal year
- Minimum 50 trading days for market variables

---

## Relationship to V2/V3

### V1 vs V2 Financial Variables

| Aspect | V1 (this folder) | V2 (3_Financial_V2/) |
|--------|------------------|----------------------|
| Purpose | General firm controls | Hypothesis-specific variables |
| Scripts | 3.0-3.4 (general features) | 3.1-3.8 (H1-H8 specific) |
| Outputs | Controls for all analyses | DVs and IVs for specific hypotheses |
| Status | STABLE | STABLE |

### H9 Financial Variables (now in 3_Financial_V2/)

Advanced interaction variables for H9 were consolidated into V2 (Phase 64, 2026-02-12):
- `3.11_H9_StyleFrozen.py` - CEO style frozen measures
- `3.12_H9_PRiskFY.py` - Political risk measures (PRisk)
- `3.13_H9_AbnormalInvestment.py` - Abnormal investment (Biddle residuals)

H9 scripts now reside in 3_Financial_V2/ alongside other hypothesis-specific variables.

---

## Execution Notes

### Execution Order

1. **3.0_BuildFinancialFeatures.py** - Initial feature construction
2. **3.1_FirmControls.py** - Standard firm controls
3. **3.2_MarketVariables.py** - Market-based variables
4. **3.3_EventFlags.py** - Event study timing

Scripts 3.1 and 3.2 can run in parallel.

### Dependencies

- **Compustat Annual:** Required for firm controls
- **CRSP Daily:** Required for market variables
- **Sample Manifest:** Required for GVKEY-fiscal year mapping

### Known Issues

None - V1 scripts are stable and no longer modified.

---

## References

Variable construction follows standard finance research practices:

- **Firm controls:** Opler, Pinkowitz, Stulz, and Williamson (1999) - cash holdings determinants
- **Market variables:** Campbell, Lo, and MacKinlay (1997) - econometrics of financial markets
- **Event studies:** MacKinlay (1997) - event study methodology

---

## Contact and Replication

For replication questions:
- `README.md` (root): Project overview
- `CLAUDE.md`: Coding conventions
- Individual script headers: Implementation details

---

*Last updated: 2026-02-14*
*Phase: 78-documentation-synchronization*
*Version: v1.0 Financial Variables*
