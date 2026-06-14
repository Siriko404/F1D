# Extract Phase-A workflow output -> write the 5 Sec 3/4 subsection-plan files + the red-team audit file.
# JSON-aware, assert-guarded, idempotent. Report-first: with --report it only prints structure; with --write it writes.
import json, sys, pathlib, html

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = pathlib.Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\w5hnpmc6t.output")
DEST = ROOT / "docs/Thesis/rewrite"

raw = OUT.read_text(encoding="utf-8")
env = json.loads(raw)                      # asserts the file is complete, valid JSON
print("TOP-LEVEL KEYS:", list(env.keys()))

# Locate the workflow return {planners, synthesis}. It may be the envelope itself or under a key.
def find_return(e):
    if isinstance(e, dict) and "synthesis" in e and "planners" in e:
        return e
    if isinstance(e, dict):
        for k in ("result", "output", "return", "value", "data"):
            v = e.get(k)
            if isinstance(v, str):
                try: v = json.loads(v)
                except Exception: pass
            r = find_return(v) if isinstance(v, dict) else None
            if r: return r
    return None

ret = find_return(env)
assert ret is not None, f"could not find {{planners,synthesis}} in envelope keys {list(env.keys())}"
planners = ret["planners"]
synth = ret["synthesis"]
print("planners:", len(planners), "| synthesis keys:", list(synth.keys()))

subs = synth["subsections"]
ids = [s["subsection_id"] for s in subs]
print("synthesis subsection_ids:", ids)
EXPECTED = ["3.1", "3.2", "3.3", "3.4", "4.1"]
assert sorted(ids) == sorted(EXPECTED), f"expected {EXPECTED}, got {ids}"

# entity check
has_ent = "&gt;" in raw or "&amp;" in raw or "&lt;" in raw
print("HTML entities present in raw:", has_ent)

def unescape(o):
    if isinstance(o, str): return html.unescape(o)
    if isinstance(o, list): return [unescape(x) for x in o]
    if isinstance(o, dict): return {k: unescape(v) for k, v in o.items()}
    return o

# per-subsection report
print("\n--- SYNTHESIS (final, red-teamed) per subsection ---")
for s in subs:
    chain = s.get("proposition_chain", [])
    miss = [p.get("prop_id") for p in chain if not p.get("reason") or not p.get("evidence")]
    print(f"  {s['subsection_id']:4} {s['title'][:46]:46} props={len(chain):2} "
          f"claims={s.get('delivers_claims')} tables={len(s.get('tables_referenced',[]))} "
          f"gaps={len(s.get('coverage',{}).get('gaps',[]))} reason/ev-missing={len(miss)}")

# red-team report summary
rr = synth.get("redteam_report", [])
print("\n--- RED-TEAM FLAWS (found + fixed) ---")
sev_tot = {"CRITICAL":0,"MAJOR":0,"MINOR":0}
for r in rr:
    by = {"CRITICAL":0,"MAJOR":0,"MINOR":0}
    for f in r.get("flaws_found", []):
        by[f.get("severity","MINOR")] = by.get(f.get("severity","MINOR"),0)+1
        sev_tot[f.get("severity","MINOR")] = sev_tot.get(f.get("severity","MINOR"),0)+1
    print(f"  {r['subsection_id']:4} flaws C/Ma/Mi = {by['CRITICAL']}/{by['MAJOR']}/{by['MINOR']}  "
          f"synthesis_decisions={len(r.get('synthesis_decisions',[]))}")
print("  TOTAL flaws C/Ma/Mi =", f"{sev_tot['CRITICAL']}/{sev_tot['MAJOR']}/{sev_tot['MINOR']}")

# coverage matrix
cm = synth.get("coverage_matrix", [])
print("\n--- COVERAGE MATRIX ---")
for c in cm:
    print(f"  {str(c.get('claim')):8} -> {str(c.get('subsection')):5} {c.get('tables')} [{c.get('status')}]")

gn = synth.get("global_notes", [])
print("\nglobal_notes:", len(gn))

if "--write" in sys.argv:
    syn = unescape(synth) if has_ent else synth
    plan = unescape(planners) if has_ent else planners
    # 5 subsection-plan files (from the synthesized, red-teamed subsections)
    for s in syn["subsections"]:
        fp = DEST / f"section{s['subsection_id']}_subsection_plan.json"
        fp.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        json.loads(fp.read_text(encoding="utf-8"))   # reload-validate
        print("WROTE", fp.name)
    # red-team audit file (report + coverage matrix + global notes)
    audit = {"redteam_report": syn.get("redteam_report", []),
             "coverage_matrix": syn.get("coverage_matrix", []),
             "global_notes": syn.get("global_notes", [])}
    fa = DEST / "section34_phaseA_redteam.json"
    fa.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(fa.read_text(encoding="utf-8"))
    print("WROTE", fa.name)
    # raw 3 planners archive (provenance)
    fp = DEST / "section34_phaseA_planners_raw.json"
    fp.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(fp.read_text(encoding="utf-8"))
    print("WROTE", fp.name)
else:
    print("\n(report only; pass --write to write files)")
