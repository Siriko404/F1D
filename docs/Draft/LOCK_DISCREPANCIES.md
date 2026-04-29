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

## Phase 4 user-caught drift (2026-04-29 LATE×7) — stale appendix content

User: *"we DONT include belowIG. we dropped it a long time ago."*

§2.4 + §3.5 v6 draft included "three-way IG/BelowIG/Unrated split" framing imported from `appendix_c_robustness.tex` line 9 subsection "Three-Tier Constraint Moderator: BelowIG Handling". Empirical verification against `per_suite/h1_2_ceo2_decomp_table.tex` and CANONICAL_FACT_SHEET.md H1.2 IV list confirms suite is BINARY (Unrated indicator only; no BelowIG row anywhere). The appendix is v5.1-era stale content describing a design extension never implemented.

Fix shipped commit `9b340cd`:
- §2.4: "three-way IG/BelowIG/Unrated split in robustness" → "binary rated-versus-unrated scheme directly...rated reference category pools investment-grade and below-investment-grade firms"
- §3.5: BelowIG paragraph dropped entirely; robustness section reports 2 disclosures instead of 3

Phase 10 cleanup required for `appendix_c_robustness.tex`:
- §"Three-Tier Constraint Moderator" subsection (lines 9-12) — DELETE or replace with binary disclosure
- Lines 19+24: "UncAnsCEO" v5.1 IV name → v6 decomp variants
- Line 12: `\ref{tab:h1_2_ceo2}` → `\ref{tab:h1_2_ceo2_decomp}`

Pattern: appendix files NOT refreshed for v6 are unreliable sources for body prose. Per_suite table files (programmatically generated from current suite_specs) are authoritative for methodological description. Recorded as additional rule in `feedback_primary_source_verify_always.md`.

## Phase 3 NLM paranoia audit (2026-04-29 LATE×6) — verbatim drift findings

User directive verbatim: *"you must double check with nlm mcp again! this is a sensitive phase. be paranoid! do not trust."*

NotebookLM F1D session `76ff5038` re-verified all primary-source verbatim quotes used in `docs/Draft/sections/section_2_framework.tex` (Phase 3 commit `617832f`). Four verbatim drift errors caught and patched (commit `782b8f5`).

**Drift attribution analysis (verified):**

| # | Paper | Drift item | Drift origin | Lock state |
|---|---|---|---|---|
| 1 | DWZ 2021 Table 3 Notes | Omitted "in communication" from "uncertainty resulting from persistent firm characteristics" | **AUTHOR-INTRODUCED** in §2 draft | `feedback_dwz_persistent_style.md` UncPre row had it CORRECT |
| 2 | ACW 2004 §II.D citation | Attributed §III p.1802 wording to §II.D p.1799 | **LOCK-PROPAGATED** (`reference_almeida_campello_weisbach_2004_verbatim.md` Q3 + `project_h1_h2_theoretical_framing_locked_2026_04_28.md` Step 2) | BOTH locks had wrong section attribution |
| 3 | OPSW 1999 Section 2.2 p.9 | "financing profitable projects" instead of "investing in profitable projects" | **AUTHOR-INTRODUCED** in §2 draft | `reference_opsw_1999_verbatim.md` Q3 had it CORRECT ("investing") |
| 4 | BKS 2009 Intro p.1987 | "post-2000 secular increase" mis-dated trend | **AUTHOR-INTRODUCED** in §2 draft | `reference_bks_2009_verbatim.md` Q6 had period CORRECT (1980-2006) |

**Lesson learned (durable rule):** 3 of 4 drifts were author-introduced into the draft when paraphrasing from memory, NOT lock-propagated. Reading-the-lock-and-typing is itself a transcription failure mode (similar to `feedback_no_llm_cell_transcription` for numbers, but for verbatim quotes). Phase 3 verification required the SECOND PASS via NLM despite locks reading correctly. Recorded as `feedback_primary_source_verify_always.md`.

**Files corrected post-Phase-3 audit:**
- `docs/Draft/sections/section_2_framework.tex` (4 fixes, commit 782b8f5)
- `reference_almeida_campello_weisbach_2004_verbatim.md` (Q3 location corrected)
- `project_h1_h2_theoretical_framing_locked_2026_04_28.md` (ACW Step 2 location corrected)

**Verifications PASSED in Phase 3 audit (no fix needed):**
- BS 2003 R² 77→80%, F p≤.0001, heterogeneity quote
- DWZ Pres-vs-QA "scripted/improvised" framing (§4.3 p.15)
- DWZ ClarityCEO "not motivated by business uncertainty" (§1 p.2)
- DWZ UncRes "explains little of the market reaction" (§1 p.3-4)
- DWZ UncRes "residual uncertainty…not explained…" (§4.4 p.17)
- DWZ headline "primarily a function of ClarityCEO" (§5.3 p.29)
- FP 2006 "credit constrained" vs "capital constrained" (§2.2 p.63)
- FP 2006 "less debt and slightly more equity" (§2.2 p.63)
- FP 2006 binary rated-vs-unrated + sample 1986-2000
- MW 2001 cluster pattern (21% cash, 17.5% median, ~3× control)
- MW 2001 working paper status, July 9, 2001 draft
- MW 2001 pecking-order interpretation (NOT precautionary; cluster shared with OPSW)
- ACW 2004 baseline hypothesis (Abstract p.1777)
- ACW 2004 §II.D macro-shock evidence (GDP-response coefficients p.1800)
- OPSW Q3 verbatim re-confirmed ("investing in profitable projects")
- OPSW Q4 directional prediction ("Uncertainty leads to situations…")
- BKS Q4 precautionary motive verbatim ("Firms hold cash to better cope with adverse shocks…")
- BKS Q6 secular trend ("more than doubles…from 10.5% in 1980 to 23.2% in 2006")
- BKS Q6 two-way clustering (firm + year, Cameron-Gelbach-Miller 2006)
