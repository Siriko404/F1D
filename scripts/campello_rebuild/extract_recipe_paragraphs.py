"""Deterministic recipe-paragraph extractor for the Campello (2022 JFQA)
replication-deviation walk.

GOAL (Sina directive 2026-05-16/17): walk the paper's replication recipe
ONE row at a time and COMPARE each against the existing rebuild
(scripts/campello_rebuild/step1..step7) to locate the deviation. NOT a
re-implementation from scratch.

WHY THIS DESIGN (evidence, not assumption)
------------------------------------------
campello_paper_FULL.md is a verbatim pdfplumber dump (extract_paper_pdf.py).
Per page it holds one `----- TEXT (pdfplumber.extract_text, verbatim) -----`
block (clean reading order) followed by `----- TABLE ... -----` grids.
The TABLE *TEXT-strategy* grids are a space-glyph-less re-dump of the same
page body ("EmpiricalCounterparts") and MUST be excluded.

A geometric (extract_words x0-indent) paragraph splitter was prototyped
(_diag_recipe_indent.py). It is clean for sz~10 body prose but SCRAMBLES
and word-merges the sz~6 Table 1 note and Table 8 caption — the two most
recipe-critical blocks (cash DV, eq-14, winsorization). FULL.md's
extract_text renders those same blocks clean and in order. Therefore the
authoritative text source is FULL.md's TEXT blocks; segmentation is by
deterministic structural regex only (no geometry, no LLM, no drift).

RECIPE SCOPE (located by content anchors, not hardcoded page numbers)
  * Section IV: from the TEXT line `IV. Data and Methodology` (the one
    inside a verbatim TEXT block, NOT the TABLE-strategy duplicate)
    through the line before `V. Results`. Spans IV.A (betaUK / eq-13),
    IV.B (sample), IV.C (treatment + DiD / eq-14), IV.D + Table 1 note
    (variable defs + "winsorized at the 1% level").
  * Table 8 caption: the `TABLE 8` ... `Table 8 reports output from
    equation (14).` ... note paragraph (cash DV "net of cash holdings",
    eq-14 DiD time window, double-clustering). One row, not split.

OUTPUT (outputs/campello_rebuild/recipe_walk/)
  recipe_paragraphs.tsv  paragraph_id<TAB>source<TAB>pdf_page<TAB>kind<TAB>text
  cursor.json            {"current_paragraph_id": 0, "total": N}
  walk_verdicts.tsv      header only; one line appended per walked row
                         (advancing the cursor REQUIRES a verdict line)

Run:  python scripts/campello_rebuild/extract_recipe_paragraphs.py
"""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FULL_MD = ROOT / "tmp" / "campello_v2" / "campello_paper_FULL.md"
OUT_DIR = ROOT / "outputs" / "campello_rebuild" / "recipe_walk"

PAGE_RE = re.compile(
    r"^=== PAGE (\d+) / \d+ \(campello_etal_2022_brexit_jfqa\.pdf\) ===$"
)
TEXT_LABEL = "----- TEXT (pdfplumber.extract_text, verbatim) -----"
BLOCK_LABEL_RE = re.compile(r"^----- (TABLE|IMAGES) ")

# Structural row classifiers (applied to verbatim TEXT lines, in order).
SECTION_RE = re.compile(r"^(IV|V)\. [A-Z]")
SUBSEC_RE = re.compile(r"^[A-D]\. [A-Z]")
NUMSEC_RE = re.compile(r"^\d+\. [A-Z]")
EQ_RE = re.compile(r"^\(\d+\) ")
FOOTNOTE_RE = re.compile(r"^(\d{1,2})([A-Z][a-z])")  # "11We" "13The"
TABLE_HDR_RE = re.compile(r"^TABLE \d+$")
NOTE_END_RE = re.compile(r"levels, respectively\.$")


def page_text_blocks() -> list[tuple[int, list[str]]]:
    """[(pdf_page, [verbatim TEXT lines]), ...] in document order.

    Per page: the lines after the TEXT label up to the first TABLE/IMAGES
    label (or page end). The TABLE-strategy duplicate is never entered.
    """
    raw = FULL_MD.read_text(encoding="utf-8").splitlines()
    out: list[tuple[int, list[str]]] = []
    page = None
    in_text = False
    buf: list[str] = []
    for line in raw:
        m = PAGE_RE.match(line)
        if m:
            if page is not None:
                out.append((page, buf))
            page, in_text, buf = int(m.group(1)), False, []
            continue
        if line.strip() == TEXT_LABEL:
            in_text = True
            continue
        if BLOCK_LABEL_RE.match(line):
            in_text = False
            continue
        if in_text:
            buf.append(line)
    if page is not None:
        out.append((page, buf))
    return out


def section_iv_lines(blocks) -> list[tuple[int, str]]:
    """[(pdf_page, line)] from `IV. Data and Methodology` (verbatim TEXT
    occurrence) through the line before `V. Results`."""
    seq: list[tuple[int, str]] = []
    started = False
    for page, lines in blocks:
        for ln in lines:
            s = ln.strip()
            if not started:
                if s == "IV. Data and Methodology":
                    started = True
                    seq.append((page, s))
                continue
            if s.startswith("V. Results"):
                return seq
            seq.append((page, ln.rstrip()))
    return seq


def table8_caption(blocks) -> list[tuple[int, str]]:
    """The TABLE 8 caption note paragraph (one logical block)."""
    for page, lines in blocks:
        for i, ln in enumerate(lines):
            if ln.strip() == "TABLE 8":
                cap: list[tuple[int, str]] = []
                for ln2 in lines[i:]:
                    cap.append((page, ln2.rstrip()))
                    if NOTE_END_RE.search(ln2.strip()):
                        return cap
                return cap
    return []


def classify(line: str) -> str:
    s = line.strip()
    if SECTION_RE.match(s):
        return "section_heading"
    if SUBSEC_RE.match(s):
        return "subsection_heading"
    if NUMSEC_RE.match(s):
        return "numbered_heading"
    if EQ_RE.match(s):
        return "equation"
    if FOOTNOTE_RE.match(s):
        return "footnote"
    return "body"


def rows_from_iv(seq: list[tuple[int, str]]) -> list[dict]:
    """Heading/equation/footnote lines = their own single row; runs of
    body lines between markers = one joined body row (FULL.md emits no
    intra-subsection paragraph break, so the subsection body IS the unit).
    """
    rows: list[dict] = []
    cur_pg: int | None = None
    cur_kind: str | None = None
    cur: list[str] = []

    def flush():
        if cur:
            txt = " ".join(x.strip() for x in cur if x.strip())
            if txt:
                rows.append({"source": "IV", "pdf_page": cur_pg,
                             "kind": cur_kind, "text": txt})

    for pg, ln in seq:
        k = classify(ln)
        if k in ("body", "footnote") and cur_kind in ("body", "footnote") \
                and k == cur_kind:
            cur.append(ln)
            continue
        flush()
        cur_pg, cur_kind, cur = pg, k, [ln]
        if k not in ("body", "footnote"):  # singleton structural rows
            flush()
            cur_kind, cur = None, []
    flush()
    return rows


def main() -> None:
    blocks = page_text_blocks()
    iv_rows = rows_from_iv(section_iv_lines(blocks))

    cap = table8_caption(blocks)
    t8_rows: list[dict] = []
    if cap:
        t8_rows = [{
            "source": "TABLE8", "pdf_page": cap[0][0], "kind": "table_caption",
            "text": " ".join(c.strip() for _, c in cap if c.strip()),
        }]

    all_rows = iv_rows + t8_rows
    for i, r in enumerate(all_rows):
        r["paragraph_id"] = i

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    tsv = OUT_DIR / "recipe_paragraphs.tsv"
    with tsv.open("w", encoding="utf-8", newline="") as f:
        f.write("paragraph_id\tsource\tpdf_page\tkind\ttext\n")
        for r in all_rows:
            txt = r["text"].replace("\t", " ").replace("\r", " ")
            f.write(f"{r['paragraph_id']}\t{r['source']}\t{r['pdf_page']}"
                    f"\t{r['kind']}\t{txt}\n")

    (OUT_DIR / "cursor.json").write_text(
        json.dumps({"current_paragraph_id": 0, "total": len(all_rows)},
                   indent=2), encoding="utf-8")

    vfile = OUT_DIR / "walk_verdicts.tsv"
    if not vfile.exists():
        vfile.write_text("paragraph_id\tverdict\trebuild_locus\tnote\n",
                          encoding="utf-8")

    kinds: dict[str, int] = {}
    for r in all_rows:
        kinds[r["kind"]] = kinds.get(r["kind"], 0) + 1
    print(f"recipe_paragraphs.tsv -> {tsv}")
    print(f"  rows={len(all_rows)}  IV={len(iv_rows)}  TABLE8={len(t8_rows)}")
    print(f"  pages IV: {sorted({r['pdf_page'] for r in iv_rows})}")
    print(f"  kinds: {dict(sorted(kinds.items()))}")
    print(f"cursor.json -> current_paragraph_id=0  total={len(all_rows)}")
    print(f"walk_verdicts.tsv -> {vfile} (header {'kept' if vfile.exists() else 'written'})")


if __name__ == "__main__":
    main()
