# Safety audit — pre-rewrite continue gate

Generated: 2026-05-26 by `tmp/safety_audit_2026_05_26.py`
Git HEAD: `0ada81cb560d` (branch: `master`)

## 1. Locked-truth artifacts (rewrite source of truth)

- `tmp/campello_method_lockin.md` — exists: PASS | size: 34847 bytes | sha256[:16]: `794115b077a1a9f2`
- `tmp/campello_variable_lockin.md` — exists: PASS | size: 93110 bytes | sha256[:16]: `fc3048c1aea2c556`
- `tmp/campello_table1_anchor_2026_05_26.json` — exists: PASS | size: 8768 bytes | sha256[:16]: `b92aedf2a73c7d38`
- `tmp/campello_pdf_extract/full_main_pdfpage21.txt` — exists: PASS | size: 4725 bytes | sha256[:16]: `51d07527d33bea71`

## 2. F1D shared infra files (read-only, must not change)

- `src/f1d/shared/variables/_compustat_engine.py` — exists: PASS | size: 61925 | mtime: 1775796246.586312
- `src/f1d/shared/variables/_crsp_engine.py` — exists: PASS | size: 21374 | mtime: 1775147407.6932254
- `src/f1d/shared/variables/winsorization.py` — exists: PASS | size: 4415 | mtime: 1775098525.470406
- `src/f1d/shared/variables/panel_utils.py` — exists: PASS | size: 17170 | mtime: 1775766504.332572
- `src/f1d/shared/variables/base.py` — exists: PASS | size: 9743 | mtime: 1775098524.2293878
- `src/f1d/shared/path_utils.py` — exists: PASS | size: 13840 | mtime: 1771633338.5285487

## 3. Git uncommitted state

- Modified (10): `.gitignore`, `CLAUDE.md`, `docs/Draft/_campello_rebuild_t8.tex`, `docs/Draft/per_suite/h1_5_disclosure_law_did_table.tex`, `docs/Draft/thesis_tables.pdf`, `docs/Draft/thesis_tables.tex`, `docs/superpowers/specs/2026-05-15-claude-mem-primary-integration-design.md`, `scripts/campello_rebuild/gen_thesis_t8_table.py`, `scripts/campello_rebuild/step7_fullpanel_hypothesis.py`, `tmp/campello_variable_audit_2026_05_17.md`
- Untracked (183): `.graphifyignore`, `1.20`, `2026-04-30-182832-this-session-is-being-continued-from-a-previous-c.txt`, `2026-05-01-042143-local-command-caveatcaveat-the-messages-below.txt`, `AGENTS.md`, `docs/Draft/_campello_summary_stats.tex`, `docs/Draft/_disclosure_law_compact.tex`, `docs/papers/eufm12289-sup-0001-supporting-information.pdf`, `"docs/papers/s11142-024-09843-7 (1).pdf"`, `docs/superpowers/specs/2026-05-26-campello-rewrite-spec.md`, `scripts/campello_rebuild/_build_final_did_statsum_consensus.py`, `scripts/campello_rebuild/_build_textual_did.py`, `scripts/campello_rebuild/_build_textual_did_sec17.py`, `scripts/campello_rebuild/_build_uncres_did_sec17.py`, `scripts/campello_rebuild/_diag_consensus_raw_test.py`, `scripts/campello_rebuild/_diag_consensus_revision.py`, `scripts/campello_rebuild/_diag_consensus_standardized_sweep.py`, `scripts/campello_rebuild/_diag_consensus_statsum.py`, `scripts/campello_rebuild/_diag_consensus_sue_round2.py`, `scripts/campello_rebuild/_diag_random_tercile_placebo.py`, `scripts/campello_rebuild/_diag_step7_consensus_sue_sensitivity.py`, `scripts/campello_rebuild/_diag_summary_stats_full.py`, `scripts/campello_rebuild/_extract_campello_supplementary.py`, `scripts/campello_rebuild/gen_deviation_ledger.py`, `scripts/campello_rebuild/gen_summary_stats_tex.py`
  - … +158 more
- Deleted (0): none

## 4. .gitnexus/ gitignore status (143 MB lbug must NOT enter repo)

- Root `.gitignore` excludes `.gitnexus/`: PASS
- `.gitnexus/.gitignore` (auto-written by gitnexus): exists=True; content: `*`
- Risk: if root `.gitignore` doesn't exclude AND `.gitnexus/.gitignore` doesn't either, the 143 MB binary will be staged on `git add`.

## 5. Rewrite-scope files (must still exist; rewrite deletes them in Phase 9 cutover)

- LIVE `brexit_*.py` builders (6):
  - `src\f1d\shared\variables\brexit_cash_flow.py`
  - `src\f1d\shared\variables\brexit_consensus_eps.py`
  - `src\f1d\shared\variables\brexit_macro_controls.py`
  - `src\f1d\shared\variables\brexit_sales_growth.py`
  - `src\f1d\shared\variables\brexit_stock_return.py`
  - `src\f1d\shared\variables\brexit_tobins_q.py`
- `scripts/campello_rebuild/*.py` files (32):
  - `scripts\campello_rebuild\_build_final_did_statsum_consensus.py`
  - `scripts\campello_rebuild\_build_textual_did.py`
  - `scripts\campello_rebuild\_build_textual_did_sec17.py`
  - `scripts\campello_rebuild\_build_uncres_did_sec17.py`
  - `scripts\campello_rebuild\_diag_consensus_raw_test.py`
  - `scripts\campello_rebuild\_diag_consensus_revision.py`
  - `scripts\campello_rebuild\_diag_consensus_standardized_sweep.py`
  - `scripts\campello_rebuild\_diag_consensus_statsum.py`
  - `scripts\campello_rebuild\_diag_consensus_sue_round2.py`
  - `scripts\campello_rebuild\_diag_moment_fingerprint.py`
  - `scripts\campello_rebuild\_diag_random_tercile_placebo.py`
  - `scripts\campello_rebuild\_diag_s1_fic8.py`
  - `scripts\campello_rebuild\_diag_step6_coef_check.py`
  - `scripts\campello_rebuild\_diag_step7_consensus_sue_sensitivity.py`
  - `scripts\campello_rebuild\_diag_summary_stats_full.py`
  - `scripts\campello_rebuild\_extract_campello_supplementary.py`
  - `scripts\campello_rebuild\_extract_campello_tables.py`
  - `scripts\campello_rebuild\gen_deviation_ledger.py`
  - `scripts\campello_rebuild\gen_summary_stats_tex.py`
  - `scripts\campello_rebuild\gen_thesis_t8_table.py`
  - `scripts\campello_rebuild\step10_cash_t1denom.py`
  - `scripts\campello_rebuild\step1_sample.py`
  - `scripts\campello_rebuild\step2_beta_uk.py`
  - `scripts\campello_rebuild\step3_treatment.py`
  - `scripts\campello_rebuild\step3b3_textual_treatment_sec17.py`
  - `scripts\campello_rebuild\step3b_textual_treatment.py`
  - `scripts\campello_rebuild\step4_timeline.py`
  - `scripts\campello_rebuild\step5_did.py`
  - `scripts\campello_rebuild\step6_controls_did.py`
  - `scripts\campello_rebuild\step7_fullpanel_hypothesis.py`
  - … +2 more

## 6. Campello-session memory files

- `project_campello_systematic_debug_2026_05_26.md` — exists: PASS | size: 4314
- `feedback_nlm_hallucinates_cell_values_2026_05_26.md` — exists: PASS | size: 2220
- `feedback_nlm_off_by_n_paragraphs_2026_05_26.md` — exists: PASS | size: 2064
- `reference_campello_pdf_artifacts_2026_05_26.md` — exists: PASS | size: 3396
- `reference_campello_paper_metadata_2026_05_26.md` — exists: PASS | size: 4984
- `MEMORY.md` — exists: PASS | size: 40284

## 7. New artifacts created this session

- `tmp/campello_method_lockin.md` — exists: PASS | size: 34847
- `tmp/campello_variable_lockin.md` — exists: PASS | size: 93110
- `tmp/campello_table1_anchor_2026_05_26.json` — exists: PASS | size: 8768
- `tmp/campello_claudeweb_88vars_2026_05_26.md` — exists: PASS | size: 94351
- `tmp/campello_var_anchor_REVERIFY_2026_05_26.md` — exists: PASS | size: 16509
- `tmp/campello_var_anchor_FAILS_summary.md` — exists: PASS | size: 12716
- `tmp/gitnexus_vs_graphify_bench_2026_05_26.md` — exists: PASS | size: 8989
- `docs/superpowers/specs/2026-05-26-campello-rewrite-spec.md` — exists: PASS | size: 20730
- `AGENTS.md` — exists: PASS | size: 2579
- `CLAUDE.md` — exists: PASS | size: 2579
- `.gitnexus/` — exists: PASS | size: 4096

## Verdict

- Locked artifacts present: PASS
- F1D infra files present: PASS
- Campello memory present: PASS
- Rewrite spec present: PASS
- .gitnexus/ gitignore: OK (excluded)

**Safe-to-continue checks:**
- All-green for proceeding to Phase 1 (sample + panel scaffolding): **YES**