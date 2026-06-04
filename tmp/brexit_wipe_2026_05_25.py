"""
Brexit/Campello observation wipe from claude-mem.db (2026-05-25).

Authorized by Sina per rigor-debug clean-slate directive. Backup-then-DELETE
with verification. Chroma vector cleanup deferred (orphan vectors harmless).
"""
import shutil
import sqlite3
from datetime import datetime
from pathlib import Path

DB = Path(r"C:\Users\sinas\.claude-mem\claude-mem.db")
STAMP = datetime.now().strftime("%Y%m%d-%H%M%S")
BACKUP = Path(rf"C:\Users\sinas\.claude-mem\backups\claude-mem-{STAMP}-pre-brexit-wipe.db")

PATTERNS = [
    "brexit",
    "campello",
    "betauk",
    "beta_uk",
    "β^uk",
    "βᵁᴷ",
]

assert DB.exists(), f"DB missing: {DB}"

print(f"[1] backup {DB} -> {BACKUP}")
shutil.copy2(DB, BACKUP)
print(f"    OK  ({BACKUP.stat().st_size:,} bytes)")

con = sqlite3.connect(str(DB))
cur = con.cursor()

print("\n[2] schema discovery")
tables = [r[0] for r in cur.execute(
    "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
)]
for t in tables:
    cols = [(r[1], r[2]) for r in cur.execute(f"PRAGMA table_info({t})")]
    print(f"  TABLE {t}: " + ", ".join(f"{n}({ty})" for n, ty in cols))

obs_tables = [t for t in tables if "obs" in t.lower() or "memor" in t.lower() or "session" in t.lower()]
print(f"\n[3] candidate tables: {obs_tables}")

def text_cols(table):
    return [
        r[1] for r in cur.execute(f"PRAGMA table_info({table})")
        if r[2].upper() in ("TEXT", "VARCHAR", "STRING", "")
    ]

def build_where(table, scope_proj=True):
    cols = text_cols(table)
    if not cols:
        return None, []
    parts = []
    params = []
    for c in cols:
        for p in PATTERNS:
            parts.append(f"LOWER(COALESCE({c},'')) LIKE ?")
            params.append(f"%{p.lower()}%")
    where = "(" + " OR ".join(parts) + ")"
    if scope_proj:
        proj_cols = [r[1] for r in cur.execute(f"PRAGMA table_info({table})") if r[1].lower() in ("project", "project_id", "projectid")]
        if proj_cols:
            where = f"({proj_cols[0]} = ? OR {proj_cols[0]} IS NULL) AND " + where
            params.insert(0, "F1D")
    return where, params

print("\n[4] PRE-COUNT (rows matching Brexit/Campello patterns)")
total_pre = 0
counts = {}
for t in obs_tables:
    where, params = build_where(t)
    if not where:
        continue
    n = cur.execute(f"SELECT COUNT(*) FROM {t} WHERE {where}", params).fetchone()[0]
    counts[t] = n
    total_pre += n
    print(f"  {t}: {n} match rows")
print(f"  TOTAL PRE: {total_pre}")

print("\n[5] DELETE")
deleted_per_table = {}
for t in obs_tables:
    where, params = build_where(t)
    if not where:
        continue
    cur.execute(f"DELETE FROM {t} WHERE {where}", params)
    deleted_per_table[t] = cur.rowcount
    print(f"  DELETE FROM {t}: {cur.rowcount} rows")
con.commit()

print("\n[6] POST-COUNT verify")
total_post = 0
for t in obs_tables:
    where, params = build_where(t)
    if not where:
        continue
    n = cur.execute(f"SELECT COUNT(*) FROM {t} WHERE {where}", params).fetchone()[0]
    total_post += n
    print(f"  {t}: {n} remaining match rows")
print(f"  TOTAL POST: {total_post}")

print(f"\n[7] SUMMARY")
print(f"  backup:  {BACKUP}")
print(f"  pre:     {total_pre}")
print(f"  deleted: {sum(deleted_per_table.values())}")
print(f"  post:    {total_post}")
print(f"  status:  {'OK' if total_post == 0 else 'INCOMPLETE — investigate'}")

con.close()
