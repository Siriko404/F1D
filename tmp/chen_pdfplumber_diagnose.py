"""Diagnose pdfplumber vs PyMuPDF divergences on Chen 2020.

For each divergent claim, dump the relevant pdfplumber-extracted page region
to confirm whether content is PRESENT (whitespace divergence — formatting only)
or ABSENT (substance divergence — invalidates claim).
"""

import pdfplumber

PDF = 'docs/papers/chen_etal_2017_restatement_jaaf.pdf'

with pdfplumber.open(PDF) as pdf:
    pages = {}
    for i, page in enumerate(pdf.pages):
        pages[i + 1] = page.extract_text() or ''


def show_region(pdf_p, anchor, span_chars=350, label=''):
    """Show ±span_chars around an anchor token on a given page."""
    txt = pages[pdf_p]
    idx = txt.lower().find(anchor.lower())
    if idx < 0:
        print(f'[{label}] anchor "{anchor}" NOT in pdfplumber p.{pdf_p}')
        # show chars around anchor's expected location anyway
        return
    s = max(0, idx - 80)
    e = min(len(txt), idx + len(anchor) + span_chars)
    print(f'[{label}] PDF p.{pdf_p} (j.p.{pdf_p+289}) — anchor: "{anchor}"')
    print('---')
    print(txt[s:e])
    print('---')
    print()


print('=' * 80)
print('DIVERGENCE 1: Q-B.1 SIGMA = industry-MEDIAN (PDF p.6)')
print('=' * 80)
show_region(6, 'SIGMA', span_chars=350, label='SIGMA region p.6')


print('=' * 80)
print('DIVERGENCE 2: Q-D.3 NEG_IND_CORR (PDF p.14)')
print('=' * 80)
show_region(14, 'negative correlation', span_chars=300, label='NEG_IND_CORR region p.14')


print('=' * 80)
print('DIVERGENCE 3: Q-D.4 Table 4 footer PS_DEMAND defn (PDF p.16)')
print('=' * 80)
show_region(16, 'PS_DEMAND', span_chars=400, label='Table 4 PS_DEMAND footer p.16')


print('=' * 80)
print('DIVERGENCE 4: Q-C.5 "matching without replacement" (PDF p.25)')
print('=' * 80)
show_region(25, 'eliminating the selected', span_chars=200, label='PSM no-replace p.25')


print('=' * 80)
print('DIVERGENCE 5: Q-E.1 n=1,391 (Table 3 PDF p.11)')
print('=' * 80)
show_region(11, '1,391', span_chars=120, label='Table 3 row n=1391 p.11')
# Fallback: maybe pdfplumber rendered without comma
show_region(11, '1391', span_chars=120, label='Fallback: n=1391 no-comma p.11')
# Or maybe the n is on a different page
print('Table 3 spans p.11-13. Search across:')
for p in [10, 11, 12, 13]:
    if pages.get(p):
        if '1,391' in pages[p] or '1391' in pages[p]:
            print(f'  Page {p}: contains 1,391 or 1391')
        else:
            print(f'  Page {p}: NEITHER "1,391" NOR "1391" found')
print()


print('=' * 80)
print('FALSIFICATION TEST: counter-claims that should be ABSENT')
print('=' * 80)

# CRITICAL: confirm "industry mean" is genuinely absent in pdfplumber too
print('Q-B.1c: searching "industry-mean" / "industry mean" anywhere:')
for p, txt in pages.items():
    if 'industry-mean' in txt.lower() or 'industry mean' in txt.lower():
        idx = txt.lower().find('industry-mean')
        if idx < 0: idx = txt.lower().find('industry mean')
        print(f'  Page {p}: ...{txt[max(0,idx-30):idx+60]}...')
print()

# CRITICAL: confirm "ACW" is absent
print('Q-D.3: searching "ACW" / "ACW corr" anywhere:')
for p, txt in pages.items():
    if 'ACW' in txt:
        idx = txt.find('ACW')
        print(f'  Page {p}: ...{txt[max(0,idx-30):idx+60]}...')
print('  (none = correct, ACW concept not directly used)')
print()

# CRITICAL: confirm "pseudo restatement" / "pseudo event" is absent
print('Q-E.8: searching "pseudo" / "placebo" anywhere:')
for p, txt in pages.items():
    for token in ['pseudo', 'placebo', 'falsif']:
        if token.lower() in txt.lower():
            idx = txt.lower().find(token.lower())
            print(f'  Page {p} ("{token}"): ...{txt[max(0,idx-30):idx+60]}...')
print()

# CRITICAL: confirm IV/2SLS absent
print('Q-E.9: searching "IV" / "instrument" / "2SLS" anywhere:')
for p, txt in pages.items():
    for token in ['instrument', '2SLS', '2sls', ' IV ']:
        if token in txt:
            idx = txt.find(token)
            print(f'  Page {p} ("{token}"): ...{txt[max(0,idx-30):idx+60]}...')
print()

# CRITICAL: confirm entropy absent
print('Q-E.10: searching "entropy" anywhere:')
hits = 0
for p, txt in pages.items():
    if 'entropy' in txt.lower():
        idx = txt.lower().find('entropy')
        print(f'  Page {p}: ...{txt[max(0,idx-30):idx+60]}...')
        hits += 1
if hits == 0:
    print('  (none = correct)')
print()

# CRITICAL: confirm "lines of credit" absent (per published)
print('Q-E.11: searching "lines of credit" / "credit line" / "unused" anywhere:')
hits = 0
for p, txt in pages.items():
    for token in ['lines of credit', 'line of credit', 'credit line', 'unused']:
        if token.lower() in txt.lower():
            idx = txt.lower().find(token.lower())
            print(f'  Page {p} ("{token}"): ...{txt[max(0,idx-30):idx+80]}...')
            hits += 1
if hits == 0:
    print('  (none = correct, lines-of-credit channel test absent from published)')
