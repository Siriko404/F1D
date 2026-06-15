#!/usr/bin/env python3
"""One-off ADVISORY query: ask the notebook (UNSCOPED, all sources) for the
conventional structure of Introduction and Conclusion sections in corporate
finance empirical papers. Answer is advisory guidance, NOT ledger-verification
evidence -- written to tmp for the record and printed.

Unscoped = NO -s (guide section 3a / 1): `clear` then `ask -n <NB> --json`.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

NB = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
EXE = shutil.which("notebooklm")
OUT = Path(__file__).with_name("nlm_abstract_structure_detailed.json")

QUERY = (
    "Across the corporate finance empirical research papers in this notebook, "
    "synthesize a thorough, decisive description of how the ABSTRACT is "
    "written, so I can follow it as a convention. Report: "
    "(a) the ordered CONTENT the abstract must contain (for example: the "
    "motivation or question, the data and sample, the method or measure, the "
    "main findings, and the contribution or implication) and the order these "
    "elements appear in; "
    "(b) its typical LENGTH in words and in sentences, and whether it is a "
    "single paragraph or more; "
    "(c) style conventions: verb tense, first-person 'we' versus impersonal "
    "voice, whether it states SPECIFIC numerical results or coefficients or "
    "only qualitative/directional findings, and how compressed the language "
    "is; "
    "(d) what an abstract MUST NOT do. "
    "Base every figure on the actual papers in this notebook; where papers "
    "vary, give the common range, and note where the convention is "
    "near-universal versus where it varies. Do not invent a template; report "
    "what these papers actually do."
)


def main() -> None:
    if not EXE:
        sys.exit("ERROR: notebooklm CLI not found on PATH.")
    try:
        subprocess.run([EXE, "clear"], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    except Exception:
        pass  # best-effort isolation
    r = subprocess.run([EXE, "ask", "-n", NB, "--json", QUERY],
                       capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=400)
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        sys.exit("No JSON in output:\n" + (out + (r.stderr or ""))[:1000])
    j = json.loads(out[i:])
    answer = j.get("answer", "")
    refs = [{"n": x.get("citation_number"), "source_id": x.get("source_id"),
             "cited_text": x.get("cited_text")} for x in j.get("references", [])]
    OUT.write_text(json.dumps({"query": QUERY, "answer": answer,
                               "references": refs}, indent=2, ensure_ascii=False),
                   encoding="utf-8")
    print("=== ANSWER ===\n")
    print(answer)
    print(f"\n=== {len(refs)} references; written to {OUT.name} ===")


if __name__ == "__main__":
    main()
