# Phase-2 REWRITE — PROGRESS LEDGER (durable, 100% compaction-safe)  2026-06-24

> **SINGLE SOURCE OF RESUME TRUTH.** After any compaction, read THIS first, then `_PHASE2_PLAN.md` (design + locked decisions 1–7).
> **Status now: scaffold COMPLETE · 0 / 16 rewritten · awaiting Sina's explicit "go" on the abstract.**

---

## HOW TO RESUME (post-compaction) — do this exactly
1. Read this file, then `_PHASE2_PLAN.md` (locked rules).
2. Find the first `NOT STARTED` row in the STATUS table (order is FIXED, top to bottom).
3. **Do NOT start without Sina's explicit "go".** One subsection at a time. HARD STOP at each ratify.
4. Run the decision-2 cycle for that subsection:
   `PULL 4 files → REWRITE → BY-HAND GATE → ADVISOR closed-checklist → Sina RATIFY → write new prose into the CLONE → update this row → commit`.

## LOCKED RULES (recap — full text in `_PHASE2_PLAN.md`)
- **No scripts** for the gate — by hand (Sina: "scripts are worst").
- **Clone is the write target; the ORIGINAL ledger is FROZEN** (spine source-of-truth + rollback).
- **Keep key jargon** ("residual", "information asymmetry", "bid-ask spread", …). Simplify sentence STRUCTURE only.
- **Per-subsection ratify** by Sina — NOT one end-review.
- **Constrained edit**: remove named anti-pattern, keep every proposition + protected string; splits ok; NO reorder / merge / add / drop.
- **Nothing touches the thesis prose** until Sina's final approval; rewrites live in the clones + diff files.

## THE 4 FILES PER SUBSECTION (the only inputs needed — 100% safe set)
1. **original** `docs/Thesis/rewrite/section*_paragraph_ledger.json` — FROZEN spine (props / number_audit / guardrails) + OLD prose.
2. **clone** `docs/Thesis/rewrite/_rewrite_working/section*_paragraph_ledger.json` — same spine, blank prose = write target.
3. **style profile** `docs/Thesis/rewrite/style_profiles/<type>_profile.json` — anti-patterns (filter by `para_id`).
4. **`_PHASE2_PLAN.md`** — workflow + by-hand gate + jargon rule + NEVER-traps.

Regenerate the clones any time (idempotent, originals untouched): `_rewrite_working/_clone_clean_ledgers.py`.

---

## STATUS — 16 subsections (FIXED order). ☐ = todo · ✅ = done
Profile column: resolve at PULL by `para_id` (8 section-level profiles span 16 subsections — confirm coverage per the advisor note). Props counted at PULL.

| # | subsection | original ledger | profile (confirm by para_id) | rewritten | gated | advisor | RATIFIED | diff file | commit |
|---|---|---|---|---|---|---|---|---|---|
| 1 | abstract | `section_abstract` | `abstract` (9 props) | ☐ | ☐ | ☐ | ☐ | `_PHASE2_diff_abstract.md` | — |
| 2 | 1 — intro | `section1` | `intro` | ☐ | ☐ | ☐ | ☐ | — | — |
| 3 | 2.1 | `section2.1` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 4 | 2.2 | `section2.2` | `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 5 | 2.3 | `section2.3` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 6 | 2.4 | `section2.4` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 7 | 2.5 | `section2.5` | `lit_review` / `hypotheses` | ☐ | ☐ | ☐ | ☐ | — | — |
| 8 | 3.1 | `section3.1` | `data` | ☐ | ☐ | ☐ | ☐ | — | — |
| 9 | 3.2 | `section3.2` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 10 | 3.3 | `section3.3` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 11 | 3.4 | `section3.4` | `results` / `methods` | ☐ | ☐ | ☐ | ☐ | — | — |
| 12 | 4.1 | `section4.1` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 13 | 4.2 | `section4.2` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 14 | 4.3 | `section4.3` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 15 | 4.4 | `section4.4` | `results` | ☐ | ☐ | ☐ | ☐ | — | — |
| 16 | 5 — conclusion | `section5` | `conclusion` | ☐ | ☐ | ☐ | ☐ | — | — |

**NEXT ACTION:** on Sina's "go" → run the abstract (row 1). Note: `_PHASE2_diff_abstract.md` holds a PRE-GO draft (jargon-stripped, superseded) — the fresh cycle OVERWRITES it; do not present it as a head-start.

## SCAFFOLD INVENTORY (what exists, committed)
- 16 clones + `_README.md` + `_clone_clean_ledgers.py` in `_rewrite_working/`.
- `_PHASE2_PLAN.md` (design, reconciled), this ledger, `_PHASE2_diff_abstract.md` (pre-go draft).
- 16 originals FROZEN (verified byte-identical after cloning).
