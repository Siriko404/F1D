# P0 → P1 Gate Log (plan Task 8)

Date: 2026-05-15. Honest result: **CONDITIONAL — NOT a full PASS** (1 of 3
items blocked on a manual elevated step).

| # | Gate check | Result | Evidence |
|---|------------|--------|----------|
| 1 | Firewall refuses external; localhost OK | **BLOCKED (manual)** | `netsh advfirewall firewall add rule ...` → "The requested operation requires elevation (Run as administrator)". NOT applied. Mitigant: `CLAUDE_MEM_WORKER_HOST=127.0.0.1` (snapshot) → worker is loopback-bound, not network-exposed by default. `localhost:37777` connect rc=0 (worker reachable locally, as intended). |
| 2 | Backup test-restore | **PASS** | `~/.claude-mem/backups/cmint/claude-mem-20260515-231522.db` opens read-only with **849** observations. Execution-found data-safety bug fixed first (broad glob matched claude-mem's own `claude-mem-pre-*.db`; rotation could delete OUR backups) → owned subdir + `claude-mem-[0-9]*.db` pattern; regression test added; 3/3 backup tests pass. |
| 3 | Health gate green on healthy install | **PASS** | Fresh first-run smoke = `{"continue": true, "suppressOutput": true}`. 4/4 health_gate tests pass. Execution-found M2(d) false-positive fixed first (compared global-id watermark to per-project rowcount; now per-project chroma-vs-SQLite count, R=0.5 #2487 floor); regression test added; real-install smoke `drift=pass`. |

## Verdict

**P0 → P1 = CONDITIONAL.** Items 2 and 3 PASS (after two execution-found
bugs were fixed + regression-tested). Item 1 (firewall) is **blocked on a
manual elevated command only Sina can run**:

```
netsh advfirewall firewall add rule name="claude-mem-worker-block-inbound" dir=in action=block protocol=TCP localport=37777
```
(run in an **Administrator** terminal; verify with
`python -c "import socket;s=socket.socket();s.settimeout(2);print(s.connect_ex(('127.0.0.1',37777)))"` → still `0` = localhost unaffected).

P0→P1 becomes a full PASS only after that command succeeds. Until then,
defense-in-depth is incomplete but the worker is loopback-bound so not
network-exposed.

## HARD STOP

- Phase 1 (the ≥1-week verification window) does **not** start until P0→P1
  is a full PASS (firewall done).
- Phase 2 (cutover — disabling native memory) is **separately
  ratification-gated** (plan Task 10) and requires explicit Sina
  authorization regardless. NOT done.

## Phase-0 commits
`6bb0068` E1 scaffold/snapshot/checklist · `4589d23` E2 backup ·
`f810a92` E3 health-gate · `c08a329` E4 canary · `0e7ca24` M2(d) fix +
plan/spec sync · (this) backup foreign-isolation fix + plan sync + gate log.
