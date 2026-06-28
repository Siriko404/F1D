# -*- coding: utf-8 -*-
"""Sync _robustness_insert_spec.json to the clone: thread the FE addendum into RU-2/CC-2
(shows + caveat = ratified), add the ratified caveat-2 + FE provenance. Keep spec<->clone aligned."""
import json, sys
from pathlib import Path
RW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite")
SPEC = RW/"_robustness_insert_spec.json"
J = json.load(open(SPEC, encoding="utf-8"))
obj = {o["id"]: o for o in J["objects"]}

RATIFIED_C2 = ("We re-estimate both binary tests with firm and year-quarter fixed effects. Logit A's "
  "coefficient is essentially unchanged and stays significant (0.0078***) -- robust to firm and "
  "year-quarter fixed effects, hence not an artifact of stable between-firm differences or common time "
  "trends; its within-firm R2 is small (0.003), as expected for a rare event, so this is a robustness "
  "check, not a claim that the signal is primarily within-firm. Logit B keeps its sign but loses "
  "significance (0.0644, n.s.): only the 8.5% of firms (48 of 563) that make both a cash and a stock "
  "deal identify it within-firm -- too few for precision, consistent with cash-concentration being a "
  "cross-firm pattern. A firm-fixed-effects logit is infeasible for both (perfect separation: 59% / 91% "
  "of firms have no within-firm outcome variation).")

# RU-2 (Logit A)
obj["RU-2"]["shows"] += (" FE ADDENDUM: re-estimated with firm + year-quarter FE, the coefficient is essentially "
  "unchanged and stays significant (LPM 0.0078***, SE 0.00275, N 39,557; within-R2 0.003 -- robust to FE, "
  "NOT a within-firm-signal claim). A firm-FE logit is infeasible (perfect separation: 59% of firms no within variation).")
obj["RU-2"]["caveat"] = ("Predictive/associational, NOT causal. POOLS ALL PAYMENT TYPES -> backs the GENERAL run-up "
  "(H1) only; cannot separate cash from stock (that is Logit B). FE: robust (0.0078***) but within-R2 0.003 -> robustness, "
  "not within-firm signal; logit-FE infeasible. See ratified caveat-2.")
# CC-2 (Logit B)
obj["CC-2"]["shows"] += (" FE ADDENDUM: under firm + year-quarter FE the coefficient keeps its sign but is insignificant "
  "(LPM 0.0644, SE 0.05076, n.s., N 1,063); only 48/563 firms (8.5%) make BOTH a cash and a stock deal -> too few to "
  "identify within-firm. A firm-FE logit is infeasible (perfect separation: 91% of firms no within variation).")
obj["CC-2"]["caveat"] = ("STOCK ARM UNDERPOWERED (N=123, 88.9% cash base rate) -> same fragility as the C6 Wald. "
  "FE: same sign, insignificant (0.0644 n.s.); only 8.5% dual-arm firms identify it within-firm; logit-FE infeasible. "
  "Frame as direction-consistent + supportive-not-definitive. See ratified caveat-2.")

J["_number_provenance"]["fe"] = ("FE-LPM (Firm + Year-Qtr FE) for both binary tests from fe_results.json; "
  "within-R2 (A 0.003, B 0.059) + dual-arm count (48/563 = 8.5%) independently re-verified (check_fe.py). "
  "Logit-FE infeasible (perfect separation 59%/91%). Tables: logit cols gained a (3) LPM+FE column + FE row.")
J["_fe_addendum_ratified_caveat_2"] = RATIFIED_C2

# ---- GATE ----
fails=[]
def ck(c,ok):
    print(f"  [{'PASS' if ok else 'FAIL'}] {c}");
    if not ok: fails.append(c)
ck("parses + 6 objects", len(J["objects"])==6)
ck("RU-2 FE present", "0.0078" in obj["RU-2"]["shows"])
ck("CC-2 FE present", "0.0644" in obj["CC-2"]["shows"] and "8.5%" in obj["CC-2"]["shows"])
ck("ratified caveat-2 present", "0.0078***" in J["_fe_addendum_ratified_caveat_2"] and "8.5%" in J["_fe_addendum_ratified_caveat_2"])
if fails: print("ABORT",fails); sys.exit(1)
json.dump(J, open(SPEC,"w",encoding="utf-8"), indent=2, ensure_ascii=False)
print("\nSPEC synced to clone. spec<->clone consistent (FE in RU-2/CC-2 + ratified caveat-2).")
