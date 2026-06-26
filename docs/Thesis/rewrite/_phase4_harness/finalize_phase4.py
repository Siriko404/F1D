"""Phase-4 finalize: materialize a harness run's returned object (MECHANICAL apply, NOT grading).
- writes the per-agent change-sets + red-team decisions as committed audit JSONs;
- applies the red-team-accepted final_changes ADDITIVELY to the cloned ledgers:
  originals stay byte-identical, each accepted change is APPENDED as a PROPOSED proposition
  (with its evidence resolved verbatim by ev_id), final_prose stays BLOCKED.

Usage: python finalize_phase4.py <section> <path-to-run-output.json>
       (run-output.json = the object the workflow returned: {section, panel1, panel2, redteam, final_changes, ...})
"""
import json, sys, re
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
ROOT = HARNESS.parents[3]
CITES = ROOT / "tmp" / "nlm_masking_cites.json"

def evidence_map():
    c = json.loads(CITES.read_text(encoding="utf-8"))
    prefix = {"shleifer_vishny2003": "SV", "louis2004": "LO"}
    ev = {}
    for key in ["shleifer_vishny2003", "louis2004"]:
        for i, q in enumerate(c.get(key, {}).get("located", []), 1):
            ev[f"{prefix[key]}{i}"] = {"cite": key, "text": q.get("quote", ""),
                                       "page": str(q.get("page", "")), "section": q.get("section", "")}
    return ev

def main():
    sec = sys.argv[1]
    o = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    # the workflow object may be nested under .result
    if "final_changes" not in o and isinstance(o.get("result"), dict):
        o = o["result"]
    EV = evidence_map()
    out = HARNESS / "out" / f"s{sec}"; (out / "applied").mkdir(parents=True, exist_ok=True)

    # 1. audit artifacts (each agent's json + red-team decisions)
    for i, r in enumerate(o.get("panel1", [])): (out / f"panel1_{chr(97+i)}.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    for i, r in enumerate(o.get("panel2", [])): (out / f"panel2_{chr(97+i)}.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
    (out / "redteam_decisions.json").write_text(json.dumps(o.get("redteam"), indent=2), encoding="utf-8")
    final_changes = o.get("final_changes", []) or []
    final_logic = o.get("final_logic", []) or []
    (out / "final_changes.json").write_text(json.dumps({"final_changes": final_changes, "final_logic": final_logic, "note": o.get("note")}, indent=2), encoding="utf-8")

    # 2. apply ADDITIVELY to the clones
    clone_dir = HARNESS / "clones" / f"s{sec}"
    missing_ev, applied = [], 0
    by_sub = {}
    for ch in final_changes:
        by_sub.setdefault(ch.get("subsection"), []).append(ch)
    logic_by_sub = {}
    for lg in final_logic:
        logic_by_sub.setdefault(lg.get("subsection"), []).append(lg)

    for clone in sorted(clone_dir.glob(f"section{sec}.*_paragraph_ledger.json")):
        sub = re.search(rf"section({sec}\.\d+)_", clone.name).group(1)
        d = json.loads(clone.read_text(encoding="utf-8"))
        paras = d.get("paragraphs", {})
        for ch in by_sub.get(sub, []):
            pk = ch.get("paragraph")
            if pk not in paras or not isinstance(paras[pk], dict):
                missing_ev.append(f"{sub} paragraph {pk} not found"); continue
            evres = []
            for eid in ch.get("ev_ids", []) or []:
                if eid in EV: evres.append({"ev_id": eid, **EV[eid]})
                else: missing_ev.append(f"{sub} {ch.get('new_prop_id')} bad ev_id {eid}")
            if ch.get("source") in ("shleifer_vishny2003", "louis2004") and not (ch.get("ev_ids") or []):
                missing_ev.append(f"{sub} {ch.get('new_prop_id')} motive-source change with NO ev_ids")
            props = paras[pk].setdefault("propositions", [])
            pid_new = ch.get("new_prop_id")
            if pid_new in {pr.get("prop_id") for pr in props}:   # never collide with an original prop_id
                pid_new = f"{pid_new}_P4PROP"
            props.append({
                "prop_id": pid_new,
                "type": f"phase4-proposed:{ch.get('action')}",
                "status": "PROPOSED",
                "targets": ch.get("target_prop_id"),
                "statement": ch.get("statement"),
                "role_in_paragraph": ch.get("role_in_paragraph"),
                "source": ch.get("source"),
                "verification": {"verdict": "PHASE4_PROPOSED", "evidence": evres, "rationale": ch.get("rationale")},
                "provenance": "phase4-harness:redteam-accepted",
            })
            applied += 1
        if logic_by_sub.get(sub):
            d.setdefault("_plan", {}).setdefault("phase4_proposed_logic", []).extend(logic_by_sub[sub])
        # final_prose stays BLOCKED -- untouched
        (out / "applied" / clone.name).write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"section {sec}: {applied} proposed props applied across {len(by_sub)} subsections; note={o.get('note')}")
    print(f"audit + applied clones -> {(out).relative_to(ROOT)}")
    if missing_ev:
        print(f"FLAGS ({len(missing_ev)}):"); [print("  -", m) for m in missing_ev[:20]]

if __name__ == "__main__":
    main()
