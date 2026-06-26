"""Dump the VERBATIM proposition `statement` strings for all 5 subsections of Section 2,
in chain order (paragraph order, then prop order). No summarization -- exact field values.
"""
import json
from pathlib import Path

BASE = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
for s in ["2.1", "2.2", "2.3", "2.4", "2.5"]:
    d = json.loads((BASE / f"section{s}_paragraph_ledger.json").read_text(encoding="utf-8"))
    print(f"\n{'='*70}\n## section {s} -- {d.get('title','')}\n{'='*70}")
    for pid, p in d.get("paragraphs", {}).items():
        if not isinstance(p, dict):
            continue
        print(f"\n[{pid}] ({p.get('lit_body','')})")
        for pr in p.get("propositions", []):
            print(f"  {pr.get('prop_id')} [{pr.get('type')}]: {pr.get('statement','')}")
