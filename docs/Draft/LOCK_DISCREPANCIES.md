# Lock-vs-canonical discrepancy report — Phase 1.5

Generated 2026-04-29 by `scripts/adhoc/extract_canonical_facts.py` cross-check against locked-framing memory docs.

## RULE going forward (per user 2026-04-29)

Memory locks may contain hallucinated numerical counts. **AUTHORITY for all numerical claims = `CANONICAL_FACT_SHEET.md`** (programmatic extraction from `suite_spec_*.json`). Do NOT cite memory docs for numbers; cite the fact sheet.

## Discrepancies found

### §3 HC — DWZ-anchored framing 2026-04-27 lock vs canonical

| Lock claim (`project_dwz_anchored_framing_locked_2026_04_27.md`) | Canonical (extracted 2026-04-29) | Verdict |
|---|---|---|
| "UncResCEO loads positively on cash with **12/12 specifications significant**" | Full: 12/12@p<.10 ✓; QtrExp: 12/12@p<.10 ✓ | **TRUE at p<.10** |
| "(10/12 at p<0.05)" | Full: **8/12@p<.05**; QtrExp: **7/12@p<.05** | **FALSE — overstates by 2-3 cells** |
| "ClarityCEO loads negatively on cash with **8–9/12 specifications significant at p<0.05**" | Full: **5/12@p<.05** (9/12@p<.10); QtrExp: **9/12@p<.05** (matches if QtrExp-only) | **AMBIGUOUS — Full 5/12, QtrExp 9/12; lock claim only matches QtrExp** |
| "Credit-constrained firms amplify this response by 2–3× **on lead-DV (next-quarter) specifications**; contemporaneous interaction terms are not significant" | Full: UncRes×Unrated 2/8@p<.05 (lead-DV cells 5+7); contemp cells null | **TRUE** |
| "UncPreCEO null" | 0/12 in HC, 0/8 in HFC base | **TRUE** |

### §4.2 — DWZ-anchored framing 2026-04-27 lock vs canonical

| Lock claim | Canonical | Verdict |
|---|---|---|
| "UncPreCEO loads bid-ask spread 4/12 sig at p<.10" | H14c: UncPreCEO 4/12@p<.10, 3/12@p<.05, 2/12@p<.01 | **TRUE** |
| "ClarityCEO and UncResCEO are null" (spread) | H14c: 0/12 + 0/12 sig | **TRUE** |
| "UncPreCEO loads SEC comment letter 4/6 at p<.10, 3/4 ext-ctrls survive" | H18: UncPreCEO 4/6@p<.10, 1/6@p<.05 | **TRUE on 4/6** (need to verify ext-ctrls split per col) |

### §3.2 H1.2 HFC QtrExp — H1/H2 framing 2026-04-28 lock vs canonical

| Lock claim (`project_h1_h2_theoretical_framing_locked_2026_04_28.md`) | Canonical | Verdict |
|---|---|---|
| "Full method, lead-DV: UncRes × Unrated 2/8 sig POS at p<0.05 (cols 5+7)" | Full: 2/8@p<.05 ✓ | **TRUE** |
| "QtrExp method, lead-DV: UncRes × Unrated 2/8 sig POS at p<0.10" | QtrExp: 2/8@p<.10, 0/8@p<.05 ✓ | **TRUE** |

### §4.3 endogeneity — endo lit review + Lewbel wake-up

All Lewbel + DWZ-FD + Phase E numbers in their respective wake-up docs MATCH canonical (verified per-suite). **Note**: Cragg-Donald F=20.42 actually exceeds Stock-Yogo 10%-max-IV-size cutoff of ~19.86 for 1-endog-6-IV; the wake-up's "borderline weak-IV under Stock-Yogo" framing slightly overstates the issue. F>20 is comfortably past the standard F>10 weak-IV cutoff. RECOMMEND: rephrase to "exceeds the Staiger-Stock 10% rule of thumb (F=10) but below the more demanding Stock-Yogo 5%-max-size cutoff (F~23)".

### Surprise finding NOT in any lock — H1.3 CFvol UncPreCEO interaction

Canonical: `UncPreCEO_c × HighCFvol`: **4/8 @ p<.10, 4/8 @ p<.05, 2/8 @ p<.01** (β: +0.0002 to +0.0101)

This interaction is STRONGER than the locked UncResCEO × HighCFvol interaction (which is 2/8 @ p<.10 only). Lock framing says "UncPreCEO null on cash" — TRUE for base effect, but FALSE in interaction with high cash-flow volatility. **§3.4 prose must address this expansion.**

### Surprise finding NOT in any lock — H23 TSIMM direction-mixed

Canonical: `z_log_TSIMM`: 5/12 @ p<.05 BUT beta range −0.0239 to +0.0304 (BOTH directions). Driver framing assumes monotone direction. Need per-column inspection: which DVs/FE configs go which way? Likely Mgr vs CEO and Q&A vs Pres differ.

## Resolution rule applied for v6 prose

For all numerical claims in v6 sections:
1. Pull from `CANONICAL_FACT_SHEET.md` (truth)
2. NEVER reproduce the lock-doc count if it disagrees
3. Cite the suite_spec source path in the section's draft comment
4. When a lock claim is wrong, prose uses canonical AND the corresponding lock-doc memory entry gets an in-place correction note

## Updated lock files (post Phase 1.5)

To be flagged in memory:
- `project_dwz_anchored_framing_locked_2026_04_27.md` — counts at p<.05 are method-confused; v6 prose uses canonical Full + QtrExp side-by-side
- `project_endogeneity_lit_review_2026_04_28.md` + `project_session_2026_04_29_h_lewbel_iv_complete.md` — Stock-Yogo framing slightly overstated; v6 prose uses corrected wording
