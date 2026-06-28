# Assemble the final audited prose (phaseB_result.json) into a compiling LaTeX PDF.
# v2 fixes: (1) real section titles from phaseB_data.json; (2) real regression tables
# from _tables_from_bible.tex (byte-exact); (3) inline-math control lists allowed to
# break so they stop overrunning the margin; (4) natbib author-year citations (the
# bibitems are already [Author(Year)]-formatted) instead of bracketed numbers; (5) the
# duplicate dwz/dwz2021 bibitem collapsed to one. Bibliography is still manual; any cite
# key without a known bibitem gets a stub so the doc never aborts.
import json, re, subprocess, sys, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
PH3 = H.parents[2]                      # .../F1D-phase3/docs
F1D = Path(str(PH3).replace("F1D-phase3", "F1D"))   # sibling tree holding the real tables
RES = json.load(open(H / "phaseB_result.json", encoding="utf-8"))
DAT = json.load(open(H / "phaseB_data.json", encoding="utf-8"))
SEC = {s["section"]: s for s in RES["sections"]}
prose_of = lambda sid: "\n\n".join(p["final_prose"].strip() for p in SEC[sid]["paragraphs"])

# ---- real section titles (phaseB_data carries them; strip the parenthetical descriptors) ----
TITLE = {s["section"]: (s.get("title") or s["section"]).split(" (")[0].strip() for s in DAT}
title_of = lambda sid: TITLE.get(sid, sid)

# ---- document structure (parents are header-only; numbering -> 1, 2, 2.1.., 3, 3.1.., 4, 4.1.., 5) ----
BODY = []
BODY.append("\\section*{Abstract}\n\n" + prose_of("abstract"))
BODY.append("\\section{" + title_of("1") + "}\n\n" + prose_of("1"))
BODY.append("\\section{Theoretical Framework and Hypothesis Development}")
for s in ["2.1", "2.2", "2.3", "2.4", "2.5"]:
    BODY.append("\\subsection{" + title_of(s) + "}\n\n" + prose_of(s))
BODY.append("\\section{Data and Main Results}")
for s in ["3.1", "3.2", "3.3", "3.4"]:
    BODY.append("\\subsection{" + title_of(s) + "}\n\n" + prose_of(s))
BODY.append("\\section{Additional Analyses and Robustness}")
for s in ["4.1", "4.2", "4.3", "4.4", "4.5"]:
    BODY.append("\\subsection{" + title_of(s) + "}\n\n" + prose_of(s))
BODY.append("\\section{" + title_of("5") + "}\n\n" + prose_of("5"))
body = "\n\n".join(BODY)

# ---- body fixes that change no meaning ----
body = body.replace("{dwz2021}", "{dwz}")                       # collapse the duplicate citation key
body = re.sub(r"\},\s*\\mathit\{", r"},\\allowbreak \\mathit{", body)   # let long $\{..\}$ lists wrap
# spell out the bare DWZ/BGT acronyms as proper citations (bare uppercase initials are non-standard).
# possessive -> \citeauthor ("Dzielinski et al.'s"); plain -> \citet ("Dzielinski et al. (2021)").
body = re.sub(r"\bDWZ's\b", r"\\citeauthor{dwz}'s", body)
body = re.sub(r"\bBGT's\b", r"\\citeauthor{bgt2018}'s", body)
body = re.sub(r"\bDWZ\b", r"\\citet{dwz}", body)
body = re.sub(r"\bBGT\b", r"\\citet{bgt2018}", body)

# ---- collect cite keys + table labels actually used (from the assembled body) ----
cites = set(); labels = set()
for g in re.findall(r"\\cite[tp]\{([^}]*)\}", body): cites |= {k.strip() for k in g.split(",")}
labels |= set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", body))

# ---- real tables: byte-exact chunks from the bible, split on the '% --- tab:LABEL' delimiters ----
BIB_TABLES = F1D / "Thesis" / "_tables_from_bible.tex"
btxt = BIB_TABLES.read_text(encoding="utf-8", errors="ignore")
order = re.findall(r"(?m)^% --- tab:(\S+)", btxt)                # 14 labels in document order
parts = re.split(r"(?m)^% --- tab:\S+.*$", btxt)[1:]            # body chunks after each delimiter
tbl = {lab: parts[i].strip() for i, lab in enumerate(order)}
missing = sorted(l for l in labels if l.replace("tab:", "") not in tbl)
if missing:
    print("[FAIL] referenced tables with no bible source: %s" % missing); sys.exit(1)
tables = "\n\n\\clearpage\n\n".join(tbl[l] for l in order)      # all 14, in bible order, at the end

# ---- bibitems: gather known, stub the rest ----
known = {}
def grab(path):
    try: txt = Path(path).read_text(encoding="utf-8", errors="ignore")
    except Exception: return
    for block in re.split(r"\n\s*\n", txt):          # blank-line-separated entries
        bi = block.find("\\bibitem")
        if bi < 0: continue
        block = block[bi:].strip()                   # drop any 'BIBS = r\"\"\"' prefix
        if "json." in block or "def " in block: continue          # reject python contamination
        m = re.match(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", block)
        if m: known.setdefault(m.group(1), block)
grab(H / "../push_2_1_to_tex.py"); grab(PH3 / "Thesis" / "_bibitems_supplement.tex")
KNOWN_EXTRA = {
 "shleifer_vishny2003": "\\bibitem[Shleifer and Vishny(2003)]{shleifer_vishny2003}\nShleifer, A., and R.~Vishny. 2003. Stock market driven acquisitions. \\emph{Journal of Financial Economics} 70: 295--311.",
 "louis2004": "\\bibitem[Louis(2004)]{louis2004}\nLouis, H. 2004. Earnings management and the market performance of acquiring firms. \\emph{Journal of Financial Economics} 74: 121--148.",
 "bgt2018": "\\bibitem[Bushee et~al.(2018)]{bgt2018}\nBushee, B.~J., I.~D. Gow, and D.~J. Taylor. 2018. Linguistic complexity in firm disclosures: Obfuscation or information? \\emph{Journal of Accounting Research} 56: 85--121. % VERIFY vol/pages",
}
for k, v in KNOWN_EXTRA.items(): known.setdefault(k, v)
bibitems = []; stubbed = []
for k in sorted(cites):
    if k in known: bibitems.append(known[k])
    else:
        stubbed.append(k)
        nm = k.replace("_", " ").title()
        bibitems.append("\\bibitem[%s(2024)]{%s}\n%s. [reference details to be completed]." % (nm, k, nm))
bibliography = "\\begin{thebibliography}{99}\n\n" + "\n\n".join(bibitems) + "\n\n\\end{thebibliography}"

DOC = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage{booktabs}
\usepackage{longtable}
\usepackage{array}
\usepackage{adjustbox}
\usepackage{pdflscape}
\usepackage[round,authoryear]{natbib}
\usepackage[hidelinks]{hyperref}
\usepackage{setspace}\onehalfspacing
\setlength{\emergencystretch}{3em}
\title{CEO Question-and-Answer Uncertainty and the Anticipation of Cash Acquisitions}
\author{}\date{}
\begin{document}
\maketitle
""" + body + "\n\n\\clearpage\n" + tables + "\n\n" + bibliography + "\n\\end{document}\n"

OUT = H / "final_thesis.tex"
OUT.write_text(DOC, encoding="utf-8")
print("wrote %s  (%d chars)" % (OUT.name, len(DOC)))
print("cites used: %d | stubbed (no bibitem): %s" % (len(cites), stubbed))
print("table labels referenced: %d | tables emitted: %d" % (len(labels), len(order)))

# ---- compile in a temp build dir (pdflatex x2 for refs) ----
BD = H / "_pdfbuild"; BD.mkdir(exist_ok=True)
shutil.copy(OUT, BD / "final_thesis.tex")
ok = True
for i in (1, 2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "final_thesis.tex"],
                       cwd=BD, capture_output=True, text=True)
    if r.returncode != 0: ok = False
pdf = BD / "final_thesis.pdf"
log = (BD / "final_thesis.log").read_text(encoding="utf-8", errors="ignore") if (BD/"final_thesis.log").exists() else r.stdout
if pdf.exists():
    pages = re.search(r"Output written on final_thesis\.pdf \((\d+) page", log)
    undef = len(re.findall(r"Citation .* undefined|Reference .* undefined|LaTeX Warning: Reference", log))
    overfull = len(re.findall(r"Overfull \\hbox", log))
    print("PDF OK: pages=%s  undefined-ref/cite=%d  overfull-hbox=%d" %
          (pages.group(1) if pages else "?", undef, overfull))
    for dest in ("final_thesis.pdf", "final_thesis_v2.pdf"):
        try: shutil.copy(pdf, H / dest); print("copied -> %s" % dest)
        except PermissionError: print("LOCKED (open in viewer), skipped -> %s" % dest)
else:
    print("PDF FAILED. Last 30 log lines:")
    print("\n".join(log.splitlines()[-30:]))
sys.exit(0 if pdf.exists() else 1)
