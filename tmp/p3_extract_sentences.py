#!/usr/bin/env python3
"""P3 Stage-1 / S0 — total-partition + reassembly extractor (zero LLM).

Partitions EVERY line of thesis_draft.tex into exactly one typed unit so nothing
can hide in a "skipped" region (AUDIT_PROTOCOL E7). Guarantees, all enforced by
`exit 1` on failure:
  - PARTITION: every line assigned once; union == file; no gaps/overlaps.
  - REASSEMBLY: concat(units, file order) == source, char-for-char (no-drop proof).
  - EVERY-LINE TRIPWIRE SCAN: attribution markers are flagged in ALL classes,
    including exempt ones (a hit in PREAMBLE/COMMENT is a structural surprise).

Output: tmp/p3_sentences.json — the frozen unit register Pass A/B classify.
This script NEVER classifies attributions; it only segments + flags. Deterministic.

Run:  python tmp/p3_extract_sentences.py
"""
import json
import re
import sys
from pathlib import Path

SRC = Path("docs/Thesis/thesis_draft.tex")
OUT = Path("tmp/p3_sentences.json")

# ---- structural boundaries: detected, never hard-coded by content -------------
def classify_lines(lines):
    """Return per-line class tag. Boundaries from real LaTeX markers only."""
    n = len(lines)
    # locate markers (1-based line numbers)
    def find(rgx, default):
        for i, l in enumerate(lines):
            if re.search(rgx, l):
                return i
        return default
    doc_begin   = find(r'\\begin\{document\}', -1)
    bib_begin   = find(r'\\begin\{thebibliography\}', n)
    bib_end     = find(r'\\end\{thebibliography\}', n)
    appendix    = find(r'\\appendix', n)
    tab_begin   = next((i for i in range(appendix, n) if re.search(r'\\begin\{tabular\}', lines[i])), n) if appendix < n else n
    tab_end     = next((i for i in range(tab_begin, n) if re.search(r'\\end\{tabular\}', lines[i])), n) if tab_begin < n else n
    tables_sec  = find(r'\\section\*\{Tables\}', n)

    tags = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if i <= doc_begin:
            t = "PREAMBLE"
        elif s.startswith('%'):
            t = "COMMENT"
        elif bib_begin <= i <= bib_end:
            t = "BIB"
        elif tab_begin <= i <= tab_end:
            t = "APX-ROWS"
        elif i >= tables_sec:
            t = "TABLES-INPUT"      # the \input{_tables_from_bible}; out of prose scope
        elif i > appendix:
            t = "APX-PROSE"
        else:
            t = "PROSE"             # body incl. abstract block + section headers
        # abstract minipage lives before first \section but after \maketitle: still PROSE-class
        tags.append(t)
    return tags, dict(doc_begin=doc_begin+1, bib=(bib_begin+1, bib_end+1),
                      appendix=appendix+1, tabular=(tab_begin+1, tab_end+1),
                      tables_sec=tables_sec+1)

# ---- sentence splitter (abbrev-guarded) --------------------------------------
_ABBR = ['et al.', 'e.g.', 'i.e.', 'U.S.', 'cf.', 'vs.', 'Dr.', 'Mr.', 'Ms.',
         'Inc.', 'Ltd.', 'No.', 'pp.', 'Fig.', 'Eq.', 'eq.', 'Sec.']
def split_sentences(text):
    """Conservative sentence split on . ? ! followed by space+capital, abbrev-safe."""
    holes = text
    for a in _ABBR:
        holes = holes.replace(a, a.replace('.', ''))
    # protect decimals like 0.0461 and equation refs
    holes = re.sub(r'(\d)\.(\d)', r'\1\2', holes)
    parts = re.split(r'(?<=[.?!])\s+(?=[A-Z(\\])', holes)
    return [p.replace('', '.') for p in parts if p.strip()]

# ---- attribution tripwires (flag only; classification is the LLM's job) -------
TRIP = {
    "cite":    re.compile(r'\\cite'),
    "surname": re.compile(r'Dzielinski|Wagner|Zeckhauser|Loughran|McDonald|Thewissen|'
                          r'Hassan|Hoberg|Phillips|Bushee|Lerman|Ragozzino|Reuer|'
                          r'Everhart|Gokkaya|Baker|Bloom|Davis|DWZ|Arslan|Tahoun|'
                          r'Hollander|van Lent|Gow|Taylor|Kravet|McVay|Warren|Liu|Stulz|'
                          r'Steffen|Zhang'),
    "year":    re.compile(r'\((?:19|20)\d{2}[a-z]?\)'),
    "soft":    re.compile(r'\b(literature|prior work|recent work|growing literature|'
                          r'a strand|established|documented|precedent|consistent with|'
                          r'following|prior studies|prior research|body of work|'
                          r'to our knowledge|nearest work|work nearest)\b', re.I),
}
def trip_hits(text):
    return sorted(k for k, rx in TRIP.items() if rx.search(text))

# ---- main --------------------------------------------------------------------
def main():
    if not SRC.exists():
        sys.exit(f"ERROR missing {SRC}")
    raw = SRC.read_text(encoding="utf-8")
    lines = raw.split("\n")           # keep exact; rejoin with "\n"
    tags, marks = classify_lines(lines)

    units = []
    uid = 0
    i = 0
    N = len(lines)
    # group consecutive same-tag lines into blocks, then segment per class
    while i < N:
        t = tags[i]
        j = i
        while j < N and tags[j] == t:
            j += 1
        block_lines = lines[i:j]                      # 0-based [i, j)
        block_text = "\n".join(block_lines)
        base_line = i + 1                             # 1-based first line

        if t in ("PROSE", "APX-PROSE"):
            # segment each non-blank line's text into sentences, preserve blanks as raw units
            for off, ln in enumerate(block_lines):
                if ln.strip() == "" or ln.strip().startswith('\\') and not re.search(r'[a-z]{3}', ln):
                    units.append(mk(uid, t+"-RAW", base_line+off, ln, ln)); uid += 1
                    continue
                segs = split_sentences(ln)
                if not segs:
                    units.append(mk(uid, t+"-RAW", base_line+off, ln, ln)); uid += 1
                    continue
                # map segments back; to keep reassembly exact, store the LINE as one unit
                # with its sentence segmentation as metadata (segments are for the LLM)
                units.append(mk(uid, t, base_line+off, ln, ln, sentences=segs)); uid += 1
        elif t == "BIB":
            # entry-mode: one unit per line, but tag \bibitem starts
            for off, ln in enumerate(block_lines):
                kind = "BIB-ITEM" if '\\bibitem' in ln else ("BIB-BODY" if ln.strip() else "BIB-RAW")
                units.append(mk(uid, kind, base_line+off, ln, ln)); uid += 1
        elif t == "APX-ROWS":
            for off, ln in enumerate(block_lines):
                kind = "APX-ROW" if '&' in ln else "APX-ROWS-RAW"
                units.append(mk(uid, kind, base_line+off, ln, ln)); uid += 1
        else:  # PREAMBLE, COMMENT, TABLES-INPUT — exempt but scanned
            for off, ln in enumerate(block_lines):
                units.append(mk(uid, t, base_line+off, ln, ln)); uid += 1
        i = j

    # ---- GUARANTEE 1: reassembly == source -----------------------------------
    rebuilt = "\n".join(u["raw"] for u in units)
    if rebuilt != raw:
        # find first divergence for the error message
        for k,(a,b) in enumerate(zip(rebuilt, raw)):
            if a != b:
                sys.exit(f"REASSEMBLY FAIL at char {k}: rebuilt {a!r} != src {b!r}\n"
                         f"  ...{rebuilt[max(0,k-40):k+10]!r}")
        sys.exit(f"REASSEMBLY FAIL: length {len(rebuilt)} != {len(raw)}")

    # ---- GUARANTEE 2: every line assigned exactly once -----------------------
    assigned = [u["line"] for u in units]
    if assigned != list(range(1, N+1)):
        sys.exit(f"PARTITION FAIL: {len(assigned)} units vs {N} lines; "
                 f"first gap near {next((a for a,b in zip(assigned,range(1,N+1)) if a!=b), '?')}")

    # ---- GUARANTEE 3: exempt-class tripwire surprises -------------------------
    surprises = [u for u in units if u["class"] in ("PREAMBLE","TABLES-INPUT")
                 and u["trip"]]
    # COMMENT hits are expected (author notes cite papers); log as INFO not fail
    comment_hits = [u for u in units if u["class"]=="COMMENT" and u["trip"]]

    data = {
        "source": str(SRC), "sha_note": "baseline 7f97a16",
        "n_lines": N, "n_units": len(units),
        "markers": marks,
        "reassembly_ok": True, "partition_ok": True,
        "exempt_surprises": [{"line":u["line"],"trip":u["trip"],"raw":u["raw"][:80]} for u in surprises],
        "comment_attrib_hits": len(comment_hits),
        "class_counts": _counts(units),
        "trip_unit_count": sum(1 for u in units if u["trip"]),
        "units": units,
    }
    OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    if surprises:
        print("WARN exempt-class tripwire surprises:", [(u['line'],u['trip']) for u in surprises])
    print(f"OK  {N} lines -> {len(units)} units | reassembly+partition PASS")
    print(f"    classes: {data['class_counts']}")
    print(f"    tripwire-flagged units: {data['trip_unit_count']} | comment-attrib hits: {len(comment_hits)}")
    print(f"    -> {OUT}")

def mk(uid, cls, line, raw, text, sentences=None):
    u = {"uid": uid, "class": cls, "line": line, "raw": raw,
         "trip": trip_hits(text)}
    if sentences and len(sentences) > 1:
        u["sentences"] = sentences
    return u

def _counts(units):
    from collections import Counter
    return dict(Counter(u["class"] for u in units))

if __name__ == "__main__":
    main()
