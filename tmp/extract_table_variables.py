"""Programmatic variable inventory for the thesis draft (S3.1 ledger, step 1).

Reads docs/Thesis/_tables_from_bible.tex (byte-exact bible copies) and extracts,
per table label, the first-column cell of every tabular row. NO interpretation:
over-capture, dedupe, dump to tmp/table_variables.json for classification.
"""
import json
import re
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "docs" / "Thesis" / "_tables_from_bible.tex"
OUT = ROOT / "tmp" / "table_variables.json"

text = SRC.read_text(encoding="utf-8")

# split into blocks by the generator's "% --- <label>" markers
blocks = re.split(r"^% --- ", text, flags=re.M)[1:]

result = {}
for blk in blocks:
    header, _, body = blk.partition("\n")
    label = header.strip()
    cells = []
    for tab in re.finditer(r"\\begin\{tabular\}.*?\\end\{tabular\}", body, re.S):
        inner = tab.group(0)
        # drop the \begin{tabular}{colspec} line itself
        inner = re.sub(r"\\begin\{tabular\}\{[^}]*\}", "", inner)
        for row in inner.split(r"\\"):
            row = row.strip()
            if not row or row.startswith(("%",)):
                continue
            first = row.split("&")[0].strip()
            # strip pure rules/spacing
            first = re.sub(r"\\(toprule|midrule|bottomrule|cmidrule\([^)]*\)\{[^}]*\}|addlinespace(\[[^\]]*\])?)", "", first).strip()
            if first and first not in cells:
                cells.append(first)
    result[label] = cells

OUT.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"blocks: {len(result)}")
for k, v in result.items():
    print(f"  {k}: {len(v)} distinct first-cells")
print(f"-> {OUT}")
