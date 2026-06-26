"""Extract the LOGICAL SPINE of a paragraph-ledger JSON, stripping the verbatim NLM
evidence blocks (quotes/answer/located/located/parts) that contaminate context.
Emits a compact markdown skeleton: per-paragraph intent/thin_claim/guardrails +
proposition statements + verdict + final_prose. Usage: python extract_spine.py <ledger.json> <out.md>
"""
import json, sys
from pathlib import Path

src, out = Path(sys.argv[1]), Path(sys.argv[2])
d = json.loads(src.read_text(encoding="utf-8"))
L = []
def w(s=""): L.append(s)

w(f"# SPINE SKELETON — {src.name}")
w(f"subsection: {d.get('subsection')}  |  title: {d.get('title')}")
w(f"status: {d.get('status')}")
w(f"current_paragraph: {d.get('current_paragraph')}")
w()
pl = d.get("_plan", {})
w("## _plan.section_job"); w(pl.get("section_job",""))
w(); w("## _plan.spine"); w(pl.get("spine",""))
w(); w("## _governing.claim_ceiling"); w(d.get("_governing",{}).get("claim_ceiling",""))
w(); w("## _plan.logic_chain_validated")
for k,v in pl.get("logic_chain_validated",{}).items():
    w(f"- **{k}**: {v}")
w()
w("## papers (key -> ref/para)")
for k,v in d.get("papers",{}).items():
    if isinstance(v,dict):
        w(f"- {k}  [para {v.get('para','?')}]: {v.get('ref', v.get('nlm_source_title',''))}")
    else:
        w(f"- {k}: {v}")
w()
w("## legal_sources")
for k,v in d.get("legal_sources",{}).items():
    if isinstance(v,dict):
        w(f"- {k}: {v.get('ref','')}  [{v.get('status','')}]")
w()
w("=" * 70)
w("# PARAGRAPHS")
paras = d.get("paragraphs", {})
for pid, p in paras.items():
    if not isinstance(p, dict):
        continue
    w(); w("#" * 3 + f" {pid}  (order {p.get('order','?')})  lit_body: {p.get('lit_body','')}")
    for f in ["intent","serves","boundary","thin_claim"]:
        if p.get(f): w(f"- **{f}**: {p[f]}")
    if p.get("guardrails"):
        w("- **guardrails**:")
        for g in p["guardrails"]: w(f"    - {g}")
    props = p.get("propositions", [])
    if props:
        w(f"- **propositions** ({len(props)}):")
        for pr in props:
            vr = pr.get("verification", {})
            verdict = vr.get("verdict", "?")
            note = vr.get("verdict_note", "")
            w(f"    - **{pr.get('prop_id')}** [{pr.get('type')}] verdict={verdict}")
            w(f"        stmt: {pr.get('statement','')}")
            if pr.get("role_in_paragraph"): w(f"        role: {pr['role_in_paragraph']}")
            if note: w(f"        verdict_note: {note}")
    # prose status + the actual committed prose
    for f in ["prose_status","prose_status_note"]:
        if p.get(f): w(f"- **{f}**: {p[f]}")
    pg = p.get("prose_gate")
    if isinstance(pg, dict):
        w(f"- **prose_gate.unlocked**: {pg.get('unlocked')}  status: {pg.get('status','')}")
    fp = p.get("final_prose")
    if fp:
        w(f"- **final_prose**:")
        w(f"    {fp}")
w()
out.write_text("\n".join(L), encoding="utf-8")
print(f"wrote {out}  ({len(L)} lines, {out.stat().st_size} bytes)")
# also report any 'placebo' occurrences with the field path
import re
def walk(o, path=""):
    if isinstance(o, dict):
        for k,v in o.items(): yield from walk(v, f"{path}.{k}")
    elif isinstance(o, list):
        for i,v in enumerate(o): yield from walk(v, f"{path}[{i}]")
    elif isinstance(o, str) and "placebo" in o.lower():
        yield path, o
print("\n--- 'placebo' sites in this ledger ---")
for path, s in walk(d):
    snip = s if len(s) < 240 else s[:240] + "..."
    print(f"{path}:\n  {snip}\n")
