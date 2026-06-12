# PROPOSITION IDENTIFICATION RULES (v1)

**Job.** Turn each seed in `thesis_propositions.json` into one or more proposition rows.
**Audience.** A model with NO judgment. You do not decide "what matters." You run mechanical
surface tests and emit a row whenever a test fires. Closed lists only. When unsure, you DO NOT
skip — the fallback (Rule Z) forces a row.

**Golden rule.** RECORD, NEVER JUDGE-OUT. Over-emission is fine (the user trims). Under-emission
is failure. If a seed could plausibly fire two triggers, fire BOTH.

---

## 0. How to process ONE seed

For each seed object (in `seq` order):

1. Read `verbatim_span`, `block`, `note`.
2. If `block` is a SPECIAL block → go to §4 (fixed assignment), done.
3. Otherwise run all 13 triggers T1–T13 (§2) as yes/no surface tests.
4. For every trigger that FIRES, emit one row using its template (§3).
5. If ZERO of T1–T12 fired → emit exactly one K row (Rule Z, §2 T13).
6. Fill the bookkeeping fields (§5): `id`, `role`, `p2_ref`, `depends_on`.
7. Never edit `seq`, `block`, `file_line`, `verbatim_span`.

One seed → ≥1 row. A multi-claim seed → many rows that SHARE its `seq`/`file_line`/`verbatim_span`
but get distinct `id`s (`INT-015a`, `INT-015b`, …).

---

## 1. Closed lists (the ONLY vocabulary you may use)

### 1A. CITED-AUTHOR → bibkey  (surname tokens; trigger T2 named-no-cite)
| surname token(s) in span | bibkey |
|---|---|
| Dzielinski / Wagner / Zeckhauser / "Dzielinski--Wagner--Zeckhauser" | dwz |
| Loughran / McDonald / "Loughran--McDonald" | lm2011 |
| Baker / Bloom / "Baker--Bloom--Davis" | baker2016 |
| Davis (+ "global") | davis2016 |
| Hassan | hassan2020 |
| Hoberg / Phillips / "Hoberg--Phillips" / TNIC | hoberg2010+hoberg2016 |
| Bushee / Gow / Taylor | bushee2018 |
| Everhart / Kravet / McVay / Warren | everhart2025 |
| Gokkaya / Liu / Stulz | gokkaya2025 |
| Lerman / Steffen / Zhang | lerman2026 |
| Ragozzino / Reuer | ragozzino2024 |
| Thewissen / Arslan-Ayaydin | thewissen2024 |

> Ambiguity rule for "Davis": if span also contains "global" → davis2016; if "Baker"/"Bloom"
> present → baker2016; if both senses plausible, emit BOTH (over-emit).

### 1B. DATA VENDORS (trigger T3 uncited-source)
`Capital IQ`, `SDC`, `Compustat`, `CRSP`, `IBES`. (NBER appears only in the bibliography.)

### 1C. LIT-PHRASES → mapping (trigger T4; each phrase has a FIXED route+bibkeys)
| phrase (substring, case-insensitive) | route | bibkeys |
|---|---|---|
| "growing literature" | nlm | thewissen2024, ragozzino2024, everhart2025, gokkaya2025 |
| "nearest work" / "the nearest" / "nearest to" | nlm | thewissen2024, ragozzino2024 |
| "two papers closest to ours" | bib | (AMBIGUOUS — note "which two unstated") |
| "what this work has not measured" / "left empty" / "uncertainty dimension is still missing" | nlm | thewissen2024, ragozzino2024, everhart2025, gokkaya2025 |
| "standard cash regression" / "determinants of cash" | missing-cite | (none — NEEDS-CITATION: determinants-of-cash lit) |
| "established precedent" / "established uncertainty measures" | nlm-or-missing | (if a bibkey/surname is in the same span → nlm to it; else missing-cite) |

### 1D. METHOD MARKERS (trigger T7 method-review) — substring, case-insensitive
`we estimate`, `we regress`, `regress`, `fixed effect`, `fixed-effect`, `two-way`, `2WFE`,
`clustered`, `cluster`, `OLS`, `one-tailed`, `two-tailed`, `Wald`, `interact`, `pooled`,
`matched universe`, `event study`, `event-time`, `difference-in-differences`, `placebo`,
`baseline`, `exclud`, `drop`, `cap` (window), `winsor`, `lag`, `partial-adjustment`,
`tokeniz`, `parsed`, `link table`, `match` (record linkage), `require at least`, `qualif`,
`sample`, `tercile`, `median`, `decomposition`, `residual ... regress`.

### 1E. HYPOTHESIS / PREDICTION MARKERS (trigger T8 logic-check, role=hypothesis)
`\textbf{H` , `H1`, `H1a`, `H1b`, ` should `, `predicts`, `prediction`, `should be elevated`,
`should follow`, `should resolve`, `should persist`.

### 1F. INFERENCE CONNECTIVES (trigger T9 logic-check, role=inference) — substring
`so `, `therefore`, `thus`, ` hence `, `because`, `licenses the reading`, `implies`,
`is the trace predicted`, `is the differential-timing prediction`, `we read it as`,
`we read this as`, `this is the`, `follows the`, ` so that `, `which is what makes`.

### 1G. CAVEAT / LIMITATION MARKERS (trigger T10 logic-check, role=caveat) — substring
`not a `, `not yet`, `claim no`, `no identification`, `correlational`, `failure to find`,
`fragile`, `supported but`, `limit`, `limitation`, `does not exclude`, `not proof of absence`,
`not a powered`, `not itself a test`, `deliberately hedged`, `at one remove`, `cannot`,
`leaves ... open`, `not a headline`, `not pillars`.

### 1H. RESULT-NUMBER MARKERS (trigger T5 internal-verify) — regex
A seed fires T5 if it matches ANY of:
`-?\d*\.\d+` (decimal) · `\bSE\b` · `%` · `R\^?2` · `\bn\.s\.\b` · `\b\d{2,3},\d{3}\b`
(firm-quarter counts) · `significant at` · `\d+\\?%\s*level` · `p<`.

### 1I. FORMULA / DEFINITION MARKERS (trigger T6 formula-check)
- span contains inline math `$...$`, OR
- substring `equation 1`/`equation 4`/`equation-4`/`equation (4)`, OR
- `block == appendix-vartable` AND span matches `^<Name> & <def>` (a `&`-delimited row).

### 1J. CONSISTENCY / CROSS-REF EQUIVALENCE MARKERS (trigger T12 consistency) — substring
`same table`, `same event`, `as in Main Analysis`, `otherwise that of`, `the same as`,
`identical`, `nearly identical`, `economically the same`, `same forces`, `same way`,
`reproduces the run-up`, `against 0.0461 there`. (Plain `Table~\ref{}` alone does NOT fire —
label existence already verified in P1.)

---

## 2. The 13 triggers (run ALL on every non-special seed)

| # | FIRES when span … | category | route | role |
|---|---|---|---|---|
| **T1** | contains `\citep{` or `\citet{` | A (one row PER bibkey inside the braces; split comma-lists) | nlm | premise |
| **T2** | contains a surname from §1A AND that bibkey is NOT already covered by a T1 cite in the same span | A | nlm | premise |
| **T3** | contains a vendor from §1B AND no `\cite` covering it | B | missing-cite | premise |
| **T4** | contains a lit-phrase from §1C | A or B (per table) | per table | premise |
| **T5** | matches a §1H number marker | E (ONE row per seed; list ALL number tokens) | internal-verify | result |
| **T6** | matches a §1I formula marker | D (one row per distinct equation/`$...$`/vartable-row) | formula-check | formula/definition |
| **T7** | contains a §1D method marker | C | method-review | design |
| **T8** | contains a §1E hypothesis marker | G | logic-check | hypothesis |
| **T9** | contains a §1F inference connective | F | logic-check | inference |
| **T10** | contains a §1G caveat marker | H | logic-check | caveat |
| **T11** | `block == bibliography` | I (see §4) | bib | metadata |
| **T12** | contains a §1J equivalence marker | J | consistency | consistency |
| **T13 (Rule Z)** | NONE of T1–T12 fired | K | none | rhetoric |

**Roadmap exception.** If span starts with `Section~\ref` or contains `proceeds as follows` /
`The rest of the paper` → force K, role=`roadmap` (overrides T12 if only a bare ref fired).

**Caps note.** T5 also fires on a number that is a method threshold ("at least five calls",
"50% cash", "+4 quarters", "1993--2024"). Those ALSO fire T7. Emit both the C row and the E row;
the C-row note carries the threshold, the E-row lists the number. Over-emit, never choose.

---

## 3. Emit templates (NO paraphrase — copy the trigger clause verbatim)

`proposition` is written by COPYING the minimal clause around the trigger, prefixed by a fixed stem:

| cat | proposition stem | mapped_bibkey | note must contain |
|---|---|---|---|
| A | `Attributed to {bibkey}: "{verbatim clause}"` | the bibkey | which paper-fact to verify |
| B | `Uncited external reference: "{verbatim clause}"` | null | what source is missing |
| C | `Design/method choice: "{verbatim clause}"` | null | the estimator/filter/threshold |
| D | `Definition/formula: "{verbatim clause}"` | bibkey if borrowed else null | the var name + RHS |
| E | `Own result: {list EVERY number token, comma-sep} — "{outcome clause}"` | null | table ref if present |
| F | `Inference: "{verbatim clause}"` | null | what must follow / hidden assumption |
| G | `Prediction {Hx}: "{verbatim clause}"` | null | the predicted sign/timing |
| H | `Self-limitation: "{verbatim clause}"` | null | what is conceded |
| I | (parsed fields, §4B) | the bibitem's key | — |
| J | `Cross-reference equivalence: "{verbatim clause}"` | null | which locations must agree |
| K | `""` (empty) | null | "rhetoric/transition" or "roadmap" |

Rule: the `{verbatim clause}` MUST be a contiguous substring of `verbatim_span`. If you cannot
copy it verbatim, you are paraphrasing — STOP and copy the whole span.

---

## 4. SPECIAL blocks (fixed assignment — skip T1–T13)

### 4A. `front-matter` title-block (note = `title-block:*`)
- `title` → I, route bib, role metadata, prop `Metadata: thesis title`.
- `author` → I, route bib, role metadata.
- `date` → I, route bib, role metadata.
(These are not literature; route bib just means "check the title-page facts," here trivially self.)

### 4B. `bibliography` (T11) — parse each bibitem into fields, ONE I row:
`proposition = "Bib metadata: {authors} ({year}) '{title}' — {venue}"`, `mapped_bibkey` = the
key from `note` (`bibitem:KEY`), route bib, role metadata. The verify stage checks year/venue/title
vs the NLM title page. Flag in note any pre-known issue (e.g. davis2016 "NBER WP 22740" vs body
"global EPU"; gokkaya "Dice WP 2024-04, June 2025"; thewissen "SSRN 4900453, 2024"; dwz "M-RCBG
2017-02, rev 2021").

### 4C. `appendix-vartable` rows (note = `table-row`)
- If span matches `^<Name> & <definition>` → emit **D** (formula-check, role=definition),
  `proposition = "Definition: {Name} = {definition verbatim}"`. THEN also run T2/T4 on the
  definition text — if a surname/phrase appears (e.g. "Hassan et al.", "Baker--Bloom--Davis",
  "Davis global", "Hoberg--Phillips", "\citet{dwz}") emit an additional A row. (Over-emit.)
- If span is `\multicolumn...{group label}` or `Variable & Definition` (header) → K (none),
  role=rhetoric, note "vartable group header".

### 4D. `tables` pointer (`\input{...}`)
One J row, route consistency, role=consistency, prop `Pointer: table cells in thesis_tables.tex
(P2-verified)`, p2_ref = "findings.json (P2 numeric audit)".

### 4E. `appendix-prose` (`\noindent ...`)
Strip the leading `\noindent`, then process the remainder through T1–T13 normally.

---

## 5. Bookkeeping fields (mechanical maps)

### 5A. `id` — `{BLOCKPREFIX}-{seq3}{letter}`
BLOCKPREFIX (fixed): front-matter→`FM`, Introduction→`INT`, Conceptual Framework→`CF`,
Hypothesis Development→`HYP`, Estimation of the Main Variable→`EMV`, Methodology and Empirical
Design→`MED`, Specification and Measurement of Key Constructs→`KC`, Data Sample and Variable
Construction→`DS`, Main Analysis 1→`MA1`, Main Analysis 2→`MA2`, Main Analysis 3→`MA3`,
Ruling Out Analyst Scrutiny→`RAS`, The Presentation-Side Contrast→`PSC`, Summary of Findings→`SUM`,
Contributions→`CON`, Limitations→`LIM`, Directions for Future Research→`FUT`, bibliography→`BIB`,
appendix-prose→`APX`, appendix-vartable→`VAR`, tables→`TAB`.
`seq3` = the seed's `seq` zero-padded to 3. `letter` = `a,b,c…` when a seed emits multiple rows
(single-row seed gets no letter).

### 5B. `role` ← fixed from category (§2 table). If multiple categories on one seed, each row
carries its own category's role.

### 5C. `p2_ref` — set ONLY for C and E rows, by block (link, don't re-verify):
- E rows in MA1/MA2/MA3/RAS/PSC → `findings.json (P2 numeric audit); verify_draft_numbers.py`.
- C rows touching winsorization → `methodology_audit.json#M2-03`.
- C rows touching post-withdrawal drop / 2nd-announcement truncation / window cap → `methodology_audit.json#M2-04`.
- C rows touching tails (one/two-tailed) → `methodology_audit.json#M2-02`.
- else null.

### 5D. `depends_on` — add the referenced id when span contains (mechanical):
- `equation 4` / `equation-4` / `their equation 4` → the DWZ-eq4 definition row (canonical: the
  DS block "Following \citet{dwz}, we regress UncAnsCEO…" row).
- `equation 1` → the UncPreCEO eq-1 row.
- `H1`/`H1a`/`H1b` → the matching HYP row.
- `Main Analysis 1/2/3` → that analysis's first (design) row.
Keep sparse; only when the span literally leans on the earlier item.

---

## 6. DEDUP (for the later NLM stage, recorded now)
The same paper-fact recurs (DWZ eq-4 at seq 5, 23, 52, 54, 80, 82, 204; UncPre eq-1 at 54, 82, 205).
Each gets its OWN A/D row (record every instance), but tag the note `dwz-eq4-instance` /
`dwz-eq1-instance` so the verify stage queries NLM ONCE and fans the verdict.

---

## 7. Enforcement (`tmp/check_propositions.py` — runs after each block)
Post-conditions; a FAIL blocks the commit:
1. every seq present in ≥1 emitted row.
2. `#A-rows ≥ total \citep/\citet keys` across the file.
3. every vendor mention (§1B) → ≥1 B row at that seq.
4. every seed firing T5 (§1H) → exactly one E row.
5. every `$...$` and every `equation N` and every vartable `&`-row → ≥1 D row.
6. bibliography → exactly 13 I rows; each maps to a distinct bibkey.
7. every emitted `{verbatim clause}` is a substring of its seed's `verbatim_span` (no paraphrase).
8. every row has non-null `id`, `category`, `check_route`, `role`.
9. K rows have `proposition == ""` and `check_route == "none"`.

---

## 8. Worked examples (3 real seeds)

**seq 15** (L38): `"A growing literature already studies… \citep{thewissen2024}, … \citep{ragozzino2024}, … \citep{everhart2025}, … \citep{gokkaya2025}."`
Fires T1 ×4 (4 cites) + T4 ("growing literature"). Emit 5 A rows:
- INT-015a A nlm thewissen2024 — "bidders manage the tone of their earnings press releases ahead of stock-for-stock deals"
- INT-015b A nlm ragozzino2024 — "the volume of corporate-strategy vocabulary on conference calls rises with deal activity"
- INT-015c A nlm everhart2025 — "recent work examines the precision of management's guidance around transactions"
- INT-015d A nlm gokkaya2025 — "markets react to acquisition plans once those plans are disclosed"
- INT-015e A nlm [4 keys] — "A growing literature already studies corporate disclosure around acquisitions" (the umbrella phrase, note: semantic-lit)

**seq 95** (L104): the `$Y_{i,t}=…$` equation, "two-way fixed-effects OLS", "clustered by firm", "one-tailed".
Fires T6 ($...$) + T7 (method markers) + T5? (no result numbers, the symbols are masked → if no `\d.\d`, T5 does not fire). Emit:
- MA1-095a D formula-check — "Definition/formula: $Y_{i,t} = \beta PreAnnounceQtr…$"
- MA1-095b C method-review — "Design: two-way fixed-effects OLS, firm + year-quarter FE, SE clustered by firm; treatment one-tailed" (p2_ref M2-02 for the tail)

**seq 137** (L138): `"We therefore read the result as supported but fragile — concentration, not strict specificity…"`
Fires T9 ("therefore", "we read… as") + T10 ("supported but", "not strict"). Emit:
- MA3-137a H logic-check — "Self-limitation: supported but fragile — concentration, not strict specificity"
- (T9 and T10 both point at the same caveat clause → emit ONE H row, note both markers; do not duplicate identical rows.)

> De-dup identical rows: if two triggers produce the SAME category + SAME verbatim clause, emit one
> row and list both markers in the note. Different clause or different category → separate rows.

---

## 9. What you NEVER do
- Never decide a claim is "obvious / standard / true" and skip it. Triggers decide, not you.
- Never paraphrase the verbatim clause.
- Never invent a bibkey, vendor, or phrase not in §1.
- Never merge two different seeds into one row.
- Never leave a seed with zero rows (Rule Z forbids it).
