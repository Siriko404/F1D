# Second-Layer Adversarial Audit of Round 2 Review Panel

**Date:** 2026-04-03
**Scope:** Fact-check every empirical claim made by 5 reviewers against source data
**Agents:** 4 parallel auditors (NoCEO counts, star levels, hit rates, magnitudes)

---

## Audit Results Summary

| Auditor | Scope | Errors Found | Severity |
|---------|-------|-------------|----------|
| NoCEO Decomposition | All NoCEO counts across 5 reviewers | 6 | 4 Moderate, 2 Minor (all DA) |
| Star Levels & P-Values | All coefficients, stars, p-values in 6 suites | 3 | 3 HIGH (table bug) |
| Hit Rates & Single-IV | Cherry-picking rate, single-IV, no-lagged-DV | 7 | 2 Moderate (DA), 5 Minor |
| Magnitudes & Sample Sizes | DV means, standardized effects, N, R2, probit | 0 | --- |

**Total errors found: 16** (3 HIGH, 6 Moderate, 7 Minor)

---

## CRITICAL BUG FOUND AND FIXED

### IV_NAMES bug in both table generators

**Root cause:** `generate_thesis_tables.py` and `generate_all_tables.py` had OLD pre-rename
variable names in `IV_NAMES` list. The regression output files use NEW names (`UncAnsMgr`,
`UncAnsCEO`, etc.) since the variable rename. The IVs failed to match `IV_NAMES`, fell through
to the controls section, and received TWO-TAILED significance instead of the suite-specified tail.

**Impact:** H1 (one-tailed) had 3 under-starred cells in BOTH `thesis_tables.tex` AND `all_tables.tex`:
- Col 1: showed `*`, correct is `**` (p_one=0.0457 < 0.05)
- Col 2: showed `*`, correct is `**` (p_one=0.0289 < 0.05)
- Col 9: showed `**`, correct is `***` (p_one=0.0089 < 0.01)

For two-tailed suites (H4, H13, H16), the bug was SILENT because controls also use two-tailed.

**Fix applied:** Added post-rename short names to `IV_NAMES` in both files. Regenerated both
`thesis_tables.tex/pdf` and `all_tables.tex/pdf`. Verified fix: all 3 cells now show correct stars.

---

## Devil's Advocate Errors (8 total)

The DA made the strongest adversarial claims but had the most factual errors:

### NoCEO counts (6 errors)
| DA Claim | Actual | Error |
|----------|--------|-------|
| UncAnsNoCEO H1: 0/12 | **2/12** (col3 *, col5 * at Industry FE) | Undercounted by 2 |
| UncAnsNoCEO H13: 0/12 | **2/12** (col3 *, col5 * at Industry FE) | Undercounted by 2 |
| UncAnsNoCEO H16: 0/12 | **3/12** (col1 *, col3 *, col5 * at Industry FE) | Undercounted by 3 |
| UncAnsCEO H1: 9/12 | **10/12** | Undercounted by 1 |
| UncAnsCEO H16: 2/12 | **6/12** | Undercounted by 4 |
| "Null across ALL 60 specs" | **7/60 marginal** | Overstated nullity |

**Impact on DA's argument:** DA's central "kill shot" — "UncAnsNoCEO is null across ALL 60 specifications" —
is factually false. UncAnsNoCEO shows 7/60 marginal significance (all * at Industry FE). The thesis_findings.txt
correctly characterizes this as "marginal * at Industry FE." DA's claim that non-CEO managers "contribute ZERO
detectable signal" is wrong; the correct framing is "contribute only marginal Industry FE significance."

### Single-IV counts (2 errors)
| DA Claim | Actual | Error |
|----------|--------|-------|
| H4 single-IV: 1/24 | **3/24** | Undercounted by 2 |
| H16 single-IV: 3/12 | **4/12** | Undercounted by 1 |

### Hit rate denominator (1 error)
| DA Claim | Actual | Note |
|----------|--------|------|
| Denominator: 70 | **68** | Likely counted 2 non-IV terms |

---

## Minor Errors in Other Reviewers

### R1 & thesis_findings.txt: Star inflation in no-lagged-DV section
- H1 no-lagged-DV Firm FE specs: reported as `***`, actual p-values are 0.001-0.003 = `**`
- UncPreMgr no-lagged-DV: reported as `***`, actual p-values are 0.001-0.007 = `**`
- **Fixed** in both `thesis_findings.txt` and `findings.txt`

### thesis_findings.txt: H13 single-IV "pattern unchanged"
- Count actually increased 4/12 → 6/12. "Pattern" is defensible if interpreted as the
  Industry-FE-only selectivity pattern, but "unchanged" is misleading for counts.

---

## Fully Verified (Zero Errors)

| Category | Items Checked | Result |
|----------|--------------|--------|
| DV means | 11 values | All exact to 4dp |
| Standardized effects | 8 entries (24 sub-computations) | All correct |
| Sample sizes | 13 values | All exact |
| R-squared values | 12 entries | All correct |
| Coverage numbers | 3 ratios | All arithmetically correct |
| CEO probit | 5 coefficients, 5 z-stats, N, pseudo R2 | All exact |
| H4a/H4b stars | 24 columns | All correct |
| H13 stars | 12 columns | All correct |
| H16 stars | 12 columns | All correct |
| H1.2 stars | All terms | All correct |

---

## Corrections Applied

| # | File | Change | Severity |
|---|------|--------|----------|
| 1 | generate_thesis_tables.py | Added post-rename IV names to IV_NAMES | HIGH |
| 2 | generate_all_tables.py | Added post-rename IV names to IV_NAMES | HIGH |
| 3 | thesis_tables.tex + .pdf | Regenerated (H1 col1 *→**, col2 *→**, col9 **→***) | HIGH |
| 4 | all_tables.tex + .pdf | Regenerated (same 3 cells fixed) | HIGH |
| 5 | thesis_findings.txt | No-lagged-DV: *** → ** (2 instances) | Minor |
| 6 | findings.txt | No-lagged-DV: *** → ** (3 instances) | Minor |

---

## Conclusion

The pipeline's data flow from model estimation through CSV diagnostics is **perfectly accurate** —
zero transcription errors in DV means, coefficients, sample sizes, R-squared, or probit results.

The one real bug (IV_NAMES using old variable names) affected star rendering in tables for ONE
suite (H1, one-tailed). It was present in BOTH table generators but silent for two-tailed suites.
Now fixed and verified.

The Devil's Advocate reviewer had the most factual errors (8), all systematic undercounting that
overstated the adversarial case. The DA's conclusions remain directionally valid (CEO does dominate,
non-CEO contribution is marginal) but the specific counts and the "null everywhere" framing are wrong.

All other reviewers (EIC, R1, R2, R3) had correct or near-correct empirical claims.
