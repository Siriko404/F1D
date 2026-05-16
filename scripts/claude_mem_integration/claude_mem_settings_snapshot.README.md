# claude-mem settings snapshot (C4 / M4)

- Captured: 2026-05-15
- `CLAUDE_MEM_MODEL`: `claude-haiku-4-5-20251001` (DEFAULT — **KEPT** for Phase 1).
  Decision (plan §Decisions): do NOT change the capture model during the
  verification window; a Sonnet upgrade is out of scope (post-cutover option
  only). Changing it mid-verification would confound the recall-fidelity gate.
- `CLAUDE_MEM_WORKER_HOST`: `127.0.0.1` (already localhost-bound — M5's
  firewall rule is defense-in-depth on top of this).
- `CLAUDE_MEM_WORKER_PORT`: `37777`.
- `CLAUDE_MEM_CONTEXT_OBSERVATIONS`: `100`.
- `CLAUDE_MEM_PROVIDER`: `claude`.

`claude_mem_settings_snapshot.json` is the pinned baseline. Any drift from it
before a claude-mem upgrade is a change to investigate — see
`PRE_UPGRADE_CHECKLIST.md` (M4 / C6).
