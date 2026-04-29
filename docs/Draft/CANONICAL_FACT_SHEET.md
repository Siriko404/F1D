# CANONICAL FACT SHEET — v6 thesis rewrite empirical audit

Generated 2026-04-29 14:28:39 via `scripts/adhoc/extract_canonical_facts.py`.

All numbers programmatically extracted from latest `suite_spec_*.json`.
AUTHORITY: this file. NOT memory docs. Memory locks are LLM-written and may contain hallucinated counts.

## Suite spec source files

- **H1.ceo2.decomp**: `h1_cash_holdings_ceo2iv_decomp\2026-04-29_142735\suite_spec_H1.ceo2.decomp.json`
- **H1.ceo2.decomp.qtrexp**: `h1_cash_holdings_ceo2iv_decomp_qtrexp\2026-04-29_142736\suite_spec_H1.ceo2.decomp.qtrexp.json`
- **H1.2.ceo2.decomp**: `h1_2_cash_constraint_ceo2iv_decomp\2026-04-29_142737\suite_spec_H1.2.ceo2.decomp.json`
- **H1.2.ceo2.decomp.qtrexp**: `h1_2_cash_constraint_ceo2iv_decomp_qtrexp\2026-04-29_142738\suite_spec_H1.2.ceo2.decomp.qtrexp.json`
- **H1.3.cfvol**: `h1_3_cfvol_moderation\2026-04-29_142744\suite_spec_H1.3.cfvol.json`
- **H11**: `h11_prisk_uncertainty\2026-04-29_142745\suite_spec_H11.json`
- **H11-Lag**: `h11_prisk_uncertainty_lag\2026-04-29_142746\suite_spec_H11-Lag2.json`
- **H23**: `h23_competition_uncertainty\2026-04-29_142747\suite_spec_H23.json`
- **H24**: `h24_us_epu\2026-04-29_142752\suite_spec_H24.json`
- **H24b**: `h24b_global_epu\2026-04-29_142753\suite_spec_H24b.json`
- **H14c.ceo2.decomp**: `h14c_spread_bgt_level_ceo2iv_decomp\2026-04-29_142756\suite_spec_H14c.ceo2.decomp.json`
- **H18.ceo2.decomp**: `h18_cccl_received_ceo2iv_decomp\2026-04-29_142757\suite_spec_H18.ceo2.decomp.json`
- **H.death.did**: `ceo_death_did_cash\2026-04-29_142804\suite_spec_H.death.did.json`
- **H.dwz.fd**: `h_dwz_fd_cash\2026-04-29_142806\suite_spec_H.dwz.fd.json`
- **H.lewbel.iv**: `h_lewbel_iv_cash\2026-04-29_142811\suite_spec_H.lewbel.iv.json`

## H1.ceo2.decomp — HC Full method (3-IV decomp)

**Cols**: 12  |  **n range**: 41,108 to 43,333

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO` | CEO Clarity (DWZ) | 9/12@.10 | 5/12@.05 | 0/12@.01 | -0.0170 to -0.0046 | 0.0362 |
| `UncResCEO` | CEO Residual Unc. (DWZ) | 12/12@.10 | 8/12@.05 | 0/12@.01 | +0.0016 to +0.0028 | 0.0198 |
| `UncPreCEO` | CEO Pres Uncertainty | 0/12@.10 | 0/12@.05 | 0/12@.01 | -0.0007 to +0.0009 | 0.2158 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CashRatio | industry | calendar_ | 43,333 | 1376 | 0.8253924072526952 |
| 2 | CashRatio | firm | calendar_ | 43,333 | 1376 | 0.43086950878848007 |
| 3 | CashRatio | industry | calendar_ | 43,316 | 1376 | 0.8289689826664935 |
| 4 | CashRatio | firm | calendar_ | 43,316 | 1376 | 0.4486947098027728 |
| 5 | CashRatio | industry | calendar_ | 43,316 | 1376 | 0.8299300183867196 |
| 6 | CashRatio | firm | calendar_ | 43,316 | 1376 | 0.44880698842637723 |
| 7 | CashRatio_le | industry | calendar_ | 41,122 | 1321 | 0.658649562024331 |
| 8 | CashRatio_le | firm | calendar_ | 41,122 | 1321 | 0.09232380357442438 |
| 9 | CashRatio_le | industry | calendar_ | 41,108 | 1321 | 0.6671845400746916 |
| 10 | CashRatio_le | firm | calendar_ | 41,108 | 1321 | 0.10834078846591311 |
| 11 | CashRatio_le | industry | calendar_ | 41,108 | 1321 | 0.6681160930272243 |
| 12 | CashRatio_le | firm | calendar_ | 41,108 | 1321 | 0.1080757635316858 |

---

## H1.ceo2.decomp.qtrexp — HC QtrExp method (within-tenure expanding)

**Cols**: 12  |  **n range**: 23,120 to 24,868

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO_QtrExp` | CEO Clarity (DWZ Qtr-Exp) | 9/12@.10 | 9/12@.05 | 6/12@.01 | -0.0215 to -0.0024 | 0.0008 |
| `UncResCEO_QtrExp` | CEO Residual Unc. (DWZ Qtr-Exp) | 12/12@.10 | 7/12@.05 | 1/12@.01 | +0.0016 to +0.0046 | 0.0082 |
| `UncPreCEO` | CEO Pres Uncertainty | 0/12@.10 | 0/12@.05 | 0/12@.01 | -0.0004 to +0.0016 | 0.2296 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CashRatio | industry | calendar_ | 24,868 | 1155 | 0.8388965849085562 |
| 2 | CashRatio | firm | calendar_ | 24,868 | 1155 | 0.45659541188323904 |
| 3 | CashRatio | industry | calendar_ | 24,855 | 1154 | 0.8417369561249337 |
| 4 | CashRatio | firm | calendar_ | 24,855 | 1154 | 0.4727425283173763 |
| 5 | CashRatio | industry | calendar_ | 24,855 | 1154 | 0.8420722876763038 |
| 6 | CashRatio | firm | calendar_ | 24,855 | 1154 | 0.47305845940199254 |
| 7 | CashRatio_le | industry | calendar_ | 23,127 | 1100 | 0.6747782081860915 |
| 8 | CashRatio_le | firm | calendar_ | 23,127 | 1100 | 0.08741965062047963 |
| 9 | CashRatio_le | industry | calendar_ | 23,120 | 1100 | 0.6825449711316214 |
| 10 | CashRatio_le | firm | calendar_ | 23,120 | 1100 | 0.10516384867023687 |
| 11 | CashRatio_le | industry | calendar_ | 23,120 | 1100 | 0.6826671001480319 |
| 12 | CashRatio_le | firm | calendar_ | 23,120 | 1100 | 0.10503842413706321 |

---

## H1.2.ceo2.decomp — HFC Full method (3-IV decomp + Unrated interaction)

**Cols**: 8  |  **n range**: 38,092 to 38,737

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO_c` | CEO Clarity (DWZ, c) | 4/8@.10 | 2/8@.05 | 0/8@.01 | -0.0157 to -0.0042 | 0.0363 |
| `UncResCEO_c` | CEO Residual Unc. (DWZ, c) | 8/8@.10 | 6/8@.05 | 0/8@.01 | +0.0018 to +0.0027 | 0.0226 |
| `UncPreCEO_c` | CEO Pres Unc. (c) | 0/8@.10 | 0/8@.05 | 0/8@.01 | -0.0008 to +0.0007 | 0.2879 |
| `Unrated` | Unrated | NO DATA |
| `UncResCEO_c_x_Unrated` | UncRes $\times$ Unrated | 2/8@.10 | 2/8@.05 | 0/8@.01 | -0.0001 to +0.0057 | 0.0230 |
| `UncPreCEO_c_x_Unrated` | UncPre $\times$ Unrated | 1/8@.10 | 0/8@.05 | 0/8@.01 | -0.0027 to +0.0029 | 0.0990 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CashRatio | industry | calendar_ | 38,737 | 1280 | 0.8272139316901881 |
| 2 | CashRatio | firm | calendar_ | 38,737 | 1280 | 0.43174178261041063 |
| 3 | CashRatio | industry | calendar_ | 38,737 | 1280 | 0.8285661989572233 |
| 4 | CashRatio | firm | calendar_ | 38,737 | 1280 | 0.4316802364124377 |
| 5 | CashRatio_le | industry | calendar_ | 38,092 | 1258 | 0.6669147872080667 |
| 6 | CashRatio_le | firm | calendar_ | 38,092 | 1258 | 0.10018980925638865 |
| 7 | CashRatio_le | industry | calendar_ | 38,092 | 1258 | 0.6689441397729543 |
| 8 | CashRatio_le | firm | calendar_ | 38,092 | 1258 | 0.10008259587494162 |

---

## H1.2.ceo2.decomp.qtrexp — HFC QtrExp method

**Cols**: 8  |  **n range**: 21,371 to 21,824

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO_QtrExp_c` | CEO Clarity (DWZ Qtr-Exp, c) | 6/8@.10 | 6/8@.05 | 4/8@.01 | -0.0187 to -0.0019 | 0.0006 |
| `UncResCEO_QtrExp_c` | CEO Residual Unc. (DWZ Qtr-Exp, c) | 8/8@.10 | 6/8@.05 | 0/8@.01 | +0.0021 to +0.0044 | 0.0130 |
| `UncPreCEO_c` | CEO Pres Unc. (c) | 0/8@.10 | 0/8@.05 | 0/8@.01 | -0.0005 to +0.0009 | 0.3406 |
| `Unrated` | Unrated | NO DATA |
| `UncResCEO_QtrExp_c_x_Unrated` | UncRes (Qtr-Exp) $\times$ Unrated | 2/8@.10 | 0/8@.05 | 0/8@.01 | +0.0013 to +0.0050 | 0.0936 |
| `UncPreCEO_c_x_Unrated` | UncPre $\times$ Unrated | 0/8@.10 | 0/8@.05 | 0/8@.01 | -0.0015 to +0.0017 | 0.2615 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CashRatio | industry | calendar_ | 21,824 | 1080 | 0.8409282956434685 |
| 2 | CashRatio | firm | calendar_ | 21,824 | 1080 | 0.4526033701956005 |
| 3 | CashRatio | industry | calendar_ | 21,824 | 1080 | 0.8414322202759893 |
| 4 | CashRatio | firm | calendar_ | 21,824 | 1080 | 0.4529533908341713 |
| 5 | CashRatio_le | industry | calendar_ | 21,371 | 1060 | 0.6790718972862781 |
| 6 | CashRatio_le | firm | calendar_ | 21,371 | 1060 | 0.09419901925287166 |
| 7 | CashRatio_le | industry | calendar_ | 21,371 | 1060 | 0.680030487673517 |
| 8 | CashRatio_le | firm | calendar_ | 21,371 | 1060 | 0.09416126874482378 |

---

## H1.3.cfvol — CFvol moderator (Han-Qiu 2007)

**Cols**: 8  |  **n range**: 38,671 to 40,795

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO_c` | CEO Clarity (DWZ, c) | 6/8@.10 | 3/8@.05 | 1/8@.01 | -0.0135 to -0.0058 | 0.0045 |
| `UncResCEO_c` | CEO Residual Unc. (DWZ, c) | 6/8@.10 | 4/8@.05 | 0/8@.01 | +0.0015 to +0.0025 | 0.0176 |
| `UncPreCEO_c` | CEO Pres Unc. (c) | 0/8@.10 | 0/8@.05 | 0/8@.01 | -0.0008 to +0.0007 | 0.2693 |
| `HighCFvol` | HighCFvol | NO DATA |
| `UncResCEO_c_x_HighCFvol` | UncRes $\times$ HighCFvol | 2/8@.10 | 0/8@.05 | 0/8@.01 | -0.0000 to +0.0048 | 0.0533 |
| `UncPreCEO_c_x_HighCFvol` | UncPre $\times$ HighCFvol | 4/8@.10 | 4/8@.05 | 2/8@.01 | +0.0002 to +0.0101 | 0.0052 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CashRatio | industry | calendar_ | 40,795 | 1303 | 0.8246414069302964 |
| 2 | CashRatio | firm | calendar_ | 40,795 | 1303 | 0.4472312026174745 |
| 3 | CashRatio | industry | calendar_ | 40,795 | 1303 | 0.8260882654958606 |
| 4 | CashRatio | firm | calendar_ | 40,795 | 1303 | 0.44738175114057965 |
| 5 | CashRatio_le | industry | calendar_ | 38,671 | 1242 | 0.6571361407238161 |
| 6 | CashRatio_le | firm | calendar_ | 38,671 | 1242 | 0.10284375739550089 |
| 7 | CashRatio_le | industry | calendar_ | 38,671 | 1242 | 0.658765394554586 |
| 8 | CashRatio_le | firm | calendar_ | 38,671 | 1242 | 0.10244145681998196 |

---

## H11 — PRisk driver (Hassan 2020)

**Cols**: 12  |  **n range**: 65,394 to 77,758

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `PRisk` | Political Risk$_{t}$ | 12/12@.10 | 12/12@.05 | 12/12@.01 | +0.0001 to +0.0003 | 0.0000 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | UncAnsMgr | industry | calendar_ | 77,658 | 1820 | 0.065651371536815 |
| 2 | UncAnsCEO | industry | calendar_ | 65,394 | 1728 | 0.05674958211420178 |
| 3 | UncPreMgr | industry | calendar_ | 77,758 | 1820 | 0.05262684430165909 |
| 4 | UncPreCEO | industry | calendar_ | 65,760 | 1730 | 0.043371388179577974 |
| 5 | UncAnsNoCEO | industry | calendar_ | 73,816 | 1794 | 0.018414244448948902 |
| 6 | UncPreNoCEO | industry | calendar_ | 76,549 | 1809 | 0.02896458357983489 |
| 7 | UncAnsMgr | firm | calendar_ | 77,658 | 1820 | 0.02597975461135449 |
| 8 | UncAnsCEO | firm | calendar_ | 65,394 | 1728 | 0.020856073624075155 |
| 9 | UncPreMgr | firm | calendar_ | 77,758 | 1820 | 0.018421743643387778 |
| 10 | UncPreCEO | firm | calendar_ | 65,760 | 1730 | 0.023121931151828146 |
| 11 | UncAnsNoCEO | firm | calendar_ | 73,816 | 1794 | 0.005263289786778813 |
| 12 | UncPreNoCEO | firm | calendar_ | 76,549 | 1809 | 0.004549407549014894 |

---

## H11-Lag — PRisk lagged driver

**Cols**: 12  |  **n range**: 62,674 to 74,561

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `PRisk_lag2` | PRisk$_{t-2}$ | 11/12@.10 | 11/12@.05 | 8/12@.01 | +0.0000 to +0.0001 | 0.0000 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | UncAnsMgr | industry | calendar_ | 74,467 | 1788 | 0.06334251541489933 |
| 2 | UncAnsCEO | industry | calendar_ | 62,674 | 1692 | 0.054869993597936206 |
| 3 | UncPreMgr | industry | calendar_ | 74,561 | 1788 | 0.047655584762410386 |
| 4 | UncPreCEO | industry | calendar_ | 63,022 | 1694 | 0.03475751485820977 |
| 5 | UncAnsNoCEO | industry | calendar_ | 70,842 | 1759 | 0.017244730329241675 |
| 6 | UncPreNoCEO | industry | calendar_ | 73,432 | 1778 | 0.02789041902898759 |
| 7 | UncAnsMgr | firm | calendar_ | 74,467 | 1788 | 0.02262251523870107 |
| 8 | UncAnsCEO | firm | calendar_ | 62,674 | 1692 | 0.01871470874447112 |
| 9 | UncPreMgr | firm | calendar_ | 74,561 | 1788 | 0.01295334451172181 |
| 10 | UncPreCEO | firm | calendar_ | 63,022 | 1694 | 0.01503753218345616 |
| 11 | UncAnsNoCEO | firm | calendar_ | 70,842 | 1759 | 0.004119742483764122 |
| 12 | UncPreNoCEO | firm | calendar_ | 73,432 | 1778 | 0.0035076583370087233 |

---

## H23 — TSIMM competition driver (Hoberg-Phillips)

**Cols**: 12  |  **n range**: 18,447 to 20,774

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `z_log_TotalSimilarity` | $z(\log(\mathrm{TSIMM}))$ | 5/12@.10 | 5/12@.05 | 3/12@.01 | -0.0239 to +0.0304 | 0.0000 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | UncAnsMgr | industry | calendar_ | 20,768 | 1625 | 0.10350013433440353 |
| 2 | UncAnsCEO | industry | calendar_ | 18,447 | 1513 | 0.10339993027293337 |
| 3 | UncPreMgr | industry | calendar_ | 20,774 | 1625 | 0.06402449563617307 |
| 4 | UncPreCEO | industry | calendar_ | 18,492 | 1516 | 0.050166305896663266 |
| 5 | UncAnsNoCEO | industry | calendar_ | 20,236 | 1600 | 0.029431580446639072 |
| 6 | UncPreNoCEO | industry | calendar_ | 20,513 | 1612 | 0.03479022844939694 |
| 7 | UncAnsMgr | firm | calendar_ | 20,768 | 1625 | 0.03781108090340779 |
| 8 | UncAnsCEO | firm | calendar_ | 18,447 | 1513 | 0.03788628643750602 |
| 9 | UncPreMgr | firm | calendar_ | 20,774 | 1625 | 0.017310667342867903 |
| 10 | UncPreCEO | firm | calendar_ | 18,492 | 1516 | 0.02127230648232603 |
| 11 | UncAnsNoCEO | firm | calendar_ | 20,236 | 1600 | 0.005841360158695075 |
| 12 | UncPreNoCEO | firm | calendar_ | 20,513 | 1612 | 0.0058381885240049725 |

---

## H24 — US EPU driver (BBD 2016)

**Cols**: 12  |  **n range**: 59,676 to 75,142

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `US_EPU_log` | $\log(\text{US EPU})_{t}$ | 7/12@.10 | 5/12@.05 | 2/12@.01 | +0.0006 to +0.0239 | 0.0008 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | UncAnsMgr | industry | calendar_ | 74,013 | 1822 | 0.17115583432974868 |
| 2 | UncPreMgr | industry | calendar_ | 75,142 | 1825 | 0.4837631426671819 |
| 3 | UncAnsCEO | industry | calendar_ | 59,676 | 1703 | 0.14126909017623535 |
| 4 | UncPreCEO | industry | calendar_ | 60,503 | 1701 | 0.29174302942078345 |
| 5 | UncAnsNoCEO | industry | calendar_ | 68,858 | 1783 | 0.05594927466955113 |
| 6 | UncPreNoCEO | industry | calendar_ | 73,835 | 1815 | 0.5922955135434143 |
| 7 | UncAnsMgr | firm | calendar_ | 74,013 | 1822 | 0.041242090991158276 |
| 8 | UncPreMgr | firm | calendar_ | 75,142 | 1825 | 0.18643072789249948 |
| 9 | UncAnsCEO | firm | calendar_ | 59,676 | 1703 | 0.030478101616549846 |
| 10 | UncPreCEO | firm | calendar_ | 60,503 | 1701 | 0.08392250726641481 |
| 11 | UncAnsNoCEO | firm | calendar_ | 68,858 | 1783 | 0.010386951573418401 |
| 12 | UncPreNoCEO | firm | calendar_ | 73,835 | 1815 | 0.2909954694757877 |

---

## H24b — Global EPU driver (Davis 2016)

**Cols**: 12  |  **n range**: 59,676 to 75,142

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `GEPU_log` | $\log(\text{GEPU})_{t}$ | 9/12@.10 | 5/12@.05 | 3/12@.01 | +0.0053 to +0.0309 | 0.0021 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | UncAnsMgr | industry | calendar_ | 74,013 | 1822 | 0.17120448722641013 |
| 2 | UncPreMgr | industry | calendar_ | 75,142 | 1825 | 0.48378694210089634 |
| 3 | UncAnsCEO | industry | calendar_ | 59,676 | 1703 | 0.14127973024988172 |
| 4 | UncPreCEO | industry | calendar_ | 60,503 | 1701 | 0.29171273490134286 |
| 5 | UncAnsNoCEO | industry | calendar_ | 68,858 | 1783 | 0.05595908176191544 |
| 6 | UncPreNoCEO | industry | calendar_ | 73,835 | 1815 | 0.5923007775786997 |
| 7 | UncAnsMgr | firm | calendar_ | 74,013 | 1822 | 0.04131038465279857 |
| 8 | UncPreMgr | firm | calendar_ | 75,142 | 1825 | 0.1864582255607906 |
| 9 | UncAnsCEO | firm | calendar_ | 59,676 | 1703 | 0.03050015761110303 |
| 10 | UncPreCEO | firm | calendar_ | 60,503 | 1701 | 0.08386683679012397 |
| 11 | UncAnsNoCEO | firm | calendar_ | 68,858 | 1783 | 0.010398145440197015 |
| 12 | UncPreNoCEO | firm | calendar_ | 73,835 | 1815 | 0.29100043793516295 |

---

## H14c.ceo2.decomp — Bid-ask spread 25-day post-call (3-IV decomp)

**Cols**: 12  |  **n range**: 42,625 to 43,049

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO` | CEO Clarity (DWZ) | 0/12@.10 | 0/12@.05 | 0/12@.01 | -0.1886 to +1.1056 | 0.2131 |
| `UncResCEO` | CEO Residual Uncertainty (DWZ) | 0/12@.10 | 0/12@.05 | 0/12@.01 | -0.1021 to +0.0984 | 0.2312 |
| `UncPreCEO` | CEO Pres Uncertainty | 4/12@.10 | 3/12@.05 | 2/12@.01 | -0.1072 to +0.3496 | 0.0026 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | BGTLevel_Spr | industry | calendar_ | 42,625 | 1384 | 0.7029557282916269 |
| 2 | BGTLevel_Spr | firm | calendar_ | 42,625 | 1384 | 0.5173640007812386 |
| 3 | BGTLevel_Spr | industry | calendar_ | 42,625 | 1384 | 0.720913607030197 |
| 4 | BGTLevel_Spr | firm | calendar_ | 42,625 | 1384 | 0.5505193794348646 |
| 5 | BGTLevel_Spr | industry | calendar_ | 42,625 | 1384 | 0.730193644849083 |
| 6 | BGTLevel_Spr | firm | calendar_ | 42,625 | 1384 | 0.5478540002916826 |
| 7 | BGTLevel_Spr | industry | calendar_ | 43,049 | 1391 | 0.7001449982578387 |
| 8 | BGTLevel_Spr | firm | calendar_ | 43,049 | 1391 | 0.4992051985463294 |
| 9 | BGTLevel_Spr | industry | calendar_ | 43,049 | 1391 | 0.7019790629106574 |
| 10 | BGTLevel_Spr | firm | calendar_ | 43,049 | 1391 | 0.503787770960234 |
| 11 | BGTLevel_Spr | industry | calendar_ | 43,049 | 1391 | 0.7232112775767735 |
| 12 | BGTLevel_Spr | firm | calendar_ | 43,049 | 1391 | 0.5228130858196192 |

---

## H18.ceo2.decomp — SEC comment letter receipt (3-IV decomp)

**Cols**: 6  |  **n range**: 44,096 to 44,113

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|
| `ClarityCEO` | CEO Clarity (DWZ) | 0/6@.10 | 0/6@.05 | 0/6@.01 | +0.0039 to +0.0062 | 0.9054 |
| `UncResCEO` | CEO Residual Uncertainty (DWZ) | 0/6@.10 | 0/6@.05 | 0/6@.01 | -0.0004 to -0.0003 | 0.6287 |
| `UncPreCEO` | CEO Pres Uncertainty | 4/6@.10 | 1/6@.05 | 0/6@.01 | +0.0007 to +0.0016 | 0.0144 |

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | CCCL | industry | calendar_ | 44,113 | 1402 | 0.0005533812141436112 |
| 2 | CCCL | firm | calendar_ | 44,113 | 1402 | 0.0019017740114004589 |
| 3 | CCCL | industry | calendar_ | 44,096 | 1402 | 0.0002791049534833778 |
| 4 | CCCL | firm | calendar_ | 44,096 | 1402 | 0.00199458321854451 |
| 5 | CCCL | industry | calendar_ | 44,096 | 1402 | 0.0005486507623437831 |
| 6 | CCCL | firm | calendar_ | 44,096 | 1402 | 0.001954479203537085 |

---

## H.death.did — CEO sudden-death DiD (Phase E)

**Cols**: 4  |  **n range**: 338 to 338

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | ? | ? | ? | 338 | 16 | 0.4056429378689954 |
| 2 | ? | ? | ? | 338 | 16 | 0.32046708712685523 |
| 3 | ? | ? | ? | 338 | 16 | 0.4204759120324185 |
| 4 | ? | ? | ? | 338 | 16 | 0.32012833326252865 |

---

## H.dwz.fd — DWZ §6 first-difference (turnover replication)

**Cols**: 3  |  **n range**: 659 to 659

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | ? | ? | ? | 659 | 516 | 0.10790002053301462 |
| 2 | ? | ? | ? | 659 | 516 | 0.12841510728986005 |
| 3 | ? | ? | ? | 659 | 516 | 0.058960395941239696 |

---

## H.lewbel.iv — Lewbel 2012 heteroskedasticity-based IV

**Cols**: 3  |  **n range**: 43,454 to 43,471

| IV key | Label | sig p<.10 | sig p<.05 | sig p<.01 | beta range | min p |
|---|---|---|---|---|---|---|

**Per-column n + DV + FE**:

| col | dv | fe_entity | fe_time | n_obs | n_firms | r2 |
|---|---|---|---|---|---|---|
| 1 | ? | ? | ? | 43,471 | 1423 | 0.863465468839582 |
| 2 | ? | ? | ? | 43,471 | 1423 | 0.8632657751946057 |
| 3 | ? | ? | ? | 43,454 | 1423 | 0.8639087415073533 |

---
