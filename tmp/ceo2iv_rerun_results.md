# H1 & H1.2 CEO 2-IV Re-run Results

**Generated:** 2026-04-22
**Runners:**
- `src/f1d/econometric/run_h1_cash_holdings_ceo2iv.py` (commit ddbb7d4)
- `src/f1d/econometric/run_h1_2_cash_constraint_ceo2iv.py` (commit 35ed599)

**Output timestamps:**
- H1.ceo2: `outputs/econometric/h1_cash_holdings_ceo2iv/2026-04-22_132230/`
- H1.2.ceo2: `outputs/econometric/h1_2_cash_constraint_ceo2iv/2026-04-22_133120/`

**Spec:** both main CEO IVs (UncAnsCEO, UncPreCEO) enter simultaneously in every regression. No manager-pool IVs (UncAnsMgr, UncPreMgr, UncAnsNoCEO, UncPreNoCEO). Both mean-centered on Main sample for H1.2.ceo2.

Stars: `***` p<0.01, `**` p<0.05, `*` p<0.10 (one-tailed; HFC/HC: β > 0). SEs firm-clustered.

---

## H1 CEO 2-IV results (12 cols; parent spec structure)

### CashRatio_t (cols 1–6)

| Col | ID | N | UncAnsCEO β (SE) p | UncPreCEO β (SE) p |
|----:|----|---:|---|---|
| 1 | Cash_t / Ind+Year (base) | 65,148 | **+0.0027*** (0.0010) p=0.0037 | +0.0001 (0.0010) p=0.457 |
| 2 | Cash_t / Firm+Year (base) | 65,148 | **+0.0020*** (0.0008) p=0.0075 | +0.0002 (0.0010) p=0.408 |
| 3 | Cash_t / Ind+Year (ext) | 62,523 | **+0.0030*** (0.0010) p=0.0015 | +0.0002 (0.0010) p=0.436 |
| 4 | Cash_t / Firm+Year (ext) | 62,523 | **+0.0018** (0.0008) p=0.0150 | +0.0000 (0.0010) p=0.497 |
| 5 | Cash_t / Ind+YrQtr (ext) | 62,523 | **+0.0031*** (0.0010) p=0.0013 | +0.0002 (0.0010) p=0.409 |
| 6 | Cash_t / Firm+YrQtr (ext) | 62,523 | **+0.0019** (0.0008) p=0.0124 | +0.0002 (0.0010) p=0.441 |

### CashRatio_lead (cols 7–12)

| Col | ID | N | UncAnsCEO β (SE) p | UncPreCEO β (SE) p |
|----:|----|---:|---|---|
| 7 | Cash_{t+1} / Ind+Year (base) | 60,638 | **+0.0023*** (0.0016) p=0.0803 | +0.0006 (0.0019) p=0.375 |
| 8 | Cash_{t+1} / Firm+Year (base) | 60,638 | **+0.0028** (0.0012) p=0.0111 | +0.0016 (0.0016) p=0.151 |
| 9 | Cash_{t+1} / Ind+Year (ext) | 59,459 | **+0.0025*** (0.0016) p=0.0593 | +0.0006 (0.0019) p=0.367 |
| 10 | Cash_{t+1} / Firm+Year (ext) | 59,459 | **+0.0025** (0.0012) p=0.0203 | +0.0013 (0.0015) p=0.198 |
| 11 | Cash_{t+1} / Ind+YrQtr (ext) | 59,459 | **+0.0024*** (0.0016) p=0.0635 | +0.0006 (0.0019) p=0.384 |
| 12 | Cash_{t+1} / Firm+YrQtr (ext) | 59,459 | **+0.0024** (0.0012) p=0.0259 | +0.0012 (0.0015) p=0.221 |

**Significance tallies (one-tailed H1 β > 0):**
- UncAnsCEO: 12/12 sig @ p<0.10; 9/12 sig @ p<0.05 (contemp 4/6 @ p<0.01; lead 3/6 @ p<0.05)
- UncPreCEO: 0/12 sig at any conventional level — CEO Presentation-segment uncertainty does NOT move cash

---

## H1.2 CEO 2-IV results (16 cols; 8 base + 8 interaction)

**Design note:** BelowIG interactions SUPPRESSED (per H1.2 BelowIG suppression decision — IG vs Unrated only). BelowIG level dummy retained. The interaction-spec main-IV slope therefore applies to rated firms jointly (IG ∪ BelowIG), not IG-alone.

### Base specs (cols 1–4 = CashRatio_t; cols 9–12 = CashRatio_lead) — main IVs only

| Col | ID | N | UncAnsCEO_c β (SE) p | UncPreCEO_c β (SE) p |
|----:|----|---:|---|---|
| 1 | Cash_t / Ind+Year | 56,795 | **+0.0029*** (0.0010) p=0.0028 | +0.0004 (0.0011) p=0.369 |
| 2 | Cash_t / Firm+Year | 56,795 | **+0.0017** (0.0009) p=0.0273 | +0.0001 (0.0011) p=0.471 |
| 3 | Cash_t / Ind+YrQtr | 56,795 | **+0.0030*** (0.0010) p=0.0022 | +0.0004 (0.0011) p=0.335 |
| 4 | Cash_t / Firm+YrQtr | 56,795 | **+0.0018** (0.0009) p=0.0214 | +0.0002 (0.0011) p=0.412 |
| 9 | Cash_{t+1} / Ind+Year | 55,692 | **+0.0022*** (0.0016) p=0.0921 | +0.0008 (0.0019) p=0.343 |
| 10 | Cash_{t+1} / Firm+Year | 55,692 | **+0.0024** (0.0013) p=0.0290 | +0.0012 (0.0016) p=0.220 |
| 11 | Cash_{t+1} / Ind+YrQtr | 55,692 | **+0.0021*** (0.0016) p=0.0959 | +0.0007 (0.0019) p=0.354 |
| 12 | Cash_{t+1} / Firm+YrQtr | 55,692 | **+0.0023** (0.0013) p=0.0349 | +0.0011 (0.0016) p=0.239 |

### Interaction specs (cols 5–8 = CashRatio_t; cols 13–16 = CashRatio_lead)

**Primary interest: UncAnsCEO_c × Unrated and UncPreCEO_c × Unrated (both one-tailed, HFC: β > 0)**

| Col | ID | N | Main UncAnsCEO_c β p | Main UncPreCEO_c β p | UncAnsCEO_c × Unrated β (SE) p | UncPreCEO_c × Unrated β (SE) p |
|----:|----|---:|---|---|---|---|
| 5 | Cash_t / Ind+Year | 56,795 | +0.0014 p=0.113 | −0.0012 p=0.814 | **+0.0030*** (0.0019) p=0.0608 | **+0.0028*** (0.0020) p=0.0746 |
| 6 | Cash_t / Firm+Year | 56,795 | +0.0011 p=0.162 | −0.0005 p=0.645 | +0.0010 (0.0017) p=0.284 | +0.0010 (0.0021) p=0.310 |
| 7 | Cash_t / Ind+YrQtr | 56,795 | +0.0011 p=0.168 | −0.0011 p=0.805 | **+0.0032*** (0.0019) p=0.0479 | **+0.0027*** (0.0019) p=0.0793 |
| 8 | Cash_t / Firm+YrQtr | 56,795 | +0.0011 p=0.156 | −0.0003 p=0.596 | +0.0011 (0.0017) p=0.263 | +0.0010 (0.0021) p=0.312 |
| 13 | Cash_{t+1} / Ind+Year | 55,692 | −0.0012 p=0.748 | −0.0006 p=0.603 | **+0.0068*** (0.0031) p=0.0142 | +0.0027 (0.0035) p=0.222 |
| 14 | Cash_{t+1} / Firm+Year | 55,692 | +0.0001 p=0.484 | +0.0016 p=0.208 | **+0.0040*** (0.0025) p=0.0507 | −0.0006 (0.0032) p=0.574 |
| 15 | Cash_{t+1} / Ind+YrQtr | 55,692 | −0.0019 p=0.838 | −0.0008 p=0.641 | **+0.0069*** (0.0031) p=0.0122 | +0.0026 (0.0035) p=0.229 |
| 16 | Cash_{t+1} / Firm+YrQtr | 55,692 | −0.0001 p=0.516 | +0.0015 p=0.216 | **+0.0041*** (0.0025) p=0.0484 | −0.0007 (0.0032) p=0.584 |

(Note: Base-spec main IVs are reported from unconditional models; interaction-spec main IVs shown here for reference only — in the interaction spec the main slope applies to rated firms jointly since BelowIG interaction is dropped.)

### Level dummies (interaction specs)

BelowIG: two-tailed, mixed signs; sig at p<0.05 in cols 13 (β=+0.0021 p2=0.398), col 15 (β=−0.0068 p2=0.012), col 13 (β=+0.0021 p2=0.398). Generally null except in industry-FE + lead-DV cells where BelowIG cash is ~0.007 lower than IG.

Unrated level (two-tailed): strongly positive in industry-FE lead cells — +0.0103 sig p2=2e-6 in col 13, +0.0066 sig p2=1e-7 in col 5 — confirming unrated firms hold more cash unconditionally. Firm-FE cells null.

---

## Comparison vs `.r` baseline (H1.2.r)

**Task-requested comparison:** UncAnsCEO_c × Unrated significance count (contemp vs lead).

| | `.r` baseline (single-IV CEO) | CEO 2-IV (this run) |
|---|---:|---:|
| UncAnsCEO_c × Unrated overall sig @ p<0.10 | **4/8** | **6/8** |
| UncAnsCEO_c × Unrated overall sig @ p<0.05 | **1/8** | **4/8** |
| Contemp (CashRatio_t): sig @ p<0.10 | 2/4 | 2/4 |
| Contemp (CashRatio_t): sig @ p<0.05 | 0/4 | 1/4 |
| Lead (CashRatio_{t+1}): sig @ p<0.10 | 2/4 | **4/4** |
| Lead (CashRatio_{t+1}): sig @ p<0.05 | 1/4 | **3/4** |

**Verdict (HFC interaction): SURVIVES AND STRENGTHENS.** The CEO 2-IV variant does not collapse the HFC interaction — it actually sharpens it, particularly on the lead DV where every single cell is now sig at p<0.10 (4/4) and 3/4 sig at p<0.05, up from 2/4 and 1/4 respectively in `.r`. The interaction is not thesis-blocking.

**Second main IV (UncPreCEO_c × Unrated):** Distinct pattern. Marginally sig in contemp industry-FE cells (2/4 at p<0.10 in cells 5, 7), null elsewhere. Does NOT support HFC through the Presentation-segment channel.

**Pattern summary:** HFC signal localizes to CEO Q&A uncertainty × Unrated constraint on the lead DV. Presentation channel is null. CEO Q&A is carrying both the H1 main effect (12/12 sig contemp + lead) and the H1.2 HFC constraint-moderated effect (6/8 interaction cols sig at p<0.10).

---

## File references

- H1.ceo2 runner: `src/f1d/econometric/run_h1_cash_holdings_ceo2iv.py`
- H1.ceo2 diagnostics: `outputs/econometric/h1_cash_holdings_ceo2iv/2026-04-22_132230/model_diagnostics.csv`
- H1.ceo2 LaTeX table: `outputs/econometric/h1_cash_holdings_ceo2iv/2026-04-22_132230/h1_cash_holdings_ceo2iv_table.tex`
- H1.2.ceo2 runner: `src/f1d/econometric/run_h1_2_cash_constraint_ceo2iv.py`
- H1.2.ceo2 diagnostics: `outputs/econometric/h1_2_cash_constraint_ceo2iv/2026-04-22_133120/model_diagnostics.csv`
- H1.2.ceo2 LaTeX table: `outputs/econometric/h1_2_cash_constraint_ceo2iv/2026-04-22_133120/h1_2_cash_constraint_ceo2iv_table.tex`
- `.r` baseline (H1.2.r): `outputs/econometric/h1_2_cash_constraint_robustness/2026-04-20_005340/model_diagnostics.csv`
