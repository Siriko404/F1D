# _rewrite_working/ — Phase-2 rewrite targets (compaction-safe)

These 16 files are **CLONES** of the subsection paragraph ledgers, made 2026-06-24 by
`scratchpad/clone_clean_ledgers.py`.

- **Every `final_prose` was blanked** (79 fields), `prose_status` flagged "CLEARED -- Phase-2 rewrite pending".
- **Spine kept intact**: `proposition_chain`, `_phaseC_audit.number_audit`, `guardrails`, `intent`, `allocation_coverage`.
- The **ORIGINALS** (one directory up, `docs/Thesis/rewrite/section*_paragraph_ledger.json`) are **FROZEN** — the source-of-truth spine + rollback. They were verified byte-identical after cloning. Do NOT edit them during rewriting.

## How the rewrite uses these
1. Pull the spine from the clone (props / number_audit / guardrails) + the OLD prose from the original.
2. Rewrite plain (simple sentences, **jargon kept** — see `_PHASE2_PLAN.md` decision 7).
3. Hand-gate (numbers + protected phrases survive verbatim) — recorded in `style_profiles/_PHASE2_diff_<id>.md`.
4. Advisor closed-checklist, then Sina ratifies.
5. On ratify: write the new prose into THIS clone's `final_prose` + commit.

The thesis prose is updated from these ratified clones only at the very end.
