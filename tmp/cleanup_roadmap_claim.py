# Deferred before-prose sweep: reconcile the NON-deliverable docs (roadmap + claim_findings C4) to the
# scrutiny-driver framing. Numbers + the C4 hedge + the C4 id stay untouched. Fail-closed asserts.
import json

# ---- roadmap (markdown) ----
rp = "docs/Thesis/rewrite/section2_roadmap.md"
t = open(rp, encoding="utf-8").read()
def rep(t, old, new):
    assert old in t, f"MISSING in roadmap: {old[:60]!r}"
    return t.replace(old, new)
t = rep(t, "cash-concentration framed via the visible-position bind, not the ruled-out scrutiny channel.",
    "cash-concentration framed via the visible-position bind, not the scrutiny channel (a plausible alternative driver tested & rejected in §4.1).")
t = rep(t, "State the competing **analyst-scrutiny** reading formally here as the hypothesis §4.1 tests/rules out (gives the rule-out a home).",
    "FLAG the competing **analyst-scrutiny** reading here (lean); its construct + motivation live in §2.5, and §4.1 tests & rejects it.")
t = rep(t, "validate the construct (convergent + discriminant) and pre-empt the scrutiny confound.",
    "validate the construct (convergent + discriminant) and MOTIVATE the scrutiny identification side-test (a plausible alternative driver, tested & rejected in §4.1).")
t = rep(t, "1. State the two demands: the residual must (a) move with real uncertainty, (b) not be a scrutiny artifact.",
    "1. State the two demands: the residual must (a) move with real uncertainty, (b) be distinct from competing observable channels (competition; and not merely analyst scrutiny, a plausible alternative driver tested in §4.1).")
t = rep(t, "4. **Pre-register the scrutiny rule-out** (§4.1 forward-ref): define CashScrutiny/HighCashScrutiny + the three-step logic; frame as \"doesn't account for THIS run-up.\"",
    "4. **Introduce + motivate the scrutiny side-test** (§4.1 forward-ref): define CashScrutiny/HighCashScrutiny, establish validity (CashRatio→CashScrutiny) + plausibility (rises ahead of cash deals); the verdict (\"doesn't account for THIS run-up\") is reported in §4.1, not §2.5.")
t = rep(t, "2. **Cash-concentration mechanism vs the ruled-out scrutiny channel.** §2.1/§2.2 must motivate cash-concentration via the *visible material position under the gag*, NOT via \"analysts ask harder cash questions\" — because §4.1 rules the scrutiny channel out.",
    "2. **Cash-concentration mechanism vs the scrutiny channel (tested & rejected in §4.1).** §2.1/§2.2 must motivate cash-concentration via the *visible material position under the gag*, NOT via \"analysts ask more cash questions\" — because §4.1 tests and rejects the scrutiny channel as the driver.")
open(rp, "w", encoding="utf-8", newline="\n").write(t)
print("roadmap: 6 stale confound/rule-out mandate lines reframed.")

# ---- claim_findings_ledger C4 (keep id + numbers + hedge) ----
cp = "docs/Thesis/rewrite/claim_findings_ledger.json"
d = json.load(open(cp, encoding="utf-8"))
s = json.dumps(d, ensure_ascii=False)
def reps(s, old, new):
    assert old in s, f"MISSING in claim_findings: {old[:60]!r}"
    return s.replace(old, new)
s = reps(s, '"hypothesis": "alternative rule-out"', '"hypothesis": "plausible alternative driver, tested & rejected"')
s = reps(s, "the confound (scrutiny rises pre-announce) is genuine; only the gating interaction kills it, and it is underpowered",
    "the scrutiny rise pre-announce is genuine (a plausible driver); only the gating interaction rejects it, and it is underpowered")
d = json.loads(s)
open(cp, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
print("claim_findings C4: 'alternative rule-out' -> driver framing; risks reworded (id + numbers + hedge untouched).")
print("OK -- before-prose cleanup complete.")
