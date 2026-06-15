#!/usr/bin/env python3
"""Extract DWZ's PUBLISHED Equation-4 estimation numbers (R2, N, #CEOs, control coefs) +
the reported summary stats of the measures, for the construct-validity replication table.
Scoped to DWZ (source_id from nlm_dwz_id.json); LOCATOR clause for page+section (guide section 7)."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
NB = "63e3b970-7976-47bc-8291-37ce7ac9bf74"
SRC = "67b17abd-1aed-49dc-938c-ec12775df1ee"  # DWZ 'Straight talkers...'
EXE = shutil.which("notebooklm")
OUT = Path(__file__).with_name("nlm_dwz_repl_numbers.json")

QUERIES = {
 "eq4_estimation": (
   "Reading only this paper, \"Straight talkers and vague talkers\" by Dzielinski, "
   "Wagner and Zeckhauser: they construct Clarity and the residual UncRes by estimating "
   "Equation 4, a regression of UncAnsCEO (uncertainty-word frequency in the CEO's "
   "answers) on a CEO fixed effect, speech controls, firm characteristics, and year fixed "
   "effects. For THIS Equation-4 estimation, what does the paper report? Give (a) the "
   "R-squared or adjusted R-squared, (b) the number of observations or call-quarters, "
   "(c) the number of distinct CEOs in the estimation sample, and (d) any reported "
   "coefficients on the control variables (UncPreCEO, UncQue, NegCall, SurpDec, EPSgrowth, "
   "stock return, market return). For each number, quote the exact sentence or table cell, "
   "and report the exact page printed in the paper and the table or section number."),
 "measure_summary_stats": (
   "Reading only this paper, \"Straight talkers and vague talkers\" by Dzielinski, Wagner "
   "and Zeckhauser: what summary statistics does the paper report for the measures "
   "UncAnsCEO, UncPreCEO, ClarityCEO, and UncResCEO, for example the number of "
   "observations, the mean, the standard deviation, the minimum and maximum? Quote each "
   "reported statistic and report the exact page printed in the paper and the table number."),
}


def ask(q):
    try:
        subprocess.run([EXE, "clear"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
    except Exception:
        pass
    r = subprocess.run([EXE, "ask", "-n", NB, "-s", SRC, "--json", q],
                       capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=400)
    out = r.stdout or ""
    i = out.find("{")
    if i < 0:
        return {"error": "no JSON", "raw": (out + (r.stderr or ""))[:600]}
    j = json.loads(out[i:])
    return {"answer": j.get("answer", ""),
            "references": [{"n": x.get("citation_number"), "cited_text": x.get("cited_text")} for x in j.get("references", [])]}


def main():
    if not EXE:
        sys.exit("notebooklm not on PATH")
    data = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}
    for key, q in QUERIES.items():
        if data.get(key, {}).get("answer"):
            print(f"[skip {key}: already captured]")
            continue
        print(f"[asking {key} ...]", flush=True)
        res = ask(q)
        data[key] = {"query": q, **res}
        OUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
        print("OK" if res.get("answer") else f"ERR {res.get('error')}", flush=True)
    print(f"\n=== written -> {OUT.name} ===\n")
    for key in QUERIES:
        print(f"----- {key} -----")
        print((data.get(key, {}).get("answer") or "(empty)")[:1800])
        print()


if __name__ == "__main__":
    main()
