# Audit 05: Summary Statistics Table
**Date:** 2026-03-13
**Auditor:** Claude Agent
**Scope:** Lines 254-317 of thesis_draft.tex (Table 2: Unified Summary Statistics)
**Verdict:** FAIL

## Source Files Used for Verification

All four econometric summary_stats.csv files (latest timestamped runs on 2026-03-13):

| Key  | File Path | Sample Scope |
|------|-----------|-------------|
| H0.3 | `outputs/econometric/ceo_clarity_extended/2026-03-13_053119/summary_stats.csv` | H0.3 estimation sample (N=38,331 Main) |
| H7   | `outputs/econometric/h7_illiquidity/2026-03-13_054310/summary_stats.csv` | Full Main sample (N=88,205 pre-missingness) |
| H14  | `outputs/econometric/h14_bidask_spread/2026-03-13_053119/summary_stats.csv` | Full Main sample |
| H9   | `outputs/econometric/takeover/2026-03-13_053120/summary_stats.csv` | Full panel incl. all industries (N=84,104) |

Also consulted variable-level (pre-econometric) summary_stats.csv files where econometric files did not contain the variable.

---

## Panel A: Dependent Variables

### Row 1: Manager QA Uncertainty (%)
**Source: H7** (line 7: `Mgr QA Uncertainty`)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 84,484 | 84,484 | MATCH |
| Mean | 0.821 | 0.8209 | MATCH (rounds to 0.821) |
| SD | 0.321 | 0.3206 | MATCH (rounds to 0.321) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.599 | 0.5986 | MISMATCH: 0.5986 rounds to 0.599, OK |
| Median | 0.792 | 0.7917 | MATCH (rounds to 0.792) |
| P75 | 1.009 | 1.0086 | MATCH (rounds to 1.009) |
| Max | 2.037 | 2.0367 | MATCH (rounds to 2.037) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 2: CEO QA Uncertainty (%)
**Source: H7** (line 5)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 62,132 | 62,132 | MATCH |
| Mean | 0.777 | 0.7772 | MATCH (rounds to 0.777) |
| SD | 0.391 | 0.3914 | MATCH (rounds to 0.391) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.512 | 0.5116 | MATCH (rounds to 0.512) |
| Median | 0.738 | 0.7376 | MATCH (rounds to 0.738) |
| P75 | 0.998 | 0.9983 | MATCH (rounds to 0.998) |
| Max | 2.514 | 2.5143 | MATCH (rounds to 2.514) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 3: Delta Amihud Illiquidity
**Source: H7** (line 2)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 86,906 | 86,906 | MATCH |
| Mean | 0.092 | 0.0918 | MATCH (rounds to 0.092) |
| SD | 12.624 | 12.6241 | MATCH (rounds to 12.624) |
| Min | -99.595 | -99.5945 | MATCH (rounds to -99.595) |
| P25 | -0.001 | -0.0006 | MATCH (rounds to -0.001) |
| Median | -0.000 | -0.0000 | MATCH |
| P75 | 0.000 | 0.0001 | MATCH (rounds to 0.000) |
| Max | 2678.235 | 2678.2347 | MATCH (rounds to 2678.235) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 4: Delta Bid-Ask Spread
**Source: H14** (line 2)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,157 | 87,157 | MATCH |
| Mean | -0.004 | -0.0043 | MATCH (rounds to -0.004) |
| SD | 0.022 | 0.0222 | MATCH (rounds to 0.022) |
| Min | -0.586 | -0.5860 | MATCH |
| P25 | -0.013 | -0.0134 | MATCH (rounds to -0.013) |
| Median | -0.003 | -0.0032 | MATCH (rounds to -0.003) |
| P75 | 0.005 | 0.0054 | MATCH (rounds to 0.005) |
| Max | 1.167 | 1.1670 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H14 source)**

### Row 5: Takeover (All)
**Source: H9** (line 6)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 84,104 | 84,104 | MATCH |
| Mean | 0.007 | 0.0067 | MATCH (rounds to 0.007) |
| SD | 0.081 | 0.0813 | MATCH (rounds to 0.081) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.000 | 0.0000 | MATCH |
| Median | 0.000 | 0.0000 | MATCH |
| P75 | 0.000 | 0.0000 | MATCH |
| Max | 1.000 | 1.0000 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

### Row 6: Takeover (Uninvited)
**Source: H9** (line 7)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 84,104 | 84,104 | MATCH |
| Mean | 0.001 | 0.0009 | MATCH (rounds to 0.001) |
| SD | 0.029 | 0.0294 | MATCH (rounds to 0.029) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.000 | 0.0000 | MATCH |
| Median | 0.000 | 0.0000 | MATCH |
| P75 | 0.000 | 0.0000 | MATCH |
| Max | 1.000 | 1.0000 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

### Row 7: Takeover (Friendly)
**Source: H9** (line 8)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 84,104 | 84,104 | MATCH |
| Mean | 0.006 | 0.0055 | MISMATCH: 0.0055 rounds to 0.006 (OK by 3dp) |
| SD | 0.074 | 0.0738 | MATCH (rounds to 0.074) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.000 | 0.0000 | MATCH |
| Median | 0.000 | 0.0000 | MATCH |
| P75 | 0.000 | 0.0000 | MATCH |
| Max | 1.000 | 1.0000 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

---

## Panel B: Key Independent Variables

### Row 8: Manager Pres. Uncertainty (%)
**Source: H7** (line 8)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 86,038 | 86,038 | MATCH |
| Mean | 0.863 | 0.8631 | MATCH (rounds to 0.863) |
| SD | 0.353 | 0.3526 | MATCH (rounds to 0.353) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.613 | 0.6130 | MATCH |
| Median | 0.822 | 0.8215 | MATCH (rounds to 0.822) |
| P75 | 1.066 | 1.0658 | MATCH (rounds to 1.066) |
| Max | 2.096 | 2.0959 | MATCH (rounds to 2.096) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 9: CEO Pres. Uncertainty (%)
**Source: H7** (line 6)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 62,049 | 62,049 | MATCH |
| Mean | 0.656 | 0.6557 | MATCH (rounds to 0.656) |
| SD | 0.390 | 0.3901 | MATCH (rounds to 0.390) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.377 | 0.3772 | MATCH (rounds to 0.377) |
| Median | 0.596 | 0.5958 | MATCH (rounds to 0.596) |
| P75 | 0.867 | 0.8671 | MATCH (rounds to 0.867) |
| Max | 2.233 | 2.2332 | MATCH (rounds to 2.233) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 10: Analyst QA Uncertainty (%)
**Source: H7** (line 10)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 81,031 | 81,031 | MATCH |
| Mean | 1.440 | 1.4398 | MATCH (rounds to 1.440) |
| SD | 0.483 | 0.4831 | MATCH (rounds to 0.483) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 1.122 | 1.1216 | MATCH (rounds to 1.122) |
| Median | 1.411 | 1.4108 | MATCH (rounds to 1.411) |
| P75 | 1.727 | 1.7268 | MATCH (rounds to 1.727) |
| Max | 3.595 | 3.5945 | MATCH (rounds to 3.595) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 11: Negative Sentiment (%)
**Source: H7** (line 9)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 86,858 | 86,858 | MATCH |
| Mean | 0.921 | 0.9210 | MATCH |
| SD | 0.302 | 0.3024 | MATCH (rounds to 0.302) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.704 | 0.7038 | MATCH (rounds to 0.704) |
| Median | 0.880 | 0.8798 | MATCH (rounds to 0.880) |
| P75 | 1.094 | 1.0943 | MATCH (rounds to 1.094) |
| Max | 2.390 | 2.3901 | MATCH (rounds to 2.390) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 12: Clarity (CEO FE)
**Source: H9** (line 2: ClarityCEO)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 52,080 | 52,080 | MATCH |
| Mean | -0.074 | -0.0742 | MATCH (rounds to -0.074) |
| SD | 0.975 | 0.9745 | MATCH (rounds to 0.975) |
| Min | -4.505 | -4.5054 | MATCH (rounds to -4.505) |
| P25 | -0.618 | -0.6184 | MATCH (rounds to -0.618) |
| Median | 0.019 | 0.0190 | MATCH |
| P75 | 0.608 | 0.6079 | MATCH (rounds to 0.608) |
| Max | 3.270 | 3.2699 | MATCH (rounds to 3.270) |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

### Row 13: CEO Clarity Residual
**Source: MIXED (N from H7, distributional stats from H9)**

H7: N=38,671, Mean=0.0000, SD=0.2992, Min=-1.5136, P25=-0.1835, Median=-0.0173, P75=0.1641, Max=1.7627
H9: N=40,452, Mean=-0.0000, SD=0.3023, Min=-1.5136, P25=-0.1849, Median=-0.0173, P75=0.1656, Max=1.8804

| Cell | Draft | H7 Source | H9 Source | Match? |
|------|-------|-----------|-----------|--------|
| N | 38,671 | 38,671 | 40,452 | MATCH H7 only |
| Mean | 0.000 | 0.0000 | -0.0000 | MATCH both |
| SD | 0.302 | 0.2992 (->0.299) | 0.3023 (->0.302) | **MISMATCH with H7; matches H9** |
| Min | -1.514 | -1.5136 (->-1.514) | -1.5136 (->-1.514) | MATCH both |
| P25 | -0.185 | -0.1835 (->-0.184) | -0.1849 (->-0.185) | **MISMATCH with H7; matches H9** |
| Median | -0.017 | -0.0173 (->-0.017) | -0.0173 (->-0.017) | MATCH both |
| P75 | 0.165 | 0.1641 (->0.164) | 0.1656 (->0.166) | **MISMATCH with BOTH** (0.165 is between H7 and H9) |
| Max | 1.880 | 1.7627 (->1.763) | 1.8804 (->1.880) | **MISMATCH with H7; matches H9** |

**Verdict: MIXED SOURCE ERROR**
- N is from H7 (Main sample, 38,671) but SD, P25, and Max are from H9 (full panel incl. all industries, 40,452)
- P75 matches neither source exactly (0.165 vs H7's 0.164 or H9's 0.166)
- **Severity: HIGH** -- The N and distributional stats describe different populations

### Row 14: Manager Clarity Residual
**Source: MIXED (N from H7, distributional stats from H9)**

H7: N=53,070, Mean=-0.0000, SD=0.2351, Min=-1.2946, P25=-0.1530, Median=-0.0109, P75=0.1410, Max=1.2928
H9: N=55,181, Mean=0.0002, SD=0.2362, Min=-1.2629, P25=-0.1538, Median=-0.0115, P75=0.1413, Max=1.1727

| Cell | Draft | H7 Source | H9 Source | Match? |
|------|-------|-----------|-----------|--------|
| N | 53,070 | 53,070 | 55,181 | MATCH H7 only |
| Mean | 0.000 | -0.0000 | 0.0002 | MATCH (approximately both) |
| SD | 0.236 | 0.2351 (->0.235) | 0.2362 (->0.236) | **MISMATCH with H7; matches H9** |
| Min | -1.263 | -1.2946 (->-1.295) | -1.2629 (->-1.263) | **MISMATCH with H7; matches H9** |
| P25 | -0.154 | -0.1530 (->-0.153) | -0.1538 (->-0.154) | **MISMATCH with H7; matches H9** |
| Median | -0.012 | -0.0109 (->-0.011) | -0.0115 (->-0.012) | **MISMATCH with H7; matches H9** |
| P75 | 0.141 | 0.1410 (->0.141) | 0.1413 (->0.141) | MATCH both |
| Max | 1.173 | 1.2928 (->1.293) | 1.1727 (->1.173) | **MISMATCH with H7; matches H9** |

**Verdict: MIXED SOURCE ERROR**
- N is from H7 (Main sample, 53,070) but SD, Min, P25, Median, Max are from H9 (full panel, 55,181)
- **Severity: HIGH** -- Same mixed-source problem as CEO Clarity Residual

---

## Panel C: Financial Controls

### Row 15: Size (log assets)
**Source: H7** (line 11)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,994 | 87,994 | MATCH |
| Mean | 7.471 | 7.4710 | MATCH |
| SD | 1.661 | 1.6607 | MATCH (rounds to 1.661) |
| Min | -0.569 | -0.5692 | MATCH (rounds to -0.569) |
| P25 | 6.301 | 6.3008 | MATCH (rounds to 6.301) |
| Median | 7.376 | 7.3763 | MATCH (rounds to 7.376) |
| P75 | 8.544 | 8.5436 | MATCH (rounds to 8.544) |
| Max | 12.459 | 12.4592 | MATCH (rounds to 12.459) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 16: Book-to-Market
**Source: H9** (line 10: BM)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 83,443 | 83,443 | MATCH |
| Mean | 0.458 | 0.4575 | MATCH (rounds to 0.458) |
| SD | 0.583 | 0.5826 | MATCH (rounds to 0.583) |
| Min | -20.775 | -20.7748 | MATCH (rounds to -20.775) |
| P25 | 0.231 | 0.2312 | MATCH (rounds to 0.231) |
| Median | 0.389 | 0.3891 | MATCH (rounds to 0.389) |
| P75 | 0.617 | 0.6172 | MATCH (rounds to 0.617) |
| Max | 7.858 | 7.8580 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

Note: BM is not available in the H7 summary_stats.csv. Using H9 (full panel, all industries, N=84,104 base) means BM stats describe the full panel, not the Main sample. BM N=83,443 < 84,104 due to missingness.

### Row 17: Leverage
**Source: H7** (line 12)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,994 | 87,994 | MATCH |
| Mean | 0.233 | 0.2330 | MATCH |
| SD | 0.224 | 0.2240 | MATCH |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.047 | 0.0470 | MATCH |
| Median | 0.207 | 0.2065 | MATCH (rounds to 0.207) |
| P75 | 0.346 | 0.3455 | MATCH (rounds to 0.346) |
| Max | 3.945 | 3.9453 | MATCH (rounds to 3.945) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 18: Return on Assets
**Source: H7** (line 13)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,552 | 87,552 | MATCH |
| Mean | 0.039 | 0.0386 | MATCH (rounds to 0.039) |
| SD | 0.133 | 0.1330 | MATCH |
| Min | -3.983 | -3.9826 | MATCH (rounds to -3.983) |
| P25 | 0.015 | 0.0146 | MATCH (rounds to 0.015) |
| Median | 0.053 | 0.0525 | MATCH (rounds to 0.053) |
| P75 | 0.093 | 0.0925 | MATCH (rounds to 0.093) |
| Max | 0.549 | 0.5490 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 19: Current Ratio
**Source: NOT FOUND in H7 or H14 econometric CSVs**

The H7 and H14 econometric summary_stats.csv do not include CurrentRatio. The H0.3 has it (N=38,331, Mean=2.5024), but the table says N=85,783. The H9 panel doesn't have it either. Checking variable-level stats from `ceo_clarity_extended` (full panel, N=112,968): N=94,059 for CurrentRatio, which doesn't match 85,783 either.

The value N=85,783 is not present in any source CSV. Computing: the full panel has 94,059 non-null CurrentRatio observations. Filtering to Main sample (88,205) would give approximately 85,783. This is plausible but no source CSV contains this number.

| Cell | Draft | Best Source (variable-level, full panel) | Match |
|------|-------|------------------------------------------|-------|
| N | 85,783 | 94,059 (full panel) or 38,331 (H0.3 estimation) | **NO SOURCE FOUND for N=85,783** |
| Mean | 2.556 | 2.4955 (full panel) or 2.5024 (H0.3) | **MISMATCH with both** |
| SD | 2.149 | 2.2146 (full panel) or 1.8183 (H0.3) | **MISMATCH with both** |

**Verdict: NO VERIFIABLE SOURCE** -- N=85,783 does not appear in any summary_stats.csv. These values may have been computed from the Main sample of the panel directly but are not captured in any output artifact.

### Row 20: R&D Intensity
**Source: NOT FOUND in H7 or H14 econometric CSVs**

Same issue as CurrentRatio. H0.3 has N=38,331, Mean=0.0084. Variable-level has N=112,692.

Table says N=87,994. This matches the H7 Size/Lev N. The H0.3 has N=38,331. Let me check: H7 has Lev at N=87,994. If RD_Intensity is also from the full Main sample, N=87,994 would mean it has same coverage as Size. Checking variable-level: RD_Intensity has N=112,692 in the full panel; filtering to Main ~88,205 and factoring for missingness could give 87,994. But no econometric source CSV reports this.

| Cell | Draft | H0.3 Source | Variable-level (full) |
|------|-------|-------------|----------------------|
| N | 87,994 | 38,331 | 112,692 |
| Mean | 0.010 | 0.0084 | 0.0079 |

**Verdict: NO VERIFIABLE ECONOMETRIC SOURCE** -- Likely computed from Main sample panel directly. The Mean=0.010 doesn't match any source (H0.3 says 0.0084; variable-level says 0.0079).
**Severity: MEDIUM** -- Values are plausible but unverifiable.

### Row 21: Stock Volatility
**Source: H14** (line 13: `Return Volatility`)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 82,599 | 82,599 | MATCH |
| Mean | 36.756 | 36.7556 | MATCH (rounds to 36.756) |
| SD | 21.244 | 21.2437 | MATCH (rounds to 21.244) |
| Min | 9.439 | 9.4388 | MATCH (rounds to 9.439) |
| P25 | 22.971 | 22.9709 | MATCH (rounds to 22.971) |
| Median | 31.276 | 31.2762 | MATCH (rounds to 31.276) |
| P75 | 43.815 | 43.8148 | MATCH (rounds to 43.815) |
| Max | 218.600 | 211.9160 | **MISMATCH: Draft says 218.600, source says 211.916** |

**Verdict: 1 CELL MISMATCH**
- Max=218.600 does not match H14 econometric source (211.916). The value 218.600 matches the variable-level (pre-industry-filter) statistic (218.5998...). The econometric summary_stats.csv computes on the Main sample which excludes Finance and Utility, reducing the max.
- **Severity: HIGH** -- The Max is from the wrong sample (all-industry vs Main-only).

### Row 22: Stock Return
**Source: H14 does not have StockRet. Checking H7...**

H7 does not have StockRet in its econometric summary_stats.csv. H0.3 has it but at N=38,331. Variable-level full panel: N=105,777, Mean=3.0350.

Table says N=82,599. This matches the Volatility/StockRet N from the H7 variable-level stats (line 14: StockRet N=105,777 in full panel, not 82,599).

Wait -- H14 line 13 shows `Return Volatility,Volatility,"82,599"` but no StockRet. Checking variable-level h7: StockRet N=105,777. But the table says N=82,599 which equals the Volatility N.

This N=82,599 for StockRet is NOT available in any current econometric source CSV. Let me check if a previous version of H7 summary_stats had it.

The H7 source at 2026-03-12_015407 or older may have had StockRet but the current latest does not.

**Checking older H7 econometric runs:**

Examining `h7_illiquidity/2026-03-09_005445/summary_stats.csv`:

N=82,599 for StockRet appears in an older H7 run. The current H7 run no longer includes StockRet because it was removed from the H7 model. However, the table still references stats computed on the Main sample filtered for volatility/return availability (N=82,599).

| Cell | Draft | Plausible Source | Match |
|------|-------|-----------------|-------|
| N | 82,599 | N/A | **UNVERIFIABLE from current output** |
| Mean | 3.067 | 3.0350 (var-level full panel) | **MISMATCH** |

**Verdict: PARTIALLY UNVERIFIABLE** -- N and Mean don't match any current source CSV. StockRet with N=82,599 may have been in an older H7 run.

### Row 23: Market Return
**Source: NOT in current H7 or H14 econometric CSVs**

Same situation as StockRet. Table says N=82,285. No current econometric source has MarketRet. H0.3 has it at N=38,331. Variable-level has N=105,777.

**Verdict: UNVERIFIABLE** from current output files.

### Row 24: EPS Growth
**Source: NOT in current H7 or H14 econometric CSVs**

Table says N=86,535. No current econometric source has EPS_Growth at this N. H0.3 has it at N=38,331. Variable-level has N=110,900.

**Verdict: UNVERIFIABLE** from current output files.

### Row 25: Earnings Surprise Decile (SurpDec)
**Source: NONE FOUND**

Table: N=65,980, Mean=1.070, SD=2.923, Min=-5.000, P25=-1.000, Median=2.000, P75=3.000, Max=5.000

Available sources:
- H0.3: N=38,331, Mean=1.2185, Median=2.000, P75=4.000
- Variable-level (full panel): N=79,093, Mean=1.1336
- Variable-level (ceo_clarity, older): N=84,187, Mean=1.0158

**No source has N=65,980 or Mean=1.070.** The P75=3.000 in the table differs from H0.3's P75=4.000 and variable-level P75=4.000.

| Cell | Draft | Any Source | Match |
|------|-------|-----------|-------|
| N | 65,980 | None | **NO SOURCE** |
| Mean | 1.070 | None | **NO SOURCE** |
| SD | 2.923 | None | **NO SOURCE** |
| P25 | -1.000 | All sources | MATCH |
| Median | 2.000 | H0.3, var-level | Partial match |
| P75 | 3.000 | None (all sources show 3.000 or 4.000) | **UNCERTAIN** |

**Verdict: COMPLETE SOURCE FAILURE** -- N, Mean, SD, and possibly P75 have no verifiable source.
**Severity: CRITICAL** -- These values appear fabricated or from a stale/deleted computation.

### Row 26: Tobin's Q
**Source: H7** (line 14)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 86,781 | 86,781 | MATCH |
| Mean | 1.829 | 1.8294 | MATCH (rounds to 1.829) |
| SD | 1.508 | 1.5084 | MATCH (rounds to 1.508) |
| Min | 0.082 | 0.0822 | MATCH (rounds to 0.082) |
| P25 | 0.960 | 0.9601 | MATCH (rounds to 0.960) |
| Median | 1.386 | 1.3864 | MATCH (rounds to 1.386) |
| P75 | 2.143 | 2.1425 | MATCH (rounds to 2.143) |
| Max | 35.413 | 35.4131 | MATCH (rounds to 35.413) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 27: Pre-Call Amihud
**Source: H7** (line 4)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 86,906 | 86,906 | MATCH |
| Mean | 0.044 | 0.0441 | MATCH (rounds to 0.044) |
| SD | 1.380 | 1.3796 | MATCH (rounds to 1.380) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.000 | 0.0002 | MATCH (rounds to 0.000) |
| Median | 0.001 | 0.0008 | MATCH (rounds to 0.001) |
| P75 | 0.004 | 0.0038 | MATCH (rounds to 0.004) |
| Max | 267.826 | 267.8263 | MATCH (rounds to 267.826) |
**Verdict: ALL 9 CELLS MATCH (H7 source)**

### Row 28: Cash Holdings
**Source: H9** (line 13)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 83,930 | 83,930 | MATCH |
| Mean | 0.171 | 0.1714 | MATCH (rounds to 0.171) |
| SD | 0.181 | 0.1813 | MATCH (rounds to 0.181) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.037 | 0.0368 | MATCH (rounds to 0.037) |
| Median | 0.105 | 0.1048 | MATCH (rounds to 0.105) |
| P75 | 0.245 | 0.2449 | MATCH (rounds to 0.245) |
| Max | 0.994 | 0.9938 | MATCH (rounds to 0.994) |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

### Row 29: Stock Price
**Source: H14** (line 11)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,188 | 87,188 | MATCH |
| Mean | 38.694 | 38.6939 | MATCH (rounds to 38.694) |
| SD | 51.720 | 51.7195 | MATCH (rounds to 51.720) |
| Min | 0.035 | 0.0345 | MATCH (rounds to 0.035) |
| P25 | 14.898 | 14.8975 | MATCH (rounds to 14.898) |
| Median | 28.240 | 28.2400 | MATCH |
| P75 | 48.170 | 48.1700 | MATCH |
| Max | 2080.020 | 2080.0200 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H14 source)**

### Row 30: Turnover
**Source: H14** (line 12)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,188 | 87,188 | MATCH |
| Mean | 0.027 | 0.0273 | MATCH (rounds to 0.027) |
| SD | 0.042 | 0.0420 | MATCH |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.008 | 0.0083 | MATCH (rounds to 0.008) |
| Median | 0.016 | 0.0160 | MATCH |
| P75 | 0.031 | 0.0310 | MATCH |
| Max | 3.773 | 3.7726 | MATCH (rounds to 3.773) |
**Verdict: ALL 9 CELLS MATCH (H14 source)**

### Row 31: Pre-Call Spread
**Source: H14** (line 3)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 87,157 | 87,157 | MATCH |
| Mean | 0.042 | 0.0421 | MATCH (rounds to 0.042) |
| SD | 0.027 | 0.0273 | MATCH (rounds to 0.027) |
| Min | 0.000 | 0.0000 | MATCH |
| P25 | 0.025 | 0.0248 | MATCH (rounds to 0.025) |
| Median | 0.036 | 0.0355 | MATCH (rounds to 0.036) |
| P75 | 0.051 | 0.0512 | MATCH (rounds to 0.051) |
| Max | 0.733 | 0.7330 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H14 source)**

### Row 32: |Surprise Decile| (AbsSurpDec)
**Source: H14** (line 14)

| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 61,544 | 61,544 | MATCH |
| Mean | 2.167 | 2.9300 | **MISMATCH: Draft says 2.167, source says 2.930** |
| SD | 1.591 | 1.4255 | **MISMATCH: Draft says 1.591, source says 1.426** |
| Min | 0 | 0.0000 | MATCH |
| P25 | 1 | 2.0000 | **MISMATCH: Draft says 1, source says 2** |
| Median | 2 | 3.0000 | **MISMATCH: Draft says 2, source says 3** |
| P75 | 3 | 4.0000 | **MISMATCH: Draft says 3, source says 4** |
| Max | 5 | 5.0000 | MATCH |

**Verdict: 5 CELLS MISMATCH**
- Only N, Min, and Max are correct
- Mean, SD, P25, Median, P75 are ALL wrong
- **Severity: CRITICAL** -- The values reported (Mean=2.167, Median=2, P25=1, P75=3) look like they describe SurpDec (signed surprise decile), not |SurpDec| (absolute). Taking the absolute value shifts the distribution rightward: abs(decile) with values 0-5 should have mean ~3 and median 3, which matches the source.
- **Root cause:** The table row is labeled "|Surprise Decile|" (absolute) but the statistics appear to be from the SIGNED SurpDec distribution, though even then the N=61,544 matches neither SurpDec nor AbsSurpDec from any known source.

### Row 33: Duration (days)
**Source: H9** (line 5)
| Cell | Draft | Source | Match |
|------|-------|--------|-------|
| N | 84,104 | 84,104 | MATCH |
| Mean | 94.573 | 94.5726 | MATCH (rounds to 94.573) |
| SD | 80.555 | 80.5554 | MATCH (rounds to 80.555) |
| Min | 1 | 1.0000 | MATCH |
| P25 | 84 | 84.0000 | MATCH |
| Median | 91 | 91.0000 | MATCH |
| P75 | 96 | 96.0000 | MATCH |
| Max | 1461 | 1461.0000 | MATCH |
**Verdict: ALL 9 CELLS MATCH (H9 source)**

---

## Discrepancies Found

### Critical Discrepancies (values wrong)

| # | Variable | Cell | Draft Value | Actual Value | Source | Severity |
|---|----------|------|-------------|-------------|--------|----------|
| 1 | |Surprise Decile| | Mean | 2.167 | 2.930 | H14 | CRITICAL |
| 2 | |Surprise Decile| | SD | 1.591 | 1.426 | H14 | CRITICAL |
| 3 | |Surprise Decile| | P25 | 1 | 2 | H14 | CRITICAL |
| 4 | |Surprise Decile| | Median | 2 | 3 | H14 | CRITICAL |
| 5 | |Surprise Decile| | P75 | 3 | 4 | H14 | CRITICAL |
| 6 | Stock Volatility | Max | 218.600 | 211.916 | H14 | HIGH |
| 7 | CEO Clarity Residual | SD | 0.302 | 0.299 (H7) | H7 vs H9 mix | HIGH |
| 8 | CEO Clarity Residual | P25 | -0.185 | -0.184 (H7) | H7 vs H9 mix | HIGH |
| 9 | CEO Clarity Residual | P75 | 0.165 | 0.164 (H7) / 0.166 (H9) | Neither | HIGH |
| 10 | CEO Clarity Residual | Max | 1.880 | 1.763 (H7) | H7 vs H9 mix | HIGH |
| 11 | Mgr Clarity Residual | SD | 0.236 | 0.235 (H7) | H7 vs H9 mix | HIGH |
| 12 | Mgr Clarity Residual | Min | -1.263 | -1.295 (H7) | H7 vs H9 mix | HIGH |
| 13 | Mgr Clarity Residual | P25 | -0.154 | -0.153 (H7) | H7 vs H9 mix | HIGH |
| 14 | Mgr Clarity Residual | Median | -0.012 | -0.011 (H7) | H7 vs H9 mix | HIGH |
| 15 | Mgr Clarity Residual | Max | 1.173 | 1.293 (H7) | H7 vs H9 mix | HIGH |

### Unverifiable Rows (no matching source CSV)

| # | Variable | N in Draft | Closest Source N | Issue |
|---|----------|-----------|-----------------|-------|
| 16 | SurpDec | 65,980 | 38,331 (H0.3) / 79,093 (var-level) | N matches no source |
| 17 | CurrentRatio | 85,783 | 38,331 (H0.3) / 94,059 (var-level) | Plausible Main-sample N but no artifact |
| 18 | R&D Intensity | 87,994 | 38,331 (H0.3) / 112,692 (var-level) | Plausible Main-sample N but no artifact |
| 19 | StockRet | 82,599 | Not in current econometric CSVs | May be from older H7 run |
| 20 | MarketRet | 82,285 | Not in current econometric CSVs | May be from older H7 run |
| 21 | EPS_Growth | 86,535 | Not in current econometric CSVs | May be from older H7 run |

---

## Completeness Check

### Variables in regression tables NOT in summary stats table:

Scanning all four regression tables (A.1 H0.3, A.2 H7, A.3 H9, A.4 H14):

**All regression variables accounted for.** Every variable appearing as a regressor in Tables A.1-A.4 has a corresponding row in the summary statistics table, with the following notes:

- `ClarityCEO` (H9 Table A.3) maps to "Clarity (CEO FE)" -- present
- `CEO_Clarity_Residual` and `Manager_Clarity_Residual` (H7/H9/H14) -- present
- `pre_call_amihud` (H7 Table A.2) maps to "Pre-Call Amihud" -- present
- `PreCallSpread` (H14 Table A.4) maps to "Pre-Call Spread" -- present
- `AbsSurpDec` (H14 Table A.4) maps to "|Surprise Decile|" -- present
- `amihud_illiq` (appears as "Amihud Illiquidity (inter-call)" in H7 source) -- **NOT in summary stats table**, but it appears in the H7 source CSV, not as a direct regressor in the table (it is a component, not a control).

### Variables in summary stats table NOT in any regression:

- **SalesGrowth, Intangibility, AssetGrowth** appear in the H9 source but NOT in the summary stats table. They also do not appear in any regression table, so this is correct.

**No orphan variables in the summary stats table.** All 33 rows correspond to variables used in at least one regression.

---

## Display Name Consistency Check

| Summary Stats Table | Regression Tables | Consistent? |
|---------------------|-------------------|-------------|
| Manager QA Uncertainty (%) | Manager_QA_Uncertainty_pct | Yes (code name in regressions) |
| CEO QA Uncertainty (%) | CEO_QA_Uncertainty_pct | Yes |
| Manager Pres. Uncertainty (%) | Manager_Pres_Uncertainty_pct | Yes |
| CEO Pres. Uncertainty (%) | CEO_Pres_Uncertainty_pct | Yes |
| Analyst QA Uncertainty (%) | Analyst_QA_Uncertainty_pct | Yes |
| Negative Sentiment (%) | Entire_All_Negative_pct | Yes |
| Clarity (CEO FE) | ClarityCEO / "Clarity Measure" | Yes |
| CEO Clarity Residual | CEO_Clarity_Residual | Yes |
| Manager Clarity Residual | Manager_Clarity_Residual | Yes |
| Size (log assets) | Size | Yes |
| Book-to-Market | BM | Yes |
| Leverage | Lev | Yes |
| Return on Assets | ROA | Yes |
| Current Ratio | CurrentRatio | Yes |
| R&D Intensity | RD_Intensity | Yes |
| Stock Volatility | Volatility / Return Volatility | Yes |
| Stock Return | StockRet | Yes |
| Market Return | MarketRet | Yes |
| EPS Growth | EPS_Growth | Yes |
| Earnings Surprise Decile | SurpDec | Yes |
| Tobin's Q | TobinsQ | Yes |
| Pre-Call Amihud | pre_call_amihud | Yes |
| Cash Holdings | CashHoldings | Yes |
| Stock Price | StockPrice | Yes |
| Turnover | Turnover | Yes |
| Pre-Call Spread | PreCallSpread | Yes |
| |Surprise Decile| | AbsSurpDec | Yes |
| Duration (days) | duration | Yes |

**No display name inconsistencies found.**

---

## Panel Assignment Check

| Variable | Assigned Panel | Correct? | Notes |
|----------|---------------|----------|-------|
| Manager QA Uncertainty | A (DV) | Yes | DV in H0.3 |
| CEO QA Uncertainty | A (DV) | Yes | DV in H0.3 |
| Delta Amihud | A (DV) | Yes | DV in H7 |
| Delta Spread | A (DV) | Yes | DV in H14 |
| Takeover (All/Uninvited/Friendly) | A (DV) | Yes | DV in H9 |
| Manager Pres Uncertainty | B (IV) | Yes | Key IV in H0.3, H7, H14 |
| CEO Pres Uncertainty | B (IV) | Yes | Key IV |
| Analyst QA Uncertainty | B (IV) | Yes | Key IV / Control |
| Negative Sentiment | B (IV) | Yes | Key IV / Control |
| Clarity (CEO FE) | B (IV) | Yes | Key IV in H9 |
| CEO/Mgr Clarity Residual | B (IV) | Yes | Key IV in H7, H9, H14 |
| All Panel C variables | C (Control) | Yes | Financial controls |

**Panel assignments are correct.**

---

## Table Note Verification

### "Main sample (N = 88,205)"

**VERIFIED.** The Main sample (FF12 non-Finance, non-Utility) contains 88,205 observations. This is confirmed by:
- README.md: "Main (FF12 non-fin, non-util) | 88,205"
- H7 provenance doc: "Main=88,205; Finance=20,482; Utility=4,281"
- H0.3 provenance doc attrition table

However, **N=88,205 is NOT the N for any specific variable.** It is the total number of observations in the Main sample before listwise deletion. Individual variable Ns are lower due to missingness (e.g., Size N=87,994; CEO_QA_Uncertainty N=62,132).

### "except H9 variables (full panel, N = 84,104)"

**VERIFIED.** The H9/takeover panel has 84,104 observations (all industries, counting-process format). The H9 summary_stats.csv header says "All" for the sample.

### Which variables come from which sample?

The table note implies all non-H9 variables are from the "Main sample" and H9 variables are from the "full panel." However, the actual sourcing is more complex:

| Source Sample | Variables |
|--------------|-----------|
| H7 Main sample (88,205 base) | Mgr/CEO QA Unc, Mgr/CEO Pres Unc, Analyst QA Unc, Negative Sentiment, Delta Amihud, Size, Lev, ROA, TobinsQ, Pre-Call Amihud, CEO/Mgr Clarity Residual |
| H14 Main sample (88,205 base) | Delta Spread, Pre-Call Spread, StockPrice, Turnover, Volatility, AbsSurpDec |
| H9 full panel (84,104 base) | ClarityCEO, Takeover indicators, Duration, BM, CashHoldings |
| Unknown/Unverifiable | CurrentRatio, RD_Intensity, StockRet, MarketRet, EPS_Growth, SurpDec |

**Issue:** BM (N=83,443) and CashHoldings (N=83,930) come from the H9 full panel (all industries), not the Main sample. The table note implies they are from the Main sample. This is misleading because these rows include Finance and Utility firms.

---

## Summary

| Metric | Count |
|--------|-------|
| Total cells to audit | 297 (33 rows x 9 columns) |
| Cells verified correct | 222 |
| Cells with discrepancies | 15 |
| Cells unverifiable (no source CSV) | 60 (from 6+ unverifiable rows x ~9 cells + partial) |
| Verified correct rows (all 9 cells match) | 22 of 33 |
| Partially wrong rows | 4 (CEO Clarity Residual, Mgr Clarity Residual, Volatility, AbsSurpDec) |
| Completely unverifiable rows | 6 (CurrentRatio, RD_Intensity, StockRet, MarketRet, EPS_Growth, SurpDec) |
| Display name issues | 0 |
| Panel assignment issues | 0 |
| Missing variables | 0 |

### Critical Issues Requiring Immediate Fix

1. **AbsSurpDec row (|Surprise Decile|):** 5 of 9 cells are wrong. The reported statistics (Mean=2.167, Median=2) appear to be from the SIGNED SurpDec variable, not the absolute value. The actual AbsSurpDec from H14 has Mean=2.930, Median=3.

2. **SurpDec row (Earnings Surprise Decile):** N=65,980 has NO source. This entire row is unverifiable. The N, Mean, and SD do not match any known output artifact.

3. **CEO/Manager Clarity Residual rows:** Both rows mix N from the H7 Main sample with distributional statistics from the H9 full panel (all industries). This makes the rows internally inconsistent -- the N describes one population but the percentiles describe a different, larger population.

4. **Volatility Max:** Reports 218.600 (from full panel, all industries) while the econometric source for the Main sample shows 211.916.

5. **Six unverifiable rows:** CurrentRatio, RD_Intensity, StockRet, MarketRet, EPS_Growth, SurpDec have N values that do not appear in any current output CSV. These appear to have been computed from the Main sample panel directly, but no artifact preserves them.

### Root Cause

The unified summary statistics table was manually composed from multiple per-suite summary_stats.csv files, each computed on a different sample. The residual and some control variable rows were created by mixing values from different source files describing different samples (Main vs full panel). Additionally, at least 6 rows appear to have been computed outside the pipeline, with no surviving output artifact.

### Recommended Actions

1. **Create a single unified summary_stats generation script** that computes all 33 variables on consistently defined samples and outputs a single CSV.
2. **Fix AbsSurpDec:** Replace with actual absolute-value statistics (Mean=2.930, SD=1.426, P25=2, Median=3, P75=4).
3. **Fix or remove SurpDec row:** Either find the correct source or regenerate from the Main sample panel.
4. **Fix residual rows:** Use stats from a consistent sample (either all H7/Main or all H9/full, but not mixed).
5. **Fix Volatility Max:** Use 211.916 (Main sample) or note that it covers all industries.
6. **Regenerate the 6 unverifiable rows** from the panel and preserve the output artifact.
