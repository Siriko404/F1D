# Scrub competition from claim_findings (C3/C5), roadmap §2.5, resume. Idempotent; per-file fail-closed.
import json

# --- claim_findings: supersede C3, fix C5 thinnest_claim ---
cf = "docs/Thesis/rewrite/claim_findings_ledger.json"
c = json.load(open(cf, encoding="utf-8"))
claims = c["claims_ranked_strong_to_fragile"]
c3 = next(x for x in claims if x["id"] == "C3_discriminant_validity")
c3["_SUPERSEDED_2026_06_14"] = "DROPPED from the thesis (user): the product-market competition / discriminant test is removed entirely; C3 is no longer used in 2.5. Record kept for history only."
c5 = next(x for x in claims if x["id"] == "C5_convergent_validity")
if "Lean on the discriminant" in c5["thinnest_claim"]:
    c5["thinnest_claim"] = "LEAD with the SIGNIFICANT positive convergent association (one-tailed) of the residual with PRisk/US-EPU/GEPU; keep the economic magnitude (FB) and the one-tailed test as honest SECONDARY qualifiers. (C3/discriminant dropped 2026-06-14; do NOT 'lean on discriminant'.)"
open(cf, "w", encoding="utf-8", newline="\n").write(json.dumps(c, indent=2, ensure_ascii=False) + "\n")
json.load(open(cf, encoding="utf-8"))

# --- roadmap §2.5: remove competition/discriminant (clean, no tombstone words so it greps to zero) ---
rm = "docs/Thesis/rewrite/section2_roadmap.md"
t = open(rm, encoding="utf-8").read()
reps = [
    ("validate the construct (convergent + discriminant)", "validate the construct (convergent validity)"),
    ("State the two demands: the residual must (a) move with real uncertainty, (b) be distinct from competing observable channels (competition; and not merely analyst scrutiny, a plausible alternative driver tested in §4.1).",
     "State the checks: the residual must (a) move with real uncertainty (convergent); and (b) the pre-announcement rise must not be merely analyst scrutiny, a plausible alternative driver tested in §4.1."),
    ('convergent = "consistent with" (weak, disclosed); discriminant = decisive; scrutiny',
     'convergent = LEAD with the significant association (one-tailed; magnitude secondary); scrutiny'),
]
for a, b in reps:
    if a in t:
        t = t.replace(a, b)
# drop the discriminant Must-do line + the hoberg literature mention
lines = []
for ln in t.split("\n"):
    if "Discriminant validity (the decisive evidence)" in ln:
        continue
    if "hoberg" in ln.lower():
        ln = ln.replace(", hoberg2010/2016", "").replace("hoberg2010/2016, ", "").replace("hoberg2010/2016", "").replace(", hoberg2010/hoberg2016", "")
    lines.append(ln)
t = "\n".join(lines)
assert "hoberg" not in t.lower() and "discriminant" not in t.lower() and "competition" not in t.lower(), "roadmap still has competition content"
open(rm, "w", encoding="utf-8", newline="\n").write(t)

# --- resume: status + supersede F1/F2/F3 + hoberg yardstick (tombstones OK) ---
rs = "docs/Thesis/rewrite/_RESUME_STATE.json"
r = json.load(open(rs, encoding="utf-8"))
r["prose_progress_2026_06_13"]["status"]["2.5 (whole)"] = "REDRAFTED 2026-06-14: competition/discriminant test DROPPED completely (P3 gone); FD lead-with-significance + FC appendix pointer applied; FB economic-effect = PLACEHOLDER (summary stats disregarded). 2.5 ledger + claim_findings + roadmap scrubbed. PENDING: push-replace -> remove hoberg bibitems -> compile -> user ratify."
r["_COMPETITION_DROPPED_2026_06_14"] = "Competition/discriminant test dropped from the thesis (user, from PDF). nlm_conflict_audit F1/F2/F3 + validity_yardsticks hoberg2016 are now SUPERSEDED scaffolding (kept for history). Live state: 2.5 has no competition; validity = convergent (P2, significant) + 4.1 scrutiny + 2.3 floor."
r["NEXT_ACTION"] = "Push-replace 2.5 in thesis_draft.tex (keys P1/P2/P4/P5) -> assert zero \\citet{hoberg} -> remove hoberg2010+hoberg2016 bibitems -> compile -> open PDF -> user ratifies 2.3/2.4/2.5. Fill [PLACEHOLDER-FB] in 2.5 P2 after corrected summary stats. Then whole-§2 pass + 2.1-P7 softening. DISCIPLINE: programmatic transfer w/ asserts; numbers from regression tables (summary stats disregarded); SHOW/ratify in PDF; no '---'/'--'."
open(rs, "w", encoding="utf-8", newline="\n").write(json.dumps(r, indent=2, ensure_ascii=False) + "\n")
json.load(open(rs, encoding="utf-8"))
print("scrubbed: claim_findings (C3 superseded, C5 fixed) + roadmap (competition-free) + resume.")
