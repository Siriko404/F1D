# Add Execucomp (CEO tenure / identification source) to the 3.1 paragraph ledger PARA1.
# Verified primary-source: src/f1d/sample/build_tenure_map.py Step 1.3 builds the monthly CEO
# tenure panel FROM Execucomp (input inputs/Execucomp/comp_execucomp.parquet). The CEO identity
# is the manager fixed-effect input in the Section 2.3 eq-4 decomposition.
# JSON-aware, assert-guarded (each replace must hit exactly once), reload-validated.
import json, pathlib
F = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\section3.1_paragraph_ledger.json")
d = json.loads(F.read_text(encoding="utf-8"))
p = d["paragraphs"][0]
assert p["para_id"] == "3.1-PARA1"

def rep(s, a, b):
    assert s.count(a) == 1, f"expected 1 occurrence of {a!r}, found {s.count(a)}"
    return s.replace(a, b)

EXEC = ("The identity of the chief executive on each call, the input to the manager fixed effect of "
        "Section~2.3, comes from Execucomp, whose annual records we aggregate into a monthly panel of "
        "which executive holds the CEO role in each quarter.")

# 1) final_prose: four -> five + insert Execucomp sentence after the SDC sentence
p["final_prose"] = rep(p["final_prose"], "The analysis combines four data sources.", "The analysis combines five data sources.")
p["final_prose"] = rep(p["final_prose"],
    "cash-versus-stock payment composition. These sources are keyed to different identifier systems",
    "cash-versus-stock payment composition. " + EXEC + " These sources are keyed to different identifier systems")

# 2) proposition 3.1-PARA1-a: statement + evidence
pa = p["proposition_chain"][0]
assert pa["prop_id"] == "3.1-PARA1-a"
pa["statement"] = rep(pa["statement"], "The analysis combines four data sources:", "The analysis combines five data sources:")
pa["statement"] = rep(pa["statement"],
    "and SDC M&A records (announcement date, completion/withdrawal date, cash-vs-stock payment composition).",
    "SDC M&A records (announcement date, completion/withdrawal date, cash-vs-stock payment composition); and "
    "Execucomp annual CEO records, aggregated into a monthly tenure panel identifying which executive holds the "
    "CEO role in each quarter (the input to the eq-4 manager fixed effect of Section 2.3).")
pa["evidence"].append("src/f1d/sample/build_tenure_map.py Step 1.3 -- monthly CEO tenure panel built FROM Execucomp (input inputs/Execucomp/comp_execucomp.parquet); VERIFIED primary-source 2026-06-14")

# 3) intent + thin_claim count/source updates
p["intent"]["statement"] = rep(p["intent"]["statement"], "the four sources the whole section rests on", "the five sources the whole section rests on")
p["intent"]["statement"] = rep(p["intent"]["statement"], "CRSP/IBES return-and-surprise records, SDC M&A records)", "CRSP/IBES return-and-surprise records, SDC M&A records, Execucomp CEO tenure)")
p["intent"]["reason"] = rep(p["intent"]["reason"], "Every downstream number originates in one of these four sources", "Every downstream number originates in one of these five sources")
p["thin_claim"] = rep(p["thin_claim"], "Four named sources fused through the acquirer six-digit CUSIP to gvkey",
                      "Five named sources, the deal records fused through the acquirer six-digit CUSIP to gvkey")

F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
json.loads(F.read_text(encoding="utf-8"))
print("OK: Execucomp added to 3.1-PARA1; JSON valid.")
print("\n--- new final_prose ---\n", p["final_prose"][:520], "...")
