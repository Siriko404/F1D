# H1.5 — 3-DiD Design Search — Progress Log

**Session:** 2026-05-08 (post-compaction continuation)
**Mission:** Identify 3 verbatim-replicable DiD designs for §III.E.4 endo-defense layer.
**Constraint:** H1.6 Hasan-redistricting stays AS-IS; need 3 NEW DiDs alongside it.

---

## STATE BLOCK (read first)

```
SLOTS                                      STATUS
─────────────────────────────────────────────────────────────────
[#1] Brexit (Campello 2022 JFQA)           ✓ VERIFIED + ACCEPTED
[#2] Boasiako 2020 EFM Data Breaches       ✓ VERIFIED + ACCEPTED
[#3] Chen 2017 JAAF Restatements           ✓ ACCEPTED 2026-05-08
                                             firm-specific shock fallback;
                                             closes search after 8 NLM rounds

SEARCH CLOSED. 3-tier shock hierarchy:
   #1 = MACRO international policy (Brexit referendum 2016)
   #2 = STATE-LEVEL US legal regime (data-breach disclosure laws)
   #3 = FIRM-SPECIFIC US idiosyncratic event (irregularity restatements)

VERIFIED + KILLED                          REASON
─────────────────────────────────────────────────────────────────
Javadi 2023 FM Climate                     country-level (DROUGHT_TREND
                                            "only time series within country")
Ghaly 2017 RFS Katrina                     opposite polarity (cash DOWN
                                            β = -0.047** Houston*Post)
Campbell 2025 RAST TCJA                    Faulkender-Wang valuation,
                                            NOT level-DID
De Simone 2018 RFS Repatriation            tax-arbitrage mechanism
                                            NOT precautionary; Q7 NLM:
                                            "precautionary channel test
                                            NOT IN PAPER"
Berg 2018 RFS Got Rejected?                German private SMEs via
                                            Bureau van Dijk DAFNE;
                                            no US public-firm sample
Chen 2017 JAAF Restatements                firm-specific shock (mechanism
                                            partial mismatch with macro
                                            Story B); FALLBACK ONLY

DROPPED on abstract evidence (no NLM round needed)
─────────────────────────────────────────────────────────────────
Graham-Huang-Yang 2024 (TPU)               OLS not DiD per own abstract
                                            "ordinary least squares 
                                            regression"

Master HEAD @ 721b0f7  (lit-search artifacts; no code changes)
F1D window CORRECTED: 2002-01-16 to 2018-12-22 (NOT 2002-2021)
```

---

## SEARCH PASSES — CUMULATIVE

| Pass | Strategy | Papers | Result |
|------|----------|--------|--------|
| v1   | Trump+cash+DiD keyword (17 queries) | 223 | 0 hits |
| v2   | Citation chase 4 anchors | 902 | 0 hits |
| v3   | Relaxed (no DiD required) | 492 | 3 title hits, all OLS or invalid |
| v4   | Broad shock-DiD-cash-precautionary (27 queries + 6 anchors) | 1,779 | 10 cash+DiD+prec, 4 verified |
| v5   | Refined (50 queries + 8 anchors, polarity-sentinel filter) | 2,207 | Strict filter killed too many; loosened to 47 cash+broader-DiD; 16 tier-A, 4 NEW strong candidates |

---

## v5 NEW CANDIDATES SURFACED (was not in v4)

```
[#1 SLOT — already filled by Brexit]

[#2 NEW] Boasiako, O'Connor Keefe 2020 EFM
   "Data Breaches and Corporate Liquidity Management"
   DOI: 10.1111/eufm.12289
   Why missed in v4: EFM not in v4 anchor citation chase + 
   "data breach" keyword not in v4 query set
   
[REJECTED] De Simone, Piotroski, Tomy 2018 RFS
   "Repatriation Taxes and Foreign Cash Holdings"
   DOI: 10.1093/rfs/hhy124
   Why missed in v4: TCJA-anticipation framing not in v4 queries
   NLM verdict: tax-arbitrage mechanism not precautionary
   
[REJECTED] Berg 2018 RFS "Got Rejected?"
   DOI: 10.1093/rfs/hhy038
   Why missed in v4: lender-cutoff RDD not in v4 query set
   NLM verdict: German private SME loan data, no US public-firm sample
   
[#3 PENDING] Chowdhury, Doukas, Park 2021 JCF
   "Stakeholder Orientation and the Value of Cash Holdings"
   DOI: 10.1016/j.jcorpfin.2021.102029
   Why missed in v4: empty abstract caused filter miss
   Status: PDF uploaded to NLM, Q1 query drafted, awaiting answers
```

---

## F1D WINDOW CORRECTION (CRITICAL FIX)

```
PRIOR CLAIM (session-long error):  2002-2021
ACTUAL DATA-VERIFIED RANGE:        2002-01-16 → 2018-12-22

Source of truth: outputs/variables/h1_cash_holdings/2026-04-19_182724/
                 h1_cash_holdings_panel.parquet
                 N=112,968 calls, start_date column

Implication: drop all post-2018 shocks from v5 (COVID, Russia-Ukraine, 
SVB) and any 2018-onwards shocks have only ≤4 quarters post-window.

Memory.md still says 2002-2021 in some entries — needs update at 
next durable-write opportunity.
```

---

## TURN-BY-TURN LOG

### TURN 1 — Compaction recap

User asked "where are we" post-compaction. State recap delivered.

### TURN 2 — Chen 2017 PDF re-upload

User reuploaded full Chen 2017 JAAF PDF (prior PDF had been incomplete).
Drafted Q1 (10 questions) for NLM.

### TURN 3 — Chen Q1 results

NLM returned full verbatim. Key facts:
- Sample 1997-Jun 2006 (F1D-overlap = 4 yrs)
- 270 irregularity restatements
- DiD: POST × Treated firm with PSM 1:1 no-replacement
- DV = CHE/AT
- Industry excl SIC 6000-6999 + 4900-4999
- HEADLINE β_DiD = +0.034 (p=.002)
- Channel: PS_DEMAND high vs low partition (precautionary verbatim)
- Pseudo-event placebo ✓

Drafted Q2 (7 questions) for NLM.

### TURN 4 — Chen Q2 results + verdict

NLM Q2 surfaced channel-competitor handling + missing items:
- Q12: ✓ CEO/CFO turnover partition shown (effect ONLY in firms 
  WITHOUT turnover) — supports precautionary
- Q12: ✗ Credit-rating, financing access, regulator — NOT IN PAPER
- Q13: ✗ NO CEO speech/disclosure analysis
- Q15: ✗ No alternative robustness (entropy, Heckman, IV)

Verdict: replicable but mechanism mismatch (firm-specific vs macro).
Marked as FALLBACK candidate.

### TURN 5 — User asked about 3-DiD scope

User clarified: H1.6 stays separate, need 3 NEW DiDs.
Brexit confirmed for #1.

### TURN 6 — DOI extraction for next batch

Read v3+v4 candidate reports. Identified:
- Graham 2024 (TPU): OLS per abstract, KILL without NLM
- Campbell 2025 RAST: TCJA, top-tier
- Manakyan 2021: TCJA, lower-tier
- Ghaly 2017 RFS: 264 cites, "quasi-experimental shock to labor 
  markets" — NEW STRONG candidate

User picked top 2 by criteria match: Ghaly + Campbell.

### TURN 7 — Q1 drafted for Ghaly + Campbell

10 questions Ghaly, 12 questions Campbell. Sent to user.

### TURN 8 — Ghaly + Campbell Q1 results

**Ghaly (Q1 verbatim):**
- Sample 1999-2012 (F1D overlap 2002-2012)
- HEADLINE Houston*Post = -0.047** ← OPPOSITE POLARITY
- Mechanism: Katrina labor INFLOW reduces precautionary need
- Q9 CEO communication NOT IN PAPER

→ KILL on opposite polarity mismatch

**Campbell (Q1 verbatim):**
- Q2: "marginal value of cash by following Faulkender and Wang (2006)"
- Q3: sub-period split, NOT treatment×post DiD
- Q4: NOT IN PAPER (no treated/control)
- Q7: NOT IN PAPER (no precautionary test)
- Q11: MNC-only sample

→ KILL: valuation not level-DID

### TURN 9 — User asked "is Brexit verified, correct?"

Confirmed. Status pool re-stated. User asked for 3 BEST = Brexit (✓) 
+ 2 more. Discussed scope: H1.6 stays separate, 3 NEW DiDs needed.

### TURN 10 — User wanted v5 OpenAlex search

Drafted v5 strategy + criteria. User confirmed:
- Polarity-sentinel filter: drop opposite-polarity hits
- DV scope: cash holdings only (CHE/AT)

### TURN 11 — User flagged sample-period error

User: "check our sample period again. i have a feeling you got it wrong"

Programmatic check of h1_cash_holdings_panel.parquet:
- start_date: 2002-01-16 → 2018-12-22
- NOT 2002-2021 as claimed throughout session

Critical fix. Re-revised v5 query set to drop post-2018 shocks 
(COVID, Russia-Ukraine, SVB) and add pre-2018 shocks (debt-ceiling, 
shutdown 2013, fiscal cliff, Eurozone, oil 2014, financial crisis 
2008, etc.).

### TURN 12 — v5 ran

50 queries + 8 anchors → 2,207 unique papers
Strict filter: cash + DiD + precautionary + positive-polarity + 
macro-shock + US-only → 0 papers
Loosened to cash + broader-DiD/shock/IV: 47 papers, 16 tier-A

NEW STRONG candidates surfaced:
- Boasiako 2020 EFM (Data Breaches) — cleanest match
- De Simone 2018 RFS (Repatriation) — top-tier
- Berg 2018 RFS (Got Rejected?) — top-tier
- Beuselinck 2021 JCF (Employee Protection) — top-tier
- Chowdhury 2021 JCF (Stakeholder Orientation) — top-tier

### TURN 13 — Boasiako + De Simone uploaded

User: "your call" on top 2. I picked Boasiako (best criteria match) 
+ De Simone (top-tier RFS, MNC-only caveat).

Q1 drafted for both.

### TURN 14 — Boasiako + De Simone Q1 results

**Boasiako (Q1 verbatim):**
- Sample 1997-2015 (F1D overlap 2002-2015 = 14 yrs CLEAN)
- Industry excl SIC 6000-6999 + 4900-4999 ✓
- DV = cash + ST securities / AT
- DiD: Disclosure_Law(0/1)_{s,t} HQ-state-based
- HEADLINE β = +0.0076** (SE 0.0031) ✓ POSITIVE
- N = 56,646 firm-years
- Pre-trends + falsification + entropy balancing ✓
- Channel: financial constraint partition ✓
- FE: state + year + industry + firm
- SE state-cluster
- Q11: Col 4 explicitly excludes 2007-2009 financial crisis

→ ACCEPT for slot #2 — ALL 6 criteria satisfied + bonus channel + 
  bonus identification checks

**De Simone (Q1 verbatim):**
- Q1: sample bounds NOT IN PAPER (only "end of 2008")
- Q2: legislative events 2008-2011
- Q3: Pr(repatriate) × ΔPeriod design
- Q5: Cash = total cash + ST securities + LT investments / AT
- Q7: precautionary channel test NOT IN PAPER ← FATAL
- Q11: CEO communication NOT IN PAPER
- HEADLINE Pr(repat)×2009=+0.048***, ×2010=+0.055***, 
  ×2011=+0.074*** ← POSITIVE escalating

→ REJECT for slot #3 — mechanism = TAX-DEFERRAL ARBITRAGE, 
  NOT precautionary uncertainty response

### TURN 15 — Berg uploaded

User: "Verify Berg 2018 RFS — Recommended"

Q1 drafted: 12 questions probing geography + sample-type + 
data-source compatibility with F1D.

### TURN 16 — Berg Q1 results

**Berg (Q1 verbatim):**
- Q1: "16,855 SME loan applications from 13,484 firms between 
  2009 and 2012 from a major German bank"
- Q4: "Bureau van Dijk's DAFNE database... Compustat NOT IN PAPER"
- Q12: "NOT IN PAPER. The entire analysis is restricted to 
  private-SMEs"
- Mechanism perfect match: Q6 verbatim "consistent with 
  PRECAUTIONARY MOTIVES narrative... inconsistent with 
  alternative narratives"
- HEADLINE β = +0.025** (low-liquidity column)

→ REJECT for slot #3 — DATA SOURCE INCOMPATIBLE with F1D 
  (German private SMEs via Bureau van Dijk vs F1D's CRSP/Compustat 
  US public firms)

### TURN 17 — Chowdhury 2021 JCF chosen

User: "Verify Chowdhury 2021 JCF Stakeholder Orientation — Recommended"

Authors: Chowdhury (Old Dominion), Doukas (Old Dominion), 
Park (Suffolk) — US-based authors → US data likely.

Awaiting PDF upload + Q1 draft.

### TURN 18 — Progress recording (this turn)

User: "record our progress in detail step by step as we proceed"

Created this progress log. Will update at each turn going forward.

### TURN 19 — Chowdhury Q1 results

NLM returned full verbatim. Four independent fatal facts:

**Q3 verbatim:** PRIMARY design = Faulkender-Wang excess-return regression
"applying the regression model developed by Faulkender and Wang (2006)... 
excess stock return is regressed on changes in cash"
Level-DiD (Eq. 5) only secondary in §4.9.

**Q8 verbatim:** OPPOSITE polarity
"the level of cash holdings DECREASES after the adoption of constituency 
statutes, suggesting that strong stakeholder monitoring REDUCES agency 
costs and subsequently LIMITS cash holdings"

**Q7 verbatim:** INVERSE Story B mechanism  
"stakeholder orientation alleviates short-termism and thus REDUCES 
firms' operating risks and PRECAUTIONARY cash holdings"

**Q10 verbatim:** ZERO identification checks
parallel-trends, pre-trend placebo, placebo dates, PSM, entropy, IV — 
ALL "NOT IN PAPER"

→ REJECT for slot #3.

### TURN 20 — Chen 2017 accepted as fallback #3

User picked "Accept Chen 2017 JAAF as #3" (Recommended).

Rationale framing: 3 DiDs as 3-tier shock-scale hierarchy
   #1 Brexit            = macro international policy (2016-Q3)
   #2 Boasiako          = state-level US legal regime (1997-2015 staggered)
   #3 Chen Restatements = firm-specific US accounting events (1997-2006)

All 3 share precautionary mechanism. Chen is firm-event scale; Brexit 
+ Boasiako are macro/regional scale. Together they triangulate 
Story B at multiple shock-scale levels.

SEARCH CLOSED. 8 NLM rounds total (Chen Q1+Q2, Ghaly Q1, Campbell Q1, 
Boasiako Q1, De Simone Q1, Berg Q1, Chowdhury Q1).

### TURN 21 — Durable-write phase (memory + reference files + commit)

User: "Update memory + commit progress log first" (Recommended).

Files written:
  + memory/reference_campello_etal_2022_brexit_jfqa_verbatim.md  
    (NLM Q1+Q2 verbatim from prior session's tmp/h1_5_trump_cash_did_lit_search.md
     extracted into structured reference format; replication checklist added)
  + memory/reference_boasiako_oconnor_keefe_2020_efm_verbatim.md
    (NLM Q1 verbatim from this session turn 14; replication checklist)
  + memory/reference_chen_etal_2017_jaaf_restatement_verbatim.md
    (NLM Q1+Q2 verbatim from prior session + this session turn 3-4;
     replication checklist; CEO/CFO turnover channel partition noted)
  + memory/project_session_2026_05_08_3did_lineup_locked.md
    (NEW NEWEST session memory; supersedes prior brexit_pivot file)
  M memory/MEMORY.md
    (top entry rewritten; 3 reference files added near hasan/hu/akyol refs;
     prior brexit_pivot demoted to PREDECESSOR)

Git commit 6a91645 "H1.5 v5 OpenAlex search + 8-NLM-rounds verdict — 
3-DiD lineup LOCKED":
  + tmp/openalex_lit_search_v5.py
  + tmp/openalex_v5_results.csv
  + tmp/openalex_v5_top.md
  + tmp/h1_5_3_did_search_progress_2026_05_08.md
  4 files, 3,253 insertions.

### TURN 22 — Plan deletion + compaction prep

User: "no need for updating the plan. delete it. get ready for compaction 
extremely thoroughly".

Action:
  1. DELETED ~/.claude/plans/tender-popping-origami.md (stale; referenced
     dead Trump-2016 BothHigh×Post spec; H1.6 Phase 5 TEST 3+5 already
     superseded by 813d735 ship state).
  2. Updated this progress log + session memory file with compaction
     readiness checklist.
  3. Verified durable state.

COMPACTION READINESS:

```
[✓] tmp/h1_5_3_did_search_progress_2026_05_08.md        committed @ 6a91645
[✓] memory/project_session_2026_05_08_3did_lineup_locked.md  durable
[✓] memory/reference_campello_etal_2022_brexit_jfqa_verbatim.md durable
[✓] memory/reference_boasiako_oconnor_keefe_2020_efm_verbatim.md durable
[✓] memory/reference_chen_etal_2017_jaaf_restatement_verbatim.md durable
[✓] memory/MEMORY.md top entry replaced + 3 ref entries added
[✓] git committed (master @ 6a91645)
[✓] stale plan deleted (was: tender-popping-origami.md)
```

POST-COMPACT NEXT ACTIONS:
   1. User picks first DiD to implement (Brexit / Boasiako / Chen)
   2. Implementation follows 3 reference verbatim files (per-DiD
      replication checklist embedded in each reference file)
   3. Total estimated effort 12-19 days for full 3-DiD ship
   4. §V update A/B/C choice (carry from 2026-05-06 session) STILL deferred

---

## NLM VERIFICATION VERDICT TABLE

| # | Paper | Year | Venue | Cites | Verdict | Reason |
|---|-------|------|-------|-------|---------|--------|
| 1 | Brexit Campello | 2022 | JFQA | 66 | ✓ ACCEPT #1 | All criteria; Trump-2016 contamination addressable |
| 2 | Boasiako Data Breaches | 2020 | EFM | 64 | ✓ ACCEPT #2 | All 6 criteria + bonus channel + bonus IDs |
| 3 | Chen Restatements | 2017 | JAAF | 11 | ⚠ FALLBACK | Mechanism partial match; firm-specific |
| 4 | Javadi Climate | 2023 | FM | 134 | ✗ KILL | DROUGHT_TREND country-level |
| 5 | Ghaly Katrina | 2017 | RFS | 264 | ✗ KILL | Opposite polarity (cash DOWN) |
| 6 | Campbell TCJA | 2025 | RAST | 0 | ✗ KILL | Faulkender-Wang valuation, not level |
| 7 | De Simone Repatriation | 2018 | RFS | 53 | ✗ KILL | Tax-arbitrage not precautionary |
| 8 | Berg Got Rejected? | 2018 | RFS | 87 | ✗ KILL | German private SMEs (data incompatible) |
| 9 | Chowdhury Stakeholder | 2021 | JCF | 39 | ✗ KILL | Faulkender-Wang primary; cash DECREASES; zero IDs |

---

## PATTERN OBSERVATIONS (lessons from 7 NLM rounds)

1. **Mechanism dimension was missing from v4 filter** — only added to 
   pre-NLM screen for v5+. Three papers (De Simone, Ghaly, Berg) 
   passed criteria 1-5 but failed mechanism dimension.

2. **Empty abstracts in OpenAlex are a critical limitation** — both 
   Beuselinck and Chowdhury had empty abstracts; could only be 
   evaluated via NLM Q1.

3. **"Top-tier" venue ≠ replicable for our F1D** — Berg RFS 87 cites 
   has perfect mechanism match but data source (German SMEs) makes 
   it non-replicable. Tier alone isn't predictive.

4. **Polarity-sentinel filter cannot rely on abstracts** — Ghaly's 
   abstract uses "precautionary" extensively but coefficient is 
   negative; only NLM Q7 verbatim revealed the direction.

5. **"DiD" can mask many design types** — Faulkender-Wang valuation 
   regressions appear in cash-DiD search results because they use 
   pre/post comparisons but are not level-DID on cash.

---

## REMAINING UNINVESTIGATED CANDIDATES (post-Chowdhury)

```
Beuselinck 2021 JCF "Employee Protection"      48 cites
   Authors French/Italian/Belgian → likely European
   Probability of US sample: low

Other v5 tier-A pool entries (already evaluated as KILL):
   - Worldwide board reforms (non-US)
   - Sharing the Pain (Portuguese)
   - Curbing Shocks JPE (Sweden)
   - Cross-border MMoU (cross-listed foreign)
```

If Chowdhury fails:
- Option A: accept Chen as fallback #3 (mechanism partial match)
- Option B: 2 DiDs only (Brexit + Boasiako) + Chen as appendix

---

## SEARCH CLOSED — FINAL 3-DID LINEUP

```
[#1] BREXIT (Campello-Cortes-d'Almeida-Kankanhalli 2022 JFQA)
─────────────────────────────────────────────────────────────────
  Suite ID:        H1.5.brexit_did
  Shock:           UK Brexit Referendum (June 23 2016)
  Treatment:       HIGH_β^UK or HIGH_10K_ENTRIES (US firms with UK exposure)
  Window:          2016:Q3-Q4 vs 2015:Q3-Q4
  Cash result:     β = +0.231 to +0.357 SE 0.06 *** (Campello)
  Channel:         precautionary verbatim
  ID checks:       formal parallel-trends + 2 placebo dates
  Trump-2016:      contamination addressed via (i) drop Q4 2016 
                   (ii) drop Wagner-Zeckhauser-Ziegler "Trump losers"
  Speech extension: NEW — UncResCEO parallel regression
  
[#2] DATA BREACHES (Boasiako-O'Connor Keefe 2020 EFM)
─────────────────────────────────────────────────────────────────
  Suite ID:        H1.5.databreach_did  (or H1.7?)
  Shock:           Staggered state-level data-breach disclosure laws 
                   (CA SB 1386 = 2002 first; ~50 states 2003-2018)
  Treatment:       HQ-state firm × Disclosure_Law(0/1)_{s,t}
  Window:          1997-2015 (paper); F1D-overlap = 2002-2015 = 14 yrs
  Cash result:     β = +0.0076** SE 0.0031 (Boasiako Col 1)
  Channel:         financial constraint partition (Small/Young/Non-div)
  ID checks:       parallel-trends + falsification (random states) 
                   + entropy balancing
  FE:              state + year + industry + firm
  SE:              state-cluster
  Speech extension: NEW — UncResCEO parallel regression
  
[#3] RESTATEMENTS (Chen-Cheng-Lin-Tang 2017 JAAF)
─────────────────────────────────────────────────────────────────
  Suite ID:        H1.5.restatement_did  (or H1.8?)
  Shock:           Firm-specific irregularity restatement events 
                   (GAO data 2003-2006; events 1997-Jun 2006)
  Treatment:       PSM-matched 1:1 no-replace within FF48-industry; 
                   POST × Treated
  Window:          Year -3 to +3 around event
  Cash result:     β_DiD = +0.034 (p=.002) (Chen Table 3)
  Channel:         PS_DEMAND high vs low (CFvol+invest-vol+ACW corr)
  ID checks:       pseudo-event placebo + CEO/CFO turnover partition
  FE:              firm
  SE:              matched-pair × year cluster (Gow et al 2010)
  Caveat:          F1D overlap = 4 yrs; firm-specific shock not macro
                   (frame as "firm-event scale" of 3-tier hierarchy)
  Speech extension: NEW — UncResCEO parallel regression
```

## STORY B FRAMING — 3-TIER SHOCK HIERARCHY

```
Story B claim: CEO speech and cash holdings are JOINT INDICATORS 
              of an underlying precautionary state.

Test logic: identify EXOGENOUS shocks that activate precautionary 
            state, verify BOTH speech AND cash respond positively.
            
Triangulation across shock scales rules out mechanism artifacts:

   MACRO       international policy uncertainty   (Brexit)
        ↓ activates precautionary state via macro spillover
        ↓ BOTH speech UP + cash UP expected
        ↓
   STATE       US sub-national legal regime change  (data breach laws)
        ↓ activates precautionary state via legal/operational risk  
        ↓ BOTH speech UP + cash UP expected
        ↓
   FIRM        firm-event idiosyncratic shock      (restatements)
        ↓ activates precautionary state via own-firm credibility
        ↓ BOTH speech UP + cash UP expected
        
If all 3 layers show concordant positive cash + speech responses
to exogenous shocks, the precautionary-indicator interpretation 
of CEO speech (Story B) is robust to:
  • mechanism scale heterogeneity
  • cross-firm vs within-firm identification
  • macro vs micro shock identification claim
```

## NEXT PHASE — IMPLEMENTATION SCAFFOLD

```
Each DiD = NEW H suite. Three new suites total.

ENGINEERING SURFACE PER SUITE
─────────────────────────────────────────────────────────────────
[Brexit]    NEW data:    CRSP daily returns 2014-2016 + FTSE100 
                         daily returns 2014-2016 → β_i^UK
                         SEC EDGAR 10-K 2015 + Brexit-mention 
                         text counts → HIGH_10K_ENTRIES
            NEW builders: brexit_treatment_beta_uk.py + 
                          brexit_treatment_10k.py
            NEW runner:   run_h1_5_brexit_did.py
            
[Boasiako]  NEW data:    NCSL data-breach state-law passage dates 
                         + state crosswalk to Compustat addzip
            NEW builder:  databreach_law_treatment.py
            NEW runner:   run_h1_5_databreach_did.py
            
[Chen]      NEW data:    Hennes-Leone-Miller (2008) GAO restatement 
                         data; OR Audit Analytics restatement set
            NEW builders: restatement_event.py + 
                          ps_demand_index.py (CFvol+invest+ACW corr)
                          + psm_matching.py
            NEW runner:   run_h1_5_restatement_did.py

EDIT SHARED INFRA
─────────────────────────────────────────────────────────────────
  src/f1d/shared/variables/__init__.py       (5+ new exports)
  config/suite_render_order.yaml             (3 new suite IDs)
  docs/Draft/sections/section_3_main.tex     (§III.E.4 prose)
  docs/Draft/sections/section_5_conclusion.tex (rewrite §V text)

ESTIMATED EFFORT
─────────────────────────────────────────────────────────────────
  Brexit suite:     5-8 days (data acquisition is largest cost)
  Boasiako suite:   3-4 days (state-law crosswalk is small)
  Chen suite:       3-5 days (restatement data + PSM)
  Prose + render:   1-2 days
  ─────────────────────────────────────
  TOTAL:           12-19 days for full 3-DiD ship
```

## OUTSTANDING DURABLE-WRITE TASKS

```
[ ] Update memory/MEMORY.md current state entry
    (currently still says "i will decide after the compaction")
[ ] Update memory/project_session_2026_05_08_h1_5_brexit_pivot.md
    with corrected F1D window (2018 not 2021)
[ ] Update memory file with 8-NLM-rounds summary + 3-DiD lineup
[ ] Create reference files for verified anchors:
    [ ] memory/reference_campello_etal_2022_brexit_jfqa_verbatim.md
    [ ] memory/reference_boasiako_oconnor_keefe_2020_efm_verbatim.md
    [ ] memory/reference_chen_etal_2017_jaaf_restatement_verbatim.md
[ ] Plan v3 update (~/.claude/plans/tender-popping-origami.md):
    Replace H1.5 Trump-2016 BothHigh×Post with 3-DiD lineup
[ ] Commit v5 lit-search artifacts + this progress log to git
[ ] §V update A/B/C choice (carry from prior session) — defer

Will execute on user direction.
```
