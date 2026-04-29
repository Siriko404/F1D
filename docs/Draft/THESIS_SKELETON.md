# Thesis Skeleton — v6 (from-scratch rewrite)

Revised 2026-04-29 (v6): full draft rewrite under locked-framing constraints.
Supersedes v5.1 (2026-04-22, archived at git tag `draft-v5.1-pre-rewrite`).

## Drivers of v6 (what changed since v5.1)

1. **3-IV decomp framing locked 2026-04-27** (`project_dwz_anchored_framing_locked_2026_04_27.md`): all §3 + §4.2 results report ClarityCEO + UncResCEO + UncPreCEO, NOT joint-IV (UncAnsCEO + UncPreCEO).
2. **Headline contribution locked 2026-04-27**: "UncResCEO drives 12/12 cash where DWZ found null on prices — same variable, different outcome class, opposite verdict." MUST appear in abstract + §1 + §3 + §5.
3. **H1/H2 §2 framing locked 2026-04-28** (`project_h1_h2_theoretical_framing_locked_2026_04_28.md`): precautionary chain = OPSW + BKS + DWZ + BS 2003. H2 amplification anchor = ACW 2004 verbatim (Section II.D).
4. **§4.2 dual-channel** (locked 2026-04-27): bid-ask spread (H14c.ceo2.decomp, market channel) + SEC comment letter (H18.ceo2.decomp, regulatory channel). Both load UncPreCEO.
5. **§4.3 endogeneity defense** — NEW section. 3 designs shipped 2026-04-29: Phase E sudden-death DiD (H.death.did), DWZ §6 first-difference (H.dwz.fd), Lewbel 2012 IV (H.lewbel.iv). Plus Option 4 asymmetry footnote.
6. **§4.1 driver expansion**: add H23 TSIMM (Hoberg-Phillips competition) per locked framing.
7. **H1.3 CFvol** included in §3 alongside HFC (user decision 2026-04-29: same pattern as H1.2 at ~85% magnitude).
8. **H1.4 HedgingNeeds DROPPED entirely** (user decision 2026-04-29: 0/8 sig at any threshold).

## Title

**Hold On to Your Cash: CEO Speech Uncertainty and Financing Conservatism**

## Research Question

Does CEO speech uncertainty during earnings calls predict firm financing conservatism, and does the response decompose differently across CEO-style vs state-residual vs presentation components?

## Headline contribution (DO NOT BURY)

> UncResCEO — which DWZ 2021 found "explains little" of market price reaction — loads positively on cash holdings in 12/12 specifications. Same variable, different outcome class, opposite verdict. The Q&A residual that does not move stock prices does move corporate cash decisions.

This is the single sharpest finding. Every section pulling at it: abstract, §1 contributions, §3 results, §5 synthesis. Supporting evidence: ClarityCEO 8-9/12 NEG sig (persistent CEO style → leaner balance sheets); HFC and CFvol amplify on lead-DV (constrained-firm channel); UncPreCEO null on cash but POS on outsider channels (spread + SEC).

## Formal Hypotheses

**H1 (HC): Cash response to CEO speech uncertainty under DWZ 3-IV decomp**

| IV | Prediction | Anchor | Pre-registration |
|---|---|---|---|
| UncResCEO → cash↑ | POS one-tailed | OPSW 1999 (precautionary directional) + BKS 2009 secular | **PRIMARY PRE-REGISTERED** |
| ClarityCEO → cash | direction observed; channel pre-registered | BS 2003 (manager-FE channel exists for cash) + DWZ 2021 (Clarity = persistent CEO style) | **CHANNEL PRE-REGISTERED; DIRECTION INTERPRETIVE** |
| UncPreCEO → null | null expected | DWZ verbatim: UncPre "controls for uncertainty resulting from persistent firm characteristics" | LOW-CONFIDENCE NULL |

Suite: H1.ceo2.decomp + H1.ceo2.decomp.qtrexp.

**H2 (HFC): Constraint amplifies UncResCEO → cash response**

| IV | Prediction | Anchor | Pre-registration |
|---|---|---|---|
| UncResCEO × Unrated → POS | POS one-tailed | ACW 2004 §II.D verbatim (constrained firms increase cash following negative macro shocks) + FP 2006 (credit-constrained Unrated) | **PRE-REGISTERED PRIMARY** |
| UncResCEO × HighCFvol → POS | POS one-tailed | Han-Qiu 2007 (cash-flow vola moderator); same channel as ACW via different proxy | **SECONDARY PRE-REGISTERED** |

Suite: H1.2.ceo2.decomp + H1.2.ceo2.decomp.qtrexp + H1.3.cfvol.

## Section-by-section spec

### Abstract (target ~200 words)

- Headline contribution sentence
- 3-IV decomposition + sample
- HC + HFC results in decomp form (Clarity NEG, UncRes POS, UncPre null on cash)
- §4.1 drivers: speech responds to PRisk + EPU + GEPU + competition
- §4.2 outsider asymmetry: spreads + SEC load UncPreCEO (the one DWZ called firm-culture)
- §4.3 endogeneity: 3 designs across 3 threats — sudden-death DiD, DWZ FD, Lewbel IV
- Keywords + JEL

### §1 Introduction

1. **Motivation**: earnings call as quarterly window on managerial uncertainty + DWZ 3-IV architecture as starting point
2. **Gap**: DWZ tested CARs/volume/analyst (Table A.1 verbatim); never tested cash, spreads, SEC. We extend in two outcome directions.
3. **Approach**: preserve DWZ decomposition, extend outcome set. Apply CEO-specific partition to firm-quarter financing + outsider-reaction outcomes.
4. **Empirical setting + headline findings** including the contribution sentence
5. **Contributions** (3):
   1. UncResCEO 12/12 cash result CONTRASTS DWZ's UncRes-null on prices (headline)
   2. Insider-outsider channel asymmetry on DWZ's own scripted-vs-improvised theoretical structure
   3. Three-design endogeneity package (sudden-death DiD + DWZ FD + Lewbel IV) addressing three orthogonal threats
6. **Roadmap**

### §2 Conceptual Framework and Empirical Strategy

Per `project_h1_h2_theoretical_framing_locked_2026_04_28.md` §2.1-§2.6 outline (use VERBATIM as spec):

- **§2.1 Pre-Commitment Statement**: 3-IV decomp; opposite-sign predictions (Clarity NEG observed, UncRes POS pre-registered, UncPre null expected); H2 amplification PRE-REGISTERED on UncRes × Unrated (and × HighCFvol secondary).
- **§2.2 Conceptual framework**: precautionary motive lens (OPSW 1999 + BKS 2009)
- **§2.3 Speech uncertainty measurement**: DWZ 2021 architecture (UncPre + Clarity + UncRes); Pres-vs-QA framing per DWZ verbatim ("scripted firm-culture" vs "improvised CEO-style"); Hassan 2020 + BBD 2016 supporting text-based real-time uncertainty family
- **§2.4 H1 development**: precautionary chain OPSW → BKS → DWZ → BS 2003 manager-FE-on-cash
- **§2.5 H2 development**: ACW 2004 §II.D verbatim asymmetry + FP 2006 operational definition + Phan 2019 mechanism interpretation
- **§2.6 Disclosures**: MW 2001 mechanism split (financial slack vs precautionary); FP 3-way extension; out-of-scope = identification (forward-link to §4.3); ClarityCEO direction interpretive
- **§2.7 Empirical design**: PanelOLS, 4-step FE ladder, base+extended controls, firm-clustered SE (two-way for macro suites)

### §3 Main Empirical Analyses

- **§3.1 Data, sample, variables, specification** (re-write under decomp framing — note 3-IV vs old 2-IV)
- **§3.2 HC — Cash holdings under DWZ 3-IV decomp**: tab:h1_ceo2_decomp + tab:h1_ceo2_decomp_qtrexp. Headline contribution sentence here. Results: Clarity 8-9/12 NEG sig at p<.05; UncRes 12/12 POS sig (10/12 at p<.05); UncPre null
- **§3.3 HFC — Constraint amplification (Unrated channel)**: tab:h1_2_ceo2_decomp + tab:h1_2_ceo2_decomp_qtrexp. UncRes × Unrated POS on lead-DV
- **§3.4 H1.3 CFvol — Constraint amplification (cash-flow vola channel)**: tab:h1_3_cfvol. UncRes × HighCFvol POS on lead-DV + industry-FE; same pattern as HFC at ~85% magnitude. Disclose 1-tier weaker p-value.
- **§3.5 Robustness notes** (compact)

### §4 Additional Analyses

- **§4.1 Drivers of CEO speech uncertainty**: tab:driver_matrix consolidating 4 drivers (PRisk H11 + EPU H24 + GEPU H24b + TSIMM H23). Each one-tailed positive in theoretically predicted direction. Construct validation, not formal hypothesis.
- **§4.2 Outside-world reaction**: locked dual-channel
  - **§4.2.1 Market channel**: tab:h14c_ceo2_decomp — 25-day post-call spread loads UncPreCEO contemporaneously (4/12 sig at p<.10), Clarity + UncRes null
  - **§4.2.2 Regulatory channel**: tab:h18_ceo2_decomp — SEC comment-letter receipt loads UncPreCEO (4/6 sig at p<.10, 3/4 ext-ctrls survive), Clarity + UncRes null
  - **§4.2.3 Asymmetry synthesis**: outsider-loaded segment is the one DWZ called firm-culture-reflecting (Pres); insider-loaded segment (cash) is the CEO-style-revealing (Q&A — both Clarity and UncRes)
- **§4.3 Endogeneity defense — three designs, three threats** (NEW)
  - **§4.3.1 Threats framing**: NOT "convergence on β" — "three designs cover three orthogonal identification threats"
  - **§4.3.2 Sudden-death DiD** (Phase E, n=8): exogenous shock; reverse-causality + omitted-vars threat. ATT≈−0.018 p=0.14 power-limited at n=8. Pre-trend disclosure + heterogeneity-test power note
  - **§4.3.3 DWZ §6 first-difference** (n=659 turnover pairs): time-invariant heterogeneity (firm + manager). β(ΔClarityCEO)=−0.018 p=0.046. Sample filters per DWZ verbatim
  - **§4.3.4 Lewbel 2012 IV** (n=43,471): time-varying omitted confounders. OLS β=+0.0021 → 2SLS β=+0.010 (5×). Cragg-Donald F=20.4 (borderline weak-IV per Stock-Yogo). Sargan p=0.92. Wu-Hausman p=0.24 (CANNOT reject OLS-consistency null, NOT evidence FOR). Pesaran-Taylor filter
  - **§4.3.5 ClarityCEO vs UncResCEO asymmetry footnote**: Option 4 (locked) — different statistical structures (CEO-level trait vs call-level residual with within-CEO mean = 0 by construction) require different identification tools. Asymmetry reflects underlying variables, not coverage gap

### §5 Discussion and Conclusion

- Summary of findings (decomp form)
- Channel-asymmetry synthesis: insider (cash) loads Clarity NEG + UncRes POS (both Q&A components); outsider (spread + SEC) loads UncPre. Three empirical patterns across §3, §4.1, §4.2 sit cleanly on DWZ's own scripted-vs-improvised structure
- Mechanism disclosure: financing-margin (cash) and outsider-margin (spread + SEC) operate through theoretically distinct mechanisms; no causal-bridge claim
- Limitations
- Future research

## Suite allocation v6

| Location | Suites | Notes |
|---|---|---|
| **§3.2 HC** | H1.ceo2.decomp + H1.ceo2.decomp.qtrexp | 3-IV decomp |
| **§3.3 HFC** | H1.2.ceo2.decomp + H1.2.ceo2.decomp.qtrexp | 3-IV decomp |
| **§3.4 CFvol channel** | H1.3.cfvol | NEW — same pattern as HFC at ~85% mag |
| **§4.1 Drivers** | H11 + H11-Lag1 + H11-Lag2 + H24 + H24b + H23 | tab:driver_matrix consolidates |
| **§4.2.1 Spread** | H14c.ceo2.decomp | 3-IV decomp; replaces H14c parent in thesis_suites |
| **§4.2.2 SEC** | H18.ceo2.decomp | NEW |
| **§4.3 Endogeneity** | H.death.did + H.dwz.fd + H.lewbel.iv | NEW — 3 designs |
| **DROPPED entirely** | H1.4.hedging_needs (0/8 sig); H14c parent (replaced by decomp); all v5.1 dropped suites |

### thesis_suites: changes in `config/suite_render_order.yaml`

ADD: `H.death.did`, `H.dwz.fd`, `H.lewbel.iv`, `H1.3.cfvol`, `H18.ceo2.decomp`, `H23` (already in suites:; ADD to thesis_suites:)
REMOVE: `H14c` (parent, replaced by H14c.ceo2.decomp which is already in thesis_suites)
KEEP UNCHANGED: existing 14 thesis_suites entries except H14c parent

## Reference stack v6 (additions to references.bib)

| Cite key | Paper | Role | NLM verbatim status |
|---|---|---|---|
| `bertrand2003` | Bertrand & Schoar 2003 QJE | H1 manager-FE-on-cash channel anchor | ✓ `reference_bertrand_schoar_2003_verbatim.md` |
| `acw2004` | Almeida, Campello, Weisbach 2004 JF | H2 amplification anchor (§II.D verbatim) | ✓ `reference_almeida_campello_weisbach_2004_verbatim.md` |
| `hanqiu2007` | Han & Qiu 2007 JCF | H1.3 CFvol moderator anchor | ✓ `reference_han_qiu_2007_verbatim.md` |
| `bennedsen2020` | Bennedsen, Pérez-González, Wolfenzon 2020 JF | §4.3.2 sudden-death DiD anchor | ✓ `reference_bennedsen_perezgonzalez_wolfenzon_2020_verbatim.md` |
| `ghafoor2023` | Ghafoor, Yousaf, Li 2023 SSRN | §4.3.2 cash-DiD precedent | ✓ `reference_ghafoor_yousaf_li_2023_verbatim.md` |
| `lewbel2012` | Lewbel 2012 JBES | §4.3.4 het-IV anchor | optional — methodology cite |
| `dzielinski2021` (already in bib) | Add §6 first-difference cite for §4.3.3 | already verbatim |

DOI verification via WebSearch / Crossref before write.

## Phase plan (v6 rewrite)

**Phase 1 (this commit)**: skeleton v6 + charter + branch + tag + archive old sections
**Phase 2**: Abstract + §1 intro
**Phase 3**: §2 framework
**Phase 4**: §3 main (HC + HFC + CFvol with 3-IV decomp)
**Phase 5**: §4.1 drivers (4 drivers via driver_matrix)
**Phase 6**: §4.2 outsider reaction (spread + SEC)
**Phase 7**: §4.3 endogeneity (3 designs + Option 4 footnote)
**Phase 8**: §5 conclusion
**Phase 9**: bib additions + suite_render_order.yaml update + final render verification + advisor pass

**Each phase**: atomic commit + WAKE_UP doc in memory.

## Failure-mode rule (per user 2026-04-29)

Stop + WAKE_UP doc + wait. Never ship silent contradiction.
- NLM down → use claim only if already-verified in lock doc; else stop
- Runner data conflicts with locked claim → STOP + escalate
- Locks contradict each other → authority hierarchy (DWZ-anchor 2026-04-27 > H1/H2 2026-04-28 > endo lit 2026-04-28) AND escalate
- LaTeX render fails → debug 3 attempts, then stop

## Quality gates (per phase)

1. Framing match: explicit cross-reference to relevant lock doc paragraph
2. Numbers programmatic: extract from suite_spec.json, never type
3. Citations exist: every `\citeA{}` resolves in references.bib
4. Render clean: 0 undefined refs, 0 missing citations
5. Atomic commit (specific files, never push)

## What stays from v5.1

- main.tex shell (preamble, geometry, twocolumn, apacite, hyperref) — verified working
- Appendices B/C/D — already 3-IV-decomp-aware (appendix_b updated 2026-04-27)
- references.bib base 17 entries — keep, only ADD per "additions" table above
- variable_definitions.tex (90 entries, NLM-verified)
- generate_all_tables.py + generate_summary_stats.py (auto-render)
- suite_render_order.yaml structure (only thesis_suites: list mutates)

## Cross-references

- `project_dwz_anchored_framing_locked_2026_04_27.md` — §3 + §4.2 + §5 spec
- `project_h1_h2_theoretical_framing_locked_2026_04_28.md` — §2 spec
- `project_endogeneity_lit_review_2026_04_28.md` — §4.3 anchors
- `project_session_2026_04_29_uncrescco_asymmetry_brainstorm.md` — Option 4 footnote prose
- `project_session_2026_04_29_h_lewbel_iv_complete.md` — Lewbel headline diagnostics
- `project_session_2026_04_29_h_dwz_fd_complete.md` — DWZ FD specs
- `project_session_2026_04_29_phase_e_complete.md` — sudden-death DiD specs
- v5.1 archived at git tag `draft-v5.1-pre-rewrite`; sections at `docs/Draft/sections/_archived_2026_04_22/`
