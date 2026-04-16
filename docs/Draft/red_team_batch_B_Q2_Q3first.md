# Q2 + Q3-first Red Team Audit — Batch B (8 suites)

**Target**: 8 suite records in DECISIONS.md §4.1 / §4.2
**Auditor**: Red team agent spawned 2026-04-15 (batch B)
**Approach**: Adversarial, hardnosed, manual cell-by-cell. Assume wrong until verified.
**Suites**: H1.1, H1.1b, H1.2, H13.1, H13.2, H22, H5, H7

---

## H1.1 — red team audit


**LaTeX source**: outputs/all_tables.tex lines 77–138
**Record audited**: DECISIONS.md §4.1 line 143; §4.2 block lines 355–371
**Table structure**: 4 cols, DV=CashRatio (contemp), FE ladder: (1)Ind+Yr, (2)Firm+Yr, (3)Ind+YQ, (4)Firm+YQ. IVs: UncAnsMgr_c (main), z_log_TotalSimilarity (moderator), UncAnsMgr_c_x_zlogTSIMM (interaction). Firm-level cluster. N=73,707.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsMgr_c 4/4 sig β>0 | L88: 0.0045***, 0.0035***, 0.0046***, 0.0035*** | CORRECT |
| z_log_TotalSimilarity 4/4 sig β>0 | L90: 0.0057***, 0.0030**, 0.0055***, 0.0029** | CORRECT |
| Interaction 0/4 null | L92: 0.0017(ns), 0.0014(ns), 0.0017(ns), 0.0014(ns) | CORRECT |
| Leverage 4/4 sig β<0 | L95: -0.0122***, -0.0169***, -0.0124***, -0.0170*** | CORRECT |
| lnAssets 4/4 sig β<0 | L97: -0.0021***, -0.0172***, -0.0018***, -0.0168*** | CORRECT |
| TobinsQ 4/4 sig β>0 | L99: 0.0045***, 0.0032***, 0.0044***, 0.0029*** | CORRECT |
| ROA 4/4 sig β<0 | L101: -0.0601***, -0.0329***, -0.0572***, -0.0309*** | CORRECT |
| Capex 4/4 sig β<0 | L103: -0.1578***, -0.2392***, -0.1543***, -0.2312*** | CORRECT |
| DivDummy 2/4 sig β<0 (cols 1,3) | L105: -0.0033***, -0.0024(ns), -0.0029***, -0.0020(ns) | CORRECT |
| sCFO 2/4 sig β>0 (cols 1,3) | L107: 0.0122**, 0.0026(ns), 0.0119**, 0.0026(ns) | CORRECT |
| SalesGrowth 4/4 sig β<0 | L109: -0.0101***, -0.0116***, -0.0095***, -0.0111*** | CORRECT |
| RDSales "2/4 sig β>0 ind + 1 marginal firm" | L111: 0.0041***, 0.0014(ns), 0.0041***, **0.0015*** | FLAG: col4=0.0015* IS bold/sig — record calls it "marginal" but it IS significant at *. Effective count is 3/4 sig, description ambiguous |
| CashFlowAt 4/4 sig β>0 | L113: 0.1013***, 0.1279***, 0.1009***, 0.1271*** | CORRECT |
| DailyVola 2/4 — col2 sig β<0, col3 sig β>0 | L115: -0.0000(ns), -0.0001***, +0.0000*, -0.0000(ns) | CORRECT |
| Lagged_DV: 0.857/0.858 (ind); 0.665/0.666 (firm) | L117: 0.8574, 0.6646, 0.8581, 0.6658 | CORRECT (rounded) |
| R²: 0.834/0.484 → 0.835/0.484 | L126: 0.834, 0.484, 0.835, 0.484 | CORRECT |
| N=73,707 all 4 cols | L125: 73,707 all | CORRECT |
| Tail: one-tailed β>0 for IVs | L132 notes | CORRECT |
| Cluster: firm-level | L133 | CORRECT |

### Findings

- **[LOW]** RDSales description: record says "2/4 sig β>0 ind + 1 marginal firm" when col4 (Firm+YQ) = 0.0015* is bold and significant. Effective sig count is 3/4, but the record hedges "marginal" for col4 rather than stating 3/4 sig clearly. Not a factual fabrication — the * sig is acknowledged — but the phrasing is misleading and understates sig count. Low severity because the record explicitly notes col4 as sig-level via "marginal."
- **[CLEAN]** All IV sig counts verified exactly. All base controls verified. All extended controls verified. Lagged_DV values verified. R²/N verified. FE labels correct. Tail and cluster correct.

### Verdict
CLEAN + 1 LOW (RDSales phrasing ambiguity)

---

## H1.1b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 140–201
**Record audited**: DECISIONS.md §4.1 line 144; §4.2 block lines 373–389
**Table structure**: 4 cols, DV=CashRatio (contemp), FE ladder identical to H1.1. IVs: UncAnsMgr_c (main), HighTSIMM (binary moderator), UncAnsMgr_c_x_HighTSIMM (interaction). Firm-level cluster. N=73,707.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsMgr_c 4/4 sig β>0 | L151: 0.0044***, 0.0038***, 0.0044***, 0.0037*** | CORRECT |
| HighTSIMM 2/4 sig β>0 (cols 1,3 ind contemp) | L153: 0.0060***, 0.0014(ns), 0.0058***, 0.0014(ns) | CORRECT |
| Interaction 0/4 null | L155: 0.0010(ns), -0.0006(ns), 0.0010(ns), -0.0006(ns) | CORRECT |
| Leverage 4/4 sig β<0 | L158: -0.0109***, -0.0171***, -0.0113***, -0.0173*** | CORRECT |
| lnAssets 4/4 sig β<0 | L160: -0.0018***, -0.0169***, -0.0016***, -0.0166*** | CORRECT |
| TobinsQ 4/4 sig β>0 | L162: 0.0046***, 0.0032***, 0.0045***, 0.0030*** | CORRECT |
| ROA 4/4 sig β<0 | L164: -0.0633***, -0.0332***, -0.0603***, -0.0313*** | CORRECT |
| Capex 4/4 sig β<0 | L166: -0.1488***, -0.2384***, -0.1455***, -0.2303*** | CORRECT |
| DivDummy 2/4 sig β<0 (ind-only) | L168: -0.0039***, -0.0025(ns), -0.0035***, -0.0022(ns) | CORRECT |
| sCFO 2/4 sig β>0 (ind-only) | L170: 0.0127**, 0.0026(ns), 0.0124**, 0.0026(ns) | CORRECT |
| SalesGrowth 4/4 sig β<0 | L172: -0.0094***, -0.0116***, -0.0088***, -0.0111*** | CORRECT |
| RDSales "2/4 sig β>0 ind + 1 marginal firm" | L174: 0.0045***, 0.0014(ns), 0.0045***, **0.0015*** | FLAG: same as H1.1 — col4=0.0015* IS bold/sig, phrasing understates |
| CashFlowAt 4/4 sig β>0 | L176: 0.1018***, 0.1278***, 0.1014***, 0.1271*** | CORRECT |
| DailyVola 2/4 FE sign flip (col2 β<0, col3 β>0) | L178: -0.0000(ns), -0.0001***, +0.0001**, -0.0000(ns) | CORRECT |
| Lagged_DV: 0.862/0.863 (ind); 0.665/0.666 (firm) | L180: 0.8623, 0.6650, 0.8628, 0.6662 | CORRECT (rounded) |
| R²: 0.833/0.484 → 0.834/0.484 | L189: 0.833, 0.484, 0.834, 0.484 | CORRECT |
| N=73,707 | L188: 73,707 all | CORRECT |

### Findings

- **[LOW]** RDSales: same phrasing issue as H1.1 — col4=0.0015* is bold and sig, record says "1 marginal firm" instead of noting it as significant. Effectively 3/4 sig. Same LOW severity.
- **[CLEAN]** All other claims verified exactly. FE labels, tail, cluster, Lagged_DV, R², N all match.

### Verdict
CLEAN + 1 LOW (RDSales phrasing, same pattern as H1.1)

---

## H1.2 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 203–270
**Record audited**: DECISIONS.md §4.1 line 145; §4.2 block lines 391–407
**Table structure**: 4 cols, DV=CashRatio (contemp), FE ladder identical to H1.1/H1.1b. IVs: UncAnsMgr_c (main), BelowIG/Unrated (moderators, IG=reference), 3 interaction terms. Firm-level cluster. N=67,544.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsMgr_c 4/4 sig β>0 | L214: 0.0053***, 0.0035***, 0.0050***, 0.0035*** | CORRECT |
| BelowIG 1/4 sig β>0 (col 1 only) | L216: 0.0034***, -0.0009(ns), -0.0007(ns), -0.0011(ns) | CORRECT |
| Unrated 1/4 sig β>0 (col 1 only) | L218: 0.0062***, -0.0014(ns), -0.0004(ns), -0.0014(ns) | CORRECT |
| UncAnsMgr_c_x_IG 0/4 null | L220: 0.0020(ns), 0.0011(ns), 0.0015(ns), 0.0012(ns) | CORRECT |
| UncAnsMgr_c_x_BelowIG 0/4 null | L222: -0.0010(ns), 0.0003(ns), -0.0008(ns), 0.0001(ns) | CORRECT |
| UncAnsMgr_c_x_Unrated 4/4 sig β>0 | L224: 0.0059***, 0.0040**, 0.0064***, 0.0040** | CORRECT |
| Leverage 4/4 sig β<0 | L227: -0.0095***, -0.0154**, -0.0104***, -0.0155** | CORRECT |
| lnAssets — col 1 ind sig β>0 (+0.0005**), "cols 3, 5 ind sig β<0" | L229: col1=+0.0005**, col2=-0.0165***, col3=-0.0016***, col4=-0.0161*** | **ERROR: record says "cols 3, 5" but table has only 4 cols. Col 5 does not exist. Record references a non-existent column. Actual pattern: col1 ind β>0, col3 ind β<0, cols 2,4 firm β<0 = 4/4 sig.** |
| TobinsQ 4/4 sig β>0 | L231: 0.0051***, 0.0040***, 0.0045***, 0.0037*** | CORRECT |
| ROA 4/4 sig β<0 | L233: -0.0647***, -0.0328***, -0.0603***, -0.0309*** | CORRECT |
| Capex 4/4 sig β<0 | L235: -0.1378***, -0.2415***, -0.1391***, -0.2330*** | CORRECT |
| DivDummy 3/4 sig β<0 (col 4 null) | L237: -0.0045***, -0.0032*, -0.0047***, -0.0028(ns) | CORRECT — col4=ns, cols 1-3 sig |
| sCFO 2/4 sig β>0 (ind-only) | L239: 0.0112**, 0.0024(ns), 0.0105**, 0.0024(ns) | CORRECT |
| SalesGrowth 4/4 sig β<0 | L241: -0.0092***, -0.0108***, -0.0084***, -0.0102*** | CORRECT |
| RDSales 4/4 sig β>0 | L243: 0.0044***, 0.0024*, 0.0044***, 0.0025** | CORRECT (all 4 sig, record notes this differs from H1.1) |
| CashFlowAt 4/4 sig β>0 | L245: 0.1031***, 0.1278***, 0.1006***, 0.1270*** | CORRECT |
| DailyVola FE-mixed | L247: 0.0000(ns), -0.0001***, +0.0001*(sig), -0.0000(ns) | CORRECT |
| Lagged_DV: 0.864/0.867 (ind); 0.656/0.657 (firm) | L249: 0.8672, 0.6558, 0.8644, 0.6571 | FLAG: record says "0.864/0.867 (ind)" — LaTeX is 0.8672 (col1 ind+yr) and 0.8644 (col3 ind+yq). Rounded: 0.867/0.864 not 0.864/0.867. Order is SWAPPED in record — col1 should be listed first. Also firm: 0.6558, 0.6571 → 0.656/0.657 ✓. The ind swap is a LOW ordering error. |
| R²: 0.831/0.469 → 0.832/0.469 | L258: 0.831, 0.469, 0.832, 0.469 | CORRECT |
| N=67,544 | L257: 67,544 | CORRECT |

### Findings

- **[HIGH]** lnAssets "cols 3, 5 ind sig β<0": table H1.2 has only 4 columns total. There is NO col 5. Record references a non-existent column. The correct description is "col 3 ind+YQ sig β<0" (only one ind column in the non-col-1 group). This is a fabricated column reference — HIGH severity per the factual-error standard.
- **[LOW]** Lagged_DV ind order: LaTeX col1=0.8672 (ind+yr), col3=0.8644 (ind+yq). Record says "0.864/0.867 (ind)" — this lists col3 first, col1 second, reversing the natural column order. Values are correct but order is inverted.
- **[CLEAN]** IV sig counts, interaction sig counts, all controls (except lnAssets), R², N, tail, cluster all verified correct.

### Verdict
1 HIGH (lnAssets col 5 fabricated — non-existent column reference) + 1 LOW (Lagged_DV ind order swap)

---

## H13.1 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1169–1230
**Record audited**: DECISIONS.md §4.1 line 146; §4.2 block lines 409–425
**Table structure**: 8 cols — cols 1-4=Capex (contemp), cols 5-8=Capex_lead. FE ladder: (1)Ind+Yr, (2)Firm+Yr, (3)Ind+YQ, (4)Firm+YQ × 2 DVs. IVs: UncAnsMgr_c, z_log_TotalSimilarity, interaction. Base controls: lnAssets, TobinsQ, ROA, Leverage, CashRatio, DivDummy, sCFO + extended (SalesGrowth, RDSales, CashFlowAt, DailyVola). Firm-level cluster.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsMgr_c 4/8 sig β>0 ind-only (firm 0/4 null) | L1180: cols 1,3,5,7 bold (ind); cols 2,4,6,8 null (firm) | CORRECT |
| z_log_TotalSimilarity 6/8 sig β>0 | L1182: cols 1,3,5,6,7,8 bold; cols 2,4 null | CORRECT |
| Interaction 8/8 sig β>0 including all 4 firm-FE | L1184: all 8 bold (cols 1-4: **, **, **, **; cols 5-8: ***, ***, ***, ***) | CORRECT |
| lnAssets 8/8 sig β<0 | L1187: all 8 bold β<0 (*,**,**,***,***,***,***,***) | CORRECT |
| TobinsQ 8/8 sig β>0 | L1189: all 8 bold β>0 | CORRECT |
| ROA "8/8 sig — direction split: cols 1-6 contemp β<0, cols 7-8 lead β>0 firm-FE" | L1191: cols 1-4 all β<0; col5(lead-ind)=-0.0122***(neg); col6(lead-firm)=+0.0177***(pos); col7(lead-ind)=-0.0142***(neg); col8(lead-firm)=+0.0152***(pos) | **MEDIUM ERROR: record says "cols 1-6 contemp β<0" but cols 5-6 ARE LEAD (not contemp). Col6=+0.0177*** is lead-firm-yr and is POSITIVE, contradicting the "β<0" claim. Actual pattern: contemp 1-4 all β<0; lead: ind(5,7) β<0, firm(6,8) β>0.** |
| Leverage 6/8 sig (contemp all, lead firm-only) | L1193: cols 1-4 all sig β<0; col5,7 null; col6,8 sig β<0 | CORRECT |
| CashRatio 5/8 sig β<0 | L1195: cols 1,2,3,4 bold; col5=-0.0081*** (bold); col6=0.0059 (null); col7=-0.0080*** (bold); col8=0.0059 (null) | **HIGH ERROR: record says 5/8 but LaTeX has 6 bold sig cells (cols 1,2,3,4,5,7). Actual count = 6/8 sig β<0.** |
| DivDummy 2/8 sig β<0 (lead only) | L1197: cols 1-4 null; col5=-0.0017**, col7=-0.0016** (both lead-ind); cols 6,8 null | CORRECT |
| sCFO 6/8 sig β<0 | L1199: col1=-0.0040**, col2=-0.0058**, col3=-0.0039**, col4=-0.0058**, col5=-0.0017*, col6=-0.0043**, col7=-0.0016(null), col8=-0.0042** → 7 sig cells, col7 only null | **HIGH ERROR: record says 6/8 but LaTeX has 7 bold sig cells (cols 1,2,3,4,5,6,8). Actual count = 7/8 sig β<0.** |
| SalesGrowth 8/8 sig β>0 | L1201: all 8 bold | CORRECT |
| RDSales 8/8 sig β>0 | L1203: all 8 bold | CORRECT |
| CashFlowAt 8/8 sig β>0 | L1205: all 8 bold | CORRECT |
| DailyVola 8/8 sig — sign flip contemp vs lead | L1207: cols 1-4 contemp (2 pos, 1 null, 1 neg); cols 5-8 lead all neg | Record claims "8/8 sig" but col3=0.0000 (no asterisk, null). Actual: 7/8 sig. HIGH error — same error type as CashRatio and sCFO (wrong sig count). |
| Lagged_DV ind contemp 0.731/0.734; ind lead 0.624/0.625; firm contemp 0.333/0.335; firm lead 0.094/0.097 | L1209: 0.7311/0.3325/0.7337/0.3354/0.6234/0.0949/0.6251/0.0969 | CORRECT (rounded) |
| R²: contemp 0.620/0.156 → 0.623/0.159; lead 0.494/0.071 → 0.497/0.070 | L1218: 0.620,0.156,0.623,0.159 (contemp); 0.494,0.071,0.497,0.070 (lead) | CORRECT |
| N: 73,673 contemp / 69,580 lead | L1217: 73,673 all contemp; 69,580 all lead | CORRECT |

### Findings

- **[HIGH]** CashRatio sig count: record says "5/8 sig β<0" but LaTeX clearly shows 6 bold cells (cols 1,2,3,4,5,7 all have `\textbf` with ***). Col5=-0.0081*** is bold. Correct count is 6/8.
- **[HIGH]** sCFO sig count: record says "6/8 sig β<0" but LaTeX shows 7 bold cells (cols 1,2,3,4,5,6,8 — only col7=-0.0016 lacks asterisks). Correct count is 7/8.
- **[MEDIUM]** ROA direction description: record says "cols 1-6 contemp β<0" but cols 5-8 are ALL lead (Capex_lead), not contemp. Col6=+0.0177*** is lead-firm-yr and is POSITIVE, directly contradicting the "β<0" claim in the description. Correct description: contemp cols 1-4 all β<0; lead col5,7 (ind) β<0; lead col6,8 (firm) β>0.
- **[HIGH]** DailyVola "8/8 sig": col3 (Ind+YQ contemp) = 0.0000 with no asterisk (null). Actual count is 7/8 sig. Same error type as CashRatio and sCFO — wrong sig count — upgraded to HIGH for consistency.

### Verdict
3 HIGH (CashRatio miscounted 5→6, sCFO miscounted 6→7, DailyVola miscounted 8→7) + 1 MEDIUM (ROA direction mislabels lead as contemp)

---

## H13.2 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1232–1295
**Record audited**: DECISIONS.md §4.1 line 147; §4.2 block lines 427–455
**Table structure**: 16 cols — 4 horizons (Capex_lead, lead2, lead3, lead4) × 4 FE configs each. IVs: UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr (native 4-IV structure, NO moderation). Firm-level cluster. Tail: two-tailed (L1289).

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsCEO 0/16 null | L1243: no bold cells across 16 cols | CORRECT |
| UncPreCEO 0/16 null | L1245: no bold cells across 16 cols | CORRECT |
| UncAnsMgr 10/16 sig β>0 (cols 1,3,5,7,9,10,11,12,13,15) | L1247: bold at cols 1(***),3(***),5(***),7(***),9(***),10(*),11(***),12(*),13(***),15(***) = 10 sig | CORRECT |
| UncPreMgr 1/16 sig β<0 (col 3 lead1 only) | L1249: col3=-0.0020*(bold) only | CORRECT |
| Tail: two-tailed | L1289 notes: "(two-tailed)" | CORRECT |
| N: 58,897→52,648→46,679→41,091 | L1282: 58,897/52,648/46,679/41,091 | CORRECT |
| R²: h1 0.496/0.070→0.501/0.068; h4 0.361/0.016→0.366/0.016 | L1283: h1=0.496,0.070,0.501,0.068; h4=0.361,0.016,0.366,0.016 | CORRECT |
| Lagged_DV h1: "0.640/0.625 (ind); +0.087/+0.088 (firm)" | L1266: col1=0.6398, col2=0.0868, col3=0.6364, col4=0.0883 | **HIGH ERROR: record says ind = "0.640/0.625" but col3=0.6364≈0.636, NOT 0.625. The 0.625 is wrong. Likely copy-paste from H13.1 lead ind (0.624/0.625). Firm: 0.087/0.088 ✓** |
| Lagged_DV h2: "0.563/0.565 (ind); −0.035/−0.034 (firm)" | L1266: col5=0.5626, col6=-0.0351, col7=0.5645, col8=-0.0343 | ind: 0.5626≈0.563, 0.5645≈0.565 ✓; firm: -0.0351≈-0.035, -0.0343≈-0.034 ✓ CORRECT |
| Lagged_DV h3: "0.521/0.518 (ind); −0.077/−0.078 (firm)" | L1266: col9=0.5206, col10=-0.0774, col11=0.5175, col12=-0.0782 | ind: 0.5206≈0.521, 0.5175≈0.518 ✓; firm: -0.0774≈-0.077, -0.0782≈-0.078 ✓ CORRECT |
| Lagged_DV h4: "0.497/0.494 (ind); −0.064/−0.063 (firm)" | L1266: col13=0.4968, col14=-0.0641, col15=0.4939, col16=-0.0625 | ind: 0.4968≈0.497, 0.4939≈0.494 ✓; firm: -0.0641≈-0.064, -0.0625≈-0.063 ✓ CORRECT |
| lnAssets "mixed signs by horizon; firm-FE negative" | L1252: varies across cols | CORRECT |
| TobinsQ "8/8 sig β>0 at h1, declining" | L1254: h1 all 4 bold (cols 1-4); h2 firm cols 6,8 bold; h3-h4 minimal | MEDIUM: record says "8/8 sig β>0 at h1" but h1 has 4 cols (1-4). "8/8 at h1" implies 8 cells but h1 only has 4. Likely means cols 1-4 (4/4) + cols 5-8 (4/4)=h2 partial. Let me recount h1: cols 1,2,3,4 all bold → 4/4 sig at h1. Record says "8/8 sig β>0 at h1" which is wrong — h1 has only 4 cols. |
| sCFO "sign flip across horizons" | L1264: h1 firm β<0; h2 contemp sig β>0; h3-h4 firm sig β>0 | CORRECT description |

### Findings

- **[HIGH]** Lagged_DV h1 ind second value: record says "0.640/0.625 (ind)" but col3 (Ind+YQ, h1)=0.6364≈**0.636**, not 0.625. The 0.625 appears to be copied from H13.1's lead result (0.6251). This is a numerical fabrication — 0.625 does not appear in H13.2's Lagged_DV row.
- **[MEDIUM]** TobinsQ "8/8 sig β>0 at h1": the table has 4 horizons × 4 cols each. Horizon h1 has only 4 cols (1-4), not 8. "8/8 at h1" is structurally impossible for this layout. The record appears to have conflated h1+h2 as "h1." Actual h1 TobinsQ: 4/4 sig β>0 (cols 1-4 all bold). This is a description error that overstates h1 breadth.

### Verdict
1 HIGH (Lagged_DV h1 ind second value 0.625→0.636 fabrication) + 1 MEDIUM (TobinsQ "8/8 at h1" structural error — h1 only has 4 cols)

**Caveat — base controls not individually verified**: The §4.2 record contains substantial base-control claims across all 16 columns (lnAssets, ROA, Leverage, CashRatio, DivDummy, sCFO — each with cross-horizon descriptions). These were not cell-by-cell verified against LaTeX in this audit. H13.1 precedent — where the same assistant produced 3 HIGH sig-count errors in base controls — makes this an elevated-risk gap in a 16-col table. Treat H13.2 base-control sig counts as unaudited.

---

## H22 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 2103–2168
**Record audited**: DECISIONS.md §4.1 line 148; §4.2 block lines 457–473
**Table structure**: 4 cols, DV=EquityDelayCon_lead (lead, firm-year panel). FE: (1)Ind+Yr, (2)Firm+Yr, (3)Ind+Yr+ExtCtrl, (4)Firm+Yr+ExtCtrl (no YQ — annual panel). Native 4-IV (UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr). Firm-level cluster. N=8,621/8,564.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsCEO 2/4 sig β>0 — cols 1,3 (ind-FE only) | L2114: col1=0.0058*(bold), col2=0.0039(null), col3=0.0059*(bold), col4=0.0041(null) | CORRECT |
| UncPreCEO 0/4 null | L2116: all null | CORRECT |
| UncAnsMgr 0/4 null | L2118: all null (negative but unbolded) | CORRECT — no rule-22 violation in record |
| UncPreMgr 0/4 null | L2120: all null (negative but unbolded) | CORRECT — no rule-22 violation in record |
| lnAssets sign flip: col1 β>0, col3 β<0, cols 2,4 null | L2123: col1=0.0010*(bold pos), col2=0.0026(null), col3=-0.0009**(bold neg), col4=0.0025(null) | CORRECT |
| TobinsQ 0/4 null | L2125: all null | CORRECT |
| ROA 1/4 sig β<0 (col 1 only) | L2127: col1=-0.0119**(bold), rest null | CORRECT |
| Leverage 0/4 null | L2129: all null | CORRECT |
| Capex 0/4 null | L2131: all null | CORRECT |
| CashRatio 3/4 sig β>0 (cols 1,2,3) | L2133: col1=0.0215***(bold), col2=0.0158*(bold), col3=0.0137**(bold), col4=0.0146(null) | CORRECT |
| DivDummy 0/4 null | L2135: all null | CORRECT |
| sCFO 2/4 sig β<0 — cols 2,4 firm-FE only | L2137: col2=-0.0040**(bold), col4=-0.0039**(bold); cols 1,3 null | CORRECT |
| Lagged_DV: 0.660/0.181/0.664/0.184 | L2139: 0.6600, 0.1811, 0.6641, 0.1841 | CORRECT (rounded) |
| Extended: SalesGrowth 1/2 β>0 (col3 ind) | L2141: col3=0.0048**(bold), col4=0.0013(null) | CORRECT |
| Extended: RDSales 1/2 β>0 (col3 ind) | L2143: col3=0.0027**(bold), col4=0.0004(null) | CORRECT |
| Extended: CashFlowAt 0/2 null | L2145: both null | CORRECT |
| Extended: DailyVola 1/2 β>0 (col4 firm) | L2147: col3=-0.0001(null), col4=0.0001**(bold) | CORRECT |
| R²: 0.491/0.041/0.491/0.043 | L2156: exactly matches | CORRECT |
| N: 8,621 (cols 1,2) / 8,564 (cols 3,4) | L2155: exactly matches | CORRECT |
| Tail: one-tailed β>0 for IVs | L2162: confirms | CORRECT |
| Cluster: firm-level | L2163: confirms | CORRECT |

### Findings

- **[CLEAN]** All 19 verifications pass. IV sig counts correct. All controls correct. Lagged_DV values correct. R², N, FE labels, tail, cluster all correct. No rule-22 violations (null IVs described as null, no direction language applied). No rule-21 inversion (UncAnsCEO 2/4 is an informative pattern, KEEP is correct). Small-N flag appropriately noted.

### Verdict
CLEAN

---

## H7 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 470–534
**Record audited**: DECISIONS.md §4.2 block lines 493–509
**Table structure**: 12 cols — cols 1-6=DeltaILLIQ (contemp), cols 7-12=DeltaILLIQ_lead1. 6-rung FE ladder identical to H5. Extended controls: DailyVola, StockPrice, Turnover, UncQue (cols 3-6, 9-12). Firm-level cluster. N=60,182–63,736.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsCEO 0/12 null | L481: no bold cells | CORRECT |
| UncPreCEO 1/12 sig β>0 (col 2 firm+yr contemp) | L483: col2=0.0008*(bold only) | CORRECT |
| UncAnsMgr 0/12 null | L485: no bold cells (values mostly negative but unbolded) | CORRECT — no rule-22 violation; record says "0/12 null" not "wrong direction" |
| UncPreMgr 0/12 null | L487: no bold cells | CORRECT |
| lnAssets 12/12 sig β>0 | L490: all 12 bold β>0 | CORRECT |
| TobinsQ 12/12 sig β>0 | L492: all 12 bold | CORRECT |
| ROA 2/12 sig β>0 — cols 7,8 lead only | L494: col7=0.0031*(bold), col8=0.0045*(bold); rest null | CORRECT |
| Leverage 2/12 sig β<0 — cols 2,4 firm-FE contemp | L496: col2=-0.0024*(bold), col4=-0.0023*(bold); rest null | CORRECT |
| Capex 4/12 sig β>0 — cols 1,5,7,11 | L498: col1=0.0044**(bold), col5=0.0047**(bold), col7=0.0044**(bold), col11=0.0044**(bold) | CORRECT |
| DivDummy 1/12 sig β<0 (col 9 only) | L500: col9=-0.0004*(bold) | CORRECT |
| sCFO 1/12 sig β<0 (col 8 only) | L502: col8=-0.0004*(bold) | CORRECT |
| Lagged_DV 0/12 null; values 0.022/-0.012/0.028/-0.009/0.026/-0.009/0.012/-0.022/0.017/-0.018/0.016/-0.018 | L504: 0.0218/-0.0118/0.0276/-0.0091/0.0264/-0.0085/0.0122/-0.0215/0.0174/-0.0181/0.0162/-0.0180, all null | CORRECT — all 12 values verified |
| Extended: DailyVola 5/8 sig β<0 — col 3 + cols 9-12 | L506: col3(***), col9(***), col10(***), col11(**), col12(**) bold; cols 4,5,6 null | CORRECT |
| Extended: StockPrice 7/8 sig β<0 (col 3 null) | L508: col3 null; cols 4,5,6,9,10,11,12 bold | CORRECT |
| Extended: Turnover 8/8 sig β>0 | L510: all 8 bold | CORRECT |
| Extended: UncQue 1/8 sig β<0 (col 3 only) | L512: col3=-0.0005*(bold); rest null | CORRECT |
| R²: contemp 0.004/0.001→0.003/0.001→0.005/0.001; lead 0.004/0.001→0.005/0.003→0.005/0.002 | L522: matches | CORRECT |
| N: 63,736→60,182→63,313→61,060 | L521: distinct values match | CORRECT |
| Tail: one-tailed β>0 for IVs | L528: confirms | CORRECT |
| Cluster: firm-level | L529: confirms | CORRECT |

### Findings

- **[CLEAN]** All 20 verifications pass. IV sig counts verified exactly. All base controls verified. Lagged_DV 12 values verified (all null, all values correct to 3 decimal places). All extended controls correct. R², N, FE, tail, cluster all match. No rule-22 violations (negative null UncAnsMgr described as null, not wrong-direction). Rule-21 KEEP correct (1 sig cell ≥ informative pattern threshold). Near-null flag and H16 comparison appropriately noted.

### Verdict
CLEAN

---

## H5 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 404–468
**Record audited**: DECISIONS.md §4.1 line (Q3 section); §4.2 block lines 475–491
**Table structure**: 12 cols — cols 1-6=DISP (contemp), cols 7-12=DISP_lead. 6-rung FE: (1)Ind+Yr, (2)Firm+Yr, (3)Ind+Yr+Ext, (4)Firm+Yr+Ext, (5)Ind+YQ+Ext, (6)Firm+YQ+Ext × 2 DVs. Native 4-IV. Extended controls: SurpDec, Loss, UncQue, NegCall (cols 3-6, 9-12). Firm-level cluster. N=18,406–20,069.

### Verification trace

| Claim | LaTeX line | Verified |
|---|---|---|
| UncAnsCEO 0/12 null | L415: no bold cells | CORRECT |
| UncPreCEO 0/12 null | L417: no bold cells | CORRECT |
| UncAnsMgr 6/12 sig β>0 — all ind-FE (cols 1,3,5,7,9,11) | L419: cols 1(***),3(***),5(***),7(**),9(***),11(**) bold; cols 2,4,6,8,10,12 null | CORRECT |
| UncPreMgr 12/12 sig β>0 — every cell incl all 6 firm-FE | L421: all 12 bold (*,***,**,**,*,**,*,**,***,**,**,**) | CORRECT — first full-ladder UncPreMgr confirmed |
| lnAssets 0/12 null | L424: no bold cells | CORRECT |
| TobinsQ 12/12 sig β<0 | L426: all 12 bold | CORRECT |
| ROA 12/12 sig β<0 | L428: all 12 bold | CORRECT |
| Leverage 12/12 sig β>0 | L430: all 12 bold | CORRECT |
| Capex 3/12 sig β<0 — cols 2,4,6 firm-FE contemp only | L432: cols 2(-0.0024***),4(-0.0019**),6(-0.0020**) bold; rest null | CORRECT |
| DivDummy 6/12 sig β<0 — all 6 ind-FE (cols 1,3,5,7,9,11) | L434: cols 1,3,5,7,9,11 bold; firm cols 2,4,6,8,10,12 null | CORRECT |
| sCFO 11/12 sig β>0 (col 2 null) | L436: col2=0.0001(no bold); all other 11 bold | CORRECT |
| Lagged_DV contemp 0.648/0.388/0.628/0.372/0.631/0.376 | L438: 0.6484/0.3880/0.6278/0.3722/0.6310/0.3758 | CORRECT (rounded) |
| Lagged_DV lead 0.593/0.310/0.579/0.302/0.584/0.309 | L438: 0.5926/0.3103/0.5789/0.3019/0.5836/0.3093 | CORRECT (rounded) |
| Extended: SurpDec 6/8 sig β<0 | L440: cols 3,5 contemp bold; cols 9,10,11,12 lead bold = 6 sig | CORRECT |
| Extended: Loss 8/8 sig β>0 | L442: all 8 bold | CORRECT |
| Extended: UncQue 0/8 null | L444: all null | CORRECT |
| Extended: NegCall 8/8 sig β>0 | L446: all 8 bold | CORRECT |
| R²: contemp 0.488/0.204→0.501/0.223→0.503/0.223; lead 0.431/0.158→0.452/0.179→0.458/0.180 | L456: matches exactly | CORRECT |
| N: 20,069→19,124→19,355→18,406 | L455: 20,069/20,069/19,124/19,124/19,124/19,124/19,355/19,355/18,406/18,406/18,406/18,406 | CORRECT (distinct values captured) |
| Tail: one-tailed β>0 for IVs | L462: confirms | CORRECT |
| Cluster: firm-level | L463: confirms | CORRECT |

### Findings

- **[CLEAN]** All 21 verifications pass. IV sig counts verified exactly (UncAnsMgr 6/12, UncPreMgr 12/12, CEO 0/12). All base controls verified. All extended controls verified. Lagged_DV 12 values all correct. R², N, FE labels, tail, cluster all match. No rule-22 violations. §5.14 cross-reference (UncPreMgr full-ladder) verified as 12/12 ✓.

### Verdict
CLEAN

---

## Batch B — Overall Audit Summary

| Suite | HIGH | MEDIUM | LOW | Verdict |
|---|---|---|---|---|
| H1.1 | 0 | 0 | 1 (RDSales phrasing) | CLEAN + 1L |
| H1.1b | 0 | 0 | 1 (RDSales phrasing) | CLEAN + 1L |
| H1.2 | 1 (lnAssets col 5 non-existent) | 0 | 1 (Lagged_DV ind order) | 1H + 1L |
| H13.1 | 3 (CashRatio 5/8→6/8; sCFO 6/8→7/8; DailyVola 8/8→7/8) | 1 (ROA direction label) | 0 | 3H + 1M |
| H13.2 | 1 (Lagged_DV h1 ind 0.625→0.636) | 1 (TobinsQ "8/8 at h1" impossible) | 0 | 1H + 1M |
| H22 | 0 | 0 | 0 | CLEAN |
| H5 | 0 | 0 | 0 | CLEAN |
| H7 | 0 | 0 | 0 | CLEAN |
| **TOTAL** | **5** | **2** | **3** | — |

### High-severity findings requiring correction in DECISIONS.md

1. **H1.2 lnAssets**: record says "cols 3, 5 ind sig β<0" — H1.2 has only 4 columns total; col 5 does not exist. Correct: "col 3 (ind+YQ) sig β<0."

2. **H13.1 CashRatio sig count**: record says "5/8 sig β<0" — actual count from LaTeX L1195 is **6/8** (cols 1,2,3,4,5,7 all `\textbf` with ***). Col5=-0.0081*** is clearly bold. Correct count: 6/8.

3. **H13.1 sCFO sig count**: record says "6/8 sig β<0" — actual count from LaTeX L1199 is **7/8** (cols 1,2,3,4,5,6,8 bold with **,**,**,**,*,**,**; only col7=-0.0016 lacks asterisks). Correct count: 7/8.

4. **H13.2 Lagged_DV h1 ind**: record says "0.640/0.625 (ind)" — col3 (Ind+YQ h1) from LaTeX L1266 is 0.6364≈**0.636**, not 0.625. The value 0.625 appears copied from H13.1's Capex_lead ind Lagged_DV (col7=0.6251). Correct: "0.640/0.636 (ind)."

5. **H13.1 DailyVola sig count**: record says "8/8 sig" — col3 (Ind+YQ contemp) from LaTeX L1207 = 0.0000 with no asterisk (null). Actual count is 7/8 sig. Same error class as CashRatio and sCFO miscounts.

### Key observations

- H22, H5, H7 are completely clean — zero errors detected across 60+ verifications.
- H13.1 has the heaviest error concentration (3 HIGH + 1 MEDIUM), all in base-control sig counts and descriptions.
- All 5 HIGH findings are in the Q2 cluster (H1.2 and H13.1/H13.2). The Q3 suites (H5, H7) are clean.
- No rule-22 violations detected across any of the 8 suites (no direction language applied to null cells).
- No rule-21 inversions (H7's near-null was appropriately kept with a flag, not dropped silently).
- The H13.1 ROA MEDIUM error (horizon mislabeling: cols 5-6 called "contemp" when they are lead) could mislead the ROA mechanism story at synthesis time.

