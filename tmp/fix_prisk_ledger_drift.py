# The PRisk-gloss raw-text replace updated thesis_draft.tex but missed section2.5_paragraph_ledger.json
# (JSON escapes \citet as \\citet, so a raw-text match failed). Re-do it JSON-aware so the ledger
# P2 final_prose matches the .tex. Drift-guard: final_prose must be verbatim in the .tex afterward.
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
LED = ROOT / "docs" / "Thesis" / "rewrite" / "section2.5_paragraph_ledger.json"
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"

OLD = "the share of a firm's earnings call devoted to political risk of \\citet{hassan2020}"
NEW = "\\citet{hassan2020}'s scaled measure of the share of a firm's earnings call devoted to political risk"

d = json.loads(LED.read_text(encoding="utf-8"))
p2 = d["paragraphs"]["P2"]["final_prose"]
assert OLD in p2, "OLD gloss not found in P2 final_prose (parsed) -- inspect ledger"
d["paragraphs"]["P2"]["final_prose"] = p2.replace(OLD, NEW)
LED.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

tex = TEX.read_text(encoding="utf-8")
assert d["paragraphs"]["P2"]["final_prose"] in tex, "DRIFT: P2 final_prose not verbatim in .tex"
print("OK: 2.5 ledger P2 final_prose synced to .tex; drift check passed.")
