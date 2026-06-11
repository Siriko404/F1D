#!/usr/bin/env python3
"""Novelty lit-check via OpenAlex/pyalex.

Question: has ANY prior work linked pending/undisclosed M&A (deal anticipation)
to earnings-call linguistic measures (uncertainty/tone/obfuscation/etc.)?

Strategy: 18 multi-angle relevance searches; dedupe; auto-tier each hit by
whether title+abstract mention deal-terms x call-terms x language-terms.
Tier 1 (deal+call+language) = the closest possible priors to screen by hand.
Full results -> tmp/litcheck_openalex_results.json ; curated shortlist -> stdout.
"""
import json, time
from pathlib import Path
from collections import Counter
import pyalex
from pyalex import Works

pyalex.config.email = "sinasoleimanipour@gmail.com"  # polite pool
pyalex.config.max_retries = 3
pyalex.config.retry_backoff_factor = 0.5
pyalex.config.retry_http_codes = [429, 500, 503]

QUERIES = [
    # phenomenon: deal x call language
    'earnings call acquisition linguistic uncertainty',
    'conference call merger tone manager',
    'earnings call merger obfuscation language',
    'acquisition announcement conference call manager tone',
    'pending acquisition disclosure earnings call language',
    'takeover earnings call linguistic uncertainty CEO',
    'acquirer earnings call information asymmetry language',
    'bidder disclosure tone merger announcement',
    # strategic silence / withholding / MNPI
    'strategic silence disclosure earnings call',
    'quiet period disclosure language merger acquisition',
    'managerial withholding material information conference call',
    'selective disclosure acquisition manager language',
    'material nonpublic information manager disclosure tone call',
    # call linguistic-uncertainty measure family
    'CEO earnings call speech uncertainty',
    'managerial obfuscation conference call readability',
    'earnings call uncertainty words Loughran McDonald',
    'earnings conference call linguistic tone CEO residual',
    'manager hedging language earnings call uncertainty',
]

DEAL = ['acquisition', 'acquisitions', 'acquirer', 'acquiring', 'merger', 'mergers',
        'm&a', 'takeover', 'takeovers', 'bidder', 'tender offer', 'target firm', 'deal ']
CALL = ['earnings call', 'conference call', 'earnings conference', 'quarterly call',
        'earnings-call', 'conference-call', 'analyst call']
LANG = ['uncertainty', 'tone', 'linguistic', 'obfuscation', 'readability', 'fog',
        'hedging', 'sentiment', 'textual', 'speech', 'vague', 'wording', 'narrative',
        'disclosure tone', 'language']


def recon(inv):
    if not inv:
        return ''
    pos = {}
    for w, ixs in inv.items():
        for i in ixs:
            pos[i] = w
    return ' '.join(pos[i] for i in sorted(pos))


def has(t, terms):
    t = t.lower()
    return any(k in t for k in terms)


seen = {}
for q in QUERIES:
    try:
        try:
            res = Works().search(q).get(per_page=50)
        except TypeError:
            res = Works().search(q).get()
    except Exception as e:
        print('ERR', q, '->', e)
        continue
    for w in res:
        wid = w.get('id')
        if not wid:
            continue
        if wid not in seen:
            pl = w.get('primary_location') or {}
            src = pl.get('source') or {}
            seen[wid] = {
                'id': wid, 'title': w.get('title') or '',
                'year': w.get('publication_year'),
                'venue': src.get('display_name') or '',
                'cited': w.get('cited_by_count', 0),
                'doi': w.get('doi'),
                'abstract': recon(w.get('abstract_inverted_index')),
                'queries': [q],
            }
        else:
            seen[wid]['queries'].append(q)
    time.sleep(0.2)

works = list(seen.values())
for w in works:
    blob = w['title'] + ' ' + w['abstract']
    d, c, l = has(blob, DEAL), has(blob, CALL), has(blob, LANG)
    w['tier'] = 1 if (d and c and l) else 2 if (d and c) else 3 if (c and l) else 4

Path('tmp').mkdir(exist_ok=True)
Path('tmp/litcheck_openalex_results.json').write_text(
    json.dumps(works, indent=1, ensure_ascii=False), encoding='utf-8')

tc = Counter(w['tier'] for w in works)
print(f"TOTAL unique works: {len(works)}  (from {len(QUERIES)} queries)")
print(f"Tier1 deal+call+lang: {tc[1]}   Tier2 deal+call: {tc[2]}   "
      f"Tier3 call+lang: {tc[3]}   Tier4 other: {tc[4]}")


def show(tier, label, limit=25):
    rows = sorted([w for w in works if w['tier'] == tier], key=lambda x: -x['cited'])
    print(f"\n{'='*72}\n### {label}  (n={len(rows)}, showing {min(limit,len(rows))})")
    for w in rows[:limit]:
        print(f"[{w['cited']:>5}c {w['year']}] {w['title'][:104]} | {w['venue'][:38]}")


show(1, "TIER 1 - deal x call x language (CLOSEST priors - screen these)")
show(2, "TIER 2 - deal x call (no language term)")
print(f"\n(Tier 3 call+language = {tc[3]} general call-text papers; in JSON.)")
print("wrote tmp/litcheck_openalex_results.json")
