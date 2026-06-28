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
    return t

def prose_of(sid):
    body = "\n\n".join(normalize(p["final_prose"].strip()) for p in SEC[sid]["paragraphs"])
    return repoint_45(body) if sid == "4.5" else body

# ---- 1. clone every .tex in docs/Thesis so all \input deps resolve; originals untouched ----
CLONE.mkdir(exist_ok=True)
for f in SRC.glob("*.tex"):
    shutil.copy(f, CLONE / f.name)
print("cloned %d .tex files -> %s" % (len(list(CLONE.glob('*.tex'))), CLONE.name))

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
 "\\section{Ruling Out Analyst Scrutiny}\n\n" + prose_of("4.1") + "\n\n"
 "\\section{Outsider Reactions: The Bid-Ask Spread}\n\n" + prose_of("4.2") + "\n\n"
 "\\section{Robustness: Withdrawal as a Resolution Event}\n\n" + prose_of("4.3") + "\n\n"
 "\\section{Robustness: The Cash Result Without the Dynamic Term}\n\n" + prose_of("4.4") + "\n\n"
 "\\section{Robustness: The Main Findings Without the First-Deal Restriction}\n\n" + prose_of("4.5") + "\n")
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
LAND = {0, 3}                                           # the wide run-up (16-col) + cash-spec (6-col) go landscape
robtex = []
for k, (c, lab) in enumerate(zip(chunks, LABELS)):
    c = c.replace(r"\begin{table}[H]", r"\begin{table}[htbp]")          # float[H] needs a package we don't load
    c = re.sub(r"\\caption\{Table 5\.\d+ --- ", r"\\caption{", c)       # drop the hardcoded "Table 5.x" prefix
    c = re.sub(r"(\\caption\{[^}]*\})", r"\1\\label{%s}" % lab, c, count=1)
    spec = re.search(r"\\begin\{tabular\}\{([lc]+)\}", c).group(1)
    c = c.replace(r"\bottomrule", fe_row(spec) + r"\bottomrule", 1)
    robtex.append(("\\begin{landscape}\n" + c + "\n\\end{landscape}") if k in LAND else c)
logit = strip_doc(LOGIT_SRC.read_text(encoding="utf-8", errors="ignore"))   # already labelled tab:logit_*
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
JOB = "thesis_uottawa_rev"
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
