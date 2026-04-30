# v7 Thesis Draft — Decisions Ledger

**Started:** 2026-04-29
**Workflow:** big-picture → small-picture, branch-by-branch, step-by-step
**Existing draft:** to be archived (not deleted) inside `docs/Draft/`. New v7 draft built parallel.

---

## Process / current step

- [x] Step 0a — open decisions ledger
- [ ] Step 0b — read template + extract structure constraints
- [ ] Step 1 — lock thesis structure (sections + subsections per template, mapped to thesis content)
- [ ] Step 2 — inventory empirical findings (in / out)
- [ ] Step 3 — lock narrative anchor (story arc)
- [ ] Step 4 — archive old draft into `docs/Draft/_archived_v6/`
- [ ] Step 5 — scaffold new v7 LaTeX set with locked structure (blank shells, two-column top-journal style per template mandate)
- [ ] Step 6 — populate big-picture-first (section abstracts → subsection abstracts → ¶ scaffolds → final prose)
- [ ] Step 7 — wire generated tables + variable definitions appendix + bibliography
- [ ] Step 8 — compile + audit + commit

---

## Template — read 2026-04-29

**Source:** `docs/Draft/DraftTemplate.txt`

**Style mandate (line 1):**
> two column style mandatory with traditional styling, according to fin/econ traditional top journal design.

**Roman-numeral section convention** (I. II. III. IV. V.).

**Structure outline (per template):**

| Section | Subsections (template guides) |
|---|---|
| Title block + abstract | Title / Authors / Affiliations / Abstract / Keywords / JEL |
| **I. Introduction** | (single block in template — sub-structure thesis-author choice) |
| **II. Conceptual Framework and Empirical Strategy** | (5 subsections suggested) Conceptual Framework / [Theory + Main Construct + Research Logic] / [Estimation of Main Variable(s)] / [Methodology / Empirical Design] / [Specification and Measurement of Key Constructs] |
| **III. Main Empirical Analyses** | (4 subsections suggested) Data / Sample / Variable Construction / Main Analysis 1 / Main Analysis 2 / Main Analysis 3 |
| **IV. Additional Analyses** | (2 subsections suggested) Additional Analysis 1 / Additional Analysis 2 |
| **V. Conclusion** | (single block) |
| **References** | apacite |
| **Appendix: Variable Definition and Measurement** | Dependent Variables / Independent Variables |
| **Tables** | T1 Summary Stats + 8 main tables T2-T9 |

**Implications for v7 structure:**
- Tighter than v6 (v6 had §2.1 Pre-Commitment + §3.5 Robustness Notes + §4.3.5 Asymmetry that don't map to template subsections)
- Template suggests 4 main analyses in §III not 5 (collapse §3.5 robustness into §3.1 setup; collapse HC + HFC + CFvol into 3 main analyses)
- Template suggests 2 additional-analysis blocks in §IV not 3 (collapse drivers + reaction + endogeneity into 2 blocks, OR keep as 3)
- Tables: 9 max suggested. Currently we have 14+ body suite tables. Demands prioritization.

---

## Decisions log (chronological)

### D24 — 2026-04-29 — Pre-Commitment Statement formally killed
**Decision:** v6 §2.1 Pre-Commitment Statement removed entirely from v7. Pre-registration framing absorbed into §II.2 Hypothesis Development (each hypothesis has its formal statement + theoretical anchors + tail direction stated explicitly).
**Rationale:** v6 §2.1 was empirical filler — every load-bearing claim was restated in §2.4 (now §II.2) or §1.4 (now §I).

### D23 — 2026-04-29 — Wide regression tables = sidewaystable* (landscape pages)
**Decision:** Standard JF/JFE/RFS practice for 12-column regression tables. Body in two-column; wide tables on dedicated landscape pages with content upright.

### D22 — 2026-04-29 — §V Conclusion structure = 3 subsections (Summary / Limitations / Future Work)
**Decision:** Deviation from template's single-block §V (template line 94-96). Three subsections give navigable structure for committee/referee review.

### D21 — 2026-04-29 — Tables placement = end of document (after refs + appendix)
**Decision:** Per template line 116. Standard for top-journal submission.

### D20 — 2026-04-29 — Variable Definitions appendix = 4 sections (DV / IV / Controls / Moderators)
**Decision:** Top-journal navigability beats template's 2-section minimum. DV (Cash, Lead Cash, Spread, CCCL); IV (ClarityCEO, UncResCEO, UncPreCEO, drivers); Controls (Bates base + extended); Moderators (Unrated, HighCFvol).

### D19 — 2026-04-29 — Hypothesis statement format = bold label + italicized declarative
**Format example:** **Hypothesis 1.** *An increase in CEO speech uncertainty during an earnings call is associated with a higher cash-to-assets ratio at the firm.*

### D18 — 2026-04-29 — §IV.B title = "Disclosure-Insufficiency Channel: CCCL"
**Verbatim source:** Lerman, Steffen, Zhang (2026?, NLM session 3f2ff407). Abstract: "the SEC primarily references these voluntary disclosures to illustrate **insufficiencies** and, less commonly, **inconsistencies** in mandatory filings". §3.2 p.5: 80% of CCCLs flag insufficient disclosure; 15% flag inconsistent info; 3% concern call disclosures themselves.
**Decision:** §IV.B subsection title = "Disclosure-Insufficiency Channel: Conference-Call Comment Letter (CCCL)". Mechanism: SEC reviewers reference the call to flag gaps in mandatory filings.
**Variable form:** binary indicator, linear probability model. Sample 2005-2018 AA, n=13,808 / 3,902 firms.
**v6 framing correction:** v6 §4.2.2 said "we measure SEC scrutiny via CCCL" — empirically loose. CCCL doesn't measure scrutiny generically; it measures specifically whether SEC references the call to flag disclosure-gap (80% of CCCLs).

### D17 — 2026-04-29 — §II.5 drivers = 1 composite table
**Decision:** Single §II.5 construct-validity table with 4 driver coefficients side-by-side as columns (PRisk + US-EPU + GEPU + TSIMM). Top-journal standard.

### D16 — 2026-04-29 — §I Introduction = single flowing block (no subsections)
**Decision:** Per template line 32-34. One coherent intro narrative — motivation → gap → approach → findings → contributions → roadmap, all in one §I.
**Implication:** v6 §I had 6 subsections; v7 collapses to one block.

### D15 — 2026-04-29 — §III.E Endogeneity = 1 composite table, 3 panels
**Decision:** Single §III.E table. Panel A Death DiD; Panel B DWZ FD; Panel C Lewbel IV. Tightens body footprint; matches top-journal endogeneity-package convention.

### D14 — 2026-04-29 — §IV.A title = "Market Information-Asymmetry Channel: Post-Call Bid-Ask Spread"
**Decision:** §IV.A subsection title locks mechanism-first naming (BGT 2018 + Amihud 2002 anchor).

### D13 — 2026-04-29 — §IV = two distinct channels (H2 market info-asymmetry + H3 disclosure-insufficiency)
**Decision:** §IV.A = H2 (market info-asymmetry channel: Spread). §IV.B = H3 (disclosure-insufficiency channel: CCCL). Two different parties (traders vs SEC reviewers) + two different processes (price formation vs disclosure-gap detection) = genuinely distinct channels.

### D12 — 2026-04-29 — §II.1 + §II.2 lit-review structure: precautionary motive + 2 triggers + specific papers
**Decision:**
- §II.1 Conceptual Framework: precautionary motive overview (OPSW 1999 + Bates 2009 anchor); points at the two testable amplification triggers
- §II.2 Hypothesis Development: full theoretical anchors for H1 + H1a + H1b
  - H1 anchor: OPSW 1999 + Bates 2009 (precautionary cash motive); DWZ 2021 (speech-uncertainty as real-time signal); BS 2003 (CEO-trait channel)
  - H1a anchor: FP 2006 (binary rated/unrated, "credit constrained") + ACW 2004 §II.D (macro-shock asymmetry)
  - H1b anchor: Han-Qiu 2007 (CFvol → cash; CV(CF) 16-quarter)
- Drop "two channels" framing; write "two triggers of the same precautionary channel"
**Each hypothesis paragraph cites its specific anchor papers explicitly.**

### D11 — 2026-04-29 — §II.2 hypothesis labels = H1 + H1a/H1b
**Decision:** H1 (main cash response) + H1a (financing-friction trigger amplification) + H1b (CF-volatility trigger amplification). Sub-letter notation reflects parent-child structure: H1a/H1b are amplification predictions UNDER H1's precautionary channel.
**Rationale:** standard top-journal practice for nested channel decomposition (cf. ACW 2004 use sub-numbered constraint tests).

### D10 — 2026-04-29 — Single precautionary channel with two triggers (supersedes D6, D9)
**Trigger:** user correction — both HFC and CFvol are SAME precautionary channel, different triggers. Not two distinct channels.
**Evidence:** Han-Qiu 2007 paper title is "Corporate Precautionary Cash Holdings" — explicitly precautionary. FP 2006 + ACW 2004 mechanism (Unrated firms hoard cash because no debt-market access) is also precautionary. The difference is what STRESS triggers the precautionary response: financing-friction trigger vs CF-volatility trigger.
**Decision:**
- §II.2 Hypothesis Development states ONE precautionary channel; H1 main effect; H1a + H1b = two amplification predictions under different stress triggers
- §III.C subtitle: "Precautionary Amplification: External-Financing-Friction Trigger" (FP+ACW)
- §III.D subtitle: "Precautionary Amplification: Cash-Flow-Volatility Trigger" (Han-Qiu)
- Drop "two channels" framing in v7 prose. Use "two triggers of the same precautionary channel".
**Implications for §IV (Spread + CCCL):** distinct from §III precautionary channel — outsider channels operate via information-asymmetry / regulatory-review mechanisms. §IV is genuinely a different mechanism, NOT a third trigger of the precautionary channel.

### D9 — SUPERSEDED by D10 — kept for audit trail
~~5-subsection §III separating HFC and CFvol as distinct "channels"~~. Subsection layout retained, but framing changes from "two channels" to "two triggers of one precautionary channel".

### D8 — 2026-04-29 — §IV.B regulatory channel terminology = CCCL not SEC
**Trigger:** user correction.
**Decision:** §IV.B variable is "Conference-Call Comment Letter (CCCL) indicator" per Lerman et al. paper title and v6 prose §4.2.2 line 44 ("conference-call-comment-letter (CCCL) indicator"). Drop "SEC Comment Letter" as the channel name in v7. Use "CCCL" or "Regulatory Channel: CCCL" as subsection title.
**Verification COMPLETE 2026-04-29:** Lerman paper publication metadata (per user-provided paper masthead): Received July 5, 2023; Revised October 1, 2024 + June 11, 2025; Accepted July 30, 2025; **Published Online in Articles in Advance January 30, 2026**. Cite key updated `lerman2024` → `lerman2026`; year updated `{2024}` → `{2026}`. Bib note now reads "Articles in Advance, Published online January 30, 2026". 3 v6 prose files updated to `\citeA{lerman2026}`.
**File reference:** `docs/Draft/references.bib` line 291.

### D7 — 2026-04-29 — §IV layout = 2 subsections (Spread + CCCL)
**Decision:** §IV.A Market Channel: Post-Call Bid-Ask Spread. §IV.B Regulatory Channel: CCCL. Matches template's 2-block §IV.

### D6 — 2026-04-29 — §III layout = HC → constraint amplification (combined) → endogeneity
**Decision:**
- §III.A Data, Sample, Variable Construction
- §III.B Cash Holdings (HC) — primary cash result
- §III.C Constraint Amplification (Unrated + CFvol combined in single subsection — ACW asymmetry test through two proxies)
- §III.D Endogeneity (Death DiD + DWZ FD + Lewbel pulled into §III as endogeneity package)
**Implications:** §IV becomes outsider-reaction-only (Spread + CCCL).

### D5 — 2026-04-29 — Drivers (PRisk + US-EPU + GEPU + TSIMM) → §II construct validity
**Decision:** Move 4 driver suites from §IV into §II.5 Specification and Measurement of Key Constructs (template's slot for measurement-construct validation). Drivers shown as construct-validity tests of CEO speech-uncertainty measure against external uncertainty drivers. 4 suites → 1 composite table or appendix table (final granularity TBD).
**Rationale:** (i) clears §IV to fit template's 2-block structure; (ii) drivers are validation of measurement, not outcome tests, so §II is theoretically correct location; (iii) reduces total table count.

### D4 — 2026-04-29 — Narrative anchor = precautionary-cash main + DWZ-extension secondary
**Decision:** Primary contribution framing is precautionary-cash (real-time CEO speech-uncertainty signal predicts firm precautionary cash holdings, anchored on OPSW + Bates). Secondary framing is DWZ-extension (the measurement architecture is borrowed and extended from DWZ 2021's three-component decomposition; we apply their architecture to a financing-policy outcome class their paper does not test).
**Implication for prose:** lead with the precautionary-cash result, follow with "we use DWZ 2021's architecture as the measurement tool, extending its application to firm financing-policy outcomes". Insider-outsider asymmetry is a third-order observation, not the headline.

### D1 — 2026-04-29 — Discard v6 paragraph-by-paragraph audit; rewrite v7 from scratch
**Trigger:** §2.1 audit revealed §2.1 = filler; §3.1 audit revealed HC/HFC/CFvol naming asymmetry. Two data points + user observation that "all of it is useless".
**Decision:** Build v7 LaTeX set fresh. Old v6 preserved in archive folder. v7 follows `DraftTemplate.txt`.
**Workflow:** big-picture → small-picture, step-by-step, branch-by-branch.
**Rationale:** v6 prose has structural cruft inherited from v5 (Mgr-pool, capex appendix, BelowIG three-tier). Audit-and-edit becomes whack-a-mole. Rewrite from locked structure faster.
**Risk:** lose 7+ honest disclosures embedded in v6 prose. Mitigation: old draft preserved; cherry-pick disclosures during v7 population.

### D2 — 2026-04-29 — Section order matches template
**Decision:** Roman-numeral sections (I-V) + Abstract + References + Appendix + Tables, exact template order.
**Rationale:** Template is mandatory — top-journal fin/econ style requirement.

### D3 — 2026-04-29 — All decisions recorded here
**Decision:** Every structural decision, scope decision, finding-include/exclude decision, narrative decision logged in this file with date + rationale.
**Rationale:** Cross-session durability; future reference; audit trail.

---

## Pending decisions (to lock in Step 1-3)

### PD1 — §III subsection count
Template suggests 4 (Data + 3 analyses). Current empirical body fits 3 main analyses (HC + HFC + CFvol) → matches template. **Lock as 1 + 3 = 4 subsections.**

### PD2 — §IV subsection count
Template suggests 2. Current §4 has 3 sub-blocks (drivers + outsider reaction + endogeneity). Three options:
- (a) Collapse to 2: e.g., "Construct Validity and Outsider Reaction" + "Identification" — drops driver/reaction asymmetry framing
- (b) Stretch to 3: keep current granularity, deviate from template's 2-suggested
- (c) Restructure: drivers move to §II (construct validity); §IV is reaction + endogeneity (=2 blocks per template)
→ NEEDS DECISION

### PD3 — Hypothesis labels (HC / HFC / CFvol)
v6 has HC + HFC formal labels in §2.4; CFvol no formal label.
Options:
- (a) Promote: H1 (HC) / H2 (HFC) / H3 (HCFvol)
- (b) Demote: drop HC/HFC labels; just use "Hypothesis 1/2/3" with descriptive subsection titles
- (c) Verbatim hypothesis statements: write each hypothesis as a numbered, italicized declarative sentence
→ NEEDS DECISION

### PD4 — Pre-Commitment Statement (v6 §2.1)
v6 §2.1 = filler per audit. Options:
- (a) Drop entirely; absorb pre-registration framing into §2.4 Hypothesis Development
- (b) Keep as 1-paragraph block at end of §II (compressed to ~80 words)
→ NEEDS DECISION

### PD5 — Empirical findings inventory — what makes the cut
v7 §III + §IV must report a tight subset. Currently 14+ suite tables exist. Template suggests 9 max. Need to lock:
- Body tables (HC main / HFC main / CFvol main) — clear KEEP
- §IV.drivers (4 drivers: PRisk + US-EPU + GEPU + TSIMM) — KEEP / DROP / which?
- §IV.reaction (Spread + SEC) — KEEP / DROP / which?
- §IV.endogeneity (Death DiD + DWZ FD + Lewbel) — KEEP / DROP / which?
→ NEEDS DECISION

### PD6 — Narrative anchor / story arc
Three candidates:
- (a) DWZ-extension thesis: "we extend DWZ 2021 from market/governance to firm financing-policy" (current v6 framing)
- (b) Insider-outsider asymmetry thesis: "two segments of the call carry signals to two audiences" (current v6 secondary framing)
- (c) Precautionary-cash thesis: "earnings-call CEO speech uncertainty is a real-time precautionary-cash signal" (closer to OPSW/Bates roots)
→ NEEDS DECISION

### PD7 — Two-column body width: text vs tables
Template mandates two-column traditional fin/econ design. Tables are wide (12 cols × bordered). Use `sidewaystable*` (current v6 approach) or condense tables to fit two-column? Top journals (JF, JFE, RFS) use sidewaystable for wide regression results — KEEP `sidewaystable*` is current default and template-compatible.
→ Recommended LOCK: keep `sidewaystable*` for body regression tables.

---

## Empirical findings inventory (Step 2 — pending)

(populated when we walk through suite_spec_index.json subsection by subsection)

---

## Narrative anchor (Step 3 — pending)

(populated after structure + findings locked)

---

## Archive plan

When approved (Step 4):
- New folder: `docs/Draft/_archived_v6_2026_04_29/`
- Move into it: all `sections/*.tex` v6, `main.tex` v6 backup, `THESIS_SKELETON.md` v6, `appendix_c_robustness.tex` v6, `abstract.tex` v6, plus `_archived_2026_04_22/` (already there) consolidated as nested
- KEEP at top of `docs/Draft/`: `references.bib`, `variable_definitions.tex` (will be revised), `per_suite/` auto-tables, `summary_stats.tex` auto, generation scripts, this `v7_DECISIONS.md`, `CANONICAL_FACT_SHEET.md`
- New v7 files in `docs/Draft/sections/` after archive

---

## Reference resources locked at Phase 0

| Asset | Path | Purpose |
|---|---|---|
| Per-cell numbers | `tmp/suite_spec_index.json` | every β/p/n for 15 suites; never retype |
| Suite summary | `docs/Draft/CANONICAL_FACT_SHEET.md` | sig-count summary table; programmatic |
| Theoretical anchors | `~/.claude/projects/.../memory/reference_*_verbatim.md` | DWZ + ACW + ACW2007 + BS + FP + OPSW + Bates verbatim |
| Locked framings | `~/.claude/projects/.../memory/project_dwz_anchored_framing_locked_2026_04_27.md` + `project_h1_h2_theoretical_framing_locked_2026_04_28.md` | story-arc constraints |
| Generated tables | `docs/Draft/per_suite/*_table.tex` | auto from generate_all_tables.py |
| Bibliography | `docs/Draft/references.bib` | apacite-keyed |
