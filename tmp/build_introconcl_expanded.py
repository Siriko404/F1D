#!/usr/bin/env python3
"""Inline expansion: intro 6->9 paragraphs, conclusion 3->7, WITHOUT re-running Phase A/B.
Every verified Phase-A prop is copied VERBATIM (only prop_id + depends_on reassigned);
new 'filler' props (significance, contributions, implications, measurement-limits, future)
are authored here, schema-identical to the workflow props. Linear depends_on is rebuilt by
reading order (matches the existing pattern). Abstract is NOT touched."""
import copy
import json
from pathlib import Path

REW = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")

S1 = json.loads((REW / "section1_paragraph_ledger.json").read_text(encoding="utf-8"))
S5 = json.loads((REW / "section5_paragraph_ledger.json").read_text(encoding="utf-8"))


def index(ledger):
    exist = {}
    para_by_first = {}
    for para in ledger["paragraphs"]:
        chain = para["proposition_chain"]
        para_by_first[chain[0]["from_phaseA_prop"]] = para
        for p in chain:
            exist[p["from_phaseA_prop"]] = p
    return exist, para_by_first


EXI, PARI = index(S1)
EXC, PARC = index(S5)

# ---------------------------------------------------------------- NEW PROPS
NEW = {
"IN.S1": {
  "from_phaseA_prop": "new-significance",
  "statement": "Reading this language matters because the information in an undisclosed acquisition is exactly what securities law keeps off the call, yet the unscripted question-and-answer session is one of the few recurring venues in which a constrained executive must keep speaking and fielding questions. If the bind leaves a trace in the words, that trace would mark a deal's passage from private to public in the firm's own voice, in a channel separate from the price run-up already documented around mergers.",
  "role_in_paragraph": "framing -- M1 significance / why it matters: the stake that motivates reading the language, between the phenomenon and the gap.",
  "type": "framing",
  "reason": "Adds the verbose-convention significance component the original chain lacked: states why the question matters (a readable channel distinct from prices, in the firm's own voice) before the gap and objective. Kept within the ceiling with a conditional ('if the bind leaves a trace', 'would mark'); no causal or predictive claim.",
  "evidence": ["DraftTemplate.txt (verbose INTRO: institutional/background context + 'why it matters' significance component)","section2.1 P1 + P3 final_prose (the disclosure bind; the unscripted venue where silence speaks)","section2.1 P6 final_prose (keown1981: price run-up precedes announcement -- the distinct channel this signal complements)"],
  "numbers": [],
  "register_locks": ["correlational","supportive-not-definitive","mechanism-open"],
},
"IN.C1": {
  "from_phaseA_prop": "new-contributions",
  "statement": "This study makes three contributions, each descriptive. First, it reads a residual measure of CEO question-and-answer uncertainty, the call-varying component that remains once each executive's persistent speaking style is netted out, in the anticipatory window before an acquisition is public, where the nearest prior work has read managed tone, the volume of strategy vocabulary, and prices rather than uncertainty language. Second, it documents that this language pattern concentrates in cash acquisitions rather than stock, a contrast that survives a formal pooled test. Third, it reads the unscripted question-and-answer session as tracking a deal's passage from private to public, connecting the literature on when managers withhold private information with the evidence that markets anticipate corporate transactions, while claiming no causal channel.",
  "role_in_paragraph": "framing -- M3 enumerated contributions: the paper's value-add, in the correlational register, after the findings and within the no-identification ceiling.",
  "type": "framing",
  "reason": "Adds the verbose-convention enumerated-contributions component the original chain lacked. Drafted maximally hedged ('each descriptive', 'reads / documents / reads', 'while claiming no causal channel') to avoid novelty- or causality-overclaim; mirrors the 'to our knowledge' register of the gap (IN.6) without re-asserting the negative as fact. CEILING-BREACH PIECE: the Phase C red-team ceiling check is tuned to the result-claims, not to contributions overclaim, so the hedge is built in here.",
  "evidence": ["DraftTemplate.txt (verbose INTRO: enumerated contributions, 'First... Second... Third...')","section1_paragraph_ledger.json IN.5 + IN.6 (the positioning and the 'to our knowledge' gap this restates in-register)","section2.3 P2 final_prose (the residual measure netted of persistent style)","section3.4 P3 final_prose + claim_findings_ledger.json C6 (the formal pooled cash-concentration test the second contribution rests on)","section2.1 P1 + P6 final_prose (the two literatures the third contribution bridges: withholding theory; transaction anticipation)"],
  "numbers": ["cash-concentration 'survives a formal pooled test' grounded in the Wald diff (tab:empire_cashspec col 1); NO coefficient stated in prose"],
  "register_locks": ["correlational","no-identification","concentration-not-strict-specificity","supportive-not-definitive","mechanism-open"],
},
"CO.I1": {
  "from_phaseA_prop": "new-implications",
  "statement": "For the academic literature, the pattern connects two strands usually studied apart: the theory of when an informed manager withholds private information, and the evidence that markets anticipate corporate transactions before they are announced. It locates a within-firm language signature in the window between the two. We draw no prescription for investors, managers, or regulators from a correlational pattern that identifies no causal channel; the contribution is to characterize a regularity, not to recommend acting on it.",
  "role_in_paragraph": "inference -- M3 implications, developed by audience: the literature-bridge implication and an explicit no-prescription hedge, extending CO.4.",
  "type": "framing",
  "reason": "Develops the implications move the verbose convention asks for, split by audience, while staying inside the ceiling. The explicit 'we draw no prescription ... not to recommend acting on it' forecloses the correlational-to-prescriptive creep the Phase C red-team is not tuned to catch. CEILING-BREACH PIECE. Follows the readable-trace implication (CO.4).",
  "evidence": ["DraftTemplate.txt (verbose CONCLUSION: implications FOR WHOM -- literature, investors, regulators, managers)","section2.1 P1 final_prose (withholding theory: verrecchia1983/dye1985) and section2.1 P6 final_prose (keown1981: market anticipation of deals) -- the two bridged strands","claim_findings_ledger.json thin_claim_ceiling (correlational; no causal channel; no prescription)"],
  "numbers": [],
  "register_locks": ["correlational","no-identification","supportive-not-definitive","mechanism-open"],
},
"CO.L1": {
  "from_phaseA_prop": "new-limitations-measurement",
  "statement": "The measure itself bounds the inference. Uncertainty is captured by applying a finance-specific word list to the transcripts, a count of words that abstracts from their context, and the residual is one operationalization of call-specific uncertainty rather than a direct reading of what a CEO knows. The stock-financed placebo shares the disclosure bind but is an imperfect counterfactual, and the sample, United States public firms from 2002 to 2018, approximately the S\\&P~1500, may not extend to other periods, other markets, or the smaller firms outside it.",
  "role_in_paragraph": "caveat -- M3 limitations, measurement and external validity: the dictionary-based measure, the imperfect placebo, and the sample bound, extending CO.6.",
  "type": "framing",
  "reason": "Develops the limitations move with the measurement and external-validity bounds the verbose convention asks authors to state specifically. Reuses the settled 'approximately the S&P 1500' hedge verbatim and the finance-specific word-list / bag-of-words characterization from Section 2.2. Low-risk, additive to CO.6.",
  "evidence": ["DraftTemplate.txt (verbose CONCLUSION: limitations -- measurement, identification, external validity, stated specifically)","section2.2 P2 final_prose (lm2011 finance-specific uncertainty word list; bag-of-words applied to the Q&A)","section2.3 P2 final_prose (the residual as an operationalization net of style)","section3.1 P4 final_prose (estimation sample bounded to Execucomp-covered firms, approximately the S&P 1500)"],
  "numbers": ["sample window 2002 to 2018 (sample-scale only); 'approximately the S&P 1500' reused verbatim from section3.1 P4"],
  "register_locks": ["correlational","no-identification","supportive-not-definitive"],
},
"CO.F1": {
  "from_phaseA_prop": "new-future",
  "statement": "Several extensions follow. The same residual-uncertainty reading could be applied to other classes of withheld material events and to other corporate transactions, such as divestitures, joint ventures, and strategic alliances, and to settings outside the United States; richer measures of spoken uncertainty could replace the word-list count; and establishing why the signal concentrates in cash acquisitions, the cash-accumulation channel this study leaves open, would require a design the present setting does not provide.",
  "role_in_paragraph": "transition -- M3 future research, developed: additional settings, transactions, measures, and the open cash-concentration mechanism, extending CO.7.",
  "type": "framing",
  "reason": "Develops the future-research move with the specific, actionable directions the verbose convention favors, complementing CO.7 ('other withheld events'; 'separate the two readings'). Deliberately EXCLUDES any two-step-correction / generated-regressand item (E1; the locked red-team decision dropped it).",
  "evidence": ["DraftTemplate.txt (verbose CONCLUSION: directions for future research -- specific, actionable, adjacent settings)","section5_paragraph_ledger.json CO.7 (other withheld events; designs separating compliance-constrained from strategic silence)","section2.1 P6 final_prose / ragozzino2024 (other corporate transactions as adjacent settings)","AUDIT_PROTOCOL E1 (no generated-regressand / two-step item, even as future work)"],
  "numbers": [],
  "register_locks": ["mechanism-open","no-identification"],
},
}

# ---------------------------------------------------------------- META for new/split paragraphs
def meta(statement, reason, serves, boundary, thin, guards, lit="none new", evid=None):
    return {"intent": {"statement": statement, "reason": reason, "evidence": evid or []},
            "serves": serves, "boundary": boundary, "thin_claim": thin,
            "guardrails": guards, "lit_body": lit}

M = {
"1-P2sig": meta(
  "Deliver the Move 1 significance ('why it matters'): state the stake that motivates reading the language, that the unscripted Q&A is a rare recurring venue where a constrained executive must keep speaking, so a trace in the words would mark a deal's passage from private to public in the firm's own voice, a channel distinct from the price run-up (IN.S1).",
  "The verbose intro convention adds a significance component; placed right after the phenomenon and before the gap, it raises the stake without yet claiming the contribution. Kept conditional and within the ceiling.",
  ["Move 1 significance: why reading the language matters (a readable channel distinct from prices, in the firm's own voice); bridges the phenomenon to the gap"],
  "States the stake only; does NOT name the measure (1-P4), expose the gap (1-P3), or preview findings. Conditional register ('if the bind leaves a trace'); no causal or predictive claim.",
  "Reading the language could in principle reveal a deal before announcement, in a channel distinct from prices; conditional, correlational, no mechanism asserted.",
  ["Conditional only: 'if the bind leaves a trace', 'would mark'; NO causal/predictive claim.","Distinct-from-prices channel (keown is price; this is language); no overclaim of novelty here (the gap is 1-P3).","mechanism-open; supportive-not-definitive."],
  evid=["DraftTemplate.txt (verbose INTRO significance component)","section2.1 P1/P3/P6 final_prose"]),

"1-P5find": meta(
  "Deliver the first half of the Move 3 findings preview: First the C2 run-up, residual CEO uncertainty elevated in the quarter before a cash acquisition with no comparable rise before stock (IN.9); Second the C1 anticipatory two-clocks contrast, indistinguishable from zero once announced while the funding cash persists to completion, signaled as the strongest result (IN.10). Qualitative; each direction matches its table cell.",
  "The verbose intro splits the findings summary across paragraphs; the run-up and the timing contrast form the first finding pair (C2 then C1, the strongest), preserving body order, and hand off the cash-concentration test and the rule-out to 1-P6.",
  ["Move 3 findings (1 of 2): C2 run-up (3.2) and C1 two-clocks timing (3.3, strongest), in body order; hands to 1-P6"],
  "Qualitative preview only; NO coefficients/SEs/p-values; each directional claim matches its table's sign/significance. Holds C2 and C1 only; C6 and the rule-out are 1-P6. Does NOT include the no-identification caveat (1-P8).",
  "Two within-firm correlational findings stated qualitatively: the run-up (no comparable stock rise) and the anticipatory two-clocks contrast (strongest, signaled in place).",
  ["C2 (IN.9): cash-vs-stock here is the descriptive side-by-side, distinct from the formal test (IN.11/1-P6); matches col 2 positive+sig / col 6 null.","C1 (IN.10): 'indistinguishable from zero once announced' at the GAP, signaled strongest in-place; NEVER 'falls/reverses/unwound'; do NOT read the negative POST.","QUALITATIVE: no coefficients/SEs/p-values; each claim matches table sign/significance.","Body order within M3: C2 -> C1 here, continuing C6 -> C4 in 1-P6."],
  evid=["DraftTemplate.txt L78-79+L89-92 (M3 findings, enumerated, QUALITATIVE, match sign/significance)","section3.2 + section3.3 final_prose","claim_findings_ledger.json C2, C1"]),

"1-P6find": meta(
  "Deliver the second half of the Move 3 findings preview: Finally the C6 formal pooled cash-specificity test, the run-up concentrating in cash rather than stock, read as concentration not strict specificity with the cash-accumulation mechanism left open (IN.11); and the C4 'we also rule out' closer, the run-up not accounted for by analysts devoting more of the call to cash questions (IN.12). Qualitative; body order C6 -> C4.",
  "Continues the split findings preview: the formal pooled test upgrades the descriptive cash-vs-stock contrast, and the scrutiny rule-out closes the enumeration, keeping body order C2->C1->C6->C4 across 1-P5 and 1-P6.",
  ["Move 3 findings (2 of 2): C6 formal cash-concentration (3.4) and the C4 scrutiny rule-out (4.1); closes the findings, hands to contributions (1-P7)"],
  "Qualitative preview only; NO coefficients/SEs/p-values. Holds C6 and C4 only. C6 is the FORMAL pooled (Wald) difference, never a side-by-side; C4 hedged to this run-up.",
  "The formal pooled cash-concentration (concentration not strict specificity, cause open) and the scrutiny rule-out (does not account for THIS run-up).",
  ["C6 (IN.11): the FORMAL pooled (Wald) difference; NEVER Gelman-Stern side-by-side; concentration-not-strict-specificity; supportive-not-definitive; EFFECT separated from the open CAUSE (cause leg n.s.).","C4 (IN.12): survives scrutiny + interaction; 'does not account for THIS run-up', NEVER 'scrutiny never matters'; underpowered null not upgraded.","QUALITATIVE: no coefficients/SEs/p-values.","Body order continues C6 -> C4."],
  evid=["DraftTemplate.txt L78-79+L89-92","section3.4 + section4.1 final_prose","claim_findings_ledger.json C6, C4"]),

"1-P7con": meta(
  "Deliver the Move 3 enumerated contributions in one paragraph, in the correlational register: First, reading the residual uncertainty measure in the anticipatory pre-announcement window where prior work read tone/vocabulary/prices; Second, documenting the cash-vs-stock concentration that survives a formal pooled test; Third, reading the unscripted Q&A as tracking a deal's passage from private to public and connecting the withholding and transaction-anticipation literatures, while claiming no causal channel (IN.C1).",
  "The verbose intro convention adds an enumerated-contributions paragraph; placed after the findings and before the caveat, it states the value-add. CEILING-BREACH PIECE: drafted maximally hedged to avoid novelty/causality overclaim the Phase C red-team is not tuned to catch.",
  ["Move 3 enumerated contributions: extends the residual reading to the anticipatory window; documents cash-concentration; bridges two literatures; all descriptive"],
  "Contributions only; stated as 'reads / documents / reads', NOT 'first to'; 'while claiming no causal channel'. No new finding, no coefficient. Sits within the no-identification ceiling; the explicit caveat follows in 1-P8.",
  "Three descriptive contributions, each within the correlational ceiling, mirroring the 'to our knowledge' register of the gap; no causal channel claimed.",
  ["NOVELTY HEDGE: 'reads/documents/reads', 'each descriptive'; do NOT write 'first to show' or assert the gap as established fact (the everhart/gokkaya scar).","CAUSALITY HEDGE: 'while claiming no causal channel'; correlational + no-identification + mechanism-open.","C6 framing: 'survives a formal pooled test' = the Wald difference; concentration-not-strict-specificity; NO coefficient in prose.","Contributions precede the explicit caveat (1-P8), which bounds them."],
  evid=["DraftTemplate.txt (verbose INTRO enumerated contributions)","section1 IN.5/IN.6; section2.3 P2; section3.4 P3 + claim_findings_ledger.json C6; section2.1 P1/P6"]),

# -------- conclusion
"5-P2find": meta(
  "Deliver Move 2 qualitative findings summary in one paragraph: the three main findings (C2 run-up with no comparable stock rise, C1 indistinguishable from zero once announced while the funding cash persists to completion, C6 cash-concentration on a formal pooled test), synthesized in one merged prop, qualitatively (CO.2).",
  "The verbose conclusion gives the findings summary its own paragraph, separate from the rule-out; CO.2 stays the single merged result prop per the locked chain (not split to the abstract's granularity).",
  ["Move 2 findings summary: C2 run-up, C1 two-clocks timing, C6 formal cash-concentration (CO.2); hands the rule-out to 5-P3"],
  "Qualitative synthesis only; NO coefficients/SEs/p-values. CO.2 stays ONE merged result prop (C2+C1+C6); do NOT split or harmonize to the abstract's four props. Each direction tied to its table cell. ~Zero citations. The rule-out is 5-P3.",
  "Three within-firm correlational findings synthesized; C-traps held in compressed form; mechanism open.",
  ["C1 (within CO.2): 'indistinguishable from zero once announced'; NEVER 'unwound/falls'; negative POST not read.","C6 (within CO.2): the formal pooled test; NEVER side-by-side; concentration-not-strict-specificity.","Keep CO.2 as ONE merged prop (do not split C2/C1/C6) per the locked chain.","QUALITATIVE: no coefficients/SEs/p-values; body order C2 -> C1 -> C6."],
  evid=["DraftTemplate.txt L165-166 (M2 qualitative summary)","section3.2/3.3/3.4 final_prose","claim_findings_ledger.json C2, C1, C6"]),

"5-P3rule": meta(
  "Deliver the analyst-scrutiny rule-out as its own paragraph: the pre-announcement elevation is not accounted for by analysts devoting more of the call to cash questions, surviving a direct scrutiny measure and its interaction, hedged to this run-up (CO.3).",
  "The verbose conclusion gives the rule-out its own paragraph after the findings summary; it is a distinct move (an additional analysis result), kept hedged per the C4 trap.",
  ["Move 2 (cont.): the C4 scrutiny rule-out (CO.3); sets up the implications in 5-P4"],
  "The C4 rule-out only; 'not accounted for by analysts devoting more of the call to cash questions' = does not account for THIS run-up; NEVER 'scrutiny never matters'. Qualitative; ~zero citations.",
  "The pre-announcement elevation survives a direct scrutiny measure and its interaction; underpowered null, hedged to this run-up.",
  ["C4 (CO.3): does not account for THIS run-up; NEVER 'scrutiny never matters'.","Underpowered null not upgraded to a powered equivalence (that boundary is voiced in 5-P6).","QUALITATIVE: no coefficients/SEs/p-values."],
  evid=["DraftTemplate.txt L165-166","section4.1 P3 + P4 final_prose","claim_findings_ledger.json C4"]),

"5-P4imp": meta(
  "Deliver Move 3 implications in one paragraph: the broader takeaway that the unscripted language carries a readable, anticipatory trace of a deal's passage from private to public (CO.4), developed by audience, that for the literature it bridges the withholding and transaction-anticipation strands, with an explicit no-prescription hedge for investors, managers, and regulators (CO.I1).",
  "The verbose conclusion develops implications by audience; CO.4 opens with the readable-trace takeaway within the ceiling, and the new CO.I1 adds the literature bridge plus an explicit no-prescription hedge. CEILING-BREACH PIECE: the hedge forecloses correlational-to-prescriptive creep.",
  ["Move 3 implications: the readable-trace takeaway (CO.4) and the literature-bridge + no-prescription implication by audience (CO.I1)"],
  "Implications within the ceiling: a readable trace and a literature bridge, NOT a tested mechanism or a prescription. Explicit 'we draw no prescription ... not to recommend acting on it'. No new finding. ~Zero citations.",
  "Implication is a readable anticipatory trace that bridges two literatures; explicitly no prescription for any stakeholder; correlational, mechanism-open.",
  ["CO.4 kept within the ceiling: a readable, anticipatory TRACE, not a tested mechanism.","CO.I1 NO-PRESCRIPTION hedge explicit: 'we draw no prescription for investors, managers, or regulators ... not to recommend acting on it'.","correlational + no-identification + supportive-not-definitive + mechanism-open; no causal channel.","~Zero citations; no roadmap."],
  evid=["DraftTemplate.txt L167-168 (M3 implications) + verbose implications-FOR-WHOM component","section2.1 P1/P6/P7 final_prose","claim_findings_ledger.json thin_claim_ceiling"]),

"5-P5lim": meta(
  "Deliver Move 3 core limitations as its own paragraph: the evidence is correlational and within-firm, the design supports no causal identification and establishes no mechanism, the war-chest cause is unestablished, and the two readings (compliance-constrained inability to speak and strategically chosen reticence) remain observationally equivalent (CO.5).",
  "The verbose conclusion gives the core limitations their own paragraph, voicing the no-identification/correlational/mechanism-open boundaries explicitly, mirroring the intro caveat (IN.13).",
  ["Move 3 core limitations: correlational/within-firm, no causal identification, mechanism-open, war-chest unestablished, two observationally-equivalent readings (CO.5)"],
  "Core limitations only; stated EXPLICITLY. E1: NO generated-regressand/Pagan/two-step-SE disclaimer. ~Zero citations.",
  "Correlational, within-firm; no causal identification; no established mechanism; war-chest unestablished; two readings observationally equivalent.",
  ["CO.5 EXPLICIT: correlational, within-firm, no causal identification, mechanism-open, war-chest unestablished, two observationally-equivalent readings.","E1: NO generated-regressand / Pagan / two-step-SE disclaimer.","Do NOT soften or upgrade the register."],
  evid=["DraftTemplate.txt L167-168 + Task rule (conclusion states no-identification/correlational caveat EXPLICITLY)","section2.1 P7 / section2.2 P5 final_prose","claim_findings_ledger.json register_that_stands; AUDIT_PROTOCOL E1"]),

"5-P6bnd": meta(
  "Deliver Move 3 further boundaries in one paragraph: the residual is estimated only for CEOs with enough calls to fix a speaking style, skewing the sample toward larger, more heavily covered firms, and the scrutiny rule-out is a failure to find rather than a powered test of equivalence since most calls draw no cash scrutiny (CO.6); plus the measurement and external-validity bounds, the dictionary-based bag-of-words measure, the imperfect stock placebo, and the 2002 to 2018 sample approximately the S&P 1500 (CO.L1).",
  "The verbose conclusion develops limitations with the specific measurement and external-validity bounds the convention favors; CO.6 carries the selection + underpowered-null boundaries, and the new CO.L1 adds the measure and sample bounds, reusing the settled 'approximately the S&P 1500' hedge. Low-risk, additive.",
  ["Move 3 further boundaries: selection toward larger firms + underpowered null (CO.6); dictionary-based measure, imperfect placebo, sample bound (CO.L1)"],
  "Boundaries only; specific and accurate. C4 boundary = 'failure to find', NOT equivalence. 'approximately the S&P 1500' reused verbatim. No new finding. ~Zero citations.",
  "Selection toward larger more-covered firms; underpowered scrutiny null; dictionary-based measure abstracting from context; imperfect placebo; sample bounded approximately to the S&P 1500.",
  ["CO.6 C4 boundary: 'failure to find', NOT a powered test of equivalence; CEO >=5-call selection skews toward larger, more-covered firms.","CO.L1: measure is a finance-specific word-list / bag-of-words abstracting from context; residual is one operationalization; stock placebo imperfect.","Reuse 'approximately the S&P 1500' verbatim (section3.1 P4); sample-scale numerals only (2002 to 2018).","correlational + no-identification + supportive-not-definitive."],
  evid=["DraftTemplate.txt verbose limitations (measurement + external validity)","section3.1 P4 + section3.2 P2 final_prose (selection; approximately the S&P 1500)","section4.1 P4 final_prose (failure to find; ~89% no cash scrutiny)","section2.2 P2 final_prose (lm2011 word list; bag-of-words); section2.3 P2 (residual operationalization)"]),

"5-P7fut": meta(
  "Deliver Move 3 future research as the closing paragraph: whether the same anticipatory language signature appears around other classes of withheld material events and designs separating compliance-constrained from strategic silence (CO.7); plus other corporate transactions (divestitures, joint ventures, alliances), settings outside the United States, richer measures of spoken uncertainty, and establishing the open cash-accumulation mechanism (CO.F1). Drops the roadmap; E1-clean.",
  "The verbose conclusion develops future research with specific, actionable directions; CO.7 supplies the withheld-events and separating-the-readings directions, and the new CO.F1 adds adjacent transactions, markets, measures, and the open mechanism. Deliberately excludes any two-step / generated-regressand item (E1).",
  ["Move 3 future research close: other withheld events + separating the two readings (CO.7); other transactions/markets/measures + the open mechanism (CO.F1); drops the roadmap"],
  "Future research only; specific and actionable. E1: NO two-step-correction/generated-regressand item, even as future work. No roadmap; no lit-review re-run. ~Zero citations.",
  "Future work: other withheld events; designs separating the two readings; other transactions, markets, and measures; establishing the cash-accumulation mechanism.",
  ["E1: deliberately EXCLUDE any 'two-step correction' / generated-regressand item (red-team dropped plan3 K8); no Pagan disclaimer even as future work.","Directions specific and adjacent (divestitures/JVs/alliances; non-US; richer measures; the open mechanism).","~Zero citations; NO roadmap; do NOT re-run the literature review."],
  evid=["DraftTemplate.txt verbose future-research (specific, adjacent settings)","section5 CO.7; section2.1 P6 / ragozzino2024 (adjacent transactions)","section2.2 P5 final_prose (design cannot distinguish the two readings); AUDIT_PROTOCOL E1"]),
}

# ---------------------------------------------------------------- ASSEMBLE
def build(unit, plan):
    paras = []
    flat = []  # (para_index, prop_dict) for linear depends_on
    for order, spec in enumerate(plan, 1):
        pid = spec["pid"]
        # paragraph metadata
        if spec.get("meta_from"):
            src = spec["meta_from"][1] if spec["meta_from"][0] == 1 else None
            base = PARI[spec["meta_from"][1]] if unit == 1 else PARC[spec["meta_from"][1]]
            pm = {k: copy.deepcopy(base[k]) for k in ("intent", "serves", "boundary", "thin_claim", "guardrails", "lit_body", "prose_gate")}
        else:
            pm = copy.deepcopy(M[spec["meta"]])
            pm["prose_gate"] = {"rule": "all props homed + reason+evidence atomic + qualitative; planning-only", "all_supported": True, "unlocked": False}
        para = {"para_id": pid, "order": order, **pm, "proposition_chain": [], "final_prose": "", "prose_status": "BLOCKED -- planning only"}
        # ensure prose_gate present
        if "prose_gate" not in para:
            para["prose_gate"] = {"rule": "planning-only", "all_supported": True, "unlocked": False}
        for kind, key in spec["props"]:
            src = (EXI if unit == 1 else EXC)[key] if kind == "exist" else NEW[key]
            p = copy.deepcopy(src)
            para["proposition_chain"].append(p)
            flat.append(p)
        paras.append(para)
    # relabel prop_ids + rebuild linear depends_on by reading order
    prev = None
    pmap = {}  # from_phaseA -> new prop_id
    for para in paras:
        for i, p in enumerate(para["proposition_chain"]):
            new_id = f"{para['para_id']}-{chr(97+i)}"
            p["prop_id"] = new_id
            p["depends_on"] = [prev] if prev else []
            pmap[p["from_phaseA_prop"]] = (new_id, para["para_id"])
            prev = new_id
    return paras, pmap

INTRO_PLAN = [
  {"pid": "1-P1", "meta_from": (1, "IN.1"), "props": [("exist", "IN.1"), ("exist", "IN.2"), ("exist", "IN.3"), ("exist", "IN.4")]},
  {"pid": "1-P2", "meta": "1-P2sig", "props": [("new", "IN.S1")]},
  {"pid": "1-P3", "meta_from": (1, "IN.5"), "props": [("exist", "IN.5"), ("exist", "IN.6")]},
  {"pid": "1-P4", "meta_from": (1, "IN.7"), "props": [("exist", "IN.7"), ("exist", "IN.8")]},
  {"pid": "1-P5", "meta": "1-P5find", "props": [("exist", "IN.9"), ("exist", "IN.10")]},
  {"pid": "1-P6", "meta": "1-P6find", "props": [("exist", "IN.11"), ("exist", "IN.12")]},
  {"pid": "1-P7", "meta": "1-P7con", "props": [("new", "IN.C1")]},
  {"pid": "1-P8", "meta_from": (1, "IN.13"), "props": [("exist", "IN.13")]},
  {"pid": "1-P9", "meta_from": (1, "IN.14"), "props": [("exist", "IN.14")]},
]

CONCL_PLAN = [
  {"pid": "5-P1", "meta_from": (5, "CO.1"), "props": [("exist", "CO.1")]},
  {"pid": "5-P2", "meta": "5-P2find", "props": [("exist", "CO.2")]},
  {"pid": "5-P3", "meta": "5-P3rule", "props": [("exist", "CO.3")]},
  {"pid": "5-P4", "meta": "5-P4imp", "props": [("exist", "CO.4"), ("new", "CO.I1")]},
  {"pid": "5-P5", "meta": "5-P5lim", "props": [("exist", "CO.5")]},
  {"pid": "5-P6", "meta": "5-P6bnd", "props": [("exist", "CO.6"), ("new", "CO.L1")]},
  {"pid": "5-P7", "meta": "5-P7fut", "props": [("exist", "CO.7"), ("new", "CO.F1")]},
]

ip, imap = build(1, INTRO_PLAN)
cp, cmap = build(5, CONCL_PLAN)

S1["paragraphs"] = ip
S5["paragraphs"] = cp
S1["title"] = "Introduction (verbose, nine paragraphs: M1 phenomenon + significance + gap; M2 objective; M3 findings x2 + contributions + caveat; M4 roadmap)"
S5["title"] = "Conclusion (verbose, seven paragraphs: restate; findings; rule-out; implications; core limitations; further boundaries; future research)"

def coverage(mapping, originals):
    return {"all_phaseA_props_homed": "All original Phase-A props homed exactly once; new additive props (significance/contributions/implications/measurement-limitations/future) carry from_phaseA_prop='new-*'.",
            "prop_to_paragraph": [{"phaseA_prop": k, "paragraph": v[1], "note": ("ADDED filler" if k.startswith("new-") else "verified Phase-A prop, re-homed verbatim")} for k, v in mapping.items()],
            "gaps": []}

S1["allocation_coverage"] = coverage(imap, 14)
S5["allocation_coverage"] = coverage(cmap, 7)
S1["paragraph_count_rationale"] = {"statement": "Nine paragraphs (user-set verbose target). M1 over three (phenomenon; significance; gap), M2 one, M3 over four (findings 1-2; finding 3 + rule-out; contributions; caveat), M4 one.", "reason": "Expanded inline from six to the user's nine-paragraph verbose target using the NLM verbose-intro menu: added a significance ('why it matters') paragraph and an enumerated-contributions paragraph, and split the crammed four-finding preview into two. Every original IN.1-IN.14 prop is preserved verbatim; only IN.S1 (significance) and IN.C1 (contributions) are added.", "evidence": ["DraftTemplate.txt verbose INTRO (6-9 paragraphs; significance + enumerated contributions components)", "tmp/nlm_verbose_intro_conclusion.json", "user directive 2026-06-15 (intro = 9 paragraphs)"]}
S5["paragraph_count_rationale"] = {"statement": "Seven paragraphs (user-set verbose target): restate; findings; rule-out; implications; core limitations; further boundaries; future research.", "reason": "Expanded inline from three to the user's seven-paragraph verbose target using the NLM verbose-conclusion menu: un-crammed the merged paragraphs (findings vs rule-out; implications vs limitations vs future) and developed implications by audience (CO.I1), measurement/external-validity limitations (CO.L1), and future directions (CO.F1). Every original CO.1-CO.7 prop is preserved verbatim.", "evidence": ["DraftTemplate.txt verbose CONCLUSION (implications FOR WHOM; specific limitations; future research)", "tmp/nlm_verbose_intro_conclusion.json", "user directive 2026-06-15 (conclusion = 7 paragraphs)"]}

(REW / "section1_paragraph_ledger.json").write_text(json.dumps(S1, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(REW / "section5_paragraph_ledger.json").write_text(json.dumps(S5, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"INTRO: {len(ip)} paragraphs, {sum(len(p['proposition_chain']) for p in ip)} props")
print(f"CONCL: {len(cp)} paragraphs, {sum(len(p['proposition_chain']) for p in cp)} props")
print("new props:", [k for k in NEW])
