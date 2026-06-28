# -*- coding: utf-8 -*-
"""Generalized number-vs-source check for the 15 non-4.5 sections (the readiness gate).
Builds a token set {(value, stars)} from the located primary sources, then classifies every
coefficient-shaped number in each section's props: EXACT match / STAR-MISMATCH / ABSENT.
Derived stats (p, z, within-R2, pseudo-R2) are skipped (not table cells). Surfaces a fix-list."""
import json, re
from pathlib import Path
PH = Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3")
FIN = PH/"docs/Thesis/rewrite/_final"

# ---- 1. source token set: (normalized_value, stars) from all located primary sources ----
SOURCES = [
    PH/"docs/Thesis/_tables_from_bible.tex",
    PH/"docs/Draft/_empire_drop_resolution.tex",
    PH/"docs/Draft/_empire_drop_staticfe.tex",
    PH/"tmp/nlm_dwz_reactions.json",
    PH/"tmp/nlm_bgt_spread.json",
    Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")/"outputs/econometric/firstdeal_robustness/2026-06-23_162451/rob_4tables.tex",
]
TOK = re.compile(r'(-?\d?\.\d{2,5})\s*(?:\$\^\{(\*{1,3})\}\$|\^\{?(\*{1,3})\}?|(\*{1,3}))?')
def val(s):  # normalize: drop sign + leading zero, keep digits
    return s.lstrip('+-').lstrip('0') or '0'
src_exact=set()   # (value, stars)
src_vals=set()    # value only (any stars)
for p in SOURCES:
    if not p.exists():
        print(f"  [warn] source missing: {p.name}"); continue
    raw=p.read_text(encoding="utf-8")
    if p.suffix=='.json':  # pull all numbers from json text
        for m in re.finditer(r'-?\d?\.\d{2,5}', raw):
            v=val(m.group(0)); src_vals.add(v); src_exact.add((v,''))
    else:
        raw=raw.replace(r'\textbf{','').replace('}$^{','$^{').replace('}^{','^{')  # join NUM to its star marker
        for m in TOK.finditer(raw):
            v=val(m.group(1)); st=m.group(2) or m.group(3) or m.group(4) or ''
            src_exact.add((v,st)); src_vals.add(v)
print(f"[input] source tokens: {len(src_exact)} (value,stars) from {len(SOURCES)} files; {len(src_vals)} distinct values")

# ---- 2. per-section prop number classification ----
DERIVED = re.compile(r'(within-?R2|pseudo-?R2|R2|p\s*[=~<.]|p\b|z\s*[=~]|SE\b|\bN\b|n_firms|base rate|%)', re.I)
PROPNUM = re.compile(r'([+-]?\d?\.\d{3,4})(\*{1,3})?')
files=[f for f in sorted(FIN.glob("section*.json")) if '4.5' not in f.name]
summary=[]; allflags=[]
for f in files:
    d=json.load(open(f,encoding="utf-8"))
    pl=d['paragraphs']; items=list(pl.values()) if isinstance(pl,dict) else pl
    ok=star=absent=derived=0; flags=[]
    for pa in items:
        props=pa.get('propositions') or pa.get('proposition_chain') or []
        for pr in props:
            pid=pr.get('prop_id','?')
            # token-with-context: scan statement + each numbers[] entry
            chunks=[pr.get('statement','')] + (pr.get('numbers',[]) if isinstance(pr.get('numbers'),list) else [])
            for ch in chunks:
                for m in PROPNUM.finditer(ch):
                    raw=m.group(1); st=m.group(2) or ''
                    v=val(raw)
                    # context window for derived-stat detection
                    a=max(0,m.start()-8); ctx=ch[a:m.end()+3]
                    if DERIVED.search(ctx) and (v,st) not in src_exact:
                        derived+=1; continue
                    if (v,st) in src_exact: ok+=1
                    elif v in src_vals:
                        star+=1; flags.append((pid,'STAR',raw+st,f'value {v} in source but not with stars "{st}"'))
                    else:
                        absent+=1; flags.append((pid,'ABSENT',raw+st,f'value {v} not in any source'))
    sec=f.stem.replace('_paragraph_ledger','')
    summary.append((sec,ok,star,absent,derived))
    for fl in flags: allflags.append((sec,)+fl)

print("\n"+"="*70)
print(f"{'section':14s} {'OK':>4s} {'STAR?':>6s} {'ABSENT?':>8s} {'derived':>8s}")
print("="*70)
to=ts=ta=0
for sec,ok,st,ab,de in summary:
    tag = '' if (st+ab)==0 else '  <-- CHECK'
    print(f"{sec:14s} {ok:>4d} {st:>6d} {ab:>8d} {de:>8d}{tag}")
    to+=ok; ts+=st; ta+=ab
print("="*70)
print(f"{'TOTAL':14s} {to:>4d} {ts:>6d} {ta:>8d}")
print(f"\nSections fully clean (0 flags): {sum(1 for _,_,st,ab,_ in summary if st+ab==0)}/15")
print(f"Sections with flags: {sorted(set(s for s,_,_,_ ,_ in summary if True) & set(fl[0] for fl in allflags))}")
print(f"\n--- ALL FLAGS ({len(allflags)}) ---")
for sec,pid,kind,tok,why in allflags[:80]:
    print(f"  [{kind:6s}] {sec} {pid}: {tok}  ({why})")
