# scripts/claude_mem_integration/backup_claude_mem.py
"""C2/M6: SQLite Online-Backup of claude-mem.db to a rotating dir.

Online Backup API copies a CONSISTENT snapshot even while the worker
holds the WAL open (a plain file copy of a WAL db can be torn).

Isolation (execution-found bug fix 2026-05-15): our backups live in a
DEDICATED OWNED subdir (`backups/cmint`), and rotation matches only the
strict pattern `claude-mem-[0-9]*.db`. claude-mem itself writes its own
pre-upgrade dumps as `claude-mem-pre-<ver>-<ISO>.db` into `backups/`;
the broad glob `claude-mem-*.db` matched THOSE too and lexicographic
sort placed `...-pre-...` after our `...-2026...`, so the prior rotation
could delete OUR backups while keeping stale 0-row foreign ones. Both
the owned subdir and the digit-anchored pattern prevent ever touching a
non-ours file.
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
