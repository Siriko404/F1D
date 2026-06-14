# Neutralize stale LIVE competition/convergent-demote lines the blanket notes didn't reach (advisor). Idempotent.
import json

RS = "docs/Thesis/rewrite/_RESUME_STATE.json"
r = json.load(open(RS, encoding="utf-8"))

# 1) WRITE_TIME_FLAGS: drop moot hoberg/fluidity + variable_ledger-'persistent' entries; fix C3/C4/C5 -> C4/C5
fl = r["PENDING_EDITS_unapplied"]["WRITE_TIME_FLAGS"]
kept, dropped = [], 0
for x in fl:
    lo = x.lower()
    if "hoberg" in lo or "fluidity" in lo or ("l188" in lo and "persistent" in lo):
        dropped += 1; continue
    kept.append(x.replace("C3/C4/C5", "C4/C5 (C3 dropped 2026-06-14)"))
if dropped:
    kept.append("[SUPERSEDED 2026-06-14] hoberg2010/'fluidity' (old F2) + the variable_ledger L188 'persistent' flag are MOOT: the competition/discriminant test was DROPPED from the thesis.")
r["PENDING_EDITS_unapplied"]["WRITE_TIME_FLAGS"] = kept

# 2) subsection_loop phase_A_owed 2.5
pa = r.get("subsection_loop_workflow_2026_06_13", {}).get("phase_A_owed_by_subsection", {})
if "2.5" in pa and "hoberg" in pa["2.5"].lower():
    pa["2.5"] = "[2026-06-14 competition DROPPED] Remaining 2.5 owed: reconcile Hassan cite-year; bible cross-check C4/C5 numbers; davis2016 provisional fold-as-is; fill the [PLACEHOLDER-FB] economic effect after corrected summary stats. (hoberg2010/'fluidity', C3, variable_ledger 'persistent' are MOOT.)"

# 3) nlm_conflict_audit -> superseded
if "nlm_conflict_audit_2026_06_13" in r:
    r["nlm_conflict_audit_2026_06_13"]["_SUPERSEDED_2026_06_14"] = "MOOT: the competition/discriminant test (all hoberg/yardstick conflicts F1/F2/F3) was DROPPED from the thesis 2026-06-14. Historical only -- do NOT act on F1/F2/F3."

# 4) validity_yardsticks hoberg2016 -> dropped stamp
vy = r.get("validity_yardsticks_VERIFIED_2026_06_13", {})
k = "hoberg2016 (TNIC competition)"
if k in vy and not vy[k].startswith("[DROPPED"):
    vy[k] = "[DROPPED 2026-06-14 -- competition test removed; this yardstick is no longer used. History:] " + vy[k]

# 5) EDITS_APPLIED 2.5 -> competition-moot note
ea = r.get("EDITS_APPLIED_2026_06_13", {})
if "2.5" in ea and "_competition_dropped_2026_06_14" not in ea:
    ea["_competition_dropped_2026_06_14"] = "The F1/F3 'competition' edits in the 2.5 entry are MOOT (competition/discriminant DROPPED 2026-06-14). The non-competition parts (CashScrutiny foregrounding, convergent fold) remain; convergent later flipped to LEAD-with-significance (FD)."

open(RS, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(RS, encoding="utf-8"))

# CLAIM_FINDINGS: kill the convergent-demote contradiction with FD
CF = "docs/Thesis/rewrite/claim_findings_ledger.json"
c = json.load(open(CF, encoding="utf-8"))
tc = c["thin_claim_ceiling"]
if "C5 convergent validity -> 'consistent with'" in tc["demoted"]:
    tc["demoted"] = tc["demoted"].replace("C5 convergent validity -> 'consistent with'",
        "C5 convergent validity -> LEAD with the significant association (FD override 2026-06-14; was 'consistent with')")
for risk in c.get("cross_cutting_rerun_class_risks", []):
    if "being demoted anyway" in risk.get("impact", ""):
        risk["impact"] = risk["impact"].replace("being demoted anyway", "now LED-with per FD 2026-06-14 (one-tailed caveat kept secondary)")
open(CF, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
json.load(open(CF, encoding="utf-8"))
print(f"neutralized: resume ({dropped} hoberg/persistent flags dropped + 4 blocks stamped) + claim_findings (demote->lead).")
