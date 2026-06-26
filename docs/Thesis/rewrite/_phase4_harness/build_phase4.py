"""Phase-4 build: bake ONE thesis section's proposition-chain skeleton + the fixed evidence map
into the section-agnostic harness -> a runnable .js. Also clones the section's ledgers (for finalize).
The harness never reads files at runtime (Workflow tool has no filesystem access).

Usage:  python build_phase4.py 2          # build the section-2 run
        python build_phase4.py 3          # later: section 3, same template
"""
import json, sys, re, shutil
from pathlib import Path

HARNESS = Path(__file__).resolve().parent                 # .../_phase4_harness
RW = HARNESS.parent                                         # .../docs/Thesis/rewrite
ROOT = HARNESS.parents[3]                                   # .../F1D-phase3
CITES = ROOT / "tmp" / "nlm_masking_cites.json"
TEMPLATE = HARNESS / "phase4_props_redesign.js"

# strip PDF/editor hidden chars the Workflow approval dialog rejects + that break ASCII embedding
_HIDDEN = dict.fromkeys([0x00ad, 0x200b, 0x200c, 0x200d, 0x2060, 0xfeff], None)
_CTRL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")
_SPACES = re.compile("[  -   　]")

def clean(s):
    if not isinstance(s, str):
        return s
    s = s.translate(_HIDDEN)
    s = _CTRL.sub("", s)
    s = _SPACES.sub(" ", s)
    return re.sub(r"[ \t]+", " ", s).strip()

def skeleton(path):
    d = json.loads(path.read_text(encoding="utf-8"))
    m = re.search(r"section(\d+\.\d+)_", path.name)
    sub = m.group(1) if m else d.get("subsection", path.name)
    pl = d.get("_plan", {})
    paras = []
    for pid, p in (d.get("paragraphs", {}) or {}).items():
        if not isinstance(p, dict):
            continue
        props = []
        for pr in (p.get("propositions", []) or []):
            props.append({
                "prop_id": clean(pr.get("prop_id", "")),
                "type": clean(pr.get("type", "")),
                "verdict": clean((pr.get("verification", {}) or {}).get("verdict") or "none"),
                "statement": clean(pr.get("statement", "")),
                "role": clean(pr.get("role_in_paragraph", "")),
            })
        paras.append({
            "pid": clean(pid),
            "intent": clean(p.get("intent", "")),
            "thin_claim": clean(p.get("thin_claim", "")),
            "guardrails": [clean(g) for g in (p.get("guardrails", []) or [])],
            "props": props,
        })
    return {
        "subsection": sub,
        "title": clean(d.get("title", "")),
        "section_job": clean(pl.get("section_job", "")),
        "spine": clean(pl.get("spine", "")),
        "logic_chain_validated": {clean(k): clean(v) for k, v in (pl.get("logic_chain_validated", {}) or {}).items()},
        "paragraphs": paras,
    }

def build_evidence():
    c = json.loads(CITES.read_text(encoding="utf-8"))
    prefix = {"shleifer_vishny2003": "SV", "louis2004": "LO"}
    ev = {}
    for key in ["shleifer_vishny2003", "louis2004"]:        # fixed order; published JFE motive + behaviour
        for i, q in enumerate(c.get(key, {}).get("located", []), 1):
            ev[f"{prefix[key]}{i}"] = {
                "cite": key,
                "text": clean(q.get("quote", "")),
                "page": clean(str(q.get("page", ""))),
                "section": clean(q.get("section", "")),
            }
    return ev

def main():
    sec = (sys.argv[1:] or ["2"])[0]
    ledgers = sorted(RW.glob(f"section{sec}.*_paragraph_ledger.json"),
                     key=lambda p: [int(x) for x in re.search(r"section(\d+)\.(\d+)_", p.name).groups()])
    assert ledgers, f"no ledgers found for section {sec} in {RW}"

    # clone the originals verbatim (for finalize to annotate; originals stay pristine)
    clone_dir = HARNESS / "clones" / f"s{sec}"
    clone_dir.mkdir(parents=True, exist_ok=True)
    for lp in ledgers:
        shutil.copy2(lp, clone_dir / lp.name)

    SECTION = {"section": sec, "subsections": [skeleton(lp) for lp in ledgers]}
    EVIDENCE = build_evidence()

    tpl = TEMPLATE.read_text(encoding="utf-8")
    sec_json = json.dumps(SECTION, ensure_ascii=True)
    ev_json = json.dumps(EVIDENCE, ensure_ascii=True)
    out, did_s, did_e = [], False, False
    for line in tpl.splitlines():
        if "__SECTION_ANCHOR__" in line:
            out.append(f"const SECTION = {sec_json} // s{sec}"); did_s = True
        elif "__EVIDENCE_ANCHOR__" in line:
            out.append(f"const EVIDENCE = {ev_json} // {len(EVIDENCE)} quotes"); did_e = True
        else:
            out.append(line)
    assert did_s and did_e, f"anchors missing (section={did_s}, evidence={did_e})"

    run_dir = HARNESS / "_run"; run_dir.mkdir(parents=True, exist_ok=True)
    dest = run_dir / f"phase4_s{sec}.js"
    text = "\n".join(out)
    dest.write_text(text, encoding="utf-8", newline="\n")     # LF only

    # VERIFY: the approval dialog rejects any non-ASCII / CR / stray control char
    bad = [(i, hex(ord(ch))) for i, ch in enumerate(text) if ord(ch) > 0x7f or ch == "\r" or (ord(ch) < 0x20 and ch not in "\n\t")]
    print(f"wrote {dest.relative_to(ROOT)}  ({len(text):,} chars)")
    print(f"ASCII/LF check: {'CLEAN' if not bad else f'DIRTY {bad[:5]}'}")
    print(f"evidence quotes: {len(EVIDENCE)}  ({', '.join(EVIDENCE.keys())})")
    print(f"cloned {len(ledgers)} ledgers -> {clone_dir.relative_to(ROOT)}")
    print("per-subsection skeleton (verify nothing dropped):")
    for ss in SECTION["subsections"]:
        npr = sum(len(p["props"]) for p in ss["paragraphs"])
        print(f"  {ss['subsection']:5s} {len(ss['paragraphs'])} paras / {npr:2d} props   {ss['title'][:60]}")
    assert not bad, "ABORT: non-ASCII/CRLF in generated file"

if __name__ == "__main__":
    main()
