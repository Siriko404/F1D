#!/usr/bin/env python3
"""Exhaustive novelty check v2 — forward-citation screen.

The plain relevance sweep had bad recall (missed DWZ/Mayew/Larcker). Fix:
any paper linking earnings-call language to M&A almost certainly CITES one of
the canonical call-language measure papers. So:
  1. retrieve the seed papers (verify identity),
  2. pull ALL works citing each seed,
  3. screen citers for M&A/deal terms (title+abstract),
  4. union -> the candidate-prior shortlist.
Also a precise title_and_abstract search for deal x call x language directly.
Full -> tmp/litcheck_citenet_results.json ; shortlist -> stdout.
"""
import json, time, sys
from pathlib import Path
import pyalex
from pyalex import Works

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

pyalex.config.email = "sinasoleimanipour@gmail.com"
pyalex.config.max_retries = 4
pyalex.config.retry_backoff_factor = 0.6
pyalex.config.retry_http_codes = [429, 500, 503]

SEEDS = {
    'DWZ (speech uncertainty, conf calls)': 'Straight Talkers and Vague Talkers Managerial Style Earnings Conference Calls',
    'Bushee-Gow-Taylor (linguistic complexity)': 'Linguistic Complexity in Firm Disclosures Obfuscation or Information',
    'Mayew-Venkatachalam (power of voice)': 'The Power of Voice Managerial Affective States Future Firm Performance',
    'Larcker-Zakolyukina (deceptive calls)': 'Detecting Deceptive Discussions in Conference Calls',
    'Loughran-McDonald (uncertainty words)': 'When Is a Liability Not a Liability Textual Analysis Dictionaries 10-Ks',
}

DEAL = ['acquisition', 'acquisitions', 'acquirer', 'acquiring', 'merger', 'mergers',
        ' m&a', 'takeover', 'takeovers', 'bidder', 'tender offer', 'target firm',
        'diversifying deal', 'deal completion', 'pending deal', 'announced deal']


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


def sid(url):
    return (url or '').rsplit('/', 1)[-1]


# ---- 1. seed retrieval + identity print ----
seed_ids = {}
print("=== SEED IDENTITY (verify these are the right papers) ===")
for name, q in SEEDS.items():
    try:
        res = Works().search(q).get(per_page=3)
    except Exception as e:
        print(f"  ERR {name}: {e}")
        continue
    if not res:
        print(f"  NO MATCH: {name}")
        continue
    top = res[0]
    seed_ids[name] = sid(top.get('id'))
    print(f"  {name}\n     -> [{top.get('cited_by_count')}c {top.get('publication_year')}] "
          f"{(top.get('title') or '')[:90]}  ({sid(top.get('id'))})")
    time.sleep(0.2)

# ---- 2+3. pull citers of each seed, screen for deal terms ----
print("\n=== FORWARD-CITATION SCREEN ===")
deal_hits = {}
for name, wid in seed_ids.items():
    cnt = 0
    dmatch = 0
    try:
        pager = Works().filter(cites=wid).paginate(per_page=200, n_max=2000)
        for page in pager:
            for w in page:
                cnt += 1
                blob = (w.get('title') or '') + ' ' + recon(w.get('abstract_inverted_index'))
                if has(blob, DEAL):
                    dmatch += 1
                    k = sid(w.get('id'))
                    if k not in deal_hits:
                        pl = w.get('primary_location') or {}
                        src = pl.get('source') or {}
                        deal_hits[k] = {
                            'title': w.get('title') or '', 'year': w.get('publication_year'),
                            'venue': src.get('display_name') or '', 'cited': w.get('cited_by_count', 0),
                            'doi': w.get('doi'), 'abstract': recon(w.get('abstract_inverted_index')),
                            'via': [name]}
                    else:
                        deal_hits[k]['via'].append(name)
            time.sleep(0.15)
    except Exception as e:
        print(f"  ERR citers {name}: {e}")
    print(f"  {name}: {cnt} citers, {dmatch} mention M&A/deal terms")

# ---- 4. direct precise title+abstract search for the phenomenon ----
print("\n=== PRECISE title_and_abstract search (deal x call x language) ===")
PRECISE = [
    '"conference call" acquisition uncertainty',
    '"earnings call" merger language',
    '"conference call" acquirer tone',
    'acquisition "earnings call" obfuscation',
]
for q in PRECISE:
    try:
        res = Works().filter(**{'title_and_abstract.search': q}).get(per_page=25)
    except Exception as e:
        print(f"  ERR '{q}': {e}")
        continue
    rel = [w for w in res if has((w.get('title') or '') + ' '
           + recon(w.get('abstract_inverted_index')), DEAL)]
    print(f"  '{q}': {len(res)} hits, {len(rel)} with deal-term")
    for w in rel[:6]:
        k = sid(w.get('id'))
        if k not in deal_hits:
            pl = w.get('primary_location') or {}
            src = pl.get('source') or {}
            deal_hits[k] = {'title': w.get('title') or '', 'year': w.get('publication_year'),
                            'venue': src.get('display_name') or '', 'cited': w.get('cited_by_count', 0),
                            'doi': w.get('doi'), 'abstract': recon(w.get('abstract_inverted_index')),
                            'via': ['precise:' + q]}
    time.sleep(0.2)

# ---- output ----
hits = sorted(deal_hits.values(), key=lambda x: -x['cited'])
Path('tmp/litcheck_citenet_results.json').write_text(
    json.dumps(hits, indent=1, ensure_ascii=False), encoding='utf-8')
print(f"\n=== CANDIDATE PRIORS: {len(hits)} works cite a call-language seed AND mention M&A ===")
for w in hits:
    print(f"  [{w['cited']:>5}c {w['year']}] {w['title'][:96]} | {w['venue'][:30]}")
print("\nwrote tmp/litcheck_citenet_results.json (full abstracts for screening)")
