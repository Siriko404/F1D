# Programmatic push of the Section 2.4 ledger's P5 final_prose into the inline §2
# of thesis_draft_uottawa.tex. Section 2 is inline (no assembler), so this script is
# the §2 equivalent of build_sec34_body.py: prose originates in the JSON ledger and
# is copied verbatim into the .tex. It replaces ONLY the P5 paragraph (matched by its
# stable opening anchor), asserting exactly one match. Re-running is idempotent.
import json, pathlib
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
LEDGER = ROOT / "docs/Thesis/rewrite/section2.4_paragraph_ledger.json"
TEX = ROOT / "docs/Thesis/thesis_draft_uottawa.tex"
ANCHOR = "Several choices that do not belong to a single equation are recorded here."

new_p5 = json.loads(LEDGER.read_text(encoding="utf-8"))["paragraphs"]["P5"]["final_prose"].strip()
lines = TEX.read_text(encoding="utf-8").splitlines(keepends=True)
hits = [i for i, ln in enumerate(lines) if ANCHOR in ln]
assert len(hits) == 1, f"expected exactly 1 P5 line, found {len(hits)}"
i = hits[0]
eol = "\n" if lines[i].endswith("\n") else ""
lines[i] = new_p5 + eol
TEX.write_text("".join(lines), encoding="utf-8")
print(f"pushed §2.4 P5 -> uottawa.tex line {i+1}; ledger==tex:", new_p5 in TEX.read_text(encoding='utf-8'))
