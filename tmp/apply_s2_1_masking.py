"""Apply the masking redesign to a DURABLE CLONE of section2.1_paragraph_ledger.json.

ZERO-HALLUCINATION CONTRACT:
  - All VERBATIM evidence (query / answer / quotes / located / verdict / verdict_note / nlm id)
    is DEEP-COPIED from verified sources, never re-typed:
      * P5.2 (Shleifer-Vishny) + P5.3 (Louis)  <-  tmp/nlm_masking_cites.json
      * P5.4 (thewissen)                        <-  the in-ledger P6.1 proposition's verification
  - The ONLY hand-authored strings here are `statement` / `role_in_paragraph` (claims, not quotes)
    and the two framing props P5.5 / P5.6 (no verbatim cites -> nothing to hallucinate).
  - Reads the PRISTINE original; writes ONLY the clone. Original is never opened for writing.

Run from anywhere:  python tmp/apply_s2_1_masking.py
"""
import json, copy, sys
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]          # ...\F1D-phase3
REWRITE = FORK / "docs" / "Thesis" / "rewrite"
ORIG = REWRITE / "section2.1_paragraph_ledger.json"   # PRISTINE - read only
CITES = FORK / "tmp" / "nlm_masking_cites.json"       # verified NLM evidence
CLONE_DIR = REWRITE / "_phase3_clones"
CLONE = CLONE_DIR / "section2.1_paragraph_ledger.json"

data = json.loads(ORIG.read_text(encoding="utf-8"))
M = json.loads(CITES.read_text(encoding="utf-8"))


def paragraphs(d):
    if "paragraphs" in d and "P5" in d["paragraphs"]:
        return d["paragraphs"]
    if all(k in d for k in ("P1", "P5", "P7")):
        return d
    raise SystemExit("FATAL: paragraphs container (P1..P7) not found")


PARA = paragraphs(data)
P4, P5, P6 = PARA["P4"], PARA["P5"], PARA["P6"]

# ---- locate the verified evidence to MOVE (copy, never retype) -------------
sv = M["shleifer_vishny2003"]
lo = M["louis2004"]
p6_props = {p["prop_id"]: p for p in P6["propositions"]}
assert "P6.1" in p6_props, "P6.1 (thewissen) not found to source P5.4 evidence"
thew = p6_props["P6.1"]


def nlm_prop(prop_id, statement, role, bibkey, src):
    """Build an external-NLM prop; verification block DEEP-COPIED from `src` (verified)."""
    return {
        "prop_id": prop_id,
        "statement": statement,
        "role_in_paragraph": role,
        "type": "external-NLM",
        "source": {"key": bibkey, "ref": copy.deepcopy(src["label"]),
                   "nlm_source_id": copy.deepcopy(src["id"])},
        "nlm_query_draft": copy.deepcopy(src["query"]),
        "verification": {
            "method": "NLM",
            "source": {"id": copy.deepcopy(src["id"]), "title": copy.deepcopy(src["label"])},
            "query": copy.deepcopy(src["query"]),
            "answer": copy.deepcopy(src["answer"]),
            "quotes": copy.deepcopy(src["quotes"]),
            "located": copy.deepcopy(src["located"]),
            "verdict": copy.deepcopy(src["verdict"]),
            "verdict_note": copy.deepcopy(src["verdict_note"]),
        },
    }


def framing_prop(prop_id, statement, role, note):
    return {
        "prop_id": prop_id,
        "statement": statement,
        "role_in_paragraph": role,
        "type": "framing-nonverifiable",
        "source": {"key": "n/a", "ref": "framing / interpretation -- not a paper-fact",
                   "nlm_source_id": None},
        "nlm_query_draft": "",
        "verification": {"method": "n/a", "evidence": [], "answer_nonevidence": "",
                         "verdict": "INCONCLUSIVE_MANUAL", "verified_date": None, "note": note},
    }


# ---- P5.2  Shleifer-Vishny (MOTIVE leg) -- evidence copied from nlm json ----
p52 = nlm_prop(
    "P5.2",
    "A stock acquirer pays in its own equity -- its acquisition currency; an overvalued bidder "
    "has a powerful incentive to get its equity overvalued so that it can make acquisitions with "
    "stock (a valuation/currency motive).",
    "MOTIVE leg of the masking asymmetry: stock bidders carry a currency-protection incentive "
    "that cash bidders lack. Cite the VALUATION/currency motive ONLY -- never disclosure tone; "
    "do not import the full merger-wave model.",
    "shleifer_vishny2003", sv)

# ---- P5.3  Louis (BEHAVIOR + TIMING leg) -- evidence copied from nlm json ---
p53 = nlm_prop(
    "P5.3",
    "Acquirers act on that motive before the deal: stock-for-stock bidders overstate reported "
    "earnings (positive abnormal accruals) in the quarter immediately preceding the announcement, "
    "whereas cash acquirers do not.",
    "BEHAVIOR+TIMING leg: the currency motive translates into real pre-deal earnings management, "
    "stock-only, in the anticipatory window. Cite as EARNINGS-number management, NOT tone "
    "(thewissen carries the tone link).",
    "louis2004", lo)

# ---- P5.4  thewissen (TONE leg) -- evidence MOVED from the in-ledger P6.1 ----
p54 = {
    "prop_id": "P5.4",
    "statement": "The same pre-deal management reaches disclosure tone: stock bidders inflate the "
                 "tone of earnings press releases by about 15 percent in the year before a "
                 "stock-for-stock acquisition.",
    "role_in_paragraph": "TONE leg (our language axis) of the masking asymmetry -- the step linking "
                         "earnings-number management to disclosure language. SAME evidence as P6.1 "
                         "(deliberate dual role); preprint, supplementary; discloses the "
                         "earnings->tone->Q&A genre-jump openly.",
    "type": copy.deepcopy(thew["type"]),
    "source": copy.deepcopy(thew["source"]),
    "nlm_query_draft": copy.deepcopy(thew.get("nlm_query_draft", "")),
    "verification": copy.deepcopy(thew["verification"]),
}

# ---- P5.5  managed-comparison synthesis (framing) --------------------------
p55 = framing_prop(
    "P5.5",
    "Cash bidders have no equity currency to protect and so lack the parallel pre-deal management "
    "incentive that stock bidders have; we therefore read cash as the (relatively) UNMANAGED window "
    "on the disclosure state and stock as the MANAGED comparison. This MOTIVATES OUR FOCUS ON CASH "
    "DEALS (a positioning/sample choice); the magnitude of the cash-stock gap and why stock sits "
    "lower in our measure are developed in 2.2 (H1a). Masking is motivation, not identification; the "
    "source of the cash uncertainty stays open (P7).",
    "Synthesis of P5.2-P5.4 into the why-cash MOTIVATION for FOCUSING on cash; the concentration "
    "magnitude/differential is 2.2's, not 2.1's. Replaces the old 'stock = placebo / why-open'. "
    "Register: motivation-not-mechanism.",
    "Framing synthesis; not NLM-verifiable. HONESTY FLOOR: our data show cash rising (+0.0461***) "
    "and stock a noisy flat null (-0.0429 n.s.); masking is the ex-ante MOTIVATION -- we interpret, "
    "we do not detect. NO 'stock suppressed' / nothing below baseline. Per advisor 2026-06-26: 2.1 "
    "motivates FOCUS only; the global-disposition byproduct + attenuation that explain the DV-level "
    "gap live in 2.2 (avoids the P5.5/P5.6 firewall contradiction).")

# ---- P5.6  cross-channel bridge (framing) ----------------------------------
p56 = framing_prop(
    "P5.6",
    "The cited management operates on SCRIPTED channels (earnings numbers, prepared press-release "
    "tone); our dependent variable is the unscripted-Q&A residual UncResCEO, which nets out the "
    "scripted presentation (UncPreCEO) and other observable call-level factors (eq-4, 2.3). Reading "
    "the channel hardest to script means the documented tone-management bears LEAST on our measure "
    "-- a strength, not a gap.",
    "Cross-channel BRIDGE closing the earnings/tone -> Q&A genre-jump: defends that the masking "
    "cites (scripted) do not contaminate our unscripted measure.",
    "Framing; not NLM. ANCHOR: 2.3 P2 (UncRes nets UncPre + UncQue + NegCall; DWZ isolation of the "
    "unscripted component; eq-4 control set NLM-verified, Catch-3 closed 2026-06-13). Forward-"
    "reference to 2.3 -- keep as motivation/positioning, not a tested claim.")

# ---- splice: keep P5.1, append the five new props --------------------------
existing = {p["prop_id"]: p for p in P5["propositions"]}
assert "P5.1" in existing, "P5.1 (Harford) missing"
P5["propositions"] = [existing["P5.1"], p52, p53, p54, p55, p56]

# ---- P5 plan-field rewrites (placebo / why-open -> managed comparison / motivated) ----
P5["intent"] = (
    "Cash and stock deals share the disclosure bind but differ in TWO design-relevant ways: "
    "(a) a cash purchase draws on an accumulated, visible balance-sheet position -- a war chest -- "
    "that a stock deal need not; and (b) a stock bidder pays in equity, a currency whose price it "
    "has reason to manage, so stock bidders carry a documented pre-deal incentive to manage their "
    "narrative (overvaluation motive, Shleifer-Vishny; pre-deal earnings management, Louis; "
    "press-release tone, thewissen) that cash bidders lack. We therefore read cash as the "
    "(relatively) UNMANAGED window where the disclosure strain surfaces, and stock as the MANAGED "
    "comparison; this MOTIVATES why the signal concentrates in cash (motivation, NOT identification "
    "-- the source stays open, P7). A cross-channel bridge notes our DV is the unscripted-Q&A "
    "residual net of the scripted presentation, so the cited (scripted) management bears least on "
    "our measure. The two clocks then diverge: uncertainty tracks the information and resolves at "
    "announcement; the cash position serves the purchase and -- mechanically -- persists to "
    "completion.")
P5["serves"] = (
    "Reviews cash-holdings literature AND establishes the masking-asymmetry MOTIVATION for the cash "
    "concentration; sets up CASH as the design contrast + UNMANAGED read and STOCK as the MANAGED "
    "comparison (-> H1a, -> MA3); frames differential-timing CONTRAST (-> H1b), cash-persistence "
    "leg labeled mechanical.")
P5["thin_claim"] = (
    "A where-it-appears CONTRAST plus an ex-ante MOTIVATION (the masking asymmetry) for why it "
    "concentrates in cash; the source mechanism stays open; the cash-persistence leg is mechanical. "
    "No identification; no claim that stock uncertainty is suppressed below baseline.")
assert "DESIGN CONTRAST only" in P5["boundary"]
P5["boundary"] = P5["boundary"] + (
    " | MASKING: develop the differential/attenuation argument in 2.2 (H1a), NOT here. Masking = "
    "MOTIVATION; no mechanism, no stock-suppression claim. Keep the 4.1 scrutiny channel OUT "
    "(never 'visible cash -> analysts probe -> hedge').")

# guardrails: augment the two existing, append the masking register guardrail
g = P5["guardrails"]
for i, s in enumerate(g):
    if s.startswith("ADVISOR_FIX_contrast (A2)"):
        g[i] = ("ADVISOR_FIX_contrast (A2): stock = same setting minus visible cash, PLUS the "
                "masking MOTIVE (currency-protection) now marks stock as the MANAGED comparison "
                "(not an inert placebo). The SOURCE mechanism stays OPEN (P7); masking is "
                "MOTIVATION, not a tested channel.")
    if s.startswith("DROPPED P5.2 (Bates 2009 / Opler 1999)"):
        g[i] = ("DROPPED (a slot once labeled 'P5.2'): Bates 2009 / Opler 1999 'analysts watch "
                "cash' -- one step from the FORBIDDEN scrutiny channel (visible cash -> analysts "
                "probe -> CEO hedges) that 4.1 rules out; dropped on the GUARDRAIL, not "
                "availability. RENUMBER NOTE: the masking redesign's NEW P5.2/P5.3 are "
                "Shleifer-Vishny / Louis -- unrelated to this dropped Bates/Opler item.")
g.append(
    "MASKING register (advisor 2026-06-26): cite Shleifer-Vishny + Louis as EARNINGS/VALUATION, "
    "NEVER tone (miscite = referee kill-shot). thewissen = tone, preprint, supplementary. Masking "
    "= MOTIVATION not mechanism. NO 'stock suppressed' -- data show stock -0.0429 n.s. (noisy flat "
    "null), nothing below baseline; the differential/attenuation lives in 2.2, not 2.1. Bridge "
    "(P5.6) anchored to 2.3 P2 (UncRes nets UncPre).")

# ---- P5 prose gate: BLOCK final_prose pending chain ratification + rewrite ---
P5["prose_gate"] = {
    "rule": "MASKING REDESIGN 2026-06-26: P5.1 SUPPORTED; P5.2 (S-V) + P5.3 (Louis) SUPPORTED (NLM, "
            "evidence copied verbatim from nlm_masking_cites.json); P5.4 (thewissen) SUPPORTED "
            "(evidence = P6.1); P5.5 + P5.6 framing (INCONCLUSIVE_MANUAL). final_prose BLOCKED until "
            "Sina ratifies the redesigned chain, then rewrite.",
    "all_supported": False,
    "unlocked": False,
}
P5["final_prose_PRE_MASKING"] = P5.get("final_prose", "")
P5["final_prose"] = ""
P5["prose_status"] = ("BLOCKED_PENDING_MASKING_REWRITE (chain redesigned 2026-06-26; old prose "
                      "preserved in final_prose_PRE_MASKING; rewrite only after Sina ratifies the "
                      "chain)")

# ---- P4 guardrail: placebo -> comparison, isolate -> motivate --------------
hit = 0
for i, s in enumerate(P4["guardrails"]):
    if "the P5 placebo + timing design isolate it" in s:
        P4["guardrails"][i] = s.replace("the P5 placebo + timing design isolate it",
                                        "the P5 comparison + timing design motivate the concentration")
        hit += 1
assert hit == 1, f"P4 guardrail placebo-string not found exactly once (got {hit})"

# ---- _plan sweep (cash-why only; leave claim_ceiling / source-why open) -----
plan = data["_plan"]
assert "placebo" in plan["logic_chain_validated"]["P4_necessity"]
plan["logic_chain_validated"]["P4_necessity"] = plan["logic_chain_validated"]["P4_necessity"].replace(
    "the P5 placebo + timing design do",
    "the P5 comparison + timing design motivate the concentration")
plan["logic_chain_validated"]["A2_contrast"] = (
    "P5: do NOT assert a cash-sharpens-the-bind mechanism (= the ruled-out scrutiny channel). Cash "
    "is a DESIGN CONTRAST (stock = same gag minus visible cash); concentration informative on its "
    "own; WHY-cash now MOTIVATED by the masking asymmetry (S-V currency motive + Louis pre-deal "
    "behavior + thewissen tone) -- motivation, NOT identification; the SOURCE mechanism stays open "
    "(P7).")
plan["spine"] = plan["spine"].replace(
    "P5 cash design-contrast -> concentration + two clocks.",
    "P5 cash design-contrast + masking MOTIVE (currency-protection asymmetry) -> motivated "
    "concentration + two clocks.")
assert data["_governing"]["claim_ceiling"].count("WHY") >= 1  # untouched (source-why stays open)

# ---- provenance + write CLONE (original untouched) -------------------------
data["revised"] = data.get("revised", "") + (
    " | 2026-06-26 MASKING REDESIGN (clone): P5 rebuilt -- P5.2 S-V motive, P5.3 Louis behavior, "
    "P5.4 thewissen tone (evidence moved from P6.1), P5.5 managed-comparison, P5.6 cross-channel "
    "bridge; P4 guardrail + _plan A2/P4_necessity/spine swept placebo->comparison; final_prose "
    "BLOCKED. Evidence for new NLM props deep-copied from tmp/nlm_masking_cites.json (zero retype).")
data["_clone_provenance"] = {
    "is_clone": True, "of": "section2.1_paragraph_ledger.json (pristine original)",
    "purpose": "Phase-3 masking proposition redesign -- collaborative, ratify-before-retire.",
    "evidence_integrity": "P5.2/P5.3 verification deep-copied from tmp/nlm_masking_cites.json; "
                          "P5.4 from in-ledger P6.1. No quote/answer/verdict typed by hand.",
    "built_by": "tmp/apply_s2_1_masking.py", "date": "2026-06-26",
}

CLONE_DIR.mkdir(parents=True, exist_ok=True)
CLONE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

# ---- integrity proof (printed so the copy can be audited) ------------------
def first(q):
    return (q[0]["cited_text"][:55] + "...") if q else "(none)"

print(f"CLONE written: {CLONE.relative_to(FORK)}")
print(f"original bytes unchanged: {ORIG.stat().st_size}")
print("-" * 72)
print("P5 propositions now:", [p["prop_id"] for p in P5["propositions"]])
for pid, src_name, prop in [("P5.2", "nlm:S-V", p52), ("P5.3", "nlm:Louis", p53),
                            ("P5.4", "ledger:P6.1", p54)]:
    v = prop["verification"]
    print(f"  {pid} <- {src_name}: verdict={v['verdict']}  quotes={len(v['quotes'])}  "
          f"located={len(v['located'])}")
    print(f"       first cited_text: {first(v['quotes'])}")
print("  P5.5 framing:", p55["verification"]["verdict"], "| P5.6 framing:", p56["verification"]["verdict"])
print("-" * 72)
# prove the copy is byte-identical to the verified source
assert p52["verification"]["quotes"] == sv["quotes"], "S-V quotes copy MISMATCH"
assert p52["verification"]["verdict_note"] == sv["verdict_note"], "S-V verdict_note copy MISMATCH"
assert p53["verification"]["quotes"] == lo["quotes"], "Louis quotes copy MISMATCH"
assert p53["verification"]["located"] == lo["located"], "Louis located copy MISMATCH"
assert p54["verification"] == thew["verification"], "thewissen verification copy MISMATCH"
print("INTEGRITY OK: S-V / Louis / thewissen evidence == verified source (byte-identical).")
print("placebo sweep -> P4 guardrail, P5.intent/serves/final_prose, _plan A2/P4_necessity/spine.")
print("UNTOUCHED: P1 P2 P3 P6 P7 props; _governing.claim_ceiling (source-why stays open).")
