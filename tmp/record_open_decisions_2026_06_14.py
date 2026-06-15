# Record the user's 4 open-decision resolutions as ONE additive key in claim_findings_ledger.json.
# Additive only: does NOT alter any claim, number, or register lock. JSON-aware, idempotent, reload-validated.
import json, pathlib
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
F = ROOT / "docs/Thesis/rewrite/claim_findings_ledger.json"
KEY = "_open_decisions_resolved_2026_06_14"
val = {
    "sd_basis": "RESOLVED -> 0.3010 (all-universe Table-1 Panel B UncResCEO SD). Apply consistently across 3.2/3.3/3.4 economic-magnitude statements. The 0.3072 estimation-sample alternative is RETIRED. Coheres with the locked 2.5 FB scaling (0.300988). [user 2026-06-14]",
    "orphan_bibitems": "DROPPED from thesis_draft.tex: bushee2018, everhart2025, gokkaya2025, lerman2026. Verified zero \\cite/\\citet/\\citep usage before removal (grep -> 0 matches). [user 2026-06-14]",
    "appendix_I": "No rename needed: appendix_I_cash_scrutiny.tex is ALREADY titled '\\section*{Appendix I\\quad Cash-Scrutiny Measure: Variable Construction}' and \\input at thesis_draft.tex L198 (relocated 2026-06-14). Content edits remain flagged pending (unspecified). [user 2026-06-14]",
    "c6_two_way_clustering": "RERUN executed (tmp/cashspec_twoway_cluster.py; reuses frozen production loaders; read-only; production script + table untouched). EFFECT diff point estimate identical 0.0983 both ways. firm-clustered (locked): se 0.0476, p2=.039 **. two-way (firm x cal-qtr): se 0.0485, p2=.043 ** -> HOLDS at 5%; does NOT strengthen, does NOT damage. CAUSE matched: n.s.->n.s. (p .367->.411); CAUSE full: *->* (p .095->.072); mechanism stays open. DECISION: keep the locked firm-clustered table (no regeneration); OPTIONAL one-line prose robustness note that the formal difference survives two-way clustering (p=.043). [user 2026-06-14 run-and-see; not damaging]",
}
d = json.loads(F.read_text(encoding="utf-8"))
if d.get(KEY) == val:
    print("idempotent: key already present + identical; no change.")
else:
    d[KEY] = val
    F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(F.read_text(encoding="utf-8"))   # reload-validate
    print("OK: added", KEY, "to claim_findings_ledger.json; JSON valid.")
