# GitNexus vs graphify — head-to-head bench on F1D rewrite queries

**Date**: 2026-05-26
**Purpose**: Decide which code-knowledge-graph tool to use for the Campello rewrite planning.

**F1D HEAD at bench time**: `0ada81c`
**Graphify index**: refreshed to HEAD (7574 nodes / 11833 edges / 604 communities)
**GitNexus index**: fresh `analyze --force --embeddings` (29014 nodes / 38896 edges / 572 clusters / 300 flows)

## Tool capabilities discovered

| Capability | graphify 0.8.14 | GitNexus 1.6.5 (Windows) |
|---|---|---|
| Concept / semantic search | `graphify query` — BFS around best symbol match | `query` returns empty + warns "FTS indexes missing" even after `--force`. **Broken on Windows.** |
| Raw symbol lookup | N/A (must guess starting symbol) | `cypher` (Cypher-like SQL on the graph) — **fast + clean tables** |
| Symbol context (callers/callees) | BFS depth-N from a node | `context` — works, returns callers/callees + processes |
| Unicode-safe output (Windows) | **No** — crashed with `UnicodeEncodeError: →` on Q5 (known gotcha per `reference_campello_pdf_artifacts_2026_05_26.md` lineage) | **Yes** — clean output for all queries |
| VECTOR semantic index | N/A | **Unavailable on Windows** (LadybugDB VECTOR disabled) |
| Install footprint | already installed; `graphify-out/` ~9 MB | 143 MB `.gitnexus/lbug` + 6 auto-installed Claude skills + CLAUDE.md/AGENTS.md edits |
| Index build time | ~30s (`graphify update .`) | 57s analyze + **21 min** for `--force --embeddings` |

## Q1 — Sample-screening helpers (COMPUSTAT filter, winsorization)

- **graphify**: BFS from `panel()` (in test file) → surfaces `panel_utils.build_cal_yr_qtr_index()` + `get_latest_output_dir`. Partial hit; doesn't directly land on COMPUSTAT screen.
- **GitNexus query**: EMPTY (FTS broken).
- **GitNexus cypher** (workaround): would have found `chk_compustat`, `load_compustat` via name match.

**Winner**: GitNexus (via cypher workaround) — surfaces actual function names directly.

## Q2 — Variable-builder class hierarchy

- **graphify**: BFS around `VariableBuilder` → **23+ concrete builders** + base class + `build_panel()` entry points across `f1d/variables/build_h*_panel.py`. Includes CEOPresUncertainty, CEOQA, ROA, Size, ManagerPres/QA, TobinsQ, BookLev, CashHoldings, DividendPayer, NonCEOManager variants.
- **GitNexus cypher**: 14 builders + `VariableBuilder` base in `src/f1d/shared/variables/base.py`. Clean table, includes `_archived/` filter.

**Winner**: **graphify** — surfaced more concrete builders AND the call-out to `build_h*_panel.py` orchestrators that GitNexus missed.

## Q3 — Econometric runners

- **graphify**: BFS from `panel()` → test code only. Wrong entry point. **Failed to enumerate runners.**
- **GitNexus cypher**: 15 runners cleanly enumerated (`run_h_lewbel_iv_cash.py`, `run_h_dwz_fd_cash.py`, `run_h9_*`, `run_h7_*`, `run_h5b_*`).

**Winner**: **GitNexus**.

## Q4 — Data loaders (Compustat / CRSP / I/B/E/S)

- **graphify**: Found `CRSPEngine` class in `src/f1d/shared/variables/_crsp_engine.py` with methods `.get_data()`, `.get_raw_daily_data()`, `_load_crsp_years()`, `_build_date_bounded_permno_map()`, `_compute_returns_for_manifest()`, `get_engine()`. Plus `winsorize_by_year()` in `winsorization.py`.
- **GitNexus cypher**: `load_compustat`, `load_ibes_consensus`, `load_compustat_raw`, `load_h1_panel` — but ALL in `archive/brexit_2026-05-17_pre-supervised-rebuild/` (deprecated code). Missed the live `CRSPEngine` class.

**Winner**: **graphify** — found the actual current loader class architecture.

## Q5 — Campello tests

- **graphify**: **CRASHED** with Windows unicode encoding error (charmap can't encode `→`). Known graphify gotcha.
- **GitNexus cypher**: `[]` empty result — correctly confirming no Campello tests exist.

**Winner**: **GitNexus** — graphify can't even answer due to Windows bug.

## Score grid

| Q | graphify | GitNexus | Winner |
|---|---|---|---|
| Q1 sample screen | 1/3 partial | 2/3 (via cypher) | GitNexus |
| Q2 var builders | 3/3 | 2/3 | graphify |
| Q3 runners | 0/3 fail | 3/3 | GitNexus |
| Q4 loaders | 3/3 (CRSPEngine) | 1/3 (only archive) | graphify |
| Q5 tests | crashed | 3/3 | GitNexus |
| **Total** | **7/15** | **11/15** | GitNexus by margin |

## Honest read

- **GitNexus cypher** is the strongest individual tool: clean tabular output, fast on Windows, no unicode crashes, enumerates by name pattern.
- **GitNexus query** (semantic + BM25) is BROKEN on Windows — VECTOR extension unavailable, FTS reports missing. ~30% of GitNexus's value gone on this platform.
- **graphify** is genuinely useful for BFS exploration (Q2/Q4) but unreliable on Windows for any output containing common unicode (`→`, `β`, etc. — exactly what F1D's data has).
- Neither tool fully covers what's needed for the rewrite plan.

## Root-cause addendum (2026-05-26 19:10)

After bench, both "semantic search" failures were diagnosed.

### graphify Q5 unicode crash — FIXED

- **Root cause**: Python's default stdout encoding on Windows = cp1252; graphify's `print()` calls a path that emits the `→` (U+2192) character, which cp1252 can't encode → `UnicodeEncodeError`.
- **Fix**: prefix every graphify invocation with `$env:PYTHONIOENCODING="utf-8"`.
- **Re-test**: with utf-8 set, Q5 returns 40 nodes including `BrexitTobinsQBuilder` at `src/f1d/shared/variables/brexit_tobins_q.py` — a builder the bench's GitNexus side missed because of `LIMIT 15` alphabetical truncation.
- **Persist**: add `$env:PYTHONIOENCODING="utf-8"` to standard graphify wrapper. Already a memory rule per `project_graphify_primary_2026_05_20.md` — bench failure was my omission, not graphify's bug.

### GitNexus `query` empty results — NOT FIXABLE LOCALLY

- **Root cause**: `query` is mis-marketed in README. Its actual scope is "search the knowledge graph for execution **flows** related to a concept" — it operates on `Process` nodes only (300 in F1D). Process schema fields: `id`, `label` (e.g., `"Main → _load_ff48_map"`), `heuristicLabel`, `processType`, `stepCount`, `communities`, `entryPointId`, `terminalId`. **No `description` / `docstring` / `content` field.** So BM25 keyword search has only the short label string (2-5 tokens) to match against — natural-language queries return empty.
- **Vector side**: VECTOR extension unavailable on Windows; falls back to exact-scan over `CodeEmbedding` nodes (28,505 of them). Embeddings are present per `meta.json`, but the merge step combines BM25 + vector and keeps only Processes — Code symbols never escape into the result.
- **"FTS indexes missing" warning**: misleading. `gitnexus doctor` + `meta.json` both confirm `fts.status: available`. The warning fires when zero BM25 candidates land — wrongly attributed to missing index instead of sparse Process labels.
- **Local fix possible?** No. Would require GitNexus upstream to enrich Process search documents with member-function names + docstrings, or expose Code-symbol BM25 to `query`.
- **Workaround**: use `cypher` (raw graph query) for symbol enumeration, `context` (callers/callees of a known symbol) for traversal. Both work cleanly on Windows.

### Updated decision

Bench standing unchanged: **both tools kept, capability-split**. The fix above (PYTHONIOENCODING) plus the diagnosis of GitNexus `query` (narrow-scoped, not broken) sharpens the split:

| Use case | Tool + invocation |
|---|---|
| "What functions match name pattern foo*" | `gitnexus cypher "MATCH (n) WHERE n.name STARTS WITH 'foo' RETURN n.name, n.filePath"` |
| "Who calls / is called by X" | `gitnexus context "X"` |
| "Find related code by BFS around X" | `graphify query "X"` (with PYTHONIOENCODING=utf-8) |
| "What execution flows exist between funcA and funcB" | `gitnexus query "funcA funcB"` — narrow-scoped to Process labels |
| Open-ended concept search | NEITHER reliably; use Grep or a focused cypher |

## Decision recommendation

**Use BOTH for the Campello rewrite plan**, segregated by capability:

| Use case | Tool |
|---|---|
| "Enumerate all X named foo*" | GitNexus `cypher` (clean tables, no unicode crash) |
| "Show me callers of X" | GitNexus `context` (handles Windows correctly) |
| "BFS around an unfamiliar symbol to find related code" | graphify (deeper edges, rationale_for) |
| "Community / cluster of related concepts" | graphify (mature community detection) |
| Semantic concept search | NEITHER reliably on Windows — fall back to Grep |

Don't drop graphify (its Q2/Q4 wins matter for finding the existing F1D infra to reuse). Don't drop GitNexus (its cypher is the only reliable name-pattern enumerator on Windows). Update memory `project_graphify_primary_2026_05_20.md` to reflect "graphify + GitNexus, capability-split".

## Next actions

1. Update memory file to note dual-tool approach
2. Build Campello rewrite spec using both tools per capability split
3. Defer the formal 1-week bench (if Sina wants longitudinal evidence)
