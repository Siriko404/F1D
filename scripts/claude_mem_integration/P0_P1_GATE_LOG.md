# P0 → P1 Gate Log (plan Task 8)

Date: 2026-05-15. Result: **PASS** — all 3 items (firewall completed by
Sina in an elevated terminal 2026-05-15, verified).

| # | Gate check | Result | Evidence |
|---|------------|--------|----------|
| 1 | Firewall refuses external; localhost OK | **PASS** | Sina ran `netsh advfirewall firewall add rule name="claude-mem-worker-block-inbound" dir=in action=block protocol=TCP localport=37777` elevated → "Ok." Verified: `netsh advfirewall firewall show rule` → Enabled=Yes, Dir=In, TCP, LocalPort 37777, Profiles Domain/Private/Public. `localhost:37777` connect rc=0 (loopback unaffected, as intended). Also worker is `127.0.0.1`-bound (snapshot) — firewall is defense-in-depth on top. |
| 2 | Backup test-restore | **PASS** | `~/.claude-mem/backups/cmint/claude-mem-20260515-231522.db` opens read-only with **849** observations. Execution-found data-safety bug fixed first (broad glob matched claude-mem's own `claude-mem-pre-*.db`; rotation could delete OUR backups) → owned subdir + `claude-mem-[0-9]*.db` pattern; regression test added; 3/3 backup tests pass. |
| 3 | Health gate green on healthy install | **PASS** | Fresh first-run smoke = `{"continue": true, "suppressOutput": true}`. 4/4 health_gate tests pass. Execution-found M2(d) false-positive fixed first (compared global-id watermark to per-project rowcount; now per-project chroma-vs-SQLite count, R=0.5 #2487 floor); regression test added; real-install smoke `drift=pass`. |

## Verdict

**P0 → P1 = PASS.** All 3 items pass. Two execution-found bugs (M2(d)
drift false-positive; backup foreign-file rotation) were fixed +
regression-tested + plan/spec synced before this verdict. Firewall
completed by Sina (elevated) and verified.

## STATUS

- Phase 0: **COMPLETE.**
- Phase 1 (≥1-week verification window) is now **eligible to start**:
  native auto-memory stays ON as the safety net; each session-start the
  health gate must be green; ≥3 distinct recall-fidelity canaries must
  PASS (0 FAIL) across ≥8 sessions / ≥7 days. This window is **passive**
  (accrues over normal use) — no active build work.
- Phase 2 (cutover — disabling native memory) remains **ratification-
  gated** (plan Task 10): explicit Sina authorization required, only
  after the Phase-1 gate passes. NOT done.

## Phase-0 commits
`6bb0068` E1 scaffold/snapshot/checklist · `4589d23` E2 backup ·
`f810a92` E3 health-gate · `c08a329` E4 canary · `0e7ca24` M2(d) fix +
plan/spec sync · (this) backup foreign-isolation fix + plan sync + gate log.
