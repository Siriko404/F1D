# Advisor fixes to the 3.1-PARA4 S&P-1500 disclosure:
#  (1) widen 'residual sample' -> 'sample' (user confirmed the WHOLE sample is S&P-1500-bounded)
#  (2) soften 'coverage IS the S&P 1500' -> 'approximately' (ExecuComp coverage is ~S&P1500 + legacy,
#      NOT primary-source-verified as exactly equal; keep to what is verified = ExecuComp is the CEO source).
import json, pathlib
F = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\section3.1_paragraph_ledger.json")
d = json.loads(F.read_text(encoding="utf-8"))
p = [x for x in d["paragraphs"] if x["para_id"] == "3.1-PARA4"][0]
def rep(s, a, b):
    assert s.count(a) == 1, f"expected 1 of {a!r}, found {s.count(a)}"
    return s.replace(a, b)
p["final_prose"] = rep(p["final_prose"],
    "from Execucomp, whose coverage is the S\\&P~1500, the residual sample is bounded to firms in that index, which skews",
    "from Execucomp, the sample is bounded to the firms it covers, approximately the S\\&P~1500, which skews")
pa = p["proposition_chain"][0]
pa["statement"] = rep(pa["statement"],
    "bounded to Execucomp-covered firms, the S\\&P 1500, since",
    "bounded to Execucomp-covered firms, approximately the S\\&P 1500, since")
F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
json.loads(F.read_text(encoding="utf-8"))
i = p["final_prose"].find("Because the manager fixed effect")
print("OK. New sentence:\n", p["final_prose"][i:i+230])
