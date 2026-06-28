# Phase-5 Prose-Writing Harness — DESIGN PROPOSAL (2026-06-28)

> STATUS: PROPOSAL for Sina ratification. Not built. Advisor-vetted before presentation.
> GOAL: turn the 16 locked-proposition ledgers (82 paragraphs) into audited LaTeX-ready
> `final_prose`, per the v2 type-rulebooks, then assemble → compile → PDF thesis.

## 0. The pieces (all verified from primary source this session)
- INPUT: `_final/section*_paragraph_ledger.json` — 16 files, 82 paragraphs, `final_prose=""` everywhere.
  Each prop carries: statement · numbers (with stars) · register_locks · depends_on · reason. Two formats (A: §2.1–2.5 dict; B: rest list).
- STYLE: `docs/papers/style_exemplars/_rulebooks_v2/{8 types}.json` — 62 evidence-grounded principles. Map: abstract→abstract, §1→intro, §2.1→lit_review, §2.2→hypotheses, §2.3-2.5→(methods/hypotheses), §3.1→data, §3.2-3.4/§4.5→results, §4.x→results/methods, §5→conclusion.
- OUTPUT CONTRACT (from `push_2_1_to_tex.py`): `final_prose` = **LaTeX-ready** prose with `\citep{key}` / `\emph{}`; spliced verbatim between `\subsection{}` anchors; **push ABORTS if any cite key lacks a `\bibitem`**.
- COMPILE: 16 ledgers → `push_*_to_tex.py` (deterministic) → per-section `_*_body.tex` → master `thesis_draft(_uottawa).tex` \inputs all + tables (outputs/) + `uo-ethesis.bib` → pdflatex → PDF.
- LESSONS: `HARNESS_DESIGN_LESSONS.md` (§6 build/embed/ASCII, §7 validate-one-first, §8 no-external-grader, §9 collab) + `_HARNESS_PRINCIPLES_battle_tested.md` (3 families; P1–P10; B1–B8).

## 1. Architecture — Sina's 4 layers mapped to PROVEN families
UNIT = one SECTION (16 units), fully independent (§1), sequential-batched for rate limits (B5).
Writing a whole section at once preserves intra-section flow.

```
 EMBEDDED BRIEF (one section): ordered props + type-rulebook + register-locks/bright-lines
                               + allowed cite-keys + table labels + adjacent-section seam context
   │
   ▼ L1  WRITER PANEL ........ 3 agents, paraphrased-identical, NO examples, NO caps   [chain P1]
   │        emit per-paragraph LaTeX final_prose + numbers_used[] + cite_keys[]
   ▼ GATE-W (deterministic JS, the spine) ........ number-trace · honesty-FORBID · cite-key · structure
   │        drop any draft that fabricates a number / trips a lock; all-3-fail → degrade+flag (P8)
   ▼ L2  WRITER RED-TEAM ..... 1 agent, RE-AUTHOR/synthesize best per paragraph        [chain B2]
   │        fixes flow, kills redundancy (§5 parsimony), one consolidated section draft
   ▼ GATE-W' (same JS gate re-run on L2 output — it writes, so re-check)
   │
   ▼ L3  AUDIT PANEL ......... 6 agents, EXCLUSIVE lanes, PROPOSE-only (P9 describe-only)  [referee P7]
   │        1 honesty/register · 2 number-context · 3 rulebook · 4 citation · 5 flow/voice/seam · 6 completeness/depends_on
   │        each emits issues{paragraph,severity,issue,proposed_fix,evidence}. NO rewriting.
   ▼ L4  DELIVERY RED-TEAM / JUDGE  1 agent, refute-by-default + bounded re-author       [referee B4 + B2]
   │        dedup across lanes · accept valid fixes & APPLY (ONE pass) · reject spurious · emit FINAL section json
   ▼ GATE-FINAL (deterministic JS, hard floor) .... number-trace · honesty · cite-resolves · prop→paragraph bijection
            CLEAN → write final_prose to the section ledger (materialize, §8)
            RESIDUAL VIOLATION → do NOT loop; emit BLOCKED + flags for human (P10)
```

Checker authority gradient honored: L2 re-authors (chain) → L3 describes-only (referee P9) → L4 culls+applies (referee B4).

## 2. The deterministic gates = the anti-hallucination spine (§3 / P5 / "meaning-vs-mechanical")
Run INSIDE the workflow as JS (NOT an external grader — §8 forbids that). Scripts do the mechanical:
- **number-trace**: every coefficient-shaped token (decimal ≥3 places, e.g. `0.0391`) in `final_prose` ∈ the section's prop `numbers` (after digit/punct fold). Foreign stat number → drop. (Whitelist scaffolding ints/years so we don't false-reject — §3 scar.)
- **honesty-FORBID**: scan for `suppress·dampen·strict specificity·detect ·"we are the first"` + ensure each load-bearing register-lock word present where the prop carries it (schema-as-gate, P4).
- **cite-key**: every `\citep/\citet{key}` ∈ allowed bib keys (else flag for bibitem add).
- **structure/bijection**: every locked prop rendered exactly once; paragraph count stable; no empty prose.
Agents do the meaning (direction, soundness, register, flow) in L3.

## 3. Inputs the build step must embed (§6/§7 — harness can't read files at runtime)
External Python build script (reads the ledgers + rulebooks DIRECTLY, embeds per-section briefs into the
`.js` at an anchor; logs `[input] section:Nprops/Mcites` as line 1). ASCII-sanitize: `ensure_ascii=True`,
`newline="\n"`, escape smart quotes/em-dash, verify zero bytes >0x7f / no `\r` / no ctrl. node wrap-check.

## 4. Assembly + compile (deterministic post-steps — mechanical, allowed)
1. generalize `push_2_1_to_tex.py` → `push_all_to_tex.py`: each ledger final_prose → `_*_body.tex`.
2. collect all cite keys → verify/append bibitems vs `uo-ethesis.bib` (+2 known-needed: shleifer_vishny2003, louis2004).
3. master tex \inputs bodies + table floats + bib → `pdflatex` → PDF. Compile success = mechanical check (not grading).

## 5. Execution discipline (§7 / B5 / §9)
- **VALIDATE-FIRST = §4.5, END-TO-END TO A COMPILING PDF.** §4.5 is small (3 paras), results-type (our dominant
  type), honesty-sensitive (Wald, mechanism-open, no "strict specificity"), and already 69/69-verified — the ideal
  pilot. Prove the WHOLE pipe on it: write → audit → final json → push_to_tex → **`pdflatex` success**. The unproven
  surface is the OUTPUT CONTRACT (LaTeX prose, `\citep` resolution, splice, compile), not prose quality — prove that
  before writing 16 sections that could share a systematic LaTeX/citation defect. Also plant ONE honesty violation in
  the pilot to confirm the gates + lane-1 catch it. THEN release the rest in SEQUENTIAL batches (peak ≤ ~3 sections).
- **Seams use adjacent THIN_CLAIMS, never prior `final_prose`** — parallel batches mean the prior section's prose isn't
  written yet; depending on it would secretly kill unit independence. Thin_claims are available from the locked ledger.
- Resume granularity = per-section ledger on disk (B1). Re-run a section = re-run its unit only.
- Token budget: 16 × ~11 agents = ~176 agents + iteration. LARGE. Pipeline per section so it streams; batch sequentially.

## 6. DEVIATIONS from battle-tested (flag + advisor-vet — these are the risks)
1. **4 agent layers, not 2.** Justified: generation+audit ≠ extraction (§8 scope note permits re-judging §1–5).
2. **Bounded auto-fix at L4.** No template exists (P10 / "ABSENT in all 9"). Mitigation: SINGLE adjudication pass +
   final deterministic gate + flag-to-human on residual (NOT an unbounded retry loop). Riskiest piece.
3. **★ THE TRADE Sina must consciously make — BIMODAL reversal.** Until now Sina personally authored the load-bearing
   masking/honesty-floor FRAMING; BIMODAL reserved it for him. This harness hands that to agents. The deterministic
   FORBID gate canNOT catch a subtly-causal framing built from ALLOWED words ("cash acquirers elevate uncertainty
   ahead of deals" trips no FORBID term) — only L3-lane-1 (an agent) defends it. So the output is **an audited DRAFT
   with flagged residuals, NOT a hands-off final thesis**, and BLOCKED sections may be exactly the honesty-critical
   ones he is too numb to adjudicate. He may still say go — but knowingly. This is the decision, not a footnote.
4. **Writers emit LaTeX** (not plain) — forced by the push_to_tex contract.

## 7. PREREQUISITES (RESOLVED — input IS ready; the "lock" scare was stale bookkeeping)
- **`prose_gate.unlocked` is STALE/inconsistent bookkeeping, NOT the readiness signal.** Proof: §1 and §5 are
  `all_supported=True` but `unlocked=False` (contradiction if the flag tracked readiness); and all 15 non-§4.5
  sections share one lifecycle status `prose_status="PROSE-STRIPPED ... prose regenerated after chain ratified"`.
  → There is NO 46-paragraph ratify blocker. Do not gate the harness on `unlocked`.
- **★ "Audited" ≠ "number-verified-vs-source" — the gap I slid past; CLOSED by a new harness gate.** The 15 non-§4.5
  sections passed the 74b7a0f8 referee OVERCLAIM audit, but only §4.5 got §4.5-level number-vs-source tracing (69/69
  this session) — and that very audit STILL missed §4.5's within-R² gap. So audited ≠ verified, by my own demonstrated
  standard. My prose gates guarantee prose-faithful-to-prop; NOTHING yet guarantees prop-true-to-source. A flawless
  renderer of an unverified prop = a polished FALSE statement that passes every gate. CLOSURE (conservative, mechanical,
  one pass): fold the `verify_45_claims.py` prop-number-vs-source-table logic into the harness as a **PRE-WRITE GATE
  over all 16 sections** — every prop number must trace to its source table cell / result json BEFORE any prose is
  written. This is the most conservative move and exactly what "design flawlessly, run once" demands.
- **§4.5 is the one explicit exception**: still `prose_status=PROPOSAL`, verified 69/69 this session, awaits one `unlock`.
  → It becomes the VALIDATE-FIRST unit (small, results-type, honesty-sensitive) the moment Sina unlocks it.
- **Compile target**: `thesis_draft.tex` (inline biblio) vs `uo-ethesis` uottawa template (.bib). Recommend uottawa (formal).

## 8. Open decisions for Sina (the real forks)
1. **★ BIMODAL trade (§6.3):** authorize agents to write the load-bearing honesty framing (audited draft + flagged
   residuals, not a hands-off thesis)? GO / NO-GO. — *the one that matters.*
2. **L4 auto-fix:** bounded-single-pass + flag-residual (recommend) vs flag-ALL-to-human (safest, no auto-apply).
3. **Readiness criterion:** confirm "corpus-audited (74b7a0f8) = ready for prose" (one yes) — unblocks the 15 sections.
4. **Pilot:** §4.5 end-to-end-to-PDF (recommend) — needs the §4.5 `unlock` first.
- (Settled by evidence, not asking: unit = section, for flow; `unlocked` flag is stale, ignored.)

## 9. SAFETY AUDIT — single-run hardening (adversarial self-check)
**Honest verdict: NOT 100% machine-safe.** Three risks cannot be driven to zero by gates alone — (i) semantic honesty
(a smooth causal sentence built from ALLOWED words trips no denylist), (ii) correlated 3-writer error, (iii) first-time
LaTeX compile. The closures below take each as low as a single run can get; ONE short human skim closes the last gap.

### 9a. Gate hardening (deterministic — added beyond §2)
- **numbers — closed allowed-set per paragraph** = that paragraph's prop `numbers[]` PLUS verbatim magnitude phrases
  from the prop `statement` ("roughly a third of a residual standard deviation"). **Signed tokens required**
  (`-0.0348` ≠ `0.0348` → catches sign flips). Scaffolding ints/years whitelisted so we don't false-reject (§3 scar).
- **citations — CLOSED whitelist per paragraph** = only the cite keys that paragraph's props carry. A new/extra key → reject
  (kills mis-attribution + invented cites deterministically).
- **bijection** — writer tags each sentence with its `prop_id`; gate asserts every locked prop rendered exactly once,
  none added, none dropped.
- **LaTeX-lint gate (pre-compile)** — balanced braces, escaped `% & _ #`, known macros only → stops a SYSTEMATIC compile
  failure before it hits all 82 paragraphs.
- **lexical-traceability flag** — any load-bearing sentence whose content-words/verbs aren't traceable to its prop →
  forced lane-1 review (catches "to mask" drift that the FORBID list misses).
- **causal-construction denylist (constructions, not just words)** — cause/drive/induce/manage/manipulate/"in order to"/
  "to mask"/"so as to" near the masking subject → flag.

### 9b. Agent-layer hardening
- **lane-1 HONESTY = 3-agent refute-by-default sub-panel** (not 1). Majority-refute → section BLOCKED. The semantic
  honesty check gets redundancy because it is the thesis-killer dimension.
- **L4 = MINIMAL-EDIT adjudicator** — prefer the audited L2 draft; apply only high-confidence fixes; LOG every diff;
  a large rewrite is itself a flag. Re-gate after L4 (it writes).
- **null-degrade every agent** (dead agent → flag, never crash). Build-time assert `embedded prop count == ledger`;
  per-section count logged as line 1 (a dropped input screams immediately — §7).

### 9c. Systematic-risk closure
- **§4.5 pilot → COMPILING PDF first** confines any LaTeX/citation/plumbing defect to 3 paragraphs (else all 82 fail
  together). This is the single highest-value safety measure; it is real kept output, not a throwaway dry run.
- **Assembly-time deterministic cross-section checks** — `\label` uniqueness, `\ref` resolution, bibitem completeness,
  terminology consistency — before the full `pdflatex`.

### 9d. The ONE residual the machine cannot close → a 5-minute human SKIM (reading, not writing)
A causal sentence made of allowed words can pass every gate AND slip a 3-agent honesty panel. The only 100% backstop on
the thesis-killer dimension is a human reading the ~12–15 auto-extracted **load-bearing sentences** (a digest, not the
whole thesis). This is a SKIM, not authoring — consistent with "nothing for me to write." **Timing: this happens BEFORE
SUBMISSION, not before the run** — it never blocks progress and demands no judgment from a currently-numb user; it is the
last gate before the thesis leaves the building, whenever capacity returns. **Do not ship without it.** Without the skim,
the honesty floor rests entirely on agents (residual, non-zero).

**SAFETY VERDICT:** all closures + the §4.5 pilot-to-PDF + the 15-sentence skim = as safe as a single-run harness gets.
Claiming literal "100%" without the skim would be dishonest — the semantic-honesty residual is real and is exactly the
dimension that can sink the thesis.

## 10. THE WRITE-CRITERIA — the v2 rulebooks (all 62 principles ingested 2026-06-28)
Each writer's style contract = its section TYPE's principle list, embedded VERBATIM (device + principle). Section→type:
abstract→abstract(8) · §1→intro(9) · §2.1→lit_review(8) · §2.2→hypotheses(7) · §2.3/2.4/2.5→methods(7, design/measurement/
identification) · §3.1→data(9) · §3.2/3.3/3.4→results(7) · §4.1–4.5→results(7, robustness) · §5→conclusion(7). (§2.3-2.5
map needs a one-line Sina OK.)

### KEY FINDING — rulebooks ENCODE the honesty floor (reinforcement, not tension)
6 of 8 types carry an explicit hedge/self-limit rule that IS the register-lock in style form:
- results "Hedge and self-limit" (*'only suggestive','we should not overstate','do not push too far'*) = supportive-not-definitive.
- results "Raise the rival, then refute it" + methods "Concede-then-counter" + data "Referee-proofing" = the mechanism-open / threat-disclosure register.
- abstract "Calibrated Assertion" (findings flat, broad takeaway hedged) · lit_review/hypotheses "Calibrated hedging" (may/might/tend to).
→ The writer is told the hedges are MANDATORY (style AND honesty). lane-1 (honesty) and lane-3 (rulebook) overlap here, double-covering the thesis-killer sentences.

### Cross-cutting universals (every writer, all types)
first-person agentive "we"-voice + active research verbs · calibrated hedging · concrete anchors (exact estimates/N/dates/
tangible magnitudes) · connective signposting (However/Thus/Moreover) · enumerated parallel scaffolding (First/Second).

### ~5 principles become DETERMINISTIC soft-gate flags (cheap, mechanical — feed lane-3)
- first-person voice present (we/I + research verb) · intro "Terminal Roadmap" = the LAST §1 paragraph maps Section 2…3…
- results "Exhibit-anchored": each finding sentence names a Table/Panel/Row · results "Magnitude made concrete": coefficient
  paired with a tangible-unit/benchmark gloss · enumerated-marker presence where the type expects it.
(Soft = flag for the rulebook lane, not a hard reject — style is semantic; the agent judges, the flag points.)
