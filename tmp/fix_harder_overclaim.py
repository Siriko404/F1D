# User catch: "asking MORE questions, not HARDER" -- CashScrutiny is a VOLUME measure (% of cash Q&A turns),
# so "harder" overclaims an intensity we do not measure. Fix the 3 scrutiny-framing hits (skip the 2.1
# cited_text quotes, which are verbatim source). Fail-closed asserts.
import json
def fix(path, old, new):
    d = json.load(open(path, encoding="utf-8"))
    s = json.dumps(d, ensure_ascii=False)
    assert old in s, f"MISSING in {path}: {old!r}"
    s = s.replace(old, new)
    d = json.loads(s)
    open(path, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
    print(f"fixed: {path}")

fix("docs/Thesis/rewrite/section2.2_paragraph_ledger.json",
    "analysts asking more or harder cash-related questions", "analysts asking more cash-related questions")
fix("tmp/section2_subsection_plan.json",
    "analysts ask harder cash questions", "analysts ask more cash questions")
fix("docs/Thesis/rewrite/claim_findings_ledger.json",
    "analysts asking harder cash questions", "analysts asking more cash questions")
print("OK -- 'harder' overclaim removed from the 3 scrutiny-framing hits.")
