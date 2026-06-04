"""Pre-rewrite safety audit. Read-only. Verifies:
  1. Locked artifacts exist + SHA256 hashes
  2. F1D shared infra files unchanged (size + mtime sanity)
  3. Git uncommitted state (untracked + modified) reviewed
  4. .gitnexus/ binary is gitignored (143 MB shouldn't enter the repo)
  5. brexit_*.py + scripts/campello_rebuild/ NOT YET deleted (rewrite in scope, current state preserved)
  6. Memory files still present
Emits tmp/safety_audit_2026_05_26.md with per-check status.
"""
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(".")
OUT = ROOT / "tmp" / "safety_audit_2026_05_26.md"

def sha256_of(path):
    if not path.exists() or not path.is_file():
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()[:16]

def stat_or_none(p):
    if not p.exists(): return None
    s = p.stat()
    return {"size": s.st_size, "mtime": s.st_mtime}

# 1. Locked artifacts
locked = [
    "tmp/campello_method_lockin.md",
    "tmp/campello_variable_lockin.md",
    "tmp/campello_table1_anchor_2026_05_26.json",
    "tmp/campello_pdf_extract/full_main_pdfpage21.txt",  # Table 1 page
]
locked_status = []
for p in locked:
    fp = ROOT / p
    locked_status.append({
        "path": p,
        "exists": fp.exists(),
        "size": fp.stat().st_size if fp.exists() else None,
        "sha256_16": sha256_of(fp),
    })

# 2. F1D shared infra files
infra = [
    "src/f1d/shared/variables/_compustat_engine.py",
    "src/f1d/shared/variables/_crsp_engine.py",
    "src/f1d/shared/variables/winsorization.py",
    "src/f1d/shared/variables/panel_utils.py",
    "src/f1d/shared/variables/base.py",
    "src/f1d/shared/path_utils.py",
]
infra_status = [{"path": p, **(stat_or_none(ROOT / p) or {"exists": False})} for p in infra]

# 3. Git state
def git(*args):
    try:
        return subprocess.check_output(["git", *args], cwd=str(ROOT),
                                       stderr=subprocess.STDOUT).decode("utf-8", errors="replace")
    except subprocess.CalledProcessError as e:
        return e.output.decode("utf-8", errors="replace")

git_head = git("rev-parse", "HEAD").strip()
git_branch = git("rev-parse", "--abbrev-ref", "HEAD").strip()
git_status_z = git("status", "--porcelain=v1")
# Categorize files
modified, untracked, deleted = [], [], []
for line in git_status_z.splitlines():
    if not line.strip(): continue
    code = line[:2]
    fname = line[3:].strip()
    if code.startswith("M") or "M" in code: modified.append(fname)
    elif code.startswith("??"): untracked.append(fname)
    elif code.startswith("D"): deleted.append(fname)

# 4. .gitnexus gitignored?
gitignore = (ROOT / ".gitignore")
gitnexus_ignored = False
gitnexus_text = ""
if gitignore.exists():
    gitnexus_text = gitignore.read_text(encoding="utf-8", errors="replace")
    gitnexus_ignored = any(".gitnexus" in line for line in gitnexus_text.splitlines() if not line.strip().startswith("#"))
# Also check inside .gitnexus/.gitignore which GitNexus writes
local_gitignore = ROOT / ".gitnexus" / ".gitignore"
local_gitnexus_ignored_text = local_gitignore.read_text(encoding="utf-8") if local_gitignore.exists() else ""

# 5. brexit_*.py + scripts/campello_rebuild/ inventory (in-scope-for-rewrite, NOT deleted)
brexit_files = sorted(ROOT.glob("src/f1d/shared/variables/brexit_*.py"))
campello_rebuild = sorted(ROOT.glob("scripts/campello_rebuild/*.py"))

# 6. Memory files
memory_dir = Path.home() / ".claude" / "projects" / "C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D" / "memory"
campello_memories = [
    "project_campello_systematic_debug_2026_05_26.md",
    "feedback_nlm_hallucinates_cell_values_2026_05_26.md",
    "feedback_nlm_off_by_n_paragraphs_2026_05_26.md",
    "reference_campello_pdf_artifacts_2026_05_26.md",
    "reference_campello_paper_metadata_2026_05_26.md",
    "MEMORY.md",
]
memory_status = [{"name": n, "exists": (memory_dir / n).exists(),
                  "size": (memory_dir / n).stat().st_size if (memory_dir / n).exists() else None}
                 for n in campello_memories]

# 7. New artifacts created this session
new_artifacts = [
    "tmp/campello_method_lockin.md",
    "tmp/campello_variable_lockin.md",
    "tmp/campello_table1_anchor_2026_05_26.json",
    "tmp/campello_claudeweb_88vars_2026_05_26.md",
    "tmp/campello_var_anchor_REVERIFY_2026_05_26.md",
    "tmp/campello_var_anchor_FAILS_summary.md",
    "tmp/gitnexus_vs_graphify_bench_2026_05_26.md",
    "docs/superpowers/specs/2026-05-26-campello-rewrite-spec.md",
    "AGENTS.md",
    "CLAUDE.md",
    ".gitnexus/",
]
new_artifacts_status = [{"path": p, **(stat_or_none(ROOT / p) or {"exists": False})}
                         for p in new_artifacts]

# Emit markdown
def fmt_bool(b): return "PASS" if b else "FAIL"
lines = ["# Safety audit — pre-rewrite continue gate",
         "",
         f"Generated: 2026-05-26 by `tmp/safety_audit_2026_05_26.py`",
         f"Git HEAD: `{git_head[:12]}` (branch: `{git_branch}`)",
         "",
         "## 1. Locked-truth artifacts (rewrite source of truth)", ""]
for s in locked_status:
    lines.append(f"- `{s['path']}` — exists: {fmt_bool(s['exists'])} | size: {s['size']} bytes | sha256[:16]: `{s['sha256_16']}`")

lines += ["", "## 2. F1D shared infra files (read-only, must not change)", ""]
for s in infra_status:
    lines.append(f"- `{s['path']}` — exists: {fmt_bool(s.get('exists', s.get('size') is not None))} | size: {s.get('size')} | mtime: {s.get('mtime')}")

lines += ["", "## 3. Git uncommitted state", ""]
lines.append(f"- Modified ({len(modified)}): " + (", ".join(f"`{f}`" for f in modified[:20]) if modified else "none"))
if len(modified) > 20:
    lines.append(f"  - … +{len(modified)-20} more")
lines.append(f"- Untracked ({len(untracked)}): " + (", ".join(f"`{f}`" for f in untracked[:25]) if untracked else "none"))
if len(untracked) > 25:
    lines.append(f"  - … +{len(untracked)-25} more")
lines.append(f"- Deleted ({len(deleted)}): " + (", ".join(f"`{f}`" for f in deleted) if deleted else "none"))

lines += ["", "## 4. .gitnexus/ gitignore status (143 MB lbug must NOT enter repo)", ""]
lines.append(f"- Root `.gitignore` excludes `.gitnexus/`: {fmt_bool(gitnexus_ignored)}")
lines.append(f"- `.gitnexus/.gitignore` (auto-written by gitnexus): exists={local_gitignore.exists()}; content: `{local_gitnexus_ignored_text.strip()}`")
lines.append(f"- Risk: if root `.gitignore` doesn't exclude AND `.gitnexus/.gitignore` doesn't either, the 143 MB binary will be staged on `git add`.")

lines += ["", "## 5. Rewrite-scope files (must still exist; rewrite deletes them in Phase 9 cutover)", ""]
lines.append(f"- LIVE `brexit_*.py` builders ({len(brexit_files)}):")
for f in brexit_files:
    lines.append(f"  - `{f}`")
lines.append(f"- `scripts/campello_rebuild/*.py` files ({len(campello_rebuild)}):")
for f in campello_rebuild[:30]:
    lines.append(f"  - `{f}`")
if len(campello_rebuild) > 30:
    lines.append(f"  - … +{len(campello_rebuild)-30} more")

lines += ["", "## 6. Campello-session memory files", ""]
for m in memory_status:
    lines.append(f"- `{m['name']}` — exists: {fmt_bool(m['exists'])} | size: {m['size']}")

lines += ["", "## 7. New artifacts created this session", ""]
for s in new_artifacts_status:
    lines.append(f"- `{s['path']}` — exists: {fmt_bool(s.get('exists', s.get('size') is not None))} | size: {s.get('size')}")

# Overall
all_locked = all(s["exists"] for s in locked_status)
all_infra = all(s.get("size") is not None for s in infra_status)
all_memory = all(m["exists"] for m in memory_status)
spec_exists = (ROOT / "docs/superpowers/specs/2026-05-26-campello-rewrite-spec.md").exists()

lines += ["", "## Verdict", ""]
lines.append(f"- Locked artifacts present: {fmt_bool(all_locked)}")
lines.append(f"- F1D infra files present: {fmt_bool(all_infra)}")
lines.append(f"- Campello memory present: {fmt_bool(all_memory)}")
lines.append(f"- Rewrite spec present: {fmt_bool(spec_exists)}")
lines.append(f"- .gitnexus/ gitignore: {'OK (excluded)' if gitnexus_ignored else 'ACTION_NEEDED (add `.gitnexus/` to root .gitignore before any git add)'}")
lines.append("")
lines.append("**Safe-to-continue checks:**")
go = all_locked and all_infra and all_memory and spec_exists
lines.append(f"- All-green for proceeding to Phase 1 (sample + panel scaffolding): **{'YES' if go else 'NO'}**")
if not gitnexus_ignored:
    lines.append(f"- BUT: must add `.gitnexus/` to root `.gitignore` first (low-risk one-line edit).")

OUT.write_text("\n".join(lines), encoding="utf-8")
print(OUT)
print(f"Locked: {sum(s['exists'] for s in locked_status)}/{len(locked_status)}")
print(f"Infra: {sum(s.get('size') is not None for s in infra_status)}/{len(infra_status)}")
print(f"Memory: {sum(m['exists'] for m in memory_status)}/{len(memory_status)}")
print(f"Modified files: {len(modified)}, Untracked: {len(untracked)}, Deleted: {len(deleted)}")
print(f".gitnexus gitignored: {gitnexus_ignored}")
print(f"Verdict: {'SAFE' if go and gitnexus_ignored else 'ACTION_NEEDED'}")
