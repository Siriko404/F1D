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
    # Regression for the v1 false-positive: drift must depend on the
    # per-project CHROMA embedding count vs SQLite obs count, NOT on any
    # global-id watermark. No chroma-sync-state.json exists here, so a
    # pass proves the watermark path is gone.
    db = tmp_path/"m.db"; _mkdb(db)
    c = sqlite3.connect(db)
    c.executemany("INSERT INTO observations(project,created_at_epoch) VALUES(?,?)",
                   [("F1D", 1)] * 500)
    c.commit(); c.close()
    st = tmp_path/"s.json"
    # healthy: 400 chroma vs 500 obs (>=50%) -> pass
    _mk_chroma(tmp_path/"chroma"/"chroma.sqlite3", 400)
    rh = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert rh["checks"]["drift"] == "pass"
    # #2487: 200 chroma vs 500 obs (<50%) -> fail with #2487 message
    (tmp_path/"chroma"/"chroma.sqlite3").unlink()
    _mk_chroma(tmp_path/"chroma"/"chroma.sqlite3", 200)
    rd = hg.evaluate(str(db), "F1D", str(st), port=0, worker_check=False)
    assert rd["checks"]["drift"] == "fail"
    assert any("#2487" in m for m in rd["messages"])
