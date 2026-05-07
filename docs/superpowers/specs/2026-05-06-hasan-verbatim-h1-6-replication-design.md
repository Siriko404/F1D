# Hasan-verbatim H1.6 Redistricting DiD Replication — Design

**Date:** 2026-05-06
**Tier:** 1 (single file, ~50 LOC)
**Anchor:** Hasan, Alam, Paramati & Islam (2022), RQFA 59(1), Table 4

## Purpose

Replicate Hasan 2022 Table 4 redistricting DiD verbatim — every formula,
every sample restriction, every variable definition matches the paper.
Then report the result honestly, regardless of whether we reach Hasan's
significance level.

## Hasan Table 4 reference targets (verbatim)

```
                        Col 1 (Firm FE)     Col 2 (Industry FE)
Treated × After         +0.007 ***          +0.006 **
                        (p = 0.007)         (p = 0.050)
Treated                 −0.008 ***          −0.006 **
After                   +0.038 ***          +0.049 ***
N                       24,311              24,311
Adj R²                  0.063               0.286
SE clustering           firm                firm
```

## Confirmed verbatim matches (no fix)

```
DV:              cheq / atq                                  ✓
SIC excl:        6000-6999, 4900-4999                        ✓
M/B formula:     (AT + PRCC_F·CSHO − CEQ) / AT               ✓ (named "TobinsQ")
NWC:             (WCAP − CHE) / AT                           ✓
Acquisition:     AQC / AT                                    ✓
Capex:           CAPX / AT                                   ✓
Leverage:        (DLTT + DLC) / AT                           ✓
DivDummy:        1 if DVC > 0                                ✓
Size:            log(AT)                                     ✓ (App A def)
R&D formula:     XRD / SALE                                  ✓
Tertile:         qcut q=3, equal-frequency                   ✓
After:           year > 2011                                 ✓
SE cluster:      firm                                        ✓
```

## Deviations to fix

```
D1 [MAJOR]   Sample = MOVERS ONLY                  state_cd_pre != post filter
             Hasan: "moving firms constitute       Drop stayers entirely from
                     our treated firms"            regression sample
             Ours: all firms with both CDs

D2 [MAJOR]   Cashflow formula
             Hasan: (OIBDP - XINT - TXT - DVC)/AT  Replace OANCF with
             Ours: oancf_q / atq                   income-statement formula

D3 [MEDIUM]  Industry sigma window
             Hasan: 10-year SD of CashFlow/AT      Rolling window 20q → 40q
             Ours: 5-year

D4 [MEDIUM]  Extras to drop
             Ours has: ROA, sCFO, SalesGrowth      Remove from CONTROLS list
             Hasan: not in 11-control list

D5 [LOW]     R&D missing handling
             Hasan: "the value of R&D is set       fillna(0) on RDSales
                     to zero"
             Ours: NaN propagates
```

## Hasan-silent items → defaults

Verified absent via NLM exhaustive search (Query 4):

```
Sample window           ABSENT  →  use full 2002Q1-2021Q3 (Hasan's full sample)
Min-PRisk filter        ABSENT  →  use ≥1 obs (most permissive; was ≥8 ours)
Winsorization           ABSENT  →  drop our 1/99 winsorize entirely
Tie-break in tertile    ABSENT  →  numpy default (s.rank(method="first"))
Missing data (other)    ABSENT  →  listwise drop on DV + Treated only
Control lag structure   ABSENT  →  contemporaneous (eq subscript t)
PRisk as control        ABSENT  →  do NOT add PRisk as separate control
                                   (Q3+Q4 confirmed)
```

## Implementation plan (incremental with verify gates)

```
Step  Action                                    Verify after
────  ───────────────────────────────────       ──────────────────────────
1.    D4 — drop ROA, sCFO, SalesGrowth          β similar; sanity check
2.    D5 — fillna(0) for RDSales                N firms increase if any
3.    D3 — industry sigma 5y → 10y              β shift; document
4.    Drop our winsorization                    β shift; document
5.    Drop ≥8 PRisk filter (≥1)                 N firms increase
6.    D2 — Cashflow formula change              β shift; document
7.    D1 — sample = movers only                 FINAL spec; compare to Hasan
```

After each step: print β, p_one, N, adj R² for all 4 columns.

## Stopping criterion

```
Run final spec (Step 7), record results, compare to Hasan Table 4.
Accept whatever sig level emerges. Do not iterate further on
silent-gap defaults to chase significance — that would over-fit.

Report: full β/p/N/R² grid for our spec vs Hasan Table 4 verbatim.
Document each Hasan-silent default we adopted.
```

## File scope

```
M  src/f1d/econometric/run_h1_6_test5_full_compustat.py     (control list,
                                                              cashflow formula,
                                                              window, filters,
                                                              movers-only
                                                              filter, winsorize
                                                              dropped, R&D
                                                              fillna)

(builder unchanged — used by other suites; modifications are runner-local)
```

## Out of scope

- §V prose update (deferred until results known)
- Body table change (TEST 3 F1D-call panel remains primary)
- Resolving why Hasan's firm-FE β has so much higher precision than ours
  (firm count + window length structural; not a "fix")
- New NLM queries (4 batches done; gap list is closed)

## Risks

```
Risk                                 Mitigation
─────────────────────────────────    ────────────────────────────────────
Movers-only filter shrinks N         Accept; Hasan's N = 24,311 is the
heavily                              target; we can only get there with
                                     full window + minimum filters

Cashflow formula change requires     OIBDPQ, XINTQ, TXTQ, DVY exist in
new Compustat fields                 our parquet; verify before edit

Industry sigma 10y window            Hasan-faithful even though our PRisk
exceeds our PRisk pre-window         pre-window is 5y (different windows
                                     for different vars)

Step 3 result (current §V)           Keep result + memory for fallback;
contradicts new spec result          §V update is separate phase
```
