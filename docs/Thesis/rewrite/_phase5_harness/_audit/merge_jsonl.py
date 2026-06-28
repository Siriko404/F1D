# Deterministic merge of the per-referee JSONL report files (_audit_reports/*.jsonl) into ONE audit report.
# Each agent appended one JSON object per line (kind = finding | clean_bill | sweep). No LLM. Robust to a
# malformed/partial trailing line (skips + counts it). Output: _AUDIT_REPORT.{json,md}.
import json
from pathlib import Path

RD = Path(__file__).resolve().parents[1] / "_audit_reports"
findings, bills, sweeps, bad = [], [], [], 0
files = sorted(RD.glob("*.jsonl"))
for f in files:
    for ln in f.read_text(encoding="utf-8").splitlines():
        ln = ln.strip().rstrip(",")
        if not ln or ln in "[]":
            continue
        try:
            o = json.loads(ln)
        except Exception:
            bad += 1
            continue
        k = o.get("kind")
        (findings if k == "finding" else bills if k == "clean_bill" else sweeps if k == "sweep" else []).append(o)

SEV = {"high": 0, "medium": 1, "low": 2}
findings.sort(key=lambda o: (SEV.get(o.get("severity"), 3), o.get("referee", "")))
hi = [f for f in findings if f.get("severity") == "high"]
med = [f for f in findings if f.get("severity") == "medium"]
low = [f for f in findings if f.get("severity") == "low"]
referees_reported = sorted({f.stem for f in files})

out = {"referees_reported": referees_reported, "counts": {"high": len(hi), "medium": len(med), "low": len(low),
       "total": len(findings), "clean_bills": len(bills), "malformed_lines": bad}, "findings": findings,
       "clean_bills": bills, "sweeps": sweeps}
(RD.parent / "_AUDIT_REPORT.json").write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

L = ["# THESIS FINAL AUDIT REPORT (1 panel x 7 referees, merged from JSONL)\n",
     "## Coverage", "- referees reported: %s" % ", ".join(referees_reported),
     "- malformed/partial lines skipped: %d" % bad,
     "\n## Counts", "- HIGH %d | MEDIUM %d | LOW %d | total %d | clean-bills %d" %
     (len(hi), len(med), len(low), len(findings), len(bills))]
def dump(title, items):
    L.append("\n## %s (%d)" % (title, len(items)))
    for i, f in enumerate(items, 1):
        L.append("\n### %d. [%s] %s -- %s" % (i, f.get("referee", ""), f.get("severity", ""), f.get("aspect", "")))
        L.append("- location: %s" % f.get("location", ""))
        L.append("- problem: %s" % f.get("problem", ""))
        L.append("- evidence: %s" % " | ".join(f.get("evidence", []) if isinstance(f.get("evidence"), list) else [str(f.get("evidence"))]))
        L.append("- best fix: %s" % f.get("best_fix", ""))
        L.append("- refutation: %s  (confidence: %s)" % (f.get("refutation", ""), f.get("confidence", "")))
dump("HIGH severity", hi)
dump("MEDIUM severity", med)
dump("LOW severity", low)
L.append("\n## Completeness sweeps")
for s in sweeps:
    L.append("- [%s] %s" % (s.get("referee", ""), s.get("completeness", "")))
(RD.parent / "_AUDIT_REPORT.md").write_text("\n".join(L), encoding="utf-8")
print("merged %d referee files | HIGH %d MED %d LOW %d | clean-bills %d | malformed %d -> _AUDIT_REPORT.{json,md}" %
      (len(files), len(hi), len(med), len(low), len(bills), bad))
