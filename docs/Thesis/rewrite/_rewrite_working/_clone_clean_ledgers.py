"""
Phase-2 setup: clone the 16 subsection paragraph ledgers and blank ONLY the prose,
keeping the spine (propositions / number_audit / guardrails / intent / allocation) intact.
Originals are READ-ONLY here -> they stay frozen as the source of truth.
Clones land in rewrite/_rewrite_working/ and are the rewrite targets.
"""
import json
from pathlib import Path

SRC = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")
WORK = SRC / "_rewrite_working"
WORK.mkdir(exist_ok=True)

def blank_prose(obj):
    """Recursively blank final_prose; flag prose_status. Returns (n_prose, n_status)."""
    np = ns = 0
    if isinstance(obj, dict):
        for k, v in list(obj.items()):
            if k == "final_prose" and isinstance(v, str):
                obj[k] = ""
                np += 1
            elif k == "prose_status" and isinstance(v, str):
                obj[k] = "CLEARED -- Phase-2 rewrite pending (spine frozen in original)"
                ns += 1
            else:
                a, b = blank_prose(v)
                np += a; ns += b
    elif isinstance(obj, list):
        for it in obj:
            a, b = blank_prose(it)
            np += a; ns += b
    return np, ns

files = sorted(SRC.glob("section*_paragraph_ledger.json"))
report = []
for f in files:
    original_text = f.read_text(encoding="utf-8")
    data = json.loads(original_text)
    np, ns = blank_prose(data)
    out = WORK / f.name
    out.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    # safety: confirm we did NOT touch the original on disk
    still_same = f.read_text(encoding="utf-8") == original_text
    report.append((f.name, np, ns, still_same))

print(f"{'file':50s} {'prose_blanked':>13s} {'status_set':>11s} {'orig_intact':>11s}")
for name, np, ns, same in report:
    print(f"{name:50s} {np:13d} {ns:11d} {str(same):>11s}")
print(f"\nTotal files cloned: {len(report)}  ->  {WORK}")
print(f"Total prose fields blanked: {sum(r[1] for r in report)}")
print(f"All originals intact: {all(r[3] for r in report)}")
