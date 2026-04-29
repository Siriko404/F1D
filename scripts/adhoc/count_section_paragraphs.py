"""
Phase 0 — paragraph-count verification per content section.
Splits each section file by \subsection / \subsubsection and counts text blocks per subsection.
Block = text between blank lines, excluding pure comment lines and excluding LaTeX env markers.
"""
import re
from pathlib import Path

FILES = [
    'docs/Draft/sections/abstract.tex',
    'docs/Draft/sections/section_1_intro.tex',
    'docs/Draft/sections/section_2_framework.tex',
    'docs/Draft/sections/section_3_main.tex',
    'docs/Draft/sections/section_4_additional.tex',
    'docs/Draft/sections/section_5_conclusion.tex',
    'docs/Draft/sections/appendix_c_robustness.tex',
]


def count_paragraphs(text):
    """Split a block of LaTeX text into paragraphs.

    A paragraph is a maximal run of non-blank non-comment lines.
    Lines starting with %, \section, \subsection, \subsubsection, \label, \begin/\end, \item are excluded
    from initiating a paragraph (but may appear inside one).
    """
    blocks = []
    cur = []
    for line in text.splitlines():
        stripped = line.strip()
        is_blank = not stripped
        is_comment = stripped.startswith('%')
        is_struct = re.match(r'^\\(section|subsection|subsubsection|label|begin|end|input|maketitle|appendix|onecolumn|twocolumn|noindent|item)\b', stripped)
        if is_blank or is_comment or is_struct:
            if cur:
                blocks.append(' '.join(cur))
                cur = []
            continue
        cur.append(stripped)
    if cur:
        blocks.append(' '.join(cur))
    return blocks


def split_subsections(text):
    """Yield (heading, body_text) per \subsection or \subsubsection block.

    The pre-first-heading block is yielded as ('PREAMBLE', text) only if non-empty after filtering.
    Inside each section, \subsubsection markers create nested entries.
    """
    parts = []
    HEADER_RE = re.compile(r'^\\(?P<lvl>section|subsection|subsubsection)\*?\{(?P<title>[^}]*)\}', re.MULTILINE)
    matches = list(HEADER_RE.finditer(text))
    if not matches:
        parts.append(('FILE_BODY', text))
        return parts
    # Preamble before first heading
    pre = text[:matches[0].start()]
    if count_paragraphs(pre):
        parts.append(('PREAMBLE', pre))
    for i, m in enumerate(matches):
        end = matches[i+1].start() if i+1 < len(matches) else len(text)
        heading = f"\\{m.group('lvl')}{{{m.group('title')}}}"
        body = text[m.end():end]
        parts.append((heading, body))
    return parts


for fpath in FILES:
    p = Path(fpath)
    text = p.read_text(encoding='utf-8')
    print(f'\n=== {p.name} ===')
    for heading, body in split_subsections(text):
        paras = count_paragraphs(body)
        # Truncate long heading display
        h = heading[:80]
        print(f'  {h:80s}  paras={len(paras)}')
