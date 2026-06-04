"""
Append Round 2 (IA Appendix E.1) paragraph-level lock-in to
tmp/campello_method_lockin.md.

Resolution:
- 2 paragraphs in IA E.1 per Claude-web + PyMuPDF anchor (matched character-for-character)
- NLM split into 4 paragraphs (over-split — same pattern as Round 1b §IV.A.1 / §IV.C.2)
- Content agreement 3/3 on the PROSE (NLM's prose matches anchor; only chunking differs)
- Verbatim taken from PyMuPDF anchor (cleanest, no LaTeX subscripts vs Unicode subscript disagreement)
"""
import re
from pathlib import Path

ANCHOR_FILE = Path("tmp/campello_pdf_extract/full_supp_pdfpage16.txt")
LOCKIN_FILE = Path("tmp/campello_method_lockin.md")

# Read anchor and extract the 2 IA E.1 body paragraphs (PyMuPDF default text mode)
anchor_text = ANCHOR_FILE.read_text(encoding="utf-8")
# Skip header (first 3 lines)
body = "\n".join(anchor_text.splitlines()[3:])
# Collapse single-line wraps within paragraphs: lines that are continuation
# should join with single space. Identify paragraph breaks by blank lines, or
# by the structural markers we know (line starting with "With" after period).
# Simplest: known boundaries
para1_start_marker = "For more details on the geographic measure"
para2_start_marker = "With the textbook in hand"
para2_end_marker = "AUTOMATIONi variable."

# Find exact positions
i1 = body.find(para1_start_marker)
i2 = body.find(para2_start_marker)
iend = body.find(para2_end_marker)
assert i1 >= 0 and i2 >= 0 and iend >= 0, "anchor markers not found"

# Para 1: from para1_start to just before para2_start
para1_raw = body[i1:i2].strip()
# Para 2: from para2_start to end of "...AUTOMATIONi variable."
para2_raw = body[i2:iend + len(para2_end_marker)].strip()

def collapse(s):
    """Join broken lines into single space, preserve text."""
    return re.sub(r"\s+", " ", s).strip()

para1 = collapse(para1_raw)
para2 = collapse(para2_raw)

# Append to lock-in
existing = LOCKIN_FILE.read_text(encoding="utf-8")
existing = re.sub(r"\n## Round 2 — still pending.*?(?=\n## |\Z)", "", existing, flags=re.DOTALL)
existing = re.sub(r"\n## Round 2 — IA Appendix E.*?(?=\n## |\Z)", "", existing, flags=re.DOTALL)

lines = [
    "",
    "## Round 2 — IA Appendix E.1 (Automation construction) lock-in (added 2026-05-26)",
    "",
    "**Source**: `docs/papers/campello_etal_2022_brexit_supplementary.pdf` page 16 — Appendix E, sub-subsection E.1 \"Details on Automation Exposure Measures\".",
    "",
    "**Cross-check summary**:",
    "- NLM returned 4 paragraphs (over-split into individual sentences — same NLM off-by-N pattern as Round 1b §IV.A.1 and §IV.C.2)",
    "- Claude-web returned 2 paragraphs (matches anchor)",
    "- PyMuPDF anchor (line-by-line read of supp_pdfpage16.txt) confirms **2 body paragraphs** in E.1",
    "- Content prose: 3/3 sources agree character-for-character (only chunking differs)",
    "",
    "**Resolution**: Claude-web's 2-paragraph structure adopted; verbatim text below taken from PyMuPDF anchor (cleanest source — preserves AUTOMATION_i subscript as inline `AUTOMATIONi`).",
    "",
    "**Status**: `LOCKED` (3/3 content agreement, anchor-confirmed paragraph structure).",
    "",
    "### IA_E_PARA_01 — E.1 ¶1  (supp pdf page 16)",
    "**First word**: \"For\"   |   **Last word**: \"universities.\"",
    "**Contains equation**: no   |   **References**: Acemoglu and Restrepo (2020), Leigh and Kraft (2018), Loughran and McDonald (2011), Benhabib (2003)",
    "",
    "**Verbatim** (from PyMuPDF anchor, supp p16):",
    "",
    "> " + para1,
    "",
    "### IA_E_PARA_02 — E.1 ¶2  (supp pdf page 16)",
    "**First word**: \"With\"   |   **Last word**: \"variable.\"",
    "**Contains equation**: yes (`AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi)`)   |   **References**: Mihalcea and Tarau (2004)",
    "",
    "**Verbatim** (from PyMuPDF anchor, supp p16):",
    "",
    "> " + para2,
    "",
    "## Methodology lock-in — COMPLETE for the Hybrid scope",
    "Round 1 (47 sentence-level §IV steps) + Round 1b (9 paragraph-level §IV locks) + Round 2 (2 paragraph-level IA E.1 locks) covers the full scope decided 2026-05-26.",
    "",
    "**Next phase candidates** (Sina decides):",
    "1. **Variables checklist** — enumerate every variable definition in the paper verbatim (separate per Sina earlier directive: \"we will make a checklist of ALL variables and their verbatim definition, later\")",
    "2. **Code audit** — compare `scripts/campello_rebuild/` against this locked methodology to identify code bugs",
    "3. **Sample-construction filters** — also explicitly inside this scope decision (\"ONLY the method\"); some are in §IV.B but not isolated as steps",
    "",
]

LOCKIN_FILE.write_text(existing + "\n".join(lines), encoding="utf-8")
print(f"Appended Round 2 to {LOCKIN_FILE}")
print(f"Para 1 length: {len(para1)} chars")
print(f"Para 2 length: {len(para2)} chars")
