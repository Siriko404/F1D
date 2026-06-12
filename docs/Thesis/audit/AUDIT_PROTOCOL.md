# Thesis Audit Protocol — deterministic, subsection-by-subsection (v1, 2026-06-11)

Referee-proofing audit of `docs/Thesis/thesis_draft.tex`. **Audit-only: this protocol finds and records; fixes are separate, user-ratified sessions.** Extends the repo's existing machinery (verify_draft_numbers / extract_draft_tables / nlm.py / variable_ledger / plan_ledger) — it does NOT replace it with the ARS reviewer (see §8).

**Runs in Claude Code on this machine** — GitNexus MCP, `notebooklm` CLI (saved auth), and pdflatex live there. (Cowork sandbox has none of the three — verified 2026-06-11.)

---

## 1. Determinism rules (binding)

1. **Extraction is scripted; judgment is constrained; adjudication is human.** Inventories (numbers, cites, refs, terms) come from deterministic scripts, never LLM reading. LLM passes return enum verdicts + mandatory evidence pointers, schema-validated. The user confirms/waives every finding.
2. **No finding without evidence**: verbatim quote + `thesis_draft.tex` line + ground-truth pointer (table cell / `file:line` / NLM quoted text / GitNexus chain). A finding whose evidence does not reproduce on re-check is auto-demoted to `candidate`.
3. **All state on disk, incremental, resumable** (nlm.py pattern: write after every item; partial runs lose nothing). Scripts exit 1 on any FAIL.
4. **Fixed unit order** (§3). One unit per cycle. No unit starts until the prior is logged.
5. **Pinned baseline**: every finding references the baseline SHA + file hashes in `baseline.json`. If the draft changes mid-audit, re-baseline explicitly and diff-rescope; never mix baselines.
6. Carry-over invariants: numbers never typed from memory; author names never expanded from memory; register locks (correlational / "no identification" / "concentrated" not "specific" / change-in-cash not level / "no comparable **positive** run-up").
7. Idempotent re-runs: findings deduped by content hash; re-run appends an `audit_version` stamped to the baseline SHA.

## 2. State files (`docs/Thesis/audit/`)

| File | Contents |
|---|---|
| `baseline.json` | git SHA (commit the tree first — it is currently dirty), sha256 of draft/bible/fragments, GitNexus index stats + freshness, date |
| `coverage_matrix.json` | units × dimensions grid; every cell must reach `pass` / `findings-logged` / `n/a` — **the audit is done when no cell is `pending`, not when it "feels done"** |
| `findings.json` | append-only: `{id: AUD-###, unit, dimension, severity: CRITICAL/MAJOR/MINOR/NIT, quote, draft_line, evidence, verdict, recommendation, status: open/confirmed/fixed/waived}` |
| `number_coverage.json`, `methodology_audit.json`, `citation_audit.json`, `terminology_registry.json`, `claim_register.json` | per-phase outputs (schemas in the generating scripts) |
| `audit_log.md` | per-unit cycle log (plan_ledger style) |

## 3. Unit map (fixed order)

U00 Title/Abstract/Keywords/JEL (L18–32) · U01 §1 Intro (L34) · U02 §2.1 (L52) · U03 §2.2 (L60) · U04 §2.3 (L72) · U05 §2.4 (L76) · U06 §2.5 (L80) · U07 §3.1 (L90) · U08 §3.2 (L102) · U09 §3.3 (L115) · U10 §3.4 (L128) · U11 §4.1 (L143) · U12 §4.2 (L156) · U13 §5.1 (L171) · U14 §5.2 (L177) · U15 §5.3 (L183) · U16 §5.4 (L189) · U17 References (L197–238) · U18 Appendix variable defs (L241–305) · U19 Tables block + spec pages (`_tables_from_bible.tex`)

## 4. Dimensions (coverage-matrix columns)

- **D1 Numbers** — byte-exact vs bible AND coverage-complete AND derived arithmetic recomputed.
- **D2 Methodology fidelity (text→code)** — every estimator/SE/inference/sample/filter/variable claim traced to current pipeline code via GitNexus chains.
- **D3 Disclosure completeness (code→text)** — every material pipeline step the code performs is disclosed (draft, appendix, or table note). Inverse of D2; catches undisclosed researcher degrees of freedom.
- **D4 Citation attribution** — every in-text claim about a cited paper supported by that paper (NLM scoped quotes).
- **D5 Citation metadata** — bibitem fields vs the paper's own title page.
- **D6 Prose & register** — clarity, grammar, house register locks, no-new-info rule.
- **D7 Coherence & redundancy** — within-unit logic; cross-section: generalized conclusion-vs-conclusion gate (diff vs whole draft), abstract↔intro↔body↔conclusion claim-strength monotonicity.
- **D8 Structure & cross-refs** — labels/refs resolve, no hard-coded section numbers, DraftTemplate.txt compliance, table numbering.
- **D9 Referee anticipation** — stats-methodology probes a finance referee will raise (seeded list §7b).

## 5. Phases

### P0 — Freeze & baseline
Commit the working tree (repo rule: `detect_changes()` first). `node .gitnexus/run.cjs status` → if stale, `analyze`, restart MCP. Kill PDF viewer; compile ×2; expect 0 undefined / 0 errors; write `baseline.json`.

### P1 — Mechanical gates (scripted, no LLM; `tmp/audit_*.py`)
- **G1 regen-and-diff (CRITICAL):** rerun table generators → byte-diff fragments + `_tables_from_bible.tex` vs baseline. Resolves the known risk that `_empire_building_did/_empire_drop_placebo/_empire_cashspec.tex` carry uncommitted `M` from the reverse-causality session — i.e., *the 76/76 pass currently proves draft↔bible only, not bible↔code*. Scope choice (user): 3 flagged fragments minimum, all 13 ideal.
- **G2 number coverage gate:** extract every numeric token from prose → classify {covered-by-CHECK, derived (recompute), structural (years/section numbers)} → fail on any unclassified token; extend CHECKS to 100%. *Pass≠coverage today: the 76 checks were built incrementally, never proven exhaustive.*
- **G3 derived arithmetic:** recompute every ratio/multiple/% claim ("fifteen percent of a SD", "half again", "89% of calls", "1.4% of the sample", "roughly three percent of the mean").
- **G4 compile & cross-ref integrity:** parse the .log; label↔ref matrix; cite↔bibitem matrix (incl. fragments).
- **G5 ledger freshness:** verify every `file:line` evidence anchor in `variable_ledger.json` still matches current code (it was hand-built 2026-06-10; code may have moved). Stale anchors → re-trace in P2.

### P2 — Methodology audit (GitNexus; feeds D2/D3)
For each appendix variable (U18) and each design claim in U05/U07–U12: `context({name})` / `query` → record chain `symbol → file:line → process flow` into `methodology_audit.json`; verdict MATCH / DRIFT / NOT_FOUND vs draft wording. Then the **inverse sweep**: enumerate each generator's actual steps (winsorization points, sample filters, merge rules, fallbacks — e.g. saleq fallback, consecutive-quarter lag rule, +4-quarter cap, post-withdrawal drops, truncation at 2nd announcement, CUSIP6 link) → check disclosure → D3 findings. Index must be fresh (P0); never trust chains from a stale index.

### P3 — Citation audit (NLM; feeds D4/D5)
Scripted extraction of every `\cite` context sentence → per paper, atomic **non-leading** questions (nlm.py conventions: `clear` before each ask; `-s <source_id>` single-source scoping; "Reading only this paper," prefix; incremental JSON; exploratory phrasing — never "confirm that…"). Verdict per attribution: SUPPORTED / OVERCLAIM / UNSUPPORTED with quoted text. Already done this way (reuse, don't redo): thewissen, ragozzino, everhart, gokkaya + dwz Eq-4. Remaining: lm2011, hassan2020, baker2016, davis2016, hoberg2010/2016, bushee2018, lerman2026 — first confirm each has a NotebookLM source ID (extend nlm.py SOURCES; user uploads any missing PDF). D5: bibitem fields vs title pages (web metadata is NOT acceptable ground truth — the everhart incident proved it stale/wrong).

### P4 — Per-unit semantic audit (LLM-judged, rubric-fixed; D6/D7/D8)
Per unit in §3 order: inputs = unit text + scripted registries + adjacent-unit summaries. Fixed rubric, schema-validated output. Cycle per unit: audit → advisor pass (Opus tool, adversarial) → user adjudicates findings → log in `audit_log.md` → tick coverage matrix. Pre-read gate: the auditor must read every section a unit characterizes before judging it (the §5.1/§5.2 lesson).

### P5 — Global passes
- Terminology/notation registry: one canonical term per construct; flag drift (e.g. residual nicknames; one- vs two-tailed statements per table consistent everywhere they're mentioned).
- Claim register: every headline claim × {abstract, intro, body, conclusion} wording; strength must be monotone non-increasing toward the front matter; register locks intact.
- **D9 referee-anticipation register** (§7b) — adjudicated with user/advisors; outcome per item: address-in-text / hold-response-ready / accept-risk.
- **ARS reviewer pass (one run, full mode + methodology-focus):** treat output as *candidate findings* to triage into `findings.json`; its scores and accept/reject verdicts are ignored (§8).

### P6 — Close-out
Re-run P1 gates; coverage matrix complete; findings → fix queue grouped by file (code fixes follow repo rules: `impact` before edit, `detect_changes` before commit; tex fixes re-run G2/G4 + recompile); final `audit_report.md` with per-dimension statistics; commit.

## 6. Severity

CRITICAL = a number/claim/citation is wrong, or bible↔code diff → halt, fix before continuing. MAJOR = referee-exploitable (overclaim, undisclosed step, unsupported attribution). MINOR = local prose/consistency. NIT = style. No silent fixes at any level.

## 7. Seed findings (adjudicate first — known before the audit starts)

a) From plan_ledger residuals: (1) bible `h1_2` note "Eq.5"→"Eq.4"; (2) thewissen2024 year + SSRN# unconfirmed from title page; (3) the 3 uncommitted-`M` empire fragments (→G1); (4) dirty working tree (→P0); (5) working-paper bibitem non-uniformity (user-ratified leave-as-is — record as waived).
b) D9 starters: lagged-DV + firm FE (Nickell) in the CashRatio equations — T is large (~68 quarters max) so bias is small, but the draft never says so; UncResCEO is a generated regressor/DV (2nd-stage SEs ignore 1st-stage noise; DWZ precedent — have the response ready); one-tailed treatment inference choice (disclosed, but expect a referee question); winsorization disclosure completeness (per-variable, where stated?); multiple-deal firms handling disclosure; LM dictionary release mismatch vs DWZ's 2014/297-word list (known, user-aware, currently NOT footnoted — decide disclose vs hold); ≥50%-cash/-stock threshold sensitivity (mixed deals 50/50 edge); matched-universe SD used to scale MA2 effect drawn from MA1 universe (ledger calls it robust — record the response).
c) Cross-source seam found 2026-06-11: code/docs say "Lerman et al. **2024**" (run_h18 docstring, variable_ledger CCCL) vs bibitem "**2026**, Articles in Advance" — likely WP-year vs print-year; verify against the paper and align code comments (cosmetic) or bibitem (substantive).

## 8. Why not just run the ARS reviewer (assessment, 2026-06-11)

ARS `academic-paper-reviewer` (7-agent EIC+R1/R2/R3+Devil's-Advocate, 0–100 rubrics, concession-threshold protocol, read-only) is a good **adversarial opinion generator** and is kept as one P5 pass. It cannot be the audit because: (1) **text-only** — no binding to bible/pipeline/PDFs, and this draft's residual risk lives precisely in those seams (the prose itself was already advisor-gated per unit); (2) **stochastic by its own admission** (its repro_lock doc: "LLM outputs are not byte-reproducible"; calibration mode exists because FNR/FPR drift) — reviewer runs are evidence-free opinions unless triaged into this ledger; (3) **wrong output type** — scores and Accept/Reject map to journal decisions, not to an exhaustive findings ledger with a coverage guarantee; (4) **its citation tooling (Semantic Scholar API) is the method the everhart incident proved unreliable** vs the actual PDF; house standard = NLM scoped quotes; (5) **no coverage matrix** — nothing proves every unit × dimension was examined.

## 9. Anti-patterns

No fixes during audit. No findings from memory. No web metadata as citation ground truth. No skipping advisor on "easy" units. No new CHECKS hand-typed from prose without the extraction script. No GitNexus conclusions from a stale index. No marking a coverage cell `pass` without a logged artifact.

## 10. Experience addenda (lessons from live runs — read before P2+ grading)

### E1 (2026-06-11) — Verify a critique's PRECONDITION before its mechanism. [M2-01 withdrawn]

**What happened.** Graded M2-01 MAJOR: "UncResCEO is a DWZ eq-4 residual used as the Analysis-1 DV; second-stage clustered SEs ignore first-stage estimation error (generated-regressor, Pagan 1984); undisclosed." The code chain was verified airtight (first stage stores `model.resid.values` only, first-stage covariance discarded; loader carries no covariance; second stage = plain firm-clustered `PanelOLS`; zero correction repo-wide; prose discloses construction but not the inference). **Withdrawn in full** (commit 6cfb387) — the finding misidentified the **estimand**.

**Root cause.** A named critique has three parts: **precondition + mechanism + consequence.** I verified the *mechanism* exhaustively and mistook that for the critique *binding*. I never tested the *precondition*. Pagan's generated-regressor correction binds only when the estimand is a **latent** quantity for which the variable is a noisy **proxy**. `UncResCEO` is not a proxy — it is the **operationally-defined** measure (the eq-4 residual; the deviation from the *estimated* CEO baseline + controls **is** its definition, per DWZ). The thesis's claim is about the **measure** ("the residual rises pre-announcement"), so standard clustered inference is valid — as across the entire residual-measure literature (abnormal returns, discretionary accruals). Exhaustive mechanism-verification *felt* like rigor and substituted for the one cheap, decisive check I skipped.

**Standing gate (apply to every methodology finding, D2/D3/D9).** Before importing ANY named critique (Pagan/generated-X, Nickell, Murphy–Topel, weak-IV, attenuation, etc.):
1. Write the thesis's **exact claim** and its **estimand** in one line (a property of an *observed constructed measure*, or a *latent/structural parameter*?).
2. Write the critique's **trigger condition**.
3. Proceed **only if** the trigger holds for *this* estimand. `mechanism-present ≠ critique-binds`. If the critique presumes a latent estimand and the claim is about a constructed measure, kill it before gathering code evidence.

**Cheap heuristics that would each have caught it.**
- **Established-method smell test:** if a finding implies the method's own authors *and* the standard literature mis-do inference, the burden flips to me — default to "I've misframed it," not MAJOR.
- **Seed labels are hypotheses to falsify, not findings to confirm.** §7b *named* this "generated regressor"; I confirmed the label instead of seeking the disconfirming reading first.
- **Advisor agreement on the same frame ≠ independent check.** The advisor also endorsed MAJOR; two models sharing a wrong frame is not corroboration. Ask the advisor to test the **precondition**, not to bless the finding.

### E2 (2026-06-11) — Cite the executable line, never the comment. [M2-01, M2-03]

**What happened.** Two findings in this audit mis-stated a method because I trusted a **comment/label** instead of the **executable line**:
- **M2-01** took §7b's seed *label* ("generated regressor") as the conclusion.
- **M2-03** took a *docstring* (`ceo_qa_uncertainty.py:4` "pooled 1%/99%") and a table *note* as the winsorization scheme. The actual call is `winsorize_by_year(_pct_cols, lower=0.0, upper=0.99)` (`_linguistic_engine.py:331`) = **per-year, upper-only, 99th pct** — a different transform. Sina caught it.

**Standing rule.** Every methodology fact in a finding must cite the **executable line** — the `fit()` / `winsorize()` / `clip()` / `.quantile()` / formula call and its **literal arguments** — not a docstring, header comment, table note, or variable name that *describes* it. Comments, notes, and seed labels **drift from code and are themselves audit targets**: when a comment and the call disagree, **the call is ground truth and the comment becomes a (separate) finding** (e.g. M2-03's stale `pooled 1%/99%` docstrings). A finding whose only evidence is a comment is not yet verified.

### E3 (2026-06-11) — NLM citation-query discipline (5 rules; Sina-set, smoke-test verified). [P3]

**What it is.** The five operating rules for every NotebookLM query in P3 (D4/D5). They are already wired into `tmp/nlm.py`; this addendum makes them binding and explains the failure each one prevents. Smoke-tested 2026-06-11 (post-auth-renewal): `clear` → single-source `-s` → `--json` ask on Thewissen returned a scoped answer with verbatim `cited_text` + char offsets. All five live.

| # | Rule | `nlm.py` mechanism | Failure it prevents |
|---|------|--------------------|---------------------|
| 1 | **Self-contained question** — each query stands alone; no "as above", no carry-over from a prior turn | `PREFIX = "Reading only this paper, "` + one question per call | NLM answering from conversation context instead of the source → unverifiable attribution |
| 2 | **Name the paper / single-source scope** — every question targets ONE named paper's source id | `ask -s <source_id>` | cross-paper mixing — NLM pulls a quote from the wrong document in the notebook |
| 3 | **Non-leading / exploratory phrasing** — ask open ("what does it say about X?"), never "confirm that X" | question wording in `INFOS` | confirmation bias — a leading prompt manufactures agreement; the audit must elicit, not suggest |
| 4 | **Clear before each ask** — reset conversation state between questions | `cli(["clear"])` before every `ask` | residual context bias bleeding from the previous question into the next answer |
| 5 | **Incremental JSON, verbatim** — write structured output (answer + `cited_text` quotes) to disk after every item | `--json` + `OUT.write_text(...)` after each task | (a) lost work on quota/interrupt; (b) attribution from a paraphrase instead of a verbatim quote — only the quoted `cited_text` is admissible evidence |

**Standing rule.** No P3 attribution verdict (SUPPORTED / OVERCLAIM / UNSUPPORTED) without all five satisfied. The verdict's evidence is the verbatim `cited_text` from the scoped JSON, never NLM's prose `answer` alone (the answer can drift; the quoted span is ground truth — same principle as E2 for code). Web metadata remains inadmissible as citation ground truth (the everhart incident, §9).

### E4 (2026-06-11) — NLM is the SOLE paper-side authority; every query is ATOMIC. [P3, Sina-set, HARD]

**Two absolute rules. No exceptions, no routing around them.**

1. **NEVER read a cited paper directly — NLM for everything.** No `WebFetch`, no `Read`, no opening a PDF, no web metadata, no abstract page — for *any* external paper. **Every** paper-side fact comes from NLM scoped quotes: findings, construct definitions, **equation numbers**, methodology, *and* title-page metadata (author/year/venue/working-paper number for D5). This supersedes the earlier "method/eq# → DWZ PDF" routing — that leg is dead. Two prior burns make this non-negotiable: a direct PDF read of DWZ produced wrong factual claims (the notebook held a different edition), and web metadata produced a wrong citation (the everhart incident). **Scope:** this rule governs *external papers only*. Repo artifacts — `thesis_draft.tex`, the generators/`*.py` code, `*.tex` bibitems, the bible — are **not** papers; they remain readable and are the thesis-side ground truth (code stays the implementation authority, per E2).

2. **Atomic queries — one check per query.** Each NLM `ask` verifies exactly **one** checkable proposition. No multi-part questions ("what measure does it use **and** what dictionary defines it **and** quote the sentence"). Split every compound into separate scoped asks. One proposition → one query → one quoted span → one verdict. (`tmp/nlm.py`'s current `INFOS` are compound; they must be atomized before the Stage-2 run.)

**Consequence — the fallback when NLM can't retrieve.** If NLM cannot surface a fact after honest atomic asks (e.g. a structural equation number that retrieval misses), the verdict is **inconclusive → manual** (flag for Sina), and the manual check is *still not* a direct paper read — it is Sina's own inspection or a re-scoped NLM ask. The auditor never substitutes a direct read to "resolve" an inconclusive. Silence/miss ≠ UNSUPPORTED, and ≠ license to read the PDF.

### E5 (2026-06-11) — Every NLM query lives in a committed script; the paper title is the anchor. [P3, Sina-set, HARD]

**Two mechanics, both binding.**

1. **Scripted, never ad-hoc.** No NLM query is ever typed straight into the shell. **Every** query is authored in a deterministic script file (the `tmp/nlm.py` pattern), committed before/with its run, and writes its results to a durable JSON for later review. Rationale: reproducibility + an auditable record of *exactly* what was asked and *exactly* what came back. An inline `notebooklm ask` leaves no reviewable trace, cannot be re-run identically, and is therefore inadmissible as audit evidence. (This is why an inline identification probe was rejected on 2026-06-11.)

2. **The paper title is the anchor — never the upload filename.** Sources are identified and referred to by the paper's **exact title** (from the bibitem), never by the NLM upload filename (`ssrn-4900453.pdf`, `1-s2.0-…`, `w22740.pdf`). Filenames are opaque and untrustworthy as identifiers. *(Mechanism for achieving this — superseded by E6: an early version tried to pre-resolve each title to a `source_id` for `-s` scoping; E6 proves naming the paper in the query is sufficient and the id-mapping is unnecessary.)*

### E6 (2026-06-11) — Scope by NAMING the paper in the query; `source_id` is a post-hoc check, not a prerequisite. [P3, Sina-corrected, PROVEN]

**What changed.** E3 #2 / E5 assumed scoping required `-s <source_id>`, which forced a source-id pre-mapping step over a 94-source notebook (and the notebook stores **filenames, not titles**, so the mapping was painful). Sina: *"why do you need the index? you don't need it when you have the paper's full title and authors and year."* Correct — and proven.

**Proof (2026-06-11, `tmp/p3_proof_naming.py`).** An **unscoped** query that *names* DWZ in its text — "in the paper 'Straight talkers and vague talkers…' by Dzielinski, Wagner, and Zeckhauser (2021), what is the dependent variable of equation (4)?" — returned an answer grounded **only** in DWZ's source (`67b17abd` cited ×3, **zero** other sources). Naming the paper scopes it.

**Standing mechanism (supersedes the `-s` requirement).**
1. **Every atomic query is self-contained and NAMES its target paper** — exact title + authors + year — so NLM retrieves from that paper. No `-s`, no id, no filename.
2. **Post-hoc scope verification (replaces the `-s` guarantee).** Read the `source_id`s cited in the answer JSON; the answer is **admissible only if every citation is the same single source** — the named paper. Blended citations ⇒ re-ask or flag. This is *stronger* than `-s`: it both scopes *and* proves scoping from the returned evidence.
3. **Consequence.** The id-pre-mapping (`p3_identify_sources.py`) is **retired as a prerequisite**. Its one durable by-product: `lm2011` and `hoberg2010` returned *"not present in the notebook"* — confirm with a named query; if still absent, Sina uploads the PDF. Everything else in E1–E5 stands (NLM-only, atomic, scripted, never read a paper).

### E7 (2026-06-11) — Referenced-claim extraction: total-partition + reassembly, not eyeballing. [P3 Stage-1 — ⚠️ RETIRED 2026-06-11, kept as a lesson]

> **RETIRED the same day by Sina's decision.** The programmatic extractor was trashed: the script only *segmented* text — the LLM still had to **read** every unit to find claims, so the machinery (total-partition, Pass A/B taxonomy, enum-lock, reconcile) was pure overhead over "just read it," and sentence-fragmentation actively **hurt** semantic/indirect-claim capture (a claim spanning sentences, or implied across a paragraph, reads worse in fragments). **Replacement method (the standing P3 Stage-1):** read the draft **subsection by subsection** and manually extract every referenced claim — DIRECT (`\cite`) and INDIRECT (named-author-no-cite; semantic attribution with no cite/name) — into a JSON ledger, one record per (paper × claim) with verbatim thesis span + `file:line` + claim type + mapped bibkey (or `UNNAMED-LIT`); user ratifies each subsection. The one durable lesson from E7 below still holds: **the eyeball/grep method it replaced was genuinely unreliable** (blind to no-cite/no-surname semantic attributions), so the manual read must *explicitly* hunt indirect claims, not just cites. The NLM verification method (E3–E6) is unaffected.

**[Historical record of the retired approach follows.]**

**Why this exists.** The auditor first built the citation list by *reading the draft and noticing* attributions, anchored on `\cite` tokens + a hand-typed surname list. Sina was rightly skeptical. A programmatic fight-test (`tmp/p3_fighttest.py`) proved the method unreliable: (a) it is structurally blind to **semantic attributions** that carry no cite and no surname (e.g. L38 "A growing literature already studies corporate disclosure around acquisitions"); (b) it violates §9 ("no checks hand-typed from prose without an extraction script"); (c) "N claims" was an eyeball estimate with no coverage guarantee. The fight-test also surfaced two structural traps a naive section-walker hits: the **appendix sits AFTER `\begin{thebibliography}`** (a "walk to bibliography and stop" loop drops it), and the **appendix is a `tabular`, not prose** (a sentence-splitter mangles `Var & def \\` rows).

**The mechanism — a complete partition the model cannot escape.** Stage-1 extraction is a script-first pipeline whose *no-drop* guarantee is mechanical and whose *classification* is best-effort + adversarial + a load-bearing human floor. The LLM **never re-types draft text**; it emits sentence/row IDs + a closed enum only, and the script copies verbatim spans by index.

1. **Total partition (S0 script, zero LLM).** Every line of the draft file is assigned to exactly one typed unit-class — the union must equal the whole file with no gaps/overlaps or the script **exits 1**:
   - `PROSE` / `ABSTRACT` / `APX-PROSE` → sentence-mode (abbrev-guarded split: *et al., e.g., U.S., i.e.*);
   - `BIB` → entry-mode (one record per `\bibitem` → the D5 metadata unit);
   - `APX-ROWS` → **row-mode** (one record per `&`-row of the variable table — never sentence-split);
   - `PREAMBLE` / `COMMENTS` → exempt-but-scanned.
   "Exempt ≠ skipped": **every line of every class is tripwire-scanned regardless**; a cite/surname/soft-attribution hit inside an exempt class is itself an `exit 1`. The bibliography-then-appendix ordering and the tabular region are therefore just two more ranges, not special cases.
2. **Reassembly coverage proof.** `concat(all units in file order) == source file`, char-for-char, or `exit 1`. This is the artifact that proves *nothing was skipped* (the only fully mechanical guarantee in P3).
3. **Two-pass classification (LLM, IDs only).** Pass A: per unit, classify `{DIRECT cite | NAMED no-cite | SEMANTIC no-cite/no-name | NONE | UNSURE}` + bib-key from a **closed enum** (13 keys + `UNNAMED-LIT` + `UNSURE`; any other token ⇒ `exit 1`). Pass B (adversarial, different framing): "list every unit that relies on ANY external work," a pure recall net with no taxonomy. Script unions + diffs A vs B; every disagreement must reach a resolution record or `exit 1`.
4. **Tripwire-justify.** A deterministic scan flags units containing cite-tokens, surnames, `(20xx)`, "et al", or soft markers ("literature", "prior/recent work", "following", "consistent with", "precedent", "documented"). A tripped unit cannot be labelled `NONE` without a one-line justification; empty justification ⇒ `exit 1`.

**Two-tier honesty (do not oversell — the "airtight" claim was wrong).**
- **No-drop: mechanically proven** (total partition + reassembly + every-line scan).
- **Classification: best-effort + adversarial + HUMAN FLOOR.** No regex captures "implies a paper's finding without naming it." The irreducible residual — a semantic attribution with zero tripwire words missed by *both* passes — is caught only at **Sina's ratification read of each unit's NONE-list**, which is therefore **load-bearing, not optional**. Fight-test good news: the body is mostly explicit (≈2 soft-only lines, one a false positive), so the human floor is cheap (~one pass over short NONE-lists). The claim count is an **output** of this pipeline, never asserted up front.
