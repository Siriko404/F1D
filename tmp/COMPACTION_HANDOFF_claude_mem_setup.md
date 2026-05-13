# Compaction Handoff — claude-mem Setup + learn-codebase Front-Load

**Date**: 2026-05-12
**Master HEAD**: `56caf2c` (unchanged this session — setup work, no code commits)
**Session work**: Plugin setup (claude-hud + context-mode + claude-mem) + learn-codebase pass session 1/N

---

## Read-FIRST after /compact

1. **This file** (canonical state of plugin setup + learn-codebase progress)
2. `tmp/learn_codebase_progress.txt` (which files have been Read by claude-mem)
3. `tmp/f1d_source_inventory.txt` (full 449-line file inventory, sorted)

After those 3, resume per "Resume protocol" section below.

---

## Plugin install state (FINAL — do NOT re-install)

Three plugins installed at user scope (global), enabled in `~/.claude/settings.json`:

| Plugin | Version | Marketplace | Purpose |
|---|---|---|---|
| `claude-hud@claude-hud` | 0.1.0 | jarrodwatts/claude-hud | Statusline HUD (3 lines: info + tools + agents) |
| `context-mode@context-mode` | 1.0.124 | mksglu/claude-context-mode | Sandbox + FTS5 KB (token compression) |
| `claude-mem@thedotmack` | 13.2.0 | thedotmack/claude-mem | Cross-session semantic memory |

**Skipped**: `drona23/claude-token-efficient` — NOT a CC plugin (CLAUDE.md template); redundant with caveman + karpathy + sina-profile already enforcing same rules.

---

## claude-hud config (TUNED)

`~/.claude/plugins/claude-hud/config.json`:
- `lineLayout: "compact"` — single info line (vs 3 expanded)
- `usageCompact: true` — `5h: 7% (4h 19m)` short format
- `usageBarEnabled: false` — text, not visual bar
- `gitStatus.showDirty: true` — `git:(master*)`
- **All display.show* keys: TRUE** EXCEPT `showTodos: false` (disabled due to upstream bug — see below)

### claude-hud BUG (showTodos disabled)

**Source**: `~/.claude/plugins/cache/claude-hud/claude-hud/0.1.0/dist/transcript.js:267-318`

**Symptom**: HUD shows `▸ X (101/239)` where 239 is implausibly large for current session.

**Root cause**: parser aggregates `TodoWrite` AND `TaskCreate` (Task-tool subagent spawns) into one `latestTodos` array. `TodoWrite` replaces list (correct CC semantics) but `TaskCreate` appends. Task-tool subagent invocations accumulate across the transcript without ever being cleared by a TodoWrite replace.

**Mitigation**: `display.showTodos: false`. Hides line entirely.

**Upstream fix needed**: TodoWrite handler should also clear TaskCreate-added items, OR TaskCreate items should live in a separate array from TodoWrite-managed todos.

---

## claude-mem config (STRICT-MAX CAPACITY, 2026-05-12 PM)

`~/.claude-mem/settings.json` — strict-max tuning post-audit:

| Key | Default | Set to | Why |
|---|---|---|---|
| `CLAUDE_MEM_SEMANTIC_INJECT` | "false" | "true" | Inject relevance-ranked |
| `CLAUDE_MEM_SEMANTIC_INJECT_LIMIT` | "5" | **"15"** | Strict-max ↑ from 10 |
| `CLAUDE_MEM_CONTEXT_SESSION_COUNT` | "10" | **"30"** | Strict-max ↑ from 20 |
| `CLAUDE_MEM_CONTEXT_FULL_COUNT` | "0" | **"10"** | Strict-max ↑ from 5 |
| `CLAUDE_MEM_CONTEXT_OBSERVATIONS` | "50" | **"100"** | Strict-max ↑ |
| `CLAUDE_MEM_CONTEXT_SHOW_LAST_MESSAGE` | "false" | "true" | Recall hint |
| `CLAUDE_MEM_SKIP_TOOLS` | (skips 5) | **""** | Strict-max = capture EVERY tool |
| `CLAUDE_MEM_TIER_SUMMARY_MODEL` | "" (→haiku) | **"claude-sonnet-4-6"** | Stronger model for Stop-hook summary |
| `CLAUDE_MEM_CHROMA_ENABLED` | "true" | **"false"** | Disabled — Windows stdio bug (see below) |
| `CLAUDE_MEM_CHROMA_MODE` | "local" | **"disabled"** | Match disabled state |

Unchanged + already-good:
- `CLAUDE_MEM_PROVIDER: "claude"` (subscription auth — no API key)
- `CLAUDE_MEM_MODEL: "claude-haiku-4-5-20251001"` (SIMPLE tier compression)
- `CLAUDE_MEM_TIER_SIMPLE_MODEL: "haiku"` (fast bulk obs)
- `CLAUDE_MEM_TIER_ROUTING_ENABLED: "true"` (haiku simple + sonnet summary)
- Worker on port 37777, PID written to `worker.pid`
- Data dir: `~/.claude-mem/` (SQLite + WAL active)

## Environment variables persisted

Set via PowerShell `[Environment]::SetEnvironmentVariable(..., "User")`:
- **`UV_LINK_MODE=copy`** — required because Sina's filesystem is OneDrive-synced; uvx hardlink mode fails with error 396 ("incompatible hardlinks"). Without this, any uvx invocation by the worker subprocess crashes during dep install.

## Chroma vector DB: DISABLED (known Windows bug)

**Bug**: worker's chroma-mcp stdio handshake times out in ~30ms while chroma-mcp subprocess needs ~2-5s to spawn Python + import onnxruntime + initialize FastMCP. Worker logs `MCP error -32000: Connection closed` repeatedly.

**Reproduce**:
```
[CHROMA_MCP] Connecting to chroma-mcp via MCP stdio {command=cmd.exe /c uvx ...}
[CHROMA_MCP] Connection failed in 27ms, killing subprocess tree
[CHROMA_MCP] Connection attempt failed MCP error -32000: Connection closed
```

**Tried (all failed)**:
- Pre-warmed uvx cache (Python + chroma-mcp + onnxruntime + protobuf) → subprocess starts cleanly when invoked manually, but worker still times out the MCP init handshake before chroma-mcp imports finish.
- CHROMA_MODE=http with separate `chroma run --host 127.0.0.1 --port 8000` server → worker ignored the setting, still spawned stdio persistent subprocess.
- CHROMA_MODE=external → same as http; ignored.

**Workaround**: CHROMA_ENABLED=false. Falls back to FTS5 keyword search (SQLite full-text). Capture-and-inject still works; only semantic relevance ranking is lost.

**Upstream fix needed**: worker needs longer MCP init timeout for stdio chroma-mcp on Windows, OR CHROMA_MODE=http should actually switch the launcher to talk HTTP to a separate chroma server.

## Verification results (post-strict-max restart 2026-05-12 PM)

- Worker live: HTTP 200 on `http://127.0.0.1:37777/health`
- Observation count this session: **15 → 36+** (after SKIP_TOOLS="" + restart)
- DB WAL: 4.2 MB (active writes confirmed)
- FTS5 keyword search: working (verified via `mcp__plugin_claude-mem_mcp-search__search`)
- Session-level summary rollups: present (#S1–S7)
- Per-Read observations: now capturing post-restart (was DROPPED during Session 2 due to haiku non-XML response bug — see notes)

### claude-mem hooks (verified firing)

`~/.claude/plugins/cache/thedotmack/claude-mem/13.2.0/hooks/hooks.json`:
- `Setup` — version check
- `SessionStart` (matcher: startup|clear|compact) — start worker + inject context
- `UserPromptSubmit` — session-init
- `PreToolUse` (matcher: Read) — file-context capture
- **`PostToolUse` (matcher: *)** — observation recording per tool call
- `Stop` — summarize session

→ EVERY Read fires PostToolUse hook → observation queued for compression. Observations persist in SQLite + chroma even after my context resets via /compact.

---

## learn-codebase pass status — Sessions 1+2 COMPLETE

**Inventory**: 449 source files (165k LOC) across `src/`, `tests/`, `scripts/`, `config/`.

**Cumulative progress**: **58/449 files read (13%)**

See `tmp/learn_codebase_progress.txt` for exact file list. Coverage:
- configs (5/5) ✓
- scripts/ root (4/4) ✓
- scripts/adhoc/ (29/29) ✓ COMPLETE
- scripts/brexit/ (9/9) ✓ COMPLETE
- src/f1d/__init__.py (1/1) ✓
- src/f1d/sample/ (7/7) ✓
- src/f1d/text/ (3/3) ✓

**scripts/ tree FULLY COMPLETE.**

**Session 2 high-value reads (Brexit Phase 1 area, plan tender-popping-origami.md)**:
- parse_10k_keywords.py — full ETL (~350 LOC), CRITICAL-1 split-regex fix, CCM time-varying mapping, MINOR-5 dedup
- build_beta_uk.py / build_treatment_10k.py / build_macro_controls.py / build_consensus_eps.py / build_fic100.py / build_brexit_controls.py / build_psm.py — CLI wrappers calling into src/f1d/shared/variables/brexit_*

**Remaining**: 391 files
- src/f1d/econometric/ (~95 incl _archived) — NEXT (start with run_h1_5_brexit_did.py + run_h1_5_trump_did.py + panel_ols.py)
- src/f1d/shared/ utilities (~50)
- src/f1d/shared/variables/ (~85 builders) — brexit_* builders, boasiako_*, chen_*, etc.
- src/f1d/variables/ panel builders (~25)
- tests/ (~80 files)

### Why multi-session

- 165k LOC × ~3.5 tokens/line (cat -n format) = ~580k tokens raw content
- Plus reasoning + tool overhead = ~700k+ tokens minimum
- Exceeds 1M Opus context if done single-session
- Sina's protocol: read in batches → /compact between → claude-mem persists observations
- Estimated total: ~10 sessions to cover full 449 files

---

## Resume protocol post-/compact

```
1. Read this file (tmp/COMPACTION_HANDOFF_claude_mem_setup.md) FIRST
2. Read tmp/learn_codebase_progress.txt (find last completed line)
3. Read tmp/f1d_source_inventory.txt (find next file in order)
4. Begin batch reads in parallel (10 files per assistant message)
5. After each batch: Edit tmp/learn_codebase_progress.txt to append done files
6. When context approaches ~60% used: stop + signal user to /compact
7. Repeat ~9 more sessions until inventory exhausted
```

### Next file (verified)

After Session 1 last file (`scripts/adhoc/panel_filter_ceo_deaths_a2.py`), next inventory line is:
- `scripts/adhoc/phase_e_precheck.py`

### Batch sizing guidance

- 10 files per parallel Read call = ~30k-50k tokens per batch
- 4-5 batches per session = ~200k tokens consumed
- Stop at ~60% context to leave room for compaction prep + closing handoff
- Each Read fires claude-mem PostToolUse → observation persisted to ~/.claude-mem/

### Verifying claude-mem captured observations

Optional sanity check on resume:
```
mcp__plugin_claude-mem_mcp-search__observation_search(query: "boasiako_disclosure_law_treatment")
```
Should return observation(s) referencing the file content read in earlier sessions.

---

## Files this session created/modified

| Path | Action | Purpose |
|---|---|---|
| `~/.claude/settings.json` | edited | Added statusLine + 3 enabledPlugins + extraKnownMarketplaces |
| `~/.claude/plugins/claude-hud/config.json` | created | HUD layout + features |
| `~/.claude-mem/settings.json` | edited (5 keys) | Max capability settings |
| `tmp/f1d_source_inventory.txt` | created | 449-file source inventory |
| `tmp/learn_codebase_progress.txt` | created/updated | 40/449 read tracker |
| `tmp/COMPACTION_HANDOFF_claude_mem_setup.md` | created (this file) | Compaction handoff |

No source-code commits this session. Master HEAD `56caf2c` unchanged.

---

## After last learn-codebase session

When inventory exhausted (~9 more sessions):
1. Delete `tmp/learn_codebase_progress.txt` + `tmp/f1d_source_inventory.txt` (transient state)
2. Verify claude-mem corpus via `mcp__plugin_claude-mem_mcp-search__list_corpora`
3. Test semantic recall: ask claude-mem about an F1D module Sina hasn't touched recently
4. Document final corpus size + observation count in this handoff (or new memory entry)
5. Phase 2 work (§III.E.4 prose + main.pdf recompile) can begin with full codebase semantic context

Safe to /compact.
