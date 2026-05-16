# scripts/claude_mem_integration/backup_claude_mem.py
"""C2/M6: SQLite Online-Backup of claude-mem.db to a rotating dir.

Online Backup API copies a CONSISTENT snapshot even while the worker
holds the WAL open (a plain file copy of a WAL db can be torn).
"""
from __future__ import annotations
import sqlite3, sys, time, os
from pathlib import Path

DEFAULT_SRC = Path.home() / ".claude-mem" / "claude-mem.db"
DEFAULT_OUT = Path.home() / ".claude-mem" / "backups"

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
    backups = sorted(out.glob("claude-mem-*.db"))
    for old in backups[:-retain]:
        old.unlink()
    return str(dest)

if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else str(DEFAULT_SRC)
    out = sys.argv[2] if len(sys.argv) > 2 else str(DEFAULT_OUT)
    if not Path(src).exists():
        print(f"SKIP: {src} not found"); sys.exit(0)
    print("backed up ->", backup(src, out))
