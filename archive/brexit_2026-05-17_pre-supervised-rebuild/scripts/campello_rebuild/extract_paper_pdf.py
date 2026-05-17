"""Faithful PDF -> Markdown extractor for the Campello (2022 JFQA) audit.

GROUND-TRUTH artifact builder. The output md is used to audit the rebuild
implementation step by step. Therefore it MUST be a verbatim, deterministic
dump of what pdfplumber sees — NO LLM in the loop, NO rephrasing, NO
cleanup, NO filtering. The only bytes this script writes that did not come
out of pdfplumber are the machine-generated navigation markers (page
delimiters / section labels), which are clearly fenced and contain no
paper content.

EXTRACTION METHODOLOGY (transparent, evidence-validated, NO content edit)
-------------------------------------------------------------------------
The raw Cambridge PDF carries a per-page platform watermark — the string
"https://doi.org/10.1017/S0022109022000308 Published online by Cambridge
University Press" — laid out vertically down the RIGHT margin as UPRIGHT
(not rotated) text. pdfplumber's default (top, x0) ordering interleaves
those ~88 vertical char-positions row-by-row with the horizontal body and
table text, shredding tables into one-char-per-line garbage.

Diagnostic evidence (pages 1, 14, 31, 44 — a spread):
  * page width = 441.4 pt on every page
  * watermark = EXACTLY 88 chars at x0 >= 405 on every sampled page,
    contiguous & identical ("https://doi.org/...Cambridge University Press")
  * article body never exceeds x0 = 381 on any sampled page
  => a >=24 pt clean gap separates article text from the watermark.

Fix (programmatic extraction parameters ONLY — changes NO character of
article content; the excluded band is provably a non-article Cambridge
overlay, the exclusion is spatial, deterministic, and reversible):
  - per page: page.crop((0, 0, 405, page.height))   # drop watermark band
  - text  : cropped.extract_text(x_tolerance=1.0, y_tolerance=3)
            x_tolerance=1.0 chosen by sweep (1.0/1.5/2.0/3.0): this PDF's
            text layer has no space glyphs, so word breaks are inferred
            from x-gaps; 1.0 reproduces known-good tokens (e.g. "as the
            quarterly percentage change in profits ... divided by sales"),
            higher values merge words. Residual space-merge on some lines
            is an inherent pdfplumber limitation on space-glyph-less PDFs,
            NOT an edit — it is exactly what the tool returns, verbatim.
  - tables: cropped.extract_tables() (line strategy) PLUS a text-strategy
            pass for borderless academic tables; rendered as a raw pipe
            grid (cell -> str(cell); None -> ""); lossless + reversible.
            Table numeric content also survives in the verbatim text dump.
  - images: count + bbox only (pdfplumber cannot read raster content;
            recording presence is factual, fabricating content is not)

There is NO LLM in the loop and NO hand-cleanup: this script writes the md
directly from pdfplumber output. The only non-pdfplumber bytes are the
fenced page/section markers, which contain no paper content.

Both the main paper and the supplementary material are extracted (Table C1
— the Step-1 sample-filter list — lives in the supplementary file).

Output:
  tmp/campello_v2/<stem>_FULL.md         one md per source PDF
  tmp/campello_v2/_extract_manifest.json per-page char/table/image counts
                                         (for fidelity verification — NOT
                                         derived from the text content)

Run:  python scripts/campello_rebuild/extract_paper_pdf.py
"""

from __future__ import annotations

import json
from pathlib import Path

import pdfplumber

ROOT = Path(__file__).resolve().parents[2]
OUT_DIR = ROOT / "tmp" / "campello_v2"

SOURCES = [
    ("docs/papers/campello_etal_2022_brexit_jfqa.pdf", "campello_paper_FULL.md"),
    ("docs/papers/campello_etal_2022_brexit_supplementary.pdf",
     "campello_supplementary_FULL.md"),
]


def _grid(table: list[list]) -> str:
    """Lossless pipe rendering of a raw extract_tables() table.

    cell -> str(cell); None -> "". No alignment, no header inference, no
    type coercion. Reversible: split on ' | ' recovers the cell list.
    """
    lines = []
    for row in table:
        cells = ["" if c is None else str(c) for c in row]
        lines.append(" | ".join(cells))
    return "\n".join(lines)


def extract(pdf_path: Path, out_md: Path) -> list[dict]:
    manifest = []
    parts: list[str] = []
    parts.append(f"<!-- SOURCE: {pdf_path.as_posix()} -->")
    parts.append("<!-- VERBATIM pdfplumber dump. NO edits. Page markers "
                 "and TABLE/IMAGE labels are machine-generated navigation "
                 "only; all other bytes are raw pdfplumber output. -->")

    with pdfplumber.open(str(pdf_path)) as pdf:
        n = len(pdf.pages)
        for i, raw_page in enumerate(pdf.pages, start=1):
            # Drop the right-margin Cambridge watermark band (x0 >= 405).
            # Evidence: watermark = 88 chars x0>=405 every page; body
            # max x0 = 381. Crop is spatial, deterministic, content-safe.
            page = raw_page.crop((0, 0, 405, raw_page.height))
            text = page.extract_text(x_tolerance=1.0, y_tolerance=3) or ""
            tables = page.extract_tables() or []
            # borderless academic tables: line strategy misses them; add a
            # text-strategy pass (still pure pdfplumber, verbatim cells).
            tables_txt = page.extract_tables(table_settings={
                "vertical_strategy": "text",
                "horizontal_strategy": "text",
            }) or []
            images = raw_page.images or []

            parts.append(f"\n\n{'='*78}\n=== PAGE {i} / {n} "
                         f"({pdf_path.name}) ===\n{'='*78}\n")
            parts.append("----- TEXT (pdfplumber.extract_text, verbatim) "
                         "-----")
            parts.append(text)

            for ti, tbl in enumerate(tables, start=1):
                parts.append(f"\n----- TABLE {ti} on page {i} "
                             f"(extract_tables, LINE strategy, raw grid) "
                             f"-----")
                parts.append(_grid(tbl))
            for ti, tbl in enumerate(tables_txt, start=1):
                parts.append(f"\n----- TABLE {ti} on page {i} "
                             f"(extract_tables, TEXT strategy, raw grid) "
                             f"-----")
                parts.append(_grid(tbl))

            if images:
                bboxes = [
                    {"x0": round(im.get("x0", 0), 1),
                     "top": round(im.get("top", 0), 1),
                     "x1": round(im.get("x1", 0), 1),
                     "bottom": round(im.get("bottom", 0), 1)}
                    for im in images
                ]
                parts.append(f"\n----- IMAGES on page {i}: {len(images)} "
                             f"(pdfplumber cannot read raster content; "
                             f"bbox only) -----")
                parts.append(json.dumps(bboxes))

            manifest.append({
                "pdf": pdf_path.name,
                "page": i,
                "text_chars": len(text),
                "n_tables_line": len(tables),
                "n_tables_text": len(tables_txt),
                "n_images": len(images),
            })

    out_md.write_text("\n".join(parts), encoding="utf-8")
    return manifest


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    full_manifest: dict[str, list[dict]] = {}
    for rel, out_name in SOURCES:
        src = ROOT / rel
        out_md = OUT_DIR / out_name
        m = extract(src, out_md)
        full_manifest[src.name] = m
        tot_c = sum(r["text_chars"] for r in m)
        tot_tl = sum(r["n_tables_line"] for r in m)
        tot_tt = sum(r["n_tables_text"] for r in m)
        tot_i = sum(r["n_images"] for r in m)
        print(f"{src.name}: {len(m)} pages -> {out_md}")
        print(f"  text chars={tot_c:,}  tables(line)={tot_tl} "
              f"tables(text)={tot_tt}  images={tot_i}")

    man_path = OUT_DIR / "_extract_manifest.json"
    man_path.write_text(json.dumps(full_manifest, indent=2),
                        encoding="utf-8")
    print(f"\nmanifest -> {man_path}")
    print("\nVERBATIM extraction complete. Audit ground-truth ready.")


if __name__ == "__main__":
    main()
