# PHASE 3 — DURABLE STATE (resume truth for the fork)   2026-06-25

> **Read THIS to resume Phase 3.** Self-contained. Companion: `style_profiles/_PHASE3_KICKOFF.md` (scope + isolation rules).

## Session identity
- This = the **Phase-3 fork**. Worktree `…/F1D-phase3`, branch `phase3/propositions`.
- **Shell cwd = `…/F1D` (the data home).** Data parquets + the installed `f1d` package live ONLY in F1D — any re-run MUST execute from F1D. The fork worktree has no data.
- **Isolation (do NOT break):** edit only the proposition spine (`section*_paragraph_ledger.json`) + `_PHASE3_*` files. Do NOT touch `style_profiles/*`, do NOT run the Phase-2 harness, do NOT edit `_REWRITE_MASTER_LEDGER.md`. Merge `phase3/propositions` → `debug/campello…` when done.

## Phase-3 scope
Collaboratively redesign the proposition spine to address the supervisor's critique. Ratify per section before committing. HIGH blast-radius (drives the Phase-4 rewrite).

## The driver — supervisor critique
**"The cash dimension's motivation is not justified."** The base theory (the disclosure bind: a CEO can't confirm/deny a pending deal → uncertainty language) covers **all** payment types, not only cash.

## ~~THE OPEN FORK~~ — RESOLVED 2026-06-25 → **KEEP cash** (masking framework). Full framework + evidence + tweaks LOCKED in **`_PHASE3_CONCLUSION.md`**.
| | KEEP cash | DOWNGRADE to all-payment-types |
|---|---|---|
| condition | a defensible *why-cash* theory exists | no such theory |
| effect | H1a (cash-concentration) stays a hypothesis | main H1/H1b = any deal; cash-concentration → "additional, unexplained"; **rewire scrutiny §4.1** |

## SETTLED — power/count-artifact verdict (advisor-vetted)
- **Cash significance is REAL, not a low-power artifact** (low power → false *negatives*, not false positives). Cash run-up ≈ 15% of a residual SD.
- **cash ≠ stock is BORDERLINE/fragile.** Stock arm underpowered (n≈123). Wald 0.0983 (p=.039) is large only because β_stock is a **noisy negative** (−0.0524); stock 95% CI ≈ [−0.14, +0.03], cash 0.046 just outside.
- **More statistics won't resolve it** — stays borderline whatever we run. The paper's own "supported but fragile" is already the correct calibration.
- **⇒ The fork is a THEORY call (why-cash), not a data call.** No theory → **downgrade is the honest call, supervisor is right.**
- Optional (only if Sina wants): clustered permutation/bootstrap of the Wald to check whether p=.039 is optimistic at n≈123. NOT auto-run; won't change the verdict.

## DONE — Step 1: new logits → rob_ALL.pdf
Two advisor-locked "Ask 3" logits, **re-run with full thesis controls, ClarityCEO removed (it was a bug), UncResCEO the only CEO-speech regressor**:
- **Logit A** — `1[deal announced next quarter, any payment]` ~ UncResCEO + 7 controls: **LPM 0.0086\*\*\*, Logit 0.3233\*\*\*** (N 40,004; 1,422 firms). Uncertainty predicts *any* deal.
- **Logit B** — `1[cash deal]` (cash=1 vs stock=0) ~ UncResCEO + 7 controls: **LPM 0.0613\*\*, Logit 0.7478\*\*** (N 1,105; 563 firms; cash 982 / stock 123). Predicts cash-vs-stock — but stock underpowered.

Rendered in the thesis convention (mirrors `_cash_scrutiny_channel.tex`): DV in the **column header** ("Deal next quarter" / "Cash deal"), columns `(1) LPM (2) Logit`, UncResCEO + all 7 controls as rows. Two separate tables. Appended to `rob_ALL.pdf` (now **8 pages**, tables on pp. 7–8). Written to **both** `F1D\docs\Thesis\rob_ALL.pdf` (Sina's view) and this fork. Canonical = fork's committed copy.

**Provenance (committed under `tmp/`):** `logit_fullcontrols_rerun.py` (compute — run from F1D), `render_logit_tables.py` (tables), `merge_rob.py` (PDF append), `logit_fullcontrols_results.json` (numbers), `rob_ALL_BEFORE.pdf` (original 6-page backup).

## Context already absorbed (don't re-read)
- **Full spine claim-map** (abstract + §1–§5). Hypotheses: **H1** run-up, **H1a** cash-concentration, **H1b** two-clocks/differential-timing. Designs: MA1 §3.2, MA2 §3.3, MA3 §3.4. Results: C1 (strongest), C2, C4 (scrutiny rule-out), C6 (cash Wald) + §4.2 bid-ask + §4.3/4.4 robustness. Register locks: correlational · no-identification · concentration-not-strict-specificity · mechanism-open.
- **rob_ALL.pdf "thesis vs all-deals" stress test:** the core results (run-up, two-clocks, cash-Wald) all **survive** moving cash→all-payment-types; cash-Wald even slightly stronger stacked (0.1056\*\* vs 0.0983\*\*).

## RESOLVED + NEXT
**Fork closed → KEEP cash.** A defensible *why-cash* framework was found by connecting evidence already in the thesis (no new tests, no new cites): the **masking asymmetry** — stock acquirers manage pre-deal tone up to protect their equity currency (thewissen2024, +15%); cash acquirers don't → cash is the *unmanaged* read where the disclosure-strain surfaces. Honesty floor: our data show **cash rising, stock flat** (no detected stock suppression); masking = motivation, NOT a tested mechanism. Full dossier + the per-section proposition tweaks: **`_PHASE3_CONCLUSION.md`**.

**NEXT:** execute the proposition tweaks (§2.1 P6 · §2.2 H1a · §1 P4b/P6a/P8a · abstract) — Phase-4 rewrite, ratified per section; register locks unchanged. Then merge `phase3/propositions` → `debug/campello-did-supervisor-interrogation`.
