# H1.5 Brexit Phase 0 — Data Acquisition + Spec Finalized (2026-05-08 PM)

This is the durable in-repo log for the Brexit DiD data-acquisition phase. The session-memory equivalent (with framing + cross-references) lives in
`memory/project_session_2026_05_08_brexit_data_acquired.md` (outside repo, in user-level Claude memory).

## Master state

- HEAD: `cd74832` (UNCHANGED — no code commits this session, only data acquisition + spec refinement)
- Branch: master

## NLM rounds (3 this session, 16 questions total)

| Round | Q | Topic | Result |
|-------|---|-------|--------|
| Q1' (post-compact, 12q) | sample, DV, β^UK, 10-K, controls, FE, SE, POST, robustness, placebo, identification, parallel-trends | Detailed extraction; flagged 10 gaps |
| Q2 (5q) | SIC ranges, β^UK structure, 10-K scope+year, lagged DV+SE, parallel trends | 8 of 12 sub-questions returned "NOT IN PAPER" — supplementary tables (C1, C4, C5) inaccessible to NLM |
| Q3 (3q targeted) | Footnote 27 verbatim, SIC ranges (entire-doc search), 10-K parsing detail | **Critical:** Footnote 27 is in **Section VI.A FX-robustness**, NOT baseline; β^UK baseline is STATIC per-firm OLS |

## Locked spec (verbatim)

### Sample + DV
- Period: 2010Q1-2016Q4
- N: 41,630 firm-quarters baseline
- Industry exclusions: utility + financial (SIC 4900-4999, 6000-6999 — F1D default; verbatim NOT IN PAPER MAIN)
- Size: market value OR book assets >= $10M
- DV: CASH = CHE / lag(AT), winsorized 1% both tails

### β^UK builder (BASELINE) — Section IV.A.1, eq. 13
```
For each firm i:
  Compute monthly rolling 24-mo vol(r_i,t) for t = 2010M1...2014M12
  Same for vol(FTSE100_t), vol(SP500_t), vol(FX£_t)
  Per-firm OLS: vol(r_i,t) = α_i + β^UK_i·vol(FTSE100_t)
                            + γ_i·vol(SP500_t) + δ_i·vol(FX_t) + ε
  Output single β^UK_i per firm (STATIC, not time-varying)
Filter:   nonnegative β^UK_i (drop β<0 from BOTH treated AND control)
Tercile:  upper = TREATED (1), bottom = CONTROL (0), middle dropped
Expected: ~449 treated + ~360 control firms
```

**MAJOR CORRECTION FROM PRIOR SESSIONS:** Earlier memos described β^UK as a "rolling regression producing time-varying β^UK_{i,t}." That description is the FX-robustness spec (Section VI.A), not baseline. Baseline = ONE β^UK per firm.

### 10-K classifier — Section IV.A.2 + Footnote 14
**Brexit terms (verbatim, complete):**
- Primary: "Brexit", "Great Britain", "Uncertainty"
- Subsumed: "Referendum", "Uncertain", "United Kingdom", "UK", "U.K.", "G.B."

**Defaults (NOT IN PAPER):**
- Filing scope: whole 10-K (not Item 1A only)
- Filing year: calendar 2015 (paper notes "Mar-Jun filing window" implies calendar)
- Matching: case-insensitive, whole-word, normalize "U.K."→"UK"

**Cutoffs:** >5 mentions = TREATED, =0 = CONTROL, expected 807+433 firms.

### DiD equation — Section V.A
```
Y_{i,t} = α + δ(POST_t × HIGH_UK_EXPOSURE_i) 
        + θ·CONTROLS_{i,t-1} 
        + Σ FIRM_i 
        + Σ Σ INDUSTRY_j × QUARTER_t 
        + ε_{i,t}

POST_t:    1 in 2016Q3-Q4 only (2 quarters POST, 26 quarters PRE)
Industry:  Hoberg-Phillips FIC 100 (acquired this session)
SE:        double-cluster firm + calendar-quarter (HC1 robust)
```

### Controls (verbatim Section V.A)
**Macro (5, all 1Q-lagged):**
1. USD/British pound FX rate
2. VIX
3. 1Y-ahead GDP forecast (Philly Fed Livingstone Survey)
4. Consumer Sentiment Index (Michigan UMCSENT)
5. Leading Economic Indicator (Philly Fed; default = ADS Index)

**Firm-level (5, all 1Q-lagged):**
1. Stock returns
2. Tobin's Q
3. Cash flow
4. log(Assets)
5. Sales growth

### Robustness layers
- PSM-matched sample (verbatim)
- Drop Q4 2016 (compare 2016Q3 vs 2015Q3 only)
- Drop WZZ-2018 "Trump losers" (DEFER to v2)
- Cameron 2015Q3 vs 2014Q3 placebo
- Debt-ceiling 2011Q2-Q4 vs 2010Q2-Q4 placebo

## Defaults for 8 un-closeable gaps (locked)

| Gap | Default | Justification |
|-----|---------|---------------|
| SIC utility/financial ranges | 4900-4999 + 6000-6999 | F1D convention |
| 10-K filing scope | Whole 10-K | Most permissive |
| 10-K filing year | Calendar 2015 | Paper notes "Mar-Jun filing window" |
| 10-K matching | Case-insensitive, whole-word | Standard NLP |
| Robust SE | HC1 within firm+quarter cluster | linearmodels.PanelOLS default |
| Lagged DV | NOT in main spec | Eq. 14 omits Y_{t-1} |
| Parallel trends | Standard event-study form | Tables C4-C5 inaccessible |
| WZZ filter detail | Defer | Not in Campello text |

## Hassan Brexit_Exposure investigation (cannot substitute)

`inputs/FirmLevelRisk/firmquarter_2022q1.csv` has columns `Brexit_Exposure`, `Brexit_Risk`, `Brexit_Net_Sentiment` (Hassan-Sautner-style earnings-call topic exposure).

**Empirical:** Pre-Q3-2016 ONLY 59 US firms had non-zero Brexit_Exposure vs Campello's 1,240 firms via 10-K (21x less power).

**Methodological:** Campello explicitly rejects earnings-call substitutes ("we choose not to rely on conference calls...severe problems with the information content of such calls").

**Use case:** Post-Q3-2016 Brexit_Exposure (670 US firms) as Story B novelty validator (cross-check Campello-treated firms had higher attention). NOT a substitute for 10-K classification.

## F1D pipeline audit (already-have findings)

```
inputs/CRSP_DSF/                    Daily 1999-2022, RET + sprtrn + vwretd embedded
inputs/comp_na_daily_all/           Compustat daily 2000-2020 (956k rows)
inputs/Compustat_Quarterly_OCF_Extended/  Quarterly fundamentals
inputs/EconomicPolicyUncertaintyIndex/  US + Global EPU (BBD)
inputs/matteoiacoviello/            Iacoviello GPR
inputs/TNIC3HHIdata/                HP TNIC3 HHI/TSIMM (yearly, gvkey)
inputs/FF1248/                      FF12 + FF48 SIC classifications
inputs/FirmLevelRisk/               Hassan PRisk + Brexit_Exposure (firm-quarter)

src/f1d/shared/variables/_crsp_engine.py     Daily CRSP + windowing
src/f1d/shared/variables/macro_uncertainty.py  GPR + EPU monthly→manifest matcher
src/f1d/econometric/run_h24_us_epu.py    Monthly→quarterly matching template
src/f1d/shared/variables/trump_did_treatment.py  H1.5 Trump DiD existing
src/f1d/shared/industry_utils.py    FF12/FF48 mapping helper
```

## Data acquired this session (all under inputs/Brexit_replication/)

```
✅ BoE/USD_GBP_daily_2008-2018.csv         55 KB    daily
✅ CBOE/VIX_daily_1990-present.csv         468 KB   daily
✅ HobergPhillips_FIC/FIC_Data.zip         857 KB   FIC 50/100/200/300/400 bundle
✅ PhillyFed/ADS_Index_current.xlsx        780 KB   Aruoba-Diebold-Scotti
✅ PhillyFed/Livingston_means.xlsx         149 KB   Livingston means
✅ PhillyFed/Livingston_medians.xlsx       144 KB   Livingston medians
✅ UMich/UMCSENT.csv                       13 KB    Index of Consumer Sentiment monthly 1952-2026
✅ Yahoo_FTSE100/FTSE100_yfinance_monthly.csv  13 KB  yfinance one-shot, 132 rows monthly 2008-2018
   ────────
   ~2.5 MB total
```

**Acquisition workarounds (when API/script blocked):**

| Original | Block | Workaround |
|----------|-------|------------|
| FRED VIXCLS | Times out (anti-bot) | CBOE direct CDN |
| FRED DEXUSUK | Times out | Bank of England XUDLUSS |
| FRED UMCSENT | Times out (script); browser works | Manual download by user |
| Stooq FTSE100 | API key + CAPTCHA | yfinance Python one-shot |
| Yahoo direct CSV | Cookies + crumb | yfinance handles cookies |

## 10-K archive filtering (in-place, no extraction)

```
SOURCE   inputs/10-X_C_2011-2015.zip       9.13 GB   179,140 files (SRAF Notre Dame)
TARGET   inputs/10-X_C_2015_10Konly.zip    826 MB    9,275 files
METHOD   Python zipfile rewrite (no extraction)
TIME     2.8 minutes
INTEGRITY  unzip -t passed: "No errors detected"

KEPT
  7,985  2015 10-K        regular annual reports
  1,258  2015 10-K-A      amended annual reports
     22  2015 10-KT       transitional annual
      5  2015 10-KT-A     amended transitional
  ─────
  9,270  total files + 5 directory entries = 9,275 entries

DROPPED
  146,607 files in 2011, 2012, 2013, 2014 (entire years)
  23,258 10-Q* files in 2015 (Campello specifies 10-K only)

POST-VERIFY  original 9.13 GB archive deleted (user confirmed Y)
```

## Phase 1 plan — 5 modules to write next

```
1. brexit_macro_controls.py       Load 5 macro series, lag 1Q, merge to manifest
                                   Reuses macro_uncertainty.py pattern (~1 day)
2. brexit_treatment_beta_uk.py    Per-firm vol regression → β^UK_i + tercile cut
                                   New, 60 monthly obs/firm OLS (~2 days)
3. brexit_treatment_10k.py        Parse 9,275 10-Ks, count 9 Brexit terms
                                   Regex case-insensitive (~1-2 days)
4. hoberg_phillips_fic100_industry.py  FIC100 → industry FE classifier
                                   Reuses TNIC3 builder pattern (~0.5 day)
5. run_h1_5_brexit_did.py         DiD eq + PSM + placebos + Q4-2016 robustness
                                   Mirror H1.6 runner (~2-3 days)
```

**Effort:** 5-7 days build + 2-3 days debug/spec verification.

## Open carry-overs

- §V update A/B/C choice (still deferred from 2026-05-06 H1.6 ship)
- §III.E.4 prose update (after Brexit MVP ships)
- WZZ-2018 paper acquisition (defer to v2 robustness)
- JFQA Cambridge Core supplementary (Tables C1, C4, C5) — defaults are conservative; defer
- 2 of 3 DiDs not yet built: Boasiako (databreach) + Chen (restatement)

## Files NOT committed (in repo gitignore)

- `inputs/Brexit_replication/*` — entire dir (per .gitignore line 190 `/inputs/`)
- `inputs/10-X_C_2015_10Konly.zip` — same

These data files exist on local disk only. This progress log + the corresponding memory file (`memory/project_session_2026_05_08_brexit_data_acquired.md`) document their content + provenance for cross-session durability.
