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
    # Regression: claude-mem's own pre-upgrade dumps are
    # `claude-mem-pre-<ver>-<ISO>.db`. Our rotation must NEVER prune or
    # select them (the execution-found data-safety bug).
    src = tmp_path / "claude-mem.db"
    sqlite3.connect(src).close()
    outdir = tmp_path / "b"; outdir.mkdir()
    foreign = outdir / "claude-mem-pre-12.4.3-2026-05-12T21-53-47-190Z.db"
    foreign.write_bytes(b"")            # 0-row foreign dump
    for _ in range(20):
        bk.backup(str(src), str(outdir), retain=3, _force_unique=True)
    assert foreign.exists()                                   # never pruned
    assert len(list(outdir.glob(bk.OURS_GLOB))) == 3          # ours rotated
    assert foreign not in list(outdir.glob(bk.OURS_GLOB))     # pattern excludes it
