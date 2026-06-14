# Advisor catch: neutralize the false cite phrase IN PLACE (the prepended correction left the
# original false sentence physically intact -> a keyword scan could still hit it). Also tidy the
# mission's "NOW in the PROSE phase: drafting" vs appended "PROSE PHASE COMPLETE" contradiction.
import json
import pathlib

RS = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite\_RESUME_STATE.json")
r = json.loads(RS.read_text(encoding="utf-8"))

# 1. kill the live false clause in the old portion of PENDING_EDITS._note
pe = r["PENDING_EDITS_unapplied"]
OLD1 = "cites that are already in the prose + bibliography"
assert pe["_note"].count(OLD1) == 1, f"expected 1 live occ of OLD1, got {pe['_note'].count(OLD1)}"
pe["_note"] = pe["_note"].replace(
    OLD1, "cites (these are NOT in the draft -- verified 2026-06-14; moot, see the correction above)")

# 2. tidy the mission stale-vs-complete contradiction
OLD2 = ("NOW in the PROSE phase: drafting each paragraph into its ledger's final_prose "
        "(LEDGER-FIRST; .tex push deferred).")
assert r["mission"].count(OLD2) == 1, f"expected 1 occ of OLD2, got {r['mission'].count(OLD2)}"
r["mission"] = r["mission"].replace(OLD2, "[PROSE PHASE COMPLETE 2026-06-14 -- see the UPDATE below].")

RS.write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
r2 = json.loads(RS.read_text(encoding="utf-8"))  # fail-closed
assert OLD1 not in r2["PENDING_EDITS_unapplied"]["_note"], "false clause still live"
assert OLD2 not in r2["mission"], "mission contradiction still live"
print("OK: false cite clause neutralized in-place; mission tidied; JSON valid.")
