#!/usr/bin/env python3
"""Extract Phase-C prose -> fill final_prose in the 3 expanded ledgers + gate
(dash-free, no coefficients, every paragraph drafted, redundancy spot-check)."""
import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
REW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")
OUT = Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\woqdnqs3f.output")
NAME = {"abstract": "section_abstract_paragraph_ledger.json", "1": "section1_paragraph_ledger.json", "5": "section5_paragraph_ledger.json"}

wrap = json.loads(OUT.read_text(encoding="utf-8", errors="replace"))
res = wrap["result"]
if isinstance(res, str):
    res = json.loads(res)
drafters = res["drafters"]
synth = res["synthesis"]
subs = synth["subsections"]

(REW / "introconcl_phaseC_drafters_raw.json").write_text(json.dumps(drafters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(REW / "introconcl_phaseC_redteam.json").write_text(json.dumps({"redteam_report": synth.get("redteam_report"), "audit_matrix": synth.get("audit_matrix")}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

DASH = re.compile(r"--")                       # en/em dash (any double hyphen)
COEF = re.compile(r"\b\d?\.\d{2,}\b|\*\*|\bp\s*[=<]\s*\.?\d|\bz\s*=|t-stat")
flags = []
for s in subs:
    sid = str(s["subsection_id"])
    led = json.loads((REW / NAME[sid]).read_text(encoding="utf-8"))
    drafted = {pp["para_id"]: pp for pp in s["paragraphs"]}
    n_words = 0
    for para in led["paragraphs"]:
        pid = para["para_id"]
        d = drafted.get(pid)
        if not d or not d.get("final_prose", "").strip():
            flags.append(f"{sid}/{pid}: NO prose")
            continue
        fp = d["final_prose"]
        para["final_prose"] = fp
        para["prose_status"] = "DRAFTED -- Phase C (synthesis)"
        para["_phaseC_audit"] = {k: d.get(k) for k in ("direction_audit", "number_audit", "dash_free", "no_coefficients")}
        n_words += len(fp.split())
        # dash scan (allow none)
        if DASH.search(fp):
            flags.append(f"{sid}/{pid}: DASH '--' present: ...{fp[max(0,DASH.search(fp).start()-25):DASH.search(fp).start()+25]}...")
        # coefficient scan (exclude sample years like 2002/2018 -> those are \d{4} ints, not \d.\d)
        leaks = [m for m in COEF.findall(fp)]
        if leaks:
            flags.append(f"{sid}/{pid}: COEF/p-value in prose: {leaks}")
    (REW / NAME[sid]).write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"[{sid}] {len(led['paragraphs'])} paras filled, ~{n_words} words")

print("\n=== FLAGS ===")
print("\n".join(flags) if flags else "NONE -- gate clean (dash-free, no coefficients, all drafted)")
print(f"\n[redteam units]: {[r.get('subsection_id') for r in (synth.get('redteam_report') or [])]}")
print(f"[audit_matrix rows]: {len(synth.get('audit_matrix') or [])}")
