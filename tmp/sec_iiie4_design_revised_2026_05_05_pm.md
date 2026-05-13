# §III.E.4 Design Spec — REVISED 2026-05-05 PM (v3)

**SUPERSEDES** v2 (single-shock Trump 2016). User decision 2026-05-05 PM late: implement BOTH the redistricting DiD (Hasan 2022 Layer 2 replication) AND the Trump 2016 DiD as parallel evidence layers, each with cash + speech outcomes.

## Status

**PROPOSED — locked design, pending advisor 2nd-pass confirmation BEFORE code.**

## Pivot history (this session)

```
v0 (morning):  Hasan 2022 4-layer ladder + UncResCEO×log(PRisk) interaction.
               KILLED — type-redundant w/ H1.2/H1.3 modus tollens.

v1 (PM-1):     HighPRisk_pre × Post(Trump 2016) DiD on Cash.
               KILLED by advisor — 6 findings.

v2 (PM-2):     BothHigh × Post(Trump 2016) DiD + Cash + Speech parallel.
               REVISED — addresses 5 of 6 advisor findings.

v3 (PM-3):     ⭐ THIS DOC. Add SECOND parallel layer: Hasan 2022 
               redistricting DiD with our speech rerun. Two-layer evidence 
               stack on the SAME thesis claim.
```

## Design class

**TWO parallel DiD layers, each tested on cash AND speech outcomes:**

```
LAYER A — H1.4 Trump 2016 DiD
  Shock:           2016 US presidential election (unexpected)
  Treatment:       BothHigh trade × tax exposure (5-yr pre-window)
  Outcome 1:       Cash (cheq/atq) — replicates Hasan-style w/ new shock
  Outcome 2:       UncResCEO — NEW (load-bearing novelty)

LAYER B — H1.5 Redistricting DiD (Hasan 2022 Layer 2 replication + extension)
  Shock:           2010 decennial census redistricting (politicians redrew 
                   congressional district boundaries 2011-2013)
  Treatment:       Treated_i = +1 / 0 / −1 per Hasan 2022 verbatim 
                   (district PRisk profile rose / unchanged / fell)
  Outcome 1:       Cash (cheq/atq) — replicates Hasan 2022 Layer 2 verbatim
  Outcome 2:       UncResCEO — NEW (load-bearing novelty for redistricting)
```

## Anchor citations

### Tier 0 — design template
**Hu, Kang, Li, Lin (2024).** *Review of Accounting Studies* 30(1). DOI: 10.1007/s11142-024-09843-7. (Trump 2016 DiD template for H1.4.)

### Tier 0 — replication anchor (H1.5)
**Hasan, Alam, Paramati, Islam (2022).** *Review of Quantitative Finance and Accounting* 59(1). DOI: 10.1007/s11156-022-01049-9. (Layer 2 redistricting DiD template for H1.5.)

### Tier 1 — PRisk construct + 8 sub-topics
**Hassan, Hollander, van Lent, Tahoun (2019).** *QJE* 134(4). DOI: 10.1093/qje/qjz021.

### Tier 2 — Trump-2016 corp-finance template
**Wagner, Zeckhauser, Ziegler (2018)** *JFE*.

## H1.4 — Trump 2016 DiD spec

### Treatment definition (PRE-FIXED)

```
For each firm i in F1D panel:
  trade_i = mean(PRiskT_trade) over Q4 2011 – Q3 2016 (20 quarters)
  tax_i   = mean(PRiskT_tax)   over Q4 2011 – Q3 2016 (20 quarters)

For each FF12 industry j:
  trade_med_j = median(trade_i for firms in industry j)
  tax_med_j   = median(tax_i   for firms in industry j)

TREATED:  BothHigh_i = 1 if (trade_i ≥ trade_med_j) AND (tax_i ≥ tax_med_j)
CONTROL:  BothLow_i  = 1 if (trade_i <  trade_med_j) AND (tax_i <  tax_med_j)
DROPPED:  off-diagonal (~21% of sample)

EXCLUSIONS (per Hasan 2022):
  • SIC 6000-6999 (financials)
  • SIC 4900-4999 (utilities)
```

### Sample period for the regression
```
Q3 2014 – Q4 2018 (Hu 2024 cutoff window — avoids 2019 trade war + COVID).
Pre-period:  Q3 2014 – Q3 2016
Post-period: Q4 2016 – Q4 2018 (Q4 2016 = Trump elected)
```

### Headline regression (canonical TWFE-DiD form)

```
Run 1 (Cash):
  Cash_{i,t} = β·BothHigh_i × Post_t + θ·Bates_2009_controls
             + Firm_FE + YearQuarter_FE + ε_{i,t}

Run 2 (Speech) — load-bearing novelty:
  UncResCEO_{i,t} = β·BothHigh_i × Post_t + θ·Bates_2009_controls
                  + Firm_FE + YearQuarter_FE + ε_{i,t}
```

### Empirical sizes (verified 2026-05-05 PM)
- F1D firms with 5-yr pre-window data: 2,037
- Treated (BothHigh): ~814 firms (panel-wide median; FF12 will be similar)
- Control (BothLow): ~813 firms
- Off-diagonal dropped: ~410 firms
- Trade × tax correlation at firm-level: 0.515

### Data status: ALL ON DISK ✓
- `inputs/FirmLevelRisk/firmquarter_2022q1.csv` — 8 sub-topic PRisk vars verified
- `inputs/Compustat_Quarterly_OCF_Extended/` — Cash + Bates controls
- `inputs/CRSPCompustat_CCM/` — gvkey crosswalk
- Existing pipeline: UncResCEO already extracted

## H1.5 — Redistricting DiD spec (Hasan 2022 Layer 2 replication + speech extension)

### Treatment definition (per Hasan 2022 verbatim)

```
For each firm i in F1D panel with HQ ZIP at time of redistricting:
  district_pre_2011_i  = congressional district containing HQ ZIP under 
                         old map (post-2000 Census)
  district_post_2011_i = congressional district containing HQ ZIP under 
                         new map (post-2010 Census)

For each district d:
  PRisk_district_d = aggregate firm-level PRisk for firms in district d
                     (mean or median across firms in d)

Treated_i = +1 if PRisk_district_post_i > PRisk_district_pre_i  (PRisk rose)
Treated_i =  0 if district unchanged OR PRisk profile unchanged
Treated_i = −1 if PRisk_district_post_i < PRisk_district_pre_i  (PRisk fell)

Post_t = 1 if year > 2011, else 0.

EXCLUSIONS (per Hasan 2022):
  • SIC 6000-6999 (financials)
  • SIC 4900-4999 (utilities)
```

### Sample period
```
2008-2014 (Hasan 2022's redistricting DiD window).
Pre:  2008-2010
Post: 2012-2014 (2011 = transition year, often excluded or interpolated)
```

### Headline regression (Hasan 2022 verbatim spec)

```
Run 1 (Cash) — Hasan 2022 Layer 2 replication:
  Cash_{i,t} = β·Treated_i × Post_t + θ·Bates_2009_controls
             + Firm_FE + YearQuarter_FE + ε_{i,t}

Run 2 (Speech) — NEW load-bearing novelty:
  UncResCEO_{i,t} = β·Treated_i × Post_t + θ·Bates_2009_controls
                  + Firm_FE + YearQuarter_FE + ε_{i,t}
```

### Data acquisition required ⚠ NOT ON DISK
```
1. Firm HQ ZIP code per quarter
   - Compustat has `addzip` field (verify availability in 
     inputs/Compustat_Quarterly_OCF_Extended)
   - If unavailable, may need supplementary CRSP / FactSet HQ data

2. ZIP-to-congressional-district crosswalk pre-2011
   - US Census Bureau TIGER/Line shapefiles (113th Congress for 
     pre-2013, 112th for pre-2011)
   - Free, public-domain
   - Estimate: 2-3 days to build crosswalk

3. ZIP-to-congressional-district crosswalk post-2011
   - US Census Bureau TIGER/Line (114th Congress and later)

4. District-level PRisk
   - Aggregate firm-level Hassan PRisk to district level
   - Compute district-mean PRisk pre vs post

ESTIMATE: 1-2 weeks engineering before regression-ready panel.
```

### Empirical scope (uncertain until data acquired)
- Treated subset: ~30-40% of F1D firms (firms in states with significant 2010 redistricting changes)
- Sample size: ~700-900 F1D firms expected (sub-sample vs Trump's larger sample)

## Why both layers? (the marginal contribution argument)

```
Each layer answers a different identification critique:

  H1.4 Trump 2016:        Strong shock recency + clear treatment narrative
                          Critique it answers: "Is this Trump-relevant?"
                          Answer: yes — BothHigh trade × tax = exact Trump
                          policy bundle exposure.
                          
  H1.5 Redistricting:     Strong published precedent (Hasan 2022 Layer 2)
                          Critique it answers: "Is this design valid?"
                          Answer: yes — exact Hasan replication.

Together: BOTH critiques answered. The two layers are independently 
identified shocks; replicating across them = stronger evidence than 
either alone.

Speech regression on BOTH = double-novelty (no one ran speech on either 
shock before).
```

## Why β1, β3 are NOT in any spec (advisor #1 BLOCKING)

Same as v2: TWFE-DiD form. Time-invariant treatment dummy collinear with Firm_FE; period-only Post collinear with YearQuarter_FE. Only the interaction is estimable. Document absorption in table footnote.

## Theoretical framing — STORY B (locked)

```
Underlying precautionary stress (latent state)
              │
   ┌──────────┼──────────┐
   ▼          ▼          ▼
   Speech    Cash       (other
   ↑         ↑          indicators)
   
Activated by EITHER:
  (a) Trump 2016 election — H1.4
  (b) 2010 redistricting — H1.5

Story B: speech is INDICATOR, not CAUSE, of cash decisions. 
Both shocks should activate BOTH outcomes if Story B holds.
```

## Reverse-causality kill (both layers)

```
H1.4 Trump 2016:
  Trump 2016 unexpected (Wolfers-Zitzewitz pre-mkts: Clinton ~70%).
  Pre-fixed treatment label (5-yr 2011-2016 mean BEFORE shock).
  → Forward arrow only.

H1.5 Redistricting:
  Politicians redrew district lines (2010 Census + state legislatures).
  Firm cash/speech decisions cannot reach back in time to redraw maps.
  → Forward arrow only.

Both layers independently kill reverse causality. 
TWO independent identification angles on the SAME thesis claim.
```

## Required robustness layers (per layer)

```
For BOTH H1.4 and H1.5:
  1: Baseline DiD                     (the headline regression)
  2: Parallel pre-trends test         must be insignificant
  3: 1:5 matching                     (Hu 2024 method for H1.4; 
                                       Hasan 2022 for H1.5)
  4: Pseudo-treatment dates           placebo must be null
  5: Alternative cash measure         (cheq+ivst−debt)/atq
  6: Channel-control regressions      rule out trade/tax/etc. 
                                       confounders
  7: ⭐ Speech parallel regression    load-bearing novelty
  8: CEO turnover restriction         drop firms changing CEO 
                                       in event window

H1.4-specific:
  9: Window robustness                re-run with 2yr, 8yr 
                                       treatment-label windows
  10: Single-topic robustness         HighTrade alone | HighTax alone
  11: Triple-difference (DDD)         keep all 4 cells

H1.5-specific:
  12: District-level PRisk aggregation  alternatives 
                                       (mean / median / weighted)
  13: 2SLS using PCI as IV             (per Hasan 2022 Layer 3) — 
                                       optional bonus layer
```

## Marginal contribution (now triple-stacked)

```
Hasan 2022 published:
  Redistricting → Cash (Layer 2)
  PCI-IV → Cash (Layer 3)
  PSM → Cash (Layer 4)
  
Our extensions:
  H1.4 Trump 2016 → Cash         (different shock — replication)
  H1.4 Trump 2016 → Speech       ⭐ NEW
  H1.5 Redistricting → Speech    ⭐ NEW (extends Hasan's exact Layer 2)
  
"Speech regression on TWO different exogenous shocks, both identifying 
joint co-movement of speech and cash post-shock, consistent with 
Story B's joint-indicator framing."
```

## §V text reconciliation (NOW BIGGER per both layers)

Current §V conclusion verbatim:
> "we acknowledge as a limitation that no exogenous-shock or instrumental-variable identification is pursued"

Required §V edit:

```
Replace:  "we acknowledge as a limitation that no exogenous-shock or 
           instrumental-variable identification is pursued"

With:     "We pursue auxiliary heterogeneity tests using two independent 
           plausibly-exogenous shocks: the 2016 US presidential election 
           and the 2010 decennial congressional redistricting (§III.E.4). 
           Both tests confirm that politically-exposed firms exhibit 
           JOINT post-shock movement in both speech uncertainty and cash 
           holdings, consistent with the indicator framing developed in 
           §II. We do not claim a causal bridge from speech to cash; 
           the designs identify each SHOCK's effect on a precautionary 
           state of which speech and cash are joint indicators."
```

## New code modules required

```
H1.4 (Trump 2016):
  src/f1d/shared/variables/political_risk.py        — Hassan PRisk merge + BothHigh
  src/f1d/variables/build_h1_4_prisk_did_panel.py   — H1.4 panel builder
  src/f1d/econometric/run_h1_4_prisk_did.py         — H1.4 DiD runner

H1.5 (Redistricting):
  src/f1d/shared/variables/redistricting.py         — district crosswalk + 
                                                       Treated +1/0/-1 label
  src/f1d/variables/build_h1_5_redistricting_panel.py — H1.5 panel builder
  src/f1d/econometric/run_h1_5_redistricting_did.py   — H1.5 DiD runner

Common:
  config/suite_render_order.yaml                     — add H1.4 + H1.5
```

## Suite IDs

- **H1.4** — Trump 2016 DiD on Cash + Speech
- **H1.5** — Redistricting DiD on Cash + Speech (Hasan 2022 Layer 2 replication + extension)

## Honest design limits (to disclose in §III.E.4 prose)

```
1. The DiDs identify each SHOCK's joint effect on cash AND speech for 
   exposed firms. They do NOT formally identify mediation through speech 
   (Imai-Tingley-Yamamoto 2010 framework would be required; we do not 
   use it).

2. Co-movement of UncResCEO and Cash post-shock is "consistent with" 
   the indicator-of-shared-stress story but does NOT "prove" mediation.

3. Channel competitors are partially ruled out via Layer 6 controls; 
   cannot all be eliminated.

4. The two layers add INDEPENDENT angles to the existing endo defense 
   stack (firm FE + lagged DV + lead DV + H1.2/H1.3 modus tollens 
   + Lewbel IV + DWZ FD).

5. H1.4 Trump 2016: DiD captures TRUMP'S effect on BothHigh firms — 
   NOT effect of "political risk" or "speech uncertainty" in isolation.

6. H1.5 Redistricting: DiD captures REDISTRICTING'S effect on firms 
   whose district reassignment changed local PRisk profile — NOT a 
   universal claim about all firms.

7. Treatment labels in both layers are pre-fixed at exposure measured 
   BEFORE shock; firms that pivoted post-shock still get labeled by 
   pre-shock exposure.
```

## Decision pending from user

```
A) Approve revised v3 spec → proceed to advisor 2nd pass + prototype
B) Build H1.4 first (data-ready), defer H1.5 until data acquired
C) Build BOTH in parallel (data-acquisition for H1.5 starts now)
D) Pause and think — sleep on it
```

## Cross-references

- `tmp/trump2016_did_lit_review_2026_05_05_part2.md` — full lit review report
- `memory/project_session_2026_05_05_pm_design_pivot.md` — session journey
- `memory/reference_hu_kang_li_lin_2024_verbatim.md` — Hu DiD verbatim (H1.4)
- `memory/reference_hasan_alam_paramati_islam_2022_verbatim.md` — Hasan 2022 verbatim (H1.5)
- `memory/reference_hassan_hollander_vanlent_tahoun_2019_verbatim.md` — PRisk + 8 sub-topics verbatim
- `memory/project_dwz_anchored_framing_locked_2026_04_27.md` — Story B framing precedent
- (Empirical data check) `inputs/FirmLevelRisk/firmquarter_2022q1.csv` — confirmed all 8 sub-topics + 98.6% F1D coverage 2026-05-05 PM
