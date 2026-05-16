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
