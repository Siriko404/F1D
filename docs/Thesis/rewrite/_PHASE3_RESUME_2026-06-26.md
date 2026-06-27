# RESUME — Phase-3 masking propagation: PROPOSED-FIX clones DONE, ready to APPLY (2026-06-26)

> ⚠️ **SUPERSEDED BY THE AUDIT LAYER (2026-06-27).** The proposed fixes below were then AUDITED.
> **Start at `_audit/_AUDIT_RESUME_2026-06-27.md`** (17 findings in `_audit/audit.json`; nothing applied;
> P3.4 needs ratify; spine-vs-data sweep decision pending). This doc remains the record of the fixes themselves.

> **THE current entry point.** SUPERSEDES the harness-era docs (`_PHASE3_HARNESS_RESUME.md`,
> `_PHASE4_FORK_PROMPT_1.md`, `_PHASE4_HARNESS_HANDOFF.md`, `_PHASE4_S2_MODSPEC.md`) — those describe a
> multi-agent **harness that was ABANDONED**. We did the redesign **MANUALLY**, section by section.
> **Do NOT build a harness.** Treat all memory as unverified; the files + commits are truth.

## WHAT WE DID (this session) — append PROPOSED FIXES to every section, by hand
The masking redesign was propagated across **all 16 section paragraph-ledgers** as **PROPOSED fixes
appended under a top-level `_proposed_fixes` key — NOT applied.** Method per section:
clone the pristine ledger → strip locked `final_prose` → investigate (grep `placebo` + a BROAD
contradiction grep, classify each hit) → append fixes (NLM evidence **copied-by-CODE**; pointers
elsewhere) → advisor-audit → commit. Clones in `docs/Thesis/rewrite/_phase3_clones/`. Originals PRISTINE.

## STATUS — all 16 done, verified, committed
| section | fixes | nature |
|---|---|---|
| §2.1 | 14 | masking re-derivation: P5 +5 props (S-V motive, Louis behavior, thewissen tone, managed-comparison synthesis, cross-channel firewall), P4 guardrail + `_plan`, placebo→comparison |
| §2.2 | 8 | placebo→managed-comparison (×4) + **P3.4 attenuation** (the cash>stock motivation, deferred here from 2.1) |
| §2.3, §2.5 | 0 | reviewed → **untouched** |
| §2.4 | 2 | placebo→comparison (stmt+role); MA3 Wald unchanged |
| §3.1–3.4 | 38 | **surgical** placebo→comparison sweep (identifiers protected) + 2 no-suppression locks |
| §1 | 11 | sweep + **3 motivation rewords** (1-P8 "why cash concentrates left open" → motivated, all 3 sibling fields) |
| abstract | 5 | sweep + lock (motivation clause **DROPPED** — suppression-misread risk in the zero-caveat zone) |
| §4.1–4.4 | 0 | reviewed → **untouched** (4.2 "inert" = residual-unpriced, NOT stock-placebo) |
| §5 | 9 | sweep + **2 motivation rewords** (5-P5-a limitations, 5-P7-b future-work: "why cash" → motivated) |

**Verified (clone-verify, 16/16 PASS):** `final_prose` empty · chain **byte-identical** to pristine
original (fixes appended ONLY, never applied to the chain) · every fix carries its evidence (NLM
ADD_PROP = verbatim quotes **copied-by-code**; framing ADD_PROP = verdict+note; SWEEP/REWORD = from/to;
locks = lock text). placebo identification-sweep + broad contradiction grep both grep-verified complete.

**Commits — branch `phase4/masking-rewrite-harness`:**
`ece8b553` (s2) · `3866e3af` (s3) · `ecd02201` (s1+abstract) · `37867c3e` (s4+s5) ·
`00ea72cf` (removed the 8 stray `subsection_plan.json` — off-disk, git-recoverable).

## THE CONTENT TRUTH (unchanged — point here, do not re-derive)
- **Decision + masking framework + cite stack:** `_PHASE3_CONCLUSION.md` (still accurate).
- **NLM-verified verbatim evidence:** `tmp/nlm_masking_cites.json` (Shleifer-Vishny + Louis, SUPPORTED).
- **HONESTY FLOOR (non-negotiable):** cash run-up **+0.0461\*\*\*** / stock **−0.0429 n.s.** (noisy flat
  null). **NO "stock suppressed"** — the gap is **cash rising**. Masking = **MOTIVATION, not mechanism**.
  Cite S-V/Louis as **earnings/valuation, NEVER tone**; thewissen = tone (preprint, supplementary).
- **placebo→comparison** wherever it does identification work; **KEEP** `tab:empire_drop_placebo` +
  `placebo_cash_PRE1` / `placebo_stock_PRE1` (fixed identifiers across 18 files — renaming breaks them).
- Two different "why"s stay OPEN (NOT touched): the **source** mechanism (compliance-vs-strategic) and
  the **war-chest CAUSE** leg (C6 cause n.s.). Only the **effect-concentration why** became motivated.

## NEXT — NOT done; gated on Sina's ratify-to-apply
1. **Apply** the `_proposed_fixes` to the chains (reword from→to · ADD props · sweeps · locks).
2. **Regenerate `final_prose`** for changed paragraphs from the redesigned chains (currently blank).
3. **+2 `\bibitem`** (`shleifer_vishny2003`, `louis2004`) in `thesis_draft.tex` — else undefined-cite on compile.
4. **Retire originals** — only when 100% safe.
5. **Compile + verify** the draft.

## TOOLS (committed under `tmp/`)
`clone_strip_prose.py` (generic clone+strip) · `append_s2_proposed_fixes.py` ·
`append_s3_proposed_fixes.py` · `append_s1abs_proposed_fixes.py` · `append_s4_5_proposed_fixes.py` ·
`apply_s2_1_masking.py` (reference). NLM evidence source: `tmp/nlm_masking_cites.json`.

## HARD RULES (do not break)
- NLM evidence **COPIED-by-code** (deepcopy), never typed; statements/framing authored (OK).
- Fixes **APPENDED** under `_proposed_fixes`; originals **PRISTINE**; edit CLONES only.
- NO "stock suppressed"; motivation not mechanism; source + war-chest-cause stay open.
- advisor-vet before declaring done; ratify per step; no overclaim.
