# Extract Phase-B output -> write the 5 paragraph ledgers, WITH the advisor's fidelity gate.
# Gate (diff-to-ratified, NOT trusting the red-team's allocation_matrix):
#   (a) FILENAME: section{N}_paragraph_ledger.json   (Phase C manifest + 2.x convention require this)
#   (b) set-completeness: every Phase-A prop_id is covered by some from_phaseA_prop; flag orphans + multi-homed
#   (c) force final_prose=="" and prose_status BLOCKED on every paragraph
#   (d) per-prop fidelity: every numeric token / register_lock in a Phase-B prop traces to its from_phaseA_prop source
# Report-first: default prints the gate; pass --write to write files.
import json, sys, re, pathlib, html
from collections import Counter, defaultdict

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
OUT = pathlib.Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\d480c84a-ac35-4372-980f-ac2d3bbc8380\tasks\wvtxin0ip.output")
DEST = ROOT / "docs/Thesis/rewrite"
IDS = ["3.1", "3.2", "3.3", "3.4", "4.1"]
NUM = re.compile(r"-?\d+\.\d+")

raw = OUT.read_text(encoding="utf-8")
env = json.loads(raw)

def find_return(e):
    if isinstance(e, dict) and "synthesis" in e and "planners" in e:
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
assert ret is not None, "could not find {planners,synthesis}"
planners, synth = ret["planners"], ret["synthesis"]
subs = synth["subsections"]
print("planners:", len(planners), "| synthesis subs:", [s["subsection_id"] for s in subs])
assert sorted(s["subsection_id"] for s in subs) == sorted(IDS)

# --- load Phase-A source props (the ratified ceiling) ---
phaseA = {}
for sid in IDS:
    plan = json.loads((DEST / f"section{sid}_subsection_plan.json").read_text(encoding="utf-8"))
    for p in plan["proposition_chain"]:
        nums = set()
        for t in p.get("numbers", []):
            nums |= set(NUM.findall(t))
        phaseA[p["prop_id"]] = {"numbers": nums, "locks": set(p.get("register_locks", []))}
print(f"Phase-A props loaded: {len(phaseA)}")

# --- collect Phase-B coverage + per-prop ---
covered = Counter()
bprops = []       # (subsection, para, prop_id, from, numset, locks)
prose_violations = []
for s in subs:
    for para in s["paragraphs"]:
        fp = para.get("final_prose", "")
        ps = para.get("prose_status", "")
        if fp != "" or "BLOCK" not in ps.upper():
            prose_violations.append((para.get("para_id"), repr(fp[:30]), ps))
        for p in para.get("proposition_chain", []):
            src = p.get("from_phaseA_prop", "")
            covered[src] += 1
            nums = set()
            for t in p.get("numbers", []):
                nums |= set(NUM.findall(t))
            bprops.append((s["subsection_id"], para.get("para_id"), p.get("prop_id"), src, nums, set(p.get("register_locks", []))))

# (b) completeness
phaseA_ids = set(phaseA)
covered_real = {k for k in covered if k in phaseA_ids}
orphaned = sorted(phaseA_ids - covered_real)
multi = {k: c for k, c in covered.items() if k in phaseA_ids and c > 1}
non_source = {k: c for k, c in covered.items() if k not in phaseA_ids}  # e.g. new-transition
print("\n=== (b) ALLOCATION COMPLETENESS ===")
print(f"  Phase-A props: {len(phaseA_ids)} | covered once+: {len(covered_real)} | ORPHANED (dropped): {orphaned}")
print(f"  multi-homed (split/dup, review): {multi}")
print(f"  non-source from_phaseA_prop (transitions etc.): {non_source}")

# (c) prose gate
print("\n=== (c) PROSE GATE (must be empty + BLOCKED) ===")
print(f"  paragraphs total: {sum(len(s['paragraphs']) for s in subs)} | violations (non-empty/!BLOCKED): {len(prose_violations)}")
for v in prose_violations[:10]:
    print("   VIOLATION", v)

# (d) fidelity: numbers + locks trace to source
print("\n=== (d) PER-PROP FIDELITY vs from_phaseA_prop ===")
num_extra, lock_dropped = [], []
for sid, para, pid, src, nums, locks in bprops:
    if src not in phaseA:
        continue
    a = phaseA[src]
    extra = nums - a["numbers"]
    if extra:
        num_extra.append((para, pid, src, sorted(extra), sorted(a["numbers"])))
    dropped = a["locks"] - locks
    if dropped:
        lock_dropped.append((para, pid, src, sorted(dropped)))
print(f"  props checked: {sum(1 for b in bprops if b[3] in phaseA)} | NUMBER-not-in-source: {len(num_extra)} | LOCK-dropped: {len(lock_dropped)}")
for v in num_extra[:12]:
    print("   NUM ", v[0], v[1], "from", v[2], "extra", v[3], "| source", v[4])
for v in lock_dropped[:12]:
    print("   LOCK", v[0], v[1], "from", v[2], "dropped", v[3])

if "--write" in sys.argv:
    has_ent = "&gt;" in raw or "&amp;" in raw or "&lt;" in raw
    def un(o):
        if isinstance(o, str): return html.unescape(o)
        if isinstance(o, list): return [un(x) for x in o]
        if isinstance(o, dict): return {k: un(v) for k, v in o.items()}
        return o
    syn = un(synth) if has_ent else synth
    plan = un(planners) if has_ent else planners
    for s in syn["subsections"]:
        for para in s["paragraphs"]:          # (c) force-empty
            para["final_prose"] = ""
            para["prose_status"] = "BLOCKED -- planning only"
        fp = DEST / f"section{s['subsection_id']}_paragraph_ledger.json"   # (a) filename
        fp.write_text(json.dumps(s, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        json.loads(fp.read_text(encoding="utf-8"))
        print("WROTE", fp.name)
    audit = {"redteam_report": syn.get("redteam_report", []), "allocation_matrix": syn.get("allocation_matrix", []), "global_notes": syn.get("global_notes", [])}
    fa = DEST / "section34_phaseB_redteam.json"
    fa.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("WROTE", fa.name)
    fp = DEST / "section34_phaseB_planners_raw.json"
    fp.write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("WROTE", fp.name)
else:
    print("\n(report only; pass --write to write files)")
