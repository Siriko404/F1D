# claude-mem PRE-UPGRADE CHECKLIST (M4 / C6)

Do ALL of these BEFORE running any claude-mem version upgrade. The plugin
ships ~12 releases / 7 days; an upgrade can silently re-introduce
capture=0 (#2485) or chroma drift (#2487).

1. [ ] On-demand backup: `python scripts/claude_mem_integration/backup_claude_mem.py`
2. [ ] Read the target release notes + open issues at
       github.com/thedotmack/claude-mem — confirm **#2485** (observations
       stay at 0) and **#2487** (chroma ~48% drift) are NOT open/regressed
       in the target version.
3. [ ] Diff current `~/.claude-mem/settings.json` vs the pinned
       `claude_mem_settings_snapshot.json`; investigate any difference.
4. [ ] Upgrade.
5. [ ] Re-run the P0→P1 gate (plan Task 8) in full before trusting it.
6. [ ] Run the canary: `python scripts/claude_mem_integration/canary.py plant`,
       then in a later session call the mem-search MCP tool and
       `... canary.py verify <cid> --recalled "<mcp text>"` — must PASS
       before relying on memory.
7. [ ] If ANY check fails: execute the two-flip rollback
       (`~/.claude/settings.json` `autoMemoryEnabled:true` +
       `autoDreamEnabled:true`) and pin back to the previous claude-mem
       version.
