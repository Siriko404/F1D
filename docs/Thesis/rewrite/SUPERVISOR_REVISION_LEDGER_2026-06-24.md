# SUPERVISOR REVISION LEDGER — Meeting 2026-06-24

**Durable record of the supervisor meeting's three asks + the plan to tackle them.**
Branch `debug/campello-did-supervisor-interrogation`. Thesis prose is governed: *"Prose units are user-ratified one by one before they enter this file"* (master L7) and tables are byte-exact from the bible. **No prose enters the thesis without Sina's ratification.**

---

## THE THREE ASKS

### 1. LANGUAGE — rewrite all sections
- Supervisor: prose throughout is **too complex, not corporate-finance style.**
- Aspiration quote: *"so simple your mother would read and understand the entire paper."*
- **Locked operational target:** corporate-finance **academic** register, pushed to the **simplest end the register allows.** NOT de-technicalization — keep the econometrics. Make every *sentence* plain:
  - short, active voice, one idea per sentence
  - zero unexplained jargon (define on first use)
  - lead with the point; cut nominalizations, stacked clauses, Latinate filler
- Current prose fails this. Example (§3.1 ¶4, the 212-deals sentence): one ~90-word sentence, multiple subordinate clauses, "residualizes", "researcher degree of freedom", "orthogonal". Mother-test: fail.

### 2. CASH-SPECIFICITY JUSTIFICATION
- Supervisor: still unjustified. Need an economic **reason** cash deals attract more interest *in this context.*
- May ultimately be wrong — but must be (a) **not obviously wrong**, (b) **defer identification to Future Directions.**

### 3. TWO LOGIT ROBUSTNESS TESTS
- **Test A:** does `UncResCEO` predict a **deal announcement**? (DV binary: announce = 1)
- **Test B:** does `UncResCEO` predict the **deal TYPE**? (DV binary: cash = 1 / stock = 0)
- **If WEAK → drop the cash claim**, fall back to ALL deal types (the `rob_ALL.pdf` version already built).

---

## CRITICAL DEPENDENCY (the spine — read first)

- **Cash is in the TITLE:** *"Cash Got Your Tongue? CEO Language-Uncertainty Around Undisclosed Cash Acquisitions."* → **Test B is existential**, not a side robustness check.
- **Test B gates** both Feedback 2 (justify cash) and the cash-specific PROSE of Feedback 1.

| Test A (predict deal) | Test B (predict cash/stock) | Action |
|---|---|---|
| strong | strong | cash survives → full rewrite incl. cash; finalize Feedback 2 |
| strong | **weak** | **DROP cash** → all-deal-types (`rob_ALL.pdf`); Feedback 2 MOOT; **retitle thesis** |
| **weak** | — | run-up *predictive* premise shaky; event-study DiD may still stand (different identification) — FLAG, do not auto-drop |

---

## HARNESS CRITIQUE (Sina proposed: ~15 papers, agents compare our style to theirs)

Good instinct (parallel, exemplar-grounded). Three reframes:

1. **COMPARE → REWRITE+VERIFY.** A comparison *report* does not fix the thesis. Pipeline = distill a style rubric → rewrite each unit to it → verify nothing substantive changed.
2. **Rewrite the SOURCE, not the `.tex`.** §3/§4 + intro/concl/abstract are AUTO-GENERATED from paragraph ledgers (`final_prose`); editing the `.tex` gets overwritten on regen. Rewrite `final_prose` → regen. §2 is inline in the master → rewrite in place (+ `thesis_draft.tex` mirror).
3. **~6–8 exemplars, not 15.** Style is near-uniform across top journals; sharp diminishing returns. Shortlist: **Dzielinski FWP_2017** (`docs/papers/PaperBank/FWP_2017_02_v2.pdf` — method anchor + target register), **Harford 2011** (cash+acquisitions), **Loughran-McDonald 2011** (textual), **Hassan 2019** (PRisk), **Druz et al. 2020** (call tone), 1–2 JFE M&A exemplars.

**HARD GATES on every rewritten unit:** numbers unchanged · claims unchanged · citations intact · **load-bearing hedges preserved** (e.g. "fails to establish, not confirms"; "researcher degree of freedom"; null-only/underpowered caveats). Output = candidates **for Sina's ratification**, never auto-committed to the thesis.

---

## PROSE SOURCE MAP (where each section's editable truth lives)

| Section | Source of truth | Generated file |
|---|---|---|
| Abstract / Intro / Conclusion | introconcl paragraph ledgers | `_abstract_body.tex` / `_intro_body.tex` / `_conclusion_body.tex` |
| §2.1–2.5 | **inline** `thesis_draft_uottawa.tex` L162–262 | (mirror: `thesis_draft.tex`) |
| §3.1–3.4, §4.1 | `section{3.1,3.2,3.3,3.4,4.1}_paragraph_ledger.json` → `final_prose` | `sec34_body_from_ledgers.tex` via `tmp/build_sec34_body.py` |

Existing infra to reuse: the A→B→C→D proposition pipeline + workflow scripts in `docs/Thesis/rewrite/`.

---

## CASH MECHANISMS (Feedback 2 — candidates to pick/refine)

**Lead (composite, hooks constructs the thesis already has):**
Cash acquisitions drain a closely-watched, fungible resource — the firm's **cash buffer** → draw disproportionate analyst/investor **scrutiny** (Jensen 1986 free-cash-flow agency; Harford 2011 cash reserves + acquisitions document value-decreasing cash deals → markets watch them) → the CEO faces **higher pressure to guard material non-public info pre-announcement** → more uncertainty language. Stock deals dilute but do not drain cash → lower balance-sheet salience.
**Future Directions (defers ID):** disentangling *scrutiny* vs *financing-commitment* vs *signaling* as the precise driver is left to future work.

**Before this becomes load-bearing:** (1) **read Harford 2011 from the PDF** (`docs/papers/new/...Harford...pdf`) — confirm what it actually concludes; do not cite from the title/memory. (2) Tie the mechanism explicitly to the **uncertainty DV** ("why *pre-announcement uncertainty* is sharper for cash"), not generic "scrutiny."

**Alternates:** (b) **cleaner transaction clock** — cash closes faster, less price-contingent → sharper two-clock identification; (c) **signaling asymmetry** (Myers-Majluf / Shleifer-Vishny: stock signals overvaluation, cash signals confidence → cash carries more information); (d) **financing-commitment** — cash needs hard funding lined up pre-announcement → acute information-asymmetry window.

---

## LOGIT TEST DESIGN (Feedback 3) — advisor-corrected

**⚠ The logit is NOT the event study.** The thesis result is within-firm: uncertainty spikes at **e=−1** then *resolves* at announcement (e=0). A naive logit sampled at the wrong quarter produces a **false-negative null** that would wrongly kill a title-level claim. Two non-negotiables:

- **TIMING (the crux):** the regressor is `UncResCEO` at **e=−1**, not the deal quarter.
  - **Test A:** `P(announce at e=0) ~ UncResCEO at e=−1 + CTRL + year FE`, cluster firm. (= the t→t+1 lead.) Watch the rare-event base rate.
  - **Test B:** among firms with a deal, `P(cash=1 | deal type) ~ UncResCEO at e=−1 + CTRL + year FE`, cluster firm. **Do NOT run it contemporaneously on deal-quarters** — that samples decayed signal.
- **RUN BOTH specs side by side:** (1) supervisor's simple pooled logit; (2) thesis-aligned FE version (LPM + firm FE, or conditional logit — logit can't carry firm FE cleanly, incidental-parameters). **Agreement/disagreement between them is the decision input, not a lone p-value.** Simple weak + aligned holds → the weak result is an artifact, NOT grounds to drop.

- **Panel hygiene:** build from `base_panel` + a clean announcement indicator. **Do NOT reuse the trimmed `build()` output** — it drops treated firms' post-event quarters → biases a prediction test.
- **Straddle / arm definition:** thesis arms are `pc>=50` / `ps>=50` (FLAG J). `pc>50` / `pc>ps` is a *third* definition — **mirror the headline arms (`pc>=50`) or run both**, so the logit and the event study describe the same split. State which.

**Define "weak" BEFORE acting (small N: ~485 cash / ~134 stock post-dropna):** a null may be pure power. Report **CI + marginal effect per 1-SD `UncResCEO` + effective N**, not just significance. **Drop requires a *precise* null (tight CI around zero), not a noisy one** — same "null-only, underpowered, don't over-read" discipline §4.1 already carries.

**Deliverable for the supervisor = results + correct interpretation relative to the event-study evidence**, so the keep/drop decision is defensible either way. NOT a mechanical p<0.05 threshold on a possibly-misaligned test.

---

## PARALLELIZATION (time-critical)

```
t=0  START BOTH:
 TRACK A (short, GATES cash):   build logit panel → Test A → Test B → VERDICT
 TRACK B (long pole, language):  collect exemplars → distill rubric →
                                 rewrite SAFE (cash-independent) units:
                                 intro framing, §2.1 framework, §2.3 estimation,
                                 §2.4 methodology, conclusion → verify gate
GATED on VERDICT:
 survive → rewrite cash units (§3.2/3.3/3.4, §4.1, abstract cash lines)
           + finalize Feedback 2 mechanism + Future-Directions ¶
 drop    → pivot cash units to all-deal-types (rob_ALL); Feedback 2 dropped; retitle
```

The only work that CANNOT start at t=0 is the **cash-specific** prose + Feedback 2 (both gated on Test B). Everything else runs in parallel from the start.

---

## OPEN DECISIONS (settle before execution)

- **D1** Ledger location = `docs/Thesis/rewrite/` ✔ (this file).
- **D2** Rewrite via ledger-source + regen (REC) vs edit `.tex` directly.
- **D3** Gate cash content on Test B before rewriting it (REC: yes — don't rewrite prose that may be deleted).
- **D4** Harness model: OPUS (REC — style rewrite is quality-sensitive; prior pipeline used opus, env pin removed) vs SONNET (cheaper).
- **D5** Exemplar shortlist (above) — confirm/adjust.

---

## STATUS LOG
- 2026-06-24 — ledger created from supervisor meeting. Orientation done (paper bank, prose source map, infra). Plan drafted.
- 2026-06-24 — **advisor second-look done + integrated.** Key catch: logit ≠ event study → Test B must be timed at **e=−1** (not deal-quarter) or it false-negatives; run pooled + FE specs side by side; define "weak" as a precise null; build from `base_panel` not trimmed `build()`; verify Harford from PDF. All folded into Logit + Cash sections above.
- 2026-06-24 — **harness design locked (Sina-driven):** panel(3 identical)+redteam(1) per phase; phases = analysis → rewrite; build the shared **style spine** ONCE from the papers; **analyze by section-TYPE**, rewrite per ledger; **pilot one section first**; spine = ledger `proposition_chain`+`thin_claim`+`guardrails`, fingerprint = `number_audit` (both gate every rewrite). Pilot section = §3.1.
- 2026-06-24 — **EXTRACTION DONE (Role 0).** 8 style-exemplars chosen (anchor DWZ + neighbors thewissen/ragozzino + influences lm/hollander/harford/bertrand_schoar + bushee) → moved to `docs/papers/style_exemplars/`. Multi-tool stack: **GROBID(CRF, docker :8070)** = structure; PyMuPDF/pdftotext/pdfplumber = coverage cross-check; regex = glyph scan. Advisor-corrected: cross-verify = COVERAGE not glyph-consensus (GROBID strips heads → glyph votes misfire). Script = `tmp/extract_papers.py` → `docs/papers/style_exemplars/extracted/<key>.json` (sections[type,paragraphs] + verify{coverage,glyphs}). Result: glyphs 0/8, vocab-in-raw 0.96–0.99 (no scramble), all prose typed via deterministic head-overrides. Pilot on DWZ (62pg working paper — advisor's worry) passed clean.
- **NEXT:** design the analysis-phase agents (panel reads exemplars + our prose → style findings → spine). Still NOT started: the 2 logits (cash-independent, can parallelize).
- Open D2–D5 from above: D2 (edit source not .tex) + D3 (gate cash on Test B) still pending explicit lock; D4=Opus, D5=8 exemplars now locked.

---

## STYLE HARNESS — PHASE 1 (ANALYSIS) — LOCKED SPEC (2026-06-24)

Phase 1 = ANALYSIS ONLY (rewriting = phase 2, designed later). Per section-TYPE: **3 panel agents (paraphrased) + 1 redteam**. 8 types: abstract, intro, lit_review, hypotheses, data, methods, results, conclusion.

### Sec 1 — INPUTS (per panel agent)  [LOCKED + AIRTIGHT]
1. **Exemplar prose for its type** — `docs/papers/style_exemplars/bundles/<type>.json` → `exemplars[]{paper,venue,head,paragraphs}`.
2. **Our slim ledger for its type** — same bundle `ours[]{ledger,para_id,final_prose,propositions(claim statements),guardrails,number_audit}` (NLM receipts stripped).
3. **Objective + open mandate + finding schema** (NO fixed checklist).
- Built by `tmp/build_bundles.py`; coverage **96.9%** (drops logged: artifact 2,150w watermarks, appendix 1,342w); verified clean (0 receipt keys leaked).

### Sec 2 — TASK (panel; identical for all 3)  [LOCKED, panel-only]
- Read exemplars vs our prose for YOUR type. Discover **every aspect where OUR language is needlessly more complex** than the exemplars. **Open aspects** (no checklist).
- **OBJECTIVE / yardstick:** the **simplest end of the corporate-finance register** (supervisor's mother-test). Flag only where **WE are needlessly more complex**; never where we are already simpler. On register conflict, **prefer journal (JF/JAR/QJE) over working-paper** (use `venue`).
- Each difference → one **finding** (schema below). **≥2 exemplar quotes from ≥2 DIFFERENT papers** + **≥1 our quote**. Grade **major/minor**.
- **HARD RULES:** style only — never flag a point/number/hedge as "fix"; never say "cut hedging" (load-bearing, e.g. "fails to establish, not confirms"); **no rewriting** (phase 2); stay inside your type.

### Finding schema (LOCKED contract — all 3 agents + redteam emit/consume)
`{ aspect, exemplar_pattern, exemplar_quotes:[{paper,quote}] (≥2, ≥2 papers), our_pattern, our_quotes:[{para_id,quote}] (≥1), gap, aim, materiality: "major"|"minor" }`

### Validation (deterministic, post-run — phase-1 analog of the number fingerprint)
- **Quote-substring check:** every `exemplar_quote` must substring-match its paper's bundle text; every `our_quote` must substring-match the ledger `final_prose`. Not found → finding dropped/flagged. (Catches hallucinated quotes.)

### Neurodiversity
3 agents = **same task + same inputs + same schema**, only **3 paraphrased promptings**. NOT different roles/lenses (honors the prior "no diverse lenses" rule).

### Scope note
This locks the **PANEL**. Analysis phase also requires the **REDTEAM** (Sec 3 below).

### Sec 3 — REDTEAM (1 per type) — LOCKED
**Principle:** VERIFY + SYNTHESIZE, **never adds findings**; **merge by REFERENCE, never re-authors** (the anti-hallucination rule — applies to every agent).
- **HAS:** the 3 panels' finding-JSONs (its type) + the bundle. **Pre-filtered by a SCRIPT** (quote-substring + schema/cardinality ≥2 quotes/≥2 papers) → redteam sees only clean findings.
- **VERIFY** (judgment only, per finding → keep / reject+reason): ① direction — we're needlessly *more* complex, not the reverse · ② evidence actually supports the gap · ③ style-only (no point/number/hedge targeted) · ④ materiality sane.
- **MERGE:** duplicates across the 3 agents → one canonical, **by id**. Conflict tiebreak = **more + journal-weighted** quotes win.
- **RETURNS (decisions only):** `{ keep:[ids], merge:[[ids]→canonical], reject:[{id,reason}], side_notes:[...] }`. `side_notes` = **segregated** under-coverage flags ("all 3 missed paragraph-level"), **never findings** (user: strictly side notes).
- **ASSEMBLY:** the **main loop copies the winning panel findings VERBATIM** → `<type>_profile.json` (the type's style profile).
- **Division of labor:** SCRIPT verifies facts (quotes/schema) · REDTEAM verifies judgment (the 4 checks) · MAIN LOOP assembles. **No agent free-authors prose.**

### PHASE-1 OUTPUT
8 `<type>_profile.json` (verified, deduped findings) + side_notes. These feed Phase 2 (rewrite, designed later) and the later global-spine distillation.

### PILOT-FIRST (committed)
Run the full chain (3 panel → script gate → redteam → profile) on **ONE type** before fanning to all 8. Cheap proof the profile is usable.

---

## ▶ RESUME / COMPACTION CHECKPOINT — 2026-06-24 (PHASE 1 COMPLETE)

**One-line state:** Phase-1 ANALYSIS complete + both logits done. Thesis prose UNTOUCHED (verified: 0 tracked `.tex` / `*paragraph_ledger.json` modified this session). **Detailed hub: `docs/Thesis/rewrite/style_profiles/_WAVE_STATUS.md`.**

### DONE this session
- **8/8 style profiles** → `docs/Thesis/rewrite/style_profiles/<type>_profile.json` (157 findings; lit_review 18, abstract 15, intro 14, hypotheses 23, data 20, methods 18, conclusion 17, results 32). All schema-unified: describe-only + `guardrail_collision` (verified 0 with `aim`, 0 missing the flag). Each = aspect + ≥2 exemplar quotes (≥2 papers) + ≥1 our_quote, verbatim-gated, redteam-merged, **describe-only** (no reword / no equivalence claim) + `guardrail_collision` flag. Raw digest example: `lit_review_RAW_digest.md`.
- **Logits (Ask 3) → CASH HOLDS, do NOT retitle.** `tmp/logit_cash_gate.py` → `tmp/logit_cash_gate_results.json`. Test A (UncRes→deal) p=0.001 ✅; Test B (UncRes→cash vs stock) +1.9pp p=0.02 ✅ (robust to controls+logit); persistent ClarityCEO null → it's the TRANSIENT spike, not chronic style. Caveat: modest (~2pp on 89% cash base), CI below the pre-set 5pp SESOI; stock N=124 underpowered but came out sig. Event-study-style binarized logit = SKIP (advisor: binarizing only loses power vs the already-won continuous event study, which stays the backbone).
- **Harness hardening:** `TOOL_LOCK` on panel+redteam (ONLY StructuredOutput, one turn — fixed the wander→idle-timeout that nulled the abstract redteam: tool calls 84→8, ~17× faster, SAME token work ~408k, reproducibility-confirmed) + null-guard (dead redteam degrades to gate-clean findings, never crashes the type). Multi-type WAVE runner: `docs/Thesis/rewrite/style_phase1_master.js` built by `tmp/build_master.py`, embedded per wave by `tmp/embed_master.py <types...>` → `tmp/run_wave_<types>.js`.

### NEXT (Phase 2 — REWRITE; NOT started; Sina ratifies every step)
1. **Design Phase-2 harness LATER.** Spine FROZEN: propositions / guardrails / number_audit unchanged; ONLY sentence wording editable. Human sees 100% of diffs before anything ships.
2. **Number-survival gate is LOAD-BEARING:** results has 14/32 findings touching real numbers, 6 with `guardrail_flag=FALSE` → the collision flag MISSES numbers. Phase-2 must mechanically verify every `number_audit` value + guardrail string survives the rewrite, scanning ALL findings, not just flagged ones.
3. **Guardrail-completeness pass** (human-ratified) before guardrails can auto-gate — current guardrails are concept-notes, not exact protected strings (e.g. "not informationally empty" is NOT in §2.1 U1/U3 guardrails).
4. Prose source map (where each section's editable prose lives) is in this ledger above (§ prose source map).

### Durable artifacts (all on disk)
| Path | What |
|---|---|
| `docs/Thesis/rewrite/SUPERVISOR_REVISION_LEDGER_2026-06-24.md` | THIS — master plan + all locked specs |
| `docs/Thesis/rewrite/style_phase1_pilot.js` | workflow template (anchor `__BUNDLE_ANCHOR__`) |
| `tmp/embed_bundle.py` | `<type>` → self-contained `tmp/run_<type>.js` (deterministic bundle inject) |
| `tmp/build_bundles.py` | → `docs/papers/style_exemplars/bundles/<type>.json` (8, coverage 96.9%) |
| `tmp/extract_papers.py` | → `docs/papers/style_exemplars/extracted/<key>.json` (8 papers, GROBID) |
| `docs/papers/style_exemplars/*.pdf` | the 8 exemplar PDFs |

### Standing constraints (carry across compaction)
- **No thesis-prose edit without Sina's ratification.** Phase-1 = ANALYSIS only (no rewriting).
- **All agents programmatic / no-hallucination:** quotes copied verbatim + substring-checked; main loop assembles; agents emit JSON only.
- **Redteam = verify + merge-by-reference, never adds** (gap flags allowed only as segregated `side_notes`).
- **Neurodiversity = paraphrase, not re-role.** Model = **Opus**.
- **GROBID** docker container `grobid` still running on :8070 (stop with `docker rm -f grobid` if needed; re-run extraction needs it up).
