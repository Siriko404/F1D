import json, os, sys

BASE = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\style_profiles"
OUT  = r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\ef5c9060-5c18-48e5-b556-5bb839b73b23\scratchpad"

FIELDS = ["id","aspect","exemplar_pattern","exemplar_quotes",
          "our_pattern","our_quotes","gap","materiality","guardrail_collision"]

ROSTER = {
    "abstract":   "The thesis abstract: ~10 sentences stating the problem, the constructed measure, the design, the headline results, and a flat takeaway.",
    "intro":      "The introduction: motivates the gap, states the contribution, previews the design and findings.",
    "lit_review": "The literature review: positions the study against prior corporate-finance and disclosure work.",
    "hypotheses": "The hypothesis development: builds each prediction from theory into a stated, testable hypothesis.",
    "data":       "The data section: describes sample construction, sources, and variable definitions.",
    "methods":    "The methods/empirical-design section: specifies the estimating equations, identification, and controls.",
    "results":    "The results section: reports each coefficient's sign, magnitude, and significance, plus robustness.",
    "conclusion": "The conclusion: restates findings, limitations, and implications.",
}
CONVENTION = ("Corporate-finance prose uses a plain, literal register: short single-clause declaratives, "
              "concrete actor-verb-object sentences, plainly named constructs, explicit direction words, and "
              "flat takeaways - no metaphor, dramatization, nominalized abstraction, or stacked compound nouns.")

def load_findings(t):
    p = os.path.join(BASE, f"{t}_profile.json")
    with open(p, encoding="utf-8") as f:
        prof = json.load(f)
    fnd = prof["profile"]
    clean = [{k: f.get(k) for k in FIELDS} for f in fnd]
    return clean

def build(types, tag):
    profiles = []
    report = []
    for t in types:
        cl = load_findings(t)
        profiles.append({"type": t, "findings": cl})
        empty = [f["id"] for f in cl if not f.get("exemplar_quotes")]
        report.append((t, len(cl), empty))
    args = {"profiles": profiles, "types": types,
            "roster": {t: ROSTER[t] for t in types}, "convention": CONVENTION}
    out = os.path.join(OUT, f"phase2_args_{tag}.json")
    with open(out, "w", encoding="utf-8") as g:
        json.dump(args, g, ensure_ascii=False)
    n_agents = sum(3 for _ in types) + len(types) + 1 + 3   # 3 extract/type + 1 cull/type + 1 judge + 3 classify
    print(f"[{tag}] -> {out}")
    print(f"   bytes: {os.path.getsize(out)}   agents: ~{n_agents}")
    for t, n, empty in report:
        print(f"   {t}: {n} findings, empty-anchor: {empty}")
    return out

build(["results","methods"], "results_methods")   # wave D (reuse)
print()
# wave args: 2 types each, paired to keep each file readable in one shot (results isolated in wave D)
build(["abstract","hypotheses"], "wA")
print()
build(["intro","data"], "wB")
print()
build(["lit_review","conclusion"], "wC")
print()
# single-type re-run args for the types my multi-type pastes truncated
build(["data"], "data")
print()
build(["conclusion"], "conclusion")
print()
build(["results"], "results")
