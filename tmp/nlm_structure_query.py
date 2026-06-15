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
OUT = Path(__file__).with_name("nlm_verbose_intro_conclusion.json")

QUERY = (
    "Across the corporate finance empirical research papers in this notebook, "
    "I want the VERBOSE, fully-developed version of the Introduction and the "
    "Conclusion: how the LONGER, well-developed ones expand beyond a minimal "
    "skeleton. For EACH of the two sections, report: "
    "(a) the FULL set of components a well-developed version contains, "
    "including the expansion components that lengthen it. For the CONCLUSION, "
    "cover discussion of IMPLICATIONS (and explicitly FOR WHOM: investors, "
    "managers, regulators, and the academic literature), LIMITATIONS (data, "
    "measurement, identification/causality, external validity/generalizability), "
    "and DIRECTIONS FOR FUTURE RESEARCH. For the INTRODUCTION, cover expansion "
    "components such as institutional or background context, a fuller "
    "literature-positioning, an enumerated contribution paragraph, and a 'why "
    "it matters' significance paragraph; "
    "(b) for EACH component, what it typically CONTAINS and roughly how many "
    "sentences or paragraphs it occupies; "
    "(c) the ORDER these components usually appear in; "
    "(d) for the CONCLUSION specifically, how authors keep the "
    "implications/limitations/future-work paragraphs SUBSTANTIVE and accurate "
    "rather than padding: what makes a limitation paragraph credible, and what "
    "a good future-research direction looks like; "
    "(e) how many PARAGRAPHS a fully-developed introduction and a "
    "fully-developed conclusion typically run to. "
    "Base everything on the actual papers in this notebook; give the common "
    "range; report what they actually do, not an invented template."
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
