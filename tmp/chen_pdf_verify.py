"""Programmatic PyMuPDF re-verification of every Chen 2020 spec claim.
Reads docs/papers/chen_etal_2017_restatement_jaaf.pdf fresh on each invocation
(no cached text). For each verbatim phrase, reports:
  - Found: True/False
  - PDF page (1-N index, p.1 = title page)
  - Journal page (= PDF p + 289)
  - 80-char context snippet
"""

import fitz  # PyMuPDF
import re

PDF = 'docs/papers/chen_etal_2017_restatement_jaaf.pdf'
doc = fitz.open(PDF)

# Build per-page text dict (programmatic re-extract, fresh)
pages = {}
for i, page in enumerate(doc):
    pages[i + 1] = page.get_text('text')

print(f'Loaded {len(pages)} pages from {PDF}')
print(f'Total chars: {sum(len(t) for t in pages.values())}')
print()


def find(phrase, label):
    """Search every page for verbatim phrase. Print page + context."""
    # Normalize whitespace in needle for tolerant matching
    needle = re.sub(r'\s+', ' ', phrase).strip()
    for pdf_p, txt in pages.items():
        haystack = re.sub(r'\s+', ' ', txt)
        if needle.lower() in haystack.lower():
            idx = haystack.lower().find(needle.lower())
            ctx_start = max(0, idx - 30)
            ctx_end = min(len(haystack), idx + len(needle) + 30)
            ctx = haystack[ctx_start:ctx_end]
            j_p = pdf_p + 289
            print(f'[{label}] FOUND  PDF p.{pdf_p}  j.p.{j_p}')
            print(f'  context: ...{ctx}...')
            print()
            return pdf_p, j_p
    print(f'[{label}] *** NOT FOUND ***  needle: "{phrase[:80]}..."')
    print()
    return None, None


print('=' * 80)
print('VERIFICATION: Q-A items')
print('=' * 80)

find('January 1997 through June 2006',
     'Q-A.1 sample window')

find('Hennes, Leone, and Miller (2008)',
     'Q-A.2 Hennes-LM source')

find('financial firms (Standard Industrial Classification code [SIC] 6000-6999) and 60 restatements from utility firms (SIC 4900-4999)',
     'Q-A.3 industry exclusions')

find('final sample of 949 restatements',
     'Q-A.4a final sample size')

find('679 are related to errors and 270 are related to irregularities',
     'Q-A.4b irregularity vs error split')

find('cash and short-term investments (Compustat data item #CHE) scaled by total assets (#AT)',
     'Q-A.5 CASH formula')

find('Our main test excludes year 0',
     'Q-A.6 POST timing year 0 excluded')

find('3 fiscal years after the restatement announcement',
     'Q-A.7 pre/post period')


print('=' * 80)
print('VERIFICATION: Q-B items (CRITICAL — Correction 1)')
print('=' * 80)

# CRITICAL: Industry-MEDIAN vs MEAN
find('industry-median value of the standard deviation of operating cash flow over the previous 10 years',
     'Q-B.1 SIGMA = industry-MEDIAN')

# Counter-test: does "industry-mean" also appear in SIGMA defn?
find('industry mean of the standard deviation',
     'Q-B.1-counter SIGMA industry-MEAN check (SHOULD NOT APPEAR)')

find('Tobin’s Q (Q) is defined as the book value of total assets',
     'Q-B.2a Q definition')

find('Operating cash flow (CF) is net operating cash flow (#OANCF) scaled by total assets',
     'Q-B.2b CF definition')

find('Net working capital (NWC) is noncash working capital',
     'Q-B.2c NWC definition')

find('Leverage (LEV) is the sum of long-term debt (#DLTT) and short-term debt (#DLC)',
     'Q-B.2d LEV definition')

# Industry classification for SIGMA
find('Fama and French’s 48-industry classification',
     'Q-B.1c FF48 confirmation (Table 4 footer)')


print('=' * 80)
print('VERIFICATION: Q-C items (PSM)')
print('=' * 80)

find('1:1', 'Q-C.5 1:1 ratio (literal token)')

find('matching without replacement',
     'Q-C.5 without replacement')

find('the closest propensity score',
     'Q-C.5 closest score (no caliper)')

find('over year t', 'Q-C.7a t-3 to t-1 averaging context')

find('measured over year t',
     'Q-C.7b t-3 to t-1 verbatim')

find('the year of the restatement announcement (i.e., year 0)',
     'Q-C.10 year-0 score')

find('matching procedure after eliminating',
     'Q-C tiebreak / replacement logic')


print('=' * 80)
print('VERIFICATION: Q-D items (CRITICAL — Correction 2)')
print('=' * 80)

# CRITICAL: NEG_IND_CORR construction
find('negative correlation between the industry-median CF and the industry-median',
     'Q-D.3 NEG_IND_CORR = neg corr btw industry-median CF + industry-median Q')

# Counter-test: does "ACW corr" or "Acharya, Almeida, and Campello" firm-level appear in PS_DEMAND?
find('ACW',
     'Q-D.3-counter ACW token check')

find('standard deviation of the industry-median CF over the previous 10 years',
     'Q-D.1 IND_STDCF = std-dev of industry-median CF')

find('standard deviation of the industry-median Tobin',
     'Q-D.2 IND_STDQ = std-dev of industry-median Tobin Q')

find('mean of the three ranks',
     'Q-D.4 PS_DEMAND = mean of percentile ranks')

# Table 4 footer
find('IND_STDCF is standard deviation of industry',
     'Q-D.5 IND_STDCF Table 4 footer')

find('PS_DEMAND is the mean value of the percentile ranks',
     'Q-D.4 Table 4 footer PS_DEMAND')


print('=' * 80)
print('VERIFICATION: Q-E items (CRITICAL — Correction 3)')
print('=' * 80)

# Headline values
find('0.046',
     'Q-E.1 Col 5 POST coef 0.046')
find('4.84',
     'Q-E.1 Col 5 t-stat 4.84')
find('1,391',
     'Q-E.1 Col 5 n=1,391')

find('0.012',
     'Q-E.2 Col 6 POST coef 0.012')
find('0.034',
     'Q-E.3 DiD difference 0.034')

# SE clustering
find('cluster standard errors at both the matched pair',
     'Q-E.4 SE matched-pair × year cluster')

# CRITICAL: Pseudo-event placebo claim
find('pseudo restatement',
     'Q-E.8 pseudo-event placebo (SHOULD NOT APPEAR in published)')

find('assign year T before',
     'Q-E.8-alt pseudo-event verbatim WP-style')

# Falsification
find('random',
     'Q-E.7 random treatment / falsification (token check)')

# IV/2SLS
find('instrumental',
     'Q-E.9 IV/2SLS check')
find('2SLS',
     'Q-E.9-alt 2SLS literal')

# Entropy balancing
find('entropy',
     'Q-E.10 entropy balancing check')

# Channel competitors
find('lines of credit',
     'Q-E.11 lines-of-credit (SHOULD NOT APPEAR in published)')

find('investment irreversibility',
     'Q-E.11-alt INV_IRREVERS Table 6')

find('CEO/CFO',
     'Q-E.11-alt CEO/CFO turnover check')


print('=' * 80)
print('SUMMARY: ALL VERIFICATION COMPLETE')
print('=' * 80)
