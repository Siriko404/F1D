# Reference Stack Walkthrough — Step-by-Step Discussion Record

**Purpose:** durable record of the step-by-step construction of the thesis reference stack. Every claim in the thesis must map to one load-bearing paper, verified via primary source (NotebookLM verbatim or direct code read). This document records the walkthrough discussion.

**Session start:** 2026-04-16 evening.

**Scope:** Tier-1 load-bearing papers only. Tier-2 (supporting/validity) addressed in a single summary row per paper; their presence in F1D is already verified.

**Ground rules (per `feedback_literature_drives_hypotheses.md` + `feedback_notebooklm_mandatory.md` + anti-capitulation hook):**
- Every cited paper requires a verbatim quote from primary source (NotebookLM) OR direct code read (published replication repo) before it can appear in thesis prose.
- No acceptance of claims without firm diligent evidence.
- Step-by-step: user approval required between steps.

---

## Step 0 — Motivation and scope

Thesis v3 skeleton (`docs/Draft/THESIS_SKELETON.md`) lists 9+ papers in §2.3 (precautionary motive + financing conservatism) alone. Before writing any prose, we must verify which papers are actually in F1D NotebookLM, which have verbatim support, and which are load-bearing (critical) vs padding.

Initial stack audit (session earlier today):
- 4 papers explicitly queried for verbatim via NotebookLM: Grenadier 2002 (✓ 7 quotes), Aguerrevere 2009 (✓ 3 quotes, but venue flag: NotebookLM says JF, skeleton says RFS), BGT 2018 (✓ 3 quotes), then batched AFW 2004 + MW 2009 + SY 2013 which returned "NOT IN SOURCE" for three of four.
- Evidence gap revealed: §2.3's citation stack is larger than F1D's full-text coverage.

User challenge: "explain the final stack of references needed, and clearly explain WHY we need each. keep the stack minimal, yet 100% sufficient for supporting our thesis claims."

Response: built a 9-paper Tier-1 minimum critical list + Tier-2 supporting. Two uploads flagged (Minton-Wruck 2009 + Faulkender-Petersen 2006). AFW 2004 demoted (Bloom 2014 substitutes).

User redirect: "start explaining from beginning, proceed step by step, do not proceed until i approve. investigate thoroughly and ONLY THEN explain the step, grounded in truth."

That is this document.

---

## Step 1 — Foundational variable-construction papers (co-foundational: DWZ 2021 + BGT 2018)

### 1.0 Why these first

The thesis' entire independent-variable stack — UncAnsMgr, UncAnsCEO, UncPreMgr, UncPreCEO — has no existence without methodological precedent. These are the papers the IV rests on. Everything downstream (cash hypothesis, leverage hypothesis, HFC, etc.) presumes a defensible IV. If Step 1 fails, the thesis has no measure.

### 1.1 DWZ 2021 — Dzielinski, Wagner, and Zeckhauser

**Full cite:** Dzielinski, Wagner, and Zeckhauser (2021), "Straight Talkers and Vague Talkers: The Effects of Managerial Style in Earnings Conference Calls," M-RCBG Faculty Working Paper 2017-02 (2021 revision). **NOT** the 2017 NBER WP 23425 — they differ on terminology and sample.

**Role in thesis:**
- Wordlist source: Loughran-McDonald (2011) uncertainty words, 297 total.
- Segment decomposition: Presentation (Pre) vs Q&A (Ans) — same split we use.
- Level of aggregation: CEO-only in published body; individual CFO in Internet Appendix. **Does NOT pool across all managers.**

**Verbatim evidence (F1D NotebookLM, session `e019ecda`, 2026-04-09, 6 verified quotes):**

- Wordlist: *"The full list comprises 297 words, sourced from the 'uncertainty words' of the Loughran and McDonald (2011) Master Dictionary (August 2014 version)."*
- Speaker structure: *"The transcript from each call includes a list of conference call participants, divided into company representatives and analysts."*
- Sample: *"The full sample consists of 122,611 calls for 5,095 distinct firms..."*
- Segmentation: *"Speech characteristics denoted 'Call' are calculated for CEO, CFO and participating analysts combined. Speech characteristics denoted 'CEO' are calculated for CEO speech only."*

**Reference memory:** `memory/project_dwz_2021_verified.md`.

**F1D status:** ✓ paper in notebook. Verbatim extractable.

### 1.2 User challenge after initial Step 1 framing

Initial framing claimed UncAnsMgr was a "novel extension of DWZ 2021." User pushback:

> "but i remember iudentifying our mgr following bgt. corerct? if so, we need bgt also for our main variables design"

Testable claim. Verification required before accepting.

### 1.3 BGT 2018 — verification via primary sources

**Source 1: NotebookLM F1D, session `e4dc5567` (2026-04-16):**

Query: "When BGT construct `Fog(Present)` and `Fog(Response)`, do they POOL across ALL company-side speakers, or restrict to specific individuals (CEO-only, etc.)? What is the exact speaker-classification rule?"

Response:
- (a) Pooling — *"NOT IN SOURCE. The paper's text does not explicitly state whether they pool language across all company-side speakers or restrict the text to specific individuals."*
- (b) Speaker rule — *"NOT IN SOURCE. The authors do not provide an explicit operational rule for identifying or classifying speakers from the transcripts (and leave it implicit to the data source, Thomson Reuters StreetEvents)."*
- (c) Manager definition — only *"Fog(Present) represents the Fog index of managers' language during the presentation, and Fog(Response) is the Fog of managers' responses to questions."* (§3.2, p.94). No operational detail.
- (d) Aggregation — *"NOT IN SOURCE. There is no mention of pooling, aggregating, or combining language across multiple speakers to calculate the indices."*

**Conclusion from NotebookLM alone:** paper body does NOT document the pooling rule.

**User redirect:** "BGT doesnt disclose it in their paper, but do share their implementation codes. you must read that"

**Source 2: Ian Gow's public replication code, `github.com/iangow/bgt`:**

`fog/get_fog_speaker_data.sql`:
```sql
INSERT INTO bgt.fog_speaker
SELECT file_name, last_update, context, speaker_number,
        (fog_data(speaker_text)).*
FROM streetevents.speaker_data
WHERE file_name='%s' AND speaker_name != 'Operator';
```

The ONLY filter is `speaker_name != 'Operator'`. Every non-Operator speaker-turn gets fog-scored.

`fog/get_within_call_data.R` (aggregation):
```r
fog_answers <- questions %>%
    inner_join(fog_speaker %>% rename(answer_number=speaker_number)) %>%
    group_by(file_name, last_update, question_nums) %>%
    summarize(percent_complex = sum(percent_complex*num_words)/sum(num_words),
              num_sentences = sum(num_sentences),
              num_words = sum(num_words)) %>%
    mutate(fog_answers = 0.4 * (percent_complex + num_words/num_sentences))
```

`sum(percent_complex*num_words)/sum(num_words)` = word-count-weighted pooling across all answerers within each QA pair (`question_nums` group). Then `mean_manager_fog = regr_avgy(y, x)` averages across QA pairs in the call.

**Conclusion from code:** BGT 2018 DOES pool across all company-side answer-givers. The pooling is operational in the replication code but absent from the paper body.

### 1.4 Our pipeline — direct code read for comparison

**File:** `src/f1d/text/build_linguistic_variables.py`.

**Manager classification (lines 509-606):**

Line 509-514 explicit attribution comment:
```
# Manager classification (BGT 2018 + F1+F2+F3 + pres roster)
# Replaces the legacy 45-keyword role-string regex on 2026-04-09 after
# validation showed Pearson 0.94+ correlation with the legacy measure
# across all 8 LM categories and a procedural-precedent grounding in
# Bushee-Gow-Taylor (2018, JAR).
```

Our `is_manager` logic (lines 601-606):
```python
df["is_manager"] = passes_f123 & (
    (df["context"] == "pres")
    | ((df["context"] == "qa") & df["in_pres_roster"])
)
```

Where `passes_f123` = not placeholder & not Operator & not analyst-role & not analyst-employer, and `in_pres_roster` = speaker name appeared in presentation segment AND passed F123.

**Our aggregation (lines 616-646):**
```python
def aggregate_weighted(df, sample_mask, context_mask, count_cols):
    subset = df[sample_mask & context_mask].copy()
    gb = subset.groupby("file_name")
    sums = gb[count_cols + ["total_tokens"]].sum()
    total_tokens = sums["total_tokens"].replace(0, np.nan)
    for col in count_cols:
        pct = (sums[col] / total_tokens) * 100.0
```

**Ratio-of-sums at call (`file_name`) level.** Not QA-pair level.

### 1.5 Differences between ours and BGT — honest disclosure

| Aspect | BGT 2018 (via code) | Ours (`build_linguistic_variables.py`) | Deviation nature |
|---|---|---|---|
| Speaker filter | `speaker_name != 'Operator'` (loose) | F1 placeholder + F2 role-analyst regex + F3 employer-analyst regex + per-call pres roster (tight) | Ours stricter — necessitated by Capital IQ data lacking structural `<Participants>` XML tags that BGT's code relies on |
| Aggregation unit | Per-QA-pair (`question_nums` group) word-weighted pool; then mean across pairs | Per-call (`file_name`) ratio-of-sums directly | Both pooled-manager. Differ when QA-pair lengths vary within calls. |
| Measure content | Fog readability | LM 2011 uncertainty share | Different measure; follow DWZ 2021 for LM content |
| Segment split | Pres vs Q&A (context tag) | Pres vs Q&A (context tag) | Identical |

### 1.6 Three-step anti-capitulation protocol on my retraction

1. **Original position:** UncAnsMgr is a novel extension of DWZ 2021 alone.
2. **Specific new evidence:** (a) user memory claim pointing to BGT precedent; (b) direct read of Ian Gow's replication code showing pooled-manager aggregation; (c) direct read of `build_linguistic_variables.py:509-514` showing explicit self-attribution to BGT 2018.
3. **Evaluation:** original claim was wrong. BGT 2018 IS the variable-design precedent for pooled-manager aggregation. Pipeline code explicitly grounds itself in BGT. Verified via primary sources (code + comments), not memory alone.

### 1.7 Corrected thesis prose for §3.2

> "We follow Bushee, Gow, and Taylor (2018) for the pooled-manager aggregation logic, as documented in the authors' publicly available replication code (Gow, `github.com/iangow/bgt`); the paper body does not disclose the operational pooling rule, which is exposed only in the accompanying code. Because our Capital IQ transcripts do not preserve the structural `<Participants>` XML metadata that BGT's code relies on, we classify company-representative speakers using a three-filter rule (F1: placeholder removal; F2: role-based analyst exclusion; F3: employer-based analyst exclusion), combined with a per-call presentation-roster check that restricts Q&A classification to speakers who also appeared in the presentation segment. We aggregate at the call-segment level via ratio-of-sums rather than BGT's per-QA-pair mean-of-ratios; both are pooled-manager aggregations. For wordlist content, we apply the Loughran-McDonald (2011) 297-word uncertainty dictionary rather than the Fog readability index, following Dzielinski, Wagner, and Zeckhauser (2021)."

### 1.8 Step 1 status

**CLOSED.** Two co-foundational papers verified via primary sources:
- DWZ 2021: NotebookLM 6 verbatim quotes, memory `project_dwz_2021_verified.md`.
- BGT 2018: NotebookLM 3 verbatim quotes (paper body) + Ian Gow replication code read directly (aggregation logic); memory `project_bushee_gow_taylor_2018.md` and `reference_bgt2018_window.md`.
- Pipeline: `build_linguistic_variables.py` explicitly attributes to BGT 2018 at lines 509-514, implements filtered pooling at lines 601-606, ratio-of-sums aggregation at lines 616-646.

Reference memories updated:
- `memory/reference_grenadier_2002_verbatim.md` (already done)
- `memory/reference_aguerrevere_2009_verbatim.md` (already done — venue flag: JF not RFS)
- (TODO in next session) cleanup of `reference_bgt2018_window.md` vs `project_bushee_gow_taylor_2018.md` — consolidate

---

---

## Steps 2 & 3 — OPSW 1999 + BKS 2009 (cash-holdings foundation, closed jointly)

### 2.0 Why these two together

Step 2 (OPSW 1999) and Step 3 (BKS 2009) are the theory-method split for the CashRatio DV and the precautionary-motive framework. They were closed in the same investigation because BKS 2009's verbatim explicitly references OPSW, and a consistent theory-method chain requires both.

### 2.1 OPSW 1999 verbatim highlights

- Directional prediction (p.8): *"one would expect firms with greater cash flow uncertainty to hold more cash."* — LOAD-BEARING for HC.
- Operational definition of precautionary motive (p.9): *"firms can find it profitable to hold cash to mitigate costs of financial distress. We call this motivation to hold liquid assets the precautionary motive for holding cash."*
- DV form: `ln(cash/(assets-cash))` at annual frequency. **Different from our pipeline; NOT followed.**
- Full reference memory: `memory/reference_opsw_1999_verbatim.md` (7 quotes).

### 2.2 BKS 2009 verbatim highlights

- DV form (p.1991): *"We measure the cash ratio as cash and marketable securities (data item #1) divided by total assets (data item #6)."* **Matches our pipeline `cheq/atq` exactly.**
- Explicit rejection of OPSW's log form (pp.1998-1999): *"The cash-to-net assets ratio generates extreme outliers... Thus, we focus primarily on regressions using cash to assets as the dependent variable, but reproduce regressions using the log of cash to net assets."* Referee-response anchor.
- Two-way firm+year clustering via Cameron-Gelbach-Miller 2006 (p.2000). Procedural precedent for our macro-IV clustering.
- Sample exclusion: financial firms (SIC 6000-6999) + utilities (SIC 4900-4999). Matches our filter.
- Uncertainty → cash: *"firms hold more cash as cash flow risk increases"* (p.2013) — confirms OPSW's directional prediction.
- Full reference memory: `memory/reference_bks_2009_verbatim.md` (7 quotes).

### 2.3 Pipeline verification

Primary source: `src/f1d/shared/variables/cash_holdings.py:20`
```python
"""Build CashRatio = cheq / atq from raw Compustat quarterly data."""
```

`cheq` (cash and short-term investments, quarterly) = quarterly analogue of Compustat annual `d1`. `atq` (total assets, quarterly) = quarterly analogue of `d6`. **Our formula matches BKS 2009's primary specification — identical operational form.**

### 2.4 User challenge — "why not OPSW's DV? doesn't it raise suspicion?"

Referee-response scenario: if we cite OPSW as theory foundation but use BKS's DV form, does that look inconsistent?

**Advisor-confirmed verdict: No. Keep both. Do not rebuild.** Evidence:

1. **Theory-method split is the standard pattern in empirical corporate finance.** Dozens of papers cite OPSW 1999 for theory but use cash/assets (post-2009 convention). Examples: Harford-Mansi-Maxwell 2008, Dittmar-Mahrt-Smith 2007, Duchin-Ozbas-Sensoy 2010, He-Wintoki 2016.
2. **OPSW's directional prediction is form-agnostic.** Sign of (uncertainty → cash) is preserved across cash/assets, cash/(assets-cash), and log(cash/(assets-cash)). Magnitude differs but sign does not.
3. **BKS 2009 itself explicitly evaluated and rejected OPSW's form** on econometric grounds (pp.1998-1999). Using OPSW's form in a 2026 submission would signal unfamiliarity with post-2009 literature — worse than the "inconsistency" concern.
4. **Rebuild cost is prohibitive:** every H1-family suite (H1, H1.1, H1.1b, H1.2, H11, H11-Lag, H23, H24, H24b, H25) would need panel rebuild + regression rerun + audit redo. Zero upside on sign/significance.

### 2.5 Advisor-supplied decision criterion for rest of walkthrough

Keep a paper if EITHER:
- (a) originates a directional prediction the thesis tests
- (b) is the operational form / method we use
- (c) convention in top-tier finance requires it

Drop only when fully redundant on all three axes. "Minimal stack" ≠ absolute minimum count.

Applied:
- OPSW 1999: (a) ✓ (c) ✓ → KEEP
- BKS 2009: (b) ✓ (c) ✓ → KEEP

### 2.6 Defensible §3.3 DV prose (approved)

> "The precautionary motive for cash holdings articulated by Opler, Pinkowitz, Stulz, and Williamson (1999) predicts that firms facing higher cash-flow uncertainty hold more cash. We test this directional prediction on a firm-quarter panel, using the cash-to-assets specification adopted by Bates, Kahle, and Stulz (2009), who explicitly evaluated both OPSW's log-of-cash-to-net-assets form and the linear cash-to-assets form and chose the linear form because the log does not fully eliminate outliers for cash-heavy firms. Since BKS (2009), the linear cash-to-assets ratio has become the default in the cash-determinants literature, and we follow that convention."

### 2.7 Future work (if time permits)

Append an appendix robustness check reporting the main HC regressions using OPSW's `ln(cheq/(atq-cheq))` DV form. Mirrors BKS 2009's own reporting structure. Cost: one DV rebuild + one rerun of H1 suite. Gain: complete referee-defense coverage. NOT required for first submission.

### 2.8 Step 2-3 status

CLOSED. Both papers verbatim-backed. §3.3 attribution locked. Pipeline matches BKS 2009 exactly. Future-work hedge documented.

---

---

## Major Re-Scoping Decision — Skeleton v4 (after Steps 2-3)

User-driven structural change after Step 3 surfaced a pivot for the entire thesis structure:

1. **Capex reframed from "puzzle" to "exploratory"** — eliminates need for capex↓ anchor (no AFW 2004, no Bloom 2014 load-bearing).
2. **§4.5 payout moved from body to appendix-only** — main IV null on payout; segment-channel argument is headache > value.
3. **R&D (H16) dropped entirely** from thesis.
4. **37-suite appendix dropped** in favor of §II pre-commitment statement + targeted appendix.
5. **Reference stack tightened** — drop AFW 2004, drop Bloom 2014 as load-bearing, demote Aguerrevere 2009 to Tier-2 citation-only.
6. **Central Claim rewritten** with neutral exploratory framing for capex (no "puzzle", no "OPPOSITE").
7. **Three-bucket pre-commitment statement** front-loaded in §II (one-tailed §III; two-tailed exploratory §IV main; one-tailed explanatory §IV moderator).

V4 skeleton committed to `docs/Draft/THESIS_SKELETON.md` (overwrite v3) on 2026-04-16 evening.

---

## Steps 4 + 5 — Minton-Wruck 2001 (corrected year) + Faulkender-Petersen 2006 (single combined query, after user uploaded both papers)

### 4.0 Why these two together

User uploaded both newly-needed papers (MW + FP) to F1D on 2026-04-16 to close the remaining Tier-1 gaps. Single batched verbatim query mirrored the BGT/AFW/MW/SY batched style that worked for BGT.

### 4.1 Minton-Wruck 2001 — verbatim findings

**Year flag:** primary source NotebookLM cites as **2001** SSRN working paper, NOT 2009 as earlier project memory said. Year corrected throughout v4.

**Verbatim highlights (5 quotes):**

- Operational definition (§2.1, pp.4-5): *"A firm is classified as being financially conservative (i.e., having low leverage) if its annual ratio of long-term debt (including the current portion of long-term debt) to total assets is in the bottom 20% of all firms for five consecutive years."* — LEVERAGE-only, multi-year persistence criterion. NOT multi-dimensional.
- Definition (§1, p.1): *"persistent financial policy of low leverage."*
- Mechanism (§3.2.1, p.11): *"Donaldson (1961) and extensions of pecking order theory predict that a firm will, if possible, maintain financial slack or stockpile debt capacity..."* — financial slack / pecking-order, **NOT** precautionary motive.
- Cash finding (§2.3, p.7): *"cash and marketable securities comprise 21% of total assets on average (17.5% at the median) — almost three times that of the typical control firm."* — direct empirical evidence of cash↑/leverage↓ joint cluster.
- Sample: 1974-1998, 5,613 firms, 46,675 firm-years; logit regression.

**Theoretical-mechanism split:** MW use Donaldson 1961 / Myers 1984 financial-slack; we use OPSW 1999 / BKS 2009 precautionary. Both predict cash↑+leverage↓ cluster but differ in mechanism. v4 §2.4 explicitly discloses this split.

**Title-source confirmation:** paper title IS "Financial Conservatism" — our thesis title's "Conservatism" term is verbatim-grounded.

Full reference memory: `memory/reference_minton_wruck_2001_verbatim.md`.

### 4.2 Faulkender-Petersen 2006 — verbatim findings

**CRITICAL DISCOVERY:** FP 2006 use BINARY classification (rated vs unrated), NOT three-way (IG/BelowIG/Unrated). Our H1.2 deviates and must disclose.

**Verbatim highlights (5 quotes):**

- Binary access (§1.2, p.48): *"We use whether the firm has a bond rating or a commercial paper rating as a measure of access to the public bond markets."*
- Why unrated = no access (§1.2, pp.48-49): *"Very few firms without a debt rating have public debt..."*
- Empirical magnitude (Abstract, p.45): *"firms with access have 35% more debt."*
- "Credit constrained" qualifier (§3.1, p.62): *"The fact that firms without a bond rating use significantly less debt, and slightly more equity is evidence that they are credit constrained. **The evidence on whether they are capital constrained is weaker.**"* — must use FP's exact "credit constrained" wording, NOT "capital constrained."
- Sample: 1986-2000, 77,659 firm-years (19% rated); IV estimation correcting endogeneity.

**Three-way → binary mapping decision (per user 2026-04-16):**
- Report H1.2 with IG (0/4 baseline) and Unrated (4/4 sig) only
- BelowIG row (0/4 null) suppressed from main table — moved to appendix
- Defensible because BelowIG adds no economic content + FP's primary scheme is binary

**Constraint-language correction:** v4 thesis switches from "least capital-market access" / "most capital-constrained" → "credit constrained" / "least access to public debt markets" (FP's exact wording).

Full reference memory: `memory/reference_faulkender_petersen_2006_verbatim.md`.

### 4.3 Step 4-5 status

CLOSED. Both papers verbatim-backed. v4 skeleton updated. HFC framing refined.

---

## Step 6 — Hoberg-Phillips 2016 (TSIMM, competition moderator)

**Date:** 2026-04-16 evening (post-compaction). NotebookLM session `fd76dda7`. F1D notebook key `hp2016`.

### 6.1 Why this paper

HP 2016 is the last Tier-1 paper closing the v4 reference stack. Two roles in v4:

1. **Method anchor for Grenadier 2002's competition channel** — `TSIMM_log_c` moderates UncAnsMgr in H1.1 (cash) and H13.1 (capex) — the latter is the load-bearing test that operationalizes Grenadier's preemption-accelerates-investment prediction in §IV.A.
2. **Reverse-direction H23 robustness** — `log(TotalSimilarity)` as the IV at firm-year level. Tests whether competition predicts uncertainty language.

This makes Pattern G recur a **fourth time**: theory anchor (Grenadier 2002) + method anchor (HP 2016) for the competition construct.

### 6.2 Verbatim findings (5 quotes)

- **Data source (p.1434):** *"From each linked 10-K, our goal is to extract its business description. This section of the document appears as item 1 or item 1A in most 10-Ks."*
- **Sample period (p.1433-4):** 1997-2008 fiscal years; 50,673 obs after filters (excludes financials SIC 6000-6999).
- **Cosine similarity (Eq. 2, p.1432):** *"Product Cosine Similarity i,j = (Vi · Vj)"* — normalized 10-K word vectors, dot product on [0,1].
- **Threshold (p.1437):** *"A 21.32 percent minimum similarity threshold (where we define firms i and j as being in the same industry when 100 · Vi · Vj > 21.32) generates 10-K-based industries with 2.05 percent membership pairs, which is the same as SIC-3."* — calibrated to match SIC-3 granularity.
- **Total Similarity (p.1448):** *"Total similarity is a global measure and is the sum of the pairwise similarities between the given firm and all other firms in our sample in the given year."*
- **Interpretation (p.1453, p.1448):** *"increase in total similarity, indicating increased competition"* + *"firms with higher global total similarity are far more likely to discuss competitive pressures in their management's discussion."*

### 6.3 Two CRITICAL flags surfaced by verbatim audit

1. **"TNIC3" and "TSIMM" labels are NOT in the paper.** The paper uses *"TNIC"* generically (network industry classification) and *"total similarity"* descriptively. The "TNIC3" / "TNIC2" naming and "TSIMM" abbreviation are HP-website conventions calibrated to match SIC-3 / SIC-2 granularity. **Writing implication:** when introducing the variable, name them as our pipeline labels and cite the paper for the underlying construct.
2. **Paper sample is 1997-2008; thesis sample is 2002-2018.** We use HP's externally maintained data series (per p.1426: *"on our external website, where we maintain the data"*), which extends well beyond the paper's original window. **Writing implication:** disclose explicitly in §III.A — "We use Hoberg-Phillips' externally updated TNIC/total-similarity data covering our 2002-2018 sample period; the original construction is from HP 2016 covering 1997-2008."

### 6.4 v4 application

- **§II.4 (or §III.D footnote):** define TotalSimilarity = sum of pairwise cosine similarities (HP 2016 p.1448). Cite cosine formula (Eq. 2) and threshold-calibrated TNIC.
- **H1.1 + H13.1 + H23:** use as competition moderator (firm-fiscal-year, log-transformed, mean-centered for interactions).
- **§V limitations:** flag (i) single dimension of competition (no HHI/concentration), (ii) annual frequency vs. our quarterly panel, (iii) endogeneity not addressed in our use (HP's 2001-shock identification not pursued).

### 6.5 Step 6 status

CLOSED. All 8 Tier-1 papers now have verbatim memory files: DWZ 2021, BGT 2018, OPSW 1999, BKS 2009, MW 2001, FP 2006, Grenadier 2002, **HP 2016**.

Full reference memory: `memory/reference_hoberg_phillips_2016_verbatim.md`.

---

## Step 7 — Tier-2 supporting papers (consolidated record)

**Date:** 2026-04-16 evening (post-compaction). NotebookLM sessions `a3888472` (Batch A: macro IVs) + `2be1f145` (Batch B: mixed). 9 papers total — 7 verbatim'd this session, 2 cross-reference existing standalone files.

### 7.1 Why a single consolidated record (not 9 separate files)

These are citation-only anchors — they support specific measure constructions in §IV but do not carry load-bearing theoretical or methodological weight in the v4 thesis body. A single consolidated record satisfies the citation-defense bar (citation + role + one verbatim definition + sample) without bloating the memory tree.

### 7.2 The 9 papers + roles

| # | Paper | v4 Role | Status |
|---|-------|---------|--------|
| 1 | Hassan, Hollander, van Lent & Tahoun (**2020, QJE**) | §IV.B PRisk benchmark | Verbatim done |
| 2 | Baker, Bloom & Davis (2016, QJE) | §IV.B H24 US EPU IV | Verbatim done |
| 3 | Davis (2016, NBER WP 22740) | §IV.B H24b GEPU IV | Verbatim done |
| 4 | Caldara & Iacoviello (2022, AER) | §IV.B H25 GPR IV | Verbatim done |
| 5 | Amihud (2002, JFM) | §IV.A H7 family ILLIQ | Verbatim done |
| 6 | Wang (2020, RAF) | §IV.A H5 DISP | Verbatim done |
| 7 | Chang, Dasgupta & Hilary (2006, JF) | §IV.A H19b/H20b Dissue | Verbatim done |
| 8 | Larcker & Zakolyukina (2012, JAR) | §III.A speaker ID procedure | Cross-ref `project_larcker_zakolyukina_2012.md` |
| 9 | Aguerrevere (2009, JF — NOT RFS) | §IV.A footnote (demoted) | Cross-ref `reference_aguerrevere_2009_verbatim.md` |

### 7.3 Year/venue corrections surfaced in Step 7

1. **Hassan et al. — published year is 2020, not 2019.** "2019" was the working-paper year. The QJE article is Vol. 135 Iss. 4 (2020), pp. 2135-2202, doi:10.1093/qje/qjz021. Use **2020** in v4 bibliography and body text.
2. **Davis 2016 — NBER WP only**, no journal, no DOI. Cite as `Davis (2016, NBER Working Paper 22740, October 2016)`.
3. **Wang 2020 venue verification needed.** NotebookLM returned `RAF 19,3` header without explicit year. RAF Vol 19 Iss 3 = 2020 — verify via Emerald Insight when compiling .bib.
4. **Aguerrevere 2009 venue is JF, not RFS** — already corrected in §4 v4 reframe but reaffirmed here.

### 7.4 Step 7 status

CLOSED. All 9 Tier-2 papers in v4 reference stack now have citation + role + verbatim defense ready. v4 stack complete: 8 Tier-1 + 9 Tier-2 = 17 papers total.

Full reference memory: `memory/reference_tier2_consolidated.md`.

---

## Steps 8-N — sequence plan (pending approval per step)

- **Step 8:** Infrastructure audit — summary stats Table 1, var defs appendix, references .bib, two-col LaTeX class, table numbering map.
- **Step 9 onward:** Drafting (Methods → Results → Additional → Lit → Intro → Abstract → typeset).

Each step:
1. Investigate primary source (NotebookLM verbatim OR code read).
2. Apply advisor's (a)/(b)/(c) decision criterion.
3. Record verbatim + role + F1D status in reference memory.
4. Wait for user approval before proceeding.

---

## Appendix A — Memory files referenced

- `memory/project_thesis_skeleton.md` — v3 skeleton, current state
- `memory/project_dwz_2021_verified.md` — DWZ verbatim (7 days old)
- `memory/project_bushee_gow_taylor_2018.md` — BGT + Ian Gow code (6 days old)
- `memory/project_notebooklm_papers.md` — 38-paper F1D catalogue
- `memory/reference_grenadier_2002_verbatim.md` — 7 quotes (today)
- `memory/reference_aguerrevere_2009_verbatim.md` — 3 quotes (today, venue flag)
- `memory/reference_preemptive_precaution_verified_novel.md` — prior-session verification
- `memory/feedback_literature_drives_hypotheses.md` — process rule
- `memory/feedback_notebooklm_mandatory.md` — verbatim requirement

## Appendix B — Corrections / retractions recorded in this walkthrough

| Claim | Original | Corrected | Evidence |
|---|---|---|---|
| UncAnsMgr provenance | Novel extension of DWZ 2021 | DWZ 2021 + BGT 2018 co-foundational (pooled-manager via BGT, LM uncertainty content via DWZ) | Ian Gow code + `build_linguistic_variables.py:509-514` self-attribution |
| Aguerrevere 2009 venue | RFS (per skeleton) | JF (per NotebookLM + memory `project_notebooklm_papers.md`) | NotebookLM direct-source response + F1D catalogue |
| MW year | 2009 (per prior memory) | 2001 (SSRN WP per primary source) | NotebookLM source citation |
| FP rating scheme | 3-way IG/BelowIG/Unrated assumed | BINARY rated/unrated (we extend to 3-way; must disclose) | FP §1.2 verbatim p.48 |
| FP constraint wording | "capital constrained" | "credit constrained" (FP §3.1 explicitly weaker on capital) | FP §3.1 verbatim p.62 |
| HP 2016 paper labels | "TNIC3" + "TSIMM" treated as paper terms | NOT in paper — HP-website conventions; paper uses "TNIC" generic + "total similarity" descriptive | NotebookLM verbatim audit session fd76dda7 |
| HP 2016 sample window | Implicit assumption: covers our 2002-2018 sample | Paper covers 1997-2008; we use HP's externally maintained updated series | HP 2016 p.1433 + p.1426 |
| Hassan et al. year | "Hassan et al. (2019)" per prior memory + initial draft | **Hassan et al. (2020)** per QJE Vol 135 Iss 4 publication (2019 was the WP year) | NotebookLM verbatim citation header — session 2be1f145 |
| Davis 2016 venue | Implicit "published" status | NBER Working Paper 22740 — unpublished, no journal, no DOI | NotebookLM verbatim — session a3888472 |
| Wang 2020 title + pages | "Dispersion in Analyst Earnings Forecasts," pp. 290-315 (initial paraphrase) | **"Does analyst forecast dispersion represent investors' perceived uncertainty toward earnings?"** RAF 19(3) 2020, pp. 289-312, doi:10.1108/raf-10-2018-0224 | Crossref API verification 2026-04-16 evening |
| Hassan et al. sample + formula | "NOT IN SOURCE" + "public knowledge" claim | **2002-2016, 178,173 calls, 7,357 firms, Thomson Reuters StreetEvents** (p.2143); PRisk Eq.1 p.2148 (bigram count / total bigrams) | NotebookLM follow-up session 2be1f145 |

