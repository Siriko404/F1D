#!/usr/bin/env python3
"""Seed thesis_propositions.json with ordered SENTENCE seeds from the draft prose.

MECHANICAL ONLY: cuts prose lines into sentences and pre-fills
{seq, block, file_line, verbatim_span}. It NEVER decides what is a claim --
all judgment fields (proposition/category/route/verdict) are left null for the
manual block-by-block pass. Coverage guarantee: every body-prose line in range
emits >=1 seed, so no line can be silently skipped.

Range: start of file up to \\begin{thebibliography}. The bibliography (bibitems)
and the appendix variable-table are STRUCTURED (not prose) and are seeded by hand
during judgment -- this script stops at the bibliography and reports the stop line.

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
    r"^\s*(%|\\documentclass|\\usepackage|\\pagestyle|\\title|\\author|\\date|"
    r"\\thanks|\\section|\\subsection|\\label|\\begin|\\end|\\input|\\maketitle|"
    r"\\vspace|\\centering|\\par|\\noindent\\textbf\{Keywords|"
    r"\\noindent\\textbf\{JEL|\}|\\\[|\\\])"
)
SEC = re.compile(r"^\s*\\section\*?\{([^}]*)\}")
SUB = re.compile(r"^\s*\\subsection\*?\{([^}]*)\}")


def split_sentences(text):
    """Guarded sentence split that PRESERVES verbatim exactly: mask protected
    spans (math, cites, decimals/dotted numbers, abbreviations) with null-byte
    tokens, split on sentence boundaries, then restore the originals."""
    store = {}

    def mask(pat, s):
        def repl(m):
            k = "\x00%d\x00" % len(store)
            store[k] = m.group(0)
            return k
        return re.sub(pat, repl, s)

    s = mask(r"\$[^$]*\$", text)                                      # inline math
    s = mask(r"\\(?:citep|citet|cite|ref|eqref|label)\{[^}]*\}", s)     # cite/ref
    s = mask(r"\b(?:U\.S\.|U\.K\.|e\.g\.|i\.e\.|vs\.|etc\.|et\s+al\.|"
             r"al\.|Inc\.|No\.|Ph\.D\.|Dr\.|Fig\.|Eq\.|cf\.|approx\.|Prof\.)", s)
    s = mask(r"\d+(?:\.\d+)+", s)                                     # decimals/dotted

    parts = re.split(r"(?<=[.?!])\s+(?=[A-Z\\`(])", s)

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

    section = subsection = ""
    seeds, seq = [], 0
    stop_line = None

    for i, raw in enumerate(lines, start=1):
        if "\\begin{thebibliography}" in raw:
            stop_line = i
            break
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
            seq += 1
            seeds.append({
                "seq": seq, "id": None, "block": block,
                "file_line": "thesis_draft.tex:%d" % i, "verbatim_span": sent,
                "proposition": None, "category": None, "role": None,
                "check_route": None, "mapped_bibkey": None, "p2_ref": None,
                "depends_on": [], "verdict": None, "evidence": None, "note": None,
            })

    j["claims"] = seeds
    OUT.write_text(json.dumps(j, indent=2, ensure_ascii=False), encoding="utf-8")

    sys.stdout.reconfigure(encoding="utf-8")
    print("seeds=%d  stopped_at_bibliography_line=%s" % (len(seeds), stop_line))
    blocks = {}
    order = []
    for s in seeds:
        if s["block"] not in blocks:
            order.append(s["block"])
        blocks[s["block"]] = blocks.get(s["block"], 0) + 1
    for b in order:
        print("  %3d  %s" % (blocks[b], b))


if __name__ == "__main__":
    main()
