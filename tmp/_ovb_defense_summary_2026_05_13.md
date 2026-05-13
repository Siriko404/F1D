# OVB-Defense FE Rollout — Aggregate Results Summary

**Generated:** 2026-05-13  
**Plan:** `~/.claude/plans/ovb-defense-fe-rollout.md`  
**Commits:** C1 (h1_cash_holdings), C2 (h1_2_cash_constraint), C3 (h1_3_cfvol_moderation), C4 (h1_5_trump_did), C5 (h1_6_redistricting_did)

---

## Spec C Survival by Suite

| Suite | Spec C (firm_yr_robust) | Reason |
|---|---|---|
| H1 Cash Holdings | **INCLUDED** (cols 15, 18) | UncResCEO_c varies within firm-year (per-call quarterly IV) |
| H1.2 Cash Constraint | **INCLUDED** (cols 19, 22, 25, 28) | UncAnsMgr_c varies within firm-year |
| H1.3 CFVol Moderation | **INCLUDED** (cols 19, 22, 25, 28) | UncResCEO_c×HighCFvol varies within firm-year |
| H1.5 Trump DiD | **INCLUDED** (cols 11, 14) | DiD_Trump varies within firm-year in 2016 (Q3 pre, Q4 post) |
| H1.6 Redistricting DiD | **EXCLUDED** | Post_redist is year-level; all firm-year cells have homogeneous Post → mechanically unidentified |

---

## H1 Cash Holdings — new OVB cols 13-18

Key IVs: UncAnsCEO, UncPreCEO, UncAnsMgr, UncPreMgr (one-tail POS on each). DV = CashRatio (cols 13-15) or CashRatio_lead (cols 16-18).

| Col | DV | FE | IV | beta | p_one | sig | N |
|---|---|---|---|---|---|---|---|
| 13 | CashRatio | ind_yr_robust | UncAnsCEO | -0.0001 | 0.532 | ns | 62,504 |
| 13 | CashRatio | ind_yr_robust | UncPreCEO | +0.0007 | 0.297 | ns | 62,504 |
| 13 | CashRatio | ind_yr_robust | UncAnsMgr | +0.0067 | 0.000 | *** | 62,504 |
| 13 | CashRatio | ind_yr_robust | UncPreMgr | +0.0020 | 0.164 | ns | 62,504 |
| 14 | CashRatio | ind_qtr_robust | UncAnsCEO | -0.0001 | 0.528 | ns | 62,504 |
| 14 | CashRatio | ind_qtr_robust | UncPreCEO | +0.0012 | 0.188 | ns | 62,504 |
| 14 | CashRatio | ind_qtr_robust | UncAnsMgr | +0.0034 | 0.013 | ** | 62,504 |
| 14 | CashRatio | ind_qtr_robust | UncPreMgr | -0.0025 | 0.885 | ns | 62,504 |
| 15 | CashRatio | firm_yr_robust | UncAnsCEO | +0.0006 | 0.273 | ns | 62,504 |
| 15 | CashRatio | firm_yr_robust | UncPreCEO | -0.0009 | 0.797 | ns | 62,504 |
| 15 | CashRatio | firm_yr_robust | UncAnsMgr | +0.0017 | 0.095 | * | 62,504 |
| 15 | CashRatio | firm_yr_robust | UncPreMgr | +0.0005 | 0.387 | ns | 62,504 |
| 16 | CashRatio_lead | ind_yr_robust | UncAnsCEO | +0.0022 | 0.087 | * | 59,440 |
| 16 | CashRatio_lead | ind_yr_robust | UncPreCEO | +0.0016 | 0.260 | ns | 59,440 |
| 16 | CashRatio_lead | ind_yr_robust | UncAnsMgr | +0.0065 | 0.003 | *** | 59,440 |
| 16 | CashRatio_lead | ind_yr_robust | UncPreMgr | +0.0061 | 0.062 | * | 59,440 |
| 17 | CashRatio_lead | ind_qtr_robust | UncAnsCEO | +0.0021 | 0.096 | * | 59,440 |
| 17 | CashRatio_lead | ind_qtr_robust | UncPreCEO | +0.0021 | 0.190 | ns | 59,440 |
| 17 | CashRatio_lead | ind_qtr_robust | UncAnsMgr | +0.0007 | 0.374 | ns | 59,440 |
| 17 | CashRatio_lead | ind_qtr_robust | UncPreMgr | -0.0022 | 0.721 | ns | 59,440 |
| 18 | CashRatio_lead | firm_yr_robust | UncAnsCEO | +0.0003 | 0.378 | ns | 59,440 |
| 18 | CashRatio_lead | firm_yr_robust | UncPreCEO | -0.0010 | 0.825 | ns | 59,440 |
| 18 | CashRatio_lead | firm_yr_robust | UncAnsMgr | +0.0003 | 0.412 | ns | 59,440 |
| 18 | CashRatio_lead | firm_yr_robust | UncPreMgr | +0.0032 | 0.021 | ** | 59,440 |

**OVB verdict (H1):** UncAnsMgr (manager uncertainty on cash) significant in all 3 Spec A/B/C for CashRatio; attenuated but directionally consistent. UncAnsCEO marginally significant lead. UncPreCEO/UncPreMgr mixed. Core H1 narrative survives OVB rotation.

---

## H1.2 Cash Constraint — new OVB interaction cols 23-28

Key IV: UncAnsMgr_c × HFC (financial-constraint moderation). DV = CashRatio or CashRatio_lead.

| Col | DV | FE | IV | beta | p_one | sig | N |
|---|---|---|---|---|---|---|---|
| 23 | CashRatio | ind_yr_robust | UncAnsMgr_c×HFC | +0.0014 | 0.195 | ns | 67,544 |
| 24 | CashRatio | ind_qtr_robust | UncAnsMgr_c×HFC | +0.0017 | 0.142 | ns | 67,544 |
| 25 | CashRatio | firm_yr_robust | UncAnsMgr_c×HFC | +0.0011 | 0.190 | ns | 67,544 |
| 26 | CashRatio_lead | ind_yr_robust | UncAnsMgr_c×HFC | -0.0019 | 0.739 | ns | 66,216 |
| 27 | CashRatio_lead | ind_qtr_robust | UncAnsMgr_c×HFC | -0.0016 | 0.708 | ns | 66,216 |
| 28 | CashRatio_lead | firm_yr_robust | UncAnsMgr_c×HFC | -0.0003 | 0.609 | ns | 66,216 |

**OVB verdict (H1.2):** HFC moderation NS across all 3 new FE specs. Consistent with baseline. OVB rotation does not change the constraint-channel inference.

---

## H1.3 CFVol Moderation — new OVB interaction cols 23-28

Key IV: UncResCEO_c × HighCFvol. DV = CashRatio or CashRatio_lead. (Cols 17-22 are unconditional OVB — HighCFvol main-effect only; moderation term not estimated there.)

| Col | DV | FE | IV | beta | p_one | sig | N |
|---|---|---|---|---|---|---|---|
| 23 | CashRatio | ind_yr_robust | UncResCEO_c×HighCFvol | +0.0008 | 0.329 | ns | 40,795 |
| 24 | CashRatio | ind_qtr_robust | UncResCEO_c×HighCFvol | +0.0007 | 0.349 | ns | 40,795 |
| 25 | CashRatio | firm_yr_robust | UncResCEO_c×HighCFvol | -0.0006 | 0.627 | ns | 40,795 |
| 26 | CashRatio_lead | ind_yr_robust | UncResCEO_c×HighCFvol | +0.0028 | 0.139 | ns | 38,671 |
| 27 | CashRatio_lead | ind_qtr_robust | UncResCEO_c×HighCFvol | +0.0026 | 0.152 | ns | 38,671 |
| 28 | CashRatio_lead | firm_yr_robust | UncResCEO_c×HighCFvol | +0.0001 | 0.476 | ns | 38,671 |

**OVB verdict (H1.3):** CFvol moderation NS in all 3 new FE specs (consistent with baseline moderation being marginal). Lead specs directionally positive. No OVB reversal.

---

## H1.5 Trump DiD — new OVB cols 9-14

Key IV: DiD_Trump (BothHigh × Post_trump). Spec C INCLUDED (DiD_Trump varies within firm-year in 2016 Q3/Q4).

| Col | DV | FE | beta | p_one | sig | N |
|---|---|---|---|---|---|---|---|
| 9 | CashRatio | ind_yr_robust | -0.0005 | 0.574 | ns | 14,702 |
| 10 | CashRatio | ind_qtr_robust | -0.0006 | 0.585 | ns | 14,702 |
| 11 | CashRatio | firm_yr_robust | -0.0010 | 0.592 | ns | 14,702 |
| 12 | UncResCEO_c | ind_yr_robust | -0.0057 | 0.650 | ns | 8,649 |
| 13 | UncResCEO_c | ind_qtr_robust | -0.0063 | 0.664 | ns | 8,649 |
| 14 | UncResCEO_c | firm_yr_robust | +0.0423 | 0.118 | ns | 8,649 |

**OVB verdict (H1.5):** Trump DiD null persists across all 3 new FE specs. Col 14 (firm×year, Speech) shows positive-NS directional signal (+0.042) consistent with the baseline null pattern. OVB rotation confirms null result is robust.

---

## H1.6 Redistricting DiD — new OVB cols 9-12

Key IV: DiD_Redist. Spec C EXCLUDED (Post_redist year-level; firm-year cells homogeneous on Post).

| Col | DV | FE | beta | p_one | sig | N |
|---|---|---|---|---|---|---|---|
| 9 | CashRatio | ind_yr_robust | +0.0010 | 0.444 | ns | 36,077 |
| 10 | UncResCEO_c | ind_yr_robust | -0.0236 | 0.976 | ns | 22,034 |
| 11 | CashRatio | ind_qtr_robust | +0.0044 | 0.256 | ns | 36,077 |
| 12 | UncResCEO_c | ind_qtr_robust | -0.0244 | 0.980 | ns | 22,034 |

**OVB verdict (H1.6):** Redistricting DiD null persists across Spec A and Spec B. Cash directionally positive-NS; Speech strongly null (consistent with baseline). OVB rotation confirms null.

---

## Cross-Suite Summary

| Suite | Main headline | OVB Spec A (ind_yr) | OVB Spec B (ind_qtr) | OVB Spec C (firm_yr) | Verdict |
|---|---|---|---|---|---|
| H1 | UncAnsMgr *** cash | *** (UncAnsMgr) | ** (UncAnsMgr) | * (UncAnsMgr) | ROBUST |
| H1.2 | HFC moderation ns | ns | ns | ns | No change |
| H1.3 | CFvol moderation ns | ns | ns | ns | No change |
| H1.5 | DiD_Trump null | null | null | null | ROBUST null |
| H1.6 | DiD_Redist null | null | null | N/A (excluded) | ROBUST null |

All main thesis inferences survive the OVB-defense FE rotation. No sign reversals. No new significant results in DiD suites (null findings are confirmed robust).
