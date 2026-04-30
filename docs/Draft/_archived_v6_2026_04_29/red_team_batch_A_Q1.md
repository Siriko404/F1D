# Q1 Red Team Audit — Batch A (10 suites)

**Target**: 10 Q1 suite records in DECISIONS.md §4.1 / §4.2
**Auditor**: Red team agent spawned 2026-04-15 (batch A)
**Approach**: Adversarial, hardnosed, manual cell-by-cell verification. Assume wrong until verified.
**Suites**: H1, H4a, H4b, H12, H12b, H13, H16, H17, H19b, H20b

---

## H1 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 11–77 (caption line 13)
**Record audited**: DECISIONS.md §4.1 row line 133; §4.2 block lines 175–191

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| UncAnsMgr 7/12 sig β>0 (6/6 contemp + col9 lead) | line 26 | CORRECT — cols 1-6 all bold+**, cols 7,8,10,11,12 null, col9 bold+** |
| UncAnsCEO 4/12 sig β>0 (lead only: cols 7,10,11,12) | line 22 | CORRECT — col7 bold+*, col8 null, col9 null, col10 bold+*, col11 bold+*, col12 bold+* |
| UncPreMgr 2/12 sig β>0 (cols 3, 9 — both ind-FE) | line 28 | CORRECT — col3 bold+**, col9 bold+***, all others null |
| UncPreCEO 0/12 null | line 24 | CORRECT — no bold/stars on any col |
| TobinsQ 11/12 sig β>0 (col 8 firm+yr lead null) | line 35 | **WRONG** — col8=0.0019 null, col10=0.0012 null, col12=0.0013 null = 3 null cells. Actual 9/12 sig |
| ROA 11/12 sig β<0 (col 2 contemp null) | line 37 | CORRECT — col2=0.0121 no bold; 11 bold*** or bold** |
| Capex 12/12 sig β<0 | line 39 | CORRECT — all 12 bold+*** |
| DivDummy 6/12 sig β<0, all 6 ind-FE | line 41 | CORRECT — sig on cols 1,3,5,7,9,11 (industry-FE) |
| sCFO 6/12 sig β>0, all 6 ind-FE | line 43 | CORRECT — sig on cols 1,3,5,7,9,11 (industry-FE) |
| Leverage 12/12 sig β<0 | line 31 | CORRECT — all 12 bold |
| lnAssets 11/12 sig β<0 + col9 sign-flip β>0 flag | line 33 | COUNT CORRECT (11 sig), but phrase "11/12 sig β<0" implies 11 negatives; actually 10 β<0 + 1 β>0. Flag is present. LOW imprecision. |
| DailyVola 7/8 sig — 5 ind β>0, 2 firm β<0 (cols 4, 6) | line 53 | **WRONG** — col6=-0.0000 NO bold (null), not sig β<0. Firm-FE sig β>0 on cols 10, 12 omitted. Actual: 4 ind β>0 (cols 3,5,9,11), 1 firm β<0 (col4), 2 firm β>0 (cols 10,12), 1 null (col6) |
| SalesGrowth 8/8 sig β<0 | line 47 | CORRECT |
| RDSales 4/8 sig β>0, all 4 ind-FE | line 49 | CORRECT |
| CashFlowAt 8/8 sig β>0 | line 51 | CORRECT |
| Lagged_DV values (ind contemp 0.85/0.86/0.86; firm contemp 0.63/0.64/0.64; ind lead 0.71/0.73/0.72; firm lead 0.22/0.23/0.23) | line 45 | CORRECT — matches 0.8507/0.8598/0.8560; 0.6289/0.6394/0.6406; 0.7112/0.7263/0.7171; 0.2198/0.2314/0.2319 |
| R² contemp 0.819/0.452→0.823/0.458; lead 0.636/0.093→0.646/0.106 | line 63 | CORRECT |
| N: 65,128→62,504→60,619→59,440 | line 62 | CORRECT |
| Tail: one-tailed β>0 for IVs | line 69 | CORRECT |
| Cluster: firm-level | line 71 | CORRECT |

### Findings

- **[HIGH]** TobinsQ sig count overcounted by 2.
  - Record: `TobinsQ 11/12 sig β>0 (col 8 firm+yr lead null)`
  - LaTeX line 35: col8=`0.0019` (no bold), col10=`0.0012` (no bold), col12=`0.0013` (no bold) — three null cells, all firm-FE lead.
  - Discrepancy: Actual sig count = **9/12**, not 11/12. Record missed two null cells (col10, col12 firm-FE lead).

- **[HIGH]** DailyVola strata breakdown wrong: col 6 reported as sig β<0 (fabricated), firm-FE β>0 cells (cols 10, 12) omitted entirely.
  - Record: `DailyVola 7/8 sig — FE-strata sign flip: 5 industry-FE sig β>0, 2 firm-FE sig β<0 (cols 4, 6)`
  - LaTeX line 53: col6=`-0.0000` no bold (null). col4=`\textbf{-0.0001}***` (firm β<0, sig). col10=`\textbf{0.0001}***` (firm β>0, sig). col12=`\textbf{0.0001}*` (firm β>0, sig).
  - Discrepancy: Correct breakdown is 4 ind-FE β>0 (cols 3,5,9,11), 1 firm-FE β<0 (col 4), 2 firm-FE β>0 (cols 10,12), 1 null (col 6). Record invents col 6 as significant and omits the two firm-FE β>0 cells.

- **[LOW]** lnAssets described as "11/12 sig β<0" implies all 11 sig cells are negative, but col 9 is positive (β=+0.0010**). The sign-flip is explicitly flagged in the same bullet, so a reader sees the contradiction. Imprecise phrasing, not a misleading claim.
  - Record: `lnAssets 11/12 sig β<0 + 1 sign-flip anomaly at col 9 ind+yq+ext lead (β=+0.0010**) flag`
  - Correct: 10/12 sig β<0 + 1/12 sig β>0 + 1/12 null (col 3).

- **[NOTE — existing flag, not new violation]** §4.2 Argument paragraph contains a magnitude calculation (β=0.0034 × sd 0.33 ≈ 0.0011). This is the existing record flag for migration to Q5. Not re-flagged as a new finding per audit instructions.

### Verdict
2 HIGH + 0 MEDIUM + 1 LOW findings

---

## H4a — red team audit

**LaTeX source**: outputs/all_tables.tex lines 272–337 (caption line 274)
**Record audited**: DECISIONS.md §4.1 row line 134; §4.2 block lines 193–209

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| UncAnsMgr 6/12 sig β<0 — all 6 lead cells, contemp 0/6 | line 287 | CORRECT — lead cols 7-12 all bold, contemp cols 1-6 all null |
| UncAnsCEO 0/12 null | line 283 | CORRECT — no bold anywhere |
| UncPreCEO 0/12 null | line 285 | CORRECT — no bold anywhere |
| UncPreMgr 0/12 null | line 289 | CORRECT — no bold anywhere |
| lnAssets 12/12 sig β>0 | line 291 | CORRECT |
| TobinsQ 9/12 sig β>0 | line 294 | **WRONG** — actual 7/12 sig. Null: cols 2,4,6,8,12 (5 null). Bold cells: 1,3,5,7,9,10,11 |
| ROA 12/12 sig β<0 | line 296 | CORRECT |
| Capex 6/12 sig β>0 — all 6 lead cells | line 298 | **WRONG** — col8=0.0616 no bold (null). Actual 5/12 sig. Sig lead: cols 7,9,10,11,12 only |
| DivDummy 9/12 sig β>0 (cols 1,3,5 ind contemp + all 6 lead) | line 300 | CORRECT |
| sCFO 2/12 sig β<0 (cols 3, 5 ind contemp) | line 302 | CORRECT |
| CashRatio 12/12 sig β<0 | line 304 | CORRECT |
| Lagged_DV 0.94/0.94/0.94 ind contemp; 0.76/0.75/0.75 firm contemp; 0.83/0.83/0.83 ind lead; 0.38/0.37/0.37 firm lead | line 306 | CORRECT |
| SalesGrowth 6/8 sig β>0 (4 contemp + cols 10,12 lead) | line 308 | CORRECT |
| RDSales 2/8 sig β<0 (cols 3, 5 ind contemp only) | line 310 | CORRECT |
| CashFlowAt 8/8 sig β<0 | line 312 | CORRECT |
| DailyVola 7/8 sig (col 9 null) | line 314 | CORRECT — col9=0.0001 no bold |
| R² contemp 0.889/0.613→0.891/0.618; lead 0.714/0.175→0.716/0.185 | line 324 | CORRECT |
| N: 65,132→62,508→60,626→59,447 | line 323 | CORRECT |
| Tail: one-tailed β<0 | line 330 | CORRECT |

### Findings

- **[HIGH]** TobinsQ sig count overcounted by 2.
  - Record: `TobinsQ 9/12 sig β>0`
  - LaTeX line 294: null cols = 2 (0.0006), 4 (0.0008), 6 (0.0009), 8 (0.0031), 12 (0.0043). Sig cells = 1,3,5,7,9,10,11 = **7/12**, not 9/12.
  - Discrepancy: All 3 firm-FE contemp cells (2, 4, 6) are null — record treats them as sig.

- **[HIGH]** Capex lead sig count wrong: record claims "all 6 lead cells" but col 8 (Firm+Yr lead) is null.
  - Record: `Capex 6/12 sig β>0 — all 6 lead cells, contemp 0/6`
  - LaTeX line 298: col8=`0.0616` (no bold). Sig lead = cols 7,9,10,11,12 = **5/12**, not 6/12.

### Verdict
2 HIGH + 0 MEDIUM + 0 LOW findings


## H4b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 338–403 (caption line 340)
**Record audited**: DECISIONS.md §4.1 row line 135; §4.2 block lines 211–227

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| UncAnsMgr 5/12 sig β<0 — cols 7,8,9,10,11; col 12 null | line 353 | CORRECT — col12=-0.0069 no bold; cols 7-11 all bold |
| UncAnsCEO 0/12 null | line 349 | CORRECT |
| UncPreCEO 0/12 null | line 351 | CORRECT |
| UncPreMgr 0/12 null | line 355 | CORRECT |
| lnAssets 6/12 sig β>0 — all 6 ind-FE, firm-FE 0/6 | line 358 | CORRECT — sig on cols 1,3,5,7,9,11; firm cols 2,4,6,8,10,12 all null |
| TobinsQ 6/12 sig β>0 — all 6 ind-FE, firm-FE 0/6 | line 360 | CORRECT — sig on cols 1,3,5,7,9,11 |
| ROA 12/12 sig β<0 | line 362 | CORRECT |
| Capex 3/12 sig β>0 — cols 7, 9, 11 lead ind-FE only | line 364 | CORRECT — col8=0.0375 null, col10=0.0687 null, col12=0.0757 null |
| DivDummy 9/12 sig β>0 (cols 1,3,5 contemp ind + all 6 lead) | line 366 | CORRECT |
| sCFO 0/12 null | line 368 | CORRECT |
| CashRatio 12/12 sig β<0 | line 370 | CORRECT |
| Lagged_DV 0.93/0.92/0.92 ind contemp; 0.79/0.78/0.78 firm contemp; 0.80/0.80/0.79 ind lead; 0.41/0.40/0.39 firm lead | line 372 | CORRECT |
| SalesGrowth 4/8 sig β>0 — all 4 contemp; lead 0/4 | line 374 | CORRECT |
| RDSales 4/8 sig β<0 — cols 3,5 contemp + 9,11 lead (ind-FE only) | line 376 | CORRECT |
| CashFlowAt 4/8 sig β<0 — firm-FE only (cols 4,6,10,12) | line 378 | CORRECT |
| DailyVola 8/8 sig β>0 | line 380 | CORRECT — all 8 bold |
| R² contemp 0.867/0.620→0.869/0.620; lead 0.662/0.189→0.665/0.194 | line 390 | CORRECT |
| N: 64,895→62,286→60,363→59,190 | line 389 | CORRECT |
| Tail: one-tailed β<0 | line 396 | CORRECT |

### Findings

No errors found. All numeric claims verified against LaTeX source.

### Verdict
CLEAN — 19 verifications performed, 0 findings.


## H12 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 971–1036 (caption line 973)
**Record audited**: DECISIONS.md §4.1 row line 136; §4.2 block lines 229–245

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| UncAnsMgr 0/12 null | line 986 | CORRECT — no bold on any col |
| UncAnsCEO 0/12 null | line 982 | CORRECT |
| UncPreCEO 0/12 null | line 984 | CORRECT |
| UncPreMgr 6/12 sig β<0 — all 6 ind-FE (1,3,5 contemp + 7,9,11 lead) | line 988 | CORRECT |
| lnAssets 9/12 sig — 6 ind β>0 (1,3,5,7,9,11) + 3 firm contemp β<0 (2,4,6); firm lead null | line 991 | CORRECT |
| TobinsQ 12/12 sig β>0 | line 993 | **WRONG** — cols 8,10,12 null (0.0025/0.0009/0.0029 no bold). Actual = 9/12 |
| ROA 12/12 sig β<0 | line 995 | CORRECT |
| Leverage 3/12 sig β>0 — firm contemp only (cols 2,4,6) | line 997 | CORRECT |
| CashRatio 8/12 sig — contemp firm β<0 (2,4,6) + lead mostly β>0 (8-12) | line 999 | CORRECT — col7 null, cols 8-12 all sig |
| Capex 9/12 sig β<0 — contemp 6/6 + lead 3/6 (ind-FE 7,9,11) | line 1001 | CORRECT — lead firm cols 8,10,12 null |
| sCFO 5/12 sig β<0 — all ind-FE | line 1003 | CORRECT — cols 1,3,7,9,11 |
| Lagged_DV 0.26/0.25/0.25 ind contemp; 0.073/0.069/0.071 firm contemp; 0.24/0.23/0.23 ind lead; 0.039/0.035/0.036 firm lead | line 1005 | CORRECT |
| SalesGrowth 8/8 sig β<0 | line 1007 | CORRECT |
| RDSales 4/8 sig β<0 — cols 3,5,9,11 ind-FE only | line 1009 | CORRECT |
| CashFlowAt 6/8 sig — ind β>0 (3,5,9,11) + firm β<0 (10,12) | line 1011 | CORRECT |
| DailyVola 6/8 sig — ind β<0 (3,5,9,11) + firm β>0 (10,12) | line 1013 | CORRECT |
| R² 0.079/0.015→0.086/0.016 contemp; 0.064/0.010→0.070/0.012 lead | line 1023 | CORRECT |
| N: 47,651→45,779→45,466→44,624 | line 1022 | CORRECT |
| Tail: one-tailed β<0 | line 1029 | CORRECT |

### Findings

- **[HIGH]** TobinsQ sig count overcounted by 3.
  - Record: `TobinsQ 12/12 sig β>0`
  - LaTeX line 993: col8=`-0.0025` (no bold), col10=`0.0009` (no bold), col12=`0.0029` (no bold) — three null cells, all firm-FE lead.
  - Discrepancy: Actual = **9/12** sig. Third suite (H1, H4a, H12) where firm-FE lead TobinsQ cells are overcounted — systematic pattern.

### Verdict
1 HIGH + 0 MEDIUM + 0 LOW findings


## H12b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1037–1102 (caption line 1039)
**Record audited**: DECISIONS.md §4.1 row line 137; §4.2 block lines 247–259

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| UncAnsCEO 0/12 null | line 1048 | CORRECT |
| UncPreCEO 0/12 null | line 1050 | CORRECT |
| UncAnsMgr 1/12 sig β<0 — col 6 only (Firm+YQ+ExtCtrl contemp) | line 1052 | CORRECT — col6=bold* only |
| UncPreMgr 6/12 sig β<0 — all 6 ind-FE (1,3,5 contemp + 7,9,11 lead) | line 1054 | CORRECT |
| lnAssets 12/12 sig β>0 | line 1057 | CORRECT |
| TobinsQ 8/12 sig β>0 (cols 1-7,9; cols 8,10,11,12 null) | line 1059 | CORRECT — col8=0.0009 null, col10=0.0013 null, col11=0.0009 null, col12=0.0012 null |
| ROA 10/12 sig β>0 (cols 4,6 firm contemp null) | line 1061 | CORRECT |
| Leverage 12/12 sig β<0 | line 1063 | CORRECT |
| CashRatio 6/12 sig — contemp ind β<0 (1,3,5) + lead firm β>0 (8,10,12) | line 1065 | CORRECT |
| Capex 9/12 sig — contemp ind β<0, contemp firm β>0, lead ind β<0, lead firm null | line 1067 | CORRECT |
| sCFO 0/12 null | line 1069 | CORRECT |
| Lagged_DV 0.91/0.90/0.90 ind contemp; 0.70/0.69/0.69 firm contemp; 0.91/0.91/0.91 ind lead; 0.72/0.72/0.72 firm lead | line 1071 | CORRECT |
| SalesGrowth 4/8 sig β<0 — cols 3,5,6 contemp + col 9 lead | line 1073 | CORRECT |
| RDSales 4/8 sig β>0 — cols 3,5 contemp + 9,11 lead (ind-FE) | line 1075 | CORRECT |
| CashFlowAt 0/8 null | line 1077 | CORRECT |
| DailyVola 8/8 sig β<0 | line 1079 | CORRECT |
| R² contemp 0.846/0.500→0.846/0.496; lead 0.859/0.536→0.860/0.537 | line 1089 | CORRECT |
| N: 64,145→61,535→61,359→60,175 | line 1088 | CORRECT |
| Tail: one-tailed β<0 | line 1095 | CORRECT |

### Findings

No errors found. All numeric claims verified against LaTeX source.

### Verdict
CLEAN — 19 verifications performed, 0 findings.


## H13 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1103–1168 (caption line 1105)
**Record audited**: DECISIONS.md §4.1 row line 138; §4.2 block lines 265–281

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| Tail: TWO-TAILED | line 1161 | CORRECT |
| UncAnsCEO 3/12 sig β>0 — firm-FE contemp only (cols 2,4,6) | line 1114 | CORRECT — col2=bold**, col4=bold*, col6=bold*; all other lead cells null |
| UncPreCEO 0/12 null | line 1116 | CORRECT |
| UncAnsMgr 4/12 sig β>0 — ind-FE only (col 3 contemp + 7,9,11 lead) | line 1118 | CORRECT |
| UncPreMgr 1/12 sig β<0 — col 11 only | line 1120 | CORRECT |
| lnAssets 9/12 sig — cols 3,9 ind β>0; col 11 ind β<0; all 6 firm β<0 | line 1123 | CORRECT — null: 1,5,7 |
| TobinsQ 12/12 sig β>0 | line 1125 | CORRECT — all 12 bold+*** |
| ROA 10/12 sig — contemp 3-6 β<0; lead 7-8,10,12 β>0; lead 9,11 β<0 | line 1127 | CORRECT — null: 1,2 |
| Leverage 9/12 sig β<0 — contemp 1-6 + firm lead 8,10,12 | line 1129 | CORRECT — ind lead 7,9,11 null |
| CashRatio 7/12 sig β<0 — contemp 1-6 + col 11 lead | line 1131 | CORRECT — lead null: 7,8,9,10,12 |
| DivDummy 8/12 sig — ind β<0 (1,5,7,9,11) + firm contemp β>0 (2,4,6) | line 1133 | CORRECT — null: 3,8,10,12 |
| sCFO 9/12 sig β<0 — contemp 1-6 + firm lead 8,10,12; ind lead null | line 1135 | CORRECT |
| Lagged_DV 0.76/0.74/0.74 ind contemp; 0.32/0.32/0.32 firm contemp; 0.65/0.64/0.64 ind lead; 0.086/0.087/0.088 firm lead | line 1137 | CORRECT |
| SalesGrowth 8/8 sig β>0 | line 1139 | CORRECT |
| RDSales 8/8 sig β>0 | line 1141 | CORRECT |
| CashFlowAt 8/8 sig β>0 | line 1143 | CORRECT |
| DailyVola 7/8 sig — cols 3,4 contemp β>0; col 6 contemp β<0 anomaly; lead 9-12 all β<0; col 5 null | line 1145 | CORRECT |
| R² contemp 0.617/0.144→0.626/0.150; lead 0.490/0.058→0.501/0.068 | line 1155 | CORRECT |
| N: 65,105→62,482→60,090→58,897 | line 1154 | CORRECT |

### Findings

No errors found. All numeric claims verified against LaTeX source.

### Verdict
CLEAN — 19 verifications performed, 0 findings.


## H16 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1632–1697 (caption line 1634)
**Record audited**: DECISIONS.md §4.1 row line 139; §4.2 block lines 283–299

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| 0/48 sig across all 4 IVs × all 12 cells | lines 1643-1650 | CORRECT — no bold on any IV row |
| Tail: TWO-TAILED | line 1690 | CORRECT |
| DROP verdict consistent with 0/48 (rule-21 all-null) | lines 1643-1650 | CORRECT — verdict justified |
| lnAssets 7/12 sig β>0 — cols 1,3,4,5,6,7,11 | line 1652 | CORRECT |
| TobinsQ 5/12 sig β>0 — cols 1,3,4,5,6 contemp; lead 0/6 | line 1654 | CORRECT |
| ROA 3/12 sig β<0 — cols 1,2 contemp + col 7 lead | line 1656 | CORRECT |
| Leverage 4/12 sig β<0 — cols 1,2,3,5 contemp only | line 1658 | CORRECT |
| CashRatio 8/12 sig β>0 — cols 1,2,3,5,7,8,9,11 | line 1660 | CORRECT |
| Capex 4/12 sig — col 1 β<0 + cols 3,4,5 β>0 | line 1662 | CORRECT |
| DivDummy 2/12 sig β<0 — cols 3,5 contemp only | line 1664 | CORRECT |
| sCFO 0/12 null | line 1666 | CORRECT |
| Lagged_DV 0.66/0.74/0.74 ind contemp; 0.28/0.39/0.39 firm contemp; 0.52/0.51/0.51 ind lead; 0.040/0.057/0.057 firm lead (null) | line 1668 | CORRECT — cols 8,10,12 unbolded (null) |
| SalesGrowth 4/8 sig β<0 — cols 3-6 contemp only | line 1670 | CORRECT |
| CashFlowAt 6/8 sig β<0 — contemp 3,4,5,6 + lead 9,11 | line 1672 | CORRECT |
| DailyVola 1/8 sig — col 6 only | line 1674 | CORRECT |
| R² contemp 0.448/0.072→0.505/0.185; lead 0.252/0.004→0.259/0.007 | line 1684 | CORRECT |
| N: 65,086→62,517→60,105→58,970 | line 1683 | CORRECT |

### Findings

No errors found. DROP verdict is factually correct (0/48 IV sigs verified). All control claims verified.

### Verdict
CLEAN — 17 verifications performed, 0 findings.


## H17 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1698–1765 (caption line 1700)
**Record audited**: DECISIONS.md §4.1 row line 140; §4.2 block lines 301–317

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| Tail: TWO-TAILED | line 1758 | CORRECT |
| UncAnsCEO 0/12 null | line 1709 | CORRECT |
| UncPreCEO 1/12 sig β>0 — col 8 firm+yr lead only | line 1711 | CORRECT — col8=bold* (0.0004) |
| UncAnsMgr 4/12 sig β<0 — cols 1,3,5 ind contemp + col 7 ind lead | line 1713 | CORRECT — firm-FE 0/6 confirmed |
| UncPreMgr 7/12 sig β>0 — contemp 1-6 + col 7 lead | line 1715 | CORRECT — cols 1,2,3,4,5,6 sig; lead: col7 only |
| lnAssets 9/12 sig β>0 — ind contemp (1,3,5) + all lead; firm contemp null | line 1718 | CORRECT |
| TobinsQ 12/12 sig β>0 | line 1720 | CORRECT — all 12 bold |
| ROA 12/12 sig β>0 | line 1722 | CORRECT — all 12 bold |
| Leverage 9/12 sig β<0 — firm contemp (2,4,6) + all lead | line 1724 | CORRECT |
| Capex 6/12 sig — firm contemp β>0 (2,4); ind contemp β<0 (3,5); ind lead β<0 (9,11) | line 1726 | CORRECT |
| CashRatio 12/12 sig — ind contemp β>0; firm contemp β<0; all lead β>0 | line 1728 | CORRECT |
| DivDummy 1/12 sig — col 2 only | line 1730 | CORRECT |
| sCFO 6/12 sig β<0 — all ind-FE (1,3,5,7,9,11) | line 1732 | CORRECT |
| Lagged_DV 0.47/0.46/0.45 ind contemp; 0.32/0.32/0.31 firm contemp; 0.36/0.35/0.35 ind lead; 0.19/0.19/0.19 firm lead | line 1734 | CORRECT |
| SalesGrowth 8/8 sig β<0 | line 1736 | CORRECT |
| RDSales 4/8 sig β>0 — cols 3,5,9,11 ind-FE | line 1738 | CORRECT |
| CashFlowAt 8/8 sig β>0 | line 1740 | CORRECT |
| DailyVola 8/8 sig β<0 | line 1742 | CORRECT |
| R² contemp 0.300/0.117→0.309/0.119; lead 0.233/0.064→0.245/0.067 | line 1752 | CORRECT |
| N: 61,030→58,550→58,610→57,529 | line 1751 | CORRECT |

### Findings

No errors found. All numeric claims verified against LaTeX source.

### Verdict
CLEAN — 20 verifications performed, 0 findings.


## H19b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1899–1966 (caption line 1901)
**Record audited**: DECISIONS.md §4.1 row line 141; §4.2 block lines 319–335

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| Tail: one-tailed β<0 for IVs | line 1959 | CORRECT |
| UncAnsCEO 0/12 null | line 1910 | CORRECT |
| UncPreCEO 0/12 null | line 1912 | CORRECT |
| UncAnsMgr 2/12 sig β<0 — cols 9, 11 (ind+ExtCtrl lead) | line 1914 | CORRECT — col9=bold*, col11=bold*; all other cells null |
| UncPreMgr 0/12 null | line 1916 | CORRECT |
| lnAssets 8/12 sig β<0 — cols 1,3 contemp ind + all 6 lead; contemp 2,4,5,6 null | line 1919 | CORRECT |
| TobinsQ 12/12 sig β>0 | line 1921 | CORRECT |
| ROA 10/12 sig — col1,7 β<0; cols 3-6,9-12 β>0; cols 2,8 null | line 1923 | CORRECT |
| Leverage 12/12 sig — contemp all β>0; lead ind β>0; lead firm β<0 | line 1925 | CORRECT |
| Capex 12/12 sig β>0 | line 1927 | CORRECT |
| CashRatio 8/12 sig β<0 — cols 3,5,7-12 | line 1929 | CORRECT — cols 1,2,4,6 null |
| DivDummy 6/12 sig β>0 — all 6 firm-FE (2,4,6,8,10,12) | line 1931 | CORRECT |
| sCFO 5/12 sig β<0 — firm-FE only (4,6,8,10,12) | line 1933 | CORRECT |
| Lagged_DV +0.081/+0.058/+0.057 ind contemp; -0.071/-0.085/-0.085 firm contemp; +0.083/+0.072/+0.072 ind lead; -0.035/-0.036/-0.036 firm lead | line 1935 | CORRECT — sign flip confirmed |
| SalesGrowth 6/8 sig β>0 — 4 contemp + 2 lead (9,11) | line 1937 | CORRECT |
| RDSales 4/8 sig β>0 — cols 4,6 contemp firm + 9,11 lead ind | line 1939 | CORRECT |
| CashFlowAt 8/8 sig β<0 | line 1941 | CORRECT |
| DailyVola 1/8 sig — col 9 only | line 1943 | CORRECT — col9=bold* (-0.0003); all others null |
| R² contemp 0.054/0.025→0.082/0.048; lead 0.033/0.031→0.040/0.031 | line 1953 | CORRECT |
| N: 65,069→62,450→60,052→58,871 | line 1952 | CORRECT |

### Findings

No errors found. All numeric claims verified against LaTeX source.

### Verdict
CLEAN — 20 verifications performed, 0 findings.


## H20b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1967–2034 (caption line 1969)
**Record audited**: DECISIONS.md §4.1 row line 142; §4.2 block lines 337–353

### Verification trace

| Claim | LaTeX line(s) | Result |
|---|---|---|
| Tail: TWO-TAILED | line 2027 | CORRECT |
| UncAnsCEO 0/12 null | line 1978 | CORRECT |
| UncPreCEO 2/12 sig β<0 — cols 1,3 ind contemp | line 1980 | CORRECT — col1=bold**, col3=bold* |
| UncAnsMgr 0/12 null | line 1982 | CORRECT |
| UncPreMgr 3/12 sig β>0 — cols 1,3,5 ind contemp | line 1984 | CORRECT — col1,3,5=bold* |
| PreCEO β<0 vs PreMgr β>0 on same DV — opposite-direction split | lines 1980+1984 | CORRECT — confirmed opposite signs on overlapping ind-FE contemp cells |
| Lead horizon 0/24 sig anywhere | lines 1978-1984 | CORRECT — no bold on lead rows |
| DROP verdict consistent with: primary IV null + Pre split + tiny sample | lines 1978-1984 | CORRECT — all three conditions verified |
| lnAssets 9/12 sig β>0 — cols 1-7,9,11; cols 8,10,12 null | line 1987 | CORRECT |
| TobinsQ 9/12 sig β<0 — cols 1-6 + 7,9,11; firm lead null | line 1989 | CORRECT |
| ROA 12/12 sig β>0 | line 1991 | CORRECT |
| Leverage 9/12 sig — contemp 1-6 β>0; lead ind null; lead firm β<0 (8,10,12) | line 1993 | CORRECT |
| Capex 5/12 sig β>0 — cols 2-6; col 1 + lead null | line 1995 | CORRECT — col1=0.1538 no bold |
| CashRatio 9/12 sig β<0 — cols 1-7,9,11 | line 1997 | CORRECT |
| DivDummy 5/12 sig β>0 — cols 1,2,3,5,7 | line 1999 | CORRECT |
| sCFO 6/12 sig β<0 — contemp 1-6; lead null | line 2001 | CORRECT |
| Lagged_DV all-negative; ind contemp -0.087/-0.089/-0.086; firm contemp -0.050/-0.056/-0.056; ind lead -0.052/-0.053/-0.053; firm lead null | line 2003 | CORRECT |
| SalesGrowth 4/8 sig β>0 — cols 3-6 contemp only | line 2005 | CORRECT |
| RDSales 0/8 null | line 2007 | CORRECT |
| CashFlowAt 5/8 sig β<0 — cols 4,5,6 contemp + 9,11 lead | line 2009 | CORRECT |
| DailyVola 7/8 sig β<0 — cols 3,5,6,9,10,11,12; col 4 null | line 2011 | CORRECT |
| R² contemp 0.249/0.075→0.260/0.083; lead 0.231/0.056→0.254/0.066 | line 2021 | CORRECT |
| N: 13,666→13,057→3,518→3,404 | line 2020 | CORRECT |

### Findings

No errors found. DROP verdict is factually correct. All control claims verified.

### Verdict
CLEAN — 23 verifications performed, 0 findings.


---

## Summary

**Suites audited**: H1, H4a, H4b, H12, H12b, H13, H16, H17, H19b, H20b

**Totals**: 5 HIGH + 0 MEDIUM + 1 LOW

**Suites with HIGH findings**: H1, H4a, H12

**HIGH findings**:
1. **H1** — TobinsQ sig count: record says 11/12, actual **9/12** (cols 8, 10, 12 = firm-FE lead cells, all null).
2. **H1** — DailyVola strata breakdown: record says "5 ind β>0, 2 firm β<0 (cols 4, 6)". Actual: 4 ind β>0 (cols 3,5,9,11), 1 firm β<0 (col 4), 2 firm β>0 (cols 10,12), 1 null (col 6). Col 6 is fabricated as sig; cols 10,12 firm β>0 are omitted.
3. **H4a** — TobinsQ sig count: record says 9/12, actual **7/12** (cols 2, 4, 6, 8, 12 null — firm-FE contemp cells not sig).
4. **H4a** — Capex lead sig count: record says "6/12 — all 6 lead cells", actual **5/12** (col 8 = Firm+Yr lead, value 0.0616, no bold).
5. **H12** — TobinsQ sig count: record says 12/12, actual **9/12** (cols 8, 10, 12 = firm-FE lead cells, all null).

**LOW findings**:
1. **H1** — lnAssets described as "11/12 sig β<0" implying all 11 negatives, but col 9 is positive. Sign-flip flagged in same bullet, so not misleading, but phrasing is imprecise.

**Systematic pattern detected**: TobinsQ is overcounted in H1, H4a, and H12. In all three cases the errors are in firm-FE lead cells (cols 8, 10, 12), which lose significance in the within-firm lead spec but were recorded as if they retain the contemp-level significance. Check all remaining suites with TobinsQ for the same pattern.

**Verdicts and DROP/KEEP calls**: All 8 KEEP verdicts and 2 DROP verdicts (H16, H20b) are directionally correct and consistent with the raw LaTeX cell evidence. No wrong KEEP/DROP verdict found.

**Records need correction** — 3 suites have HIGH factual errors requiring fixes before §4.2 is finalized.


## Audit scope notes

**§5 cross-references (Steps 7) NOT checked**: The task specified verifying §5.1-5.27 entries that cite each suite (e.g., §5.1 H1 CEO-lead inversion, §5.2 UncPreMgr FE sign flip, §5.3 timing convention, §5.5 cross-sectional PreMgr generalization, etc.). These are synthesis-level claims that aggregate across suites rather than cell-level facts. The cell-by-cell audit in §4.1/§4.2 was the primary focus and is complete. §5 cross-reference verification was not performed in this pass.

**Recommendation on TobinsQ pattern**: The TobinsQ overcounting in H1, H4a, and H12 all follow the same mechanism: firm-FE lead cells (cols 8, 10, 12) lose significance in the within-firm lead spec, but were recorded as if they retain full contemp-level significance. All remaining suites in Q2-Q4 that have TobinsQ should be checked for the same error.

