#!/usr/bin/env python3
"""Fight-test Fable's extraction plan: find attributions a section-by-section
prose walker would STRUCTURALLY miss. Pure programmatic — no eyeballing."""
import re

src = open('docs/Thesis/thesis_draft.tex', encoding='utf-8').read().splitlines()

sec_re = re.compile(r'^\\(sub)?section\*?\{|^\\appendix|^\\begin\{thebibliography\}|^\\maketitle')
secs = [(i + 1, l.strip()) for i, l in enumerate(src) if sec_re.match(l.strip())]
firstsec = next(i for i, l in secs if 'section' in l.lower())
appendix_ln = next((ln for ln, l in secs if 'appendix' in l.lower()), 9999)
bib_ln = next((ln for ln, l in secs if 'thebibliography' in l), 9999)

SUR = re.compile(r'Dzielinski|Wagner|Zeckhauser|Loughran|McDonald|Thewissen|Hassan|'
                 r'Hoberg|Phillips|Bushee|Lerman|Ragozzino|Reuer|Everhart|Gokkaya|'
                 r'Baker|Bloom|Davis|DWZ')
CITE = re.compile(r'\\cite')
# "soft" semantic-attribution tripwires that carry NO cite and NO surname
SOFT = re.compile(r'\b(literature|prior work|recent work|growing literature|a strand|'
                  r'established|documented|precedent|consistent with|following|'
                  r'studies show|body of work|prior studies)\b', re.I)

attrib = [(i + 1, l.strip()) for i, l in enumerate(src) if CITE.search(l) or SUR.search(l)]
soft = [(i + 1, l.strip()) for i, l in enumerate(src)
        if SOFT.search(l) and not CITE.search(l) and not SUR.search(l)]

print("=== STRUCTURE ===")
for ln, l in secs:
    print(f"  L{ln:<4} {l[:52]}")
print(f"\nfirst section L{firstsec} | appendix L{appendix_ln} | bib L{bib_ln}")

print("\n=== A) cite/surname attributions a SECTION-WALKER could skip ===")
miss = 0
for ln, txt in attrib:
    flag = ""
    if ln < firstsec:
        flag = "ABSTRACT/FRONT (before first \\section)"
    elif ln > bib_ln:
        flag = "AFTER \\begin{thebibliography} (bib list / appendix)"
    if flag:
        miss += 1
        print(f"  L{ln:<4} [{flag}] {txt[:60]}")
print(f"  -> {miss} attribution lines outside the main \\section..\\bibliography prose band")

print("\n=== B) SEMANTIC tripwires with NO cite + NO surname (eyeball-invisible) ===")
for ln, txt in soft:
    band = ("FRONT" if ln < firstsec else "BIB/APX" if ln > bib_ln else "BODY")
    print(f"  L{ln:<4} [{band}] {txt[:78]}")
print(f"  -> {len(soft)} semantic-only lines (each must be judged, none has a surname/cite to catch it)")
