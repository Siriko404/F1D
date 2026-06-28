# Phase-B packer. Builds phaseB_data.json = the 17 written sections + a SLIM per-section brief
# (only what red-team/boss/gate need): prose (cite-normalized), bright_lines, register_global,
# the gate's number/cite/table sets, a NUMBER-CONTEXT map (value -> one-line meaning, for the
# red-team's number-in-context check since results have no quotes), and props' register_locks +
# verbatim quotes. Drops rulebook/statement/reason/intent -> fits the 512KB Workflow cap.
import json, re
from pathlib import Path
H = Path(__file__).resolve().parent
WRITTEN = json.load(open(H / "written_prose.json", encoding="utf-8"))
BRIEFS = json.load(open(H / "briefs.json", encoding="utf-8"))
byStem = {b["stem"]: b for b in BRIEFS}
bySec = {b["section"]: b for b in BRIEFS}

CITE_FIX = {"basic1988": "basic_v_levinson", "rule10b5": "rule_10b5"}   # fix #5: wrong keys in section 1
def fix_cites(prose):
    def repl(m):
        keys = [CITE_FIX.get(k.strip(), k.strip()) for k in m.group(2).split(",")]
        return "\\cite" + m.group(1) + "{" + ", ".join(keys) + "}"
    return re.sub(r"\\cite([tp])\{([^}]*)\}", repl, prose or "")

COEF = re.compile(r'[+-]?\d?\.\d{3,4}\*{0,3}')
def normval(s): return re.sub(r'^0+(?=\.)', '', s.strip().lstrip('+-'))
def number_context(brief):
    ctx = {}
    for pa in brief["paragraphs"]:
        for pr in pa["props"]:
            for s in (pr.get("numbers") or []):
                if not isinstance(s, str): continue
                toks = COEF.findall(s)
                for t in toks:
                    v = normval(t.replace("*", ""))
                    ctx.setdefault(v, s.strip()[:160])
    return ctx

out = []
for w in WRITTEN:
    b = byStem.get(w["stem"]) or bySec.get(w["section"])
    paras = [{"para_id": p["para_id"], "final_prose": fix_cites(p["final_prose"])} for p in w["paragraphs"]]
    slim_props = []
    for pa in b["paragraphs"]:
        for pr in pa["props"]:
            v = pr.get("verification") if isinstance(pr.get("verification"), dict) else {}
            slim_props.append({
                "prop_id": pr.get("prop_id"),
                "register_locks": pr.get("register_locks", []),
                "quote": (v.get("evidence_quotes") or "")[:600],
            })
    out.append({
        "section": w["section"], "stem": w["stem"], "title": b.get("title"),
        "paragraphs": paras,
        "bright_lines": b.get("bright_lines") or [],
        "register_global": b.get("register_global"),
        "allowed_tokens_all": b.get("allowed_tokens_all", []),
        "allowed_cites_all": b.get("allowed_cites_all", []),
        "number_table_map_all": b.get("number_table_map_all", {}),
        "table_xwalk": b.get("table_xwalk", {}),
        "table_labels": b.get("table_labels", []),
        "number_context": number_context(b),
        "props": slim_props,
    })

dest = H / "phaseB_data.json"
json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=True)
sz = dest.stat().st_size
nquote = sum(1 for s in out for p in s["props"] if p["quote"])
print(f"phaseB_data.json: {sz} bytes  | sections {len(out)}  props {sum(len(s['props']) for s in out)}  quotes {nquote}")
# sanity: section 1 cite keys normalized?
s1 = next(s for s in out if s["section"] == "1")
blob1 = json.dumps(s1["paragraphs"])
print("section 1 still has basic1988/rule10b5?", ("basic1988" in blob1 or "rule10b5" in blob1))
print("section 1 now has basic_v_levinson/rule_10b5?", ("basic_v_levinson" in blob1 and "rule_10b5" in blob1))
