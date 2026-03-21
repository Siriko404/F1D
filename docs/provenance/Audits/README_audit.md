# README.md Audit Report

**Date:** 2026-03-21
**Auditor:** Automated codebase audit
**File under audit:** `README.md` (repo root)
**Method:** Exhaustive cross-referencing of every README claim against actual codebase artifacts

---

## 1. Suite Inventory Completeness

### 1.1 Runners in codebase vs. README Hypothesis Suites table

**Active runners found** (19 files in `src/f1d/econometric/run_*.py`):

| # | Runner file | In hypothesis table? | In commands table? |
|---|-------------|---------------------|--------------------|
| 1 | `run_h0_3_ceo_clarity_extended.py` | YES | YES |
| 2 | `run_h1_cash_holdings.py` | YES | YES |
| 3 | `run_h1_1_cash_tsimm.py` | **NO** | **NO** |
| 4 | `run_h1_2_cash_constraint.py` | **NO** | **NO** |
| 5 | `run_h2_investment.py` | YES | YES |
| 6 | `run_h4_leverage.py` | YES | YES |
| 7 | `run_h5_dispersion.py` | YES | YES |
| 8 | `run_h6_cccl.py` | YES | YES |
| 9 | `run_h7_illiquidity.py` | YES | YES |
| 10 | `run_h9_takeover_hazards.py` | YES | YES |
| 11 | `run_h11_prisk_uncertainty.py` | YES | YES |
| 12 | `run_h11_prisk_uncertainty_lag.py` | YES (within H11 row) | YES |
| 13 | `run_h11_prisk_uncertainty_lead.py` | YES (within H11 row) | YES |
| 14 | `run_h12_div_intensity.py` | YES | YES |
| 15 | `run_h12q_payout.py` | **NO** | **NO** |
| 16 | `run_h13_capex.py` | YES | YES |
| 17 | `run_h13_1_competition.py` | YES | YES |
| 18 | `run_h14_bidask_spread.py` | YES | YES |
| 19 | `run_h15_repurchase.py` | YES | YES |

**FINDING:** 3 active runners are missing from both the Hypothesis Suites table and the All Econometric Scripts commands table:
- `run_h1_1_cash_tsimm.py` (H1.1 -- TNIC-moderated cash holdings)
- `run_h1_2_cash_constraint.py` (H1.2 -- financing-constraint-moderated cash holdings)
- `run_h12q_payout.py` (H12Q -- quarterly payout ratio)

### 1.2 Panel builders in codebase vs. README

**Active panel builders found** (16 files in `src/f1d/variables/build_*_panel.py`):

All 15 listed panel builders match the runners. Additionally:
- `build_h12q_payout_panel.py` exists but is NOT referenced anywhere in the README.

No panel builders exist for H1.1 or H1.2 (those suites merge TNIC/ratings data at runtime from the H1 panel).

### 1.3 Suite count claim

**README claims:** "13 hypothesis suites" (line 9)
**Actual count of distinct hypothesis IDs with active runners:**

H0.3, H1, H1.1, H1.2, H2, H4, H5, H6, H7, H9, H11 (base/lag/lead), H12, H12Q, H13, H13.1, H14, H15 = **17 distinct suite IDs** (or 15 if H11 base/lag/lead count as 1 suite).

If we count the way the README does (H11 as one suite with sub-variants): the correct count is **16 hypothesis suites** (adding H1.1, H1.2, H12Q to the 13 listed).

### 1.4 Provenance doc count claim

**README claims:** "Data provenance docs (13 suites)" (line 215)
**Actual provenance .md files in `docs/provenance/`:** 19 files (H0.3, H1, H1_1, H1_2, H2, H4, H5, H6, H7, H9, H11, H11-Lag, H11-Lead, H12, H12Q, H13, H13_1, H14, H15)

The correct count is **19 provenance documents** (or 16 if H11/H11-Lag/H11-Lead/H1/H1_1/H1_2 are grouped by parent suite).

---

## 2. Suite Description Accuracy

### 2.1 Missing suites from hypothesis table

| Suite | Research Question | Model | DV | Status |
|-------|-------------------|-------|----|--------|
| **H1.1** | Does product-market similarity (TNIC3TSIMM) moderate uncertainty-cash link? | PanelOLS + TSIMM interaction | CashHoldings / CashHoldings_lead | **MISSING from table** |
| **H1.2** | Does financing constraint moderate uncertainty-cash link? | PanelOLS + 3-category credit rating interaction | CashHoldings / CashHoldings_lead | **MISSING from table** |
| **H12Q** | Does speech uncertainty predict quarterly payout ratio? | PanelOLS (Industry FE / Firm FE) | PayoutRatio_q / PayoutRatio_q_lead_qtr / PayoutRatio_q_lead_yr | **MISSING from table** |

### 2.2 Existing suite descriptions -- spot checks

All 13 existing rows in the hypothesis table were verified against runner docstrings. No inaccuracies found in research question, model type, or DV for any of the 13 listed suites.

---

## 3. Provenance Documentation Paths

### 3.1 Red-team audit file location

**README claims (line 283):** Red-team audits are at `Audits/{SUITE_ID}_red_team.md`
**Actual location:** `docs/provenance/Audits/` -- this is CORRECT.

### 3.2 Red-team audit files inventory

**Files found in `docs/provenance/Audits/`:**

| File | Corresponding active suite? |
|------|---------------------------|
| H0.3_red_team.md | YES |
| H1_red_team.md | YES |
| H1_1_red_team.md | YES (suite missing from README table) |
| H1_2_red_team.md | YES (suite missing from README table) |
| H2_red_team.md | YES |
| H3_red_team.md | NO -- H3 is archived |
| H4_red_team.md | YES |
| H5_red_team.md | YES |
| H6_red_team.md | YES |
| H7_red_team.md | YES |
| H7_plan_red_team_audit.md | Supplementary audit |
| H9_red_team.md | YES |
| H11_red_team.md | YES |
| H11-Lag_red_team.md | YES |
| H11-Lead_red_team.md | YES |
| H12_red_team.md | YES |
| H12Q_red_team.md | YES (suite missing from README table) |
| H13_red_team.md | YES |
| H13_1_red_team.md | YES |
| H13.1_red_team.md | Duplicate naming? |
| H14_red_team.md | YES |
| H15_red_team.md | YES |
| observation_packet_audit.md | Supplementary |

**FINDING:** There appear to be two H13.1 red-team files with different naming conventions (`H13_1_red_team.md` and `H13.1_red_team.md`). This may be a duplicate or naming inconsistency.

### 3.3 Archived provenance

`docs/provenance/_archived/H3.md` exists (archived suite). There is also a `_archive` directory (note: both `_archive` and `_archived` exist -- possible unintentional duplication).

---

## 4. Prerequisites Accuracy

### 4.1 g++ compiler requirement

**README claims (line 102):** "Compiler: g++ (C++17) for Stage 2 tokenizer"
**Evidence:** `src/f1d/text/tokenize_transcripts.py` references C++ compilation. `src/f1d/shared/dependency_checker.py` and `src/f1d/shared/config/step_configs.py` also reference C++ compiler checks. The claim is **CORRECT**.

### 4.2 Input directory names

**README lists 12 input directories.** Cross-referencing with actual code references:

| README directory | Used in code? | Notes |
|-----------------|---------------|-------|
| `Earnings_Calls_Transcripts/` | YES | |
| `LM_dictionary/` | **MISMATCH** | Code uses `inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` (a file, not a directory) |
| `comp_na_daily_all/` | YES | |
| `CRSP_DSF/` | YES | |
| `tr_ibes/` | YES | |
| `CRSPCompustat_CCM/` | YES | |
| `SDC/` | YES | |
| `CCCL_instrument/` | YES | |
| `Execucomp/` | YES | |
| `FirmLevelRisk/` | YES | |
| `Manager_roles/` | Not verified (no grep hits in active code) | May be loaded by manifest builder |
| `FF1248/` | YES | |

**Missing from README:**
| Directory | Used by | Source |
|-----------|---------|--------|
| `TNIC3HHIdata/` | H1.1 (`run_h1_1_cash_tsimm.py`), H13.1 (`run_h13_1_competition.py`) | Hoberg-Phillips TNIC |
| `compustat_daily_ratings/` | H1.2 (`run_h1_2_cash_constraint.py`) | WRDS Compustat Daily |

### 4.3 Python version range

**README claims (line 99):** "Python: 3.9 -- 3.13"
**`requirements.txt` line 2:** "Python >= 3.8"
**`pyproject.toml`:** `requires-python = ">=3.9"` (no upper bound)

**FINDING:** The README states an upper bound of 3.13 that is not enforced anywhere in configuration. The lower bound of 3.9 is correct per pyproject.toml. The requirements.txt says >=3.8 which conflicts with both.

### 4.4 LM dictionary path

**README claims:** `LM_dictionary/` directory
**Code uses:** `inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` (a flat CSV file, not inside a `LM_dictionary/` directory)

This is a **factual error** -- the directory name in the prerequisites table does not match the actual path used in code.

---

## 5. Commands Accuracy

### 5.1 Missing commands from "All Econometric Scripts" table

| Suite | Missing Command |
|-------|-----------------|
| H1.1 | `python -m f1d.econometric.run_h1_1_cash_tsimm` |
| H1.2 | `python -m f1d.econometric.run_h1_2_cash_constraint` |
| H12Q | `python -m f1d.econometric.run_h12q_payout` |

### 5.2 H13.1 command

The commands table lists `H13.1` but the actual entry is missing. Wait -- re-checking: H13.1 is NOT in the commands table. The table has H13 (`run_h13_capex`) but not H13.1 (`run_h13_1_competition`).

**CORRECTION:** Upon re-reading, H13.1 is indeed absent from the commands table, but H13.1 IS in the hypothesis suites table. This is an inconsistency -- H13.1 appears in the hypothesis table but not the commands table.

**UPDATE after re-reading:** Actually the commands table only lists through H15 and does not include H13.1. Let me re-verify...

The commands table entries are: H0.3, H1, H2, H4, H5, H6, H7, H7(selection), H9, H11, H11-lag, H11-lead, H12, H13, H14, H15. **H13.1 is missing from the commands table** even though it appears in the hypothesis table.

### 5.3 CLI Flags

**README claims (line 180-182):** "All Stage 4 scripts support: `--dry-run`, `--panel-path`"

**Verification:** All 19 active runners + `ceo_presence_probit.py` were checked. All support `--dry-run` and/or `--panel-path`. The `ceo_presence_probit.py` supports `--panel-path` but does NOT appear to support `--dry-run` based on grep results.

**FINDING:** The claim "All Stage 4 scripts" may be inaccurate for `ceo_presence_probit.py` regarding `--dry-run`.

### 5.4 Stage 1 commands

**README claims (line 141):** `python -m f1d.sample.build_tenure_map` and `python -m f1d.sample.assemble_manifest`
**Actual files:** `build_tenure_map.py` exists. `assemble_manifest.py` exists. Both are valid. **CORRECT**.

---

## 6. Project Structure Accuracy

### 6.1 "80+ individual variable builders" claim

**README claims (line 206):** "80+ individual variable builders"
**Actual count:** 79 variable builder .py files (excluding `__init__.py`, engine files, `base.py`, `winsorization.py`, `panel_utils.py`)

**FINDING:** 79 is close to "80+" but technically does not meet the "80+" threshold. This is a minor inaccuracy. (Could be 80+ if some excluded files are counted differently.)

### 6.2 `iv_regression.py` existence

**README claims (line 208):** `iv_regression.py` at `src/f1d/shared/`
**Actual:** `src/f1d/shared/iv_regression.py` EXISTS. **CORRECT**.

### 6.3 `latex_tables*.py` existence

**README claims (line 209):** `latex_tables*.py` at `src/f1d/shared/`
**Actual:** Three files exist:
- `src/f1d/shared/latex_tables.py`
- `src/f1d/shared/latex_tables_complete.py`
- `src/f1d/shared/latex_tables_accounting.py`

**CORRECT** -- the wildcard notation accurately represents the three files.

### 6.4 `docs/provenance/Audits/` directory

**README claims (line 216):** `Audits/` under `docs/provenance/`
**Actual:** `docs/provenance/Audits/` EXISTS. **CORRECT**.

### 6.5 Test directory structure

**README claims (line 212):** `tests/ # unit / integration / regression / verification / performance`
**Actual subdirectories:** `unit/`, `integration/`, `regression/`, `verification/`, `performance/`, plus `factories/`, `fixtures/`, `utils/`

**FINDING:** The README omits `factories/`, `fixtures/`, and `utils/` test subdirectories. These are support directories, not test categories, so this is a **minor omission** at worst.

### 6.6 Missing `_archived` directories from structure tree

The project structure tree does not mention `_archived/` directories that exist under:
- `src/f1d/econometric/_archived/`
- `src/f1d/variables/_archived/`
- `docs/provenance/_archived/`

Minor omission -- archived code is intentionally hidden.

---

## 7. Technology Stack

### 7.1 Package versions vs. requirements.txt

| Package | README version | requirements.txt version | Match? |
|---------|---------------|-------------------------|--------|
| pandas | 2.2.3 | 2.2.3 | YES |
| numpy | 2.3.2 | 2.3.2 | YES |
| linearmodels | >=0.6.0 | >=0.6.0 | YES |
| statsmodels | 0.14.6 | 0.14.6 | YES |
| lifelines | 0.30.0 | 0.30.0 | YES |
| scipy | 1.16.1 | 1.16.1 | YES |
| structlog | >=25.0 | Not in requirements.txt | **MISSING from requirements.txt** |
| pydantic | >=2.0 | >=2.0,<3.0 | Partial match (README omits upper bound) |
| pyarrow | 21.0.0 | 21.0.0 | YES |
| rapidfuzz | >=3.14.0 | >=3.14.0 | YES |
| pandera | >=0.20.0 | Not in requirements.txt | **MISSING from requirements.txt** |

**FINDING:** `structlog` and `pandera` are listed in the README Technology Stack but are NOT in `requirements.txt`.

- `structlog`: Used in code (`src/f1d/shared/logging/`), so it IS a real dependency -- just missing from requirements.txt.
- `pandera`: Used in `src/f1d/shared/output_schemas.py`, so it IS a real dependency -- just missing from requirements.txt.

### 7.2 Missing from README Technology Stack

| Package | In requirements.txt | Used in code? |
|---------|-------------------|---------------|
| scikit-learn 1.7.2 | YES | YES (tokenize_transcripts.py) |
| PyYAML 6.0.2 | YES | YES (config loading) |
| openpyxl 3.1.5 | YES | Not found in active source |
| psutil 7.2.1 | YES | YES (observability) |
| pydantic-settings >=2.0 | YES | YES (config) |

`scikit-learn` is a notable omission from the Technology Stack since it is pinned at 1.7.2 in requirements.txt and used in Stage 2.

---

## 8. Pipeline Architecture

### 8.1 C++ compiler reference

**README claims (line 37):** Stage 2 uses "(C++ compiler)" for tokenization
**Evidence:** `tokenize_transcripts.py` has C++ compilation references, `dependency_checker.py` checks for C++ compiler.
**CORRECT.**

### 8.2 Pipeline description accuracy

The 4-stage description is accurate and matches the codebase structure.

---

## 9. Testing

### 9.1 Test directory structure

**README claims (line 263):** "Test categories: unit/ (shared module logic), integration/ (cross-stage flows), regression/ (output stability), verification/ (dry-run all scripts), performance/ (benchmarks)"

**Actual:** All five directories exist. Additional support directories (`factories/`, `fixtures/`, `utils/`) exist but are not test categories per se. **CORRECT** (the README correctly describes categories, not all subdirectories).

---

## 10. General

### 10.1 Intro statistics

**README claims (line 9):** "112,968 earnings call observations across 2,429 firms (2002-2018)"
**Not independently verified** -- would require running the pipeline to confirm. Taken as given.

### 10.2 `LM_dictionary/` vs actual LM path

As noted in Section 4.4, the README lists `LM_dictionary/` as a required input directory, but the code references `inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` directly (not inside a `LM_dictionary/` subdirectory). This is a factual error in the prerequisites table.

### 10.3 `_archive` vs `_archived` directories

Both `docs/provenance/_archive` and `docs/provenance/_archived` exist. This appears to be an unintentional duplication. The README does not mention either, so this is a codebase housekeeping issue, not a README error.

---

## Master Issue Table

| ID | Section | Description | Current (wrong) | Correct | Severity |
|----|---------|-------------|-----------------|---------|----------|
| 1 | Intro / Hypothesis Table | Suite count is wrong | "13 hypothesis suites" | 16 hypothesis suites (adding H1.1, H1.2, H12Q) | **HIGH** |
| 2 | Hypothesis Table | H1.1 suite missing from table | Not listed | Add row: H1.1 -- TNIC-moderated cash holdings, PanelOLS + TSIMM interaction, DV: CashHoldings | **HIGH** |
| 3 | Hypothesis Table | H1.2 suite missing from table | Not listed | Add row: H1.2 -- financing-constraint-moderated cash, PanelOLS + 3-cat credit interaction, DV: CashHoldings | **HIGH** |
| 4 | Hypothesis Table | H12Q suite missing from table | Not listed | Add row: H12Q -- quarterly payout ratio, PanelOLS, DV: PayoutRatio_q variants | **HIGH** |
| 5 | Commands Table | H1.1 command missing | Not listed | `python -m f1d.econometric.run_h1_1_cash_tsimm` | **HIGH** |
| 6 | Commands Table | H1.2 command missing | Not listed | `python -m f1d.econometric.run_h1_2_cash_constraint` | **HIGH** |
| 7 | Commands Table | H12Q command missing | Not listed | `python -m f1d.econometric.run_h12q_payout` | **HIGH** |
| 8 | Commands Table | H13.1 command missing | Not listed | `python -m f1d.econometric.run_h13_1_competition` | **HIGH** |
| 9 | Prerequisites | LM dictionary path is wrong | `LM_dictionary/` directory | `Loughran-McDonald_MasterDictionary_1993-2024.csv` (flat file in `inputs/`) | **HIGH** |
| 10 | Prerequisites | TNIC3HHIdata input missing | Not listed | Add `TNIC3HHIdata/` -- Hoberg-Phillips TNIC (used by H1.1, H13.1) | **MEDIUM** |
| 11 | Prerequisites | compustat_daily_ratings input missing | Not listed | Add `compustat_daily_ratings/` -- Compustat S&P credit ratings (used by H1.2) | **MEDIUM** |
| 12 | Provenance section | Provenance doc count wrong | "13 suites" | 19 provenance docs (or 16 distinct suites including sub-suites) | **MEDIUM** |
| 13 | Technology Stack | structlog missing from requirements.txt | Listed in README but not in requirements.txt | Add `structlog>=25.0` to requirements.txt | **MEDIUM** |
| 14 | Technology Stack | pandera missing from requirements.txt | Listed in README but not in requirements.txt | Add `pandera>=0.20.0` to requirements.txt | **MEDIUM** |
| 15 | Technology Stack | scikit-learn missing from README table | Not listed in README stack | Add scikit-learn 1.7.2 (used in Stage 2 tokenizer) | **LOW** |
| 16 | Prerequisites | Python upper bound (3.13) not enforced | "3.9 -- 3.13" | pyproject.toml says `>=3.9` (no upper bound); requirements.txt says `>=3.8` | **LOW** |
| 17 | Project Structure | "80+ variable builders" slightly overstated | "80+ individual variable builders" | 79 variable builder files (technically under 80) | **LOW** |
| 18 | CLI Flags | ceo_presence_probit may not support --dry-run | "All Stage 4 scripts support --dry-run" | ceo_presence_probit.py has --panel-path but --dry-run not confirmed via grep | **LOW** |
| 19 | Provenance | Duplicate H13.1 red-team files | Two files: `H13_1_red_team.md` and `H13.1_red_team.md` | Consolidate to one naming convention | **LOW** |
| 20 | Codebase | Duplicate archive dirs in provenance | Both `_archive/` and `_archived/` exist under docs/provenance/ | Consolidate to one | **LOW** |

---

## Summary

- **Total issues found:** 20
- **HIGH severity:** 9 (missing suites from tables, wrong LM path, missing commands)
- **MEDIUM severity:** 4 (missing input dirs, wrong provenance count, missing deps in requirements.txt)
- **LOW severity:** 7 (version bounds, count approximation, naming inconsistencies)

### Critical pattern

The root cause of most HIGH issues is that **3 sub-suites (H1.1, H1.2, H12Q) were added to the codebase after the README was last updated**. These suites have:
- Active runners
- Panel builders (H12Q) or runtime data merging (H1.1, H1.2)
- Full provenance documentation
- Red-team audit reports
- But zero README coverage

Additionally, H13.1 appears in the hypothesis table but is missing from the commands table.

### Recommended fix priority

1. Add H1.1, H1.2, H12Q to both the Hypothesis Suites table and Commands table
2. Add H13.1 to the Commands table
3. Fix the `LM_dictionary/` prerequisite to match the actual file path
4. Add `TNIC3HHIdata/` and `compustat_daily_ratings/` to prerequisites
5. Update suite count from 13 to 16
6. Add `structlog` and `pandera` to requirements.txt
7. Address LOW-severity items as time permits
