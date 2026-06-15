# Read-only condensed view of the 5 Phase-B paragraph ledgers: per subsection, the paragraph
# count rationale + each paragraph's order/intent/homed-props -- to verify atomicity + order at a glance.
import json, pathlib, textwrap
DEST = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")
def t(s, n): return textwrap.shorten(str(s).replace("\n", " "), width=n, placeholder=" ...")
for sid in ["3.1", "3.2", "3.3", "3.4", "4.1"]:
    d = json.loads((DEST / f"section{sid}_paragraph_ledger.json").read_text(encoding="utf-8"))
    paras = d["paragraphs"]
    print(f"\n{'='*92}\n{sid}  {d['title']}   ({len(paras)} paragraphs)")
    pcr = d.get("paragraph_count_rationale", {})
    if pcr: print("  WHY:", t(pcr.get("statement"), 150))
    for p in paras:
        homed = [pp.get("from_phaseA_prop") for pp in p.get("proposition_chain", [])]
        nprops = len(p.get("proposition_chain", []))
        print(f"  [{p.get('order')}] {p.get('para_id'):14} props={nprops} {homed}")
        print(f"       intent: {t(p['intent']['statement'], 160)}")
        print(f"       bound : {t(p.get('boundary'), 110)}")
