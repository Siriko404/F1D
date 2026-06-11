"""Scratch: enumerate candidate word-form arithmetic claims in the draft prose."""
import re
txt = open('docs/Thesis/thesis_draft.tex', encoding='utf-8').read()
txt = txt[txt.find(r'\begin{document}'):]
txt = re.sub(r'\\begin\{thebibliography\}.*?\\end\{thebibliography\}', ' ', txt, flags=re.S)
txt = re.sub(r'\\begin\{tabular\}.*?\\end\{tabular\}', ' ', txt, flags=re.S)
txt = re.sub(r'\\section\*\{Tables\}.*\Z', ' ', txt, flags=re.S)
txt = re.sub(r'(?<!\\)%.*', '', txt)
sents = re.split(r'(?<=[.;:])\s+', txt.replace('\n', ' '))
TRIG = re.compile(
    r'\b(percent|per cent|standard deviation|half|third|quarter|twice|double|fold|'
    r'times|identical|again|roughly|about|nearly|fifteen|three|twelve|swing|drop|'
    r'fall|exceeds|larger|smaller|point|points|percentage|share|mean|order of)\b|%',
    re.I)
n = 0
for s in sents:
    s = re.sub(r'\s+', ' ', s).strip()
    if s and TRIG.search(s):
        n += 1
        print(f'[{n:02d}] {s[:320]}')
print(f'\n{n} candidate sentences')
