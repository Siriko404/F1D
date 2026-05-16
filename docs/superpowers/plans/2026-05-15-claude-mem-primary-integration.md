# claude-mem Primary-Memory Integration — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make claude-mem the primary memory and disable Claude Code native auto-memory, safely and reversibly, per the approved spec `docs/superpowers/specs/2026-05-15-claude-mem-primary-integration-design.md`.

**Architecture:** Phase 0 hardens (firewall, backup, health-gate hook) with NO memory-source change; Phase 1 runs a verification window with native auto-memory kept ON as a safety net and a recall-fidelity canary gate; Phase 2 flips two native settings off + installs a normative CLAUDE.md directive only after the gate passes. Every step is reversible by two settings booleans.

**Tech Stack:** Python 3 (stdlib `sqlite3`, `socket`, `json`), Windows (`netsh advfirewall`, Task Scheduler `schtasks`), Claude Code SessionStart hooks (`~/.claude/settings.json`), claude-mem v13.2.0.

**Decisions locked here (spec §10 deferred to this plan):**
- **Capture model:** keep `claude-haiku-4-5-20251001` (claude-mem default) for Phase 1. Rationale: Phase 1 must verify the *as-is* default behaviour; changing the model mid-verification confounds the gate. A Sonnet upgrade is an explicit out-of-scope post-cutover option (not in this plan — YAGNI).
- **Script home:** `scripts/claude_mem_integration/` in the F1D repo (version-controlled beside the spec). Runtime data stays under `~/.claude-mem/`.
- **Canary mechanics (spec §8 deferred):** fully specified in Task 9.

**Execution gating (read before starting):** Phase 0 + Phase 1 are low-risk/reversible. **Phase 2 (Task 10) disables native memory and MUST NOT run without explicit Sina ratification at that point** — it is the only hard-to-reverse-direction step. The plan stops at the Phase-1→2 gate for a go/no-go.

---

## File Structure

| File | Responsibility |
|------|----------------|
| `scripts/claude_mem_integration/backup_claude_mem.py` | C2 — SQLite Online-Backup of `claude-mem.db` to rotating dir |
| `scripts/claude_mem_integration/health_gate.py` | C3 — SessionStart hook: M2(a–d) checks; emits LLM-visible status on failure (§6.1) |
| `scripts/claude_mem_integration/canary.py` | Task 9 — plant + verify recall-fidelity canary; append PASS/FAIL log |
| `scripts/claude_mem_integration/recall_canary_log.md` | Task 9 — append-only canary result ledger |
| `scripts/claude_mem_integration/PRE_UPGRADE_CHECKLIST.md` | C6 — pre-upgrade vetting checklist |
| `scripts/claude_mem_integration/claude_mem_directive.md` | C5 — drafted CLAUDE.md directive text (installed only in Phase 2) |
| `scripts/claude_mem_integration/tests/test_health_gate.py` | tests for health_gate |
| `scripts/claude_mem_integration/tests/test_backup.py` | tests for backup |
| `~/.claude/settings.json` | register C3 SessionStart hook (Phase 0); flip `autoMemoryEnabled`/`autoDreamEnabled` (Phase 2) |

---

## Task 1: Scaffolding

**Files:**
- Create: `scripts/claude_mem_integration/__init__.py`
- Create: `scripts/claude_mem_integration/tests/__init__.py`

- [ ] **Step 1: Create the package dirs + empty init files**

```bash
cd "C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D"
mkdir -p scripts/claude_mem_integration/tests
: > scripts/claude_mem_integration/__init__.py
: > scripts/claude_mem_integration/tests/__init__.py
```

- [ ] **Step 2: Verify**

Run: `ls scripts/claude_mem_integration scripts/claude_mem_integration/tests`
Expected: both dirs exist with `__init__.py`.

- [ ] **Step 3: Commit**

```bash
git add scripts/claude_mem_integration/__init__.py scripts/claude_mem_integration/tests/__init__.py
git commit -m "chore(claude-mem): scaffold integration scripts package"
```

---

## Task 2: Backup script (C2 / M6)

**Files:**
- Create: `scripts/claude_mem_integration/backup_claude_mem.py`
- Test: `scripts/claude_mem_integration/tests/test_backup.py`

- [ ] **Step 1: Write the failing test**

```python
# scripts/claude_mem_integration/tests/test_backup.py
import sqlite3, os
from pathlib import Path
import importlib.util

SPEC = Path(__file__).resolve().parents[1] / "backup_claude_mem.py"
spec = importlib.util.spec_from_file_location("bk", SPEC)
bk = importlib.util.module_from_spec(spec); spec.loader.exec_module(bk)

def test_backup_creates_restorable_copy(tmp_path):
    src = tmp_path / "claude-mem.db"
    con = sqlite3.connect(src)
    con.execute("CREATE TABLE observations(id INTEGER PRIMARY KEY)")
    con.executemany("INSERT INTO observations(id) VALUES (?)", [(i,) for i in range(5)])
    con.commit(); con.close()
    outdir = tmp_path / "backups"
    dest = bk.backup(str(src), str(outdir), retain=14)
    assert os.path.exists(dest)
    c = sqlite3.connect(dest)
    assert c.execute("SELECT count(*) FROM observations").fetchone()[0] == 5
    c.close()

def test_retention_prunes(tmp_path):
    src = tmp_path / "claude-mem.db"
    sqlite3.connect(src).close()
    outdir = tmp_path / "b"
    for _ in range(20):
        bk.backup(str(src), str(outdir), retain=14, _force_unique=True)
    assert len(list(Path(outdir).glob("claude-mem-*.db"))) == 14

def test_foreign_claude_mem_pre_backup_is_never_touched(tmp_path):
    # Regression: claude-mem's own `claude-mem-pre-<ver>-<ISO>.db` dumps
    # must NEVER be pruned or selected (execution-found data-safety bug).
    src = tmp_path / "claude-mem.db"
    sqlite3.connect(src).close()
    outdir = tmp_path / "b"; outdir.mkdir()
    foreign = outdir / "claude-mem-pre-12.4.3-2026-05-12T21-53-47-190Z.db"
    foreign.write_bytes(b"")
    for _ in range(20):
        bk.backup(str(src), str(outdir), retain=3, _force_unique=True)
    assert foreign.exists()
    assert len(list(outdir.glob(bk.OURS_GLOB))) == 3
    assert foreign not in list(outdir.glob(bk.OURS_GLOB))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/claude_mem_integration/tests/test_backup.py -v`
Expected: FAIL (`backup_claude_mem.py` does not exist / no `backup`).

- [ ] **Step 3: Write the implementation**

```python
# scripts/claude_mem_integration/backup_claude_mem.py
"""C2/M6: SQLite Online-Backup of claude-mem.db to a rotating dir.

Online Backup API copies a CONSISTENT snapshot even while the worker
holds the WAL open (a plain file copy of a WAL db can be torn).

Isolation (execution-found bug fix 2026-05-15): our backups live in a
DEDICATED OWNED subdir (`backups/cmint`), and rotation matches only the
strict pattern `claude-mem-[0-9]*.db`. claude-mem itself writes
pre-upgrade dumps `claude-mem-pre-<ver>-<ISO>.db` into `backups/`; the
broad glob matched THOSE too and lexicographic sort placed `...-pre-...`
after `...-2026...`, so prior rotation could delete OUR backups while
keeping stale 0-row foreign ones. Owned subdir + digit-anchored pattern
prevent ever touching a non-ours file.
"""
from __future__ import annotations
import sqlite3, sys, time, os
from pathlib import Path

DEFAULT_SRC = Path.home() / ".claude-mem" / "claude-mem.db"
DEFAULT_OUT = Path.home() / ".claude-mem" / "backups" / "cmint"
OURS_GLOB = "claude-mem-[0-9]*.db"   # excludes claude-mem-pre-*.db

def backup(src: str, outdir: str, retain: int = 14,
           _force_unique: bool = False) -> str:
    src = Path(src); out = Path(outdir); out.mkdir(parents=True, exist_ok=True)
    ts = time.strftime("%Y%m%d-%H%M%S")
    if _force_unique:
        ts += f"-{time.perf_counter_ns()}"
    dest = out / f"claude-mem-{ts}.db"
    s = sqlite3.connect(f"file:{src}?mode=ro", uri=True)
    d = sqlite3.connect(dest)
    with d:
        s.backup(d)
    s.close(); d.close()
    backups = sorted(out.glob(OURS_GLOB))   # ours only; never foreign
    for old in backups[:-retain]:
        old.unlink()
    return str(dest)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_SRC)
    out = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_OUT)
    if not Path(src).exists():
        print(f"SKIP: {src} not found"); sys.exit(0)
    print("backed up ->", backup(src, out))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest scripts/claude_mem_integration/tests/test_backup.py -v`
Expected: 3 passed.

- [ ] **Step 5: Manual smoke + first real backup**

Run: `python scripts/claude_mem_integration/backup_claude_mem.py`
Expected: `backed up -> C:\Users\sinas\.claude-mem\backups\claude-mem-<ts>.db`

- [ ] **Step 6: Commit**

```bash
git add scripts/claude_mem_integration/backup_claude_mem.py scripts/claude_mem_integration/tests/test_backup.py
git commit -m "feat(claude-mem): C2 online-backup script with rotation (M6)"
```

---

## Task 3: Schedule the backup (C2 / M6)

**Files:** none (Windows Task Scheduler).

- [ ] **Step 1: Register a daily scheduled task**

```bash
schtasks /Create /TN "claude-mem-backup" /SC DAILY /ST 03:00 /F ^
  /TR "python \"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\scripts\claude_mem_integration\backup_claude_mem.py\""
```

- [ ] **Step 2: Verify the task exists and run it once now**

Run: `schtasks /Run /TN "claude-mem-backup"` then `schtasks /Query /TN "claude-mem-backup" /V /FO LIST`
Expected: task listed, `Last Result` `0`, a new file in `~/.claude-mem/backups/`.

- [ ] **Step 3: Document (no code commit; record in checklist later in Task 8)**

No commit (system-level task). Recorded in the Task-8 P0→P1 verification log.

---

## Task 4: API lockdown (C1 / M5)

**Files:** none (Windows Firewall + a verification probe).

- [ ] **Step 1: Confirm worker bind address**

Run: `python -c "import json,pathlib;d=json.loads((pathlib.Path.home()/'.claude-mem'/'worker.pid').read_text());print(d)"`
Expected: prints `{'pid':..., 'port': 37777}` (note the port; spec assumes 37777 — use the actual value printed).

- [ ] **Step 2: Add an inbound firewall block rule for the worker port**

```bash
netsh advfirewall firewall add rule name="claude-mem-worker-block-inbound" dir=in action=block protocol=TCP localport=37777
```
(Replace `37777` with the port from Step 1 if different.)

- [ ] **Step 3: Verify localhost still works, external bind is not exposed**

Run:
```bash
python -c "import socket;s=socket.socket();s.settimeout(2);print('localhost connect:', s.connect_ex(('127.0.0.1',37777)))"
```
Expected: `localhost connect: 0` (worker reachable locally). The firewall rule blocks inbound from the network; localhost loopback is unaffected — this is the intended state (local-only access).

- [ ] **Step 4: Record** (captured in Task 8 log; no repo commit — system rule).

---

## Task 5: Health-gate SessionStart hook (C3 / M2 / §6.1)

**Files:**
- Create: `scripts/claude_mem_integration/health_gate.py`
- Test: `scripts/claude_mem_integration/tests/test_health_gate.py`
- Modify: `~/.claude/settings.json` (register hook)

- [ ] **Step 1: Write the failing test**

```python
# scripts/claude_mem_integration/tests/test_health_gate.py
import json, sqlite3, importlib.util
from pathlib import Path

MOD = Path(__file__).resolve().parents[1] / "health_gate.py"
spec = importlib.util.spec_from_file_location("hg", MOD)
hg = importlib.util.module_from_spec(spec); spec.loader.exec_module(hg)

def _mkdb(p):
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE observations(id INTEGER PRIMARY KEY, project TEXT, created_at_epoch INTEGER)")
    c.execute("CREATE TABLE pending_messages(id INTEGER PRIMARY KEY, status TEXT, created_at_epoch INTEGER)")
    c.commit(); c.close()

def test_growth_pass(tmp_path):
    db = tmp_path/"m.db"; _mkdb(db)
    c=sqlite3.connect(db); c.executemany("INSERT INTO observations(project,created_at_epoch) VALUES('F1D',1)",[]); c.commit()
    c.execute("INSERT INTO observations(project,created_at_epoch) VALUES('F1D',1)"); c.commit(); c.close()
    st = tmp_path/"state.json"
    r1 = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert r1["checks"]["growth"] in ("pass","first-run")
    # second run with no new rows -> growth fail
    r2 = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert r2["checks"]["growth"] == "fail"

def test_emits_additionalcontext_json_on_fail(tmp_path, capsys):
    db = tmp_path/"m.db"; _mkdb(db)
    st = tmp_path/"s.json"
    hg.main_for_test(str(db), "F1D", str(st), port=0, worker_check=False)
    hg.main_for_test(str(db), "F1D", str(st), port=0, worker_check=False)  # 2nd = no growth
    out = capsys.readouterr().out
    payload = json.loads(out.strip().splitlines()[-1])
    assert payload["continue"] is True
    assert "DEGRADED" in payload["hookSpecificOutput"]["additionalContext"]

def test_capture_pipeline_2485_and_failclosed(tmp_path):
    db = tmp_path/"m.db"; _mkdb(db)
    st = tmp_path/"s.json"
    r1 = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert r1["checks"]["capture_pipeline"] == "first-run"
    # no global growth between runs -> #2485 fail + fail-closed ok=False
    r2 = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert r2["checks"]["capture_pipeline"] == "fail"
    assert r2["ok"] is False
    # an observation anywhere -> pipeline pass next check
    c = sqlite3.connect(db)
    c.execute("INSERT INTO observations(project,created_at_epoch) VALUES('X',1)")
    c.commit(); c.close()
    r3 = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert r3["checks"]["capture_pipeline"] == "pass"

def _mk_chroma(p, f1d_rows):
    p.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(p)
    c.execute("CREATE TABLE embedding_metadata(id INTEGER, key TEXT, string_value TEXT)")
    c.executemany(
        "INSERT INTO embedding_metadata(id,key,string_value) VALUES(?, 'project','F1D')",
        [(i,) for i in range(f1d_rows)])
    c.commit(); c.close()

def test_drift_uses_chroma_count_not_watermark(tmp_path):
    # Regression for the v1 false-positive: drift depends on per-project
    # CHROMA embedding count vs SQLite obs count, NOT a global-id watermark.
    db = tmp_path/"m.db"; _mkdb(db)
    c = sqlite3.connect(db)
    c.executemany("INSERT INTO observations(project,created_at_epoch) VALUES(?,?)",
                   [("F1D", 1)] * 500)
    c.commit(); c.close()
    st = tmp_path/"s.json"
    _mk_chroma(tmp_path/"chroma"/"chroma.sqlite3", 400)   # 80% -> pass
    rh = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert rh["checks"]["drift"] == "pass"
    (tmp_path/"chroma"/"chroma.sqlite3").unlink()
    _mk_chroma(tmp_path/"chroma"/"chroma.sqlite3", 200)   # 40% -> #2487 fail
    rd = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert rd["checks"]["drift"] == "fail"
    assert any("#2487" in m for m in rd["messages"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest scripts/claude_mem_integration/tests/test_health_gate.py -v`
Expected: FAIL (`health_gate.py` missing).

- [ ] **Step 3: Write the implementation**

```python
# scripts/claude_mem_integration/health_gate.py
"""C3/M2/§6.1: claude-mem capture-health gate (SessionStart hook).

Checks M2(a) worker alive, (b) queue not stuck, (c) observations grew,
(d) chroma not under-populated vs source (#2487). On ANY failure prints a
SessionStart hook JSON with hookSpecificOutput.additionalContext so the
status is LLM-VISIBLE (spec §6.1). On all-pass it suppresses output.

Hook contract: stdin = Claude Code SessionStart payload (json); we only
need cwd to pick the project. stdout = one JSON line.
"""
from __future__ import annotations
import json, sqlite3, socket, sys, time, os
from pathlib import Path

HOME = Path.home()
DB = HOME / ".claude-mem" / "claude-mem.db"
STATE = HOME / ".claude-mem" / ".healthgate-state.json"
PIDF = HOME / ".claude-mem" / "worker.pid"

QUEUE_PENDING_MAX = 50          # >this pending rows = stuck
QUEUE_AGE_MAX_S = 1800          # oldest pending >30min = stuck

def _ro(p):
    return sqlite3.connect(f"file:{Path(p).as_posix()}?mode=ro", uri=True)

def _project_from_cwd(cwd: str) -> str:
    # claude-mem keys projects by basename of the repo root; fall back to cwd name
    return Path(cwd).name if cwd else "unknown"

def _worker_alive(port: int) -> bool:
    if port == 0:
        return True  # test bypass
    try:
        s = socket.socket(); s.settimeout(2)
        rc = s.connect_ex(("127.0.0.1", port)); s.close()
        return rc == 0
    except OSError:
        return False

def evaluate(db: str, project: str, state_path: str, port: int,
             worker_check: bool = True) -> dict:
    checks, msgs = {}, []
    # (a) worker
    if worker_check:
        prt = port
        if prt == 0 and PIDF.exists():
            try: prt = json.loads(PIDF.read_text()).get("port", 0)
            except Exception: prt = 0
        ok = _worker_alive(prt)
        checks["worker"] = "pass" if ok else "fail"
        if not ok: msgs.append(f"worker not reachable on 127.0.0.1:{prt}")
    else:
        checks["worker"] = "skip"
    try:
        con = _ro(db); cur = con.cursor()
        # (b) queue
        try:
            pend = cur.execute("SELECT count(*) FROM pending_messages WHERE status='pending'").fetchone()[0]
            oldest = cur.execute("SELECT min(created_at_epoch) FROM pending_messages WHERE status='pending'").fetchone()[0]
            stuck = pend > QUEUE_PENDING_MAX or (oldest and (time.time()*1000 - oldest)/1000 > QUEUE_AGE_MAX_S)
            checks["queue"] = "fail" if stuck else "pass"
            if stuck: msgs.append(f"queue stuck: {pend} pending")
        except sqlite3.OperationalError:
            checks["queue"] = "unknown"
        # (c) growth
        cnt = cur.execute("SELECT count(*) FROM observations WHERE project=?", (project,)).fetchone()[0]
        st = {}
        if Path(state_path).exists():
            try: st = json.loads(Path(state_path).read_text())
            except Exception: st = {}
        prev = st.get(project, {}).get("obs_count")
        if prev is None:
            checks["growth"] = "first-run"
        elif cnt > prev:
            checks["growth"] = "pass"
        else:
            checks["growth"] = "fail"
            msgs.append(f"observations did not grow for {project} ({prev}->{cnt})")
        st.setdefault(project, {})["obs_count"] = cnt
        st[project]["last_check_epoch"] = int(time.time()*1000)
        # (e) #2485 capture-pipeline-alive: did ANY observation anywhere
        # get written since last check? This is the headline open bug
        # against v13.2.0 (observations table stays at 0). Without this
        # the gate cannot catch the failure mode it exists for.
        gtot = cur.execute("SELECT count(*) FROM observations").fetchone()[0]
        gprev = st.get("__global__", {}).get("obs_count")
        if gprev is None:
            checks["capture_pipeline"] = "first-run"
        elif gtot > gprev:
            checks["capture_pipeline"] = "pass"
        else:
            checks["capture_pipeline"] = "fail"
            msgs.append(f"#2485: NO new observations anywhere "
                        f"({gprev}->{gtot}) — capture pipeline may be dead")
        st.setdefault("__global__", {})["obs_count"] = gtot
        Path(state_path).write_text(json.dumps(st, indent=2))
        # (d) chroma drift (#2487): per-project chroma embedding count vs
        # per-project SQLite obs count. #2487's signature is chroma FAR
        # BELOW source (issue #2487 live numbers: SQLite 703 vs chroma
        # 363 ≈ 0.52). chroma-sync-state.json[project].observations is a
        # GLOBAL-ID WATERMARK (≈ max obs id), NOT a per-project count —
        # comparing it to a per-project rowcount was the v1 false-positive
        # bug (fails every session since global ids ≫ any project's
        # rowcount). Correct test = count project-tagged chroma embeddings.
        try:
            chroma_db = Path(db).parent / "chroma" / "chroma.sqlite3"
            cdb = _ro(chroma_db); ccur = cdb.cursor()
            chroma_n = ccur.execute(
                "SELECT count(*) FROM embedding_metadata "
                "WHERE key='project' AND string_value=?",
                (project,)).fetchone()[0]
            cdb.close()
            DRIFT_R = 0.5   # #2487 floor (703->363 ≈ .52); healthier passes
            if cnt > 0 and chroma_n < cnt * DRIFT_R:
                checks["drift"] = "fail"
                msgs.append(f"#2487: chroma has {chroma_n} '{project}' "
                            f"embeddings vs {cnt} source obs "
                            f"(<{DRIFT_R:.0%}) — semantic index "
                            f"under-populated")
            else:
                checks["drift"] = "pass"
        except Exception:
            checks["drift"] = "unknown"
        con.close()
    except sqlite3.OperationalError as e:
        checks["db"] = "fail"; msgs.append(f"db unreadable: {e}")
    # FAIL-CLOSED (Sina directive 2026-05-15): ANY non-green signal warns,
    # not only a hard "fail" — unknown/skip count as not-healthy.
    failed = [k for k, v in checks.items() if v not in ("pass", "first-run")]
    return {"ok": not failed, "checks": checks, "messages": msgs,
            "project": project}

def _emit(result: dict) -> None:
    if result["ok"]:
        print(json.dumps({"continue": True, "suppressOutput": True}))
        return
    ctx = ("[claude-mem HEALTH GATE — DEGRADED] "
           + "; ".join(result["messages"])
           + f" | checks={result['checks']}. Per spec §6.1: SURFACE THIS "
             "ALERT PROMINENTLY to the user at the top of your reply, treat "
             "claude-mem recall as UNTRUSTED this session (do not rely on "
             "injected observations / mem-search for factual claims), and "
             "state the two-flip rollback (settings.json autoMemoryEnabled:"
             "true + autoDreamEnabled:true) until the user clears this.")
    print(json.dumps({
        "continue": True,
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
        },
    }))

def main_for_test(db, project, state_path, port=0, worker_check=True):
    _emit(evaluate(db, project, state_path, port, worker_check))

if __name__ == "__main__":
    raw = sys.stdin.read() if not sys.stdin.isatty() else "{}"
    try: payload = json.loads(raw or "{}")
    except Exception: payload = {}
    cwd = payload.get("cwd") or os.getcwd()
    project = _project_from_cwd(cwd)
    try:
        _emit(evaluate(str(DB), project, str(STATE), port=0,
                       worker_check=True))
    except Exception as e:
        # fail-safe: never break the session; report degraded-unknown
        print(json.dumps({"continue": True, "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": f"[claude-mem HEALTH GATE] check errored: {e}"
                                 " — treat memory with caution this session."}}))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `python -m pytest scripts/claude_mem_integration/tests/test_health_gate.py -v`
Expected: 4 passed.

- [ ] **Step 5: Register the hook in `~/.claude/settings.json`**

Add this object to the existing `hooks.SessionStart` array (do NOT remove the existing entries — append a new group):

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "python \"C:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/scripts/claude_mem_integration/health_gate.py\""
    }
  ]
}
```

- [ ] **Step 6: Verify the hook fires and is LLM-visible on a forced failure**

Temporarily corrupt the state to force a no-growth failure, start a new Claude session, confirm the `[claude-mem HEALTH GATE — DEGRADED]` text appears in the session context, then restore:

Run (simulate): `echo {} | python scripts/claude_mem_integration/health_gate.py` twice in a row in a tmp project; second run prints a JSON with `hookSpecificOutput.additionalContext` containing `DEGRADED`.
Expected: JSON with `continue:true` and the DEGRADED additionalContext on the 2nd invocation.

- [ ] **Step 7: Commit**

```bash
git add scripts/claude_mem_integration/health_gate.py scripts/claude_mem_integration/tests/test_health_gate.py
git commit -m "feat(claude-mem): C3 capture-health SessionStart gate, LLM-visible (M2/§6.1)"
```
(`~/.claude/settings.json` is outside the repo — not committed; recorded in Task 8 log.)

---

## Task 6: Pin config + capture-model decision (C4 / M4)

**Files:**
- Create: `scripts/claude_mem_integration/claude_mem_settings_snapshot.json` (recorded copy)

- [ ] **Step 1: Snapshot current claude-mem settings**

```bash
cp "C:/Users/sinas/.claude-mem/settings.json" "scripts/claude_mem_integration/claude_mem_settings_snapshot.json"
```

- [ ] **Step 2: Record the model decision in the snapshot header**

Prepend a comment file `scripts/claude_mem_integration/claude_mem_settings_snapshot.README.md`:

```markdown
# claude-mem settings snapshot (C4/M4)
- Captured: 2026-05-15
- CLAUDE_MEM_MODEL: claude-haiku-4-5-20251001 (DEFAULT — KEPT for Phase 1).
  Decision: do not change the capture model during the verification window;
  a Sonnet upgrade is out of scope (post-cutover option only).
- This snapshot is the pinned baseline. Any drift from it before a
  claude-mem upgrade is a change to investigate (see PRE_UPGRADE_CHECKLIST).
```

- [ ] **Step 3: Commit**

```bash
git add scripts/claude_mem_integration/claude_mem_settings_snapshot.json scripts/claude_mem_integration/claude_mem_settings_snapshot.README.md
git commit -m "chore(claude-mem): C4 pin settings snapshot + Haiku model decision (M4)"
```

---

## Task 7: Pre-upgrade checklist (C6 / M4)

**Files:**
- Create: `scripts/claude_mem_integration/PRE_UPGRADE_CHECKLIST.md`

- [ ] **Step 1: Write the checklist**

```markdown
# claude-mem PRE-UPGRADE CHECKLIST (M4 / C6)

Do ALL of these BEFORE running any claude-mem version upgrade. The plugin
ships ~12 releases/7 days; an upgrade can silently re-introduce capture=0
or chroma drift.

1. [ ] Run an on-demand backup: `python scripts/claude_mem_integration/backup_claude_mem.py`
2. [ ] Read the target release notes + open issues at
       github.com/thedotmack/claude-mem — confirm #2485 (observations stay
       at 0) and #2487 (chroma 48% drift) are NOT open/regressed in the
       target version.
3. [ ] Note current `~/.claude-mem/settings.json` vs the pinned snapshot;
       investigate any diff.
4. [ ] Upgrade.
5. [ ] Re-run the P0→P1 gate (Task 8) in full before trusting it.
6. [ ] Run the canary (`python scripts/claude_mem_integration/canary.py plant`
       then, next session, `... verify`) — must PASS before relying on memory.
7. [ ] If any check fails: execute the two-flip rollback and pin back to the
       previous claude-mem version.
```

- [ ] **Step 2: Commit**

```bash
git add scripts/claude_mem_integration/PRE_UPGRADE_CHECKLIST.md
git commit -m "docs(claude-mem): C6 pre-upgrade checklist (M4)"
```

---

## Task 8: P0 → P1 verification gate

**Files:**
- Create: `scripts/claude_mem_integration/P0_P1_GATE_LOG.md`

- [ ] **Step 1: Run all three gate checks and record results**

Create `scripts/claude_mem_integration/P0_P1_GATE_LOG.md` with the literal results of:
1. Firewall: `python -c "import socket;s=socket.socket();s.settimeout(2);print(s.connect_ex(('127.0.0.1',37777)))"` → expect `0` (localhost OK); note the firewall rule name from Task 4.
2. Backup restore: `python scripts/claude_mem_integration/backup_claude_mem.py` then
   `python -c "import sqlite3,glob;f=sorted(glob.glob(r'C:/Users/sinas/.claude-mem/backups/cmint/claude-mem-[0-9]*.db'))[-1];print(f, sqlite3.connect('file:%s?mode=ro'%f,uri=True).execute('select count(*) from observations').fetchone())"`
   → expect a row count > 0 from the restored copy.
3. Health gate green now: `echo {} | python scripts/claude_mem_integration/health_gate.py` → expect `{"continue": true, "suppressOutput": true}` (all-pass) on the current healthy install.

- [ ] **Step 2: Gate decision**

In the log file, write `P0->P1: PASS` only if all three pass. If any fails, STOP — fix before Phase 1.

- [ ] **Step 3: Commit**

```bash
git add scripts/claude_mem_integration/P0_P1_GATE_LOG.md
git commit -m "docs(claude-mem): P0->P1 gate results"
```

---

## Task 9: Phase 1 — recall-fidelity canary (spec §8, mechanics specified here)

**Files:**
- Create: `scripts/claude_mem_integration/canary.py`
- Create: `scripts/claude_mem_integration/recall_canary_log.md`

**Mechanics (concrete — spec deferred these here):**
- `plant`: writes a uniquely-tagged fact to a real file via the tool path so PostToolUse captures it. The fact = `CANARY <id>: verification constant = <value>; source = spec §8`. Because claude-mem's PostToolUse hook enqueues `tool_input`/`tool_response` of the Write, the canary enters capture deterministically (more reliable than relying on transcript summarization).
- `verify`: PASS must be proven on the **same recall path the model actually uses**, not just the CLI. In the verify session the operator (a) confirms the SessionStart `additionalContext` / injected context for that session, and (b) calls the `mcp__plugin_claude-mem_mcp-search__search` MCP tool for the cid, then passes that returned text to `canary.py verify <cid> --recalled "<mcp result text>"`. The script PASSES iff that LLM-path text contains `<value>` **verbatim** AND the `source = spec §8` token. It additionally runs `npx claude-mem search` as a NON-authoritative cross-check and logs both; a CLI-pass / MCP-fail split is itself a FAIL (it is the exact split the gate exists to catch).
- Gate: **≥ 3 PASS, 0 FAIL — using 3 DISTINCT canaries, each planted in its own session and recalled in a later distinct session** (spec §8). Three separate plant→recall cycles (not 3 re-verifies of one canary): this tests capture *and* recall stability across independent capture events. Sessions are `startup`/`/clear`/`/compact` segments.

- [ ] **Step 1: Write the canary tool**

```python
# scripts/claude_mem_integration/canary.py
"""Phase-1 recall-fidelity canary (spec §8). Subcommands: plant | verify.

plant  -> writes ~/.claude-mem/canary/<id>.txt with the sentinel fact
          (the Write is a real tool action -> claude-mem PostToolUse
          captures it deterministically).
verify -> queries claude-mem's own CLI search for the id; PASS iff the
          numeric value is reproduced VERBATIM and the source token is
          present. Appends a ledger row. Exit 0 on PASS, 2 on FAIL.
"""
from __future__ import annotations
import json, subprocess, sys, time, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "recall_canary_log.md"
CANDIR = Path.home() / ".claude-mem" / "canary"

def plant() -> str:
    CANDIR.mkdir(parents=True, exist_ok=True)
    cid = time.strftime("%Y%m%d") + "-" + secrets.token_hex(3)
    value = f"{secrets.randbelow(900000)+100000}.{secrets.randbelow(900)+100}"
    text = (f"CANARY {cid}: verification constant = {value}; "
            f"source = spec §8")
    (CANDIR / f"{cid}.txt").write_text(text, encoding="utf-8")
    rec = {"cid": cid, "value": value, "planted_epoch": int(time.time()*1000)}
    (CANDIR / f"{cid}.json").write_text(json.dumps(rec))
    print(f"PLANTED cid={cid} value={value}")
    print("Do other work this session, end it, start a NEW session, then in "
          f"that session call the mem-search MCP tool for 'CANARY {cid}', and "
          "run:  python scripts/claude_mem_integration/canary.py verify "
          f"{cid} --recalled \"<text the MCP tool returned>\"")
    return cid

def _check(text: str, value: str):
    return (value in text), ("spec §8" in text)

def verify(cid: str, recalled: str) -> bool:
    rec = json.loads((CANDIR / f"{cid}.json").read_text())
    value = rec["value"]
    # AUTHORITATIVE: the LLM-path text — what the mem-search MCP tool
    # returned this session (what the model actually sees).
    mcp_verbatim, mcp_sourced = _check(recalled, value)
    mcp_ok = mcp_verbatim and mcp_sourced
    # NON-authoritative cross-check: claude-mem CLI search.
    try:
        cli = subprocess.run(["npx", "claude-mem", "search", f"CANARY {cid}"],
                              capture_output=True, text=True, timeout=120,
                              shell=True).stdout
    except Exception as e:
        cli = f"<<cli error: {e}>>"
    cli_verbatim, cli_sourced = _check(cli, value)
    cli_ok = cli_verbatim and cli_sourced
    split = cli_ok and not mcp_ok          # CLI-pass / MCP-fail = the bug
    ok = mcp_ok and not split
    row = (f"| {time.strftime('%Y-%m-%d %H:%M')} | {cid} | {value} | "
           f"MCP(verbatim={mcp_verbatim},src={mcp_sourced}) "
           f"CLI(verbatim={cli_verbatim},src={cli_sourced}) split={split} | "
           f"{'PASS' if ok else 'FAIL'} |\n")
    if not LEDGER.exists():
        LEDGER.write_text("# Recall-fidelity ledger (spec §8: >=3 PASS, "
                          "0 FAIL; 3 DISTINCT canaries; MCP path "
                          "authoritative)\n\n"
                          "| when | cid | value | detail | result |\n"
                          "|---|---|---|---|---|\n", encoding="utf-8")
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(row)
    print(("PASS" if ok else "FAIL") + f" cid={cid} mcp_ok={mcp_ok} "
          f"cli_ok={cli_ok} split={split}")
    return ok

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("plant", "verify"):
        print('usage: canary.py plant | verify <cid> --recalled "<mcp text>"')
        sys.exit(1)
    if sys.argv[1] == "plant":
        plant()
    else:
        if "--recalled" not in sys.argv:
            print('verify requires --recalled "<text the mem-search MCP '
                  'tool returned for this cid THIS session>"')
            sys.exit(1)
        _cid = sys.argv[2]
        _recalled = sys.argv[sys.argv.index("--recalled") + 1]
        sys.exit(0 if verify(_cid, _recalled) else 2)
```

- [ ] **Step 2: Smoke test the plant path**

Run: `python scripts/claude_mem_integration/canary.py plant`
Expected: prints `PLANTED cid=... value=...`, creates `~/.claude-mem/canary/<id>.txt` + `.json`.

- [ ] **Step 3: Commit the tool**

```bash
git add scripts/claude_mem_integration/canary.py
git commit -m "feat(claude-mem): Phase-1 recall-fidelity canary tool (spec §8)"
```

- [ ] **Step 4: Run the Phase-1 window (operational, not a code step)**

Over ≥ 8 sessions spanning ≥ 7 days, with native auto-memory STILL ON (M1):
- Each session start: confirm the health gate is green (no DEGRADED additionalContext).
- **3 DISTINCT canaries** (not 3 re-verifies of one): for each of 3 separate plant sessions → `canary.py plant`, do real work, end the session; in a **later distinct session** call the `mcp__plugin_claude-mem_mcp-search__search` MCP tool for that cid, then `canary.py verify <cid> --recalled "<mcp result>"`. Need **≥3 PASS, 0 FAIL**.
- One-time project-key sanity (advisor note): confirm `health_gate._project_from_cwd` basename equals the key claude-mem uses in `~/.claude-mem/chroma-sync-state.json` (observed "F1D" matches; verify, don't assume — if it differs, set the project explicitly rather than via cwd basename).
- Record every result (the script appends to `recall_canary_log.md`).

- [ ] **Step 5: Commit the ledger when the window completes**

```bash
git add scripts/claude_mem_integration/recall_canary_log.md
git commit -m "docs(claude-mem): Phase-1 recall-fidelity ledger"
```

---

## Task 10: P1 → P2 gate + cutover  ⚠ RATIFICATION REQUIRED

**Files:**
- Create: `scripts/claude_mem_integration/claude_mem_directive.md` (C5 text)
- Modify: `~/.claude/CLAUDE.md` (append C5 directive — Phase 2 only)
- Modify: `~/.claude/settings.json` (`autoMemoryEnabled`/`autoDreamEnabled` → false)

**⚠ This task disables native memory. STOP and obtain explicit Sina ratification before Step 3. Do not proceed autonomously.**

- [ ] **Step 1: Evaluate the P1→P2 gate**

Confirm from `recall_canary_log.md` + the Phase-1 notes: ≥ 8 sessions over ≥ 7 days, health gate green every session (0 failures), **≥ 3 PASS in 3 distinct sessions with 0 FAIL**. Write `P1->P2: PASS/FAIL` + evidence into `P0_P1_GATE_LOG.md` (reuse the file, new section). If FAIL → do NOT cut over; keep native ON; investigate.

- [ ] **Step 2: Draft + non-conflict-verify the C5 directive (spec §6 flag)**

Create `scripts/claude_mem_integration/claude_mem_directive.md`:

```markdown
## Memory system (claude-mem is the system of record)

claude-mem is the persistent memory of record. When you need cross-session
context, use the claude-mem `mem-search` skill / injected observations.
Native Claude auto-memory is disabled by configuration; do not assume a
`memory/` file workflow. This directive is NORMATIVE guidance; the
structural guarantee is `autoMemoryEnabled:false` + `autoDreamEnabled:false`.
If the claude-mem health gate reports DEGRADED, treat memory as untrusted
and tell the user (see rollback).
```

Verify non-conflict: read `~/.claude/CLAUDE.md` and confirm this text does not contradict the existing mandatory frameworks (karpathy-guidelines, user-profile-sina, scope-discipline, superpowers). **Exact reconciliation of the native auto-memory / "## Project memory" section (do NOT delete it — the two-flip rollback depends on it still being present and valid):** append a single explicit sentence to the END of that section reading — *"SUPERSEDED while `autoMemoryEnabled` is false (claude-mem is the system of record); this section becomes active again automatically on rollback (both booleans → true)."* Deleting or rewriting the section would break §11 rollback. Record the before/after of `~/.claude/CLAUDE.md` and the conflict-check result inline in `claude_mem_directive.md`.

- [ ] **Step 3: ⚠ RATIFIED CUTOVER — append directive + flip settings**

Only after Sina says go:
1. Append the contents of `claude_mem_directive.md` to `~/.claude/CLAUDE.md`.
2. In `~/.claude/settings.json` set `"autoMemoryEnabled": false` and `"autoDreamEnabled": false`.

- [ ] **Step 4: Verify cutover + rollback both work**

- New session: confirm health gate still green; confirm no native auto-memory write occurs (no new files in `~/.claude/projects/<id>/memory/` after a session that would previously have written one).
- Rollback drill: set both back to `true`, start a session, confirm native resumes; then set back to `false` to remain in Phase 2. Confirms the two-flip rollback is real.

- [ ] **Step 5: Commit the in-repo artifacts**

```bash
git add scripts/claude_mem_integration/claude_mem_directive.md scripts/claude_mem_integration/P0_P1_GATE_LOG.md
git commit -m "docs(claude-mem): P1->P2 gate + ratified cutover record"
```
(`~/.claude/CLAUDE.md` and `settings.json` are outside the repo — record the change + timestamp in the gate log.)

---

## Self-Review

**1. Spec coverage:**
- C1/M5 → Task 4 ✓ · C2/M6 → Tasks 2,3 ✓ · C3/M2/§6.1 → Task 5 ✓ · C4/M4 → Task 6 ✓ · C5 + §6 conflict-flag → Task 10 Step 2 ✓ · C6/M4 → Task 7 ✓
- Phases: Phase 0 → Tasks 1–8 ✓ · Phase 1 + canary (spec §8, ≥3 PASS) → Task 9 ✓ · Phase 2 structural two-flip + directive → Task 10 ✓
- §7 rollback → Task 10 Step 4 drill ✓ · §11 runbook referenced in health-gate message ✓
- §9 context-mode out-of-scope: not touched by any task ✓ · Campello cross-ref: not affected, untouched ✓
- M7 numeric truth-gate: correctly OUT of scope of this plan (separate Campello work) ✓
- No spec requirement left without a task.

**2. Placeholder scan:** No "TBD/TODO/handle edge cases"; every code step has complete code; canary mechanics fully specified (spec's only deferral) in Task 9. Capture-model decision resolved (Task 6, Haiku). ✓

**3. Type/name consistency:** `evaluate(db, project, state_path, port, worker_check)` and `main_for_test(...)` signatures match between `health_gate.py` and `test_health_gate.py`; `backup(src, outdir, retain, _force_unique)` matches its test; `canary.py plant|verify <cid>` matches Task 9 prose and Task 7/8 references. Port 37777 consistently flagged as "verify actual from worker.pid". ✓

Issues found: none requiring a new task. Fixed inline: none needed.

---

## Execution Handoff

Plan complete and saved to `docs/superpowers/plans/2026-05-15-claude-mem-primary-integration.md`.

⚠ Note: Phase 0 (Tasks 1–8) and Phase 1 (Task 9) are low-risk/reversible. **Task 10 (Phase 2) disables native memory and requires explicit Sina ratification at that point** — it is intentionally a hard stop in the plan.
