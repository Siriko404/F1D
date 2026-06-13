# Scoped NLM query: DWZ's OWN stated rationale for including presentation uncertainty (UncPreCEO)
# as a control in the eq-4 decomposition, and what they say the residual (UncRes) represents.
# Convention: reuse nlm_common engine (resolve id fail-closed, clear+scoped ask, capture cited_text).
import sys, json
sys.path.insert(0, "docs/Thesis/rewrite")
import nlm_common as nc

LABEL = 'the paper "Straight Talkers" by Dzielinski, Wagner, and Zeckhauser'
QUESTION = ("In the regression (their Equation 4) that decomposes the CEO's answer-level uncertainty-word use "
            "(UncAnsCEO) into a CEO fixed effect and a residual (which they denote UncRes), the authors include "
            "among the control variables the uncertainty of the CEO's own PREPARED PRESENTATION remarks (UncPreCEO), "
            "alongside other speech controls. What reason do the authors give for including these speech controls -- "
            "in particular presentation uncertainty UncPreCEO -- in this decomposition, and what do they say the "
            "resulting residual UncRes represents (what it nets out / isolates)?")

sid, title = nc.require(["dwz2021"])["dwz2021"]
q, j = nc.ask(sid, LABEL, QUESTION)
ans = j.get("answer", "")
quotes = [{"n": x.get("citation_number"), "cited_text": x.get("cited_text"),
           "start_char": x.get("start_char"), "end_char": x.get("end_char"),
           "chunk_id": x.get("chunk_id")} for x in j.get("references", []) if x.get("cited_text")]
located = [{"quote": m.group(1).strip(), "page": m.group(2).strip(), "section": m.group(3).strip()}
           for m in nc.LOC.finditer(ans)]
out = {"source": {"id": sid, "title": title}, "query": q, "answer": ans, "quotes": quotes, "located": located}
json.dump(out, open("tmp/nlm_dwz_uncpre_control.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print("SOURCE:", title)
print("\nANSWER (context, NON-evidence):\n", ans[:2200])
print("\nVERBATIM SPANS (admissible cited_text):")
for qq in quotes:
    print(f"  [n{qq['n']}] {qq['cited_text']}")
print(f"\n(located {len(located)} answer-quotes w/ page/section; wrote tmp/nlm_dwz_uncpre_control.json)")
