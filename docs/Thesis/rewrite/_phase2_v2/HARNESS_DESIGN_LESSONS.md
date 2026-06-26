# Harness-Design Lessons (Workflow multi-agent harnesses)

Hard-won from the Phase-1 + Phase-2(v2) style-analysis harnesses. **Read this in full before designing any new harness.** These are battle-scars, not theory — each line cost a wasted run or a furious correction.

Reference implementation (proven, copy it): `docs/Thesis/rewrite/style_phase2_v2_principles.js`
Build/embed/finalize: `docs/Thesis/rewrite/_phase2_v2/{build_v2.py, prep_all.py, finalize_v2.py}`

> **SCOPE — which lessons transfer.** §1–5 are specific to the *extraction* pattern (panel → gate → red-team, evidence-anchored). If the next harness is a **different shape** (e.g. generation / rewrite / multi-stage pipeline), re-judge §1–5 rather than copy them. **§6 (Workflow-tool gotchas), §7 (input integrity + validate-one-before-all), §8 (process), §9 (collaboration) are UNIVERSAL — they apply to any Workflow harness.**

---

## 1. THE PROVEN SHAPE — copy this skeleton

Per **unit** (e.g. per writing-type), **fully independent**, **NO global / cross-unit step ever**:

```
embedded data (ONE unit) 
  -> L1: PANEL = 3 agents, IDENTICAL task, HEAVILY paraphrased prompts
  -> GATE: deterministic JS (no LLM) — verbatim-evidence + cardinality, drops fakes
  -> L2: RED-TEAM = 1 agent, scrutinize (drop false) + synthesize (merge dups) BY REFERENCE
  -> MATERIALIZE: JS copies survivors VERBATIM to disk
```

- **Two agent layers only.** Panel is ONE layer (3 paraphrased agents). Red-team is ONE layer (1 agent). Nothing else.
- **NEVER** a global/finalize/classify step that spans multiple units. **NEVER** one agent doing two units. (Both mistakes cost ~30 min each + fury.)
- Units run independently and are batched for rate limits (see §7).

## 2. PANEL NEURODIVERSITY — the non-negotiable rule

- **NO EXAMPLES in agent prompts. Ever.** An example ANCHORS/contaminates every agent toward the same answer and kills the panel's whole reason to exist. This was repeated ~"a thousand times."
- The 3 panel agents have **EXACTLY the same task, constraints, and output contract** — the ONLY difference is the prompt is **heavily paraphrased** 3 ways (3 distinct voices). That paraphrase IS the diversity.
- Paraphrase the **whole instruction body** per agent (not just the head), but keep the *hard constraints* (evidence rules, scope, no-invented-numbers) **semantically identical** across all 3 — vary voice, not constraint strength.
- Make instructions + capabilities **explicit but OPEN**. Never give a checklist or a cap — a cap causes missed findings. ("Never limit the panel; a missed finding is the danger.")
- **TOOL_LOCK stays byte-identical** across all agents (it's an execution lock, not analysis prose).

## 3. ANTI-HALLUCINATION = the deterministic JS gate (the spine)

- Every claim an agent makes MUST carry **verbatim evidence quotes** copied from the source. The gate (`norm()` + `isSub()`) checks each quote is an exact substring (after unicode/punct/digit folding) of its **CLAIMED** source. Non-verbatim → dropped mechanically. **LLMs never self-grade.**
- **Cardinality:** require ≥2 quotes from ≥2 **distinct** sources → forces a *cross-source pattern*, not one source's quirk.
- Match each quote against its **claimed source only** — NO all-sources fallback — so "cross-source" cannot be faked by a mislabel.
- **Compute locators (paragraph index, etc.) in the GATE, not the agent.** Agents get off-by-one / span boundaries; the gate is exact. Never *gate on* an agent-provided locator — it causes silent false-rejects of good quotes.
- **RELATIVE never ABSOLUTE.** A rule's target is the evidence itself, never an invented numeric threshold ("≤20 words"). The gate can't check this (semantic) — the RED-TEAM enforces it.
- Drop the gate's number-checks unless you truly need them — they false-reject on scaffolding digits (Phase/Section/Table N). Simpler gate = fewer false rejects.

## 4. RED-TEAM = scrutinize + synthesize, BY REFERENCE

- It emits **ID decisions only** (`keep / merge / reject / side_notes`); the JS main-loop copies the kept items **verbatim**. Because it never writes prose, **meaning-drift is structurally impossible**.
- It carries the **heavy semantic load** (esp. when output isn't comparative). **Arm it:** give it the **FULL evidence quotes** (not summaries) + **explicit reject CATEGORIES** — fake-evidence, invented-absolute-threshold, content-not-style, vacuous, compound/coarse. (Categories are instructions, NOT examples — allowed. Concrete *sample strings* are examples — forbidden.)
- `merge` collapses **duplicate devices** across the 3 agents → one canonical (tiebreak: more / higher-authority evidence). It does **NOT** group near-synonyms — see §5.
- `side_notes` = coverage-gap flags for a human, **never** new items.

## 5. PARSIMONY / ALTITUDE — the over-engineering trap

- Max-recall at the panel produces an **atomic, over-granular** list (26 micro-rules to write one abstract = "over-engineering as fuck").
- **Fix at the PANEL, not the red-team.** Tune the panel prompt to extract **consolidated, mid-level** principles: *"capture the MAJOR, load-bearing devices; consolidate related observations under one principle; a short high-level list, not an exhaustive catalogue."* (The red-team only merges *identical* devices, not near-synonyms, so it can't fix granularity.)
- **Watch over-correction:** too aggressive → a few vague rules ("write clearly"). Judge by **ACTIONABLE, not count.** 8 sharp > 26 atomic; but 14 sharp > 7 vague.

## 6. WORKFLOW-TOOL HARD GOTCHAS (each one silently sinks a run)

- **The harness CANNOT read files at runtime** (no fs/Node API). Source data must be **embedded into the script body by an EXTERNAL build step** (replace an anchor line like `__TYPES_ANCHOR__`), then run via `scriptPath`. Do **NOT** pass big data via `args` (giant inline pastes silently DROP content — caused −12 findings once).
- **`args` may arrive as a JSON STRING.** Guard at top: `if (typeof args==='string') args = JSON.parse(args)`.
- **The approval dialog REJECTS control / non-ASCII / hidden / CRLF characters in the script.** The build step MUST:
  - strip hidden chars (soft-hyphen U+00AD, zero-width U+200B–200D, BOM) from embedded text;
  - `json.dumps(..., ensure_ascii=True)` so all data is pure ASCII;
  - write the file with `newline="\n"` (Python's default CRLF puts `\r` in → **rejected**);
  - keep the *template itself* pure-ASCII (escape smart quotes/em-dashes as `\uXXXX`).
  - Verify: scan the generated file for any byte `>0x7f`, any `\r`, any ctrl `<0x20` except `\n\t` → must be ZERO before spawning.
- **node --check FAILS** on the harness (top-level `await`/`return` are valid in the Workflow async wrapper but not standalone). Wrap-check instead: `new Function('a','l','p',..., '(async()=>{'+src.replace('export const meta','const meta')+'})')`.
- **Degrade guards, never crash a unit:** red-team returns NULL (timeout) → degrade to gate-clean (flag re-run); red-team `keep/merge` IDs match nothing (keeps-0) → degrade to gate-clean (flag).
- **TOOL_LOCK** (exactly one StructuredOutput call, no other tools) → fast, cheap, no multi-turn runaway.
- **Schema-forced output** (StructuredOutput + JSON schema) → clean data, model retries on mismatch, no free-prose parsing.

## 7. INPUT INTEGRITY + EXECUTION

- **WE pre-extract/curate the source data; the harness only analyzes it.** Never make the harness do the extraction.
- Build the embed via a **durable script** that reads the source files directly, and **LOG per-unit counts as the FIRST line** (`[input] type:Npapers/Mparas`) so a dropped/short input screams immediately.
- **Multi-section bug class:** when the same source appears as several entries (e.g. one paper's many sections), **accumulate** its paragraphs in the index map — don't overwrite (`byPaper[p] = (byPaper[p]||[]).concat(...)`). Overwrite kept only the LAST section → 100% gate-reject (methods 0 → 7 after fix).
- **Concurrency / rate limits:** separate Workflow spawns do **NOT** share the per-workflow agent cap → firing many at once = rate-limit burst. Either batch units inside one run (default 2), or fire separate runs **sequentially / staggered ≥1 min apart**.
- **VALIDATE ON ONE UNIT FIRST** — pick a HARD unit that has the failure condition — **READ its full output**, confirm it works, THEN release the rest. Blind-firing N units = N zeros if a bug exists. (A code-correct-but-never-run fix is *unvalidated*.)
- Each run ≈ 10–15 min and a re-run doubles it. Smoke the SMALLEST unit for *plumbing*; validate *quality* on a HARD unit. Minimize total runs — that is the real budget.

## 8. PROCESS / VERIFICATION DISCIPLINE

- **READ the harness's FULL returned object** (the `.output` file on disk), not the truncated task-notification. (Got burned skipping this.)
- **NO external scripts may GRADE/AUDIT the output** (strict user rule). The harness's OWN agents + JS gate do the checking; you READ the returned object. Mechanical file ops (build args, embed data, write/extract result JSON) are FINE. **A `.js` workflow harness is NOT an audit script.**
- **Materialize results to durable disk immediately** (a `finalize` script that reads the `.output` and writes per-unit JSON) so returned objects don't evaporate into temp files.
- **Advisor-vet the design BEFORE the expensive run**, and again before declaring done. The advisor will even flip its own earlier advice once real output contradicts it — weight empirical output over prior advice.

## 9. COLLABORATION CONSTRAINTS (this user, but they shaped every decision)

- **Ultra-terse replies** (≤6–10 lines, visual, one idea per line). A long reply goes UNREAD = FAILED.
- **Literal obedience** > your "better" judgment. Do EXACTLY what was said.
- **TIME is the budget.** Every wasted/duplicate run is the cardinal sin. Smoke-test before any real run.
- Don't correct the user's arithmetic, don't lecture about "honesty" — acknowledge in one line and execute.
- When frustrated: STOP, name the cause in one line, fix the *right* thing — don't thrash (the CRLF/ASCII rabbit-hole was 8 wasted commands on a non-issue).
