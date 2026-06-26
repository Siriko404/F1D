import json, os

TASKS = r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\f9d74b65-ab20-4e1e-836c-076362f92472\tasks"
DST   = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\style_profiles\_rulebooks"
os.makedirs(DST, exist_ok=True)

# best complete source per type (data/conclusion = complete re-runs; results = the validated dry-run, 32/32)
SRC = {
    "abstract":"wl9nlqh8r", "hypotheses":"wl9nlqh8r",
    "intro":"w6pqghcds",
    "lit_review":"wlnair456",
    "methods":"wj7s7c4pt",
    "data":"wq8ke3i90",
    "conclusion":"wl81f2s4a",
    "results":"w14x0nbi7",   # earlier dry-run: 27 rules, 32/32 coverage (same panel->gate->cull mechanics)
}
EXPECTED = {"abstract":15,"intro":14,"hypotheses":23,"lit_review":18,"methods":18,"data":20,"conclusion":17,"results":32}
FIELDS = ["principle_id","trigger","gap_fix","exemplar_anchor","finding_ids","meaning_flag"]

rows = []
for t, tid in SRC.items():
    p = os.path.join(TASKS, tid + ".output")
    sz = os.path.getsize(p) if os.path.exists(p) else -1
    try:
        o = json.load(open(p, encoding="utf-8"))
    except Exception as e:
        print(f"  !! {t} ({tid}.output, {sz} bytes): {e}")
        continue
    res = o.get("result") or {}
    principles = (res.get("rulebooks") or {}).get(t) or []
    clean = [{k: p.get(k) for k in FIELDS} for p in principles]   # strip any extra fields (e.g. dry-run 'universal')
    with open(os.path.join(DST, t + ".json"), "w", encoding="utf-8") as g:
        json.dump(clean, g, ensure_ascii=False, indent=2)
    covered = len({fid for p in clean for fid in (p.get("finding_ids") or [])})
    rows.append((t, len(clean), covered, EXPECTED[t]))

print("FINAL 8 rulebooks -> _rulebooks/:")
allok = True
for t, n, cov, exp in sorted(rows):
    ok = "OK" if cov == exp else f"SHORT ({exp-cov} missing)"
    if cov != exp: allok = False
    print(f"  {t:12s} {n:2d} rules   findings covered {cov}/{exp}   {ok}")
print("\nALL 8 COMPLETE" if allok else "\n!! some still short")
