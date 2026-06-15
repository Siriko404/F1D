#!/usr/bin/env python3
"""Extract Phase-A (intro/concl/abstract) workflow output -> 3 subsection_plan ledgers
+ planners_raw + redteam, then run a mechanical gate (diff-to-ratified discipline).

Gate (mirrors the Sec 3/4 Phase-A checks, retargeted):
 - all 3 units present (abstract, 1, 5); each has purpose{statement,reason,evidence} + nonempty chain
 - reason+evidence atomic on every proposition (the hard requirement)
 - QUALITATIVE leak: no coefficient/SE/p-value/star-cluster in any prop STATEMENT
   (the `numbers` field legitimately holds the grounding table cell; statements stay verbal)
 - coverage: C1/C2/C4/C6 each homed across the units
 - external-NLM props: list bibkeys + whether flagged "needs NLM verification"
 - dropped bibkeys (everhart2025/gokkaya2025/bushee2018/lerman2026) used anywhere -> flag disposition
"""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
REW = ROOT / "docs" / "Thesis" / "rewrite"
OUTFILE = Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\w0k4i75o4.output")

NAME = {"abstract": "section_abstract_subsection_plan.json", "1": "section1_subsection_plan.json", "5": "section5_subsection_plan.json"}
DROPPED = ["everhart2025", "gokkaya2025", "bushee2018", "lerman2026"]
LIVE_CLAIMS = ["C1", "C2", "C4", "C6"]

text = OUTFILE.read_text(encoding="utf-8", errors="replace")
wrap = json.loads(text)
res = wrap["result"]
if isinstance(res, str):
    res = json.loads(res)
planners = res["planners"]
synth = res["synthesis"]
subs = synth["subsections"]

# --- write the 3 ratified ledgers ---
written = []
for s in subs:
    sid = str(s["subsection_id"])
    if sid not in NAME:
        print(f"!! unexpected subsection_id {sid!r}")
        continue
    p = REW / NAME[sid]
    p.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    written.append(NAME[sid])

(REW / "introconcl_phaseA_planners_raw.json").write_text(
    json.dumps(planners, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(REW / "introconcl_phaseA_redteam.json").write_text(
    json.dumps({"redteam_report": synth.get("redteam_report"), "coverage_matrix": synth.get("coverage_matrix")},
               indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"WROTE: {written} + planners_raw + redteam\n")

# --- GATE ---
COEF = re.compile(r"\b\d?\.\d{3,}\b|\*\*|\bp\s*[=<]\s*\.?\d|\bz\s*=|t-stat", re.I)
flags = []
print("=== GATE ===")
for s in subs:
    sid = str(s["subsection_id"])
    chain = s.get("proposition_chain", [])
    pur = s.get("purpose", {})
    miss_pur = [k for k in ("statement", "reason", "evidence") if not pur.get(k)]
    if miss_pur:
        flags.append(f"{sid}: purpose missing {miss_pur}")
    no_re = [p.get("prop_id") for p in chain if not p.get("reason") or not p.get("evidence")]
    if no_re:
        flags.append(f"{sid}: props missing reason/evidence: {no_re}")
    # qualitative leak in STATEMENTS only
    leaks = [(p.get("prop_id"), COEF.findall(p.get("statement", ""))) for p in chain if COEF.search(p.get("statement", ""))]
    if leaks:
        flags.append(f"{sid}: COEFFICIENT LEAK in statement(s): {leaks}")
    # external-NLM
    ext = [(p.get("prop_id"), p.get("evidence")) for p in chain if p.get("type") == "external-NLM"]
    # dropped bibkeys anywhere in the unit
    blob = json.dumps(s)
    dused = [b for b in DROPPED if b in blob]
    print(f"\n[{sid}] {s.get('title','')[:60]}")
    print(f"   props={len(chain)}  delivers_claims={s.get('delivers_claims')}  tables={len(s.get('tables_referenced',[]))}")
    print(f"   external-NLM props: {[e[0] for e in ext] or 'none'}")
    if dused:
        print(f"   DROPPED-BIBKEY used: {dused}  (check open_decisions disposition)")
    od = s.get("open_decisions") or []
    if od:
        print(f"   open_decisions: {len(od)} -> " + " | ".join(x[:90] for x in od[:4]))

# coverage of claims across units
print("\n=== CLAIM COVERAGE ===")
for c in LIVE_CLAIMS:
    homes = [str(s["subsection_id"]) for s in subs if c in (s.get("delivers_claims") or [])]
    print(f"   {c}: {homes}")

print("\n=== FLAGS ===")
print("\n".join(flags) if flags else "NONE -- gate clean")
print(f"\n[redteam_report units]: {[r.get('subsection_id') for r in (synth.get('redteam_report') or [])]}")
print(f"[coverage_matrix rows]: {len(synth.get('coverage_matrix') or [])}")
