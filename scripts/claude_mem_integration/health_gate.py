# scripts/claude_mem_integration/health_gate.py
"""C3/M2/§6.1: claude-mem capture-health gate (SessionStart hook).

Checks M2(a) worker alive, (b) queue not stuck, (c) observations grew,
(d) chroma watermark not ahead of source. On ANY failure it prints a
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
SYNC = HOME / ".claude-mem" / "chroma-sync-state.json"
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
        # (d) chroma drift
        try:
            wm = json.loads(SYNC.read_text()).get(project, {}).get("observations")
            if wm is not None and wm > cnt + 5:   # watermark claims more than source has
                checks["drift"] = "fail"
                msgs.append(f"chroma watermark {wm} ahead of source obs {cnt} (#2487)")
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
