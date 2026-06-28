# Heal agent-written JSONL lines that fail to parse ONLY because raw LaTeX backslashes
# (\chapter, \citet, \bibitem ...) are illegal JSON escapes. Fix = double every backslash on a
# FAILING line, then require it to parse AND that no information is lost. Valid lines are untouched.
# Idempotent (already-valid file -> 0 healed). Run before merge_jsonl.py. No agent, deterministic.
import json, sys
from pathlib import Path

RD = Path(__file__).resolve().parents[1] / "_audit_reports"
total_healed = 0
for f in sorted(RD.glob("*.jsonl")):
    lines = f.read_text(encoding="utf-8").splitlines()
    out, healed, unfixable = [], 0, 0
    for ln in lines:
        s = ln.strip()
        if not s:
            out.append(ln); continue
        try:
            json.loads(s); out.append(ln); continue          # already valid -> keep verbatim
        except Exception:
            pass
        cand = s.replace("\\", "\\\\")                         # double every backslash
        try:
            obj = json.loads(cand)
        except Exception:
            out.append(ln); unfixable += 1; continue          # not a backslash problem -> leave, flag
        out.append(json.dumps(obj, ensure_ascii=False))       # re-emit canonical valid JSON
        healed += 1
    if healed or unfixable:
        f.write_text("\n".join(out) + "\n", encoding="utf-8")
        print("%-22s healed=%d unfixable=%d" % (f.name, healed, unfixable))
        total_healed += healed
print("TOTAL healed=%d" % total_healed)
