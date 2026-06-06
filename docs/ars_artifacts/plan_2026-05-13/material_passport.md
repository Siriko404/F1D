> ⛔ **SUPERSEDED — DELETED VERSION. Do NOT treat as canonical or live.**
> This 2026-05-13 `plan_thesis_v1` (UncResCEO → precautionary cash) belongs to a thesis draft version Sina discarded. Plan mode was **restarted fresh on 2026-06-06** per Sina. Retained for history only; nothing here is load-bearing for the current paper.

# Material Passport — F1D Thesis Plan-Mode Run

(Schema 9, ARS v3.7.0)

## Required fields

- **Origin Skill:** academic-paper
- **Origin Mode:** plan
- **Origin Date:** 2026-05-13T19:00:00Z
- **Verification Status:** UNVERIFIED (in-progress; promotes to VERIFIED at Step 3 close)
- **Version Label:** plan_thesis_v1

## Optional fields

- **Upstream Dependencies:**
  - F1D NotebookLM verbatim verification 2026-05-13 (Opler 1999, Bates 2009, ACW04, FW06, HQ07, DWZ 2021, Campello 2022, Boasiako 2020)
  - 8 anchor sources confirmed in F1D notebook id `63e3b970-7976-47bc-8291-37ce7ac9bf74`
  - Locked scope: Brexit + Boasiako DiDs only (`feedback_endo_defense_final_hierarchy.md` superseded by [[project_ars_plugin_thesis_rewrite_path_2026_05_13]])
  - Existing implementation: 80+ runners under `src/f1d/econometric/`, suite_spec JSONs at `outputs/econometric/*/2026-*/suite_spec_*.json`
- **repro_lock:** null (LLM outputs not byte-reproducible per ARS standard)

## Stage / Step tracking

| Stage / Step | Status | Date | Verification |
|--------------|--------|------|--------------|
| Pipeline Stage 2 (WRITE) | in-progress | 2026-05-13 | UNVERIFIED |
| Plan Step 0 — Research Readiness Check | DONE | 2026-05-13 | VERIFIED (materials inventory confirmed) |
| Plan Step 1 — Thesis Crystallization | in-progress | 2026-05-13 | Q1a ratified; Q1b/Q1c pending |
| Plan Step 2 — Chapter-by-Chapter | pending | — | — |
| Plan Step 3 — Argument Stress Test | pending | — | — |

## INSIGHTs (per plan_mode_protocol Step 1 — emitted at Step 1 close, after Q1a+Q1b+Q1c)

| Tag | Status | Content | Date |
|-----|--------|---------|------|
| `[INSIGHT: thesis_statement]` | **DRAFT (Q1a only)** | Within-CEO quarterly deviations in earnings-call answer uncertainty (UncResCEO) signal precautionary cash-buffer demand and predict contemporaneous + one-quarter-ahead firm cash holdings. **Promotes to RATIFIED only after Q1b adversary response and Q1c reader-takeaway both ratified.** | 2026-05-13 |

## Working notes (pre-requisites for thesis crystallization — NOT protocol INSIGHTs)

| Note | Content | Verified |
|------|---------|----------|
| Variable definitions | DWZ Eq 4 decomposition verified verbatim 2026-05-13 via notebooklm.exe F1D notebook: ClarityCEO_i = −γ_i (CEO fixed effect); UncResCEO = ε_{i,t} (residual, strategic component); UncPreCEO = scripted presentation %. | 2026-05-13 |
| Primary IV rationale | UncResCEO is primary IV because (a) only within-CEO time-varying signal, (b) not absorbed by firm FE, (c) DWZ explicitly calls it "potentially strategic component". | 2026-05-13 |

## Open mitigation flags

| Flag | Issue | Resolution path |
|------|-------|-----------------|
| within-CEO claim | CEO turnover within firms across 2002–2018 window may contaminate within-firm-FE identification of UncResCEO effect | Investigate `src/f1d/econometric/run_h1_cash_holdings_ceo2iv_decomp.py` for CEO-spell handling; consider single-CEO-spell robustness or add CEO FE alongside firm FE. Triggered when chapter-level walkthrough reaches identification chapter. |

## Append-only audit trail

- 2026-05-13T18:30Z — Passport created at Plan Step 1 entry
- 2026-05-13T18:45Z — Working note ratified: variable definitions (DWZ Eq 4 verbatim via notebooklm.exe)
- 2026-05-13T18:55Z — Working note ratified: primary IV choice = UncResCEO (within-CEO time variation argument)
- 2026-05-13T19:00Z — Q1a draft `[INSIGHT: thesis_statement]_DRAFT_v1` ratified (within-CEO mitigation flag attached)
- 2026-05-13T19:10Z — Advisor compliance audit: flagged premature INSIGHT lock + non-protocol INSIGHT names; corrections applied
- 2026-05-13T19:15Z — Q1b adversary class CORRECTED twice: (a) "speech→cash causal" → REJECTED by Sina (not what thesis claims); (b) proxy-attack-classes A/B/C/D → REJECTED by Sina (peripheral); FINAL: reverse-causality (cash → speech) named as primary attack class
- 2026-05-13T19:20Z — Q1b TIER 1 rebuttal RATIFIED: Cash_{t+1} temporal asymmetry — UncResCEO_t predicts Cash_{t+1} 6/6 forward-horizon cells sig p_one<0.10 (β=+0.0019 to +0.0028, H1 main cols 7-12). Time runs forward → reverse arrow ruled out.
- 2026-05-13T19:25Z — Q1b TIER 2 advisor flagged: Brexit + Boasiako affect cash directly (FX exposure / legal liability) → DiDs provide mechanism-existence not arrow-direction. Reframed as "consistent with precautionary, not unique to it."
- 2026-05-13T20:15Z — **Lagged_DV bug discovered + fixed (commit c6686fb).** Original code line 336-340 produced Lagged_DV = Cash_{t-1} for both Cash_t and Cash_{t+1} regressions. Locked memory `feedback_endo_defense_focused_on_cash_t.md:20` documented Lagged_DV in lead-spec as Cash_t. Code-vs-documented-intent mismatch confirmed. Fix: DV-conditional branch.
- 2026-05-13T20:30Z — **TIER 1 RC defense COLLAPSED empirically.** H1 main re-run 2026-05-13_202817. Cash_{t+1} cols 7-12 UncResCEO p_one moved [0.022, 0.068] → [0.114, 0.280]. **6/6 sig → 0/6 sig.** Forward-prediction effect was Cash_t persistence leaking through. TIER 1 ironclad-RC-defense claim retracted.
- 2026-05-13T20:35Z — Q1b rebuttal RE-RATIFIED with honest state: TIER 1 dead; TIER 2 mechanism-existence only; thesis cannot claim arrow-direction identification. RC defense conceded as open limitation in §V.
- 2026-05-13T20:35Z — What survives the bug fix: 6/6 contemporaneous Cash_t sig (cols 1-6, unchanged); Brexit + Boasiako cash DiDs (4/4 + 3/4 sig POS, mechanism existence); §IV.A bid-ask + §IV.B CCCL outsider channels; DWZ method extension; §II.5 construct validity.
