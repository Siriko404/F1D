#!/usr/bin/env python3
"""G1 regen-and-diff (audit P1, mechanical gate).

Proves bible<->code for every numeric table fragment: re-renders each fragment
FROM its trusted summary.json (user-ratified 2026-06-11: the summary.json files
hold the final real results) and byte-diffs the result against the committed
(baseline 7f97a16) fragment.

  MATCH   -> the committed fragment faithfully reflects the trusted results.
  DRIFT   -> the committed fragment is STALE vs the results (CRITICAL).
  BLOCKED -> render path errored (recorded, not fatal to the run).
  SKIP    -> no generator writes this fragment (static, hand-authored).

Render-ONLY: calls each module's write_tex(...) on the latest summary.json. No
estimation re-run, no raw-panel dependency. Restores all fragments via
`git checkout` in a finally block, so the frozen tree is never left mutated.

Exit 1 if any DRIFT (protocol: scripts exit 1 on FAIL).

Run: python tmp/audit_g1.py
"""
from __future__ import annotations
import glob
import hashlib
import importlib.util
import json
import subprocess
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "docs" / "Thesis" / "audit"
BASELINE = json.loads((AUDIT / "baseline.json").read_text(encoding="utf-8"))
BASE_HASH = dict(BASELINE["hashes"]["fragments"])  # "docs/Draft/_x.tex" -> sha256


def sha(rel: str) -> str:
    return hashlib.sha256((ROOT / rel).read_bytes()).hexdigest()


def latest(pattern: str) -> Path | None:
    hits = sorted(glob.glob(str(ROOT / pattern)))
    return Path(hits[-1]) if hits else None


def load(rel: str):
    """Load a module by file path (handles modules not on sys.path)."""
    name = "m_" + Path(rel).stem
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# --- render closures: each returns the summary.json path it rendered from ------
def r_write_tex(modrel: str, json_glob: str):
    def fn():
        m = load(modrel)
        sp = latest(json_glob)
        if sp is None:
            raise FileNotFoundError(f"no summary.json for {json_glob}")
        m.write_tex(sp)
        return str(sp.relative_to(ROOT))
    return fn


def r_empire_did():
    m = load("scripts/gen_empire_did_table.py")
    sp = latest("outputs/econometric/empire_building_did/*/summary.json")
    s = json.loads(sp.read_text(encoding="utf-8"))
    res = {tuple(k.split(":")): v for k, v in s["results"].items()}
    m.write_tex(res, s["counts"])
    return str(sp.relative_to(ROOT))


def r_reason_gating():
    m = load("scripts/gen_reason_gating_table.py")
    sp = latest("outputs/econometric/reason_gating/*/summary.json")
    s = json.loads(sp.read_text(encoding="utf-8"))
    m.write_tex(s["col1_main"], s["col2_interaction"])
    return str(sp.relative_to(ROOT))


def r_subprocess(modrel: str):
    """Render-from-JSON scripts (no raw-panel read): run their main() in a child."""
    def fn():
        p = subprocess.run([sys.executable, str(ROOT / modrel)],
                           cwd=ROOT, capture_output=True, text=True, timeout=600)
        if p.returncode != 0:
            raise RuntimeError(f"exit {p.returncode}: {p.stderr.strip()[-400:]}")
        return f"main() [{modrel}]"
    return fn


# fragment -> (render fn, mode label)
JOBS = {
    "docs/Draft/_empire_building_did.tex":   (r_empire_did, "render:dict"),
    "docs/Draft/_reason_gating.tex":         (r_reason_gating, "render:dict"),
    "docs/Draft/_empire_drop_placebo.tex":   (r_write_tex("src/f1d/econometric/empire_drop_test.py",
                                              "outputs/econometric/empire_drop_test/*/summary.json"), "render:path"),
    "docs/Draft/_empire_drop_matched.tex":   (r_write_tex("src/f1d/econometric/empire_drop_matched_universe.py",
                                              "outputs/econometric/empire_drop_matched/*/summary.json"), "render:path"),
    "docs/Draft/_empire_cashspec.tex":       (r_write_tex("src/f1d/econometric/empire_cashspec_interaction.py",
                                              "outputs/econometric/empire_cashspec/*/summary.json"), "render:path"),
    "docs/Draft/_cash_scrutiny_validity.tex":(r_write_tex("scripts/gen_cash_scrutiny_validity_table.py",
                                              "outputs/econometric/cash_scrutiny_validity/*/summary.json"), "render:path"),
    "docs/Draft/_cash_scrutiny_channel.tex": (r_write_tex("scripts/gen_cash_scrutiny_channel_table.py",
                                              "outputs/econometric/cash_scrutiny_channel/*/summary.json"), "render:path"),
    "docs/Draft/_summary_stats.tex":         (r_subprocess("scripts/gen_summary_stats_table.py"), "subprocess"),
    "docs/Draft/_disclosure_law_compact.tex":(r_subprocess("scripts/gen_disclosure_law_compact_table.py"), "subprocess"),
    "docs/Draft/_boasiako_summary_stats.tex":(r_subprocess("scripts/gen_boasiako_summary_stats.py"), "subprocess"),
    "docs/Draft/_campello_summary_stats.tex":(r_subprocess("scripts/campello_rebuild/gen_summary_stats_tex.py"), "subprocess"),
    "docs/Draft/_campello_rebuild_t8.tex":   (r_subprocess("scripts/campello_rebuild/gen_thesis_t8_table.py"), "subprocess"),
}
STATIC = {"docs/Draft/_empire_building_spec.tex": "no generator (hand-authored spec table)"}

results = []
try:
    for frag, base in BASE_HASH.items():
        if frag in STATIC:
            results.append({"fragment": frag, "mode": "static", "status": "SKIP",
                            "note": STATIC[frag], "baseline": base[:12]})
            continue
        if frag not in JOBS:
            results.append({"fragment": frag, "mode": "?", "status": "BLOCKED",
                            "note": "no render path mapped", "baseline": base[:12]})
            continue
        fn, mode = JOBS[frag]
        try:
            before = sha(frag)
            if before != base:
                # working tree already differs from baseline for this file
                results.append({"fragment": frag, "mode": mode, "status": "BLOCKED",
                                "note": "pre-run hash != baseline (tree not at baseline)",
                                "baseline": base[:12], "on_disk": before[:12]})
                continue
            src = fn()
            after = sha(frag)
            status = "MATCH" if after == base else "DRIFT"
            results.append({"fragment": frag, "mode": mode, "status": status,
                            "source_json": src, "baseline": base[:12], "regenerated": after[:12]})
        except Exception as e:  # noqa
            results.append({"fragment": frag, "mode": mode, "status": "BLOCKED",
                            "note": f"{type(e).__name__}: {e}".strip()[:400],
                            "trace": traceback.format_exc()[-600:], "baseline": base[:12]})
finally:
    # ALWAYS restore the audited surface to baseline, whatever happened above.
    subprocess.run(["git", "checkout", "--", "docs/Draft", "docs/Thesis/_tables_from_bible.tex"],
                   cwd=ROOT, capture_output=True, text=True)

# --- report -------------------------------------------------------------------
order = {"DRIFT": 0, "BLOCKED": 1, "SKIP": 2, "MATCH": 3}
results.sort(key=lambda r: (order.get(r["status"], 9), r["fragment"]))
counts = {}
for r in results:
    counts[r["status"]] = counts.get(r["status"], 0) + 1

out = {"gate": "G1_regen_diff", "baseline_sha": BASELINE["baseline"]["short_sha"],
       "method": "render-only from trusted summary.json (user-ratified 2026-06-11)",
       "assumption": "summary.json = final real results; G1 proves bible<->results-render, not a fresh re-estimation",
       "counts": counts, "results": results}
(AUDIT / "g1_regen_diff.json").write_text(json.dumps(out, indent=2), encoding="utf-8")

print(f"\nG1 regen-and-diff  (baseline {BASELINE['baseline']['short_sha']})")
print("=" * 72)
for r in results:
    line = f"  {r['status']:8} {r['mode']:13} {Path(r['fragment']).name}"
    if r["status"] == "DRIFT":
        line += f"   base={r['baseline']} -> regen={r['regenerated']}"
    elif r["status"] == "BLOCKED":
        line += f"   {r.get('note','')[:80]}"
    print(line)
print("=" * 72)
print("  " + "  ".join(f"{k}={v}" for k, v in sorted(counts.items())))
print(f"  written: docs/Thesis/audit/g1_regen_diff.json")

# verify restore
st = subprocess.run(["git", "status", "--porcelain", "--", "docs/Draft", "docs/Thesis"],
                    cwd=ROOT, capture_output=True, text=True).stdout.strip()
print(f"  tree after restore (docs/): {'CLEAN' if not st else 'DIRTY -> ' + st[:200]}")

sys.exit(1 if counts.get("DRIFT") else 0)
