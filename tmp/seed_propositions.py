#!/usr/bin/env python3
"""Seed thesis_propositions.json with ordered SEEDS covering the WHOLE thesis.

MECHANICAL ONLY: it cuts the source into ordered units and pre-fills
{seq, block, file_line, verbatim_span}. It NEVER decides what is a claim --
all judgment fields stay null for the manual, rule-driven proposition pass.

Three phases, in document order, so nothing is skipped:
  1. PROSE  (front matter + body, up to the bibliography): title/author/date
     captured whole; body prose sentence-split (verbatim preserved exactly).
  2. BIB    (\\begin..\\end{thebibliography}): one seed per \\bibitem citation.
  3. APPENDIX (after the bibliography): \\noindent prose sentence-split; every
     '\\\\'-terminated tabular row = one seed (variable definition / group header).

The Tables section (\\input{_tables_from_bible}) is a pointer seed only -- the
hundreds of table cells live in thesis_tables.tex and were verified in P2.

Run:  python tmp/seed_propositions.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DRAFT = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
OUT = ROOT / "docs" / "Thesis" / "audit" / "thesis_propositions.json"

SKIP = re.compile(
    r"^\s*(%|\\appendix|\\documentclass|\\usepackage|\\pagestyle|\\thanks|\\section|"
    r"\\subsection|\\label|\\begin|\\end|\\input|\\maketitle|\\vspace|"
    r"\\centering|\\small|\\par|\\toprule|\\midrule|\\bottomrule|\\clearpage|"
    r"\\noindent\\textbf\{Keywords|\\noindent\\textbf\{JEL|\}|\\\[|\\\])"
)
SEC = re.compile(r"^\s*\\section\*?\{([^}]*)\}")
SUB = re.compile(r"^\s*\\subsection\*?\{([^}]*)\}")
TAD = re.compile(r"^\s*\\(title|author|date)\b")
BIBITEM = re.compile(r"^\s*\\bibitem(?:\[[^\]]*\])?\{([^}]+)\}")


def split_sentences(text):
    """Guarded sentence split preserving verbatim exactly."""
    store = {}

    def mask(pat, s):
        def repl(m):
            k = "\x00%d\x00" % len(store)
            store[k] = m.group(0)
            return k
        return re.sub(pat, repl, s)

    s = mask(r"\$[^$]*\$", text)
    s = mask(r"\\(?:citep|citet|cite|ref|eqref|label)\{[^}]*\}", s)
    s = mask(r"\b(?:U\.S\.|U\.K\.|e\.g\.|i\.e\.|vs\.|etc\.|et\s+al\.|"
             r"al\.|Inc\.|No\.|Ph\.D\.|Dr\.|Fig\.|Eq\.|cf\.|approx\.|Prof\.)", s)
    s = mask(r"\d+(?:\.\d+)+", s)

    # \x00 in lookahead: a masked token (cite/math/number) can START a sentence
    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z\\`(\x00])", s)
    out = []
    for p in parts:
        for k, v in store.items():
            p = p.replace(k, v)
        p = p.strip()
        if p:
            out.append(p)
    return out


def main():
    j = json.loads(OUT.read_text(encoding="utf-8"))
    lines = DRAFT.read_text(encoding="utf-8").splitlines()
    n = len(lines)

    bib_start = next(i for i, l in enumerate(lines, 1) if "\\begin{thebibliography}" in l)
    bib_end = next(i for i, l in enumerate(lines, 1) if "\\end{thebibliography}" in l)

    seeds = []
    seq = [0]

    def add(block, lineno, span, note=None):
        seq[0] += 1
        seeds.append({
            "seq": seq[0], "id": None, "block": block,
            "file_line": "thesis_draft.tex:%d" % lineno, "verbatim_span": span,
            "proposition": None, "category": None, "role": None,
            "check_route": None, "mapped_bibkey": None, "p2_ref": None,
            "depends_on": [], "verdict": None, "evidence": None, "note": note,
        })

    # ---- Phase 1: prose (front matter + body), lines 1 .. bib_start-1 ----
    section = subsection = ""
    for i in range(1, bib_start):
        raw = lines[i - 1]
        m = TAD.match(raw)
        if m:
            add("front-matter", i, raw.strip(), "title-block:%s" % m.group(1))
            continue
        m = SEC.match(raw)
        if m:
            section, subsection = m.group(1), ""
            continue
        m = SUB.match(raw)
        if m:
            subsection = m.group(1)
            continue
        if not raw.strip() or SKIP.match(raw):
            continue
        block = subsection or section or "front-matter"
        for sent in split_sentences(raw):
            add(block, i, sent)

    # ---- Phase 2: bibliography, lines bib_start+1 .. bib_end-1 ----
    key = None
    for i in range(bib_start + 1, bib_end):
        raw = lines[i - 1]
        m = BIBITEM.match(raw)
        if m:
            key = m.group(1)
            continue
        if not raw.strip():
            continue
        add("bibliography", i, raw.strip(), "bibitem:%s" % key)

    # ---- Phase 3: appendix, lines bib_end+1 .. end ----
    appsec = ""
    for i in range(bib_end + 1, n + 1):
        raw = lines[i - 1]
        if "\\end{document}" in raw:
            break
        if "\\input{" in raw:
            add("tables", i, raw.strip(),
                "POINTER: table cells live in thesis_tables.tex, verified in P2")
            continue
        m = SEC.match(raw)
        if m:
            appsec = m.group(1)
            continue
        stripped = raw.rstrip()
        if stripped.endswith(r"\\"):
            row = stripped[:-2].rstrip()
            if row.strip():
                add("appendix-vartable", i, row, "table-row")
            continue
        if not raw.strip() or SKIP.match(raw):
            continue
        for sent in split_sentences(raw):
            add("appendix-prose", i, sent)

    j["claims"] = seeds
    OUT.write_text(json.dumps(j, indent=2, ensure_ascii=False), encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    print("seeds=%d  bib=[%d,%d]  total_lines=%d" % (len(seeds), bib_start, bib_end, n))
    blocks, order = {}, []
    for s in seeds:
        if s["block"] not in blocks:
            order.append(s["block"])
        blocks[s["block"]] = blocks.get(s["block"], 0) + 1
    for b in order:
        print("  %3d  %s" % (blocks[b], b))


if __name__ == "__main__":
    main()
