# Stamp 2.2 RE-RATIFIED (user ceremony 2026-06-13, post scrutiny-reframe). Fail-closed.
import json
p = "docs/Thesis/rewrite/section2.2_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
assert d["status"].startswith("REFRAME APPLIED 2026-06-13 -- RE-RATIFY"), d["status"]
d["status"] = ("RE-RATIFIED 2026-06-13 (user ceremony, post scrutiny-reframe; P5 leaned to a flag with 'harder'->'more', "
    "P5.3/P5.4 folded into 2.5). Prose BLOCKED.")
d["_schema"]["status"] = ("RE-RATIFIED 2026-06-13 (user ceremony) after the scrutiny reframe. Prose still BLOCKED -- "
    "drafted after all four subsections are ratified.")
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.2 stamped RE-RATIFIED")
