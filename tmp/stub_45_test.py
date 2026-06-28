# -*- coding: utf-8 -*-
"""Plumbing test for the §4.5 path: insert a STUB §4.5 results subsection (3 paras with the
section's real cite keys + a Table ref) + the 2 new bibitems into a COPY of thesis_draft.tex,
so we prove the insertion point + new-citation resolution compile BEFORE any agent writes real prose.
No agents. No touch to the real thesis."""
import re, shutil
from pathlib import Path
THESIS = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\thesis_draft.tex")
SCRATCH = Path(r"C:\Users\sinas\AppData\Local\Temp\claude\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\e514389f-0c61-4e93-9f33-08043f70a4c0\scratchpad")
STUB = SCRATCH / "thesis_stub45.tex"

tex = THESIS.read_text(encoding="utf-8")

# stub §4.5 results subsection — 3 paragraphs, exercising: existing cite (harford1999),
# the 2 NEW cite keys §4.5 needs (shleifer_vishny2003, louis2004), a Table reference, math, emphasis.
STUB_BODY = r"""
\subsection{Robustness: The Main Findings Without the First-Deal Restriction}
\label{subsec:robustness_alldeals}

PLACEHOLDER run-up paragraph. The pre-announcement run-up survives on the all-deals-stacked
panel of Table~5.2 (cash $0.0391^{***}$, stock $-0.0348$, n.s.), echoing \citet{harford1999}.
That is, the result is not an artifact of the first-deal restriction.

PLACEHOLDER timing paragraph. The differential-timing round-trip holds across all deals, with
the cash arm spiking and unwinding while the stock arm stays flat \citep{shleifer_vishny2003}.

PLACEHOLDER cash-concentration paragraph. The formal cash-minus-stock Wald difference is
$0.1056^{**}$, consistent with the valuation channel \citep{louis2004}; the proposed cause
remains insignificant, so the mechanism stays open.
"""

# 2 new bibitems §4.5 needs (stub text is fine for a COMPILE test — real text comes later).
NEW_BIBS = r"""\bibitem[Shleifer and Vishny(2003)]{shleifer_vishny2003}
Shleifer, A., and R.~Vishny. 2003. Stock market driven acquisitions. \emph{Journal of Financial Economics} 70: 295--311.

\bibitem[Louis(2004)]{louis2004}
Louis, H. 2004. Earnings management and the market performance of acquiring firms. \emph{Journal of Financial Economics} 74: 121--148.

"""

# insert subsection just before the bibliography; bibitems just before its end
BIB_START = r"\begin{thebibliography}"
BIB_END = r"\end{thebibliography}"
assert tex.count(BIB_START) == 1, f"BIB_START count={tex.count(BIB_START)}"
assert tex.count(BIB_END) == 1, f"BIB_END count={tex.count(BIB_END)}"

i = tex.index(BIB_START)
new = tex[:i] + STUB_BODY + "\n" + tex[i:]
# add new bibitems (only if key absent)
defined = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", new))
for key, entry in [("shleifer_vishny2003", NEW_BIBS)]:
    pass
add = ""
for entry in re.split(r"\n(?=\\bibitem)", NEW_BIBS.strip()):
    key = re.search(r"\{([^}]*)\}", entry).group(1)
    if key not in defined:
        add += entry.strip() + "\n\n"
if add:
    j = new.index(BIB_END)
    new = new[:j] + add + new[j:]

STUB.write_text(new, encoding="utf-8")

# verify every cite key in the stub body resolves
used = set(re.findall(r"\\cite[tp]\{([^}]*)\}", STUB_BODY))
defined2 = set(re.findall(r"\\bibitem(?:\[[^\]]*\])?\{([^}]*)\}", new))
missing = used - defined2
print("stub §4.5 cite keys:", sorted(used))
print("all resolve to bibitems:", not missing, "| missing:", sorted(missing))
print("wrote", STUB.name)
