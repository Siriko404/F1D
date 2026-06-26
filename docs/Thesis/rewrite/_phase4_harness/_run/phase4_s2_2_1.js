export const meta = {
  name: 'phase4-props-redesign',
  description: 'Phase-4: redesign a thesis SECTION proposition chain so it carries the locked Phase-3 why-cash motivation (the masking asymmetry) in place of the older cash-focus motivation. OUTPUT IS LEDGER-SHAPED + ORDERED: per touched paragraph, an agent emits the COMPLETE ordered proposition chain (every original prop accounted for as retain/reword/re-derive/demote/relocate/delete, plus any added props), each changed/new prop a crisp single-claim ledger object (prop_id, statement, role, type, source_key, ev_ids). SECTION-AGNOSTIC: same prompts for any section; a build step embeds that section chain skeleton + the fixed evidence map. PANEL-1 = 3 neurodiverse agents (identical task, heavily paraphrased, NO examples) decide which paragraphs carry the why-cash motivation and rebuild only those chains. PANEL-2 = 3 agents damage-red-team all 3 Panel-1 sets (no prop outside the why-cash motivation altered; honesty floor; cite-axis; coherence) and author one hardened set each. RED-TEAM = 1 agent picks the single best ordered chain per paragraph BY REFERENCE. finalize writes the kept ordered chains to a SEPARATE field phase4_proposed_propositions; original propositions[] stays byte-identical; final_prose stays BLOCKED.',
  phases: [
    { title: 'Panel-1', detail: '3 paraphrased agents -> 3 ordered ledger-shaped redesigns of the why-cash paragraphs' },
    { title: 'Panel-2', detail: '3 paraphrased agents -> damage-red-team all 3 + author 3 hardened ordered redesigns' },
    { title: 'Red-team', detail: 'pick the single best ordered chain per paragraph BY REFERENCE -> 1 final set' },
  ],
}

// SECTION = { section, subsections:[ { subsection, title, section_job, spine, logic_chain_validated:{}, paragraphs:[ {pid, intent, thin_claim, guardrails:[], props:[ {prop_id, type, verdict, source:{key,ref}, statement, role} ] } ] } ] }
// EVIDENCE = { ev_id: { cite, text, page, section } }   (fixed NLM-verified pool; agents cite by ev_id and NEVER retype a quote)
// Both embedded by an EXTERNAL build step (_phase4_harness/build_phase4.py). The harness never reads files at runtime.
const SECTION = {"section": "2", "subsections": [{"subsection": "2.1", "title": "Conceptual Framework + Main Literature Review (fused)", "section_job": "2.1 = the main, COMPLETE literature review AND the conceptual framework, fused. Situates the paper in every body of work it draws on AND derives the two dimensions. 2.2-2.5 carry only their own instrumental cites.", "spine": "P1 bind + P2 readable -> P3 anticipatory uncertainty trace -> P4 located in the call-varying residual; P5 cash design-contrast -> concentration + two clocks. P6 novelty, P7 scope frame it. Conclusion: an anticipatory x cash-concentrated component of CEO Q&A uncertainty, in the call-varying residual, tracking the deal's disclosure state -- a PATTERN, not a mechanism. Yields H1/H1a/H1b.", "logic_chain_validated": {"advisor_verdict_2026_06_12": "VALID and INTACT -- proceed. Guardrails folded into P1/P3/P4/P5/P6.", "A1_sign": "P3: the bind must RAISE uncertainty words, not lower them. A more guarded/scripted CEO would push the measure DOWN. Earn UP affirmatively: live Q&A, analyst follow-ups, sustained clean deflection is hard -> hedging leaks. H1 one-tailed -> sign cannot be assumed.", "A2_contrast": "P5: do NOT assert a cash-sharpens-the-bind mechanism (= the ruled-out scrutiny channel). Cash is a DESIGN CONTRAST (stock = same gag minus visible cash); concentration informative on its own; WHY open (P7).", "trap": "P5 must never read as 'visible cash -> analysts ask more -> CEO hedges' (contradicts 4.1).", "mechanical_leg": "H1b cash-persists-to-completion is MECHANICAL (cash leaves when paid); H1b CONTENT is the CONTRAST (uncertainty resolves, cash does not).", "novelty_caveat": "P6 gap claim NOT NLM-verifiable (cannot prove a negative) -> 'to our knowledge'. Most likely to need walking back (everhart/gokkaya scar).", "P4_necessity": "P4 is NECESSARY (signal must be in the residual), NOT sufficiency (residual does not ISOLATE the signal -- the P5 placebo + timing design do).", "P1_legal_accuracy_2026_06_12": "Reg FD REJECTED as the disclosure-constraint cite (it governs SELECTIVE disclosure; a public-call disclosure SATISFIES it -> not a gag). Correct framing: deal is MATERIAL (Basic) + nonpublic; firm may stay silent but may not MISLEAD once it speaks (Basic facts = false denials -> liability; Rule 10b-5 half-truth). This bridges to P3 deflection AND keeps can't-speak/won't-speak OPEN for P7. Scope materiality to the ACQUIRER."}, "paragraphs": [{"pid": "P1", "intent": "A firm privately committed to an acquisition but not yet announcing sits in a distinct DISCLOSURE STATE, not a balance-sheet state: the pending deal is material nonpublic information, yet the quarterly call -- especially unscripted Q&A -- is a standing obligation. The firm may stay silent but, once it speaks, may not mislead; so the CEO must host the call while unable to address the one material thing and unable to deny it. Disclosure theory frames a withholding state as informative; that bind is the paper's organizing primitive.", "thin_claim": "State the descriptive/correlational posture near the open. Materiality scoped to the acquirer (Basic = 'can be material', NOT 'every deal is MNPI').", "guardrails": ["Do NOT assert a legal GAG. Frame: material (Basic) + nonpublic + may-stay-silent-but-not-mislead (Basic/10b-5). Keeps compliance-vs-strategic OPEN for P7.", "Scope materiality to the ACQUIRER; a small bolt-on may be immaterial to a large acquirer.", "Theory (Verrecchia/Dye) is the LENS that withholding states are informative; the legal cites establish THIS firm is in such a state. Do not conflate voluntary (theory) with compelled (legal)."], "props": [{"prop_id": "P1.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "verrecchia1983", "ref": "Verrecchia (1983), JAE 5:179-194"}, "statement": "An informed manager may rationally choose NOT to disclose private information when disclosure is costly -- there is a threshold below which the informed manager withholds.", "role": "Establishes withholding as a rational, modeled equilibrium (not mere non-compliance) -> licenses reading a withholding state as economically meaningful."}, {"prop_id": "P1.2", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "dye1985", "ref": "Dye (1985), JAR 23(1):123-145"}, "statement": "Non-disclosure can persist in equilibrium because outside investors cannot always distinguish a manager who is uninformed from one who is informed but withholding.", "role": "Second, distinct theoretical foundation of withholding (the unraveling failure) -> silence is not self-revealing; a withholding state can be sustained and is informative."}, {"prop_id": "P1.3", "type": "legal-primary", "verdict": "SUPPORTED", "source": {"key": "basic_v_levinson", "ref": "Basic Inc. v. Levinson, 485 U.S. 224 (1988)"}, "statement": "Information about preliminary/pending merger negotiations can be material to investors before a definitive agreement exists; materiality turns on a probability-times-magnitude assessment, not a bright line.", "role": "Establishes that the pending (undisclosed) deal is MATERIAL -> combined with 'nonpublic' (definitional) it is MNPI. Anchors the disclosure-state premise in law."}, {"prop_id": "P1.4", "type": "legal-primary", "verdict": "SUPPORTED", "source": {"key": "basic_v_levinson + rule_10b5", "ref": "Basic Inc. v. Levinson, 485 U.S. 224 (1988) ('silence, absent a duty to disclose, is not misleading'); Rule 10b-5, 17 C.F.R. \u00a7240.10b-5"}, "statement": "A firm has no general affirmative duty to disclose confidential merger negotiations (silence is permitted), but once it speaks it may not mislead -- an untrue or half-true statement is unlawful. So denial is not a lawful option, leaving deflection.", "role": "Completes the BIND: explains why the CEO cannot simply deny and move on. The deflection->hedging CONSEQUENCE is developed in P3 (handoff)."}]}, {"pid": "P2", "intent": "The earnings call is where the bind becomes legible: a recurring, semi-spontaneous event whose unscripted Q&A is far less managed than prepared remarks, and a large literature shows call LANGUAGE carries information beyond the numbers. Reading it quantitatively -- finance-specific word-classification dictionaries, on the presentation/Q&A split -- is an established method this paper ADOPTS. P2 makes NO novelty claim: prior work already measures uncertainty language (hassan2020, DWZ, baker2016/davis2016); our novelty is the anticipatory x cash-concentrated, residualized, disclosure-state-tracking APPLICATION, which is P6's to state.", "thin_claim": "Adopt established methods ONLY. Make NO novelty claim here: prior work (hassan2020 -- cited in 2.5 as the convergent-validity benchmark our residual loads ON -- plus DWZ, baker2016/davis2016) DOES measure uncertainty language. 'First to measure uncertainty' would contradict 2.5 and is the everhart/gokkaya scar. Novelty = the anticipatory x cash-concentrated residualized application, stated narrowly in P6 ('to our knowledge').", "guardrails": ["DROPPED P2.3 (Bushee, Gow & Taylor 2018 'linguistic complexity'): complexity is Bushee's OWN construct and a RIVAL measure, NOT uncertainty. We measure linguistic UNCERTAINTY (the LM uncertainty word-list). Citing a complexity paper to license an uncertainty read is a construct mismatch and invites the 'why not complexity' referee attack. (user, 2026-06-12)", "NO NOVELTY CLAIM in P2 (advisor 2026-06-12): prior work measures uncertainty language -- hassan2020 is cited in 2.5 as the convergent benchmark our residual loads ON; also DWZ, baker2016/davis2016. 'Prior work hasn't read uncertainty' is FALSE and self-contradicts 2.5. Novelty -> P6 only, scoped to the anticipatory x cash-concentrated residualized application."], "props": [{"prop_id": "P2.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "matsumoto2011", "ref": "Matsumoto, Pronk & Roelofsen (2011), 'What Makes Conference Calls Useful? The Information Content of Managers' Presentations and Analysts' Discussion Sessions', The Accounting Review 86(4):1383-1414"}, "statement": "The analyst-discussion (Q&A) session of a conference call carries incremental information content beyond the managers' prepared presentation. (The 'less scripted than prepared remarks' point is DEFINITIONAL background, not the queried claim.)", "role": "Licenses reading the Q&A as the informative, less-managed unit AND establishes the presentation/Q&A split the whole design rests on."}, {"prop_id": "P2.2", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "lm2011", "ref": "Loughran & McDonald (2011), 'When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks', Journal of Finance 66(1):35-65"}, "statement": "Off-the-shelf word lists (e.g. the Harvard dictionary) misclassify financial text; Loughran & McDonald build finance-specific word lists -- including the uncertainty list this paper's measure uses -- to classify tone/uncertainty in financial disclosures.", "role": "Establishes the provenance + validity of the LM finance-specific uncertainty word-list the measure is built on (the load-bearing claim). Any 'uncertainty is informative' evidence rides as BONUS."}]}, {"pid": "P3", "intent": "Under the bind, the CEO cannot answer the forbidden question directly, so unscripted answers turn hedged, qualified, non-committal -- uncertainty language rises in the Q&A. Keyed to the undisclosed state, the rise is present while the deal is secret and resolves once announcement makes it public (the information clock).", "thin_claim": "A pattern keyed to the disclosure state -- no causal claim about CEO intent.", "guardrails": ["ADVISOR_FIX_sign: earn the DIRECTION (UP). A gagged CEO could go more guarded -> measure DOWN. Affirmative reason for UP: live Q&A, analysts follow up, sustained clean deflection is hard -> hedging leaks. H1 one-tailed.", "PREMISE-ONLY (advisor 2026-06-12): Hollander is cited ONLY for the premise -- managers strategically manage call disclosure AND non-answers/silence are informative. The UP sign is H1 (one-tailed, tested in results), NEVER cited; citing the sign would BE P6's novelty (self-contradiction). 'Silence speaks' cuts toward DOWN (stay silent -> fewer words) -- frame as: the bind REMOVES the clean-silence option (sustained live Q&A) so non-disclosure leaks as hedging in WORDS."], "props": [{"prop_id": "P3.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "hollander2010", "ref": "Hollander, Pronk & Roelofsen (2010), 'Does Silence Speak? An Empirical Analysis of Disclosure Choices During Conference Calls', JAR 48(3):531-563"}, "statement": "Managers make strategic disclosure/silence choices during conference calls, and non-answers / silence are themselves informative to the market.", "role": "Grounds the deflection mechanism in the call-silence literature (PREMISE ONLY -- the UP sign is H1, never cited)."}]}, {"pid": "P4", "intent": "Call-language uncertainty is partly a CEO's persistent style: managers differ durably in how they speak (a fixed trait), not an anticipatory signal. So an anticipatory, deal-tracking component must appear and disappear within one executive's tenure -> it can only live in the call-VARYING part, once persistent style is netted out. The persistent/time-varying decomposition this paper FOLLOWS is DWZ's; that managers carry persistent fixed-effect components at all is established in the PUBLISHED Bertrand & Schoar. P4 makes a CONDITIONAL-LOCATION claim only: IF an anticipatory signal exists, it must sit in the call-varying part.", "thin_claim": "States the locating logic; construction + caveats (generated regressand, UncPre) are 2.3.", "guardrails": ["ADVISOR_FIX_necessity: NECESSARY-condition only -- the signal MUST be in the residual. Do NOT drift to 'the residual IS the deal signal'; the P5 placebo + timing design isolate it.", "ADVISOR_FIX_attribution (2026-06-12): cite DWZ STRICTLY for 'the persistent/time-varying decomposition exists, done by DWZ'. The location logic (signal must be in the residual) is THE THESIS'S OWN -- attribute it to nobody. NEVER phrase it so DWZ appears to endorse the residual as signal-bearing: DWZ found the residual carries NO market/price signal. That null is NOT P4's -- it lives in 2.3 (defensive: why we still expect signal in our conditioned cash setting) + 3 (the cash-positive contrast).", "B-S anchors the PREMISE only (persistent components are real, in firm POLICIES) -- NOT the language decomposition (DWZ's) and NOT any signal claim. DWZ is a WORKING paper; B-S (published) carries the premise so the argument does not rest on unpublished work."], "props": [{"prop_id": "P4.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "bertrand_schoar2003", "ref": "Bertrand & Schoar (2003), 'Managing with style', QJE 118(4):1169-1208"}, "statement": "Managers have persistent, individual styles that load as manager fixed effects in firm policies/outcomes -- a measurable, durable manager-specific component.", "role": "PUBLISHED anchor: persistent manager components are real. Premise only -- NOT the language method (DWZ), NOT a residual-is-signal claim."}, {"prop_id": "P4.2", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "dwz2021", "ref": "Dzielinski, Wagner & Zeckhauser, 'Straight Talkers and Vague Talkers' (working paper)"}, "statement": "Managers' uncertainty/clarity language in earnings conference calls decomposes into a persistent manager-specific component (a CEO fixed effect) and a time-varying, call-level residual; DWZ construct exactly this decomposition.", "role": "GATING. The decomposition method this paper follows -> the call-varying residual is where an anticipatory signal must live. Cite DWZ ONLY for the decomposition's existence, NEVER for the residual carrying signal."}, {"prop_id": "P4.3", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "dwz2021", "ref": "Dzielinski, Wagner & Zeckhauser, 'Straight Talkers and Vague Talkers' (working paper)"}, "statement": "DWZ find that the time-varying (residual) component of call uncertainty is largely unrelated to market/stock-price reactions -- it explains little for prices.", "role": "NON-GATING record. Captured now (source open) for 2.3 (defensive) + 3 (the cash-positive CONTRAST to DWZ's price-null). Do NOT draft this into P4."}]}, {"pid": "P5", "intent": "Cash and stock deals differ in one design-relevant way: a cash purchase requires an accumulated, visible balance-sheet position -- a war chest -- while a stock deal carries the identical disclosure setting with no comparable visible cash commitment. That makes stock the placebo and a cash-CONCENTRATED signal informative on its own; WHY cash differs is left open. The two clocks then diverge: uncertainty tracks the information and resolves at announcement, while the cash position serves the purchase and -- mechanically -- persists until paid at completion.", "thin_claim": "A where-it-appears CONTRAST; the why stays open; the cash-persistence leg is mechanical.", "guardrails": ["ADVISOR_FIX_contrast (A2): stock = same setting minus visible cash. Mechanism OPEN (P7).", "DROPPED P5.2 (Bates 2009 / Opler 1999): 'analysts watch cash' is one step from the FORBIDDEN scrutiny channel (visible cash -> analysts probe -> CEO hedges) that 4.1 rules out -- dropped on the GUARDRAIL, not availability (Bates IS in the notebook). Harford alone carries the accumulated-cash-position claim; do NOT re-add to 'strengthen' P5. (advisor 2026-06-12)"], "props": [{"prop_id": "P5.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "harford1999", "ref": "Harford (1999), 'Corporate cash reserves and acquisitions'"}, "statement": "Firms accumulate cash reserves ahead of acquisitions, and cash-rich firms are more acquisitive -- a cash purchase reflects an accumulated balance-sheet position.", "role": "Grounds the 'visible accumulated cash position' that distinguishes cash from stock deals."}]}, {"pid": "P6", "intent": "The nearest work reads how corporate language around deals is MANAGED -- tone of prepared press releases before stock-for-stock deals, volume of strategy vocabulary on calls -- and adjacent work studies guidance and the information in disclosed acquisition plans; a separate literature documents pre-announcement leakage on the price side. What none reads is UNMANAGED language along an uncertainty dimension, before a cash deal, in the anticipatory window. That empty cell is where this paper sits.", "thin_claim": "'We read what unmanaged language discloses' is a framing/positioning claim, not a tested mechanism.", "guardrails": ["ADVISOR_FIX_novelty: the GAP claim ('no prior work reads this') is NOT NLM-verifiable -> 'to our knowledge', full stop. Only PER-PAPER claims run through NLM.", "THINNED (advisor 2026-06-12): kept Thewissen + Ragozzino (load-bearing deal-language neighbors). DROPPED Everhart/Gokkaya (guidance / disclosed-plans) -- self-foreclosed by the anticipatory PRE-disclosure framing (the deal is NOT yet disclosed -> not guidance, not a disclosed plan) AND sources unresolved. Discriminator: forecloses no LIVE distinct objection + hard-to-resolve = clean cut.", "KEOWN (P6.3): cite for the FACT only -- abnormal pre-announcement stock-price run-up exists -> our LANGUAGE signal differs from the known PRICE signal. Do NOT cite its insider-trading MECHANISM (insider trading is neither the compliance nor the strategic-silence reading -> would muddy P7). (advisor 2026-06-12)"], "props": [{"prop_id": "P6.1", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "thewissen2024", "ref": "thewissen2024 (in notebook, ssrn-4900453)"}, "statement": "Thewissen et al. (2024) study tone management in earnings press releases before stock-for-stock acquisitions.", "role": "Nearest-work cell: managed tone, stock deals, press releases. Forecloses 'isn't this just managed deal tone?'"}, {"prop_id": "P6.2", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "ragozzino2024", "ref": "ragozzino2024 (in notebook, S0024630123001000)"}, "statement": "Ragozzino & Reuer (2024) study strategy-vocabulary volume on calls around deal activity.", "role": "Nearest-work cell: managed strategy vocabulary on calls. Forecloses 'isn't this just deal-strategy talk on calls?'"}, {"prop_id": "P6.3", "type": "external-NLM", "verdict": "SUPPORTED", "source": {"key": "keown1981", "ref": "Keown & Pinkerton (1981), 'Merger Announcements and Insider Trading Activity', JF 36(4):855-869 (uploaded 2026-06-12)"}, "statement": "Abnormal stock-price run-up occurs before public M&A announcements -- pre-announcement leakage is documented on the PRICE side.", "role": "Forecloses THE live confound: 'isn't this just the known pre-announcement price run-up?' Splits our LANGUAGE signal from the PRICE signal. Cite for the run-up FACT ONLY -- NOT the insider-trading mechanism (advisor)."}, {"prop_id": "P6.4", "type": "framing-nonverifiable", "verdict": "INCONCLUSIVE_MANUAL", "source": {"key": "n/a", "ref": "cannot prove a negative"}, "statement": "To our knowledge, no prior work reads unmanaged uncertainty language before cash deals in the anticipatory window.", "role": "The gap / contribution."}]}, {"pid": "P7", "intent": "Two readings of the prediction -- compliance-constrained disclosure (the CEO legally cannot speak) and strategic silence (the CEO chooses not to) -- are observationally equivalent in our data; we do not separate them, and the framework does not require it. We document a pattern keyed to the disclosure state, claim no identification, and leave the mechanism open.", "thin_claim": "Observational equivalence + no-identification stated plainly. Guarantees the review does not inflate the claim.", "guardrails": ["P7 has NO external props; its prose is ALL connective claims -> the step-10 accuracy pass IS the whole paragraph (not a skip). Two readings (compliance-constrained vs strategic silence) observationally equivalent; no identification; pattern not mechanism. (advisor 2026-06-12)"], "props": []}]}]} // s2_2_1
const EVIDENCE = {"SV1": {"cite": "shleifer_vishny2003", "text": "Using overvalued shares as a means of payment enhances the claim on capital of the bidding shareholders, and thereby cushions the collapse of the shares in the long run.", "page": "300", "section": "3. The arithmetics of returns [1]"}, "SV2": {"cite": "shleifer_vishny2003", "text": "For this reason as well, it might be better to use overvalued equity to buy other overvalued firms than to invest in cash.", "page": "302", "section": "4. Discussion [3]"}, "SV3": {"cite": "shleifer_vishny2003", "text": "Our model takes mispricing as given. But it also points to a powerful incentive for firms to get their equity overvalued, so that they can make acquisitions with stock.", "page": "308", "section": "6. Conclusion [4, 5]"}, "SV4": {"cite": "shleifer_vishny2003", "text": "We show that the key ingredients of the answers are the relative valuations of the combining firms and the synergies that the market perceives in the merger.", "page": "296", "section": "1. Introduction [6]"}, "SV5": {"cite": "shleifer_vishny2003", "text": "Both of these findings are consistent with our view that acquisitions completed with stock arise from the overvaluation of the bidder relative to the target.", "page": "304", "section": "5.1. Implications for the cross-section of returns [7]"}, "SV6": {"cite": "shleifer_vishny2003", "text": "First, the model predicts that targets in cash acquisitions are undervalued in absolute terms (i.e., relative to fundamentals), but targets in stock acquisitions are undervalued relative to the bidders.", "page": "307", "section": "5.3. Untested predictions [8]"}, "SV7": {"cite": "shleifer_vishny2003", "text": "To begin, we expect targets of cash acquisitions to be undervalued firms, and moreover, we predict that such acquisitions are more likely to be hostile than those for stock. We are likely to see acquisitions for stock under a combination of three circumstances. First, market valuations must be high, and there must be a supply of highly overvalued firms (bidders) as well as of relatively less overvalued ones (targets).", "page": "303", "section": "4. Discussion [9]"}, "LO1": {"cite": "louis2004", "text": "I find strong evidence suggesting that acquiring firms overstate their earnings in the quarter preceding a stock swap announcement.", "page": "121", "section": "Abstract"}, "LO2": {"cite": "louis2004", "text": "The median abnormal current accrual is significantly positive for bidders engaging in stock swaps, whereas it is statistically insignificant for acquirers that pay with cash.", "page": "134", "section": "4.3. Earnings management prior to merger announcements"}, "LO3": {"cite": "louis2004", "text": "For the stock-for-stock acquirers, there is a jump in the abnormal accrual in the quarter immediately prior to the merger announcement.", "page": "134", "section": "4.3. Earnings management prior to merger announcements"}} // 10 quotes

if (typeof args === 'string') { try { args = JSON.parse(args) } catch (e) { args = {} } }
if (!args || typeof args !== 'object') args = {}

// ===================== locked Phase-3 inputs (section-agnostic constants; ASCII only) =====================
const MASKING_DECISION = `LOCKED why-cash motivation (Phase 3) -- the MASKING ASYMMETRY:
- A STOCK deal pays in equity, a currency whose price matters, so the acquirer has an incentive to keep its valuation high and manages perceptions UP before the deal (scripted optimism).
- A CASH deal pays in cash, with no currency to protect, so there is no such incentive.
- Therefore cash is the (relatively) UNMANAGED window where the disclosure-strain surfaces as unscripted Q&A uncertainty, and the run-up CONCENTRATES in cash.
This is a MOTIVATION (an ex-ante reason to focus on cash), NOT a tested mechanism.`

const HONESTY_FLOOR = `HONESTY FLOOR -- non-negotiable; every proposed change must obey it:
- Data: cash run-up +0.0461 (p=.0074, significant); stock -0.0429 (not significant -- a noisy flat null); Wald cash-minus-stock 0.0983 (p=.039, two-tailed).
- NEVER say or imply "stock suppressed" or that stock is pushed below its baseline. The cash>stock differential is ATTENUATION (the stock effect is smaller and noisier), and the observed gap is CASH RISING. We interpret, we do not detect.
- Cross-channel bridge: the cited papers document management in SCRIPTED channels (earnings numbers, press-release tone); our dependent variable is the UNSCRIPTED Q&A residual, net of the scripted presentation, so we read the hardest-to-manage channel -- frame this as a STRENGTH, not a gap.
- Register locks stay intact: correlational; no-identification; concentration-not-strict-specificity; mechanism-open; supportive-not-definitive.
- The timing round-trip result (C1) carries the paper independently of masking; if a reader rejects the why-cash, the empirical contribution still stands.`

const CITE_STACK = `CITE STACK -- the ONLY admissible sources for the new motivation. Cite each on its correct axis; mixing axes is an error:
- shleifer_vishny2003 (Shleifer and Vishny 2003, JFE 70:295-311): the currency/valuation MOTIVE -- equity is the acquisition currency, so an overvalued bidder has an incentive to keep its price high to pay with stock. Cite as VALUATION, NEVER as tone. (evidence IDs prefixed SV)
- louis2004 (Louis 2004, JFE 74:121-148): pre-deal EARNINGS behavior -- bidders overstate earnings in the quarter before a stock-swap announcement. Cite as EARNINGS-NUMBER management at the genre level, NEVER as tone. (evidence IDs prefixed LO)
- thewissen2024 (SSRN preprint): the TONE leg (our own axis), a supplementary one-clause pointer only; its anchor already lives in the current chain; it carries NO ev_id (ev_ids stays empty for a thewissen prop).
- harford1999 is the OLD why-cash source already in the chain (cash-accumulation / war-chest). Under the new motivation it is DEMOTED -- relocate it to a mechanical role (e.g. the differential-timing/two-clocks node) rather than the why-cash rationale; do not delete the fact, just stop it carrying the why.`

// ===================== output contract (schema-forced; ledger-shaped + ordered) =====================
const DISPOSITIONS = ['retain', 'reword', 're-derive', 'add', 'demote', 'relocate', 'delete']
const SOURCE_KEYS = ['shleifer_vishny2003', 'louis2004', 'thewissen2024', 'harford1999', 'internal', 'none']
const PROP_TYPES = ['external-NLM', 'framing-nonverifiable', 'callback-verified', 'internal-hypothesis', 'verified-DWZ-NLM', 'verified-code', 'bible-verbatim', 'internal-table', 'definitional']

const PROP_ITEM = {
  type: 'object', additionalProperties: false,
  required: ['position', 'disposition', 'prop_id', 'statement', 'role_in_paragraph', 'type', 'source_key', 'ev_ids', 'relocate_to', 'rationale'],
  properties: {
    position: { type: 'integer' },                 // 1-based order within the paragraph's NEW chain
    disposition: { type: 'string', enum: DISPOSITIONS },
    prop_id: { type: 'string' },                   // retain/reword/...: the EXISTING id; add: the proposed new id
    statement: { type: 'string' },                 // a CRISP single claim in the register of the existing props; "" iff disposition=retain
    role_in_paragraph: { type: 'string' },         // "" allowed iff retain
    type: { type: 'string', enum: PROP_TYPES },
    source_key: { type: 'string', enum: SOURCE_KEYS },
    ev_ids: { type: 'array', items: { type: 'string' } },  // evidence IDs; [] for internal/none/thewissen/retain
    relocate_to: { type: 'string' },               // "" unless disposition=relocate; else the target like "2.2 P4"
    rationale: { type: 'string' },                 // why; ties to the masking motivation + honesty floor; "" allowed iff retain
  },
}
const TOUCHED_PARA = {
  type: 'object', additionalProperties: false,
  required: ['subsection', 'paragraph', 'why', 'proposed_chain'],
  properties: {
    subsection: { type: 'string' },
    paragraph: { type: 'string' },                 // the paragraph key, e.g. "P5"
    why: { type: 'string' },                       // why this paragraph's chain is rewired
    proposed_chain: { type: 'array', items: PROP_ITEM },  // the COMPLETE ordered chain: EVERY original prop accounted for + any added
  },
}
const LOGIC_ITEM = {
  type: 'object', additionalProperties: false,
  required: ['subsection', 'link', 'change', 'rationale'],
  properties: {
    subsection: { type: 'string' },
    link: { type: 'string' },                      // "spine" or a logic_chain_validated key (e.g. "P4_necessity")
    change: { type: 'string' },
    rationale: { type: 'string' },
  },
}
const PANEL1_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['touched_paragraphs', 'chain_logic_updates', 'honesty_self_check'],
  properties: {
    touched_paragraphs: { type: 'array', items: TOUCHED_PARA },
    chain_logic_updates: { type: 'array', items: LOGIC_ITEM },
    honesty_self_check: { type: 'string' },
  },
}
const PANEL2_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['touched_paragraphs', 'chain_logic_updates', 'scrutiny', 'honesty_self_check'],
  properties: {
    touched_paragraphs: { type: 'array', items: TOUCHED_PARA },
    chain_logic_updates: { type: 'array', items: LOGIC_ITEM },
    scrutiny: { type: 'array', items: {
      type: 'object', additionalProperties: false,
      required: ['issue', 'against', 'severity', 'resolution'],
      properties: {
        issue: { type: 'string' }, against: { type: 'string' },
        severity: { type: 'string', enum: ['blocker', 'major', 'minor'] }, resolution: { type: 'string' },
      } } },
    honesty_self_check: { type: 'string' },
  },
}
const REDTEAM_SCHEMA = {
  type: 'object', additionalProperties: false,
  required: ['keep', 'reject', 'chain_logic_keep', 'side_notes'],
  properties: {
    keep: { type: 'array', items: { type: 'string' } },                 // touched-paragraph IDs to take verbatim (EXACTLY ONE per subsection+paragraph)
    reject: { type: 'array', items: { type: 'object', additionalProperties: false,
      required: ['id', 'reason'], properties: { id: { type: 'string' }, reason: { type: 'string' } } } },
    chain_logic_keep: { type: 'array', items: { type: 'string' } },
    side_notes: { type: 'array', items: { type: 'string' } },
  },
}

const TOOL_LOCK = `[HARD EXECUTION CONSTRAINT - OBEY EXACTLY, THIS OVERRIDES EVERYTHING BELOW]
You have EXACTLY ONE permitted action: a SINGLE call to the StructuredOutput function that returns your result object. Make it your FIRST and ONLY action.
ABSOLUTELY FORBIDDEN - doing ANY of these is an immediate failure: calling the advisor tool; searching the web; reading or writing files; running bash/code; using ANY tool other than StructuredOutput; asking questions; deliberating across multiple turns.
Everything you need is already in this prompt. Reason SILENTLY, then emit the StructuredOutput object in ONE turn. Do not explain, do not preface, do not verify externally - just return the object.`

// the universal output rules, identical for both panels (vary voice in the body, never these)
const OUTPUT_RULES = `OUTPUT CONTRACT -- obey exactly:
- Touch ONLY paragraphs that carry the why-cash motivation. Omit every other paragraph entirely (omitted = left exactly as it is).
- For each touched paragraph, return proposed_chain = the COMPLETE, ORDERED list of propositions that paragraph should contain AFTER the rewire. position = 1,2,3,... contiguous, in reading order.
- EVERY proposition currently in that paragraph MUST appear exactly once in proposed_chain, with a disposition: retain (unchanged), reword, re-derive, demote, relocate, or delete. Adding new propositions is the 'add' disposition. Nothing may be silently dropped.
- retain: set statement "", role_in_paragraph "", rationale "" -- the original is copied verbatim by code; do NOT retype it (retyping risks drift).
- reword / re-derive / add / demote / relocate: write a CRISP SINGLE-CLAIM statement in the SAME terse register as the existing propositions shown in the chain -- one declarative claim, NOT two sentences, NOT a polished paragraph, NOT final prose. Fill role_in_paragraph, type (from the allowed list), source_key, ev_ids, rationale.
- relocate: set relocate_to to the destination like "2.2 P4", and ALSO list the prop in that destination paragraph's proposed_chain as an 'add'.
- Evidence by ev_id ONLY (never retype a quote). A motive claim sourced to shleifer_vishny2003 or louis2004 MUST carry at least one ev_id. A thewissen tone pointer carries none.
- Do NOT write final prose. You redesign the proposition chain only.`

// ===================== render embedded data into prompt text =====================
function chainText() {
  return SECTION.subsections.map(ss => {
    const lcv = Object.entries(ss.logic_chain_validated || {}).map(([k, v]) => `    - ${k}: ${v}`).join('\n')
    const paras = (ss.paragraphs || []).map(p => {
      const gr = (p.guardrails || []).length ? '\n    guardrails:\n' + p.guardrails.map(g => `      - ${g}`).join('\n') : ''
      const tc = p.thin_claim ? `\n    thin_claim: ${p.thin_claim}` : ''
      const props = (p.props || []).map(pr => {
        const src = pr.source && pr.source.key ? `  source=${pr.source.key}${pr.source.ref ? ' (' + pr.source.ref + ')' : ''}` : ''
        return `      ${pr.prop_id} [${pr.type}] (verdict=${pr.verdict})${src}:\n        statement: ${pr.statement}` +
          (pr.role ? `\n        role: ${pr.role}` : '')
      }).join('\n')
      return `  [${p.pid}] intent: ${p.intent || ''}${tc}${gr}\n    propositions (in order):\n${props}`
    }).join('\n\n')
    return `========== SUBSECTION ${ss.subsection} -- ${ss.title} ==========\n` +
      `section_job: ${ss.section_job || ''}\n` +
      `spine: ${ss.spine || ''}\n` +
      (lcv ? `logic_chain_validated:\n${lcv}\n` : '') +
      `\n${paras}`
  }).join('\n\n')
}
function evidenceText() {
  return Object.entries(EVIDENCE).map(([id, e]) =>
    `  ${id}  [${e.cite}, p.${e.page}, sec ${e.section}]\n    "${e.text}"`).join('\n')
}
const SHARED_INPUTS = () => `===== LOCKED DECISION =====\n${MASKING_DECISION}\n\n${HONESTY_FLOOR}\n\n${CITE_STACK}\n\n` +
  `===== EVIDENCE POOL (cite by ev_id; NEVER retype a quote) =====\n${evidenceText()}\n\n` +
  `===== CURRENT PROPOSITION CHAIN (section ${SECTION.section}) =====\n${chainText()}`

// ===================== PANEL-1: 3 identical-task prompts, heavily paraphrased; NO examples =====================
function panel1Prompt(version) {
  const body = {
    1: `You are a thesis-argument analyst. The project has locked a NEW reason for why the measured language run-up should concentrate in CASH acquisitions (the masking asymmetry, under LOCKED DECISION). The proposition chain below still rests on an OLDER reason for singling out cash. Rebuild the chain so it carries the new reason.
Decide for yourself, from the chain and the locked decision, exactly which paragraphs establish or depend on the why-cash motivation, and rebuild ONLY those paragraphs' proposition chains. Leave every other paragraph untouched. Hunt down every place the old motivation does work, including any wording (for instance the term used for the stock comparison) that quietly carries identification weight.`,
    2: `Act as a referee of this section's logical chain. A new motivation for the cash focus has been fixed (the masking asymmetry under LOCKED DECISION); the propositions below were built on an earlier motivation. Convert the chain so the cash focus is justified by the new motivation.
Work out yourself which paragraphs carry the why-cash reasoning -- and which merely lean on it -- and rebuild only those paragraphs' chains; leave the rest exactly as written. Be thorough about locating the old reasoning wherever it hides, including any single word that does identification work in a proposition's claim.`,
    3: `You are reverse-engineering and repairing a section's argument. The thesis now commits to a specific account of why the run-up should concentrate in CASH deals -- the masking asymmetry under LOCKED DECISION -- but the chain below was written around an older account. Re-engineer the chain to run on the new account.
Determine independently which paragraphs do the why-cash work, then rebuild just those paragraphs' proposition chains; do not disturb any other paragraph. Search out every trace of the old motivation, including any terminology that silently performs identification within a claim.`,
  }[version]
  return `${TOOL_LOCK}\n\n${body}\n\nGround every changed or added proposition in the cite stack on its correct axis and attach its evidence by ev_id; give each a rationale tying it to the masking motivation and the honesty floor. Also propose any needed edits to the section spine or the named logic links.\n\n${OUTPUT_RULES}\n\n${SHARED_INPUTS()}\n\n===== RETURN =====\nReturn your redesign via the structured tool. Your returned object IS the data, not a message.`
}

// ===================== PANEL-2: 3 paraphrased; damage-red-team the 3 Panel-1 sets + author one hardened set =====================
function panel2Prompt(version, p1) {
  const proposals = p1.map((r, i) => `----- PANEL-1 AGENT ${i + 1} -----\n${JSON.stringify(r, null, 1)}`).join('\n\n')
  const body = {
    1: `You are a hardening reviewer. Three analysts each independently rebuilt this section's why-cash paragraph chains onto the masking asymmetry; their redesigns are below. Author ONE corrected, hardened redesign of your own by scrutinising all three.`,
    2: `Serve as the quality gate over three independent rebuilds of this section's why-cash paragraph chains (below), each shifting them onto the masking asymmetry. Author a single, stronger redesign by interrogating all three.`,
    3: `You are the adversarial checker for three proposed rebuilds of this section's why-cash paragraph chains onto the masking asymmetry (below). Author one hardened redesign after stress-testing all three.`,
  }[version]
  return `${TOOL_LOCK}\n\n${body}
Check every proposed change for: (a) any breach of the honesty floor -- above all the faintest hint that the stock effect is "suppressed" or pushed below baseline (the framing must be attenuation, with the observed gap being cash rising); (b) a cite used off its axis (valuation motive vs earnings behaviour vs tone); (c) evidence that does not support the claim it is attached to (the ev_id points into the EVIDENCE POOL); (d) damage to the chain -- confirm NO paragraph outside the why-cash motivation is touched, EVERY original proposition of a touched paragraph is still accounted for (none silently dropped), and a 'retain' has not quietly become a reword; (e) order and coherence -- the proposed_chain reads start to finish as one developing argument; (f) gaps -- every place the old motivation appears is handled, including terminology that does identification work. Keep what is sound, repair what is weak, drop what is wrong, add anything the three missed, and log each issue in scrutiny.\n\n${OUTPUT_RULES}\n\n${SHARED_INPUTS()}\n\n===== THE THREE PANEL-1 REDESIGNS TO SCRUTINISE =====\n${proposals}\n\n===== RETURN =====\nReturn your hardened redesign + scrutiny log via the structured tool. Your returned object IS the data.`
}

// ===================== RED-TEAM: pick the best ordered chain per paragraph, BY REFERENCE =====================
function redteamPrompt(pool, logicPool) {
  return `${TOOL_LOCK}

You are the RED TEAM for this section's why-cash redesign. Three reviewers each authored a hardened redesign; below, each reviewer's per-paragraph proposed chain carries an ID, and each chain-logic update carries an ID. The evidence behind each change has fixed ev_ids -- do NOT re-check quotes.

Your job is SCRUTINISE + SELECT, BY REFERENCE ONLY. You never rewrite a chain; you emit decisions that reference IDs, and the main loop copies the referenced chains verbatim.

SCRUTINISE -- reject a paragraph chain (reject{id,reason}) when ANY holds:
- it breaches the honesty floor (implies the stock effect is suppressed or pushed below baseline; the only allowed framing is attenuation, observed gap = cash rising);
- it uses a cite off its axis (valuation motive vs earnings behaviour vs tone conflated);
- it touches a paragraph that is NOT part of the why-cash motivation, or drops an original proposition that should have been retained;
- its order is incoherent, or a statement is vacuous.
Use the LOCKED DECISION, HONESTY FLOOR, CITE STACK, EVIDENCE POOL, and CURRENT chain below to ground every rejection.

SELECT -- for EACH paragraph that genuinely needs the rewire, the three reviewers offer competing chains for the SAME paragraph: choose the ONE best (tiebreak: cleaner honesty-floor compliance, then stronger evidence, then better order/coherence) and put its ID in keep. keep MUST contain exactly ONE id per subsection+paragraph. chain_logic_keep: the logic-update IDs the kept rewire needs. side_notes: ONLY coverage-gap flags for a human (e.g. a paragraph all three missed); NEVER new content.

You invent nothing.

${SHARED_INPUTS()}

===== PER-PARAGRAPH PROPOSED CHAINS (id, reviewer, content) =====
${JSON.stringify(pool, null, 1)}

===== CHAIN-LOGIC UPDATES (id, reviewer, content) =====
${JSON.stringify(logicPool, null, 1)}

Return your decisions via the structured tool.`
}

// ===================== pipeline (one section; genuine barriers between layers) =====================
phase('Panel-1')
log(`[input] section ${SECTION.section}: ${SECTION.subsections.length} subsections, ` +
  `${SECTION.subsections.reduce((n, s) => n + (s.paragraphs || []).length, 0)} paragraphs, ` +
  `${SECTION.subsections.reduce((n, s) => n + (s.paragraphs || []).reduce((m, p) => m + (p.props || []).length, 0), 0)} props; ` +
  `${Object.keys(EVIDENCE).length} evidence quotes${args.panelOnly ? '  [DRY RUN: Panel-1 only]' : ''}`)

const p1 = (await parallel([1, 2, 3].map(v => () =>
  agent(panel1Prompt(v), { schema: PANEL1_SCHEMA, phase: 'Panel-1', label: `s${SECTION.section}/panel1-${v}` }))))
  .map(r => r || { touched_paragraphs: [], chain_logic_updates: [], honesty_self_check: 'NULL (agent failed)' })
log(`[panel-1] touched paragraphs: ${p1.map(r => (r.touched_paragraphs || []).length).join(', ')}`)

if (args.panelOnly) {
  return { section: SECTION.section, subsections: SECTION.subsections.map(s => s.subsection), panel1: p1, note: 'panelOnly_dry_run' }
}

phase('Panel-2')
const p2 = (await parallel([1, 2, 3].map(v => () =>
  agent(panel2Prompt(v, p1), { schema: PANEL2_SCHEMA, phase: 'Panel-2', label: `s${SECTION.section}/panel2-${v}` }))))
  .map(r => r || { touched_paragraphs: [], chain_logic_updates: [], scrutiny: [], honesty_self_check: 'NULL (agent failed)' })
log(`[panel-2] hardened touched paragraphs: ${p2.map(r => (r.touched_paragraphs || []).length).join(', ')}`)

// stable IDs across the Panel-2 pool for by-reference selection
const pool = [], logicPool = []
p2.forEach((r, ai) => {
  ;(r.touched_paragraphs || []).forEach(tp => pool.push({ id: `p2-${ai + 1}-${tp.subsection}-${tp.paragraph}`, reviewer: ai + 1, ...tp }))
  ;(r.chain_logic_updates || []).forEach((l, li) => logicPool.push({ id: `p2-${ai + 1}-l${li + 1}`, reviewer: ai + 1, ...l }))
})

phase('Red-team')
let redteam = null
if (pool.length > 0) redteam = await agent(redteamPrompt(pool, logicPool), { schema: REDTEAM_SCHEMA, phase: 'Red-team', label: `s${SECTION.section}/redteam` })

let final_touched = [], final_logic = [], note = 'ok'
if (!redteam) {
  final_touched = (p2[0] && p2[0].touched_paragraphs) || []
  final_logic = (p2[0] && p2[0].chain_logic_updates) || []
  note = pool.length ? 'redteam_failed_degraded_to_panel2_agent1' : 'no_panel2_output'
  log(`[red-team] NULL/skipped -> degrading to Panel-2 agent-1 (${final_touched.length} paragraphs); FLAG manual synthesis`)
} else {
  const byId = {}; pool.forEach(c => byId[c.id] = c)
  const byLid = {}; logicPool.forEach(l => byLid[l.id] = l)
  const rejectIds = new Set((redteam.reject || []).map(r => r.id))
  const seen = new Set()
  for (const id of (redteam.keep || [])) {
    const tp = byId[id]; if (!tp || rejectIds.has(id)) continue
    const key = `${tp.subsection}-${tp.paragraph}`
    if (seen.has(key)) { log(`[red-team] WARN duplicate keep for ${key} (${id}) -> ignored`); continue }
    seen.add(key); final_touched.push(tp)
  }
  final_logic = (redteam.chain_logic_keep || []).map(id => byLid[id]).filter(Boolean)
  if (final_touched.length === 0 && pool.length > 0) {
    final_touched = (p2[0] && p2[0].touched_paragraphs) || []; final_logic = (p2[0] && p2[0].chain_logic_updates) || []
    note = 'redteam_kept_zero_degraded'
    log(`[red-team] kept 0 -> degrading to Panel-2 agent-1; FLAG`)
  } else {
    log(`[red-team] final: ${final_touched.length} paragraphs, ${final_logic.length} logic updates kept`)
  }
}

return {
  section: SECTION.section,
  subsections: SECTION.subsections.map(s => s.subsection),
  panel1: p1, panel2: p2, pool, logicPool,
  redteam, final_touched, final_logic, note,
}