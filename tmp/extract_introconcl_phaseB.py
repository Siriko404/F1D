#!/usr/bin/env python3
"""Extract Phase-B (intro/concl/abstract) output -> 3 paragraph_ledger files + raw + redteam,
then gate: allocation completeness vs the ratified Phase-A chains + qualitative + format fidelity."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
REW = ROOT / "docs" / "Thesis" / "rewrite"
OUTFILE = Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\wbtb2l2uu.output")

PLAN = {"abstract": "section_abstract_subsection_plan.json", "1": "section1_subsection_plan.json", "5": "section5_subsection_plan.json"}
LEDG = {"abstract": "section_abstract_paragraph_ledger.json", "1": "section1_paragraph_ledger.json", "5": "section5_paragraph_ledger.json"}

wrap = json.loads(OUTFILE.read_text(encoding="utf-8", errors="replace"))
res = wrap["result"]
if isinstance(res, str):
    res = json.loads(res)
planners = res["planners"]
synth = res["synthesis"]
subs = synth["subsections"]

written = []
for s in subs:
    sid = str(s["subsection_id"])
    if sid in LEDG:
        (REW / LEDG[sid]).write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        written.append(LEDG[sid])
(REW / "introconcl_phaseB_planners_raw.json").write_text(json.dumps(planners, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(REW / "introconcl_phaseB_redteam.json").write_text(json.dumps({"redteam_report": synth.get("redteam_report"), "allocation_matrix": synth.get("allocation_matrix")}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"WROTE: {written} + planners_raw + redteam\n")

COEF = re.compile(r"\b\d?\.\d{3,}\b|\*\*|\bp\s*[=<]\s*\.?\d|\bz\s*=", re.I)
flags = []
print("=== GATE ===")
for s in subs:
    sid = str(s["subsection_id"])
    plan = json.loads((REW / PLAN[sid]).read_text(encoding="utf-8"))
    phaseA_ids = [p["prop_id"] for p in plan.get("proposition_chain", [])]
    paras = s.get("paragraphs", [])
    homed = {}
    for para in paras:
        # format fidelity
        if para.get("final_prose", "") != "":
            flags.append(f"{sid}/{para.get('para_id')}: final_prose not empty")
        if "BLOCKED" not in (para.get("prose_status") or ""):
            flags.append(f"{sid}/{para.get('para_id')}: prose_status not BLOCKED")
        intent = para.get("intent", {})
        if not (intent.get("statement") and intent.get("reason") and intent.get("evidence")):
            flags.append(f"{sid}/{para.get('para_id')}: intent missing reason/evidence")
        for pp in para.get("proposition_chain", []):
            src = pp.get("from_phaseA_prop")
            if src and src != "new-transition":
                homed[src] = homed.get(src, 0) + 1
            if not pp.get("reason") or not pp.get("evidence"):
                flags.append(f"{sid}/{para.get('para_id')}/{pp.get('prop_id')}: prop missing reason/evidence")
            st = pp.get("statement", "")
            if COEF.search(st):
                flags.append(f"{sid}/{para.get('para_id')}/{pp.get('prop_id')}: COEF LEAK -> {COEF.findall(st)}")
            if re.search(r"must host", st, re.I):
                flags.append(f"{sid}/{para.get('para_id')}/{pp.get('prop_id')}: 'must host' (calls are voluntary -- §17 scar) -> Phase C watch")
    orphans = [a for a in phaseA_ids if a not in homed]
    dups = {a: n for a, n in homed.items() if n > 1}
    print(f"\n[{sid}] paras={len(paras)}  phaseA_props={len(phaseA_ids)}  homed={len(homed)}")
    if orphans:
        flags.append(f"{sid}: ORPHANED Phase-A props (not allocated): {orphans}")
    if dups:
        print(f"   split props (homed >1, allowed w/ reason): {dups}")
    extra = [h for h in homed if h not in phaseA_ids]
    if extra:
        flags.append(f"{sid}: from_phaseA_prop refers to UNKNOWN Phase-A id: {extra}")

print("\n=== FLAGS ===")
print("\n".join(flags) if flags else "NONE -- gate clean")
print(f"\n[redteam units]: {[r.get('subsection_id') for r in (synth.get('redteam_report') or [])]}")
print(f"[allocation_matrix rows]: {len(synth.get('allocation_matrix') or [])}")
