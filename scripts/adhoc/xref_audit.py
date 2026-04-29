"""
Phase 0 — cross-reference audit.
1. Every \ref{tab:...} / \ref{sec:...} / \ref{app:...} in content sections → does target \label{...} exist somewhere?
2. Every \cite{key} / \citeA{key} / \citeauthor{key} in content sections → does key exist in references.bib?
3. Report orphans (labels never referenced) and broken refs (refs without matching label).
"""
import re
from pathlib import Path

CONTENT = [
    'docs/Draft/sections/abstract.tex',
    'docs/Draft/sections/section_1_intro.tex',
    'docs/Draft/sections/section_2_framework.tex',
    'docs/Draft/sections/section_3_main.tex',
    'docs/Draft/sections/section_4_additional.tex',
    'docs/Draft/sections/section_5_conclusion.tex',
    'docs/Draft/sections/appendix_c_robustness.tex',
    'docs/Draft/variable_definitions.tex',
]

# All files where a \label{...} could live (body sections + per_suite tables + summary stats + appendix)
LABEL_SOURCES = list(Path('docs/Draft').rglob('*.tex'))

REF_RE = re.compile(r'\\(?:ref|hyperref\[)\{([^}]+)\}|\\hyperref\[([^\]]+)\]')
LABEL_RE = re.compile(r'\\label\{([^}]+)\}')
CITE_RE = re.compile(r'\\(?:cite[A-Z]?|citep|citet|citealt|citealp|citeauthor|citeyear)\*?\{([^}]+)\}')

# Build label index
labels = {}  # label -> file
for p in LABEL_SOURCES:
    try:
        text = p.read_text(encoding='utf-8')
    except Exception:
        continue
    for m in LABEL_RE.finditer(text):
        lab = m.group(1)
        labels.setdefault(lab, []).append(str(p))

# Collect refs from content
refs = {}  # ref -> [files]
for fpath in CONTENT:
    text = Path(fpath).read_text(encoding='utf-8')
    for m in REF_RE.finditer(text):
        r = m.group(1) or m.group(2)
        refs.setdefault(r, []).append(fpath)

# Collect cites from content
cites = {}
for fpath in CONTENT:
    text = Path(fpath).read_text(encoding='utf-8')
    for m in CITE_RE.finditer(text):
        keys = [k.strip() for k in m.group(1).split(',')]
        for k in keys:
            cites.setdefault(k, []).append(fpath)

# Bib keys
bib_text = Path('docs/Draft/references.bib').read_text(encoding='utf-8')
bib_keys = set(re.findall(r'@\w+\{([^,]+),', bib_text))

# Report
print('=== REFS ===')
broken = []
for r, where in sorted(refs.items()):
    if r not in labels:
        broken.append(r)
        print(f'  BROKEN: \\ref{{{r}}} cited in {set(where)} — no \\label found')
if not broken:
    print('  All \\ref targets resolve.')

print()
print('=== ORPHAN LABELS ===')
# Labels defined in content sections but never referenced from content
content_labels = set()
for fpath in CONTENT:
    text = Path(fpath).read_text(encoding='utf-8')
    for m in LABEL_RE.finditer(text):
        content_labels.add(m.group(1))
orphans = content_labels - set(refs.keys())
for o in sorted(orphans):
    print(f'  ORPHAN: \\label{{{o}}} (not referenced from any content section)')
if not orphans:
    print('  No orphan labels in content.')

print()
print('=== CITES ===')
broken_cites = []
for k, where in sorted(cites.items()):
    if k not in bib_keys:
        broken_cites.append(k)
        print(f'  BROKEN: \\cite{{{k}}} cited in {set(where)} — not in references.bib')
if not broken_cites:
    print('  All \\cite keys resolve.')

print()
print('=== UNUSED BIB ENTRIES ===')
unused = bib_keys - set(cites.keys())
for k in sorted(unused):
    print(f'  UNUSED: {k}')
if not unused:
    print('  All bib entries cited.')

print()
print(f'Summary: {len(refs)} unique refs, {len(broken)} broken | {len(cites)} unique cites, {len(broken_cites)} broken | {len(orphans)} orphan labels | {len(unused)} unused bib entries')
