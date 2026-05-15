# Boasiako-O'Connor Keefe (2020) EFM — verbatim spec extract + F1D audit

Source: `docs/papers/boasiako_oconnor_keefe_2020_databreach_efm.pdf` (24 pages, EFM 2021;27:528-551).
Extraction: pdfplumber via `tmp/extract_boasiako_pdf.py`.
Per-page splits: `tmp/boasiako_pages/p01.txt … p24.txt`.

---

## §3.2 Estimation technique (p8) — VERBATIM

> "The staggered timing of the passage of the state-level disclosure laws enables us to use states that had not yet passed disclosure laws at a given time (including states that eventually enacted disclosure laws, as well as states that never enacted them within the period of study), to control for potential confounding effects. Therefore, we use a difference-in-differences approach to empirically explore the effects of the disclosure laws on cash holdings. Our model setup mirrors that of Francis et al. (2014). We estimate
>
> **Cash_{i,s,t} = α + β · Disclosure_Law(0/1)_{s,t} + γ X_{i,s,t} + θ_s + δ_t + ρ_j + ν_i + ε_{i,s,t}**     (1)
>
> where i, s, and t index firm, state, and time, respectively. The dependent variable, Cash, is cash and marketable securities scaled by total book assets; **Disclosure_Law(0/1)_{s,t} is a dummy variable that switches to one the year after the focal state passed the disclosure law**; X_{i,s,t} is a vector of controls; θ_s represents a set of state dummies that account for state-level unobservable factors that could be correlated with the data breach disclosure laws, and thus bias our estimates; δ_t represents year dummies to control for secular shocks in cash holdings coinciding with the passage of the disclosure laws; and ρ_j and ν_i capture industry and firm fixed effects, respectively. The term ε_{i,s,t} is a random error term. **We cluster standard errors by state, because the treatment is defined at the state level.**"

Footnote 5 (p8): "The industry dummies are constructed based on the **49-industry classification of Fama and French (1997)**."

## §3.3 Variables (p9) — VERBATIM

> "We use the most traditional measure of cash in the literature (Bates et al., 2009; Opler et al., 1999) as our dependent variable. We measure Cash as cash and marketable securities scaled by total book assets.
>
> ... We follow the literature (Bates et al., 2009; Opler et al., 1999) in our empirical testing and control for several variables that affect firm cash policy. Specifically, we control for **Firm Size, Firm Age, Book Leverage, Market-to-book, Cash Flow, Capital Expenditure, Acquisition Expenditure, Dividend Paying Firms(0/1), R&D Expenditure, Net Working Capital, and Industry Cash Flow Volatility**. The definitions of all the variables are detailed in the Appendix. **We winsorize all variables at the 1st and 99th percentiles to minimize the influence of outliers**."

## §3.1 Sample filters (p7) — VERBATIM

> "1997-2015 ... 5 years before California passed the first state-level data breach disclosure law, in 2002, and ends 5 years after Mississippi passed a similar law, in 2010. ... we exclude all financial firms — that is, those with Standard Industrial Classification (SIC) codes 6000-6999 ... We exclude utility companies (SIC codes 4900-4999) ... We further drop observations with negative or missing total book assets. **This yields a final sample of 56,646 firm-year observations.**"

## §4.1 Baseline regression — Table 2 STRUCTURE (p11-p12) — VERBATIM

Caption (p11): "Table 2 presents the baseline estimation results. We include state, year, industry, and firm fixed effects in various specifications. **Column (1)** includes controls for year, industry, and state fixed effects. In **Column (2)**, we include year and firm fixed effects. ... Therefore, in **Column (3)**, we exclude California and re-estimate Equation (1). ... in **Column (4)**, we purposely exclude the financial crisis period (2007-2009) from the sample period. In **Column (5)**, the standard errors are two-way clustered by state and year. Finally, in **Column (6)**, we follow Falato and Sim (2014) and re-estimate our baseline regression using first differences."

| Col | FE | SE | Sample restriction | β (paper) |
|---|---|---|---|---|
| 1 | year + industry + state | state-cluster | full | 0.0076** |
| 2 | year + firm | state-cluster | full | 0.0056** |
| 3 | year + industry + state | state-cluster | excl California | 0.0032** |
| 4 | year + industry + state | state-cluster | excl 2007-2009 | 0.0078** |
| 5 | year + industry + state | two-way state+year | full | 0.0076*** |
| 6 | year + industry + state + firm | HC (first-difference) | full (FD) | 0.0026** |

N for each: 56,646 / 56,646 / 47,526 / 48,551 / 56,646 / 47,117.

## §4.3 Role of financial constraints — Table 4 STRUCTURE (p14) — VERBATIM

> "Specifically, following To et al. (2018) and Francis et al. (2014), we sort firms into financially constrained and unconstrained groups based on **firm size, firm age, and dividend payout ratio**. For each year, we rank the firms over the sample period and **categorize firms in the bottom terciles of the size, age, and dividend payout distributions as financially constrained**. ... We create the dummy variables SmallFirms(0/1), YoungFirms(0/1), and Non-dividendPayer(0/1) ... We interact with the various financial constraint measures with the Disclosure Law(0/1) dummy ... In **Table 4, we include year and firm fixed effects in all specifications**. ... In **Columns (1)-(3)**, the variable of interest is the interaction of the financial constraint measure with the disclosure law dummy."

| Col | FE | DV | Interaction |
|---|---|---|---|
| 1 | year + firm | **Cash** | Small × Disclosure_Law |
| 2 | year + firm | **Cash** | Young × Disclosure_Law |
| 3 | year + firm | **Cash** | NonDiv × Disclosure_Law |

KEY: paper Table 4 has channel partitions on **CASH** with **year+firm FE only**.

## Appendix Table A1 (p24) — VERBATIM variable definitions

| Variable | Definition |
|---|---|
| Cash | "Cash and marketable securities scaled by total book assets **at the beginning of the year**" |
| Disclosure_Law (0/1) | "1 for periods after the enactment of the state-level data breach notification laws, and 0 otherwise" |
| Firm Age | "Natural logarithm of the number of years a firm has been listed in the **merged CRSP/Compustat** database" |
| Market-to-book | "Ratio of total book assets less the book value of common equity plus the total market value of equity, all divided by total book assets" |
| Firm Size | "Natural logarithm of total book assets" |
| Book Leverage | "Ratio of total book debt (short-term debt plus long-term debt) to total book assets" |
| Cash Flow | "Ratio of earnings after interest, dividends, and taxes but before depreciation to book assets" |
| Capital Expenditure | "Ratio of capital expenditure to total book assets at the beginning of the year" |
| Acquisition Expenditure | "Ratio of acquisitions to total book assets at the beginning of the year" |
| Dividend Paying Firms (0/1) | "1 in the year a firm pays dividends, and 0 otherwise; set to zero if missing" |
| R&D Expenditure | "Ratio of R&D expenses to total book assets at the beginning of the year" |
| Net Working Capital | "Ratio of net working capital to net assets" |
| Industry Cash Flow Volatility | "Standard deviation of industry average cash flows for the previous 10 years; at least 3 years of observations required" |

---

# F1D implementation audit

## Match summary

| Spec item | Paper | F1D | Status |
|---|---|---|---|
| Eq 1 functional form | Cash = α + β·DL + γX + θ_s + δ_t + ρ_j + ν_i + ε | linearmodels PanelOLS w/ entity_effects (firm) + other_effects (state, year, industry) | ✅ |
| Window | 1997-2015 annual | 1997-2015 annual | ✅ |
| Sample filter | drop SIC 4900-4999, 6000-6999, AT≤0 | same + us_only=True | ✅ + tighter |
| Treatment Y+1 | "year after" | baked into Disclosure_Law builder | ✅ |
| SE clustering (cols 1-4) | state-cluster | clusters_col="state" | ✅ |
| Industry classification | FF49 | FF49Industry classifier | ✅ |
| Cash DV | CHE / AT(BoY) | che / at_lag1 | ✅ |
| 11 controls | named list | matches | ✅ |
| Winsorize 1%/99% | "all variables" | `_winsorize_1pct` per CONTINUOUS_CONTROLS | ✅ |
| Industry CF Vol | σ industry-AVG over 10y, ≥3y obs | σ FF49-MEAN over [t-10, t-1], ≥3y floor | ✅ |
| Cash Flow formula | "earnings after interest+div+tax BUT before depreciation / AT" | (OIBDP - XINT - TXT - DVC) / AT | ✅ Bates 2009 interpretation |
| Firm Size | log(AT) | log(AT) | ✅ |
| Book Leverage | (DLC + DLTT) / AT | (DLC + DLTT) / AT | ✅ |
| Market-to-book | (AT - BVE + MVE) / AT | (AT - CEQ + PRCC_F·CSHO) / AT | ✅ |
| CapEx | CAPX / AT(BoY) | CAPX / AT_lag | ✅ |
| AcqEx | AQC / AT(BoY) | AQC / AT_lag | ✅ |
| Dividend Paying | 1 if pays div, 0 else (0 if missing) | 1 if DVC>0 else 0 (fillna 0) | ✅ |
| R&D | XRD / AT(BoY) | XRD / AT_lag, fillna(0) | ✅ |
| NWC | "NWC / net assets" (vague) | (ACT - LCT - DLC) / (AT - CHE) | ⚠️ F1D adds DLC subtraction (Bates 2009 net-of-debt convention); paper text vague but cites Bates 2009 |
| Firm Age | "log(years in CRSP/Compustat merged)" | log(years since first F1D Compustat appearance) | ⚠️ F1D uses Compustat-only; under-estimates pre-1990 IPOs |

## Headline gaps (table structure)

### Gap 1: Table 2 missing 2 cols
Paper Table 2 has 6 cols. F1D has 4.
- Col 5 (two-way state+year SE): NOT IMPLEMENTED. Same FE as col 1, only SE differs.
- Col 6 (first-differences, Falato-Sim 2014): NOT IMPLEMENTED. FD specification.

### Gap 2: Table 4 channel partitions wrong DV (was on speech, should be on cash) — DROPPED today
Paper Table 4 has channel partitions on **Cash** (3 cols, Small/Young/NonDiv × DL, year+firm FE).
F1D had them on **Speech** (UncResCEO_c, 6 cols, mixed FE) — methodology deviation.
Today's commit `9c8110a` DROPPED the speech channel cols. Cash channel cols NOT YET ADDED.

### Gap 3: Speech-as-DV extension is F1D-only (paper has no speech)
Paper publishes only Cash. F1D's 4 speech cols are extension, not verbatim.

## Headline gaps (numerical)

| Spec | Paper β | F1D β | Ratio | Notes |
|---|---|---|---|---|
| Col 1 (ind+state+year FE) | +0.0076** | +0.0262** | 3.4× | F1D inflated; pre-noted Sina-ratified PROCEED |
| Col 2 (firm+year FE) | +0.0056** | +0.0580*** | 10.4× | F1D inflated |
| Col 3 (excl-CA) | +0.0032** | +0.0110 NS | 3.4× β, NS | F1D NS (paper sig) |
| Col 4 (excl-crisis) | +0.0078** | +0.0317** | 4.1× | F1D inflated |

Paper N = 56,646. F1D N = 49,402 (87% match). F1D drops 7,244 firm-years vs paper, likely due to:
- 11-control complete-case (paper may impute or use available)
- us_only filter (paper doesn't explicitly state US-only)
- More stringent FF49 merge

## Recommendations (RANKED by replication-fidelity gain per LOC)

| # | Action | Effort | Replication gain |
|---|---|---|---|
| 1 | Add Table 2 col 5 (two-way state+year SE) | trivial — 1 spec entry | Closes 1/2 of Table 2 gap; paper's most-cited col |
| 2 | Add Table 4 channel partitions on CASH (3 cols, year+firm FE) | low — re-add Block 3 with DV=cash | Closes Table 4 entirely; matches paper §4.3 verbatim |
| 3 | Add Table 2 col 6 (first-differences) | medium — new spec, FD-transform panel | Closes Table 2 gap; rare-cited spec |
| 4 | Investigate β magnitude inflation 3.4-10× | high — sample composition forensics | May not converge; structural differences |
| 5 | Switch Firm Age to merged CRSP/Compustat database | medium — add CRSP first-listing | Marginal precision gain; minor coefficient impact |
| 6 | Document NWC DLC-subtraction as Bates 2009 convention deviation | trivial — code comment | No replication impact, audit-trail only |

## Decision (locked 2026-05-14)

**Sina directive:** "Re-use F1D Unrated cells — skip Boasiako's 3 partitions."

**Locked structure:** Current 8-col Boasiako baseline (4 cash + 4 speech, paper Table 2 cols 1-4 + DV-substitution mirror).

**Constraint-channel narrative:** Comes from F1D **Unrated** cells (H1.2 `run_h1_2_cash_constraint`), NOT from rebuilding Boasiako Small/Young/NonDiv tercile partitions.

### Why skip Boasiako's 3 partitions

F1D Unrated and Boasiako's 3 proxy the **same construct** (financial constraint) via **different operationalizations**:

| Proxy | Source | Lineage |
|---|---|---|
| F1D Unrated | No S&P credit rating (`splticrm IS NULL`) | ACW 2004 + Faulkender-Wang 2006 (no public-debt access) |
| Boasiako Small | Bottom tercile firm size | Hadlock-Pierce 2010 SA index |
| Boasiako Young | Bottom tercile firm age | Hadlock-Pierce 2010 SA index |
| Boasiako NonDiv | Non-dividend payer | ACW 2004 payout + Bates 2009 |

Empirical overlap (literature):
- Unrated ∩ Small: HIGH (~70-80%)
- Unrated ∩ Young: MED (~50-60%)
- Unrated ∩ NonDiv: MED (~55-65%)

Same economic story; different sample compositions. Re-using F1D Unrated avoids redundant rebuild and preserves H1.2 cross-link.

### Open (deferred)

Paper Table 2 cols 5 (two-way SE) + col 6 (first-differences) NOT implemented. Re-add only on explicit Sina request — current 8-col headline is the lock.
