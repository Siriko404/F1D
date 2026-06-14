# Record the θ/κ <-> β notation bridge as a carried seam in the 2.4 ledger (advisor 2026-06-13). Idempotent.
import json
p = "docs/Thesis/rewrite/section2.4_paragraph_ledger.json"
d = json.load(open(p, encoding="utf-8"))
seam = ("SEAM-E (notation bridge, advisor 2026-06-13): 2.2 states the hypotheses as sign restrictions on theta_e "
        "(residual-uncertainty shift vs baseline) and kappa_e (cash-ratio shift), the ESTIMANDS these designs estimate. "
        "2.4 MUST bridge its beta notation to theta/kappa so Section 2 reads consistently: beta on PreAnnounceQtr "
        "estimates theta_-1 (MA1); beta_c - beta_s estimates theta_-1^cash - theta_-1^stock (MA3); the GAP bin estimates "
        "theta_gap (MA2); the cash-ratio column estimates kappa.")
cs = d["_plan"]["carried_seams"]
if not any("SEAM-E" in x for x in cs):
    cs.append(seam)
open(p, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(p, encoding="utf-8"))
print("2.4 ledger: SEAM-E (theta/kappa <-> beta bridge) recorded.")
