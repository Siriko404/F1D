# Drop the Phase-5 audited plain-language rewrite (phaseB_result.json) into the LOCKED uOttawa
# thesis WRAPPER, byte-for-byte same frontmatter / book class / geometry / fonts / tables / appendices.
# Everything is done in a CLONE dir so the originals are never touched.
#
# What changes vs the original uOttawa body:
#   - _abstract_body / _intro_body / _conclusion_body / sec34_body  <- regenerated from phaseB prose
#   - the inline Chapter-2 (sections 2.1-2.5) block in the wrapper   <- spliced from phaseB prose
#   - 5 phaseB-only refs added to the manual bibliography
# What stays identical (copied as-is): all frontmatter, _tables_from_bible, _dwz_replication,
#   appendix_I/II, page geometry, fonts, the bibliography's existing entries.
#
# Cite keys are reconciled to the wrapper's bib: basic_v_levinson->basic1988, rule_10b5->rule10b5,
# dwz2021->dwz; bare "DWZ"/"BGT" acronyms -> \citet{dwz}/\citet{bgt2018} (\citeauthor for possessive).
import json, re, shutil, subprocess, sys
from pathlib import Path

HARNESS = Path(__file__).resolve().parent
SRC = HARNESS.parents[1]                       # .../F1D-phase3/docs/Thesis
CLONE = SRC / "_uottawa_rewrite"
RES = json.load(open(HARNESS / "phaseB_result.json", encoding="utf-8"))
SEC = {s["section"]: s for s in RES["sections"]}

def normalize(t):
    # cite-key reconciliation to the wrapper bib (covers single- and multi-key \cite groups)
    t = re.sub(r"\bbasic_v_levinson\b", "basic1988", t)
    t = re.sub(r"\brule_10b5\b", "rule10b5", t)
    t = re.sub(r"\bdwz2021\b", "dwz", t)
    # bare acronyms -> proper citations (possessive first so the bare rule doesn't strip the 's)
    t = re.sub(r"\bDWZ's\b", r"\\citeauthor{dwz}'s", t)
    t = re.sub(r"\bBGT's\b", r"\\citeauthor{bgt2018}'s", t)
    t = re.sub(r"\bDWZ\b", r"\\citet{dwz}", t)
    t = re.sub(r"\bBGT\b", r"\\citet{bgt2018}", t)
    # let long inline $\{..\}$ control lists wrap (belt-and-suspenders; wrapper also has emergencystretch)
    t = re.sub(r"\},\s*\\mathit\{", r"},\\allowbreak \\mathit{", t)
    return t

def repoint_45(t):
    # Section 4.5 cites the ALL-DEALS panels; point those refs at the new combined robustness
    # tables (which carry BOTH the first-deal and all-deals panels), and wire the two logit refs.
    t = t.replace(r"\ref{tab:empire_building_did}", r"\ref{tab:rob_runup}")
    t = t.replace(r"\ref{tab:empire_drop_matched}", r"\ref{tab:rob_timing_matched}")
    t = t.replace(r"\ref{tab:empire_drop_placebo}", r"\ref{tab:rob_timing_placebo}")
    t = t.replace(r"\ref{tab:empire_cashspec}", r"\ref{tab:rob_cashspec}")
    t = t.replace("(Logit~A)", r"(Logit~A, Table~\ref{tab:logit_dealnext})")
    t = t.replace("(Logit~B)", r"(Logit~B, Table~\ref{tab:logit_cashstock})")
    # the first-deal 0.0983 used to sit in the rob table's now-removed Thesis panel; point to the main table
    t = t.replace(r"first-deal difference of $0.0983^{**}$ ($p=.039$) in the same table.",
                  r"first-deal difference of $0.0983^{**}$ ($p=.039$) reported in Table~\ref{tab:empire_cashspec}.")
    return t

# Section 2.5 lost its measure-validation content in the phaseB rewrite (4 orphaned tables).
# Restore it in the plain phaseB register: a new "construction" paragraph (DWZ replication ->
# tab:dwz_replication), a 2->3 roadmap renumber, and source cites + table refs on the convergent
# paragraph (-> tab:h11/h24/h24b). Numbers verified vs Table 5.21 body AND its footnotes:
# DWZ R^2 is reported incremental (~0.05 over a 0.31 base ~= 0.36 total) vs our total 0.369; the
# firm-controls match in sign not magnitude because they are standardized here, not because samples differ.
DWZ_CONSTRUCTION = (
    r"The first check is construction. Before we lean on the residual, we confirm that building it "
    r"our own way, on our own data, reproduces the estimates the method was validated on. We re-estimate "
    r"the \citet{dwz} decomposition on our sample and place our numbers beside their published ones, line "
    r"by line, in Table~\ref{tab:dwz_replication}, which reports two of our specifications: a Baseline that "
    r"matches the Section~2.3 equation exactly and supplies the residual we carry forward, and an Extended one "
    r"that adds a broader set of standard firm-financial controls as a robustness check. The largest piece lines up almost "
    r"exactly: the loading on the CEO's own prepared-remarks uncertainty is $0.089$ in our Baseline against "
    r"$0.093$ in theirs, and the other two speech controls keep the same sign and significance. The fit lines up "
    r"too, once the two are put on the same footing: their published figure is the controls' added explanatory "
    r"power, about $0.05$ on top of a $0.31$ base, so roughly $0.36$ in total, against our total $R^2$ of $0.369$. "
    r"The samples are not identical, ours covering non-financial, non-utility United States firms over 2002 to "
    r"2018 and theirs 2003 to 2015; the firm-performance controls, standardized here for numerical stability, are "
    r"not comparable in raw size; they agree in sign for the earnings controls, while the two market-return "
    r"controls differ -- StockRet flips sign, and MarketRet matches in sign but is significant in the original "
    r"only -- an expected divergence "
    r"across the different samples that does not bear on the residual. The point is narrow but "
    r"enough: because we build the residual the same way \citeauthor{dwz} do, the construct validity they "
    r"establish for the measure carries over to our setting, which leaves how it behaves in our own data as "
    r"the question for the checks below."
)

def augment_25(t):
    # A: roadmap two -> three checks (construction becomes the first)
    a_old = (r"We ask two things of $\mathrm{UncResCEO}$. First, is it convergent: does it move together with "
             r"measures of uncertainty that are already established? That is the check we run in this section. "
             r"Second, could a plausible rival")
    a_new = (r"We ask three things of $\mathrm{UncResCEO}$. First, does rebuilding it on our own data reproduce "
             r"the published estimates the method rests on? Second, is it convergent: does it move together with "
             r"measures of uncertainty that are already established? Those first two are the checks we run in this "
             r"section. Third, could a plausible rival")
    # B: insert the construction paragraph before the convergent-validity paragraph
    b_anchor = "We begin with convergent validity."
    # C: add source citations + table refs to the three convergent measures (numbers unchanged)
    c_old = (r"It rises with firm-level political risk (PRisk), with a coefficient of $0.0001^{***}$; with US "
             r"economic policy uncertainty (US-EPU), at $0.0124^{**}$ and $0.0123^{*}$, the second estimate only "
             r"marginally significant once firm fixed effects are included; and with global economic policy "
             r"uncertainty (GEPU), at $0.0181^{**}$ and $0.0187^{**}$.")
    c_new = (r"It rises with firm-level political risk (PRisk), the call-based measure of \citet{hassan2020}, with "
             r"a coefficient of $0.0001^{***}$ (Table~\ref{tab:h11_prisk_uncertainty}); with US economic policy "
             r"uncertainty (US-EPU), the newspaper-based index of \citet{baker2016}, at $0.0124^{**}$ and "
             r"$0.0123^{*}$ (Table~\ref{tab:h24_us_epu}), the second estimate only marginally significant once firm "
             r"fixed effects are included; and with global economic policy uncertainty (GEPU), the index of "
             r"\citet{davis2016}, at $0.0181^{**}$ and $0.0187^{**}$ (Table~\ref{tab:h24b_global_epu}).")
    for tag, old in (("A", a_old), ("B", b_anchor), ("C", c_old)):
        assert old in t, "augment_25 anchor %s not found -- section 2.5 prose changed" % tag
    t = t.replace(a_old, a_new, 1)
    t = t.replace(b_anchor, DWZ_CONSTRUCTION + "\n\n" + b_anchor, 1)
    t = t.replace(c_old, c_new, 1)
    return t

def fix_21(t):
    # Coherence: drop the lone "war chest" assertion in 2.1. The cash accumulation is a by-product
    # (2.4) and the war-chest CHANNEL is left open/unestablished (3.4, 5); 2.1 was the only place
    # asserting it. The "accumulated, visible cash position" already conveys the point.
    a = " -- a war chest, in effect --"
    assert a in t, "fix_21 anchor (war chest) not found"
    return t.replace(a, "")

def fix_34(t):
    # Coherence: 3.4 used $\theta_{-1}^{cash}-\theta_{-1}^{stock}$, a symbol defined nowhere; 2.4
    # defines the same test as $\beta_c-\beta_s$. Drop the orphan Greek for plain wording.
    a = r"That restriction is what estimates $\theta_{-1}^{\mathrm{cash}}-\theta_{-1}^{\mathrm{stock}}$ in hypothesis~H1a."
    assert a in t, "fix_34 anchor (theta) not found"
    return t.replace(a, r"That restriction is the formal expression of the cash-versus-stock gap that hypothesis~H1a predicts.")

# Issue H1 (Sina 2026-06-28; final-audit methodology HIGH): section 2.3 flagged the generated-regressand
# two-step SE concern (Pagan 1984) but then ASSERTED, without running the bootstrap, that it "does not change
# the descriptive readings we report" -- an unsupported claim a referee can press (the load-bearing run-up's
# significance rides on those SEs). Fix = state it as an HONEST LIMITATION: the correction is not implemented,
# the reported SEs are uncorrected, significance is approximate, and the reading rests on the pattern recurring
# across designs (which the thesis already shows) rather than on any single threshold. Faithful to DWZ: the
# preceding sentence (kept verbatim) notes DWZ themselves use the residual in their own two-step second step.
# PROSE ONLY -- no number, no math, no coefficient moves; the bootstrap is NOT run (Sina chose the prose fix).
def fix_23_se(t):
    a = ("We flag the concern, together with the bootstrap that would address it, and note that it does not "
         "change the descriptive readings we report.")
    assert a in t, "fix_23_se anchor (SE no-change assertion) not found -- 2.3 prose changed"
    return t.replace(a,
        "We flag the concern, together with the bootstrap that would address it, but we do not implement that "
        "correction here. The standard errors we report are therefore uncorrected, and the significance levels "
        "that accompany them should be read as approximate. The reassurance we rely on instead is that the same "
        "pattern recurs across our several designs.")

# ===== Audit fix batch (Sina 2026-06-28; decisions + evidence in _FIX_PLAN.md). All PROSE, no number moved. =====
def fix_32(t):
    # #4: Sina-confirmed Table 5.2 stars are TWO-tailed (runners empire_drop_test:191 / empire_cashspec:127 are
    # "uniform two-tailed"; 5.2 note "(two-tailed)"; t=2.68 -> two-tailed p=.0074). So the prose calling the
    # table "one-tailed" is the error -> reword to state plainly the coef is significant two-tailed.
    a = ("One might worry that the uncertainty result is an artifact of the table's one-tailed reporting "
         "convention; it is not. The residual coefficient survives a two-tailed test ($p=.0074$), so the "
         "load-bearing result does not depend on the reporting convention.")
    assert a in t, "fix_32 #4 anchor not found"
    return t.replace(a, "The residual coefficient is significant on the two-tailed test that "
                        "Table~\\ref{tab:empire_building_did} reports ($p=.0074$).")

def fix_41(t):
    # #3 (Sina: keep the scrutiny incidence-vs-volume issue silent): remove the sentence naming incidence as
    # "the genuine confound" (it set up the mismatch with the volume-based rule-out); its $0.0854$ is reworded
    # out, the prior sentence keeps the motivation. #7 (causal verb -> associational). #8 ("rule it out" -> "assess").
    a3 = (" The continuous, volume-based measure tells a weaker story --- in column~3 the "
          "$\\mathrm{CashScrutiny}$ coefficient is $0.0854$ (standard error $0.0749$), not significant --- so "
          "the genuine confound is whether cash scrutiny happens at all (its incidence), not how much of a call "
          "it fills (its volume).")
    assert a3 in t, "fix_41 #3 anchor not found"
    t = t.replace(a3, "")
    a7 = ("Put plainly: the reason for the deal raises uncertainty, the questioning does not, and the "
          "questioning does not amplify the reason either.")
    assert a7 in t, "fix_41 #7 anchor not found"
    t = t.replace(a7, "Put plainly: the pre-announcement quarter is associated with higher uncertainty, the "
                      "questioning is not, and the questioning does not interact with it either.")
    a8 = "We rule it out in three steps."
    assert a8 in t, "fix_41 #8 anchor not found"
    t = t.replace(a8, "We assess it in three steps.")
    return t

def fix_intro(t):
    # #8 (floor: don't overclaim a null) + #7 (causal "amplify") in the introduction
    a8 = "We also rule out the most immediate alternative."
    assert a8 in t, "fix_intro #8 anchor not found"
    t = t.replace(a8, "We also assess the most immediate alternative.")
    a7 = "the elevation survives and scrutiny does not amplify it."
    assert a7 in t, "fix_intro #7 anchor not found"
    t = t.replace(a7, "the elevation survives and scrutiny does not strengthen it.")
    a8b = "additional analyses, ruling out analyst scrutiny,"
    assert a8b in t, "fix_intro #8 roadmap anchor not found"
    t = t.replace(a8b, "additional analyses, assessing analyst scrutiny,")
    return t

def fix_unmanaged(t, sid):
    # #9 (honesty: flat "unmanaged" overclaims; the design supports only "relatively unmanaged" / "hardest to stage-manage")
    pairs = {
     "2.1": [("whereas ours is unmanaged uncertainty in the unscripted Q\\&A",
              "whereas ours is relatively unmanaged uncertainty in the unscripted Q\\&A")],
     "2.2": [("not managed tone before stock deals, but unmanaged uncertainty before cash deals",
              "not managed tone before stock deals, but relatively unmanaged uncertainty before cash deals")],
    }
    for old, new in pairs.get(sid, []):
        assert old in t, "fix_unmanaged[%s] anchor not found" % sid
        t = t.replace(old, new)
    return t

def fix_24(t):
    # #14 (style: only leading-zero p-value in the doc -> no-leading-zero convention)
    a = "remains significant at $p = 0.0074$ two-tailed"
    assert a in t, "fix_24 #14 anchor not found"
    return t.replace(a, "remains significant at $p=.0074$ two-tailed")

def fix_45_se(t):
    # #18 (style: prose SEs at 5dp vs 4dp tables) -> match the table cells (5.19=0.0027, 5.20=0.0508).
    # MUST run AFTER destars (its NOSE[4.5] anchor reads "$0.00275$").
    for old, new in [("$0.00275$", "$0.0027$"), ("$0.05076$", "$0.0508$")]:
        assert old in t, "fix_45_se anchor %s not found" % old
        t = t.replace(old, new)
    return t

def global_fixes(t):
    # #12 (whole-unit "Section~N"/"Sections~N" render as Chapters): -> Chapter~N, keeping "Section~N.M" subsection refs
    t = re.sub(r"\bSection~([1-5])(?![.0-9])", r"Chapter~\1", t)
    t = re.sub(r"\bSections~([1-5])(?![.0-9])", r"Chapters~\1", t)
    return t

# Issue 2 (Sina 2026-06-28): the prose states coefficients with significance STARS, which is non-standard.
# Replace each star with a COMPACT p-threshold, dropped inside/after the standard error the prose already
# gives -- matching its OWN style (it already reads "(standard error $0.0026$, $p=.0011$)"). (Sina saw a
# worded "significant at the one percent level" MA1 sample and judged compact neater.) PROSE ONLY -- the
# table bodies keep their stars + note. *** -> $p<.01$, ** -> $p<.05$, * -> $p<.10$ (no leading zero, as in
# the table notes + existing prose). Coefs already carrying an exact p ($p=.039$, $p=.0011$, ...) just lose
# the star. Mechanism (advisor-vetted): the regex copies the value + SE VERBATIM (back-refs) and only the
# star->threshold is computed, so a coefficient value can never be mis-transcribed; echoes (no SE) lose the
# star and stay bare, exactly as the old prose does. Significance level is verified vs each table cell.
PMAP = {1: ".10", 2: ".05", 3: ".01"}
# Two coef forms carry no parenthesised SE for the generic rule to tuck the threshold into, so add it here:
#  - 2.5 convergent/validity coefs (verified vs Tables 5.6/5.7/5.8/5.9);
#  - the 4.5 forward LPM+FE coef, whose SE is followed by ";" (verified vs the Logit-A table).
NOSE = {
 "2.5": [
  (r"a coefficient of $0.0001^{***}$ (Table",                 r"a coefficient of $0.0001$, $p<.01$ (Table"),
  (r"at $0.0124^{**}$ and $0.0123^{*}$ (Table",               r"at $0.0124$ ($p<.05$) and $0.0123$ ($p<.10$) (Table"),
  (r"at $0.0181^{**}$ and $0.0187^{**}$ (Table",              r"at $0.0181$ ($p<.05$) and $0.0187$ ($p<.05$) (Table"),
  (r"with coefficients of $0.7530^{***}$ and $0.8519^{***}$,", r"with coefficients of $0.7530$ ($p<.01$) and $0.8519$ ($p<.01$),"),
 ],
 "4.5": [
  (r"coefficient of $0.0078^{***}$ (standard error $0.00275$;", r"coefficient of $0.0078$ (standard error $0.00275$, $p<.01$;"),
 ],
}
def destars(t, sid):
    for old, new in NOSE.get(sid, []):
        assert old in t, "destars[%s] special anchor missing (prose changed?): %s" % (sid, old[:50])
        t = t.replace(old, new, 1)
    # (a) parenthesised SE (optional trailing ", one-tailed"): tuck the threshold inside the paren
    t = re.sub(r"\$(-?\d+\.\d+)\^\{(\*+)\}\$ \(standard error \$(\d+\.\d+)\$(, one-tailed)?\)",
               lambda m: "$%s$ (standard error $%s$, $p<%s$%s)" % (m.group(1), m.group(3), PMAP[len(m.group(2))], m.group(4) or ""), t)
    # (b) comma SE ("$V$, standard error $SE$"): append the threshold after the SE
    t = re.sub(r"\$(-?\d+\.\d+)\^\{(\*+)\}\$, standard error \$(\d+\.\d+)\$",
               lambda m: "$%s$, standard error $%s$, $p<%s$" % (m.group(1), m.group(3), PMAP[len(m.group(2))]), t)
    # (c) any remaining significance star -> strip (echoes; and coefs already carrying an exact p)
    t = re.sub(r"(\$-?\d+\.\d+)\^\{\*+\}\$", r"\1$", t)
    return t

# Issue 1 (Sina 2026-06-28; VERY SENSITIVE): thin the redundant honesty-floor repetition WITHOUT weakening
# the floor. Per-section SHORTEN/MERGE/CUT of redundant per-paragraph CLOSERS only; each section keeps its
# load-bearing statement of every floor element (correlational / no-cause / within-firm / mechanism-open /
# supportive-not-definitive / concentration-not-specificity). Untouched: intro, all of Chapter 2, MA3
# (cash-specificity, incl. "we leave that mechanism open"), and the Conclusion limitations paragraph.
# SAFETY: every anchor is hedge PROSE with ZERO math (asserted) -> no number can move; and
# floor_inventory.py must show no section dropping any element to zero after the rebuild.
DEHEDGE = {
 "3.2": [   # MA1 run-up (CORR/NOCAUSE/WITHIN all remain in "...within-firm... correlational design... causal effect")
  (" Because each firm is compared with itself, the pattern is within-firm; it remains correlational and does not identify a cause.", ""),
  ("These magnitudes are supportive but not definitive, and they do not establish a cause.",
   "These magnitudes are supportive but not definitive."),
 ],
 "3.3": [   # MA2 differential timing (keep the section's only WITHIN; CORR/NOCAUSE remain in the primary + closer)
  ("Throughout, firms are compared with themselves, the design is correlational, and it does not identify a cause.",
   "Throughout, firms are compared with themselves."),
  (" This remains a correlational reading, not a causal one.", ""),
 ],
 "4.1": [   # scrutiny rule-out (CORR already in the within-firm sentence above; SUPP/NOCAUSE/MECH stay here)
  ("The reading is correlational and supportive, not definitive; it identifies no cause, and the mechanism remains open.",
   "The reading is supportive, not definitive; it identifies no cause, and the mechanism remains open."),
 ],
 "4.3": [   # withdrawal robustness (CORR already in "This is a correlational concern..." above)
  ("The reading is correlational and supportive rather than definitive.",
   "The reading is supportive rather than definitive."),
 ],
 "4.4": [   # dynamic-term robustness -- merge the doubled "supportive rather than definitive"; CORR moves into l.92
  ("This is a robustness check and is supportive rather than definitive.",
   "This is a correlational robustness check, supportive rather than definitive."),
  (" The reading is correlational and supportive rather than definitive.", ""),
 ],
 "4.5": [   # first-deal robustness (NOCAUSE/CONC remain in "...concentration, not strict specificity, and with no cause asserted")
  ("The design stays correlational and identifies no causal effect, and we read it as concentration in cash deals, not strict specificity.",
   "The design stays correlational."),
 ],
}
def dehedge(t, sid):
    for old, new in DEHEDGE.get(sid, []):
        assert "$" not in old and "$" not in new, "dehedge[%s]: anchor touches math -- abort" % sid
        assert old in t, "dehedge[%s] anchor not found (prose changed?): %s" % (sid, old[:50])
        t = t.replace(old, new, 1)
    return t

def prose_of(sid):
    body = "\n\n".join(normalize(p["final_prose"].strip()) for p in SEC[sid]["paragraphs"])
    if sid == "4.5": body = repoint_45(body)
    if sid == "2.5": body = augment_25(body)
    if sid == "2.1": body = fix_21(body)
    if sid == "3.4": body = fix_34(body)
    if sid == "2.3": body = fix_23_se(body)    # Issue H1: SE no-change assertion -> honest limitation (PROSE ONLY)
    if sid == "3.2": body = fix_32(body)       # #4 Table 5.2 tail mislabel
    if sid == "4.1": body = fix_41(body)       # #3 scrutiny-silent + #7 causal verb + #8 rule-out phrase
    if sid == "1":   body = fix_intro(body)    # intro #7 + #8
    if sid in ("2.1", "2.2"): body = fix_unmanaged(body, sid)  # #9 flat "unmanaged"
    if sid == "2.4": body = fix_24(body)       # #14 leading-zero p
    body = destars(body, sid)                  # Issue 2: significance stars -> compact p (PROSE ONLY)
    body = dehedge(body, sid)                  # Issue 1: thin redundant honesty-floor closers (PROSE; never math)
    if sid == "4.5": body = fix_45_se(body)    # #18 SE 4dp (AFTER destars, whose NOSE[4.5] anchor reads $0.00275$)
    body = global_fixes(body)                  # #12 Section->Chapter (whole-unit), run LAST
    if sid in ("2.1", "2.2", "2.3", "2.4", "2.5"): body = body.replace(" -- ", "---")  # #15 Ch2 dashes, LAST
    return body

# ---- 1. clone every .tex in docs/Thesis so all \input deps resolve; originals untouched ----
CLONE.mkdir(exist_ok=True)
for f in SRC.glob("*.tex"):
    shutil.copy(f, CLONE / f.name)
print("cloned %d .tex files -> %s" % (len(list(CLONE.glob('*.tex'))), CLONE.name))

# patch the DWZ-replication table note: the firm-controls do NOT all match in significance (Table 5.21 cells)
_dwz = CLONE / "_dwz_replication.tex"
_nt = _dwz.read_text(encoding="utf-8")
_old_note = "standardized here, so their magnitudes are not comparable to the original's raw-unit coefficients, though signs and significance are."
_new_note = ("standardized here, so their magnitudes are not comparable to the original's raw-unit "
             "coefficients; signs agree for the earnings-surprise and EPS-growth controls, while among the "
             "market-return controls StockRet flips sign and MarketRet matches in sign but is significant in the original only.")
assert _old_note in _nt, "dwz-note anchor not found"
_nt = _nt.replace(_old_note, _new_note)
# Issue 3 (Sina 2026-06-28): 5.21 was the only table not bolding its significant coefficients. Bold every
# starred coef so it matches the other 20 tables; the value is carried verbatim by the back-reference and
# only \textbf is wrapped around it (the R^2 dagger and the unstarred cells are untouched).
_nt, _nb = re.subn(r"\$(-?\d\.\d+)\^\{(\*+)\}\$", r"\\textbf{\g<1>}$^{\g<2>}$", _nt)
assert _nb == 13, "dwz bolding: expected 13 starred coefs, got %d" % _nb
# add the bold clause to the note + unify its significance legend to no-leading-zero (matches prose + tables)
_old_sig = "are excluded. Significance: $^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$ (two-tailed)."
_new_sig = "are excluded; significant coefficients are shown in \\textbf{bold}. $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed)."
assert _old_sig in _nt, "dwz significance-legend anchor not found"
_nt = _nt.replace(_old_sig, _new_sig)
_dwz.write_text(_nt, encoding="utf-8")
print("patched _dwz_replication.tex: note + bolded %d significant coefs + no-zero legend" % _nb)

# Issue 3: unify the significance legend in the bible tables to no-leading-zero (matches the prose + the
# robustness tables). Note-only -- the legend string can never occur in a data cell. (Sina 2026-06-28.)
_bib = CLONE / "_tables_from_bible.tex"
_bt = _bib.read_text(encoding="utf-8")
_old_leg = "$^{*}p<0.10$, $^{**}p<0.05$, $^{***}p<0.01$"
_new_leg = "$^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$"
_nleg = _bt.count(_old_leg)
assert _nleg == 13, "bible legend: expected 13 occurrences, got %d (drift)" % _nleg
_bib.write_text(_bt.replace(_old_leg, _new_leg), encoding="utf-8")
print("unified %d bible-table legends to no-leading-zero" % _nleg)

# ---- 2. regenerate the standalone body files from phaseB prose ----
(CLONE / "_abstract_body.tex").write_text(prose_of("abstract") + "\n", encoding="utf-8")
(CLONE / "_intro_body.tex").write_text(prose_of("1") + "\n", encoding="utf-8")
(CLONE / "_conclusion_body.tex").write_text(prose_of("5") + "\n", encoding="utf-8")

SEC34 = (
 "% REGENERATED from phaseB_result.json (Phase-5 audited plain-language rewrite). Do not hand-edit.\n"
 "\\chapter{Main Empirical Analyses}\\label{ch:main}\n\n"
 "\\section{Data, Sample, and Variable Construction}\n\n" + prose_of("3.1") + "\n\n"
 "\\section{Main Analysis 1: The Pre-Announcement Run-Up}\n\n" + prose_of("3.2") + "\n\n"
 "\\section{Main Analysis 2: Differential Timing Around the Announcement}\n\n" + prose_of("3.3") + "\n\n"
 "\\section{Main Analysis 3: Cash-Specificity}\n\n" + prose_of("3.4") + "\n\n"
 "\\chapter{Additional Analyses}\\label{ch:additional}\n\n"
 "\\section{Assessing the Analyst-Scrutiny Alternative}\n\n" + prose_of("4.1") + "\n\n"
 "\\section{Outsider Reactions: The Bid-Ask Spread}\n\n" + prose_of("4.2") + "\n\n"
 "\\section{Robustness: Withdrawal as a Resolution Event}\n\n" + prose_of("4.3") + "\n\n"
 "\\section{Robustness: The Cash Result Without the Dynamic Term}\n\n" + prose_of("4.4") + "\n\n"
 "\\section{Robustness: The Main Findings Without the First-Deal Restriction}\n\n" + prose_of("4.5") + "\n")
assert "^{*" not in SEC34, "Issue-2: a significance star survived in the Chapter 3-4 prose"
(CLONE / "sec34_body_from_ledgers.tex").write_text(SEC34, encoding="utf-8")

# ---- 2b. Section-4.5 robustness tables: 4 all-deals comparison tables + 2 logit ----
# Sources: rob_4tables.tex (F1D data tree, the .tex Sina trusts) + logit_tables_final.tex (FE 3-col).
PH3_ROOT = SRC.parents[1]                              # .../Data_Processing/F1D-phase3
F1D_ROOT = Path(str(PH3_ROOT).replace("F1D-phase3", "F1D"))
ROB_SRC = F1D_ROOT / "outputs" / "econometric" / "firstdeal_robustness" / "2026-06-23_162451" / "rob_4tables.tex"
LOGIT_SRC = PH3_ROOT / "tmp" / "logit_tables_final.tex"

def strip_doc(tex):
    s = tex.split(r"\begin{document}", 1)[1].rsplit(r"\end{document}", 1)[0]
    return s.replace(r"\pagestyle{empty}", "").strip()

def fe_row(spec):                                       # one "Firm FE / Year-Qtr FE: Yes" row sized to the table
    return "\\midrule\nFirm FE / Year-Qtr FE & " + " & ".join(["Yes"] * spec.count("c")) + " \\\\\n"

rob = strip_doc(ROB_SRC.read_text(encoding="utf-8", errors="ignore"))
chunks = [c.strip() for c in rob.split(r"\clearpage") if "\\begin{table}" in c]
LABELS = ["tab:rob_runup", "tab:rob_timing_matched", "tab:rob_timing_placebo", "tab:rob_cashspec"]

# Drop the redundant first-deal "Thesis" panels (they duplicate the main tables 5.2-5.5); keep only the
# All-deals columns. Each rob table is [Thesis half | All-deals half]; we keep the second half byte-exact
# and swap in an all-deals-only header. (Sina 2026-06-28.)
ADHEAD = {
 "tab:rob_runup": (8, "lcccccccc",
   " & \\multicolumn{8}{c}{\\textbf{All deals (stacked)}} \\\\\n\\cmidrule(lr){2-9}\n"
   " & \\multicolumn{4}{c}{Cash} & \\multicolumn{4}{c}{Stock} \\\\\n\\cmidrule(lr){2-5}\\cmidrule(lr){6-9}\n"
   " & CshR & UncR & CshSc & HiSc & CshR & UncR & CshSc & HiSc \\\\"),
 "tab:rob_timing_matched": (2, "lcc",
   " & \\multicolumn{2}{c}{\\textbf{All deals (stacked)}} \\\\\n\\cmidrule(lr){2-3}\n & UncRes & CashR \\\\"),
 "tab:rob_timing_placebo": (2, "lcc",
   " & \\multicolumn{2}{c}{\\textbf{All deals (stacked)}} \\\\\n\\cmidrule(lr){2-3}\n & Cash & Stock \\\\"),
 "tab:rob_cashspec": (3, "lccc",
   " & \\multicolumn{3}{c}{\\textbf{All deals (stacked)}} \\\\\n\\cmidrule(lr){2-4}\n & UncRes & CashR(m) & CashR(f) \\\\"),
}
def drop_thesis_panel(c, lab):
    keep, newspec, newhead = ADHEAD[lab]
    c = re.sub(r"\\begin\{tabular\}\{[lc]+\}", "\\\\begin{tabular}{%s}" % newspec, c, count=1)
    c = re.sub(r"\\toprule.*?\\midrule", lambda m: "\\toprule\n" + newhead + "\n\\midrule", c, count=1, flags=re.S)
    c = re.sub(r"\\multicolumn\{\d+\}\{l\}", "\\\\multicolumn{%d}{l}" % (keep + 1), c)   # Controls-panel span
    c = re.sub(r":?\s*Thesis[^}]*?All Deals \(stacked\)\}", " (All Deals, Stacked)}", c)  # caption
    out, in_body = [], False
    for line in c.split("\n"):
        s = line.strip()
        if s == "\\midrule":
            in_body = True; out.append(line); continue
        if "\\bottomrule" in line:
            in_body = False; out.append(line); continue
        if in_body and "&" in line and "multicolumn" not in line and line.rstrip().endswith("\\\\"):
            cells = line.rstrip()[:-2].split("&")
            if len(cells) > keep:
                line = "&".join([cells[0]] + cells[-keep:]) + " \\\\"
        out.append(line)
    return "\n".join(out)

# Issue 3: lift the 4 robustness notes from their terse "legend; SE" form to the bible template
# (what-it-shows -> SE clustered by firm + bold -> legend). FE is shown in each table's own FE row, so the
# note omits an FE clause (per advisor). The WHATs are anchored in the Section 4.5 prose. (Sina 2026-06-28.)
_ROB_LEG = r"Standard errors clustered by firm, in parentheses; significant coefficients in \textbf{bold}. $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed)."
ROB_NOTE = {
 "tab:rob_runup": (
   r"\textit{Notes:} $^{*}p<.10$,$^{**}p<.05$,$^{***}p<.01$ (two-tailed); SE clustered by firm. CshR=CashRatio(+lag), UncR=UncResCEO, CshSc=CashScrutiny, HiSc=HighCashScrutiny.",
   r"\textit{Notes:} All-deals pre-announcement run-up: the first-deal restriction is dropped and every deal a firm makes is stacked. " + _ROB_LEG + r" CshR=CashRatio(+lag), UncR=UncResCEO, CshSc=CashScrutiny, HiSc=HighCashScrutiny."),
 "tab:rob_timing_matched": (
   r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.",
   r"\textit{Notes:} All-deals differential-timing event study on the matched universe. " + _ROB_LEG),
 "tab:rob_timing_placebo": (
   r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.",
   r"\textit{Notes:} All-deals differential-timing event study, split by payment type (cash arm and stock placebo). " + _ROB_LEG),
 "tab:rob_cashspec": (
   r"\textit{Notes:} $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed); SE clustered by firm.",
   r"\textit{Notes:} All-deals pooled cash-specificity test: both treatments enter one regression and the cash-minus-stock difference is evaluated by a Wald restriction. " + _ROB_LEG),
}
def restyle_robnote(c, lab):
    old, new = ROB_NOTE[lab]
    assert old in c, "Issue-3 rob-note anchor not found for %s" % lab
    return c.replace(old, new, 1)

LAND = {0}                                              # only the run-up table (now 8-col) stays landscape
robtex = []
for k, (c, lab) in enumerate(zip(chunks, LABELS)):
    c = c.replace(r"\begin{table}[H]", r"\begin{table}[htbp]")          # float[H] needs a package we don't load
    c = re.sub(r"\\caption\{Table 5\.\d+ --- ", r"\\caption{", c)       # drop the hardcoded "Table 5.x" prefix
    c = drop_thesis_panel(c, lab)                                       # keep only the all-deals columns
    c = restyle_robnote(c, lab)                                         # Issue 3: note -> bible template
    c = re.sub(r"(\\caption\{[^}]*\})", r"\1\\label{%s}" % lab, c, count=1)
    spec = re.search(r"\\begin\{tabular\}\{([lc]+)\}", c).group(1)
    c = c.replace(r"\bottomrule", fe_row(spec) + r"\bottomrule", 1)
    robtex.append(("\\begin{landscape}\n" + c + "\n\\end{landscape}") if k in LAND else c)
logit = strip_doc(LOGIT_SRC.read_text(encoding="utf-8", errors="ignore"))   # already labelled tab:logit_*
# Issue 3: give the two (identical) logit notes a distinct anchored lead + the bold clause, and align the
# SE wording to the bible template. A (tab:logit_dealnext) is first in the source, B second. (Sina 2026-06-28.)
_LOGIT_OLD = r"\textit{Notes:} Col.\ (1) linear probability model; (2) logit (raw log-odds); (3) LPM adding firm and year-quarter fixed effects. A firm-fixed-effects logit is infeasible here (perfect separation: the deal/cash base rate leaves most firms with no within-firm outcome variation). UncResCEO is the residual CEO Q\&A uncertainty; all controls shown; SEs clustered by firm; $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed)."
_LOGIT_TAIL = r"Col.\ (1) linear probability model; (2) logit (raw log-odds); (3) LPM adding firm and year-quarter fixed effects. A firm-fixed-effects logit is infeasible here (perfect separation: the deal/cash base rate leaves most firms with no within-firm outcome variation). All controls shown. Standard errors clustered by firm, in parentheses; significant coefficients in \textbf{bold}. $^{*}p<.10$, $^{**}p<.05$, $^{***}p<.01$ (two-tailed)."
_LOGIT_A = r"\textit{Notes:} Forward specification on all firm-quarters: residual CEO Q\&A uncertainty (UncResCEO) predicting whether a deal of any payment type is announced the next quarter. " + _LOGIT_TAIL
_LOGIT_B = r"\textit{Notes:} Among deals at the pre-announcement quarter: residual CEO Q\&A uncertainty (UncResCEO) predicting whether the deal is cash-financed rather than stock-financed. " + _LOGIT_TAIL
assert logit.count(_LOGIT_OLD) == 2, "Issue-3 logit-note: expected 2 identical notes, got %d" % logit.count(_LOGIT_OLD)
logit = logit.replace(_LOGIT_OLD, _LOGIT_A, 1)
logit = logit.replace(_LOGIT_OLD, _LOGIT_B, 1)
robblock = ("% Section 4.5 robustness tables -- 4 all-deals comparison tables + 2 logit (FE 3-col).\n"
            "% Wired from rob_4tables.tex + logit_tables_final.tex; FE row added per the robustness resume.\n"
            + "\n\n\\clearpage\n\n".join(robtex) + "\n\n\\clearpage\n\n" + logit + "\n")
(CLONE / "_robustness_tables.tex").write_text(robblock, encoding="utf-8")
print("wrote _robustness_tables.tex: %d all-deals tables + 2 logit" % len(robtex))

# ---- 3. splice the inline Chapter-2 (sections 2.1-2.5) into the cloned wrapper ----
SEC2 = (
 "\n\n\\section{Conceptual Framework}\n\n" + prose_of("2.1") + "\n\n"
 "\\section{Hypothesis Development}\n\n" + prose_of("2.2") + "\n\n"
 "\\section{Estimation of the Main Variable}\n\n" + prose_of("2.3") + "\n\n"
 "\\section{Methodology and Empirical Design}\n\n" + prose_of("2.4") + "\n\n"
 "\\section{Specification and Measurement of Key Constructs}\n\n" + prose_of("2.5") + "\n\n")
assert "^{*" not in SEC2, "Issue-2: a significance star survived in the Chapter 2 prose"

NEW_BIBS = "\n\n".join([
 "\\bibitem[Bates et~al.(2009)]{bates2009}\nBates, T.~W., K.~M. Kahle, and R.~M. Stulz. 2009. Why do U.S.\\ firms hold so much more cash than they used to? \\emph{The Journal of Finance} 64: 1985--2021.",
 "\\bibitem[Louis(2004)]{louis2004}\nLouis, H. 2004. Earnings management and the market performance of acquiring firms. \\emph{Journal of Financial Economics} 74: 121--148.",
 "\\bibitem[Opler et~al.(1999)]{opler1999}\nOpler, T., L.~Pinkowitz, R.~Stulz, and R.~Williamson. 1999. The determinants and implications of corporate cash holdings. \\emph{Journal of Financial Economics} 52: 3--46.",
 "\\bibitem[Pagan(1984)]{pagan1984}\nPagan, A. 1984. Econometric issues in the analysis of regressions with generated regressors. \\emph{International Economic Review} 25: 221--247.",
 "\\bibitem[Shleifer and Vishny(2003)]{shleifer_vishny2003}\nShleifer, A., and R.~Vishny. 2003. Stock market driven acquisitions. \\emph{Journal of Financial Economics} 70: 295--311.",
])

wrap = (CLONE / "thesis_draft_uottawa.tex").read_text(encoding="utf-8")
HEAD = r"\chapter{Conceptual Framework and Empirical Strategy}\label{sec:framework}"
TAIL = "% Section 3 + Section 4 body prose"
BIBEND = r"\end{thebibliography}"
assert HEAD in wrap and TAIL in wrap and BIBEND in wrap, "wrapper anchors not found"
i = wrap.index(HEAD) + len(HEAD)
j = wrap.index(TAIL)
tail = wrap[j:].replace(BIBEND, NEW_BIBS + "\n\n" + BIBEND, 1)
tail = tail.replace(r"\input{_tables_from_bible.tex}",
                    "\\input{_tables_from_bible.tex}\n\n\\clearpage\n% Section 4.5 robustness tables (all-deals + logit)\n\\input{_robustness_tables.tex}", 1)
assert "_robustness_tables.tex" in tail, "robustness \\input not wired into wrapper"
wrap_new = wrap[:i] + SEC2 + tail
(CLONE / "thesis_draft_uottawa.tex").write_text(wrap_new, encoding="utf-8")
print("spliced Chapter-2 + added 5 bibitems; wrapper now %d chars" % len(wrap_new))

# ---- 4. compile (pdflatex x3 for TOC / List of Tables / refs; manual bib, no bibtex) ----
# Use a distinct -jobname so a viewer holding thesis_draft_uottawa.pdf open never blocks the write.
JOB = "thesis_draft_uottawa"
ok = True
for p in range(3):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-jobname", JOB, "thesis_draft_uottawa.tex"],
                       cwd=CLONE, capture_output=True, text=True)
    if r.returncode != 0: ok = False
pdf = CLONE / (JOB + ".pdf")
log = (CLONE / (JOB + ".log")).read_text(encoding="utf-8", errors="ignore") if (CLONE/(JOB+".log")).exists() else r.stdout
if pdf.exists():
    pages = re.search(JOB + r"\.pdf \((\d+) page", log)
    undef = len(re.findall(r"Citation .* undefined|Reference .* undefined|LaTeX Warning: Reference", log))
    overfull = len(re.findall(r"Overfull \\hbox", log))
    print("PDF OK: pages=%s  undefined-ref/cite=%d  overfull-hbox=%d" %
          (pages.group(1) if pages else "?", undef, overfull))
else:
    print("PDF FAILED. Last 30 log lines:")
    print("\n".join(log.splitlines()[-30:]))
sys.exit(0 if pdf.exists() else 1)
