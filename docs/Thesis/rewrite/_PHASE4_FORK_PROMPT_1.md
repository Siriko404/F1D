# FORK PROMPT #1 — Phase-4 harness design (paste verbatim into a fresh session)

> This is the onboarding + task brief for a forked session. It is deliberately exhaustive.
> A follow-up (FORK PROMPT #2) will answer whatever clarifications you raise after you read everything.
> **Do not write code or spawn anything until the design is approved by the user.**

---

## 0. WHO YOU ARE / WHAT THIS SESSION IS FOR

You are resuming an MSc thesis project (codename **F1D**, author Sina, U Ottawa). The thesis studies **CEO earnings-call Q&A speech-uncertainty in the run-up to undisclosed cash acquisitions**.

**Your ONE job this session:** *design* (not build) a **multi-agent Workflow harness** that **redesigns the §2 PROPOSITION CHAIN** so it carries a locked new "why-cash" framing (the **masking asymmetry**). Manual per-proposition editing is too slow; the harness automates it thoroughly + verifiably.

You will design the harness, get the user's approval section by section, advisor-vet it, then (a later session) build + run it. **Right now = design only.**

---

## 1. READ THESE FILES FIRST — FULLY, VERBATIM, IN THIS ORDER. RECITE NOTHING FROM MEMORY.

Worktree root: `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3`
All paths below are relative to that root unless absolute.

**Decision + context (the locked truth):**
1. `docs/Thesis/rewrite/_PHASE4_HARNESS_HANDOFF.md` — master pointer: the decision, honesty floor, cite stack, the §2 mod-set, what's done/pending, the harness sketch, isolation rules. **Read every section.**
2. `docs/Thesis/rewrite/_PHASE3_CONCLUSION.md` — **authoritative** decision + masking framework + cite stack (EVIDENCE DOSSIER §C) + register + ADVISOR ADDENDUM 1–6.
3. `docs/Thesis/rewrite/_PHASE3_STATE.md` — verify-first checklist + resume truth.
4. `docs/Thesis/rewrite/_PHASE4_S2_MODSPEC.md` — the §2 change/untouched map. **It is v1 — handoff §5 OVERRIDES it with 2 advisor fixes. Treat as reference, not gospel.**
5. `tmp/nlm_masking_cites.json` — the 3 locked cites' verbatim evidence (cited_text + page/section + verdicts).
6. `docs/Thesis/rewrite/section2_roadmap.md` — the design mandate (purpose) per subsection 2.1–2.5.
7. `docs/Thesis/rewrite/NLM_QUERY_GUIDE.md` — the NLM convention (any NEW cite must be verified this way).

**The data you will operate on — the proposition-chain ledgers (ONE per subsection):**
8. `docs/Thesis/rewrite/section2.1_paragraph_ledger.json` … `section2.5_paragraph_ledger.json`
   - **Do NOT read these raw end-to-end** — they are ~2000 lines each, mostly verbatim NLM evidence dumps that will drown you (this burned the last session).
   - Instead run `tmp/extract_spine.py <ledger.json> <out.md>` → it strips the evidence noise and emits the **compact chain skeleton** (spine + per-paragraph intent + each proposition's statement/role/verdict). Read those skeletons.
   - Also: `tmp/dump_props.py` = verbatim proposition dump (all §2) if you need exact statement text.

**The reference / validation oracle:**
9. `tmp/apply_s2_1_mods.py` — the human+advisor **reference application** of the masking re-derivation to **§2.1** (encodes BOTH advisor fixes). This is your **validation ORACLE**, not a recipe to feed the agents (see §5).

**Optional but recommended (harness-design battle-scars from the Phase-2 harness):**
10. `C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\_phase2_v2\HARNESS_DESIGN_LESSONS.md` — lives on the **other worktree** (`F1D`, debug branch). §6–9 (Workflow-tool gotchas, input integrity, process, collaboration) are UNIVERSAL and apply here. Read for reuse; do not copy the extraction-specific parts blindly.

---

## 2. THE DATA MODEL — learn this exactly (the last session confused two levels and the user exploded)

The thesis §2 is **not free prose**. It is a **PROPOSITION CHAIN**, stored as one JSON ledger per subsection (2.1–2.5). Schema (verbatim from the ledger's own `_schema`):

> "paragraphs = fields keyed P1..Pn. Each paragraph field has subfields: plan (intent/serves/boundary/thin_claim/guardrails) + propositions[] + prose_gate + final_prose."

```
section2.X_paragraph_ledger.json
├─ _plan
│   ├─ section_job          ← what this subsection must accomplish
│   ├─ spine                ← the one-line logical chain of the subsection
│   └─ logic_chain_validated ← named links (A1_sign, A2_contrast, P4_necessity, …) = the CHAIN logic
├─ papers / legal_sources   ← cite registry
└─ paragraphs
    ├─ P1 { intent, serves, boundary, thin_claim, guardrails[], propositions[], prose_gate, final_prose }
    ├─ P2 { … }
    └─ P5 { …, propositions: [ {prop_id:"P5.1", statement, role_in_paragraph, type, source, verification{evidence, verdict}}, … ] }
```

- `prop_type ∈ {external-NLM, legal-primary, definitional, framing-nonverifiable, internal-table}`
- `verdict ∈ {PENDING, SUPPORTED, OVERCLAIM, UNSUPPORTED, INCONCLUSIVE_MANUAL}`
- **Gate rule:** `final_prose` stays EMPTY + `prose_status = BLOCKED` until every proposition in the paragraph is verified. **We redesign the CHAIN; we do NOT write final_prose this phase — it stays BLOCKED.**
- **Evidence rule:** the only admissible evidence is **verbatim** `cited_text` in `proposition.verification.evidence[]` (NLM-sourced).

### ⚠️ TWO LEVELS — never confuse them (this is the mistake that enraged the user):
| Level | What it is | Role |
|---|---|---|
| **Section-2 proposition chain** | the section-wide logical spine across 2.1→2.5 (`_plan.spine` + `logic_chain_validated` + the ordered proposition statements) | **THIS is the unit we redesign** |
| **subsection paragraph propositions** | the granular `P1.1 / P1.2 …` inside one subsection's paragraphs, with their NLM evidence dumps | read for detail only — do NOT mistake one subsection's paragraph props for "the section-2 chain" |

When the user says "**the entire section-2 proposition chain**," he means the **spine across all five subsections**, not one subsection's paragraph-level propositions.

---

## 3. THE LOCKED DECISION (Phase 3 — NOT for the harness to re-decide)

**Why-cash = the masking asymmetry:**
```
STOCK deal → pays in equity (a currency whose price matters) → incentive to keep valuation high
           → manages perceptions UP pre-deal (scripted optimism)
CASH  deal → pays in cash (no currency to protect) → no such incentive
           ⟹ cash = the (relatively) UNMANAGED window where the disclosure-strain surfaces
             as unscripted Q&A uncertainty ⟹ the run-up CONCENTRATES in cash
```
It is **MOTIVATION** (an ex-ante reason to focus on cash), **NOT a tested mechanism**.

### HONESTY FLOOR — non-negotiable. Every harness check must enforce these:
- Data: cash run-up **+0.0461\*\*\*** (p=.0074); stock **−0.0429 n.s.** (noisy flat null); Wald cash−stock **0.0983\*\*** (p=.039, two-tailed).
- **NEVER say "stock suppressed."** The differential (cash>stock) is framed as **ATTENUATION** (stock smaller/noisier), NOT stock pushed below baseline. The observed gap = **cash rising**. "We interpret, we do not detect."
- **Cross-channel bridge:** the cites document management in *scripted* channels (earnings numbers, press-release tone); our DV is the *unscripted* Q&A residual, net of the scripted presentation → we read the **hardest-to-manage** channel → frame as a STRENGTH, not a gap.
- Register locks stay: **correlational · no-identification · concentration-not-strict-specificity · mechanism-open · supportive-not-definitive.**
- **C1 (the timing round-trip) carries the paper independent of masking** — if a reader rejects the why-cash, the empirical contribution survives.

### CITE STACK (locked, NLM-verified — keys exact):
| key | paper | leg | discipline |
|---|---|---|---|
| `shleifer_vishny2003` | Shleifer & Vishny 2003, JFE 70:295–311 | currency/valuation MOTIVE | cite as valuation, **never tone** |
| `louis2004` | Louis 2004, JFE 74:121–148 | pre-deal EARNINGS behavior | cite as earnings, **never tone** |
| `thewissen2024` | thewissen 2024, SSRN **preprint** | TONE (our axis) | supplementary one-clause pointer only |
- `+2 \bibitem` required in `thesis_draft.tex` (`shleifer_vishny2003`, `louis2004`) — undefined-cite compile risk if missed.

---

## 4. THE HARNESS TOPOLOGY (LOCKED by the user — do NOT change the agent shape)

**One harness per unit** (unit = one subsection; granularity is pending the user's confirm — see §9-Q1). Inside each harness:

```
  current §2.X proposition chain  +  locked decision (§3)  +  honesty floor  +  cite stack
                                   │
                                   ▼
 PANEL 1 — PROPOSE    3 neurodiverse agents · identical task · heavily paraphrased prompts · NO EXAMPLES
                      Each reads the chain + the locked inputs and DECIDES, on its own,
                      WHAT in the chain needs changing and HOW (which props to add / demote /
                      reword / re-derive). → 3 independent proposed redesigns
                                   │
                                   ▼
 PANEL 2 — SCRUTINIZE+FIX  3 neurodiverse agents · each reads ALL 3 Panel-1 proposals,
                      rigorously scrutinizes them (honesty floor, cite discipline, chain logic,
                      coherence) and FIXES → each emits 1 hardened, corrected redesign (→ 3 hardened)
                                   │
                                   ▼
 RED TEAM — 1 agent   reads ALL 3 Panel-2 hardened redesigns, final scrutiny + SYNTHESIZE
                      → 1 final redesigned proposition chain
```

- **Neurodiversity = heavy paraphrase of the SAME instructions** across the 3 agents in a panel. **NO EXAMPLES anywhere in agent prompts** — an example anchors/contaminates all 3 agents and destroys the panel's purpose. (The user has repeated this many times.)
- Panels 1 and 2 each have **3** agents; the red team is **1**. That is the entire agent topology. Do not add or remove agent layers.

---

## 5. THE DESIGN STANCE THAT OVERRIDES THE OLD DOCS (user directive, this session)

**Panel 1 DECIDES what to change and how. It is NOT handed a pre-written recipe.**

- The handoff §9 says "propose mods *constrained by §6 mod-set*." **The user has overridden this:** deciding which propositions change and exactly how is **Panel 1's job**, derived from the locked masking decision (§3) + the current chain — not dictated by us or by the modspec.
- Therefore `_PHASE4_S2_MODSPEC.md` and `tmp/apply_s2_1_mods.py` are a **VALIDATION ORACLE + reference for §2.1 only**, NOT inputs fed to the panel. For §2.2+ and the downstream sections there is no human answer yet — the harness must produce it.
- **Confirm this stance with the user before building** (it is the single most important design decision and it reverses the handoff's wording).

### Panel-1 information boundary — LOAD-BEARING. Enforce it in the harness.
- **Panel 1 RECEIVES, and ONLY this:** the masking decision (§3 framing) + the honesty floor + the cite stack + the current proposition chain (spine + propositions).
- **Panel 1 MUST NEVER RECEIVE:** the modspec, `apply_s2_1_mods.py`, the §6 scope map, or ANY pre-decided "which subsections/props change" or "how to change them." That is the *answer* — feeding it means Panel 1 is no longer deciding. This is the **same no-anchoring rule as "no examples," applied to SCOPE.**
- §3's framing IS a legitimate input (the locked thesis decision the panel must realize). §6's scope map and the §2.1 oracle are NOT.

---

## 6. SCOPE MAP — ⚠️ DESIGNER CONTEXT ONLY. NEVER a Panel-1 input (it is the answer).

> This section tells YOU (the designer) and the validation/red-team layers what the human expects, so you can sanity-check coverage and build the oracle. It must **never** be placed in a Panel-1 prompt — Panel 1 decides scope itself (§5 boundary).

- **First targets (the §2 chain):** subsections **2.1, 2.2, 2.4** carry real masking edits; **2.3 and 2.5** are essentially untouched (confirm against the chain). The heaviest edit is §2.1's why-cash node (one proposition becomes several) and its mirror in §2.2. A recurring terminology sweep: the word **"placebo" → "comparison"** wherever it does logic work.
- **Most of §2 stays UNTOUCHED** — the redesign is surgical, but **Panel 1 determines exactly what** (do not pre-decide it).
- **Downstream (the harness must generalize here, do NOT skip):** §1 intro, abstract, §3.1–3.4, §5. **§3 is NOT a mechanical mirror** — there are ~60 "placebo" occurrences in §3.2/3.3/3.4 results-interpretation prose, and that is exactly where "stock suppressed" can sneak in. Sweep + guard hard there.

---

## 7. THE 5 TRAPS THAT BURNED THE LAST SESSION — avoid them

1. **Reciting from memory.** Read the actual files/JSON. The user catches paraphrase-from-memory instantly and it enrages him.
2. **Confusing the two levels.** "Section-2 chain" = the spine across 2.1–2.5. Not one subsection's `P1.1/P1.2`.
3. **Deciding the edits yourself / feeding a recipe.** Panel 1 decides what+how. Your job is to design the harness, not to author the §2 changes.
4. **Drowning in evidence dumps.** Use `extract_spine.py`; don't read the 2000-line raw ledgers.
5. **Bloat / overclaim.** Most of §2 is untouched; never invent an "old reason" or a numeric threshold; never imply stock suppression.

---

## 8. HARD CONSTRAINTS (carry into every design choice)

- **Edit CLONES only**; originals pristine; retire when safe. `final_prose` stays **BLOCKED** (chain redesign only, not prose).
- **NLM is the SOLE paper authority** — never read a paper PDF for content; verbatim-verify any NEW cite via the NLM guide. No memory-sourced cites/theories.
- **Anti-meaning-drift principle (recommended, from the Phase-2 harness):** when the harness APPLIES the final chain, untouched propositions should be **copied verbatim by code from the original**, never re-emitted by an agent — so drift on untouched text is structurally impossible. Agents only ever emit the *changed* propositions.
- **Validation:** §2.1 has the `apply_s2_1_mods.py` oracle. **Run the harness on §2.1 blind → diff vs the oracle → only release other subsections once it matches.** Validate ONE hard unit and READ its full output before firing all.
- **Workflow-tool gotchas (will silently sink a run):** the harness cannot read files at runtime → embed data via an external build step at an anchor line; `args` may arrive as a JSON string; the approval dialog rejects control/non-ASCII/CRLF characters; `node --check` fails on the async wrapper. (See HARNESS_DESIGN_LESSONS.md §6.)
- **Isolation:** worktree `…/F1D-phase3`, branch `phase4/masking-rewrite-harness`. **Data parquets + the `f1d` package live ONLY in `…/F1D`** — any data re-run executes from there. Do NOT touch `style_profiles/*` or `_rewrite_working/` (Phase-2's domain); do NOT run the Phase-2 harness; do NOT edit `_REWRITE_MASTER_LEDGER.md`.
- **Collaboration:** reply **ULTRA-terse** (the user is mentally exhausted; "too long" / "what?" = failure; lead with the answer; use a visual). **TIME is the budget** — smoke-test before any real run; minimize reruns. Ratify per subsection before commit. No overclaim.

---

## 9. OPEN DESIGN QUESTIONS — raise these with the user before building (do not silently pick)

1. **Unit = per subsection (2.1, 2.2, …)?** (the handoff says "per subsection"; the user has also said "per section" — confirm the granularity.)
2. **Is there a deterministic JS safety-gate around the agents?** (mechanical-only checks: change-set vs the chain, cites ∈ the locked 3, literal "suppress"/"placebo" tripwires — fed as advisory flags to Panels 2/red-team, hard-enforced before APPLY. Semantics stay 100% the agents' job.) — recommended, but confirm.
3. **Output schema per layer + the APPLY mechanism** (clone edit, untouched-preserved, final_prose blocked).
4. **Whether `apply_s2_1_mods.py`/modspec is oracle-only** (per §5) — confirm.

---

## 10. YOUR FIRST ACTIONS (in order)

1. Read every file in §1, fully. Recite nothing.
2. Run `extract_spine.py` on all five `section2.x` ledgers and read the compact chains.
3. **Ask the user for anything missing or ambiguous — files, context, decisions — BEFORE you design.** Be exhaustive; do not guess.
4. Then present the harness architecture (per-agent input/task/output, schemas, gate, apply, validation-on-§2.1 plan) for section-by-section approval.
5. Advisor-vet the design before any expensive run.

**Be exhaustive. If unsure, read more or ask. Do not flail or guess.**
