"""Programmatic /pdf-STRICT re-verification of Chen 2020 spec claims.

Per ~/.claude/skills/pdf/SKILL.md Quick Reference table:
   "Extract text | pdfplumber | `page.extract_text()`"

This script uses pdfplumber.extract_text() — NOT PyMuPDF/fitz.
PyMuPDF is mentioned in reference.md only as something pypdfium2 replaces.
"""

import pdfplumber
import re

PDF = 'docs/papers/chen_etal_2017_restatement_jaaf.pdf'

with pdfplumber.open(PDF) as pdf:
    pages = {}
    for i, page in enumerate(pdf.pages):
        pages[i + 1] = page.extract_text() or ''

print(f'Loaded {len(pages)} pages from {PDF} via pdfplumber')
print(f'Total chars: {sum(len(t) for t in pages.values())}')
print()


def find(phrase, label):
    """Search every page for verbatim phrase via pdfplumber-extracted text."""
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
find('January 1997 through June 2006', 'Q-A.1 sample window')
find('Hennes, Leone, and Miller (2008)', 'Q-A.2 Hennes-LM source')
find('financial firms (Standard Industrial Classification code [SIC] 6000-6999) and 60 restatements from utility firms (SIC 4900-4999)',
     'Q-A.3 industry exclusions')
find('final sample of 949 restatements', 'Q-A.4a final sample')
find('679 are related to errors and 270 are related to irregularities',
     'Q-A.4b irreg vs err split')
find('cash and short-term investments (Compustat data item #CHE) scaled by total assets (#AT)',
     'Q-A.5 CASH formula')
find('Our main test excludes year 0', 'Q-A.6 POST timing')
find('3 fiscal years after the restatement announcement', 'Q-A.7 pre/post period')


print('=' * 80)
print('VERIFICATION: Q-B (CRITICAL — Correction 1: SIGMA = MEDIAN)')
print('=' * 80)

# CRITICAL CLAIM
find('industry-median value of the standard deviation of operating cash flow over the previous 10 years',
     'Q-B.1 SIGMA = industry-MEDIAN  (CRITICAL)')

# Counter-test
find('industry mean of the standard deviation',
     'Q-B.1-counter SIGMA = industry-MEAN  (MUST NOT APPEAR)')

find('Tobin', 'Q-B.2a Tobin token check')
find('Operating cash flow (CF) is net operating cash flow', 'Q-B.2b CF def')
find('Net working capital (NWC) is noncash working capital', 'Q-B.2c NWC def')
find('Leverage (LEV) is the sum of long-term debt', 'Q-B.2d LEV def (relaxed)')
find('Fama and French', 'Q-B.1c FF-industry token check')


print('=' * 80)
print('VERIFICATION: Q-C (PSM)')
print('=' * 80)
find('matching without replacement', 'Q-C.5 without replacement')
find('the closest propensity score', 'Q-C.5 closest score')
find('measured over year t', 'Q-C.7 t-3 to t-1 averaging')
find('the year of the restatement announcement (i.e., year 0)', 'Q-C.10 year-0 score')
find('eliminating the selected control firm', 'Q-C tiebreak / 1:1')


print('=' * 80)
print('VERIFICATION: Q-D (CRITICAL — Correction 2: NEG_IND_CORR industry-median)')
print('=' * 80)

# CRITICAL CLAIM
find('negative correlation between the industry-median CF and the industry-median',
     'Q-D.3 NEG_IND_CORR industry-median  (CRITICAL)')

# Counter-test
find('ACW', 'Q-D.3-counter ACW token check  (MUST NOT APPEAR)')
find('Acharya', 'Q-D.3-related Acharya citation check')

find('standard deviation of the industry-median CF over the previous 10 years',
     'Q-D.1 IND_STDCF def')
find('standard deviation of the industry-median Tobin', 'Q-D.2 IND_STDQ def')
find('mean of the three ranks', 'Q-D.4 PS_DEMAND mean of ranks')
find('IND_STDCF is standard deviation of industry', 'Q-D.5 Table 4 footer')
find('PS_DEMAND is the mean value of the percentile ranks', 'Q-D.4 Table 4 footer PS_DEMAND')


print('=' * 80)
print('VERIFICATION: Q-E (CRITICAL — Correction 3: pseudo-event NOT in published)')
print('=' * 80)

# Headline numbers
find('(0.046, t = 4.84)', 'Q-E.1 Col 5 verbatim "(0.046, t = 4.84)"')
find('1,391', 'Q-E.1 Col 5 n=1,391 in Table 3')
find('coefficient on POST for the irregularity firms', 'Q-E.1 narrative')
find('treatment effect of irregularity-related restatements is significant (0.034',
     'Q-E.3 DiD diff verbatim')

# SE
find('cluster standard errors at both the matched pair', 'Q-E.4 SE matched-pair × year')

# CRITICAL: Pseudo-event placebo
find('pseudo restatement', 'Q-E.8 pseudo-event placebo  (MUST NOT APPEAR)')
find('assign year T before', 'Q-E.8-alt pseudo-event WP-style  (MUST NOT APPEAR)')

# Falsification / IV / entropy
find('random', 'Q-E.7 random treatment token  (MUST NOT APPEAR)')
find('instrumental', 'Q-E.9 IV check')
find('2SLS', 'Q-E.9-alt 2SLS check')
find('entropy', 'Q-E.10 entropy balancing check')

# Channel-competitor: lines of credit
find('lines of credit', 'Q-E.11 lines-of-credit  (MUST NOT APPEAR per published)')
find('line of credit', 'Q-E.11-alt singular line-of-credit')

# Confirm channel partitions ARE in published
find('investment irreversibility', 'Q-E.11-alt INV_IRREVERS Table 6')
find('CEO/CFO turnover', 'Q-E.11-alt CEO/CFO partition')
find('DECREASE_OPTION', 'Q-E.11-alt DECREASE_OPTION partition')
find('DECREASE_XINV', 'Q-E.11-alt DECREASE_XINV partition')


print('=' * 80)
print('PARITY CHECK vs PyMuPDF extraction')
print('=' * 80)
print('Claim was: PyMuPDF and pdfplumber give same result on these claims.')
print('If pdfplumber FOUND items that PyMuPDF did NOT find, or vice versa,')
print('that signals an extraction-tool divergence requiring re-investigation.')
