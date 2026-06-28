# Deterministic merge of the 14 referee reports (2 panels x 7) into ONE audit report. No LLM.
# Input: a JSON file = the audit_workflow.js return {schema_version, panels, referees, reports:[14]}.
# Output: _AUDIT_REPORT.json (machine) + _AUDIT_REPORT.md (human). Flags CORROBORATED findings (same
# referee+aspect raised by BOTH panels) and ranks by severity. Pairs the panels' coverage into a manifest.
import json, sys
from collections import defaultdict
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("_AUDIT_RAW.json")
raw = json.load(open(src, encoding="utf-8"))
reports, referees, panels = raw["reports"], raw["referees"], raw["panels"]

# ---- coverage manifest: every referee x panel cell must have reported ----
seen = {(r["referee"], r["panel"]) for r in reports}
missing = [(rf, p) for rf in referees for p in panels if (rf, p) not in seen]

# ---- collect findings, tag panel+referee, mark corroboration ----
F = []
for r in reports:
    for f in r.get("findings", []):
        g = dict(f); g["referee"] = r["referee"]; g["panel"] = r["panel"]; F.append(g)
pan_by_key = defaultdict(set)
for f in F:
    pan_by_key[(f["referee"], f["aspect"].lower().strip())].add(f["panel"])
for f in F:
    f["corroborated"] = len(pan_by_key[(f["referee"], f["aspect"].lower().strip())]) >= 2
SEV = {"high": 0, "medium": 1, "low": 2}
F.sort(key=lambda f: (SEV.get(f["severity"], 3), not f["corroborated"], f["referee"], f["panel"]))

hi = [f for f in F if f["severity"] == "high"]
med = [f for f in F if f["severity"] == "medium"]
low = [f for f in F if f["severity"] == "low"]
corr = [f for f in F if f["corroborated"]]

out = {
    "coverage": {"expected": len(referees) * len(panels), "reported": len(reports), "missing": missing},
    "counts": {"high": len(hi), "medium": len(med), "low": len(low), "total": len(F), "corroborated": len(corr)},
    "findings": F,
    "clean_bills": [{"referee": r["referee"], "panel": r["panel"], "bills": r.get("clean_bills", [])} for r in reports],
    "completeness_sweeps": [{"referee": r["referee"], "panel": r["panel"], "sweep": r.get("completeness_sweep", "")} for r in reports],
}
Path("_AUDIT_REPORT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

# ---- human-readable .md ----
L = []
L.append("# THESIS FINAL AUDIT REPORT (2 panels x 7 referees, merged)\n")
L.append("## Coverage")
L.append("- expected %d cells, reported %d. MISSING: %s" % (out["coverage"]["expected"], out["coverage"]["reported"], missing or "none"))
L.append("\n## Counts")
L.append("- HIGH %d | MEDIUM %d | LOW %d | total %d | corroborated-by-both-panels %d" %
         (len(hi), len(med), len(low), len(F), len(corr)))
def dump(title, items):
    L.append("\n## %s (%d)" % (title, len(items)))
    for i, f in enumerate(items, 1):
        c = " [CORROBORATED A+B]" if f["corroborated"] else " [single panel %s]" % f["panel"]
        L.append("\n### %d. [%s/%s] %s%s" % (i, f["referee"], f["severity"], f["aspect"], c))
        L.append("- **location:** %s" % f.get("location", ""))
        L.append("- **problem:** %s" % f.get("problem", ""))
        L.append("- **evidence:** %s" % " | ".join(f.get("evidence", [])))
        L.append("- **best fix:** %s" % f.get("best_fix", ""))
        L.append("- **fix evidence:** %s" % " | ".join(f.get("fix_evidence", [])))
        L.append("- **self-refutation:** %s  (confidence: %s)" % (f.get("refutation_attempt", ""), f.get("confidence", "")))
dump("HIGH severity", hi)
dump("MEDIUM severity", med)
dump("LOW severity", low)
L.append("\n## Completeness sweeps (what each referee says it might have missed)")
for s in out["completeness_sweeps"]:
    L.append("- [%s/%s] %s" % (s["referee"], s["panel"], s["sweep"]))
Path("_AUDIT_REPORT.md").write_text("\n".join(L), encoding="utf-8")
print("merged %d reports -> _AUDIT_REPORT.{json,md} | HIGH %d MED %d LOW %d corroborated %d | missing cells: %s" %
      (len(reports), len(hi), len(med), len(low), len(corr), missing or "none"))
