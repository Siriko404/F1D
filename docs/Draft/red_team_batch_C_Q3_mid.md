# Q3-mid Red Team Audit — Batch C (6 suites)

**Target**: 6 Q3 suite records in DECISIONS.md §4.1 / §4.2
**Auditor**: Red team agent spawned 2026-04-15 (batch C)
**Approach**: Adversarial, hardnosed, manual cell-by-cell. Assume wrong until verified.
**Suites**: H7b, H7c, H7d, H7e, H14, H14b

---

## H7c — red team audit

**LaTeX source**: outputs/all_tables.tex lines 602–666
**Record audited**: DECISIONS.md §4.1 row line 152; §4.2 block lines 529–545

### Verification trace

**IVs (12 cells, LaTeX lines 613–620):**
- UncAnsCEO: cols 1–6 all bold ** → 6/6 contemp sig β>0; cols 7–12 all unbolded → lead 0/6. Total 6/12. Record: "6/12 sig β>0 — ALL 6 contemp." MATCH.
- UncPreCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncAnsMgr: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreMgr: col 9 bold ** (0.0024) → 1/12 sig β>0 (lead ind+yr+ext). Record: "1/12 sig β>0 — col 9 lead ind+yr+ext." MATCH.

**§5.15 cross-check — "UncAnsCEO 6/6 sig β>0 ALL 6 contemp cells":** LaTeX confirms cols 1–6 all bolded **. Firm-FE cells = cols 2,4,6 (all sig). CONFIRMED.

**Lagged_DV (LaTeX line 636, all *** sig):**
col 1=0.7896, col 2=0.6805, col 3=0.7740, col 4=0.6612, col 5=0.7773, col 6=0.6649, col 7=0.7859, col 8=0.6782, col 9=0.7828, col 10=0.6679, col 11=0.7840, col 12=0.6721.
Record §4.2: "0.790/0.680/0.774/0.661/0.777/0.665 contemp; 0.786/0.678/0.783/0.668/0.784/0.672 lead; ind ~0.78, firm ~0.67." MATCH (rounded correctly).

**TobinsQ (LaTeX line 624):** bold sig cols 1,3,5,7,11 only → 5/12 sig β<0, all industry-FE. Record: "5/12 sig β<0 — cols 1,3,5,7,11 (all ind-FE; firm-FE 0/6 null)." MATCH.

**ROA (LaTeX line 626):** all 12 bold *** β<0. Record: "12/12 sig β<0." MATCH.

**Leverage (LaTeX line 628):** col 3 bold *, col 10 bold * → 2/12 sig β<0. Record: "2/12 sig β<0 — cols 3, 10." MATCH.

**Capex (LaTeX line 630):** sig 10/12 (cols 2,4 null). Record: "10/12 sig β<0 (cols 2,4 null)." MATCH.

**DivDummy (LaTeX line 632):** 6/12 sig. Cols 3,5 β>0; cols 2,8,10,12 β<0. Record: "6/12 sig with FE sign flip — cols 3,5 ind β>0; cols 2,8,10,12 firm β<0." MATCH.

**sCFO (LaTeX line 634):** cols 4,6 sig * → 2/12. Record: "2/12 sig β<0 — cols 4,6 firm-FE contemp." MATCH.

**UncQue (LaTeX line 644):** contemp cols 3,4,5,6 sig → 4/8 (lead 0/4). Record: "4/8 sig β<0 — cols 3,4,5,6 contemp; lead 0/4 null." MATCH.

**N (LaTeX line 653):** 63,806→60,256→63,351→61,099. Record: same. MATCH.

**R² (LaTeX line 654):** ranges 0.621–0.623 ind / 0.451–0.456 firm. Record: "contemp 0.621/0.451 → 0.622/0.454; lead 0.623/0.456 → 0.619/0.451." MATCH.

**Notes block tail/cluster:** one-tailed IVs β>0, firm-level cluster. MATCH.

### Findings

- **[CLEAN]** All IV sig counts verified cell-by-cell. §5.15 6/6 contemp UncAnsCEO confirmed. Lagged_DV values verified (12/12). R²/N verified. Base controls verified (lnAssets, TobinsQ, ROA, Leverage, Capex, DivDummy, sCFO). Extended controls verified. Tail/cluster confirmed.

### Verdict
CLEAN — 0 HIGH + 0 MEDIUM + 0 LOW findings.

---

## H7e — red team audit

**LaTeX source**: outputs/all_tables.tex lines 734–798
**Record audited**: DECISIONS.md §4.1 row line 154; §4.2 block lines 565–581

### Verification trace

**IVs (12 cells, LaTeX lines 745–752):**
- UncAnsCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncAnsMgr: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreMgr: col 3 ** (0.0016), col 9 * (0.0020) → 2/12 sig β>0. Record: "2/12 sig β>0 — col 3 (ind+yr+ext contemp) + col 9 (ind+yr+ext lead)." MATCH.

**Lagged_DV (LaTeX line 768, all *** sig):**
col 1=0.7988, col 2=0.7012, col 3=0.7871, col 4=0.6888, col 5=0.7902, col 6=0.6925, col 7=0.8046, col 8=0.7083, col 9=0.7974, col 10=0.6987, col 11=0.7985, col 12=0.7005. Record §4.2: "0.799/0.701/0.787/0.689/0.790/0.693 contemp; 0.805/0.708/0.797/0.699/0.799/0.701 lead; 12/12 sig ~0.80 ind/0.70 firm." MATCH.

**TobinsQ (LaTeX line 756):** sig cols 1,2,3,4,5,6,7,9,11 = 9/12. Null = cols 8,10,12 (all firm-FE leads). Record: "9/12 sig β<0 (cols 8,10,12 null — firm-FE leads)." MATCH.

**ROA (LaTeX line 758):** all 12 bold *** β<0. Record: "12/12 sig β<0." MATCH.

**Leverage (LaTeX line 760):** sig cols 3,9,10,12 → 4/12 β<0. Record: "4/12 sig β<0 — cols 3,9,10,12 only." MATCH.

**Capex (LaTeX line 762):**
Raw cells: col1 * (-0.0082), col2 unbolded (0.0002), col3 ** (-0.0102), col4 unbolded (-0.0021), col5 *** (-0.0149), col6 unbolded (-0.0164), col7 *** (-0.0171), col8 ** (-0.0231), col9 *** (-0.0186), col10 *** (-0.0251), col11 *** (-0.0178), col12 ** (-0.0210).
Sig cols: 1,3,5,7,8,9,10,11,12 = **9/12** sig. Null cols: 2,4,6.
Record §4.2 states: "**10/12 sig β<0** (cols 2,6 null)." **WRONG: col 4 is also null — actual is 9/12 with cols 2,4,6 null.** Record under-counts nulls by 1.

**DivDummy (LaTeX line 764):** sig 6/12 with FE sign flip — cols 3,5,9 β>0; cols 8,10,12 β<0. Record: "6/12 sig with FE sign flip — cols 3,5,9 ind β>0; cols 8,10,12 firm β<0." MATCH.

**sCFO (LaTeX line 766):** col4 *, col6 *, col10 * → 3/12 firm-FE. Record: "3/12 sig β<0 — cols 4,6,10 firm-FE cells." MATCH.

**DailyVola (LaTeX line 770):** all 8 sig *** β>0. Record: "8/8 sig β>0." MATCH.

**StockPrice (LaTeX line 772):** all 8 sig ** or *** β>0 (small positive). Record: "8/8 sig (small positive)." MATCH.

**Turnover (LaTeX line 774):** all 8 sig *** β<0. Record: "8/8 sig β<0." MATCH.

**UncQue (LaTeX line 776):** cols 5,6 sig ** and * → 2/8 β<0. Record: "2/8 sig β<0 — cols 5,6." MATCH.

**N (LaTeX line 785):** 63,816→60,256→63,397→61,136. Record: MATCH.

**R² (LaTeX line 786):** ind range 0.642–0.649; firm range 0.492–0.500. Record: "0.647/0.496 → 0.649/0.500 contemp; 0.644/0.494 → 0.642/0.492 lead." MATCH.

**Notes block:** one-tailed IVs β>0, firm cluster. MATCH.

### Findings

- **[HIGH]** §4.2 Capex row states "**10/12 sig β<0** (cols 2,6 null)." LaTeX line 762 shows col 4 = -0.0021 unbolded (null). Actual sig count = **9/12**, null cols = 2,4,6. Record omits col 4 as null and overcounts sig by 1.

### Verdict
1 HIGH + 0 MEDIUM + 0 LOW findings. Capex sig count wrong: 10/12 claimed, 9/12 actual (col 4 incorrectly excluded from null set).

---

## H14b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1364–1429
**Record audited**: DECISIONS.md §4.1 row line 156; §4.2 block lines 601–617

### Verification trace

**IVs (12 cells, LaTeX lines 1375–1382):**
- UncAnsCEO: cols 1–7,9,11 unbolded; cols 8,10,12 bold * → 3/12 sig β>0, all firm-FE lead. Record: "3/12 sig β>0 — cols 8,10,12 firm-FE lead only." MATCH.
- UncPreCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncAnsMgr: col 3 *** (0.9758), col 9 *** (1.2029) → 2/12 β>0. Record: "2/12 sig β>0 — cols 3,9 ind+yr+ext." MATCH.
- UncPreMgr: col 2 * (0.5918), col 3 *** (1.8059), col 9 *** (1.8837) → 3/12 β>0. Record: "3/12 sig β>0 — cols 2,3,9." MATCH.
- Total: 8/48. Record: "8/48 sig." MATCH.

**§5.18 cross-check — "UncAnsCEO 3/12 sig β>0 cols 8,10,12 firm-FE lead cells only":**
LaTeX cols 8 (firm+yr lead), 10 (firm+yr+ext lead), 12 (firm+yq+ext lead) — all firm-FE, all lead. CONFIRMED.

**Lagged_DV (LaTeX line 1398):** all 12 sig *** ranging 0.4092–0.6150. Record: "12/12 ~0.60 ind/0.43 firm." MATCH.

**Notes block / rescaling (LaTeX line 1427):** "PostCallSpread rescaled by $10^4$." Record: "×10⁴." MATCH.

**lnAssets (LaTeX line 1384):** 12/12 sig *** β<0. Record: MATCH.

**TobinsQ (LaTeX line 1386):** 11/12 sig β<0 (col 9 null). Record: "11/12 sig β<0 (col 9 null)." MATCH.

**ROA (LaTeX line 1388):** 12/12 sig *** β<0. Record: MATCH.

**Leverage (LaTeX line 1390):** 10/12 sig β>0 (cols 3,9 null). Record: MATCH.

**Capex (LaTeX line 1392):** 10/12 sig β<0 (cols 3,9 null). Record: MATCH.

**DivDummy (LaTeX line 1394):**
Raw cells: col1=0.0569 (ns), col2=**-0.8433**** (sig β<0), col3=**0.3302*** (sig β>0), col4=**-0.6241*** (sig β<0), col5=0.2743 (ns — **unbolded, NOT significant**), col6=**-0.6348*** (sig β<0), col7=-0.1545 (ns), col8=**-0.9509**** (sig β<0), col9=0.1248 (ns), col10=**-0.7079**** (sig β<0), col11=0.1010 (ns), col12=**-0.6227*** (sig β<0).
Sig: 2,3,4,6,8,10,12 = **7/12** (total count CORRECT). But sign breakdown: col 3 only β>0; cols 2,4,6,8,10,12 β<0.
Record §4.2 states: "**7/12 sig with FE sign flip — cols 3,5 ind β>0**; cols 2,4,6,8,10,12 firm β<0."
**Col 5 is NOT bold in LaTeX — it is null (0.2743 ns).** Record incorrectly includes col 5 as a sig β>0 cell. **The β>0 sig cells are col 3 only, not cols 3 AND 5.**

**sCFO (LaTeX line 1396):** cols 2,8,10,12 sig * or ** β>0 → 4/12. Record: "4/12 sig β>0 — cols 2,8,10,12 firm-FE." MATCH.

**Extended controls:**
- DailyVola (line 1400): 8/8 sig β>0. MATCH.
- StockPrice (line 1402): 6/8 sig with FE sign flip — cols 3,9 β<0; cols 4,6,10,12 β>0 (cols 5,11 null). Record: MATCH.
- Turnover (line 1404): 8/8 sig β<0. MATCH.
- UncQue (line 1406): 5/8 mixed — cols 3,9 β>0; cols 4,5,6 β<0. Record: MATCH.

**N (LaTeX line 1415):** 63,972→60,368→63,554→61,257. Record: MATCH.

**R² (LaTeX line 1416):** ind 0.539–0.555; firm 0.292–0.326. Record: "0.53–0.56 ind / 0.29–0.33 firm." MATCH.

**Notes block:** one-tailed IVs β>0, firm cluster. MATCH.

### Findings

- **[HIGH]** §4.2 DivDummy description states "cols **3,5** ind β>0." LaTeX line 1394 shows col 5 = 0.2743 (un-bolded, no star) — col 5 is NULL. The only sig β>0 DivDummy cell is col 3. Total sig count 7/12 is correct (coincidentally), but the listing of which cell is β>0 is wrong. Record incorrectly attributes sig β>0 to col 5 (ind+yq+ext contemp).

### Verdict
1 HIGH + 0 MEDIUM + 0 LOW findings. DivDummy col 5 listed as sig β>0 in §4.2, but LaTeX shows col 5 unbolded/null.

---

## H14 — red team audit

**LaTeX source**: outputs/all_tables.tex lines 1297–1362
**Record audited**: DECISIONS.md §4.1 row line 155; §4.2 block lines 583–599

### Verification trace

**IVs (12 cells, LaTeX lines 1308–1315):**
- UncAnsCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncAnsMgr: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreMgr: col 6 * (0.4657) only → 1/12 sig β>0. Record: "1/12 sig β>0 (col 6 firm+yq+ext contemp only)." MATCH.
- Total IV sig: 1/48. Record §4.1: "1/48 sig — near-complete null." MATCH. §5.19 H14 1/48. CONFIRMED.

**Notes block / rescaling (LaTeX line 1360):** "DSPREAD values rescaled by $10^4$." Record: "Rescaled ×10⁴." MATCH.

**Lagged_DV (LaTeX line 1331):**
col1=0.0138 (ns), col2=-0.0170* (sig), col3=0.0167 (ns), col4=-0.0226** (sig), col5=0.0128 (ns), col6=-0.0226** (sig), col7=0.0133 (ns), col8=-0.0185* (sig), col9=0.0221* (sig), col10=-0.0156 (ns), col11=0.0193 (ns), col12=-0.0155 (ns). Sig: 5/12. Record §4.2: "5/12 sig mixed-sign — firm-FE cells mostly small β<0, col 9 ind+yr+ext lead β>0." MATCH.

**lnAssets (LaTeX line 1317):** sig 10/12 β>0 (cols 10,12 firm-FE lead null). Record: "10/12 sig β>0." MATCH.

**TobinsQ (LaTeX line 1319):** sig cols 1,2,5,7,8,11 = 6/12 β>0. Record: "6/12 sig β>0 — cols 1,2,5,7,8,11." MATCH.

**ROA (LaTeX line 1321):** sig cols 1,7 = 2/12 β<0. Record: "2/12 sig β<0 — cols 1,7." MATCH.

**Leverage (LaTeX line 1323):** sig cols 1,5,7 = 3/12 β<0. Record: "3/12 sig β<0 — cols 1,5,7." MATCH.

**Capex (LaTeX line 1325):** sig cols 5,11 = 2/12 β>0. Record: "2/12 sig β>0 — cols 5,11." MATCH.

**DivDummy (LaTeX line 1327):** 0/12 null. Record: "0/12 null." MATCH.

**sCFO (LaTeX line 1329):** sig cols 1,4,5,6,7,9,10,11,12 = 9/12 β>0. Record: "9/12 sig β>0." MATCH.

**Extended controls:**
- StockPrice (line 1333): 5/8 sig β<0 (cols 3,5,6,9,11; nulls 4,10,12). Record: MATCH.
- Turnover (line 1335): 8/8 sig *** β>0. Record: "8/8 sig β>0." MATCH.
- DailyVola (line 1337): 5/8 sig β<0 (col3 contemp + cols 9,10,11,12 lead). Record: MATCH.
- AbsSurpDec (line 1339): 4/8 sig β<0 (cols 3,5,9,11 all ind-FE). Record: MATCH.

**N (LaTeX line 1348):** 63,972→44,132→63,554→44,640 (ext drops ~30%). Record: MATCH.

**R² (LaTeX line 1349):** range 0.001–0.009. Record: "R² 0.001–0.009 near-zero." MATCH.

**Notes block:** one-tailed IVs β>0, firm cluster. MATCH.

### Findings

- **[CLEAN]** All IV sig counts confirmed. Lagged_DV 5/12 mixed-sign confirmed. All controls verified. ×10⁴ rescaling noted in LaTeX. N drops confirmed. §5.19 near-null (1/48) confirmed.

### Verdict
CLEAN — 0 HIGH + 0 MEDIUM + 0 LOW findings.

---

## H7d — red team audit

**LaTeX source**: outputs/all_tables.tex lines 668–732
**Record audited**: DECISIONS.md §4.1 row line 153; §4.2 block lines 547–563

### Verification trace

**IVs (12 cells, LaTeX lines 679–686):**
- UncAnsCEO: all 12 unbolded → 0/12. Record: 0/12. MATCH.
- UncPreCEO: col 7 **, col 9 ***, col 11 ***, col 12 * → 4/12 sig β>0 (all lead). Record: "4/12 sig β>0 — cols 7,9,11,12 (lead only: 3 ind + 1 firm col 12)." MATCH.
- UncAnsMgr: col 1 * (0.0011) → 1/12. Record: "1/12 sig β>0 (col 1 ind+yr contemp only)." MATCH.
- UncPreMgr: all unbolded → 0/12. Record: 0/12. MATCH.
- Total IV sig: 5/48. Record §4.1: "5/48 sig." MATCH.

**§5.20 cross-check — "H7d 5/48 sig":** CONFIRMED.

**Lagged_DV (LaTeX line 702):** 12/12 sig *** ranging 0.141–0.178. Record §4.2: "12/12 sig ~0.14–0.18." MATCH.

**lnAssets (LaTeX line 688):** 12/12 sig *** β>0. Record: "12/12 sig β>0." MATCH.

**TobinsQ (LaTeX line 690):** 12/12 sig *** β>0. Record: "12/12 sig β>0." MATCH.

**ROA (LaTeX line 692):** cols 1,2,9 sig → 3/12 β<0. Record: "3/12 sig β<0 — cols 1,2 contemp + col 9 lead." MATCH.

**Leverage (LaTeX line 694):** cols 1,2,3,4,5,6,8 sig → 7/12 β<0. Record: "7/12 sig β<0 — cols 1-6 contemp + col 8 firm lead." MATCH.

**Capex (LaTeX line 696):** col 3 * → 1/12 β<0. Record: "1/12 β<0 (col 3)." MATCH.

**DivDummy (LaTeX line 698):** cols 9,11 *** β<0 → 2/12. Record: "2/12 β<0 — cols 9,11 lead ind+ext." MATCH.

**sCFO (LaTeX line 700):** col 3 * (-0.0010) → 1/12. Record: "1/12 β<0 (col 3)." MATCH.

**DailyVola (LaTeX line 704):** 6/8 sig with horizon sign flip — contemp cols 4,6 β>0; lead cols 9,10,11,12 β<0. Record: MATCH.

**StockPrice (LaTeX line 706):** 7/8 sig β<0 (col 3 null). Record: MATCH.

**Turnover (LaTeX line 708):** 4/8 lead-only sig β>0 (contemp 0/4). Record: MATCH.

**UncQue (LaTeX line 710):** 0/8 null. Record: MATCH.

**N (LaTeX line 719):** 63,537→60,036→63,066→60,826. Record: MATCH.

**R² (LaTeX line 720):** range 0.022–0.039. Record: "0.022–0.039." MATCH.

**Notes block:** one-tailed IVs β>0, firm cluster. MATCH.

### Findings

- **[CLEAN]** All IV sig counts verified cell-by-cell (UncPreCEO 4/12, UncAnsMgr 1/12, others null). All control rows verified. §5.20 H7d 5/48 confirmed.

### Verdict
CLEAN — 0 HIGH + 0 MEDIUM + 0 LOW findings.

---

## H7b — red team audit

**LaTeX source**: outputs/all_tables.tex lines 536–600 (caption line 538: "H7b: Speech Uncertainty and 3-Day Post-Call Amihud Illiquidity Level")
**Record audited**: DECISIONS.md §4.1 row line 151; §4.2 block lines 511–527

### Verification trace

**IVs (12 cells, from LaTeX lines 547–554):**
- UncAnsCEO: cols 1-12 all un-bolded → 0/12 sig. Record: 0/12. MATCH.
- UncPreCEO: cols 1-12 all un-bolded → 0/12 sig. Record: 0/12. MATCH.
- UncAnsMgr: cols 1-12 all un-bolded → 0/12 sig. Record: 0/12. MATCH.
- UncPreMgr: col 3 **0.0013**$^{**}$, col 9 **0.0019**$^{***}$; all others unbolded → 2/12 sig β>0. Record: 2/12 sig cols 3, 9. MATCH.

**Lagged_DV (LaTeX line 570, all 12 cells, all sig ***):**
col 1=0.7099, col 2=0.6092, col 3=0.6928, col 4=0.5914, col 5=0.6942, col 6=0.5941, col 7=0.7277, col 8=0.6261, col 9=0.7170, col 10=0.6108, col 11=0.7170, col 12=0.6132.
All firm-FE cells (2,4,6,8,10,12): 0.6092, 0.5914, 0.5941, 0.6261, 0.6108, 0.6132 — range 0.591–0.626. **No value near 0.39 exists anywhere.**

§4.1 row states: "Lagged_DV 0.71/0.61 ind / **0.60/0.39 firm**". The "0.39" does NOT appear in the LaTeX. **FABRICATED VALUE.**

§4.2 block (line 522) states: "contemp 0.710 / 0.609 / 0.693 / 0.591 / 0.694 / 0.594; lead 0.728 / 0.626 / 0.717 / 0.611 / 0.717 / 0.613. High persistence — ind ~0.70, firm ~0.60." §4.2 values are CORRECT. The error is confined to the §4.1 summary row.

**N row (LaTeX line 587):** 63,736 / 63,736 / 60,182 / 60,182 / 60,182 / 60,182 / 63,313 / 63,313 / 61,060 / 61,060 / 61,060 / 61,060. Record: "N = 63,736 → 60,182 → 63,313 → 61,060." MATCH.

**R² row (LaTeX line 588):** 0.541, 0.390, 0.544, 0.398, 0.545, 0.395, 0.546, 0.395, 0.546, 0.398, 0.544, 0.392. Record §4.2: "contemp 0.541 / 0.390 → 0.545 / 0.395; lead 0.546 / 0.395 → 0.544 / 0.392." Matches all cited cells. MATCH.

**Notes block (LaTeX line 594):** "one-tailed for IVs, β > 0; two-tailed for controls." Cluster: "clustered at firm level." Record: "Tail: one-tailed β>0. Cluster: firm-level." MATCH.

**sCFO (LaTeX line 568):** sig cells cols 1,3,4,5,6,7,9,10,11,12 = 10/12 sig β<0 (cols 2,8 null). Record: "10/12 sig β<0 (cols 2, 8 null)." MATCH.

**DivDummy (LaTeX line 566):** sig cols 2,3,5,6,8,10,12 = 7/12. Sign flip: cols 3,5 β>0; cols 2,6,8,10,12 β<0. Record: "7/12 sig with FE sign flip — cols 3, 5 ind contemp β>0; cols 2, 6, 8, 10, 12 firm β<0." MATCH.

**Extended controls (LaTeX lines 572–579):** DailyVola 8/8 sig β>0 (all extended cols 3-6, 9-12). StockPrice 8/8 sig. Turnover 8/8 sig β<0. UncQue: col 3 un-bolded, col 4 bolded **, col 5 **, col 6 **, col 9 un-bolded, col 10 **, col 11 **, col 12 ** → sig cols 4,5,6,10,11,12 = 6/8 sig (cols 3,9 null). Record: "UncQue 6/8 sig β<0 (cols 3, 9 null)." MATCH.

**§5.16 cross-reference (H7b 2/12):** LaTeX confirms 2 sig UncPreMgr cells at cols 3,9. Record claim in §5.16 "H7b 2/12 (level)." MATCH.

### Findings

- **[HIGH]** §4.1 row (line 151) states "Lagged_DV 0.71/0.61 ind / **0.60/0.39 firm**." The value 0.39 does not exist in the H7b table. LaTeX line 570 shows all firm-FE Lagged_DV cells = 0.5914–0.6261. The §4.2 block (line 522) correctly records "ind ~0.70, firm ~0.60." Error is confined to §4.1 summary row only; §4.2 is accurate.

### Verdict
1 HIGH + 0 MEDIUM + 0 LOW findings. §4.1 row Lagged_DV "0.39" is a fabricated value (likely copy-paste from firm-FE R² = 0.390 row); §4.2 block is clean.

---

## Batch C — Summary

| Suite | §4.1 row | §4.2 block | HIGH | MEDIUM | LOW |
|---|---|---|---|---|---|
| H7c | line 152 | lines 529–545 | 0 | 0 | 0 |
| H7e | line 154 | lines 565–581 | 1 | 0 | 0 |
| H7d | line 153 | lines 547–563 | 0 | 0 | 0 |
| H14b | line 156 | lines 601–617 | 1 | 0 | 0 |
| H14 | line 155 | lines 583–599 | 0 | 0 | 0 |
| H7b | line 151 | lines 511–527 | 1 | 0 | 0 |
| **TOTAL** | | | **3 HIGH** | **0 MEDIUM** | **0 LOW** |

### HIGH findings summary

1. **H7b §4.1** (line 151): "Lagged_DV 0.71/0.61 ind / **0.60/0.39 firm**" — value 0.39 does not exist in the table. LaTeX line 570 firm-FE Lagged_DV range = 0.591–0.626. Likely copy-paste of R² firm col 2 (0.390) into wrong field. §4.2 block is correct (says "firm ~0.60").

2. **H7e §4.2** (line 574): "Capex **10/12** sig β<0 (cols 2,6 null)" — LaTeX line 762 shows col 4 = -0.0021 (unbolded, null). Actual = **9/12** sig with nulls at cols **2,4,6**. Record under-counts nulls by 1 and overcounts sig by 1.

3. **H14b §4.2** (line 610): "DivDummy 7/12 sig with FE sign flip — cols **3,5** ind β>0; cols 2,4,6,8,10,12 firm β<0" — LaTeX line 1394 shows col 5 = 0.2743 (unbolded, NOT sig). Only col 3 is sig β>0. Total count 7/12 is coincidentally correct but the cell attribution for β>0 is wrong (col 5 listed as sig, it is null).

### §5 cross-reference verification results

- **§5.15 H7c "UncAnsCEO 6/6 sig β>0 ALL 6 contemp cells"**: CONFIRMED. LaTeX cols 1–6 all bolded **. Firm-FE cells (2,4,6) all sig.
- **§5.16 H7b "2/12 (level)"**: CONFIRMED. UncPreMgr sig at cols 3,9 only.
- **§5.18 H14b "UncAnsCEO 3/12 sig β>0 cols 8,10,12 firm-FE lead cells only"**: CONFIRMED. LaTeX cols 8,10,12 bold *; cols 7,9,11 (ind leads) unbolded.
- **§5.19 H14 near-null "1/48 sig"**: CONFIRMED. UncPreMgr col 6 * only.
- **§5.20 H7d "5/48 sig"**: CONFIRMED. UncPreCEO 4 + UncAnsMgr 1.

**Completed**: 2026-04-15, batch C adversarial audit.

