# Assemble the final audited prose (phaseB_result.json) into a self-contained, compiling LaTeX PDF.
# Numbering matches the prose's hardcoded "Section 2.4" refs via \section/\subsection nesting.
# Table \ref's resolve via lightweight placeholder floats (real floats can replace later).
# Bibliography is manual; any cite key without a known bibitem gets a stub so the doc never aborts.
import json, re, subprocess, sys, shutil
from pathlib import Path

H = Path(__file__).resolve().parent
PH3 = H.parents[2]                      # .../F1D-phase3/docs
RES = json.load(open(H / "phaseB_result.json", encoding="utf-8"))
SEC = {s["section"]: s for s in RES["sections"]}
prose_of = lambda sid: "\n\n".join(p["final_prose"].strip() for p in SEC[sid]["paragraphs"])
title_of = lambda sid: (SEC[sid].get("title") or sid)

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

# ---- collect cite keys + table labels actually used ----
cites = set(); labels = set()
for s in RES["sections"]:
    for p in s["paragraphs"]:
        t = p["final_prose"]
        for g in re.findall(r"\\cite[tp]\{([^}]*)\}", t): cites |= {k.strip() for k in g.split(",")}
        labels |= set(re.findall(r"\\ref\{(tab:[A-Za-z0-9_]+)\}", t))

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
}
for k, v in KNOWN_EXTRA.items(): known.setdefault(k, v)
bibitems = []; stubbed = []
for k in sorted(cites):
    if k in known: bibitems.append(known[k])
    else:
        stubbed.append(k)
        nm = k.replace("_", " ").title()
        bibitems.append("\\bibitem[%s]{%s}\n%s. [reference details to be completed]." % (nm, k, nm))
bibliography = "\\begin{thebibliography}{99}\n\n" + "\n\n".join(bibitems) + "\n\n\\end{thebibliography}"

# ---- placeholder table floats so every \ref{tab:...} resolves to a number ----
tables = "\n\n".join(
    "\\begin{table}[htbp]\\centering\\caption{%s}\\label{%s}\\textit{[table content]}\\end{table}" %
    (lab.replace("tab:", "").replace("_", " ").title(), lab) for lab in sorted(labels))

DOC = r"""\documentclass[11pt]{article}
\usepackage[margin=1in]{geometry}
\usepackage{amsmath,amssymb}
\usepackage[hidelinks]{hyperref}
\providecommand{\citep}[1]{\cite{#1}}
\providecommand{\citet}[1]{\cite{#1}}
\usepackage{setspace}\onehalfspacing
\title{CEO Question-and-Answer Uncertainty and the Anticipation of Cash Acquisitions}
\author{}\date{}
\begin{document}
\maketitle
""" + body + "\n\n\\clearpage\n" + tables + "\n\n" + bibliography + "\n\\end{document}\n"

OUT = H / "final_thesis.tex"
OUT.write_text(DOC, encoding="utf-8")
print("wrote %s  (%d chars)" % (OUT.name, len(DOC)))
print("cites used: %d | stubbed (no bibitem): %s" % (len(cites), stubbed))
print("table labels: %d" % len(labels))

# ---- compile in a temp build dir (pdflatex x2 for refs) ----
BD = H / "_pdfbuild"; BD.mkdir(exist_ok=True)
shutil.copy(OUT, BD / "final_thesis.tex")
ok = True
for i in (1, 2):
    r = subprocess.run(["pdflatex", "-interaction=nonstopmode", "-halt-on-error", "final_thesis.tex"],
                       cwd=BD, capture_output=True, text=True)
    if r.returncode != 0: ok = False
pdf = BD / "final_thesis.pdf"
if pdf.exists():
    # page count from the log
    log = (BD / "final_thesis.log").read_text(encoding="utf-8", errors="ignore")
    pages = re.search(r"Output written on final_thesis\.pdf \((\d+) page", log)
    undef = len(re.findall(r"Citation .* undefined|reference .* undefined|LaTeX Warning: Reference", log))
    print("PDF OK: %s  pages=%s  undefined-ref/cite warnings=%d" % (pdf, pages.group(1) if pages else "?", undef))
else:
    print("PDF FAILED. Last 25 log lines:")
    log = (BD / "final_thesis.log").read_text(encoding="utf-8", errors="ignore") if (BD/"final_thesis.log").exists() else r.stdout
    print("\n".join(log.splitlines()[-25:]))
sys.exit(0 if pdf.exists() else 1)
