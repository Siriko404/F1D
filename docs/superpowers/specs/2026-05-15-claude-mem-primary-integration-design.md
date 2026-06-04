# Design Spec — claude-mem as Primary Memory (phased, reversible)

- **Date:** 2026-05-15
- **Status:** Approved design (brainstorming). Implementation NOT started — gated behind `writing-plans`.
- **Owner:** Sina (navigator) / Claude (implementation)
- **Topic:** Make claude-mem the primary memory system on this machine and stop using Claude Code's native auto-memory, safely and reversibly.
- **Approach:** A — phased harden → verify → cutover (user-selected; advisor-endorsed).
- **Environment:** Windows 11; claude-mem v13.2.0 (`thedotmack@claude-mem`); Claude Code native auto-memory currently ON.

---

## 1. Problem & Goal

**Goal.** claude-mem becomes the single primary memory; Claude is directed to use it; Claude Code's native auto-memory is disabled — without introducing silent memory loss, and fully reversible.

**Why not a naive cutover.** The triggering hypothesis ("native memory is the hallucination source") was tested and **refuted**: the `+0.0539` error originated upstream (garbled extraction → unverified hardcoded constant) and was propagated **equally** by native auto-memory *and* claude-mem (claude-mem obs #792 stored it Haiku-summarized into 3 forms). A memory swap does not reduce numeric hallucination. The legitimate goal here is **single-source-of-truth / less prose-drift**, not hallucination removal — and it must not trade a transparent, editable, git-tracked store for silent data loss.

## 2. Evidence Basis (why phased + gated)

GitHub primary sources (github.com/thedotmack/claude-mem) + independent audit:

- **#2485 (OPEN, v13.2.0):** observer SDK replies non-XML → parser drops every batch → `observations`/`session_summaries` stay at 0. Capture can silently produce nothing.
- **#2487 (CLOSED 2026-05-15, AFTER installed v13.2.0 build of 2026-05-12):** chroma backfill watermark drifts ahead of writes → ~48% observations unreachable via semantic search while watermark claims caught up.
- **#2494 / #2495 / #2484 / #2482 (Windows):** chroma-mcp / mcp-search startup broken on Windows in v13.2.0.
- **#1251 (security audit, HIGH):** unauthenticated HTTP API on the worker port; path traversal in smart_unfold/outline.
- Release cadence ≈ 12 releases in 7 days (v12→v13 "Server Beta") — high regression risk on upgrade.

**Live install check (this machine, 2026-05-15):** observations=832 (+126/24h), F1D=674, queue `pending_messages`=0 (drained), worker pid 5888 :37777 up since 2026-05-14, chroma embeddings=8,636 ≫ 832 (NOT the #2487 under-index signature). **Conclusion: the catastrophic failure modes are real but LATENT — none firing here now.** Therefore sole-memory is feasible *only* behind a recurring health gate, because the next churn upgrade can silently activate them.

## 3. Architecture — Phases & States

```
NOW:   native auto-memory ON  +  claude-mem ON   (uncoordinated, both run)
                         │
 PHASE 0  harden (reversible, NO memory-source change)
                         │   security (M5) + durability (M6) + observability (M2/M3)
 PHASE 1  verify→gate    │   native = SAFETY NET (stays ON)  [M1]
          (runs until P1→P2 gate passes; ≥1 wk minimum, may extend)
                         │   claude-mem runs + per-session health gate (M2)
                         │   gate green N≥8 sessions + recall-fidelity PASS ──┐
 PHASE 2  cutover (gated) │ ◄───────────────────────────────────────────────┘
                         ▼   STRUCTURAL: autoMemoryEnabled:false
                         ▼              + autoDreamEnabled:false
END:   claude-mem PRIMARY (structural) + CLAUDE.md directive (normative)
       · native OFF but files retained (dormant, never deleted)
       · health gate permanent · rollback = two-flip revert
```

No destructive action at any phase. Native memory files (`~/.claude/projects/<id>/memory/`) are never deleted — only the native pathway is disabled.

## 4. Components & Mitigation Definitions

**Mitigation glossary (inlined — no shorthand):**

- **M1 — native-as-net:** native auto-memory stays ON through all of Phase 1; disabled only at Phase 2 after the gate passes.
- **M2 — capture-health gate:** a session-start check asserting (a) worker process alive, (b) `pending_messages` queue not backing up, (c) `observations` row count for the active project strictly increased since the previous check, (d) per-project chroma embedding count ≥ 0.5 × per-project SQLite obs count (the #2487 under-population detector; 0.5 = #2487's documented floor, issue numbers SQLite 703 → chroma 363 ≈ 0.52). **NOTE:** `chroma-sync-state.json`.observations is a GLOBAL-ID watermark and is deliberately **NOT** used here — comparing that watermark to a per-project rowcount was a false-positive bug found and fixed during execution (see plan Task 5 (d) and `memory/project_claude_mem_v1320_windows_risk_2026_05_15.md`). Any failure → the gate emits an **LLM-visible** status (see §6.1) and counts toward the §7 rollback trigger.
- **M3 — Chroma decision:** keep ChromaDB (healthy on this install: 8,636 embeddings, no drift) rather than forcing FTS5-only; M2(d) watches for drift. Revisit only if M2(d) trips.
- **M4 — version guard:** claude-mem is pinned; before ANY claude-mem upgrade, verify upstream that #2485 and #2487 are fixed in the target version, then re-run the Phase-0→1 gate before trusting it.
- **M5 — API lockdown:** worker binds 127.0.0.1 only; a Windows Firewall inbound block rule on the worker port (37777, confirmed from `worker.pid`) prevents network exposure of the unauthenticated API (#1251).
- **M6 — backup:** scheduled SQLite Online-Backup (`.backup`) of `~/.claude-mem/claude-mem.db` to `~/.claude-mem/backups/`, daily + on-demand before any upgrade; retain last 14; monthly test-restore.
- **M7 — numeric source-of-truth gate:** OUT of the memory system entirely. Hardcoded paper constants / extracted numbers must cite a clean-extraction line; neither memory store validates numbers. Tracked separately (see §9 cross-reference); listed here so the spec is self-contained.

**Artifacts to build:**

| # | Artifact | Purpose | Mitigation |
|---|----------|---------|-----------|
| C1 | Verify worker bind = 127.0.0.1; add Windows Firewall inbound-block rule for port 37777 | close unauth API | M5 |
| C2 | Scheduled `claude-mem.db` Online-Backup script (rotating 14, daily + pre-upgrade) | source-of-truth durability | M6 |
| C3 | Capture-health gate **SessionStart hook** implementing M2(a)-(d); on failure emits an LLM-visible status (§6.1) | detect silent failure | M2/M3 |
| C4 | Pin/record `~/.claude-mem/settings.json` `CLAUDE_MEM_*` (capture model + knobs touched) | reproducibility | M4 |
| C5 | `~/.claude/CLAUDE.md` normative directive: prefer claude-mem (mem-search skill + observation recall) as the memory of record | normative usage | (see §6) |
| C6 | Pre-upgrade checklist doc (verify #2485/#2487 fixed → re-run P0→P1 gate) | churn safety | M4 |

## 5. Data Flow (post-cutover)

```
capture: PostToolUse → SQLite queue → worker → Haiku (claude-haiku-4-5)
                                        → SQLite observations + Chroma     [claude-mem only]
recall : SessionStart "context" injection + mem-search skill
         + PreToolUse(Read) file-context
gate   : C3 (M2) runs at EVERY session start, BEFORE memory is trusted
native : pathway structurally disabled (Phase 2); files retained, two-flip revivable
numbers: M7 truth-gate sits OUTSIDE memory — neither store validates a value
```

## 6. Enforcement Model — Structural vs Normative (advisor fix #2)

The safety guarantee rests on the **structural** mechanism, never on the directive alone:

- **STRUCTURAL (load-bearing):** `~/.claude/settings.json` → `autoMemoryEnabled:false` **and** `autoDreamEnabled:false`. This removes the native auto-memory write/recall pathway as a matter of configuration, independent of model compliance.
- **NORMATIVE (supplementary, can drift):** the `~/.claude/CLAUDE.md` directive (C5) instructs Claude to use claude-mem. This shapes behaviour but is guidance a future model may deviate from. It is **not** the enforcement mechanism and the design must not depend on it for correctness.

"Hard-force" therefore = structural disable of the alternative + normative steering toward claude-mem + the M2 health gate. The directive is the weakest of the three and is treated as such.

**C5 conflict-safety (flag for writing-plans):** the C5 `~/.claude/CLAUDE.md` directive wording must be drafted and then verified **non-conflicting** with the existing mandatory frameworks already loaded there (karpathy-guidelines, user-profile-sina, scope-discipline, superpowers) BEFORE installation. The implementation plan owns this draft-then-verify step; the directive is not installed until verified clean.

## 6.1 Health-Gate Failure Channel (advisor blocker fix — load-bearing)

The M2/C3 gate is only a safety net if its failure is *seen by the party that can act on it*. A console-only "WARN" is insufficient: in Phase 2 the rollback (§11) is a **user** action, and the model independently must not keep quoting a degraded memory store.

Therefore C3 runs as a **SessionStart hook** and, on ANY M2 failure, emits its status as an **`additionalContext` / system-reminder injected into the session** (the same channel the existing SessionStart hooks already use). On a failure status the model MUST, in its first response that session:

1. Surface the degraded-memory alert **prominently at the top** of the response (not buried).
2. Treat claude-mem recall as **untrusted for that session** — it must not rely on injected observations/`mem-search` results for factual claims until the user clears the alert.
3. State the §11 two-flip rollback option to the user.

The alert persists each session start until M2 passes again or the user explicitly acknowledges/rolls back. Without this channel, Phase 2 has no operational safety net — this section is load-bearing, not advisory.

## 7. Error Handling / Rollback

- **Rollback triggers (ANY):** C3/M2 gate fails on 2 consecutive sessions · observations stop growing · queue stuck · chroma drift detected (M2d) · post-upgrade regression.
- **Rollback action — TWO flips (advisor fix #5):** in `~/.claude/settings.json` set `autoMemoryEnabled:true` **and** `autoDreamEnabled:true`. Native auto-memory resumes the next session. claude-mem is left running (non-destructive). No data is deleted at any phase; native memory files were retained throughout.
- **Containment:** Phase 1 keeps native ON, so any claude-mem failure during verification loses nothing. M6 backups make corruption recoverable.

## 8. Verification Gates

**"session" definition (advisor fix #3):** a session = a Claude Code context segment initiated by `startup`, `/clear`, or `/compact` (mirrors claude-mem's own SessionStart matcher `startup|clear|compact`). `/compact`-initiated segments **count**.

**P0 → P1 gate (all required):**
1. Firewall rule verified — worker port refuses an external connection; localhost still works.
2. M6 backup runs AND a test-restore of the copied `.db` opens with the same `observations` row count.
3. C3/M2 runs green on the current (healthy) install.

**P1 → P2 gate (all required):**
1. ≥ 8 sessions (per definition above) spanning ≥ 7 calendar days.
2. C3/M2 green on every one of those sessions (zero failures).
3. **Recall-fidelity check — ≥ 3 PASS across 3 distinct Phase-1 sessions, 0 FAIL (advisor fixes #1 + tightening — the decisive gate; canary mechanics specified in the implementation plan):** in session S, plant a canary observation containing a specific numeric claim and its source string. At the start of a later session, query it via the mem-search skill. **PASS** only if the recalled text reproduces the number **verbatim** (exact characters for digits/identifiers) AND attributes it to the correct source. **FAIL** on any numeric mismatch, omission, or mis-attribution. A single PASS can be a small-model coincidence (obs #792 proves capture can be 100% "successful" while the stored memory is wrong), so cutover requires **≥ 3 independent PASS in 3 different Phase-1 sessions with zero FAIL**. Capture-count growth (M2c) is necessary but **NOT sufficient**; this recall gate is what authorises Phase 2.

**Ongoing (Phase 2+):** C3/M2 every session start; monthly M6 test-restore; C6 pre-upgrade checklist before any claude-mem version change.

## 9. Scope & Non-Goals

**Out of scope (YAGNI):**
- Patching claude-mem's Windows/v13.2.0 upstream bugs (we detect + rollback, not fix the plugin).
- Migrating off ChromaDB to FTS5-only — only if M2(d) trips.
- Other projects' memory, or any memory data deletion.
- **context-mode plugin (advisor fix #4):** `~/.claude/settings.json` SessionStart hook `context-mode-cache-heal.mjs` is a context-window protection / cache-heal layer, **NOT a persistent memory store**. It is explicitly out of scope and is **not** part of "Claude's own memory system" being disabled. Untouched by this work.

**Cross-reference — RESOLVED 2026-05-16 (was: do not bury):** the parked thesis-critical anchor defect is fixed — `scripts/campello_rebuild/step7_did_cash.py` `PAPER_ANCHOR` corrected to `+0.231***` SE (0.059) N 17,170 in commit `e0854d7` and propagated across `outputs/campello_rebuild/REBUILD_CONCLUSION_2026-05-15.md` + memory (mechanical sweep 2026-05-16, Sina-authorized KEEP + complete). Prior `+0.0539` was an extraction corruption (verified `tmp/campello_v2/campello_paper_FULL.md` L3785/L3844 + user visual PDF confirmation). Remaining open item: the "attenuation / DO NOT chase" narrative framing is Sina's editorial call (AskUserQuestion pending) — not a code defect. Finding history durable in `memory/project_campello_anchor_error_2026_05_15.md` / `project_campello_anchor_correction_DISPUTED_2026_05_16.md`.

## 10. Open Parameters (deliberate, not placeholders)

- **Capture model:** currently `claude-haiku-4-5-20251001` (claude-mem default). Decision deferred to the implementation plan: keep Haiku (lower cost, current behaviour) vs upgrade `CLAUDE_MEM_MODEL` to Sonnet (less compression drift, higher cost). Not blocking the design; resolved in `writing-plans`.
- **N (P1→P2 session count):** fixed at ≥ 8 over ≥ 7 days (chosen: enough to span multiple work sessions/compactions without an arbitrarily long delay since the live install is already healthy).
- **Backup retention:** 14 rotating daily copies (chosen: ~2 weeks recovery window at modest disk for a ~5 MB db).

## 11. Rollback Runbook (exact)

1. Open `~/.claude/settings.json`.
2. Set `"autoMemoryEnabled": true` and `"autoDreamEnabled": true`.
3. Start a new session — native auto-memory resumes (it reads the retained `memory/` files).
4. Leave claude-mem running; no uninstall, no data deletion.
5. Record the trigger + timestamp in `memory/` for the post-mortem.

Reversibility cost: two JSON booleans. No migration, no data loss.

## Appendix — Source Evidence

- Mechanism (source-read): `memory/reference_claude_mem_mechanism_2026_05_15.md`.
- Risk verdict: `memory/project_claude_mem_v1320_windows_risk_2026_05_15.md`.
- GitHub: issues #2485, #2487, #2494, #2495, #2484, #2482, #1251; repo github.com/thedotmack/claude-mem.
- Native auto-memory toggle: `~/.claude/settings.json` `autoMemoryEnabled` / `autoDreamEnabled` (lines confirmed present, value `true`).
- Live diagnostic numbers: §2 (this doc), 2026-05-15.
