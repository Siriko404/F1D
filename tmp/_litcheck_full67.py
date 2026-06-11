#!/usr/bin/env python3
"""BLOCKING fixes per advisor:
(1) abstract-screen ALL 67 citer-hits (not just the 11 title-matched);
(2) Semantic Scholar Graph API backfill for the no-abstract closest papers.
Rank by phenomenon-signal so a hidden scoop surfaces.
"""
import sys, json, time, urllib.request
from pathlib import Path
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

hits = json.loads(Path('tmp/litcheck_citenet_results.json').read_text(encoding='utf-8'))

# anticipatory-timing / withholding signal + language-outcome signal
ANTIC = ['anticipat', 'pre-announc', 'preannounc', 'before the announc', 'prior to the announc',
         'run-up', 'runup', 'leading up', 'ahead of', 'impending', 'pending', 'rumor', 'leak',
         'withhold', 'conceal', 'strategic silence', 'quiet period', 'gag', 'nonpublic',
         'non-public', 'mnpi', 'undisclosed', 'in advance of', 'prior to announc']
LANG = ['uncertain', 'vague', 'tone', 'obfuscat', 'hedg', 'linguistic', 'residual', 'speech',
        'sentiment', 'readab', 'textual', 'language', 'fog']


def score(w):
    t = (w['title'] + ' ' + w['abstract']).lower()
    a = sum(k in t for k in ANTIC)
    l = sum(k in t for k in LANG)
    return a * 10 + l, a, l


print(f"=== ALL {len(hits)} M&A-citers re-screened by anticipatory-signal ===")
ranked = sorted(hits, key=lambda w: -score(w)[0])
for w in ranked[:14]:
    s, a, l = score(w)
    ab = w['abstract'].strip() or '(NO ABSTRACT)'
    print(f"\n[sig {s} | antic {a} lang {l}] [{w['cited']}c {w['year']}] {w['title'][:88]}")
    print(f"   {ab[:340]}")

noabs = [w for w in hits if not w['abstract'].strip()]
print(f"\n=== {len(noabs)} hits with NO OpenAlex abstract ===")
for w in noabs:
    print(f"   [{w['cited']}c {w['year']}] {w['title'][:84]} | {w['doi']}")

# ---- Semantic Scholar backfill ----
print("\n=== Semantic Scholar backfill (closest no-abstract papers) ===")
TARGETS = [w['doi'] for w in noabs if w['doi']] + ['https://doi.org/10.1016/j.lrp.2023.102393']
seen_doi = set()
for d in TARGETS:
    doi = (d or '').replace('https://doi.org/', '')
    if not doi or doi in seen_doi:
        continue
    seen_doi.add(doi)
    url = f"https://api.semanticscholar.org/graph/v1/paper/DOI:{doi}?fields=title,abstract,tldr,year,venue"
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'litcheck/1.0'})
        with urllib.request.urlopen(req, timeout=25) as r:
            j = json.load(r)
        ab = (j.get('abstract') or '').strip()
        tl = ((j.get('tldr') or {}) or {}).get('text', '')
        print(f"\n[{j.get('year')}] {(j.get('title') or '')[:84]}")
        if tl:
            print(f"   TLDR: {tl[:300]}")
        print(f"   ABS: {ab[:520] if ab else '(none)'}")
    except Exception as e:
        print(f"\n  {doi} -> {e}")
    time.sleep(1.1)
