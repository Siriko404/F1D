#!/usr/bin/env python3
"""Verify seeds cover the WHOLE thesis with 100% verbatim integrity.

COVERAGE  : every CONTENT line has >=1 seed. A line may legitimately have 0 seeds
            only if it is blank or purely structural (preamble, \\begin/\\end, rules,
            section headers, \\bibitem keys, \\end{document}). Any other 0-seed line
            is a GAP (content silently dropped).
INTEGRITY : for each seeded line, joining its seeds (whitespace-normalized) reproduces
            the source line exactly -- after stripping a trailing '\\\\' row terminator.

Run:  python tmp/verify_seeds.py
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from seed_propositions import SKIP, SEC, SUB, BIBITEM, DRAFT, OUT  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
ALLOWED_EMPTY = re.compile(r"^\s*(\\appendix|\\begin\{thebibliography\}|\\end\{document\})")


def norm(s):
    return re.sub(r"\s+", " ", s).strip()


def content_norm(raw):
    s = raw.rstrip()
    if s.endswith(r"\\"):
        s = s[:-2]
    return norm(s)


def allowed_empty(raw):
    return (not raw.strip() or SKIP.match(raw) or SEC.match(raw) or SUB.match(raw)
            or BIBITEM.match(raw) or ALLOWED_EMPTY.match(raw))


def main():
    lines = DRAFT.read_text(encoding="utf-8").splitlines()
    seeds = json.loads(OUT.read_text(encoding="utf-8"))["claims"]

    by_line = {}
    for s in seeds:
        ln = int(s["file_line"].split(":")[1])
        by_line.setdefault(ln, []).append(s["verbatim_span"])

    gaps, mism, content = [], [], 0
    for i, raw in enumerate(lines, 1):
        if i in by_line:
            content += 1
            recon = norm(" ".join(by_line[i]))
            if recon != content_norm(raw):
                mism.append((i, content_norm(raw), recon))
        elif not allowed_empty(raw):
            gaps.append((i, raw[:80]))

    print("content lines seeded    :", content)
    print("seeds total             :", len(seeds))
    print("COVERAGE gaps           :", len(gaps))
    for i, t in gaps:
        print("    L%d  %r" % (i, t))
    print("INTEGRITY mismatches    :", len(mism))
    for i, src, recon in mism[:20]:
        print("    L%d" % i)
        print("       src :", src)
        print("       seed:", recon)

    # garbage: bare LaTeX-command seeds in PROSE blocks only
    prose_garbage = [s["seq"] for s in seeds
                     if s["block"] not in ("appendix-vartable", "bibliography",
                                           "tables", "front-matter")
                     and re.match(r"^\\[a-zA-Z]+(\{|\b)", s["verbatim_span"])
                     and "\\textbf{Abstract" not in s["verbatim_span"]
                     and "\\textbf{H" not in s["verbatim_span"]
                     and "\\noindent" not in s["verbatim_span"]]
    print("prose command-only seeds:", prose_garbage if prose_garbage else "NONE")

    print("\n--- front-matter seeds ---")
    for s in seeds:
        if s["block"] == "front-matter":
            print("  ", s["seq"], s["file_line"], s["note"], repr(s["verbatim_span"][:70]))
    print("--- appendix-prose seeds ---")
    for s in seeds:
        if s["block"] == "appendix-prose":
            print("  ", s["seq"], s["file_line"], repr(s["verbatim_span"][:80]))

    ok = not gaps and not mism and not prose_garbage
    print("\nVERDICT:", "CLEAN -- seeds ready for review" if ok else "FIX NEEDED")


if __name__ == "__main__":
    main()
