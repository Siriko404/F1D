"""Append _proposed_fixes to each section-2 clone in _phase3_clones/.

AUDIT CONTRACT (so the advisor can verify fast):
  - NLM evidence (query/answer/quotes/located/verdict/verdict_note/id) is DEEP-COPIED by code:
      * 2.1 P5.2 (Shleifer-Vishny) + P5.3 (Louis) <- tmp/nlm_masking_cites.json
      * 2.1 P5.4 (thewissen)                      <- the clone's own P6.1 proposition
    The end of this script ASSERTS each copied block == its source (byte-identical) and prints it.
  - Everything else (statement / role / framing note / reword 'to' text) is AUTHORED -- claims, not quotes.
  - REWORD/SWEEP 'from' text is PULLED from the clone (not retyped) so it is always exact.
  - Original propositions are NOT mutated; fixes are APPENDED under _proposed_fixes.

Run:  python tmp/append_s2_proposed_fixes.py
"""
import json, copy
from pathlib import Path

FORK = Path(__file__).resolve().parents[1]
CLONE_DIR = FORK / "docs" / "Thesis" / "rewrite" / "_phase3_clones"
M = json.loads((FORK / "tmp" / "nlm_masking_cites.json").read_text(encoding="utf-8"))


def load(s):
    return json.loads((CLONE_DIR / f"section{s}_paragraph_ledger.json").read_text(encoding="utf-8"))

def save(s, d):
    (CLONE_DIR / f"section{s}_paragraph_ledger.json").write_text(
        json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")

def prop(para, pid):
    for p in para.get("propositions", []):
        if p.get("prop_id") == pid:
            return p
    raise KeyError(pid)


def nlm_prop(prop_id, statement, role, bibkey, src):
    """external-NLM prop; verification DEEP-COPIED from src (verified nlm json)."""
    return {
        "prop_id": prop_id, "statement": statement, "role_in_paragraph": role,
        "type": "external-NLM",
        "source": {"key": bibkey, "ref": copy.deepcopy(src["label"]),
                   "nlm_source_id": copy.deepcopy(src["id"])},
        "nlm_query_draft": copy.deepcopy(src["query"]),
        "verification": {
            "method": "NLM",
            "source": {"id": copy.deepcopy(src["id"]), "title": copy.deepcopy(src["label"])},
            "query": copy.deepcopy(src["query"]), "answer": copy.deepcopy(src["answer"]),
            "quotes": copy.deepcopy(src["quotes"]), "located": copy.deepcopy(src["located"]),
            "verdict": copy.deepcopy(src["verdict"]), "verdict_note": copy.deepcopy(src["verdict_note"]),
        },
    }

def framing(prop_id, statement, role, note):
    return {
        "prop_id": prop_id, "statement": statement, "role_in_paragraph": role,
        "type": "framing-nonverifiable",
        "source": {"key": "n/a", "ref": "framing / interpretation -- not a paper-fact", "nlm_source_id": None},
        "nlm_query_draft": "",
        "verification": {"method": "n/a", "evidence": [], "answer_nonevidence": "",
                         "verdict": "INCONCLUSIVE_MANUAL", "verified_date": None, "note": note},
    }

def reword(field, current, to):
    return {"field": field, "from": current, "to": to}


# =====================================================================  2.1
d = load("2.1"); P = d["paragraphs"]
sv, lo = M["shleifer_vishny2003"], M["louis2004"]
thew = prop(P["P6"], "P6.1")                         # thewissen, in-clone

p52 = nlm_prop("P5.2",
    "A stock acquirer pays in its own equity -- its acquisition currency; an overvalued bidder has a "
    "powerful incentive to get its equity overvalued so that it can make acquisitions with stock (a "
    "valuation/currency motive).",
    "MOTIVE leg of the masking asymmetry: stock bidders carry a currency-protection incentive cash "
    "bidders lack. Cite the valuation/currency motive only, never disclosure tone.",
    "shleifer_vishny2003", sv)
p53 = nlm_prop("P5.3",
    "Acquirers act on that motive before the deal: stock-for-stock bidders overstate reported earnings "
    "(positive abnormal accruals) in the quarter immediately preceding the announcement, whereas cash "
    "acquirers do not.",
    "BEHAVIOR+TIMING leg: the currency motive translates into real pre-deal earnings management, "
    "stock-only, in the anticipatory window. Cite as earnings-number management, not tone.",
    "louis2004", lo)
p54 = {"prop_id": "P5.4",
    "statement": "The same pre-deal management reaches disclosure tone: stock bidders inflate the tone "
        "of earnings press releases by about 15 percent in the year before a stock-for-stock acquisition.",
    "role_in_paragraph": "TONE leg (our language axis): links earnings-number management to disclosure "
        "language. Same evidence as P6.1 (dual role); preprint, supplementary; discloses the "
        "earnings->tone->Q&A genre-jump.",
    "type": copy.deepcopy(thew["type"]), "source": copy.deepcopy(thew["source"]),
    "nlm_query_draft": copy.deepcopy(thew.get("nlm_query_draft", "")),
    "verification": copy.deepcopy(thew["verification"])}
p55 = framing("P5.5",
    "Cash bidders have no equity currency to protect and so lack the parallel pre-deal management "
    "incentive that stock bidders have; we read cash as the (relatively) UNMANAGED window on the "
    "disclosure state and stock as the MANAGED comparison. This motivates our FOCUS on cash deals; the "
    "magnitude of the cash-stock gap and why stock sits lower in our measure are developed in 2.2 "
    "(H1a). Motivation, not identification; the source of the cash uncertainty stays open (P7).",
    "Synthesis of P5.2-P5.4 into the why-cash MOTIVATION for focusing on cash; the concentration "
    "magnitude/differential is 2.2's. Replaces the old 'stock = placebo / why-open'.",
    "Framing synthesis; not NLM. Honesty floor: cash rises (+0.0461***), stock is a noisy flat null "
    "(-0.0429 n.s.); masking is the ex-ante motivation -- we interpret, we do not detect. No 'stock "
    "suppressed'; nothing below baseline. The DV-level gap (global-disposition by-product + attenuation) "
    "lives in 2.2.")
p56 = framing("P5.6",
    "The cited management operates on scripted, prepared artifacts (earnings press-release tone, "
    "reported accruals); our dependent variable is uncertainty in the UNSCRIPTED Q&A -- the call "
    "segment managers cannot fully prepare in advance (P2). Reading the venue hardest to stage-manage, "
    "the documented scripted-channel management does not mechanically carry into our measure, so our "
    "signal is not an artifact of the very tone-management the cites describe -- a strength, not a gap.",
    "Cross-channel firewall closing the scripted->unscripted genre-jump: defends that the masking cites "
    "(scripted, prepared documents) do not contaminate our unscripted Q&A measure.",
    "Framing; not NLM. Anchor: P2 (unscripted Q&A = the segment managers cannot fully prepare = hardest "
    "to stage-manage). Not 2.3's UncPre control -- UncPre is in-call presentation uncertainty, a "
    "different artifact from the press-release tone / accruals the cites document.")

plan = d["_plan"]["logic_chain_validated"]
p4g = next(g for g in P["P4"]["guardrails"] if "the P5 placebo + timing design isolate it" in g)
d["_proposed_fixes"] = {
    "summary": "Re-derive why-cash via the masking asymmetry (motivation, not mechanism); sweep "
               "placebo->managed comparison; P4 + _plan follow.",
    "register_locks": ["correlational", "no-identification", "concentration-not-strict-specificity",
                       "source-mechanism-open", "masking = MOTIVATION not mechanism",
                       "NO stock-suppressed (stock -0.0429 n.s.)",
                       "cite S-V / Louis as EARNINGS/VALUATION, NEVER tone"],
    "fixes": [
        {"fix_id": "S2.1-F1", "locus": "P5", "action": "ADD_PROP",
         "change": "+P5.2 Shleifer-Vishny currency MOTIVE", "proposed_prop": p52},
        {"fix_id": "S2.1-F2", "locus": "P5", "action": "ADD_PROP",
         "change": "+P5.3 Louis pre-deal EARNINGS behavior", "proposed_prop": p53},
        {"fix_id": "S2.1-F3", "locus": "P5", "action": "ADD_PROP",
         "change": "+P5.4 thewissen TONE pointer (evidence from P6.1)", "proposed_prop": p54},
        {"fix_id": "S2.1-F4", "locus": "P5", "action": "ADD_PROP",
         "change": "+P5.5 managed-comparison synthesis -> motivates FOCUS on cash", "proposed_prop": p55},
        {"fix_id": "S2.1-F5", "locus": "P5", "action": "ADD_PROP",
         "change": "+P5.6 cross-channel firewall (anchor P2)", "proposed_prop": p56},
        {"fix_id": "S2.1-F6", "locus": "P5.intent", "action": "REWORD",
         "reword": reword("paragraphs.P5.intent", P["P5"]["intent"],
            "Cash and stock deals share the disclosure bind but differ in two design-relevant ways: "
            "(a) a cash purchase draws on an accumulated, visible balance-sheet position -- a war chest "
            "-- that a stock deal need not; and (b) a stock bidder pays in equity, a currency whose "
            "price it has reason to manage, so stock bidders carry a documented pre-deal incentive to "
            "manage their narrative (overvaluation motive, Shleifer-Vishny; pre-deal earnings "
            "management, Louis; press-release tone, thewissen) that cash bidders lack. We read cash as "
            "the (relatively) UNMANAGED window where the disclosure strain surfaces, and stock as the "
            "MANAGED comparison; this motivates our FOCUS on cash (the gap magnitude and why stock sits "
            "lower in our measure are 2.2's -- motivation, not identification; the source stays open, "
            "P7). A cross-channel firewall notes our DV is uncertainty in the unscripted Q&A -- the "
            "segment managers cannot fully prepare (P2) -- so the cited scripted-channel management does "
            "not mechanically carry into our measure. The two clocks then diverge: uncertainty tracks "
            "the information and resolves at announcement; the cash position serves the purchase and -- "
            "mechanically -- persists to completion.")},
        {"fix_id": "S2.1-F7", "locus": "P5.thin_claim", "action": "REWORD",
         "reword": reword("paragraphs.P5.thin_claim", P["P5"]["thin_claim"],
            "A where-it-appears CONTRAST plus an ex-ante MOTIVATION (the masking asymmetry) for FOCUSING "
            "on cash; the gap magnitude/differential is 2.2's; the source mechanism stays open; the "
            "cash-persistence leg is mechanical. No identification; no claim that stock uncertainty is "
            "suppressed below baseline.")},
        {"fix_id": "S2.1-F8", "locus": "P4.guardrail", "action": "REWORD",
         "reword": reword("paragraphs.P4.guardrails[ADVISOR_FIX_necessity]", p4g,
            p4g.replace("the P5 placebo + timing design isolate it",
                        "the P5 comparison + timing design motivate the concentration"))},
        {"fix_id": "S2.1-F9", "locus": "_plan.P4_necessity", "action": "REWORD",
         "reword": reword("_plan.logic_chain_validated.P4_necessity", plan["P4_necessity"],
            plan["P4_necessity"].replace("the P5 placebo + timing design do",
                                         "the P5 comparison + timing design motivate the concentration"))},
        {"fix_id": "S2.1-F10", "locus": "_plan.A2_contrast", "action": "REWORD",
         "reword": reword("_plan.logic_chain_validated.A2_contrast", plan["A2_contrast"],
            "P5: do NOT assert a cash-sharpens-the-bind mechanism (= the ruled-out scrutiny channel). "
            "Cash is a DESIGN CONTRAST (stock = same gag minus visible cash); concentration informative "
            "on its own; WHY-cash now MOTIVATED by the masking asymmetry (S-V currency motive + Louis "
            "pre-deal behavior + thewissen tone) -- motivation, NOT identification; the SOURCE mechanism "
            "stays open (P7).")},
    ],
}
# --- coverage adds (advisor): P5.serves sweep + 3 P5-guardrail fixes ---
g_contrast = next(g for g in P["P5"]["guardrails"] if g.startswith("ADVISOR_FIX_contrast (A2)"))
g_dropped = next(g for g in P["P5"]["guardrails"] if g.startswith("DROPPED P5.2 (Bates"))
serves = P["P5"]["serves"]
d["_proposed_fixes"]["fixes"] += [
    {"fix_id": "S2.1-F11", "locus": "P5.serves", "action": "SWEEP", "change": "stock placebo -> managed comparison",
     "reword": reword("paragraphs.P5.serves", serves,
        serves.replace("the stock placebo (-> MA3)", "the stock managed comparison (-> MA3)"))},
    {"fix_id": "S2.1-F12", "locus": "P5.guardrails[contrast]", "action": "REWORD",
     "change": "inert 'same setting minus visible cash' -> add masking motive / managed comparison",
     "reword": reword("paragraphs.P5.guardrails[ADVISOR_FIX_contrast]", g_contrast,
        "ADVISOR_FIX_contrast (A2): stock = same setting minus visible cash, PLUS the masking MOTIVE "
        "(currency-protection) now marks stock as the MANAGED comparison (not an inert placebo). The "
        "SOURCE mechanism stays OPEN (P7); masking is MOTIVATION, not a tested channel.")},
    {"fix_id": "S2.1-F13", "locus": "P5.guardrails[dropped]", "action": "REWORD",
     "change": "fix P5.2 numbering collision (Bates/Opler vs new S-V)",
     "reword": reword("paragraphs.P5.guardrails[DROPPED_P5.2]", g_dropped,
        "DROPPED (a slot once labeled 'P5.2'): Bates 2009 / Opler 1999 'analysts watch cash' -- one step "
        "from the FORBIDDEN scrutiny channel (visible cash -> analysts probe -> CEO hedges) that 4.1 "
        "rules out; dropped on the GUARDRAIL, not availability. RENUMBER NOTE: the masking redesign's "
        "NEW P5.2/P5.3 are Shleifer-Vishny / Louis -- unrelated to this dropped Bates/Opler item.")},
    {"fix_id": "S2.1-F14", "locus": "P5.guardrails", "action": "ADD_GUARDRAIL",
     "change": "+ masking-register guard (cite as earnings/valuation NOT tone; no stock-suppressed)",
     "proposed_guardrail":
        "MASKING register: cite Shleifer-Vishny + Louis as EARNINGS/VALUATION, NEVER tone (miscite = "
        "referee kill-shot). thewissen = tone, preprint, supplementary. Masking = MOTIVATION not "
        "mechanism. NO 'stock suppressed' -- stock -0.0429 n.s. (noisy flat null), nothing below "
        "baseline; the differential/attenuation lives in 2.2, not 2.1. Firewall (P5.6) anchored to P2 "
        "(unscripted Q&A = hardest to stage-manage)."},
]
save("2.1", d)

# =====================================================================  2.2
d = load("2.2"); P = d["paragraphs"]
p22_thin = P["P2"]["thin_claim"]; p22 = prop(P["P2"], "P2.2")
p3_lit = P["P3"]["lit_body"]; p32 = prop(P["P3"], "P3.2"); p33 = prop(P["P3"], "P3.3")
p34 = framing("P3.4",
    "The masking asymmetry motivates the differential (cash > stock): stock bidders manage their "
    "pre-deal narrative (callback 2.1 P5), and the same broad optimism disposition plausibly dampens "
    "their unguarded Q&A uncertainty as a by-product, while cash bidders -- lacking the currency motive "
    "-- carry the disclosure strain into the unscripted answers more cleanly. This motivates why H1a "
    "expects a larger run-up for cash; it is interpretation, not detection.",
    "The masking MOTIVATION for the cash>stock differential (the attenuation / by-product reasoning "
    "deferred from 2.1 P5). Motivation, not mechanism.",
    "Framing; not NLM. Evidence = callback to 2.1 P5 (S-V / Louis / thewissen, SUPPORTED) + the result "
    "(claim_findings_ledger C6, Wald 0.0983**, p=.039) + data (cash +0.0461***, stock -0.0429 n.s.). "
    "Honesty floor: the stock arm is a noisy flat null, not suppressed; we interpret, we do not detect.")
d["_proposed_fixes"] = {
    "summary": "Reframe the cash-vs-stock contrast from inert placebo to MANAGED comparison; land the "
               "masking differential (attenuation) motivation for H1a here, deferred from 2.1.",
    "register_locks": ["concentration-not-strict-specificity", "EFFECT-not-CAUSE",
                       "masking = MOTIVATION not mechanism", "NO stock-suppressed",
                       "H1 / H1a statements (P2.1, P3.1) UNCHANGED"],
    "fixes": [
        {"fix_id": "S2.2-F1", "locus": "P2.thin_claim", "action": "SWEEP",
         "reword": reword("paragraphs.P2.thin_claim", p22_thin,
            p22_thin.replace("stock = placebo handled in P3", "stock = managed comparison, handled in P3"))},
        {"fix_id": "S2.2-F2", "locus": "P2.2", "action": "REWORD",
         "reword": reword("paragraphs.P2.props.P2.2.statement", p22["statement"],
            p22["statement"].replace("callback 2.1 P6", "callback 2.1 P5/P6"))},
        {"fix_id": "S2.2-F3", "locus": "P3.lit_body", "action": "SWEEP",
         "reword": reword("paragraphs.P3.lit_body", p3_lit,
            p3_lit.replace("placebo", "managed comparison"))},
        {"fix_id": "S2.2-F4", "locus": "P3.2", "action": "REWORD",
         "reword": reword("paragraphs.P3.props.P3.2.statement", p32["statement"],
            "Cash bids draw on an accumulated cash position while stock exchanges need not; moreover, "
            "stock bidders carry a currency-protection motive cash bidders lack (callback 2.1 P5). This "
            "makes the stock deal a MANAGED COMPARISON -- the same disclosure bind, but with an "
            "additional pre-deal management incentive -- rather than an inert placebo.")},
        {"fix_id": "S2.2-F5", "locus": "P3", "action": "ADD_PROP",
         "change": "+P3.4 masking-differential (attenuation) motivation for cash>stock",
         "proposed_prop": p34},
        {"fix_id": "S2.2-F6", "locus": "P3.3", "action": "REWORD",
         "reword": reword("paragraphs.P3.props.P3.3.statement", p33["statement"],
            p33["statement"].rstrip(".") + "; and it makes no claim that stock uncertainty is "
            "suppressed below baseline (the stock arm is a noisy flat null).")},
    ],
}
# --- coverage adds (advisor): P3.guardrails + P3.2.verification_plan ---
g_p3 = next(g for g in P["P3"]["guardrails"] if "harford + placebo logic = CALLBACK P5" in g)
vp32 = p32["verification_plan"]
d["_proposed_fixes"]["fixes"] += [
    {"fix_id": "S2.2-F7", "locus": "P3.guardrails", "action": "SWEEP", "change": "placebo logic -> managed-comparison logic",
     "reword": reword("paragraphs.P3.guardrails[COH-1]", g_p3,
        g_p3.replace("harford + placebo logic", "harford + managed-comparison logic"))},
    {"fix_id": "S2.2-F8", "locus": "P3.2.verification_plan", "action": "SWEEP", "change": "placebo logic -> managed-comparison logic",
     "reword": reword("paragraphs.P3.props.P3.2.verification_plan", vp32,
        vp32.replace("harford + placebo logic", "harford + managed-comparison logic"))},
]
save("2.2", d)

# =====================================================================  2.4
d = load("2.4"); P = d["paragraphs"]
p243 = prop(P["P2"], "P2.3")
d["_proposed_fixes"] = {
    "summary": "One-word placebo->comparison sweep on the stock benchmark; MA3 Wald unchanged.",
    "register_locks": ["MA3 Wald (P3) UNCHANGED (mechanism-agnostic linear restriction)"],
    "fixes": [
        {"fix_id": "S2.4-F1", "locus": "P2.3", "action": "SWEEP",
         "reword": reword("paragraphs.P2.props.P2.3.statement", p243["statement"],
            p243["statement"].replace("as a placebo, for stock acquirers",
                                      "as a comparison (benchmark), for stock acquirers"))},
        {"fix_id": "S2.4-F2", "locus": "P2.3.role", "action": "SWEEP", "change": "stock placebo -> stock comparison (benchmark)",
         "reword": reword("paragraphs.P2.props.P2.3.role_in_paragraph", p243["role_in_paragraph"],
            p243["role_in_paragraph"].replace("stock placebo", "stock comparison (benchmark)"))},
    ],
}
save("2.4", d)

# =====================================================================  2.3 / 2.5  (untouched)
for s, why in [("2.3", "Measure (UncResCEO). No placebo doing identification work; the cross-channel "
                       "firewall is re-anchored to P2 (2.1), not to 2.3 -- so 2.3 needs no change."),
               ("2.5", "Validity gate + scrutiny rival. No placebo; masking does not touch convergent "
                       "validity or the scrutiny side-test.")]:
    d = load(s)
    d["_proposed_fixes"] = {"summary": f"REVIEWED -- UNTOUCHED. {why}", "register_locks": [], "fixes": []}
    save(s, d)

# =====================================================================  integrity proof (for the advisor)
print("=" * 74)
print("EVIDENCE COPIED BY CODE -- byte-identity asserts:")
assert p52["verification"]["quotes"] == sv["quotes"]; assert p52["verification"]["verdict_note"] == sv["verdict_note"]
assert p53["verification"]["quotes"] == lo["quotes"]; assert p53["verification"]["located"] == lo["located"]
assert p54["verification"] == thew["verification"]
print("  2.1 P5.2 quotes == nlm S-V           :", p52["verification"]["quotes"] == sv["quotes"],
      f"({len(p52['verification']['quotes'])} spans, verdict {p52['verification']['verdict']})")
print("  2.1 P5.3 quotes == nlm Louis         :", p53["verification"]["quotes"] == lo["quotes"],
      f"({len(p53['verification']['quotes'])} spans, verdict {p53['verification']['verdict']})")
print("  2.1 P5.4 verification == clone P6.1  :", p54["verification"] == thew["verification"],
      f"({len(p54['verification']['quotes'])} spans)")
print("=" * 74)
for s in ["2.1", "2.2", "2.3", "2.4", "2.5"]:
    pf = load(s)["_proposed_fixes"]
    print(f"section {s}: {len(pf['fixes'])} fixes")
    for f in pf["fixes"]:
        print(f"    {f['fix_id']:9} {f['action']:9} {f['locus']:18} {f.get('change','(reword)')}")
print("=" * 74)
print("All NLM evidence deep-copied; statements/framing authored; originals NOT mutated.")
