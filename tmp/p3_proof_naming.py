#!/usr/bin/env python3
"""P3 method proof — scope-by-NAME (not by -s id), verify no cross-source blend.

Asks ONE atomic, paper-named, UNSCOPED question about DWZ and checks that NLM's
answer is grounded ONLY in DWZ's known source_id (67b17abd...). If the only cited
source is DWZ, scoping-by-name is proven and we drop the source_id pre-mapping.

Durable: writes tmp/p3_proof_naming.json. Run:  python tmp/p3_proof_naming.py
"""
import json
import shutil
import subprocess
from collections import Counter
from pathlib import Path

OUT = Path(__file__).with_name("p3_proof_naming.json")
NOTEBOOK = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
DWZ_ID = "67b17abd-1aed-49dc-938c-ec12775df1ee"  # locked by title earlier

# Paper named in the query itself (title + authors + year) = the scoping mechanism.
QUESTION = (
    "In the paper titled “Straight talkers and vague talkers: The effects of "
    "managerial style in earnings conference calls” by Dzielinski, Wagner, and "
    "Zeckhauser (2021), what is the dependent variable of their equation (4)? "
    "Quote the sentence that introduces equation (4)."
)


def cli(args, timeout):
    return subprocess.run([EXE, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace", timeout=timeout)


def main() -> None:
    if not EXE:
        raise SystemExit("notebooklm CLI not found")
    try:
        cli(["clear"], timeout=60)
    except Exception:
        pass
    r = cli(["ask", "-n", NOTEBOOK, "--json", QUESTION], timeout=360)  # NO -s : named-only
    out = r.stdout or ""
    i = out.find("{")
    j = json.loads(out[i:]) if i >= 0 else {"error": "no JSON", "raw": out[:400]}
    cited = Counter(x.get("source_id") for x in j.get("references", []) if x.get("source_id"))
    distinct = list(cited)
    clean = bool(distinct) and set(distinct) <= {DWZ_ID}
    rec = {
        "question": QUESTION,
        "answer": j.get("answer", ""),
        "cited_source_ids": cited,
        "expected_only": DWZ_ID,
        "VERDICT": "PASS scope-by-name (DWZ only)" if clean
                   else ("FLAG: no citations" if not distinct
                         else f"FLAG: blended sources {distinct}"),
        "references": [{"source_id": x.get("source_id"),
                        "cited_text": (x.get("cited_text") or "")[:240]}
                       for x in j.get("references", [])],
    }
    OUT.write_text(json.dumps(rec, indent=2, ensure_ascii=False), encoding="utf-8")
    print(rec["VERDICT"])
    print("cited:", dict(cited))
    print("answer:", rec["answer"][:600])


if __name__ == "__main__":
    main()
