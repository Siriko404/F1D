# Sweep stale METADATA across the section ledgers + 1 stale word in claim_findings.
# RESUMABLE: each block skips if already applied (a prior partial run saved 2.1/2.2/2.3).
# History preserved (next_action logs get a CURRENT banner; nothing deleted). Zero plan/number changes.
import json

R = "docs/Thesis/rewrite/"
def load(f): return json.load(open(R+f, encoding="utf-8"))
def save(f, d): open(R+f, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")

BANNER = "[CURRENT 2026-06-13 -- read FIRST; everything after '||' is SUPERSEDED historical log] "
def banner(s, truth):
    if "read FIRST" in s: return s, False           # already swept
    return BANNER + truth + " || " + s, True

done = []

# --- 2.1: header in_progress/P3 -> LOCKED (P1-P7 in thesis_draft.tex) ---
d = load("section2.1_paragraph_ledger.json")
if d["status"] == "in_progress":
    assert d["current_paragraph"] == "P3"
    d["status"] = "LOCKED 2026-06-13 -- P1-P7 committed to thesis_draft.tex (superseded prior 'in_progress')"
    d["current_paragraph"] = "DONE (all P1-P7 locked in .tex; prior value was 'P3')"
    save("section2.1_paragraph_ledger.json", d); done.append("2.1 header")
else:
    assert d["status"].startswith("LOCKED"), d["status"]

# --- 2.2: header 'Prose BLOCKED' (P1+P2 recorded) + next_action 'NOT re-ratified' landmine ---
d = load("section2.2_paragraph_ledger.json")
if "Prose still BLOCKED" in d["_schema"]["status"]:
    d["_schema"]["status"] = ("RE-RATIFIED 2026-06-13 after the scrutiny reframe; all four subsections (2.2-2.5) ratified. "
        "PROSE IN PROGRESS (ledger-first): P1+P2 recorded, P3-P5 pending.")
    done.append("2.2 _schema.status")
if d["status"].endswith("Prose BLOCKED."):
    d["status"] = d["status"][:-len("Prose BLOCKED.")] + "RE-RATIFIED; PROSE IN PROGRESS (P1+P2 recorded; P3-P5 pending)."
    done.append("2.2 status")
nx, ch = banner(d["next_action"], "2.2 RE-RATIFIED + all four (2.2-2.5) ratified; now PROSE phase (ledger-first): "
    "P1+P2 recorded, P3-P5 pending. The 'RE-RATIFY 2.2 from the beginning / NOT re-ratified' directives below are DONE")
if ch: d["next_action"] = nx; done.append("2.2 next_action")
save("section2.2_paragraph_ledger.json", d)

# --- 2.3/2.4/2.5: top-level status=RATIFIED authoritative; next_action logs describe pre-ratification state ---
for f, truth in [
    ("section2.3_paragraph_ledger.json", "2.3 RATIFIED (top-level status authoritative); prose pending its turn in ledger-first drafting. The 'NOT ratified / RE-RATIFY' fragments below are superseded"),
    ("section2.4_paragraph_ledger.json", "2.4 RATIFIED; prose pending its turn. The 'hand to user for ratification' step below is DONE/superseded"),
    ("section2.5_paragraph_ledger.json", "2.5 RATIFIED (last subsection); prose pending its turn. The 'NOT ratified' fragments below are superseded"),
]:
    d = load(f)
    assert d["status"].startswith("RATIFIED"), (f, d["status"])
    nx, ch = banner(d["next_action"], truth)
    if ch: d["next_action"] = nx; save(f, d); done.append(f.split("_")[0][-3:] + " next_action")

# --- claim_findings: C3 'persistent industry condition' (F1 retired 'persistent') ---
d = load("claim_findings_ledger.json")
c3 = next(c for c in d["claims_ranked_strong_to_fragile"] if c["id"] == "C3_discriminant_validity")
OLD = "A persistent industry condition surfaces in the scripted presentation, not in the call-varying residual."
NEW = "A known, disclosable industry condition surfaces in the scripted presentation, not in the call-varying residual."
if c3["claim"] == OLD:
    c3["claim"] = NEW; save("claim_findings_ledger.json", d); done.append("claim_findings C3")
else:
    assert c3["claim"] == NEW, c3["claim"]

# --- validate all reload + reality checks ---
for f in ["section2.1_paragraph_ledger.json","section2.2_paragraph_ledger.json","section2.3_paragraph_ledger.json",
          "section2.4_paragraph_ledger.json","section2.5_paragraph_ledger.json","claim_findings_ledger.json"]:
    json.load(open(R+f, encoding="utf-8"))
d22 = load("section2.2_paragraph_ledger.json")
assert "Prose BLOCKED" not in d22["_schema"]["status"] and not d22["status"].endswith("Prose BLOCKED.")
assert load("section2.1_paragraph_ledger.json")["status"].startswith("LOCKED")
assert "persistent industry condition" not in json.dumps(load("claim_findings_ledger.json"))
print("sweep complete. applied this run:", done or "(nothing -- all already swept)")
