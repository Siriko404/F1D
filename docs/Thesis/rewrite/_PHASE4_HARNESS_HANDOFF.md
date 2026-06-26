# PHASE 4 HANDOFF — for the harness-design session   (2026-06-26, fork `phase3/propositions`)

> Caveman lite. Exhaustive. New session = design an automated HARNESS for the Phase-4 rewrite (manual per-prop editing too slow). This doc = full context. READ the locked files below FIRST; treat everything here as unverified until checked vs those files.

---

## 0. WHY THIS HANDOFF
Phase 3 = DONE + locked. Phase 4 = redesign the §2 proposition chains for the masking framing. We started doing it by hand (read chain → propose mod → advisor → apply to clone), one subsection at a time. Too slow. STOP. Next session builds a HARNESS (multi-agent workflow) that does it thoroughly + verifiably + fast. This doc tells that session everything done + everything pending.

## 1. READ FIRST (locked files, this order) — the real source of truth
1. `docs/Thesis/rewrite/_PHASE3_CONCLUSION.md` — THE decision + masking framework + cite stack (EVIDENCE DOSSIER §C) + register + ADVISOR ADDENDUM 1–6. Authoritative.
2. `docs/Thesis/rewrite/_PHASE3_STATE.md` — VERIFY-FIRST checklist + resume truth.
3. `docs/Thesis/rewrite/_PHASE4_S2_MODSPEC.md` — the §2 mod-set (change/untouched map). **NOTE: it is v1; the 2 advisor fixes in §5 below OVERRIDE/AUGMENT it.**
4. `tmp/nlm_masking_cites.json` — verified S-V + Louis evidence (verbatim cited_text + page/section + verdicts).
5. `docs/Thesis/rewrite/NLM_QUERY_GUIDE.md` — NLM convention (any new cite goes through this).
6. `docs/Thesis/rewrite/section2_roadmap.md` — §2 design mandates (purpose per subsection 2.1–2.5).

## 2. THE DECISION (Phase 3, locked, ratified by Sina)
KEEP cash. Supervisor critique ("cash motivation not justified") = ANSWERED. Why-cash = **masking asymmetry**:
- Stock pays with **equity** (a currency whose price matters) → incentive to keep valuation high → manages perceptions UP pre-deal.
- Cash pays with **cash** → no currency to protect → no such incentive.
- ⟹ cash = the (relatively) **unmanaged** window where the disclosure-strain surfaces as unscripted Q&A uncertainty → run-up CONCENTRATES in cash.
- This is **MOTIVATION** (ex-ante reason to focus on cash), NOT a tested mechanism.

## 3. HONESTY FLOOR — non-negotiable. Every harness check must enforce.
- Our data: cash run-up **+0.0461\*\*\*** (p=.0074), stock **−0.0429 n.s.** (noisy flat null). Wald cash−stock **0.0983\*\*** (p=.039, two-tailed).
- **NEVER "stock suppressed."** The differential (cash>stock) is motivated as **ATTENUATION** (stock smaller/noisier), NOT stock pushed below baseline. Observed gap = **cash rising**. "We interpret, we do not detect."
- **Cross-channel:** the cites document management in SCRIPTED channels (earnings, press-release tone); our DV = unscripted Q&A residual, **net of the scripted presentation** (§2.3 P2.5). So our measure strips the exact channel the cites are about → frame as a **STRENGTH** (we read the hardest-to-manage channel), not a gap.
- Register locks STAY: correlational · no-identification · concentration-not-strict-specificity · mechanism-open · supportive-not-definitive.
- **C1 (the timing round-trip, strongest result) carries the paper independent of masking.** If a reader rejects the why-cash, the empirical contribution survives.
- Cite discipline: S-V/Louis = **earnings/valuation**, NEVER "tone." thewissen = tone, **preprint**, supplementary one-clause pointer only.

## 4. CITE STACK (locked, NLM-verified — `tmp/nlm_masking_cites.json`)
| Cite | Venue | Leg | Verbatim anchor (page) |
|---|---|---|---|
| **Shleifer-Vishny 2003** | JFE 70:295–311 | MOTIVE (currency) | "incentive to … get their equity overvalued, so that they can make acquisitions with stock" (p.308); overvalued-shares-as-payment (p.300) |
| **Louis 2004** | JFE 74:121–148 | pre-deal BEHAVIOR | "overstate their earnings reports in the quarter preceding a stock swap announcement" (p.121–22); "jump in the abnormal accrual … quarter immediately prior" (p.134) |
| **thewissen 2024** | SSRN **preprint** | TONE (our axis) | "inflating the tone of earnings press releases"; "+15.32%" (already cited) |
- Erickson-Wang 1999 = considered + **DROPPED** (Louis duplicate; anti-over-referencing).
- **+2 `\bibitem` required** in `thesis_draft.tex` (`shleifer_vishny2003`, `louis2004`) — compile/undefined-cite risk if missed.
- NLM: notebook `63e3b970-7976-47bc-8291-37ce7ac9bf74`; ids S-V `f649faef…`, Louis `8ed79bba…`, Erickson-Wang `ddea4f17…`. PDFs also at `F1D\docs\papers\newfinal`. **Auth expires → user runs `notebooklm login`.**

## 5. THE 2 ADVISOR FIXES (override modspec v1; ALREADY in `tmp/apply_s2_1_mods.py`)
1. **ATTENUATION-not-SUPPRESSION (the load-bearing joint).** Masking motivates θ_cash>0 but NOT the differential θ_cash>θ_stock unless stock is **attenuated** (smaller/noisier), not suppressed. P5.4 + §2.2 P3.3 must say: a stock acquirer's optimism disposition partly **offsets** the strain in its unscripted answers → stock run-up smaller/noisier; cash carries only the strain → clean larger run-up. Offset → attenuation, **never** a push below baseline.
2. **CROSS-CHANNEL BRIDGE (closes the genre-jump).** One bridge prop (P5.4): cites = scripted channels; our DV nets out scripted (§2.3 P2.5) → we read the hardest-to-manage channel → STRENGTH. This single prop closes the logic hole AND the earnings→Q&A genre-jump.
3. **ADD to CHANGES (were wrongly UNTOUCHED):** §2.1 **P4** ("the P5 *placebo* isolates the signal" → "the P5 *comparison* motivates the concentration"; guardrail + `_plan.logic_chain_validated.P4_necessity`) and §2.2 **P2.thin_claim** ("stock = placebo handled in P3" → "managed comparison"). "placebo" does **identification work** in P4 → must be swept everywhere it does logic work, not only in prop statements.
- Open-Qs resolved: Harford = keep + demote + **relocate** to the two-clocks node. thewissen split kept (motive on published S-V/Louis) + a one-clause tone pointer in P5. Genre-jump caveat = fix #2 (required).

## 6. THE §2 MOD-SET (exhaustive — from modspec, + fixes above)
**CHANGES:**
- §2.1 **P5** — re-derive why-cash (1 prop → 5): P5.1 Harford DEMOTE+RELOCATE · P5.2 S-V motive · P5.3 Louis behavior + thewissen tone pointer · P5.4 BRIDGE (cross-channel + attenuation) · P5.5 placebo→managed comparison. final_prose → rewrite.
- §2.1 **P4** — "isolates" → "motivates concentration" (guardrail + _plan).
- §2.1 **P6** — LIGHT (thewissen stays nearest-work; gap P6.4 unchanged).
- §2.2 **P2** — LIGHT (callback broadened; thin_claim placebo→comparison; H1 statement P2.1 UNCHANGED).
- §2.2 **P3** — re-derive H1a rationale (mirror of §2.1 P5): P3.2 → masking callback (placebo→managed comparison); P3.3 + attenuation-not-suppression clause; H1a statement P3.1 UNCHANGED.
- §2.4 **P2.3** — `placebo` → `comparison` (1 word). MA3 Wald (P3) UNCHANGED (mechanism-agnostic linear restriction).
- bib: +2 `\bibitem`. register: +lock (motivation-not-mechanism; no-suppression; attenuation).

**UNTOUCHED (exhaustive):** §2.1 P1·P2·P3·P7 · §2.2 P1·P2.1·P4·P5 · **§2.3 ALL** · §2.4 ALL but P2.3 (incl. MA3 Wald) · **§2.5 ALL**. (Optional, NOT proposed: §2.3 P2.5 dovetail — left clean.)

## 7. WHAT'S DONE THIS SESSION
- Cite hunt → web-verify → NLM-verify (identity + verbatim) → LOCK (3 cites). Dossier §C + addendum-5 resolved (commit `ea54c5ac`).
- §2 ALL 5 subsections READ at the chain-design level (roadmap mandates + verbatim proposition dump).
- `_PHASE4_S2_MODSPEC.md` written + advisor-vetted (2 fixes above).
- §2.1 masking mods APPLIED to a clone → advisor-checked → **clone DELETED** (this handoff). The §2.1 design (with BOTH advisor fixes) is preserved as the prop text in `tmp/apply_s2_1_mods.py` — it is a **REFERENCE, not runnable as-is**: its `CLONE` path points to the deleted clone, so re-clone + repoint before running.
- Tooling persisted in `tmp/`: `extract_spine.py` (strip the NLM evidence noise → compact chain skeleton), `dump_props.py` (verbatim proposition dump, all §2), `apply_s2_1_mods.py` (the §2.1 reference application — encodes both advisor fixes).

## 8. WHAT'S PENDING (Phase-4 work the harness must do)
- Apply masking mods to clones for §2.1 (re-run script) + §2.2 + §2.4. Ratify each.
- Then DOWNSTREAM (do NOT skip): §1 intro, abstract, §3.1–3.4, §5. **§3 is NOT a mechanical mirror** — ~60 `placebo` hits in §3.2/3.3/3.4 results-interpretation prose; that is exactly where "stock suppressed" can sneak in. Sweep + guard.
- Retire originals only when 100% safe (Sina's rule). Edit CLONES only.
- Rewrite each changed paragraph's `final_prose` (blocked until chain ratified).

## 9. THE HARNESS TO DESIGN (next session's actual job)
Automate the manual loop. Per subsection:
```
1. EXTRACT chain   (extract_spine.py method — strip NLM evidence noise)
2. PROPOSE mods    (constrained by §3 honesty floor + §6 mod-set)
3. VERIFY (adversarial panel): no-suppression · attenuation-correct · cite-discipline (earnings≠tone) ·
                    register-locks intact · logic end-to-end · exhaustiveness (no missed placebo/why-cash site)
4. APPLY to clone  (apply_s2_1_mods.py pattern: programmatic JSON edit, preserve verification, block final_prose)
5. LOGIC-CHECK     (chain holds start→finish; no contradiction P5-manages vs P1-symmetric vs data-stock-flat)
```
- Build with the **Workflow** tool (multi-agent: propose → adversarial-verify panel → synthesize → apply). NLM CLI for any NEW-cite verification (guide §1–§17).
- Make every honesty-floor item (§3) an explicit harness gate.

## 10. ISOLATION / RULES (do not break)
- Fork = `…/F1D-phase3`, branch `phase3/propositions`. **Shell cwd / data = `…/F1D`** (data parquets + `f1d` pkg live ONLY there; any re-run executes from F1D).
- Do NOT touch `style_profiles/*` or `rewrite/_rewrite_working/` (Phase-2's domain). Do NOT run the Phase-2 harness. Do NOT edit `_REWRITE_MASTER_LEDGER.md`.
- Originals PRISTINE; edit CLONES only; retire when safe.
- NLM = SOLE paper authority (never read a PDF for content). Read `.tex` tables, NOT summary JSONs (context contamination).
- NO memory-sourced cites/theories; verbatim-verify everything vs primary source.
- Sina prefs: ULTRA-terse replies (≤6 lines; "too long"/"what?" = failure); short sentences; ratify per subsection before commit; no overclaim.

## 11. GIT
HEAD after this handoff = latest commit on `phase3/propositions`. Clone removed. Locked files committed: `_PHASE3_CONCLUSION.md`, `_PHASE3_STATE.md`, `_PHASE4_S2_MODSPEC.md`, `_PHASE4_HARNESS_HANDOFF.md` (this), `tmp/nlm_masking_cites.{py,json}`, `tmp/{extract_spine,dump_props,apply_s2_1_mods}.py`. Merge `phase3/propositions` → `debug/campello-did-supervisor-interrogation` only when Phase 4 fully done.
