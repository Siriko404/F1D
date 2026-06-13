#!/usr/bin/env python3
"""Push Section 2.1 from the curated ledger JSON into thesis_draft.tex.

READS section2.1_paragraph_ledger.json (the curated, verified source) and WRITES
the P1-P7 final_prose into thesis_draft.tex, replacing the OLD 2.1 body in place.
The prose is moved by code -- never retyped -- so the .tex cannot drift from the ledger.

Touches ONLY: (1) the body between \\subsection{Conceptual Framework} and the next
\\subsection, and (2) appends the 6 bibitems 2.1 cites that the bibliography lacks
(without them those citations render as [?]). Every other section is left untouched.

Guards (abort, write nothing, on any failure):
  - section anchors must be unique;
  - after splicing, EVERY \\citep/\\citet key in the new 2.1 must have a \\bibitem
    -> guarantees no undefined-citation [?] in the compiled 2.1.

  python push_2_1_to_tex.py            # write thesis_draft.tex
  python push_2_1_to_tex.py --dry      # validate only, write nothing
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]                       # .../F1D/docs
LEDGER = HERE / "section2.1_paragraph_ledger.json"
TEX = ROOT / "Thesis" / "thesis_draft.tex"

START = "\\subsection{Conceptual Framework}"
NEXT = "\\subsection{Hypothesis Development}"
END_BIB = "\\end{thebibliography}"

# bibitems 2.1 cites that the .tex bibliography is missing. Labels (surname+year) drive
# the in-text citation; full-ref text is from the ledger metadata. No invented initials
# (Keown/Pinkerton: ledger has no initials -> surnames only, flagged for later).
BIBS = r"""\bibitem[Bertrand and Schoar(2003)]{bertrand_schoar2003}
Bertrand, M., and A.~Schoar. 2003. Managing with style: The effect of managers on firm policies. \emph{The Quarterly Journal of Economics} 118: 1169--1208.

\bibitem[Dye(1985)]{dye1985}
Dye, R. 1985. Disclosure of nonproprietary information. \emph{Journal of Accounting Research} 23: 123--145.

\bibitem[Harford(1999)]{harford1999}
Harford, J. 1999. Corporate cash reserves and acquisitions. \emph{The Journal of Finance} 54: 1969--1997.

\bibitem[Hollander et~al.(2010)]{hollander2010}
Hollander, S., M.~Pronk, and E.~Roelofsen. 2010. Does silence speak? An empirical analysis of disclosure choices during conference calls. \emph{Journal of Accounting Research} 48: 531--563.

\bibitem[Keown and Pinkerton(1981)]{keown1981}
Keown and Pinkerton. 1981. Merger announcements and insider trading activity: An empirical investigation. \emph{The Journal of Finance} 36: 855--869.

\bibitem[Verrecchia(1983)]{verrecchia1983}
Verrecchia, R. 1983. Discretionary disclosure. \emph{Journal of Accounting and Economics} 5: 179--194.

"""


def main():
    dry = "--dry" in sys.argv

    led = json.loads(LEDGER.read_text(encoding="utf-8"))
    P = led["paragraphs"]
    keys = ["P1", "P2", "P3", "P4", "P5", "P6", "P7"]
    paras = [P[k]["final_prose"].strip() for k in keys]
    for k, t in zip(keys, paras):
        if not t:
            raise SystemExit("ABORT: %s final_prose is empty" % k)
    body = "\n\n" + "\n\n".join(paras) + "\n\n"

    tex = TEX.read_text(encoding="utf-8")
    for anchor in (START, NEXT, END_BIB):
        if tex.count(anchor) != 1:
            raise SystemExit("ABORT: anchor not unique (%dx): %s" % (tex.count(anchor), anchor))

    i = tex.index(START) + len(START)
    j = tex.index(NEXT)
    if not i < j:
        raise SystemExit("ABORT: 2.1 anchors out of order")
    new_tex = tex[:i] + "\n" + body + tex[j:]

    # append ONLY bibitems whose key is not already defined (idempotent re-runs;
    # blindly appending BIBS every run duplicates entries -> duplicate \bibitem keys).
    key_re = re.compile(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}")
    existing_keys = set(key_re.findall(new_tex))
    entries = re.split(r"\n(?=\\bibitem)", BIBS.strip())
    to_add = [e.strip() for e in entries if key_re.search(e).group(1) not in existing_keys]
    if to_add:
        add_str = "\n\n".join(to_add) + "\n\n"
        b = new_tex.index(END_BIB)
        new_tex = new_tex[:b] + add_str + new_tex[b:]
    print("bibitems appended: %d %s" % (
        len(to_add), [key_re.search(e).group(1) for e in to_add]))

    # guard: every citation key in the new 2.1 must resolve to a bibitem
    used = {k.strip() for g in re.findall(r"\\cite[tp]\{([^}]*)\}", body) for k in g.split(",")}
    defined = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", new_tex))
    missing = sorted(used - defined)
    if missing:
        raise SystemExit("ABORT: undefined citation keys in 2.1: %s" % missing)

    print("2.1 cites: %s" % sorted(used))
    print("all resolve to bibitems: True")
    print("new 2.1 body: %d chars, 7 paragraphs" % len(body.strip()))
    if dry:
        print("dry-run: thesis_draft.tex NOT written")
        return
    TEX.write_text(new_tex, encoding="utf-8")
    print("wrote thesis_draft.tex")


if __name__ == "__main__":
    main()
