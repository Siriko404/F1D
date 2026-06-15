# Add the S&P 1500 sample-bound disclosure to 3.1-PARA4 (the three-layer sample paragraph).
# Driver: the eq-4 manager fixed effect identifies each CEO from Execucomp (build_tenure_map.py),
# whose coverage is the S&P 1500, so the residual/uncertainty sample is bounded to that index.
# User-confirmed 2026-06-14 ("our sample is bounded to sp1500"). JSON-aware, assert-guarded.
import json, pathlib
F = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\section3.1_paragraph_ledger.json")
d = json.loads(F.read_text(encoding="utf-8"))
p = [x for x in d["paragraphs"] if x["para_id"] == "3.1-PARA4"][0]

def rep(s, a, b):
    assert s.count(a) == 1, f"expected 1 occurrence of {a!r}, found {s.count(a)}"
    return s.replace(a, b)

SP = ("Because the manager fixed effect of Section~2.3 identifies each CEO from Execucomp, whose coverage "
      "is the S\\&P~1500, the residual sample is bounded to firms in that index, which skews the uncertainty "
      "regressions toward larger, more heavily covered firms.")

p["final_prose"] = rep(p["final_prose"],
    "no speaking style and hence no residual can be estimated. On top of it sits the SDC deal universe",
    "no speaking style and hence no residual can be estimated. " + SP + " On top of it sits the SDC deal universe")

pa = p["proposition_chain"][0]
pa["statement"] = rep(pa["statement"],
    "for whom no style and hence no residual is estimable)",
    "for whom no style and hence no residual is estimable, and bounded to Execucomp-covered firms, the S\\&P 1500, since the CEO identity feeds the eq-4 manager fixed effect)")
pa["evidence"].append("src/f1d/sample/build_tenure_map.py (CEO identity from Execucomp) + USER-CONFIRMED 2026-06-14: estimation sample bounded to the S&P 1500 (Execucomp coverage)")

F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
json.loads(F.read_text(encoding="utf-8"))
print("OK: S&P 1500 bound added to 3.1-PARA4; JSON valid.")
i = p["final_prose"].find("Because the manager fixed effect")
print("\n--- inserted ---\n", p["final_prose"][i:i+260])
