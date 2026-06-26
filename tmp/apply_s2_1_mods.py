"""Apply the masking re-derivation to the CLONE of section 2.1 (P5 full + P4 light).
Edits ONLY _phase4_s2_clone/section2.1_paragraph_ledger.json. Originals untouched.
Advisor-blessed: attenuation-not-suppression, cross-channel bridge, placebo->comparison.
"""
import json
from pathlib import Path

CLONE = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_phase4_s2_clone\section2.1_paragraph_ledger.json")
d = json.loads(CLONE.read_text(encoding="utf-8"))
P5 = d["paragraphs"]["P5"]

# ---- preserve old prose, block until rewrite ----
P5["final_prose_superseded"] = P5.get("final_prose", "")
P5["final_prose"] = ""
P5["prose_status"] = "BLOCKED (chain redesigned 2026-06-26 masking; rewrite pending)"

# ---- plan fields ----
P5["intent"] = ("Cash and stock acquisitions share the identical disclosure bind but differ in the medium of "
    "payment: stock pays with the acquirer's own equity (a currency whose value it is motivated to protect), "
    "cash pays with cash. Stock acquirers therefore have an incentive -- grounded in valuation theory "
    "(Shleifer-Vishny 2003) and documented pre-deal earnings management (Louis 2004) -- to manage perceptions "
    "upward; cash acquirers do not. Cash is thus the relatively UNMANAGED window in which the disclosure-strain "
    "surfaces as unscripted uncertainty language -- the ex-ante reason the run-up should CONCENTRATE in cash. "
    "This MOTIVATES the cash focus; it is not a tested mechanism.")
P5["serves"] = ("Derives the CASH-CONCENTRATED dimension (-> H1a) via the masking asymmetry; recasts the stock "
    "deal as a managed COMPARISON (-> MA3 Wald, -> MA2 comparison arm); frames the differential as "
    "attenuation-not-suppression; keeps the two-clocks cash-persistence (-> H1b).")
P5["thin_claim"] = ("A where-it-concentrates MOTIVATION; the why is ex-ante reasoning, not identification; the "
    "differential is ATTENUATION (stock smaller/noisier), NEVER stock-suppression; cite the published S-V/Louis "
    "as valuation/earnings, not tone.")
P5["guardrails"] = [
    ("ATTENUATION-not-SUPPRESSION (advisor 2026-06-26, the load-bearing joint): masking motivates "
     "theta_cash > theta_stock as cash being the clean window AND stock attenuated/noisy -- NEVER as stock "
     "pushed below baseline. Data: cash +0.0461***, stock -0.0429 n.s. (a noisy flat null). We interpret; we "
     "do not detect stock suppression."),
    ("CROSS-CHANNEL BRIDGE (advisor 2026-06-26): the cites document management in SCRIPTED channels (earnings, "
     "press-release tone); our DV is the unscripted Q&A residual, NET OF the scripted presentation (2.3 P2.5). "
     "State this as a STRENGTH (we read the hardest-to-manage channel), not a gap -- it closes the genre-jump."),
    ("MOTIVATION-not-MECHANISM: masking is the ex-ante reason to focus on cash; register stays correlational / "
     "no-identification / concentration-not-strict-specificity / mechanism-open."),
    ("CITE DISCIPLINE: S-V 2003 = currency/valuation MOTIVE; Louis 2004 = pre-deal EARNINGS behavior; thewissen "
     "2024 = tone (preprint, supplementary one-clause pointer only). NEVER cite S-V/Louis as 'tone'. New "
     "\\bibitem required for shleifer_vishny2003 + louis2004 (compile)."),
    ("HARFORD demoted + RELOCATED: the accumulated cash position grounds the two-clocks cash-persistence, NOT "
     "the why-cash concentration (which is now the masking asymmetry)."),
]

# ---- propositions: keep P5.1 (demoted+relocated, Harford verification intact) + add P5.2-P5.5 ----
p51 = P5["propositions"][0]   # existing Harford prop (verdict SUPPORTED) -- keep its verification
assert p51["prop_id"] == "P5.1", p51["prop_id"]
p51["statement"] = ("A cash purchase draws on an accumulated cash position (Harford 1999), whereas a stock "
    "exchange is paid in the acquirer's own equity. That accumulated cash position grounds the two-clocks "
    "cash-persistence (it serves the purchase and is paid at completion), NOT the why-cash concentration.")
p51["role_in_paragraph"] = ("DEMOTED + RELOCATED: background payment-method premise (cash side) + two-clocks "
    "cash-persistence; no longer the why-cash rationale.")

VPTR = "tmp/nlm_masking_cites.json"
p52 = {
    "prop_id": "P5.2", "type": "external-NLM",
    "statement": ("A stock acquirer pays with its own equity, whose market value is the deal currency; acquirers "
        "therefore have an incentive to keep that valuation high -- overvalued equity is used as acquisition "
        "currency, and the relative valuations of bidder and target drive the choice between stock and cash "
        "payment."),
    "role_in_paragraph": "The MOTIVE: why stock-payers protect their pre-deal valuation. Cite as valuation/currency, NOT tone.",
    "source": {"key": "shleifer_vishny2003", "ref": "Shleifer & Vishny (2003), JFE 70:295-311"},
    "verification": {"method": "NLM", "evidence_file": VPTR, "verdict": "SUPPORTED",
        "verdict_note": ("Verbatim cited_text: 'a powerful incentive for firms to get their equity overvalued, so "
            "that they can make acquisitions with stock' (p.308 sec.6); 'Using overvalued shares as a means of "
            "payment ... cushions the collapse of the shares in the long run' (p.300 sec.3). NLM-verified, "
            "identity-confirmed. DRAFTING: cite the currency/valuation MOTIVE only; the 'earnings manipulation' "
            "tail is S-V's aside -> motive-color, not behavioral proof.")},
}
p53 = {
    "prop_id": "P5.3", "type": "external-NLM",
    "statement": ("Consistent with that incentive, stock acquirers manage perceptions upward ahead of the deal: "
        "they overstate reported earnings in the quarter preceding a stock-swap announcement (Louis 2004). The "
        "disclosure channel closest to ours -- narrative tone -- shows the same management (thewissen 2024, "
        "preprint)."),
    "role_in_paragraph": ("Published pre-deal BEHAVIOR (earnings), with a one-clause thewissen TONE pointer "
        "(language bridge, supplementary)."),
    "source": {"key": "louis2004", "ref": "Louis (2004), JFE 74:121-148"},
    "verification": {"method": "NLM", "evidence_file": VPTR, "verdict": "SUPPORTED",
        "verdict_note": ("Verbatim cited_text: 'acquiring firms overstate their earnings reports in the quarter "
            "preceding a stock swap announcement' (p.121-122 sec.1); 'For the stock-for-stock acquirers, there is "
            "a jump in the abnormal accrual in the quarter immediately prior to the merger announcement' (p.134 "
            "sec.4.3). NLM-verified, identity-confirmed. CITE AS EARNINGS, not tone. thewissen tone = "
            "supplementary preprint pointer.")},
}
p54 = {
    "prop_id": "P5.4", "type": "framing-nonverifiable",
    "statement": ("A cash acquirer pays in cash, not equity, so it lacks both the currency to protect and the "
        "disposition to manage pre-deal perceptions upward. The cited management operates in scripted, numbers "
        "channels (earnings, press-release tone) that our dependent variable already strips out -- the residual is "
        "net of the scripted presentation (2.3 P2.5) -- so we read the channel hardest to manage, the unscripted "
        "Q&A, where only a genuine perception-management disposition, not a one-off scripted edit, would surface. "
        "The cross-channel inference is offered as MOTIVATION: a stock acquirer's optimism disposition partly "
        "OFFSETS the disclosure-strain in its unscripted answers, so its run-up is expected smaller and noisier "
        "(ATTENUATED), while a cash acquirer carries only the strain, so its run-up is the clean, larger one. This "
        "is attenuation, NOT suppression -- we predict no push of stock's uncertainty below baseline, and the "
        "cash-vs-stock gap is realized as the cash run-up. Not a tested mechanism."),
    "role_in_paragraph": ("THE load-bearing joint (advisor): the masking inference for the cash-vs-stock "
        "DIFFERENTIAL + the cross-channel/genre-jump bridge + the attenuation-not-suppression honesty boundary."),
    "depends_on": ["P5.2", "P5.3", "2.3 P2.5"],
}
p55 = {
    "prop_id": "P5.5", "type": "framing-nonverifiable",
    "statement": ("The stock deal is therefore a managed COMPARISON, not a placebo: the same disclosure bind, but "
        "carrying a currency-management incentive that cash lacks. The contrast remains one of CONCENTRATION, not "
        "strict specificity; the asymmetry motivates the cash focus and is not an identification claim."),
    "role_in_paragraph": "placebo -> managed COMPARISON + register (concentration-not-specificity; motivation-not-identification; mechanism-open preserved).",
}
P5["propositions"] = [p51, p52, p53, p54, p55]

# ---- P4 light: 'placebo isolates' -> 'comparison motivates concentration' (the identification-work fix) ----
lc = d["_plan"]["logic_chain_validated"]
before = lc.get("P4_necessity", "")
lc["P4_necessity"] = before.replace("the P5 placebo + timing design do",
                                    "the P5 comparison + timing design motivate the concentration")
assert lc["P4_necessity"] != before, "P4_necessity substring not found"
P4 = d["paragraphs"]["P4"]
g0 = P4["guardrails"][0]
P4["guardrails"][0] = g0.replace("the P5 placebo + timing design isolate it",
                                 "the P5 comparison + timing design motivate the concentration (not identify it)")
assert P4["guardrails"][0] != g0, "P4 guardrail substring not found"

# ---- stamp ----
d["_phase4_masking"] = ("§2.1 chain redesigned 2026-06-26: P5 re-derived via masking asymmetry (S-V motive + "
    "Louis behavior + thewissen tone pointer; attenuation-not-suppression; cross-channel bridge; placebo->managed "
    "comparison). P4 'isolates'->'motivates' to match. Evidence: tmp/nlm_masking_cites.json. Spec: "
    "_PHASE4_S2_MODSPEC.md. final_prose BLOCKED -> rewrite pending.")

CLONE.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
print(f"OK. P5 now has {len(P5['propositions'])} props: {[p['prop_id'] for p in P5['propositions']]}")
print("P4_necessity + P4 guardrail[0]: placebo->comparison applied.")
print("final_prose BLOCKED (superseded prose preserved).")
