> ⛔ **SUPERSEDED — DELETED VERSION (plan restarted 2026-06-06 per Sina).** These v2 cards belong to the discarded UncResCEO→cash draft. Not load-bearing. History only.

# Thesis Claim Cards — Sequential Defense

**Date started:** 2026-05-13
**Restarted 2026-05-13 evening:** v2 via ARS plugin /ars-plan after scope cut to 2 DiDs (Brexit + Boasiako) and full draft discard. v2 cards below; v1 cards (precautionary motive C1-C10) retained for reference but not load-bearing.
**Format:** PhD-jury defense walkthrough. One atomic claim per card. Each card carries lit anchor with verbatim verification status.
**Purpose:** Lock the logical spine of the thesis. Each card later expands into thesis-body prose. Spine ensures coherence across §I–§V.
**Verification standard:** Lit anchors must be verbatim-verified against source PDFs in F1D NotebookLM. No paraphrase claims pass.

---

## v2 — ARS /ars-plan Step 1 Thesis Crystallization

> **CANONICAL RECORD MOVED:** Per ARS plugin Schema 9 protocol, the Material Passport at `docs/ars_artifacts/plan_2026-05-13/material_passport.md` is the authoritative record. The v2 section below is a duplicate working copy kept for human readability; resolve conflicts in favor of the Material Passport.

### Thesis Claim (v2) — RATIFIED 2026-05-13 🟢

> Within-CEO quarterly deviations in earnings-call answer uncertainty (UncResCEO) signal precautionary cash-buffer demand and predict contemporaneous + one-quarter-ahead firm cash holdings.

**Primary IV:** UncResCEO (DWZ Eq 4 residual ε_{i,t})
**DV:** CashRatio + CashRatio_lead
**Evidence (h1_cash_holdings_ceo2iv_decomp 2026-04-29):** UncResCEO 12/12 sig p_one<0.10, β ∈ [+0.0016, +0.0028], n=41,108–43,333, n_firms=1376

**Variable definitions verbatim from DWZ 2021 via notebooklm.exe F1D notebook 2026-05-13:**
- ClarityCEO_i = −γ_i (CEO fixed effect, time-invariant, "stable style component not motivated by business uncertainty")
- UncResCEO_{i,t} = ε_{i,t} (residual, "potentially strategic component... deviations from Clarity")
- UncPreCEO = raw scripted-presentation %, IR-vetted

### OPEN MITIGATION FLAG — "within-CEO" claim ⚠️

Sina flagged 2026-05-13: prepare to mitigate the "within-CEO" identification claim as plan-mode walkthrough proceeds. Investigate later if needed.

**Suspected concerns to investigate when raised:**
- CEO turnover within firm: cash regressions use FIRM FE, not CEO FE. With multiple CEOs per firm across 2002-2018 window, firm-FE may not absorb CEO-specific γ_i variation cleanly. UncResCEO is constructed at CEO-time level (DWZ Eq 4 uses CEO indicator), but firm-FE specs mix across CEO transitions.
- ClarityCEO discontinuity at CEO turnover events contaminates within-firm time-series variation.
- Need to check: does H1 spec use firm-FE only, or firm-FE + CEO-spell controls? (h1_cash_holdings_ceo2iv_decomp uses fe_entity=firm OR industry; CEO turnover handling not visible in suite_spec.)

**Resolution path when triggered:** check src/f1d/econometric/run_h1_cash_holdings_ceo2iv_decomp.py for CEO-turnover handling. If absent, run robustness restricted to single-CEO-spell firms or add CEO FE alongside firm FE.

---

## Status legend

- 🟢 LOCKED — Sina ratified after verbatim verification
- 🟡 PENDING — drafted, awaiting ratification
- 🔴 RETRACTED — drafted then killed

---

## Storyline structure (planned)

```
Lit-review chain (anchor: established literature)
  C1  Precautionary motive exists
  C2  Riskier cash flows → more cash
  C3  Poor external-capital access → more cash
  C4  ACW04 amplification: constrained firms save more out of CF
  C5  HQ07 amplification: CFvol amplifies cash for constrained firms
  C6  DWZ 2021 measure: CEO speech uncertainty decomposable
  C7  DWZ 2021 scope gap: financing-policy untested

Hypothesis development (anchor: lit-review claims combined)
  C8  H1 — speech uncertainty predicts cash
  C9  H1a — financing-friction amplification
  C10 H1b — cash-flow-volatility amplification

[methodology, results, endogeneity, additional channels, conclusion — to be added]
```

---

## Cards

(filled in sequentially as Sina ratifies each)

---

### Claim 1 — Precautionary motive grounded in uncertainty  🟢 LOCKED 2026-05-13

**Claim:** Firms face uncertainty about two future dimensions:
- (A) future internal cash flow generation, and
- (B) future external-capital access cost.

Precautionary theory predicts firms hold a cash buffer to insure against funding shortfalls that occur when these uncertainties realize adversely. **Greater uncertainty → larger buffer.**

**Lit anchors (verbatim):**
- Opler 1999 §2.2: *"We call this motivation to hold liquid assets the precautionary motive for holding cash."* (Cites Keynes 1934/1936 — precautionary demand is demand under uncertainty about future needs.)
- Bates 2009 §2: *"Firms hold cash to better cope with adverse shocks when access to capital markets is costly."* (Adverse shocks = uncertain realizations.)

**Why uncertainty is constitutive, not bolted-on:** without future-state uncertainty (deterministic future CF + deterministic external capital costs), no precautionary buffer is optimal. Uncertainty creates the motive — it is not a downstream signal of it.

**Role in storyline:** foundation. Every downstream card becomes either a *dimension* or *signal* of underlying uncertainty A/B.

**Downstream prose flag (do later, not now):** §II.1:12 thesis prose needs a one-line addition grounding "shortfalls are a concern because future cash flow + capital access are uncertain." Editing deferred.

---

### Claim 2 — Riskier cash flows → MORE cash buffer  🟢 LOCKED 2026-05-13

**Claim:** Firms with higher cash-flow risk (the empirical realization of *dimension A* from Card 1) hold larger cash buffers cross-sectionally.

**Lit anchors (verbatim):**
- Opler 1999 abstract: *"firms with strong growth opportunities and **riskier cash flows** hold relatively high ratios of cash to total non-cash assets."*
- Bates 2009 abstract: *"Cash ratios increase because firms' cash flows become **riskier**."*

**Empirical proxy:** cross-sectional cash-flow volatility (σ over rolling window) is positively associated with cash/assets.

**Why this matters:** makes Card 1 falsifiable on dimension A. Two top-tier publications across three decades + US sample = CF-risk → cash robust.

**Role in storyline:** dimension A empirical evidence. Pairs with Card 3 on dimension B.



