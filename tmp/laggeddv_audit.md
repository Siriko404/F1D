# Lagged_DV footgun audit (live-grep only; GitNexus broken+stale, provenance docs deleted)

## The footgun
Generic label `Lagged_DV` is set per-runner to the lag of **whatever the DV is**:
`df["Lagged_DV"] = df[f"{dv_var}_lag"]` (or `_lag_column_for_dv(dv)`). So a residual
DV silently gets an AR(1) control it must not have.

## BUG — UncResCEO (residual) given a lagged-DV control

> **DEFERRED per Sina (2026-06-08):** these 4 suites are non-urgent — leave for now, fix
> later. (Residual lag coef ≈0.02, so the EPU betas barely move.) The thesis cash-specificity
> table got its *legit* CashRatio partial-adjustment lag separately, done 2026-06-08; THESE
> residual-lag removals are queued, NOT done.

Directive: the residual UncResCEO must NOT have a lagged-DV control. The residual ships
in TWO column-name variants — `UncResCEO` and `UncResCEO_c` (centered) — so the literal
grep had to cover both (advisor caught the `_c` blind spot).

**Code sites (definitive: every runner that maps a Lagged_DV to a residual lag):**

| Runner | Evidence | DV | Status |
|---|---|---|---|
| `run_h24_us_epu.py:700,253` | `UncResCEO_lag = groupby[UncResCEO].shift(1)` → `Lagged_DV` | UncResCEO | **BUG** |
| `run_h24b_global_epu.py:691` | same | UncResCEO | **BUG** |
| `run_h1_5_trump_did.py:338,409` | `UncResCEO_c_lag` → `lag_col` for the speech spec | UncResCEO_c | **BUG** |
| `run_h1_6_redistricting_did.py:342,452` | same | UncResCEO_c | **BUG** |

**Thesis-file (`thesis_tables.tex`) rendered manifestation — flag for the PDF:**
- **T7 US EPU (h24), line 413** — UncResCEO col shows `Lagged_DV 0.0202***`  ❌
- **T8 Global EPU (h24b), line 470** — same  ❌
- (trump/redistricting are NOT in `thesis_tables.tex`.)

**Legit Lagged_DV in the thesis file (sticky DV → keep):** L43/121/190 cash (h1/h1_2/h1_3),
L524 spread (h14c), L591 CCCL (h18).

**UncPreCEO = RAW LEVEL (user-confirmed; CEOPresUncertaintyBuilder, a word-ratio measure,
lag≈0.52).** NOT a residual → its lag is defensible, NOT a bug. Directive does not extend.

## NOT bugs (verified live)
- `run_h23_competition_uncertainty.py:227`, `run_h1_5_brexit_did_uncres.py:119` — the
  UncResCEO groupby is an **aggregation (.mean/collapse), not .shift** → no lag.
- `run_h25_gpr.py` — DVs are **raw** `UncAnsCEO/UncPreCEO/...`, NOT residual UncResCEO;
  no `UncAnsCEO_lag` column is built anywhere (grep). (Whether raw levels deserve a lag
  is a separate, undirected question.)
- `run_h11/_lag`, the other DiD-uncres runners — no `UncResCEO_lag` built/used.
- Empire run-up + cashspec — already **drop** Lagged_DV (clean).

## LABEL footprint (the rename, if adopted) — large
`Lagged_DV` string: **331 occurrences / 80+ files** in `src/` (capped) + **60+ rendered
`per_suite/*.tex`** + 3 scripts. Most are **legit** (sticky DVs: cash, spreads, capex,
CCCL, funding) — the lag is correct there; only the *label* is imprecise.

## Tooling status (do not rely on)
- GitNexus: **broken** (DB v41 vs MCP build v40, version mismatch) AND **stale** (it
  surfaced *deleted* provenance docs). Not usable for blast radius this session.
- Provenance `docs/provenance/**` — user deleted them; ignore.

## Fix scoping (proposal — not executed)
- **A. Correctness (narrow, the directed bug):** in h24 + h24b, exclude `Lagged_DV` from
  the **UncResCEO** regression (residual). Decide UncPreCEO separately. Re-render h24/h24b.
- **B. Footgun-proofing (wide, separate Tier-2):** replace the generic `Lagged_DV` label
  with the explicit lagged-variable name so a residual DV can never silently inherit a lag.
  Touches the shared renderer + ~80 runners + 60+ tables → high blast; do as its own pass.
