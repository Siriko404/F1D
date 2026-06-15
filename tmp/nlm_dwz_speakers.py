#!/usr/bin/env python3
"""Scoped DWZ query: confirm CEO is the MAIN decomposition unit and how CFO/other managers
are treated (additional). DWZ source_id from tmp/nlm_dwz_id.json. Guide: scope -s + name paper."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NB = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
SRC = "67b17abd-1aed-49dc-938c-ec12775df1ee"  # DWZ 'Straight talkers...' (nlm_dwz_id.json)
EXE = shutil.which("notebooklm")
OUT = Path(__file__).with_name("nlm_dwz_speakers.json")

Q = ("Reading only this paper, \"Straight talkers and vague talkers\" by Dzielinski, "
     "Wagner and Zeckhauser: besides the CEO, does the paper also estimate the same "
     "Clarity and uncertainty style decomposition for the CFO? Quote the sentences "
     "that describe whether and how the CFO is analyzed.")


def main():
    if not EXE:
        sys.exit("notebooklm not on PATH")
    try:
        subprocess.run([EXE, "clear"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except Exception:
        pass
    r = subprocess.run([EXE, "ask", "-n", NB, "-s", SRC, "--json", Q],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("no JSON:\n" + (out + (r.stderr or ""))[:800])
    j = json.loads(out[i:])
    ans = j.get("answer", "")
    refs = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text")} for x in j.get("references", [])]
    OUT.write_text(json.dumps({"query": Q, "answer": ans, "references": refs}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(ans)
    print(f"\n=== {len(refs)} refs (verbatim spans = admissible) -> {OUT.name} ===")


if __name__ == "__main__":
    main()
