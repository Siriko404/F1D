# Fix E (Option 1, advisor-confirmed): the validity coefs are the industry-FE column; under the
# design's firm-FE spec US-EPU is marginal (0.0123, p<0.10) while PRisk/GEPU stay robust. The table
# already prints both columns, so this just adds a one-clause disclosure. tex (raw) + 2.5 ledger (JSON).
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
LED = ROOT / "docs" / "Thesis" / "rewrite" / "section2.5_paragraph_ledger.json"

OLD = "Table~\\ref{tab:h24b_global_epu}). In economic terms,"
NEW = ("Table~\\ref{tab:h24b_global_epu}). These estimates use industry fixed effects; the positive "
       "associations are robust to firm fixed effects, with the United States index then significant "
       "at the ten percent level. In economic terms,")

assert "--" not in NEW, "dash in NEW"

tex = TEX.read_text(encoding="utf-8")
assert tex.count(OLD) == 1, f"TEX: expected 1 occ, got {tex.count(OLD)}"
TEX.write_text(tex.replace(OLD, NEW), encoding="utf-8")

d = json.loads(LED.read_text(encoding="utf-8"))
p2 = d["paragraphs"]["P2"]["final_prose"]
assert OLD in p2, "OLD anchor not in P2 final_prose"
d["paragraphs"]["P2"]["final_prose"] = p2.replace(OLD, NEW)
LED.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

assert d["paragraphs"]["P2"]["final_prose"] in TEX.read_text(encoding="utf-8"), "DRIFT: P2 not verbatim in .tex"
print("OK: E disclosure clause added to tex + 2.5 ledger; drift check passed.")
