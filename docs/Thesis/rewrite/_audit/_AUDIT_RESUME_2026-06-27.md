# ⚠️ NEXT-SESSION REVIEW REQUIRED — Proposition-chain referee AUDIT (2026-06-27)

> **THE current entry point for the audit layer.** Supersedes nothing in `_PHASE3_RESUME_2026-06-26.md`
> (that doc = the masking PROPOSED-FIXES; this doc = the AUDIT of those fixes + 2 new data-level catches).
> **Nothing is applied.** Originals pristine. Treat memory as unverified; the files + `audit.json` are truth.

## ONE LINE
We referee-audited the Phase-3 masking proposed-fix proposition chain. **17 findings, each verbatim-verified
+ blast-radius mapped + investigated fix + fix-safety checked.** Deliverable = `audit.json`. NOTHING applied.

## THE DELIVERABLE — read this first
`F1D-phase3/docs/Thesis/rewrite/_audit/audit.json`
- `problems[]` (17): each has `locus`, `severity`, verbatim `issue`, `evidence`, `proposed_fix{action,from,to,why,honesty_floor,evidence_ok}`, and `deep_analysis{verified, blast_radius, agents_missed, fix_safe, status, ...}`.
- `meta.signoff` = the calibrated advisor sign-off (below). `meta.conclusion`, `meta.lesson_internalized`.

## ⚠️ DECISIONS PENDING (this is the review flag)
1. **P3.4 → SINA MUST RATIFY.** It's THE prop answering the supervisor's "cash motivation not justified."
   Reformulated 4× (v1 dampens→suppression ✗ · v2 hidden comparative ✗ · v3 Q&A-cleaner ✗ ·
   **v4 SETTING-level: cash setting is management-free → run-up there is clean; NO Q&A comparative; gap is
   empirical C6**). v4 is in `audit.json` (locus `2.2|P3.4`). Judgment call — ratify or adjust the framing.
2. **Spine-vs-DATA sweep — DO or DEFER?** 15 of 17 findings are spine-INTERNAL (claims vs each other).
   Only 2 are spine-vs-DATA (claims vs code/tables) — and BOTH came from Sina, not the panel. The ONE data
   area sampled (SDC filters) hit **~100%**: 1 major + 4 `Filters.txt` discrepancies. So the data dimension
   is barely explored and high-yield. **Decide: bounded data sweep first, or apply now + sweep later.**
3. **Then:** apply ratified fixes → regenerate `final_prose` → +2 `\bibitem` (shleifer_vishny2003, louis2004)
   → compile.

## THE 17 AT A GLANCE — 0 critical · 5 major · 12 minor
**Majors:**
- `2.2|P3.4` masking motivation (v4 → ratify) — was the only "critical-contested"
- `1|1-P7-a` "three contributions" but four enumerated → "four"
- `1|1-P9-a` roadmap omits delivered §4.2/4.3/4.4
- `4.2|4.2-PARA4-a` null→"cannot be artifact/identification" OVERCLAIM — **8 sites** (L4,5,6,219,220,229,232,244), not 1
- `3.1|sample-selection` **(NEW, user-flagged)** SDC sample filters undisclosed; `Filters.txt` inaccurate (below)

**Minors (12):** §2.1 P5.5 "sits lower", §2.1 P6.1 thewissen dup, §1 1-P7-b provenance mislabel (5 drift props
tagged ORIGINAL-locked), §3.1 source-count (=FIVE), §4.2 PARA2 number, §4.2 PARA1 dangling depends_on,
§5 5-P5-a "so" couples 2 open whys, §5 5-P3-c "holds" overstates 4.3, §2.2 P5.2 "rejected"→4.1 register,
§2.1 P4.2 DWZ-decomposition thin span (NO ACTION; watch if referee probes the measure),
`2.4|DiD-label` **(NEW, user-flagged)** guard.

## VERIFIED GROUND-TRUTH (do NOT re-derive — confirmed this session)
- **Honesty-floor numbers — MATCH the tables:** cash **+0.0461\*\*\*** & stock **−0.0429** (`docs/Draft/_empire_building_did.tex:13`);
  C6 Wald **0.0983\*\*** & cause **0.0064** (`docs/Draft/_empire_cashspec.tex:18`). [F1D tree]
- **NO DiD in the thesis (Sina was right).** `thesis_draft.tex:94` = "within-firm, two-way fixed-effects regression."
  "DiD" lives only in §2.4 planning notes + code/table names + the disclaimer. Guard added so prose-regen can't introduce it.
- **SDC actual applied filters (code-verified, `scripts/gen_empire_did_table.py:97-128`):** 2002–2018 · US **ACQUIRERS**
  (not targets) · public acquirers · deal-status {Completed,Pending,Withdrawn} · payment-known · ≥50% cash/stock arm ·
  **$1M minimum** (parquet) · ≥1 transcript · first deal per firm · fin/util excluded via the main firm-sample match.
- **`Filters.txt` is INACCURATE — do NOT disclose from it:** #9 says "US targets" but code filters US acquirers;
  #2/#3 (control thresholds) NOT applied (no SDC field); #4/#5 (asset/self-tender) NOT applied; #6 reinterpreted.
- **§3.1 source count = FIVE** (Execucomp is a real primary source: `comp_execucomp.parquet` → CEO FE via `build_tenure_map.py`).

## CALIBRATED SIGN-OFF (advisor, NOT blanket-100%)
SIGNED: the spine-INTERNAL audit is complete + sound (17 verified, spine holds, no finding broken, no data touched,
honesty-floor + US-targets checks passed). NOT signed: (1) P3.4 → Sina ratify; (2) spine-vs-data barely sampled
(high-yield) → a bounded next pass is warranted. Claiming "100% on everything" would be the verified≠asserted reflex again.

## LESSON (recurred ~4× this session — internalize)
Every verdict needs BOTH "did I remove the error?" AND "is the replacement correct/complete/canonical/**applied**?"
**Absence-of-error ≠ presence-of-correctness.** And: the referee panel is BLIND to spine-vs-data (it had only the
proposition spine, not the code/tables/parquets) — that whole dimension needs code/data access.

## HOW WE GOT HERE (brief)
STEP-0 corpus (`build_corpus.py` → `corpus.json`, GATE-0 PASS, fixes applied to a throwaway copy) → smoke (1 overclaim
auditor, caught P3.4) → 2 referee panels (6 dimension auditors + 2 redteams each; EACH panel lost ONE redteam to API
"stalled mid-stream" — output-size, not concurrency) → union both + smoke (`audit_union.json`, 15 loci) → per-locus
adjudication was attempted (15 agents, killed as token-wasteful — verdicts were already on disk) → **deterministic
Python merge → `audit.json`** → manual per-finding deep-dive (read verbatim · verify exists · blast-radius grep ·
advisor on fix-safety) → 2 NEW user-flagged data catches (SDC $1M; DiD label).

## DURABLE FILES (all under `F1D-phase3/docs/Thesis/rewrite/_audit/`)
- `audit.json` — THE deliverable (17 findings + fixes + deep_analysis + sign-off)
- `AUDIT_SPEC.md` — the audit design
- `corpus.json` + `build_corpus.py` — the fixes-applied corpus + GATE-0 (rebuildable)
- `audit_run1.json`, `audit_run2.json`, `smoke_overclaim.json`, `audit_union.json` — raw audit data
- (workflow scripts live in the session dir `.claude/.../workflows/scripts/` — NOT cross-session durable, but reproducible)

## HARD RULES
- NOTHING applied. Clones + originals pristine. P3.4 needs Sina's ratify before apply.
- Disclose only CODE-VERIFIED sample filters, NEVER `Filters.txt` (it overstates).
- Honesty floor intact: motivation-not-mechanism · no stock-suppressed · S-V/Louis = earnings not tone · two whys stay open.
