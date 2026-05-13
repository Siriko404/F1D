# §III.E.4 Design Spec — LOCKED 2026-05-05 [SUPERSEDED 2026-05-05 PM]

> **⚠ SUPERSEDED:** This morning's design (Hasan 2022 4-layer ladder + 
> UncResCEO×log(PRisk) interaction) was rejected by user 2026-05-05 PM:
> "interaction-based, type-redundant with H1.2/H1.3 modus tollens".
>
> **NEW DESIGN:** see `tmp/sec_iiie4_design_revised_2026_05_05_pm.md` — 
> HighPRisk_pre × Post(Trump 2016) DiD on Cash. No interactions. Story B 
> indicator framing. All data on disk.
>
> **SESSION TRAIL:** see `memory/project_session_2026_05_05_pm_design_pivot.md`

---

## Design class (STALE — kept for reference)
**Hasan 2022 RQFA replication + UncResCEO×log(PRisk) interaction novelty.**

## Anchor citations

### Tier 0 — primary replication anchor
**Hasan, S.B., Alam, M.S., Paramati, S.R., & Islam, M.S. (2022).** "Does firm-level political risk affect cash holdings?" *Review of Quantitative Finance and Accounting*, Vol. 59(1), pp. 311-337. **DOI: 10.1007/s11156-022-01049-9**

### Tier 1 — supporting/cousin papers
- **Hu, X., Kang, Y., Li, O.Z., & Lin, Y. (2024).** "Trump election and minority CEO pessimism." *Review of Accounting Studies* (DOI: 10.1007/s11142-024-09843-7) — template for OPTIONAL 5th layer
- **Hassan, T.A., Hollander, S., van Lent, L., & Tahoun, A. (2019).** "Firm-Level Political Risk: Measurement and Effects." *QJE* 134(4), pp 2135-2202 (DOI: 10.1093/qje/qjz021) — foundational PRisk construct
- **Akyol, A.C. & Wei, M. (2024).** "Firm-Level Political Risk and Stock Repurchases." SSRN WP (DOI: 10.2139/ssrn.4954055) — supervisor's own methodological cousin

## The headline regression (re-run inside each layer)

```
Cash_{i,t} = α
           + β1·log(PRisk)_{i,t-1}             ← from Hasan 2022
           + β2·UncResCEO_{i,t}                 ← our existing variable
           + β3·UncResCEO × log(PRisk)_{i,t-1}  ⭐ OUR NOVELTY
           + γ·Bates_2009_controls               ← from Hasan 2022
           + Firm_FE + YearQuarter_FE + ε       ← from Hasan 2022

DV:           Cash_{i,t} = cheq / atq (Bates 2009 form)
Treatment:    log(Hassan PRisk) lagged 1 quarter (Hasan 2022 spec)
Sample:       2002–2018 (subset of Hasan 2022's 2002–2021)
Industry excl: SIC 6000-6999 (financials) + 4900-4999 (utilities)
Firms:        ~2,429 (our existing F1D panel)
Obs:          ~112,968 firm-quarters total; ~43,333 in operative sample after lagged-DV + sector exclusions

Bates 2009 controls (verbatim from Hasan 2022):
  Size = log(book value of total assets)
  M/B  = market value / book value of assets
  Cashflow = (earnings after interest+div+tax, before D&A) / book assets
  NWC  = (working capital − cash) / book assets
  R&D  = R&D expense / sales
  Capex = CapEx / book assets
  Leverage = (long-term debt + current debt) / total assets
  DivDummy = 1 if pays dividends
  Acquisition = acq expense / book assets
  Industry sigma = avg SD of cashflow within industry
  
Coefficient interpretations:
  β1 → "Firms with higher PRisk hoard more cash" (Hasan 2022 result, replicated)
  β2 → "Firms with more uncertain CEO speech hoard more cash" (our existing finding)
  β3 → ⭐ "CEO speech-uncertainty AMPLIFIES the PRisk → cash channel"
       (channel-isolation novelty; one-tailed test β3 > 0)
```

## The 4-layer endo ladder (replicated from Hasan 2022)

```
LAYER 4 — PSM (propensity-score matching)
  Following Rosenbaum-Rubin 1983.
  Match high-PRisk firms (top quartile or median split) to similar low-PRisk firms
  on observable Bates controls. Re-run regression on matched sample.

LAYER 3 — 2SLS Instrumental Variable
  Instrument: Partisan Conflict Index (PCI) by Azzimonti 2018.
  Source: FRED PCI series.
  First-stage: log(PRisk)_{i,t-1} = δ + ζ·PCI_{t-1} + Bates_controls + FE + ν
  Second-stage: Cash = α + β1·PRisk_fitted + β2·UncResCEO 
                     + β3·UncResCEO × PRisk_fitted + Bates + FE + ε
  Hasan 2022 reports F = 21.918*** and second-stage β = 0.912***.
  Exclusion defense (verbatim): "limited evidence, if any, that establishes the link
                                 between partisan conflict and the amount of cash firms' hold"
  Wu-Hausman endogeneity test required.
  
  ALTERNATIVE INSTRUMENT (for robustness): Akyol-Wei polarization 
    = (1/N)Σ(1 − |Yea% − Nay%|) from House voting records
    = quarterly time-varying

LAYER 2 — DiD natural experiment
  Shock: 2010 decennial census redistricting of federal electoral districts.
  Treated firm: dummy = +1, 0, −1 based on whether congressional district's
                political-risk profile changed (increased, unchanged, decreased) due to redistricting.
  Post: dummy = 1 if year > 2011, else 0.
  Spec: Cash = α + β1·Treated×Post + β2·Treated + β3·Post + Bates + FE + ε
  Add our novelty: + β4·UncResCEO + β5·UncResCEO×Treated×Post
  
  REQUIRES: HQ ZIP code → congressional district mapping pre/post 2011
            Hassan PRisk values per congressional district pre/post

LAYER 1 — Baseline panel OLS (the headline regression above)
  No identification claim; establishes correlation.
```

## Optional 5th layer — Trump 2016 supplement (Hu 2024 RAST template)

```
Sample restriction: Q3 2014 – Q4 2018 (Hu cutoff to avoid 2019 trade war + Covid)
Treatment: HighPRisk_pre = 1 if mean PRisk over Q3 2014–Q3 2016 ≥ industry-year median
Post: dummy = 1 if t ≥ Q4 2016 (Trump election)
Spec: Cash = α + β1·HighPRisk_pre + β2·HighPRisk_pre × Post + β3·Post 
            + β4·UncResCEO + β5·(UncResCEO × HighPRisk_pre × Post)
            + Bates + FE + ε

Pre-trends placebo: HighPRisk_pre × Pre_2qtr ≈ 0
1:5 matching: industry + firm size (Hu 2024 template)

Status: OPTIONAL. Adds Trump-specific external validity. Not load-bearing.
```

## How this addresses the reverse-causality endogeneity threat

```
Threat: Cash → CEO speech (firms with cash piles have CEOs talking uncertainly).
        Same observed correlation as forward arrow (speech → cash).

Defense logic:

LAYER 1 (OLS):
  Firm FE absorbs time-invariant firm-level factors.
  PRisk lag-1 reduces simultaneity bias.
  PARTIAL defense — doesn't kill reverse arrow directly.

LAYER 2 (DiD redistricting):
  Redistricting is a POLITICAL boundary change — congressional districts redrawn
  due to 2010 census, not due to firm cash decisions.
  If reverse arrow alone explained PRisk → Cash, redistricting (geographic, not
  firm-driven) couldn't generate the DiD effect.
  Significant DiD coefficient = forward causation supported.

LAYER 3 (2SLS PCI):
  PCI is a NATIONAL partisan-conflict index, exogenous to individual firm cash decisions.
  First stage strong (F = 21.9 in Hasan 2022).
  Exclusion: PCI affects Cash ONLY through PRisk (defensible because PCI is national,
  Cash decisions are firm-specific).
  Significant second stage = causal effect of PRisk on Cash.

LAYER 4 (PSM):
  Reduces selection-on-observables bias.
  High-PRisk and low-PRisk firms made comparable on Bates controls.
  Effect persists in matched sample = not driven by firm-characteristic differences.

CHANNEL NOVELTY (β3 interaction in each layer):
  Tests WHICH mechanism mediates the PRisk → Cash relationship.
  Pure-financial-constraint channel: β3 ≈ 0 (CEO speech unrelated to mediation)
  Speech-mediated precautionary channel: β3 > 0 (speech amplifies the effect)
  Modus tollens-style refutation: only the speech-channel story produces β3 > 0.

Net: passing PRisk → Cash + UncResCEO × PRisk effect through 4 different
identification strategies, each with different exogenous variation, makes the
forward channel highly defensible. Reverse-only story cannot generate all four
patterns simultaneously.
```

## Implementation notes

### Data acquisition needed
1. **Hassan PRisk:** publicly distributed at https://www.firmlevelrisk.com/
   - Quarterly firm-level PRisk + 8 sub-categorical topics
   - Match on cusip/gvkey/ticker → our F1D panel via CCM crosswalk
2. **Partisan Conflict Index (PCI):** Azzimonti 2018, FRED-distributed
   - Series: PCI; quarterly
3. **2010 redistricting map:** US Census + state-level congressional district changes 2010-2011
   - Firm HQ ZIP → congressional district pre-2011
   - Firm HQ ZIP → congressional district post-2011
   - Identify firms whose district's political-risk profile shifted
4. **House voting records (alternative IV):** voteview.com / govtrack — for Akyol-Wei polarization measure

### New code modules needed
1. `src/f1d/shared/variables/political_risk.py` — Hassan PRisk merge + log transform + lag-1
2. `src/f1d/shared/variables/political_polarization.py` — PCI + polarization data
3. `src/f1d/variables/build_h1_4_prisk_cash_panel.py` — panel builder for §III.E.4 layers
4. `src/f1d/econometric/run_h1_4_prisk_cash.py` — runner for full 4-layer ladder

### Suite ID
**H1.4** (continues numeric pattern from H1.1, H1.2, H1.3 in §III.E modus tollens).

### Existing infrastructure to reuse
- `f1d.shared.outputs.write_suite_spec`
- `f1d.shared.outputs.extract_coefs_panelols`
- `f1d.shared.outputs.generate_attrition_table`
- `f1d.shared.outputs.generate_manifest`
- `f1d.shared.variables.panel_utils.build_cal_yr_qtr_index`
- `f1d.shared.variables.panel_utils.assign_industry_sample`
- Path: `config/suite_render_order.yaml` add `H1.4`

## Open questions for advisor confirmation

1. Does Sina's supervisor (Dr. Akyol) approve **Hasan 2022 RQFA** as anchor (vs alternative anchors like Hu 2024 RAST or his own Akyol-Wei 2024)?
2. Does he prefer PCI-as-IV (Hasan 2022) OR polarization-as-IV (his own Akyol-Wei 2024) for Layer 3?
3. Should we add the OPTIONAL 5th layer (Trump 2016 + Hu 2024 RAST template) as supplement?
4. Is the UncResCEO × log(PRisk) interaction novelty (β3) a valid contribution, or does he see this as already covered in Hasan 2022's sub-categorical PRisk decomposition?

## Citation chain for §III.E.4 paragraph in thesis

```
"Following Hasan, Alam, Paramati, and Islam (2022), we test the relationship between
firm-level political risk (Hassan, Hollander, van Lent, and Tahoun 2019) and corporate
cash holdings using the [4-layer endo ladder]. Our novel contribution extends Hasan
et al.'s (2022) framework by adding an interaction term between PRisk and the
DWZ (2021)-derived CEO speech-uncertainty residual UncResCEO. This tests whether
CEO speech-uncertainty amplifies the precautionary cash channel..."
```
