"""
Append Round 1b paragraph-level lock-in to tmp/campello_method_lockin.md.

Resolutions:
- 6 LOCKED paragraphs (both AIs returned same anchor): use Claude-web verbatim (cleaner Unicode equations)
- 2 DRIFT resolved by Sina visual PDF verification on 2026-05-26: both go to Claude-web (NLM off-by-one paragraph numbering)
- 1 CW_ONLY (PARA_01): NLM returned INCOMPLETE; use Claude-web verbatim

All 9 paragraphs lock to Claude-web's verbatim. NLM's content was either truncated, mojibake, or wrongly numbered.
"""
import re
import unicodedata
from pathlib import Path

PROMPT_FILE = Path("tmp/process_prompt_01b_paragraph_reverify_2026_05_26.md")
LOCKIN_FILE = Path("tmp/campello_method_lockin.md")

PARA_RE = re.compile(
    r"PARA_(\d+):\s*\n(.*?)(?=\nPARA_\d+:|\nTOTAL_PARAGRAPHS|\n/{3,}|\Z)",
    re.DOTALL,
)

def parse_para_blocks(section_text):
    blocks = []
    for m in PARA_RE.finditer(section_text):
        no = int(m.group(1))
        body = m.group(2)
        fw = re.search(r"first_word_verbatim:\s*\"([^\"]*)\"", body)
        lw = re.search(r"last_word_verbatim:\s*\"([^\"]*)\"", body)
        section = re.search(r"section:\s*(.+?)\s*\n", body)
        ppos = re.search(r"paragraph_position:\s*(\d+)", body)
        page = re.search(r"page:\s*(.+?)\s*\n", body)
        ptext = re.search(
            r"paragraph_text_verbatim:\s*\|\s*\n(.*?)(?=\n\s*contains_equation:|\n\s*contains_footnote_anchor:|\Z)",
            body, re.DOTALL
        )
        blocks.append({
            "para_no": no,
            "section": section.group(1).strip() if section else "",
            "para_position": int(ppos.group(1)) if ppos else 0,
            "page": page.group(1).strip() if page else "",
            "first_word": fw.group(1) if fw else "",
            "last_word": lw.group(1) if lw else "",
            "paragraph_text": (ptext.group(1).strip() if ptext else "").strip(),
        })
    return blocks

text = PROMPT_FILE.read_text(encoding="utf-8")
chunks = re.split(r"/{5,}\s*\n", text)
nlm_text = cw_text = ""
for i, c in enumerate(chunks):
    s = c.strip()
    if s == "NLM" and i + 1 < len(chunks):
        nlm_text = chunks[i + 1]
    elif re.match(r"^Claude\s*web\s*$", s, re.IGNORECASE) and i + 1 < len(chunks):
        cw_text = chunks[i + 1]
nlm = parse_para_blocks(nlm_text)
cw = parse_para_blocks(cw_text)

# Round 1b resolution per cross-check + Sina PDF verification 2026-05-26
RESOLUTIONS = {
    1: {"status": "CW_ONLY (NLM INCOMPLETE)", "source": "Claude-web",
        "note": "NLM could not transcribe equation (11) due to mojibake. Claude-web returned clean Unicode."},
    2: {"status": "LOCKED-BY-ANCHOR (NLM off-by-one)", "source": "Claude-web",
        "note": "NLM PARA_02 = 'Following Bloom...' but anchor §IV.A.1 ¶2 starts at 'We can employ...'. Claude-web matches anchor (a[7])."},
    3: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs map to anchor a[10]. Claude-web gave the full paragraph; NLM gave only its last sentence."},
    4: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs identical content (anchor a[11])."},
    5: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs identical content (anchor a[14], cross-page p3192→3193)."},
    6: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs identical content (anchor a[15]). Claude-web includes more sentences (NLM truncated)."},
    7: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs identical content (anchor a[16]). Claude-web includes more sentences."},
    8: {"status": "LOCKED-BY-PDF-CHECK (NLM off-by-one)", "source": "Claude-web",
        "note": "Sina visually verified page 3194 contains exactly 2 body paragraphs: 'The first (dotted blue)...' (¶2) and 'Responses to official news...' (¶3). NLM's 'Having examined market uncertainty...' is on p3195 = ¶4, NOT ¶3."},
    9: {"status": "LOCKED",      "source": "Claude-web",
        "note": "Both AIs map to anchor a[24]. Claude-web gave eq (14) cleanly."},
}

# Map Round 1 STEP_NN -> Round 1b PARA_NN based on the original taxonomy
STEPS_IN_PARA = {
    1: [],
    2: [1, 2, 3, 4],
    3: [5],
    4: [8],
    5: [18, 19, 20, 21, 22],
    6: [23, 24, 25, 26, 27],
    7: [28, 29, 30, 31, 32],
    8: [34, 35],
    9: [38, 39, 40, 41, 42, 43, 44],
}

# Append Round 1b section to existing lock-in file
existing = LOCKIN_FILE.read_text(encoding="utf-8")
# Strip any prior Round 1b section to keep idempotent
existing = re.sub(r"\n## Round 1b.*?(?=\n## |\Z)", "", existing, flags=re.DOTALL)

lines = [
    "",
    "## Round 1b — Paragraph-level lock-in (added 2026-05-26)",
    "",
    "**Why Round 1b**: Round 1 sentence-level extraction left 11 EQUATION + 2 PAPER_OK steps with ugly verbatim. Round 1b re-queried both AIs at paragraph level for the 9 paragraphs containing those problem steps. Then Sina visually verified page 3194 in the PDF to resolve the §IV.C.2 paragraph-numbering drift.",
    "",
    "**Cross-check artifact**: `tmp/campello_para_crosscheck_v1_2026_05_26.md`",
    "**Anchor enumeration**: `tmp/campello_paragraph_index_2026_05_26.md`",
    "",
    "**Resolution rule**: when NLM and Claude-web disagree on `paragraph_position` for the same section, the anchor (PyMuPDF `blocks` mode + Sina PDF visual verification) settles it. In this round, **all disagreements resolved in Claude-web's favor**; NLM had off-by-one paragraph-numbering errors in §IV.A.1 and §IV.C.2.",
    "",
    "**Final result**: 9/9 paragraphs locked to Claude-web's verbatim text.",
    "",
]
for i in range(1, 10):
    cw_p = next((p for p in cw if p["para_no"] == i), None)
    if not cw_p:
        continue
    res = RESOLUTIONS[i]
    steps = STEPS_IN_PARA.get(i, [])
    steps_str = ", ".join(f"STEP_{s:02d}" for s in steps) if steps else "—"
    lines.append(f"### PARA_{i:02d} — §{cw_p['section']} ¶{cw_p['para_position']}  (printed pg {cw_p['page']})")
    lines.append(f"**Status**: `{res['status']}`   |   **Source**: {res['source']}")
    lines.append(f"**Round 1 STEPs contained in this paragraph**: {steps_str}")
    lines.append(f"**Note**: {res['note']}")
    lines.append("")
    lines.append("**Verbatim** (from Claude-web, with Unicode equation glyphs):")
    lines.append("")
    # Indent the paragraph as a blockquote
    for line in cw_p["paragraph_text"].splitlines():
        lines.append("> " + line)
    lines.append("")

lines += [
    "## Round 2 — still pending",
    "- IA Appendix E (Automation construction, supp pp 15-16) — needs NLM corpus to load supplementary PDF before 3-AI cross-check, OR proceed with 2-AI (Claude-web + anchor only).",
    "",
]

LOCKIN_FILE.write_text(existing + "\n".join(lines), encoding="utf-8")
print(f"Appended Round 1b to {LOCKIN_FILE}")
print(f"Final size: {len(LOCKIN_FILE.read_text(encoding='utf-8').splitlines())} lines")
