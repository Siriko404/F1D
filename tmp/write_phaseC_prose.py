# Extract Phase-C prose -> fill final_prose into the 5 paragraph ledgers, WITH the advisor's prose gate.
# Gate (mechanical, NOT the red-team's number_audit_matrix self-report):
#   (a) DASH scan: no '--'/'---' or unicode en/em dash in any final_prose (dash-free rule)
#   (b) NON-EMPTY: every paragraph's final_prose is non-empty
#   (c) PROP COVERAGE: delivers_props covers the paragraph's Phase-B proposition_chain
#   (d) NUMBER DIFF: every decimal token in the prose traces to that paragraph's Phase-B numbers[] (table-verified)
# Report-first; pass --write to fill the ledgers + write audit/raw.
import json, sys, re, pathlib, html

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = pathlib.Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\wcorwzqvv.output")
DEST = ROOT / "docs/Thesis/rewrite"
IDS = ["3.1", "3.2", "3.3", "3.4", "4.1"]
DEC = re.compile(r"\d*\.\d+")   # catches .039 and 0.039 and 32.7
DASH = re.compile(r"--+|–|—")   # two+ hyphens, en-dash, em-dash
def norm(x): return re.sub(r"^0+(?=\.)", "", x)   # strip leading zeros: 0.039 -> .039
SECREF = {".1", ".2", ".3", ".4", ".5"}           # x.y section refs normalize to .1.. ; handled below
SECTIONS = {"2.1", "2.2", "2.3", "2.4", "2.5", "3.1", "3.2", "3.3", "3.4", "4.1", "2.0"}
SIG = {".01", ".05", ".10", ".1"}                 # conventional significance thresholds

raw = OUT.read_text(encoding="utf-8")
env = json.loads(raw)

def find_return(e):
    if isinstance(e, dict) and "synthesis" in e and ("drafters" in e or "planners" in e):
        return e
    if isinstance(e, dict):
        for k in ("result", "output", "return", "value", "data"):
            v = e.get(k)
            if isinstance(v, str):
                try: v = json.loads(v)
                except Exception: pass
            if isinstance(v, dict):
                r = find_return(v)
                if r: return r
    return None

ret = find_return(env)
assert ret is not None, "could not find {drafters,synthesis}"
drafters = ret.get("drafters") or ret.get("planners")
synth = ret["synthesis"]
subs = synth["subsections"]
print("drafters:", len(drafters), "| synthesis subs:", [s["subsection_id"] for s in subs])
assert sorted(s["subsection_id"] for s in subs) == sorted(IDS)

# Phase-B ledgers: para_id -> {prop_ids, decimals}
pb = {}
for sid in IDS:
    led = json.loads((DEST / f"section{sid}_paragraph_ledger.json").read_text(encoding="utf-8"))
    for para in led["paragraphs"]:
        dec = set()
        for p in para.get("proposition_chain", []):
            for t in p.get("numbers", []):
                dec |= {norm(x) for x in DEC.findall(t)}
        pb[para["para_id"]] = {"props": [p["prop_id"] for p in para.get("proposition_chain", [])], "dec": dec}

# --- GATE ---
dash_hits, empty, cov_gaps, num_extra = [], [], [], []
total = 0
for s in subs:
    for para in s["paragraphs"]:
        total += 1
        pid = para.get("para_id")
        prose = para.get("final_prose", "") or ""
        if not prose.strip():
            empty.append(pid)
        for m in DASH.finditer(prose):
            ctx = prose[max(0, m.start()-25):m.start()+25]
            dash_hits.append((pid, repr(ctx)))
        b = pb.get(pid, {"props": [], "dec": set()})
        miss = [x for x in b["props"] if x not in set(para.get("delivers_props", []))]
        if miss:
            cov_gaps.append((pid, miss))
        prose_dec = {norm(x) for x in DEC.findall(prose)}
        extra = prose_dec - b["dec"] - SIG - {norm(s) for s in SECTIONS} - SECTIONS
        if extra:
            num_extra.append((pid, sorted(extra), sorted(b["dec"])))

print(f"\n=== PROSE GATE (paragraphs={total}) ===")
print(f"(a) DASH violations (-- / en / em): {len(dash_hits)}")
for v in dash_hits[:15]: print("    DASH", v[0], v[1])
print(f"(b) EMPTY final_prose: {len(empty)} {empty}")
print(f"(c) PROP-COVERAGE gaps (chain prop not in delivers_props): {len(cov_gaps)}")
for v in cov_gaps[:15]: print("    COV", v)
print(f"(d) NUMBER-not-in-ledger (decimal in prose not in Phase-B numbers): {len(num_extra)}")
for v in num_extra[:20]: print("    NUM", v[0], "extra", v[1], "| ledger", v[2])

if "--write" in sys.argv:
    has_ent = "&gt;" in raw or "&amp;" in raw or "&lt;" in raw
    def un(o):
        if isinstance(o, str): return html.unescape(o)
        if isinstance(o, list): return [un(x) for x in o]
        if isinstance(o, dict): return {k: un(v) for k, v in o.items()}
        return o
    prose_by_pid = {}
    for s in subs:
        for para in s["paragraphs"]:
            prose_by_pid[para["para_id"]] = un(para) if has_ent else para
    for sid in IDS:                                  # fill final_prose into each paragraph ledger
        fp = DEST / f"section{sid}_paragraph_ledger.json"
        led = json.loads(fp.read_text(encoding="utf-8"))
        for para in led["paragraphs"]:
            src = prose_by_pid.get(para["para_id"])
            if src is not None:
                para["final_prose"] = src.get("final_prose", "")
                para["number_audit"] = src.get("number_audit", [])
                para["prose_status"] = "DRAFTED (Phase C); gate-passed; pending .tex assembly (Phase D)"
        fp.write_text(json.dumps(led, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        json.loads(fp.read_text(encoding="utf-8"))
        print("FILLED", fp.name)
    aud = {"redteam_report": un(synth.get("redteam_report", [])) if has_ent else synth.get("redteam_report", []),
           "number_audit_matrix": un(synth.get("number_audit_matrix", [])) if has_ent else synth.get("number_audit_matrix", []),
           "global_notes": synth.get("global_notes", [])}
    (DEST / "section34_phaseC_redteam.json").write_text(json.dumps(aud, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("WROTE section34_phaseC_redteam.json")
    (DEST / "section34_phaseC_drafters_raw.json").write_text(json.dumps(un(drafters) if has_ent else drafters, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("WROTE section34_phaseC_drafters_raw.json")
else:
    print("\n(report only; pass --write to fill ledgers)")
