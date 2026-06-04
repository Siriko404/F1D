# Campello et al. (2022) — Variable Lock-in (Round 1)

**Paper**: Campello, Cortes, d'Almeida, Kankanhalli — "Exporting Uncertainty: The Impact of Brexit on Corporate America"
**Venue**: Journal of Financial and Quantitative Analysis, Vol. 57, No. 8, Dec. 2022, pp. 3178–3222
**DOI**: 10.1017/S0022109022000308   |   **Corrigendum**: 10.1017/S0022109022001259

**Lock-in date**: 2026-05-26
**Generated programmatically by**: `tmp/build_variable_lockin.py` (zero manual content)
**Scope**: 88 variables enumerated by Claude-web cold reading of full paper + IA, including DVs / Treatment / Moderators / Controls / Fixed effects / raw inputs.

## Lock-in protocol
Each variable below was triangulated across:
  1. **Claude-web** (Anthropic API, full PDF cold read) — produced the 88-variable inventory.
  2. **NLM (NotebookLM)** — produced a 17-variable inventory (under-enumerated; *additionally* fabricated Table 1 cell values — see `feedback_nlm_hallucinates_cell_values_2026_05_26.md`).
  3. **PyMuPDF anchor** (`tmp/extract_full_paper.py` + `tmp/extract_table1_anchor.py`) — programmatic extraction of main paper + IA + Table 1 cell stats (NOT LLM-typed).
  4. **Claude-web Round 2 verifier** — issued 6 minor page-attribution corrections (all applied below).
  5. **Programmatic batched verifier** (`tmp/batched_var_verifier.py`) — checked def_verbatim + page + Table 1 stats; ±1 page tolerance.
  6. **Reverify of FAILs** (`tmp/reverify_fails.py`) — 18 verifier FAILs/INCs all resolved as verifier-probe false-positives (mojibake/subscript/eq glyphs); 0 paper drift.

## Page corrections applied (8 total)

From `tmp/campello_var_anchor_check_batch_*.md` MATCH_±1 silent absorptions + Round 2 verifier:

| Var | Field | Old | New | Source |
|---|---|---|---|---|
| VAR_01 | data_source | (no Table 2 mention) | Added Table 2 "(quarterly)" restatement | Round 2 |
| VAR_08 | other_stats + uncertainty | Table 5 p3203 | Table 5 p3204 (landscape) | Round 2 |
| VAR_09 | other_stats | Table 5 p3203 | Table 5 p3204 (landscape) | Round 2 |
| VAR_11 | primary_definition.page | 3201 | 3202 | MATCH_±1 |
| VAR_26 | primary_definition.page | 3205 | 3206 (Table 6) | MATCH_±1 + Round 2 overlap |
| VAR_28 | primary_definition.page | 3191 | 3192 (§IV.A.3) | MATCH_±1 + Round 2 overlap |
| VAR_29 | primary_definition.page | 3191 | 3192 (§IV.A.3) | MATCH_±1 + Round 2 overlap |
| VAR_60 | primary_definition.page | IA p.15 | IA p.16 (Appendix E.1) | MATCH_±1 |

After corrections: ALL 88 vars exact MATCH on `page` field (zero ±1 absorptions remain).

## Inventory caveats (NOT paper drift)

- **VAR_70 / VAR_72 / VAR_73** (`market value of equity`, `book value of equity`, `deferred taxes`): inventory inflation. Component of TOBIN_Q; not a paper-listed standalone variable (Claude-web over-enumerated; safe to ignore as a separate var in code).
- **VAR_86** (`TIME`): Table-only label (appears in Tables 5/7 fixed-effects rows). No body-text definition; treat as 'calendar-quarter dummies' analog of QUARTER_t.

## Status legend
- `LOCKED` — verifier PASS + paper anchor confirms
- `LOCKED (verifier-probe false-positive resolved)` — original verifier FAIL was due to mojibake/Greek-symbol probe; reverify with looser probe confirmed paper presence
- `INVENTORY_NOTE` — variable structure issue, not paper drift (see caveats)

---

## Variables (88 total)

### VAR_01 — INVESTMENT

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> INVESTMENT is defined as capital expenditures divided by lagged total assets.

**Formula / data source**:
> INVESTMENT = capital expenditures / lagged total assets. COMPUSTAT Quarterly Fundamentals. Table 2 notes also restate '(quarterly)'; Table 10/C.7 notes likewise.

**Unit / transformation**: ratio (no unit), firm-quarter; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (INVESTMENT): mean=0.01 | SD=0.02 | median=0.01 | IQR=0.01 | N=76,094
  - Panel B (INVESTMENT): mean=0.02 | SD=0.02 | median=0.01 | IQR=0.02 | N=11,083
  - Panel C (INVESTMENT): mean=0.01 | SD=0.01 | median=0.01 | IQR=0.01 | N=12,067
  - Panel D (INVESTMENT): mean=0.01 | SD=0.02 | median=0.01 | IQR=0.01 | N=35,828
  - Panel E (INVESTMENT): mean=0.01 | SD=0.02 | median=0.01 | IQR=0.01 | N=9,389
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.01/0.02/0.01/0.01/76,094; B 0.02/0.02/0.01/0.02/11,083; C 0.01/0.01/0.01/0.01/12,067; D 0.01/0.02/0.01/0.01/35,828; E 0.01/0.02/0.01/0.01/9,389. Matched-sample means in Table C.2; pre-Brexit period means in C.4/C.5.

**Uncertainty / caveat**: Source PDF text layer strips minus signs from table cells; transcribed values are unsigned — verify against PyMuPDF anchor.

---

### VAR_02 — EMPLOYMENT_GROWTH

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> EMPLOYMENT_GROWTH is defined as the percentage change in the number of employees (annual).

**Formula / data source**:
> Percentage change in number of employees, annual. COMPUSTAT Annual Fundamentals (firm-level employment). Establishment-level analogue uses YTS (see VAR_08).

**Unit / transformation**: percentage change (annual), firm-year; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (EMPLOYMENT_GROWTH (Annual)): mean=0.08 | SD=0.28 | median=0.03 | IQR=0.16 | N=17,620
  - Panel B (EMPLOYMENT_GROWTH (Annual)): mean=0.08 | SD=0.29 | median=0.03 | IQR=0.19 | N=2,659
  - Panel C (EMPLOYMENT_GROWTH (Annual)): mean=0.06 | SD=0.20 | median=0.03 | IQR=0.11 | N=2,965
  - Panel D (EMPLOYMENT_GROWTH (Annual)): mean=0.08 | SD=0.30 | median=0.03 | IQR=0.17 | N=8,004
  - Panel E (EMPLOYMENT_GROWTH (Annual)): mean=0.08 | SD=0.30 | median=0.03 | IQR=0.16 | N=2,248
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.08/0.28/0.03/0.16/17,620; B 0.08/0.29/0.03/0.19/2,659; C 0.06/0.20/0.03/0.11/2,965; D 0.08/0.30/0.03/0.17/8,004; E 0.08/0.30/0.03/0.16/2,248. Also C.2, C.4/C.5.

**Uncertainty / caveat**: Minus signs stripped by PDF text layer; verify signs against PyMuPDF anchor.

---

### VAR_03 — R&D

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures.

**Formula / data source**:
> R&D = R&D expenditures / lagged total assets. COMPUSTAT. Table 3 notes give: 'R&D is defined as total R&D expenditures divided by lagged total assets.'

**Unit / transformation**: ratio (no unit), firm-quarter; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (R&D): mean=0.03 | SD=0.04 | median=0.02 | IQR=0.04 | N=40,864
  - Panel B (R&D): mean=0.03 | SD=0.04 | median=0.02 | IQR=0.04 | N=5,019
  - Panel C (R&D): mean=0.02 | SD=0.03 | median=0.01 | IQR=0.02 | N=6,200
  - Panel D (R&D): mean=0.03 | SD=0.04 | median=0.02 | IQR=0.04 | N=19,988
  - Panel E (R&D): mean=0.03 | SD=0.04 | median=0.01 | IQR=0.03 | N=4,745
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.03/0.04/0.02/0.04/40,864; B 0.03/0.04/0.02/0.04/5,019; C 0.02/0.03/0.01/0.02/6,200; D 0.03/0.04/0.02/0.04/19,988; E 0.03/0.04/0.01/0.03/4,745. Also C.2, C.4/C.5.

**Uncertainty / caveat**: Definition appears in two slightly different wordings (Table 1 vs Table 3 notes).

---

### VAR_04 — DIVESTITURES

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> DIVESTITURES is defined as the value of sale of plant, property, and equipment divided by lagged total assets.

**Formula / data source**:
> DIVESTITURES = value of sale of plant, property, and equipment (SPP&E) / lagged total assets. COMPUSTAT. Table 3 notes: 'DIVESTITURES are defined as the value of SPP&E (Sale of Plant, Property, and Equipment) divided by lagged total assets.'

**Unit / transformation**: ratio; printed as DIVESTITURES (×100) in Table 1; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (DIVESTITURES (100)): mean=0.06 | SD=0.28 | median=0.00 | IQR=0.00 | N=61,151
  - Panel B (DIVESTITURES (100)): mean=0.10 | SD=0.38 | median=0.00 | IQR=0.00 | N=8,604
  - Panel C (DIVESTITURES (100)): mean=0.08 | SD=0.32 | median=0.00 | IQR=0.01 | N=9,422
  - Panel D (DIVESTITURES (100)): mean=0.05 | SD=0.26 | median=0.00 | IQR=0.00 | N=29,009
  - Panel E (DIVESTITURES (100)): mean=0.05 | SD=0.24 | median=0.00 | IQR=0.00 | N=7,377
  - other_stats (from inventory): Reported as DIVESTITURES (×100). Per-panel [Mean/SD/Median/IQR/N]: A 0.06/0.28/0.00/0.00/61,151; B 0.10/0.38/0.00/0.00/8,604; C 0.08/0.32/0.00/0.01/9,422; D 0.05/0.26/0.00/0.00/29,009; E 0.05/0.24/0.00/0.00/7,377. C.2 reports DIVESTITURES (×100): treated 0.129 / control 0.088 (Panel A).

**Uncertainty / caveat**: Table 1 scaling label '(×100)' partially garbled in source text layer.

---

### VAR_05 — CASH

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> CASH is defined as cash and short-term investments divided by lagged total assets.

**Formula / data source**:
> CASH = cash and short-term investments / lagged total assets. COMPUSTAT.

**Unit / transformation**: ratio; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (CASH): mean=0.22 | SD=0.25 | median=0.12 | IQR=0.27 | N=78,044
  - Panel B (CASH): mean=0.20 | SD=0.24 | median=0.11 | IQR=0.26 | N=11,176
  - Panel C (CASH): mean=0.17 | SD=0.18 | median=0.11 | IQR=0.19 | N=12,097
  - Panel D (CASH): mean=0.23 | SD=0.25 | median=0.13 | IQR=0.29 | N=36,985
  - Panel E (CASH): mean=0.22 | SD=0.24 | median=0.12 | IQR=0.26 | N=9,533
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.22/0.25/0.12/0.27/78,044; B 0.20/0.24/0.11/0.26/11,176; C 0.17/0.18/0.11/0.19/12,097; D 0.23/0.25/0.13/0.29/36,985; E 0.22/0.24/0.12/0.26/9,533.

**Uncertainty / caveat**: CONFLICTING DEFINITION: Table 8 notes (p. 3208) redefine CASH as 'total cash holdings divided by lagged total assets net of cash holdings.' Table 1 vs Table 8 denominators differ — the Table 8 specification (Section V.C) is the one used in the CASH regression tests.

---

### VAR_06 — NON_CASH_WORKING_CAPITAL (NWC)

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets.

**Formula / data source**:
> NWC = working capital (net of cash) / lagged total assets. COMPUSTAT. Same wording in Table 8 notes.

**Unit / transformation**: ratio; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (NON_CASH_WORKING_CAPITAL): mean=0.04 | SD=0.19 | median=0.03 | IQR=0.20 | N=76,323
  - Panel B (NON_CASH_WORKING_CAPITAL): mean=0.05 | SD=0.18 | median=0.04 | IQR=0.19 | N=10,846
  - Panel C (NON_CASH_WORKING_CAPITAL): mean=0.08 | SD=0.16 | median=0.07 | IQR=0.20 | N=11,738
  - Panel D (NON_CASH_WORKING_CAPITAL): mean=0.01 | SD=0.20 | median=0.02 | IQR=0.20 | N=36,292
  - Panel E (NON_CASH_WORKING_CAPITAL): mean=0.06 | SD=0.19 | median=0.04 | IQR=0.21 | N=9,260
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.04/0.19/0.03/0.20/76,323; B 0.05/0.18/0.04/0.19/10,846; C 0.08/0.16/0.07/0.20/11,738; D 0.01/0.20/0.02/0.20/36,292; E 0.06/0.19/0.04/0.21/9,260.

**Uncertainty / caveat**: Working-capital component can be negative; minus signs stripped in source text layer — verify means/medians signs against PyMuPDF anchor.

---

### VAR_07 — PROFITS

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3208
- **section_or_table**: Table 8 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> PROFITS is defined as the quarterly percentage change in profits (operating income before depreciation divided by sales).

**Formula / data source**:
> PROFITS = quarterly % change in (operating income before depreciation / sales). COMPUSTAT.

**Unit / transformation**: percentage change (quarterly), firm-quarter

**Other reported stats**: Not in Table 1; only regression coefficients (Table 8, cols 5–6, p. 3208) are reported.

---

### VAR_08 — ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH (column header: 'ESTABLISHMENT_LEVEL_EMPLOYMENT_GROWTH')

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3202
- **section_or_table**: §V.B.1.b text + Table 5 header/notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We first repeat the analysis of Table 2 using establishment-level employment growth calculated based on YTS data on the number of employees across all establishments operated by sample firms in the United States.

**Formula / data source**:
> Percentage change in number of employees aggregated across all U.S. establishments of a firm, from YTS (Your-Economy Time-Series) database.

**Unit / transformation**: percentage change, firm-year (U.S. establishments only)

**Other reported stats**: Only regression coefficients reported (Table 5, cols 1–2, p. 3204).

**Uncertainty / caveat**: Table 5 column structure is heavily garbled in the source text layer (page 3204, landscape); column-to-coefficient mapping should be confirmed against PyMuPDF anchor.

---

### VAR_09 — ESTABLISHMENT_TURNOVER

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3203
- **section_or_table**: Footnote 24
- **paragraph_position**: N/A (footnote)

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments.

**Formula / data source**:
> (establishment openings + establishment closings) / lagged total number of establishments. YTS database.

**Unit / transformation**: ratio, firm-year

**Other reported stats**: Only regression coefficients reported (Table 5, cols 3–4, p. 3204).

---

### VAR_10 — INVESTMENT (U.S.-based subsidiaries)

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3201
- **section_or_table**: §V.B.1.a text + Table 4 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> For each parent firm, in each year, we compute their U.S.-based investment by summing fixed capital spending across their U.S. subsidiaries.

**Formula / data source**:
> Sum of fixed capital spending across a parent firm's U.S. subsidiaries (then scaled as INVESTMENT). Bureau van Dijk Orbis subsidiary-level data.

**Unit / transformation**: ratio, firm-year (parent firm, U.S. subsidiaries)

**Other reported stats**: Regression coefficients only (Table 4, cols 1–2, p. 3203).

**Uncertainty / caveat**: Text (p. 3201) refers to results 'in columns 1 and 2 of Table 3' but Table 4 holds the subsidiary results; cross-reference appears to be a typo in the body text.

---

### VAR_11 — INVESTMENT (U.K.-based subsidiaries)

- **status**: `LOCKED`
- **role**: DV
- **raw_or_derived**: derived
- **page**: 3202
- **section_or_table**: §V.B.1.a text + Table 4 notes
- **paragraph_position**: 3

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We similarly calculate the total U.K.-based investment of each U.S. parent firm by summing spending figures across U.K. subsidiaries.

**Formula / data source**:
> Sum of fixed capital spending across a parent firm's U.K. subsidiaries (then scaled as INVESTMENT). Orbis subsidiary-level data.

**Unit / transformation**: ratio, firm-year (parent firm, U.K. subsidiaries)

**Other reported stats**: Regression coefficients only (Table 4, cols 3–4, p. 3203).

---

### VAR_12 — AUTOMATIONi,t

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: DV
- **raw_or_derived**: derived
- **page**: IA p. 18 (Internet Appendix)
- **section_or_table**: Table E.2 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> The dependent variable is AUTOMATIONi,t, which is constructed from a dictionary of keywords that capture exposure to automation at the firm level, as described in Appendix E. This text-based continuous variable is the logarithm of the total number of automation-related keywords that appear in firm i's business description (10-K Section 1) and management discussion (10-K Section 7), at the firm-year level.

**Formula / data source**:
> Time-varying analogue of AUTOMATIONi = log(total automation-related keyword count in 10-K Sections 1 and 7), at firm-year level. Firms' 10-K filings.

**Unit / transformation**: log count, firm-year

**Other reported stats**: Distribution of the (time-averaged) AUTOMATIONi shown as a histogram in Figure E.1 (IA p. 16); no numeric moments printed. Table E.2 reports only regression coefficients (cols 1–2).

**Uncertainty / caveat**: AUTOMATIONi,t (time-varying, firm-year, DV in Table E.2) differs from AUTOMATIONi (time-averaged 2010–2015, RHS control in Table 11). Both share the AUTOMATION root — list separately (see VAR_59).

---

### VAR_13 — βUK_i (β_i^UK)

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3191
- **section_or_table**: §IV.A.1 text + equation (13)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Following Bloom (2014), we use stock market volatility as a gauge of aggregate uncertainty and estimate equation (12) for each firm i as vol(r_it) = α_i + β_i^UK vol(FTSE100_t) + θCONTROLS_t + ϵ_it (13). … For each firm, we take the estimated value of β_i^UK from regression (13) as the empirical counterpart to β_i in our framework.

**Formula / data source**:
> Firm-by-firm OLS slope on vol(FTSE100) in eq (13): vol(r_it) = α_i + β_i^UK·vol(FTSE100_t) + θ·CONTROLS_t + ϵ_it, where CONTROLS_t = vol(SP500) and vol(FX$£). Monthly data 2010:M1–2014:M12. Empirical counterpart to theoretical sensitivity parameter β_i.

**Unit / transformation**: regression coefficient (no unit), firm-level

**Other reported stats**: Cutoffs given in §IV.C.1 (p. 3193): treated = β_i^UK > 0.68 (449 unique firms); control = β_i^UK < 0.28 (360 unique firms).

**Uncertainty / caveat**: Superscript UK and subscript i are reconstructed from garbled glyphs 'βUKi' in the source text layer.

---

### VAR_14 — HIGH_UK_EXPOSURE_i / HIGH_βUK_i

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3196
- **section_or_table**: §IV.C.3 text (equation (14) variable definitions)
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> HIGH_UK_EXPOSURE_i is a dummy variable that equals 1 if firm i is U.K.-exposed, and 0 otherwise. A firm is considered to be U.K.-exposed according to two measures: i) if it belongs to the top tercile of β_i^UK (market-based measure); or ii) if it has a high number of Brexit-related entries in its 2015 10-K form (textual-search-based measure).

**Formula / data source**:
> Dummy = 1 if firm in top tercile of β_i^UK (market-based) OR has >5 Brexit-related 10-K entries (text-based); control = bottom tercile of β_i^UK or zero 10-K entries.

**Unit / transformation**: binary {0,1}, firm-level

**Other reported stats**: Group sizes (market-based): 449 treated / 360 control (§IV.C.1, p. 3193).

**Uncertainty / caveat**: Printed as both 'HIGH_UK_EXPOSURE' and 'HIGH_βUK_i' / 'HIGH_β_i^UK' across text and table column headers for the same market-based dummy.

---

### VAR_15 — number of Brexit-related entries in 2015 10-K (count)

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3191
- **section_or_table**: §IV.A.2
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we look for the number of entries of keywords related to uncertainty about Brexit (\"Brexit,\" \"Great Britain,\" and \"Uncertainty\") in firms' disclosures, classifying firms with a \"high\" number of entries as HIGH_UK_EXPOSURE firms, and those with zero entries as control firms.

**Formula / data source**:
> Word count of Brexit-related keywords ('Brexit,' 'Great Britain,' 'Uncertainty') in firms' 2015 10-K filings. Footnote 14: 'Referendum,' 'Uncertain,' 'United Kingdom,' 'UK,' 'U.K.,' and 'G.B.' are subsumed by the above wording.

**Unit / transformation**: count, firm-level (2015 10-K)

**Other reported stats**: Cutoff >5 entries. 807 firms cite Brexit more than 5 times; 433 cite zero (p. 3192/3193).

---

### VAR_16 — HIGH_10K_ENTRIES (printed: 'HIGH_10K_ENTRIES' / 'Treatment is > 5 Brexit Entries in 10-Ks')

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3193
- **section_or_table**: §IV.C.1
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Under this approach, 807 firms are assigned to the treated category (2015 10-K mentions of Brexit terms > 5). A total of 433 firms in the control category have no mentions of Brexit-related terms in their 10-Ks.

**Formula / data source**:
> Dummy = 1 if 2015 10-K Brexit-related entry count >5; 0 if zero entries (control). Derived from VAR_15.

**Unit / transformation**: binary {0,1}, firm-level

**Other reported stats**: 807 treated / 433 control.

---

### VAR_17 — POST_t

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3196
- **section_or_table**: §IV.C.3 (equation (14) variable definitions)
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> POST_t equals 1 if the time period is in the 2016:Q3–Q4 window.

**Formula / data source**:
> Time dummy = 1 for 2016:Q3–Q4 window (compared against 2015:Q3–Q4). Alternative windows in robustness (Table 12): 2016:Q3 vs 2015:Q3; 2015:Q3 vs 2014:Q3; 2011:Q2–Q4 vs 2010:Q2–Q4.

**Unit / transformation**: binary {0,1}, time-level

**Other reported stats**: Standalone POST coefficients reported in linear-model specifications (e.g., Table 2 col 1: 0.022; Table C.7 Panel A col 1: −0.042).

---

### VAR_18 — βUK_i,CF (β_i,CF^UK)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3191
- **section_or_table**: Footnote 13
- **paragraph_position**: N/A (footnote)

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Following Vuolteenaho (2002), we also decompose the volatility of each firm's returns into cash flow and discount rate components and reestimate equation (13) with the cash flow component (only) as the dependent variable, obtaining an alternative uncertainty measure, β_i,CF^UK.

**Formula / data source**:
> Re-estimate eq (13) using the cash-flow-news component of return volatility (Campbell–Shiller (1988) / Vuolteenaho (2002) decomposition) as the dependent variable. IA Table C.6 notes give full construction.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Rank correlation with β_i^UK = 0.8; 86% overlap of top-tercile sets (footnote 13). Results in IA Table C.6.

---

### VAR_19 — βEU_i (β_i^EU)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) re-estimated with the EU main equity index volatility; controls = FTSE100 vol, USD/GBP FX-rate vol, and USD/EUR FX-rate vol. Pre-Brexit window 2010:M1–2014:M12.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Treatment = top tercile of positive values. Coefficient in Table 13 col 2.

---

### VAR_20 — βCHINA_i (β_i^CHINA)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) using China's main equity index volatility; controls include FTSE100 vol, USD/GBP FX vol, and USD/CNY FX vol.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Coefficient in Table 13 col 3 (statistically insignificant).

---

### VAR_21 — βMEXICO_i (β_i^MEXICO)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) using Mexico's main equity index volatility; FX controls include USD/MXN.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Coefficient in Table 13 col 4 (insignificant).

---

### VAR_22 — βJAPAN_i (β_i^JAPAN)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) using Japan's main equity index volatility; FX controls include USD/JPY.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Coefficient in Table 13 col 5 (insignificant).

---

### VAR_23 — βINDIA_i (β_i^INDIA)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) using India's main equity index volatility; FX controls include USD/INR.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Coefficient in Table 13 col 6 (insignificant).

---

### VAR_24 — βBRAZIL_i (β_i^BRAZIL)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: §VI.F text + Table 13
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we repeat our tests classifying firms based on a given criterion (β_i^EU, β_i^CHINA, β_i^MEXICO, β_i^JAPAN, β_i^INDIA, and β_i^BRAZIL) according to the sensitivity of their equity returns volatility to the respective region's main equity index return volatility.

**Formula / data source**:
> Analogue of eq (13) using Brazil's main equity index volatility; FX controls include USD/BRL.

**Unit / transformation**: regression coefficient, firm-level

**Other reported stats**: Coefficient in Table 13 col 7 (insignificant).

---

### VAR_25 — U.K. Offshoring Index (Input and Output / Total) — 'HIGH_UK_OFFSHORING_INDEX'

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3205
- **section_or_table**: §V.B.2 text + Table 6 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We do this using the index of firms' offshoring activities developed by Hoberg and Moon (2017). This index, derived from firms' 10-K filings, counts mentions of words related to the purchase of inputs (\"Input\") and sale of outputs (\"Output\") from each country a firm does business with within a year. For each sample firm, we compute the sum of the Input and Output indices associated with the United Kingdom over the 2010–2014 period … We define as highly U.K.-offshoring-exposed firms those with a value of greater than 5 on a given offshoring index. Control firms are those with scores of 0 on the same index.

**Formula / data source**:
> Hoberg and Moon (2017) offshoring index summed over 2010–2014, combining Input + Output mentions for the U.K.; treatment dummy = 1 if total >5, control = 0.

**Unit / transformation**: binary {0,1} treatment dummy from a count index, firm-level

**Other reported stats**: Coefficient in Table 6 col 3 (0.074***).

---

### VAR_26 — U.K. Offshoring Index (Input Only)

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3206
- **section_or_table**: §V.B.2 text + Table 6 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> In the fourth column, the treatment group consists of firms with scores of greater than 5 on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering only input offshoring activities, whereas the control group is made of firms with scores of 0 on this index.

**Formula / data source**:
> Hoberg and Moon (2017) Input offshoring index for the U.K., summed 2010–2014; treatment dummy = 1 if >5, control = 0.

**Unit / transformation**: binary {0,1}, firm-level

**Other reported stats**: Coefficient in Table 6 col 4 (0.095***).

---

### VAR_27 — U.K. Offshoring Index (Output Only)

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3206
- **section_or_table**: Table 6 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> In the final specification, the treatment group consists of firms with scores of greater than 5 on the Hoberg and Moon (2017) U.K. Offshoring Index summed up over years 2010–2014, considering only output offshoring activities, whereas the control group is made of firms with scores of 0 on this index.

**Formula / data source**:
> Hoberg and Moon (2017) Output offshoring index for the U.K., summed 2010–2014; treatment dummy = 1 if >5, control = 0.

**Unit / transformation**: binary {0,1}, firm-level

**Other reported stats**: Coefficient in Table 6 col 5 (0.000; effect zero).

---

### VAR_28 — asset redeployability index (Kim and Kung (2016)) / HIGH_INPUT_IRREVERSIBILITY (capital)

- **status**: `LOCKED`
- **role**: Moderator
- **raw_or_derived**: derived
- **page**: 3192
- **section_or_table**: §IV.A.3 text
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> To empirically measure capital irreversibility, we use an index of capital redeployability proposed by Kim and Kung (2016). That index classifies fixed capital liquidity in terms of salability of assets in secondary markets. … Higher values of the asset redeployability index are associated with a lower degree of capital irreversibility, corresponding to a lower value of F_iK in our framework.

**Formula / data source**:
> Kim and Kung (2016) asset redeployability index. Table 7 notes: 'High capital irreversibility is defined as the top tercile of the Kim and Kung (2016) index of asset redeployability (at the firm level).' (Bottom tercile of redeployability = high irreversibility.)

**Unit / transformation**: index (no unit) → tercile partition, firm-level

**Other reported stats**: Used to form High/Low irreversibility subsamples (Table 7, cols 1–3).

**Uncertainty / caveat**: Table 7 notes call the top tercile 'High capital irreversibility' while §IV.A.3 ties high redeployability to LOW irreversibility — confirm the exact direction of the tercile cut against the code.

---

### VAR_29 — labor unionization rate (BEA) / High labor irreversibility

- **status**: `LOCKED`
- **role**: Moderator
- **raw_or_derived**: derived
- **page**: 3192
- **section_or_table**: §IV.A.3 text
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we measure the percentage of total employees who are unionized at the 4-digit SIC level using data from the Bureau of Economic Analysis.

**Formula / data source**:
> Percentage of unionized employees at 4-digit SIC level, from BEA. Table 7 notes: 'High labor irreversibility is defined as the top tercile of the labor unionization rate (at the industry level).'

**Unit / transformation**: percentage → tercile partition, industry-level (4-digit SIC)

**Other reported stats**: Used to form High/Low irreversibility subsamples (Table 7, cols 4–6).

**Uncertainty / caveat**: Table 7 notes describe its proxy role: 'The proxy for labor adjustment costs is the labor unionization rate from the Bureau of Economic Analysis.'

---

### VAR_30 — labor skills index (LSI) (Ghaly, Dang, and Stathopoulos (2017))

- **status**: `LOCKED`
- **role**: Moderator
- **raw_or_derived**: derived
- **page**: 3203
- **section_or_table**: §V.B.1.b text
- **paragraph_position**: 3

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> As a proxy for labor skills, we use the industry-level labor skills index (LSI) proposed by Ghaly, Dang, and Stathopoulos (2017). The LSI is based on data from the Occupational Employment Statistics compiled by the Bureau of Labor Statistics (BLS) and the Department of Labor's O*NET program classification.

**Formula / data source**:
> Weighted-average O*NET occupational skills classification (1–5 scale) across all occupations in an industry, weighted by fraction of workers per occupation (BLS Occupational Employment Statistics + O*NET). Table 5 notes: 'Low (high) skills firms are defined as firms in the bottom (top) tercile of the 2015 LSI (at the industry level).'

**Unit / transformation**: index (1–5 scale, weighted average) → tercile partition, industry-level

**Other reported stats**: Used to form Low/High Skills subsamples (Table 5, cols 5–8).

**Uncertainty / caveat**: Construction text continued on p. 3204.

---

### VAR_31 — POST_t × βUK_i  (POST·β_i^UK, linear continuous treatment)

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3199
- **section_or_table**: §V.A text + Table 2 col 1 header
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We begin with a firm-fixed effects estimation in which β_i^UK enters the specification as a linear continuous-treatment variable in column 1, allowing for the entire range of β_i^UK values. The POST·β_i^UK interaction coefficient is negative and highly significant, consistent with Prediction 1.

**Formula / data source**:
> Interaction of POST_t (VAR_17) with continuous β_i^UK (VAR_13) in eq (14).

**Unit / transformation**: interaction term, firm-quarter

**Other reported stats**: Coefficients: INVESTMENT −0.047*** (Table 2 col 1); EMPLOYMENT_GROWTH −4.173** (Table 2 col 4); R&D 0.361*** (Table 3 col 1); DIVESTITURES 0.012*** (Table 3 col 4).

**Uncertainty / caveat**: Table 2 column block in source text layer interleaves INVESTMENT and EMPLOYMENT_GROWTH coefficient rows; confirm sign/column mapping against PyMuPDF anchor.

---

### VAR_32 — POST × HIGH_βUK_i  (POST·HIGH_β_i^UK)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3196
- **section_or_table**: equation (14), §IV.C.3
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.

**Formula / data source**:
> Interaction POST_t × HIGH_β_i^UK (top-vs-bottom-tercile market-based treatment dummy). δ is the DID estimator.

**Unit / transformation**: interaction term, firm-quarter

**Other reported stats**: Baseline coefficients: INVESTMENT −0.165*** (Table 2); EMPLOYMENT_GROWTH −4.912*** (Table 2); R&D 0.238*** (Table 3); DIVESTITURES −0.027** (Table 3); CASH 0.231*** (Table 8); NWC −0.687*** (Table 8); PROFITS 0.135 n.s. (Table 8).

**Uncertainty / caveat**: Signs reconstructed where stripped; verify against anchor.

---

### VAR_33 — POST × HIGH_10K_ENTRIES

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3196
- **section_or_table**: equation (14), §IV.C.3
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.

**Formula / data source**:
> Interaction POST_t × HIGH_10K_ENTRIES (text-based treatment dummy, VAR_16). δ is the DID estimator under the text-based scheme.

**Unit / transformation**: interaction term, firm-quarter

**Other reported stats**: Baseline coefficients: INVESTMENT −0.077*** (Table 2); EMPLOYMENT_GROWTH −2.617*** (Table 2); R&D 0.213*** (Table 3); DIVESTITURES −0.027*** (Table 3); CASH 0.357*** (Table 8); NWC −0.608*** (Table 8); PROFITS 0.343 n.s. (Table 8).

---

### VAR_34 — POST × HIGH_UK_OFFSHORING_INDEX

- **status**: `LOCKED`
- **role**: Treatment
- **raw_or_derived**: derived
- **page**: 3206
- **section_or_table**: Table 6 (column headers + notes)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> In the third column, the treatment group consists of firms with scores of greater than five on the Hoberg–Moon U.K. Offshoring Index summed up over years 2010–2014, considering both input and output offshoring activities, whereas the control group is made of firms with scores of 0 on this index.

**Formula / data source**:
> Interaction POST_t × HIGH_UK_OFFSHORING_INDEX (Total / Input-only / Output-only treatment dummies, VAR_25/26/27).

**Unit / transformation**: interaction term, firm-quarter

**Other reported stats**: INVESTMENT coefficients (Table 6): Total −0.074***; Input-only −0.095***; Output-only 0.000.

---

### VAR_35 — POST × HIGH_βUK_i × HIGH_INPUT_IRREVERSIBILITY (DIDID triple interaction)

- **status**: `LOCKED`
- **role**: Moderator
- **raw_or_derived**: derived
- **page**: 3207
- **section_or_table**: §V.B.3 text + Table 7 (col 3 / col 6 rows)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> The estimation under column 3 uses the entire sample of firms, introducing a dummy variable High Irreversibility that equals 1 if the firm is in the high irreversibility group. The coefficient on this variable can be interpreted as a third difference in a differences-test framework, that is, as a difference-in-difference-in-differences (DIDID) estimate.

**Formula / data source**:
> Triple interaction POST_t × HIGH_β_i^UK × HIGH_INPUT_IRREVERSIBILITY, printed in Table 7 as 'POST·HIGH_βUK_i·HIGH_INPUT_IRREVERSIBILITY'. Capital version uses Kim–Kung redeployability (VAR_28); labor version uses unionization (VAR_29).

**Unit / transformation**: triple interaction term, firm-quarter (investment) / firm-year (employment)

**Other reported stats**: Triple-interaction coefficients (Table 7): INVESTMENT −0.397*** (col 3); EMPLOYMENT_GROWTH −3.577*** (col 6).

**Uncertainty / caveat**: Table 7 row label printed as 'POSTHIGH_βUKiHIGH_INPUT_IRREVERSIBILITY' (operators dropped in source text layer).

---

### VAR_36 — POST × HIGH_βCOUNTRY_i  (POST·HIGH_β^COUNTRY)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3216
- **section_or_table**: Table 13 (row header)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> treated firms are in the highest tercile of positive values of exposure of firm-level volatility to equity index volatility in the European Union, China, Mexico, Japan, India, and Brazil, respectively.

**Formula / data source**:
> Generic interaction POST_t × HIGH_β_i^COUNTRY; instantiated per country (VAR_19–24). Investment DV.

**Unit / transformation**: interaction term, firm-quarter

**Other reported stats**: Table 13 INVESTMENT coefficients: UK −0.165***; EU −0.066***; China −0.048; Mexico −0.069; Japan −0.084; India −0.058; Brazil −0.054. (Only UK and EU significant.)

**Uncertainty / caveat**: Signs stripped in source; reconstructed from text discussion (§VI.F).

---

### VAR_37 — POST × HIGH_βUK_i,CF  (POST·HIGH_β_i,CF^UK)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: IA p. 11
- **section_or_table**: Table C.6 (row header + notes)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> The treatment group is composed by the top tercile of β^UK_i,CF, while the control group is composed by firms in the bottom tercile of β^UK_i,CF.

**Formula / data source**:
> Interaction POST_t × top-tercile dummy of β_i,CF^UK (VAR_18). DVs: INVESTMENT, EMPLOYMENT_GROWTH, R&D, DIVESTITURES.

**Unit / transformation**: interaction term, firm-quarter / firm-year

**Other reported stats**: IA Table C.6 coefficients: INVESTMENT −0.330***; EMPLOYMENT_GROWTH −5.147**; R&D 0.348***; DIVESTITURES −0.034***.

---

### VAR_38 — TOBIN_Q (Tobin's Q)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> TOBIN_Q is defined as the market value of assets divided by the book value of assets, and is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.

**Formula / data source**:
> TOBIN_Q = (market value of equity + book value of assets − book value of equity + deferred taxes) / book value of assets. COMPUSTAT + CRSP.

**Unit / transformation**: ratio (no unit); winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (TOBIN_Q): mean=2.11 | SD=1.59 | median=1.57 | IQR=1.26 | N=73,353
  - Panel B (TOBIN_Q): mean=1.92 | SD=1.51 | median=1.41 | IQR=1.01 | N=11,090
  - Panel C (TOBIN_Q): mean=1.98 | SD=1.25 | median=1.62 | IQR=1.07 | N=12,055
  - Panel D (TOBIN_Q): mean=2.10 | SD=1.59 | median=1.55 | IQR=1.29 | N=34,108
  - Panel E (TOBIN_Q): mean=2.06 | SD=1.54 | median=1.55 | IQR=1.17 | N=9,138
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 2.11/1.59/1.57/1.26/73,353; B 1.92/1.51/1.41/1.01/11,090; C 1.98/1.25/1.62/1.07/12,055; D 2.10/1.59/1.55/1.29/34,108; E 2.06/1.54/1.55/1.17/9,138.

**Uncertainty / caveat**: Also enters as firm-level control (p. 3197) and is reported in Table C.7 with coefficients.

---

### VAR_39 — CASH_FLOW

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> CASH_FLOW is defined as operating income before depreciation divided by lagged total assets.

**Formula / data source**:
> CASH_FLOW = operating income before depreciation / lagged total assets. COMPUSTAT.

**Unit / transformation**: ratio; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (CASH_FLOW): mean=0.01 | SD=0.06 | median=0.03 | IQR=0.04 | N=75,287
  - Panel B (CASH_FLOW): mean=0.01 | SD=0.06 | median=0.02 | IQR=0.04 | N=10,972
  - Panel C (CASH_FLOW): mean=0.03 | SD=0.04 | median=0.03 | IQR=0.03 | N=11,871
  - Panel D (CASH_FLOW): mean=0.01 | SD=0.07 | median=0.02 | IQR=0.04 | N=35,432
  - Panel E (CASH_FLOW): mean=0.01 | SD=0.07 | median=0.02 | IQR=0.04 | N=9,240
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.01/0.06/0.03/0.04/75,287; B 0.01/0.06/0.02/0.04/10,972; C 0.03/0.04/0.03/0.03/11,871; D 0.01/0.07/0.02/0.04/35,432; E 0.01/0.07/0.02/0.04/9,240. Table C.7 reports CASH_FLOW control coefficients.

**Uncertainty / caveat**: Cash flow is frequently negative; minus signs stripped in source — mean values likely include dropped signs (e.g., several panel means may be negative). Verify against anchor.

---

### VAR_40 — SIZE (Log Assets)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> SIZE is defined as the logarithm of total assets.

**Formula / data source**:
> SIZE = log(total assets). COMPUSTAT.

**Unit / transformation**: log of USD; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (SIZE (Log Assets)): mean=6.19 | SD=2.08 | median=6.15 | IQR=3.08 | N=78,062
  - Panel B (SIZE (Log Assets)): mean=6.11 | SD=1.87 | median=6.12 | IQR=2.86 | N=11,176
  - Panel C (SIZE (Log Assets)): mean=7.25 | SD=1.99 | median=7.25 | IQR=2.65 | N=12,097
  - Panel D (SIZE (Log Assets)): mean=6.08 | SD=2.06 | median=6.02 | IQR=3.12 | N=37,002
  - Panel E (SIZE (Log Assets)): mean=5.95 | SD=2.15 | median=5.86 | IQR=3.23 | N=9,533
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 6.19/2.08/6.15/3.08/78,062; B 6.11/1.87/6.12/2.86/11,176; C 7.25/1.99/7.25/2.65/12,097; D 6.08/2.06/6.02/3.12/37,002; E 5.95/2.15/5.86/3.23/9,533. Table C.7 reports SIZE coefficients.

---

### VAR_41 — SALES_GROWTH

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales.

**Formula / data source**:
> SALES_GROWTH = year-on-year % change in quarterly sales. COMPUSTAT.

**Unit / transformation**: percentage change; winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (SALES_GROWTH): mean=0.16 | SD=0.62 | median=0.06 | IQR=0.23 | N=71,637
  - Panel B (SALES_GROWTH): mean=0.18 | SD=0.71 | median=0.06 | IQR=0.31 | N=10,624
  - Panel C (SALES_GROWTH): mean=0.10 | SD=0.36 | median=0.06 | IQR=0.16 | N=11,969
  - Panel D (SALES_GROWTH): mean=0.17 | SD=0.66 | median=0.06 | IQR=0.25 | N=33,647
  - Panel E (SALES_GROWTH): mean=0.17 | SD=0.67 | median=0.05 | IQR=0.22 | N=8,835
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.16/0.62/0.06/0.23/71,637; B 0.18/0.71/0.06/0.31/10,624; C 0.10/0.36/0.06/0.16/11,969; D 0.17/0.66/0.06/0.25/33,647; E 0.17/0.67/0.05/0.22/8,835. Table C.7 reports SALES_GROWTH coefficients.

---

### VAR_42 — CONSENSUS_EARNINGS_FORECAST

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> CONSENSUS_EARNINGS_FORECAST is defined as the standardized mean 1-quarter ahead earnings per share forecast.

**Formula / data source**:
> Standardized mean 1-quarter-ahead EPS forecast. I/B/E/S. Added 'As an additional control for first-moment effects of Brexit' (p. 3197).

**Unit / transformation**: standardized (mean 0, SD 1)

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - Panel A (CONSENSUS_EARNINGS_FORECAST): mean=0.07 | SD=3.51 | median=0.09 | IQR=2.05 | N=42,031
  - Panel B (CONSENSUS_EARNINGS_FORECAST): mean=0.01 | SD=3.40 | median=0.01 | IQR=1.83 | N=8,963
  - Panel C (CONSENSUS_EARNINGS_FORECAST): mean=0.07 | SD=2.33 | median=0.04 | IQR=2.40 | N=10,720
  - Panel D (CONSENSUS_EARNINGS_FORECAST): mean=0.04 | SD=3.46 | median=0.04 | IQR=2.06 | N=26,008
  - Panel E (CONSENSUS_EARNINGS_FORECAST): mean=0.01 | SD=4.46 | median=0.04 | IQR=1.79 | N=6,929
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.07/3.51/0.09/2.05/42,031; B 0.01/3.40/0.01/1.83/8,963; C 0.07/2.33/0.04/2.40/10,720; D 0.04/3.46/0.04/2.06/26,008; E 0.01/4.46/0.04/1.79/6,929. Table C.7 reports coefficients.

**Uncertainty / caveat**: Standardized variable can be negative; signs stripped in source — several means/medians likely negative. Verify against anchor.

---

### VAR_43 — STOCK_RETURNS (lagged stock returns)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3198
- **section_or_table**: Table 1 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> STOCK_RETURNS are defined as the quarterly buy-and-hold return.

**Formula / data source**:
> Quarterly buy-and-hold equity return (entered lagged as a firm control). CRSP.

**Unit / transformation**: return (ratio); winsorized at 1%

**Table 1 stats (cross-checked against PyMuPDF anchor)**:
  - (No anchor match for normalized name `STOCKRETURNSLAGGEDSTOCKRETURNS`)
  - other_stats (from inventory): Per-panel [Mean/SD/Median/IQR/N]: A 0.03/0.24/0.02/0.25/67,226; B 0.02/0.27/0.00/0.30/11,088; C 0.04/0.18/0.03/0.20/12,063; D 0.02/0.25/0.01/0.27/29,983; E 0.03/0.24/0.02/0.24/8,523. Table C.7 reports STOCK_RETURNS coefficients (some negative).

**Uncertainty / caveat**: Returns can be negative; signs stripped in source. Verify against anchor.

---

### VAR_44 — lagged U.S. dollar/British pound FX rate

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3197
- **section_or_table**: §IV.C.3 (Empirical Model, control list)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia.

**Formula / data source**:
> Lagged USD/GBP exchange-rate level. Bloomberg currency data; macro series cross-checked via FRED.

**Unit / transformation**: exchange-rate level (lagged), time-level

**Other reported stats**: Macro control; used only in linear-model specifications (industry×time FE absorb macro factors otherwise).

**Uncertainty / caveat**: Distinct from the vol(FX$£) input to eq (13) (VAR_76) and from the FX-exposure controls in Table 9 (VAR_49–52).

---

### VAR_45 — lagged VIX implied volatility index

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3197
- **section_or_table**: §IV.C.3 (control list)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Macro controls include the lagged U.S. dollar/British pound FX rate, the lagged VIX implied volatility index, the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey, the lagged Consumer Sentiment Index from the University of Michigan, and the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia.

**Formula / data source**:
> Lagged VIX index level. CBOE VIX (via FRED/Bloomberg).

**Unit / transformation**: index level (lagged), time-level

**Other reported stats**: Macro control.

---

### VAR_46 — lagged mean GDP growth 1-year-ahead forecast (Livingstone Survey)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3197
- **section_or_table**: §IV.C.3 (control list)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> the lagged mean GDP growth 1-year-ahead forecast from the Federal Reserve Bank of Philadelphia's Livingstone Survey

**Formula / data source**:
> Lagged mean 1-year-ahead GDP growth forecast, Federal Reserve Bank of Philadelphia Livingstone Survey.

**Unit / transformation**: forecast growth rate (lagged), time-level

**Other reported stats**: Macro control.

**Uncertainty / caveat**: Printed 'Livingstone Survey'; the Philadelphia Fed series is commonly spelled 'Livingston Survey' — transcribed as printed.

---

### VAR_47 — lagged Consumer Sentiment Index (University of Michigan)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3197
- **section_or_table**: §IV.C.3 (control list)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> the lagged Consumer Sentiment Index from the University of Michigan

**Formula / data source**:
> Lagged University of Michigan Consumer Sentiment Index level.

**Unit / transformation**: index level (lagged), time-level

**Other reported stats**: Macro control.

---

### VAR_48 — lagged Leading Economic Indicator (Federal Reserve Bank of Philadelphia)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3197
- **section_or_table**: §IV.C.3 (control list)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> the lagged Leading Economic Indicator from the Federal Reserve Bank of Philadelphia

**Formula / data source**:
> Lagged Leading Economic Indicator, Federal Reserve Bank of Philadelphia.

**Unit / transformation**: index level (lagged), time-level

**Other reported stats**: Macro control.

---

### VAR_49 — βFX£_i,t (β_i,t^FX£)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3209
- **section_or_table**: §VI.A text + Table 9 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We include as an additional control each firm's end-of-quarter coefficient on FX£, namely β^FX£_i,t, which captures the time-varying sensitivity of firm i's equity returns to changes in the British pound.

**Formula / data source**:
> Firm-by-firm rolling regression of equity-return levels on U.S. and U.K. equity index returns and USD–GBP FX-rate changes; 24-month rolling windows over 2010:M1–2016:M12 (footnote 27). β^FX£_i,t is the end-of-quarter GBP-sensitivity coefficient.

**Unit / transformation**: regression coefficient (time-varying), firm-quarter

**Other reported stats**: Used as control in Table 9 cols 1–2 (INVESTMENT DID coefficients −0.172*** / −0.080***).

---

### VAR_50 — Alfaro et al. (2018) GBP Instruments (first- and second-moment)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3209
- **section_or_table**: §VI.A text + Table 9 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Second, we include in our estimations the Alfaro et al. (2018) firm-level instruments for first- and second-moment shocks to the USD–GBP rate.

**Formula / data source**:
> Alfaro, Bloom, and Lin (2018) firm-level instruments for first- and second-moment shocks to the USD–GBP rate (Finance Uncertainty Multiplier instruments).

**Unit / transformation**: firm-level instrument controls

**Other reported stats**: Table 9 cols 3–4 (INVESTMENT DID −0.145*** / −0.097***).

**Uncertainty / caveat**: Related to but distinct from the first-moment-only instrument set used in Table C.7 (VAR_57).

---

### VAR_51 — FX hedging dummy (prior-year)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3209
- **section_or_table**: §VI.A text + Table 9 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We include as additional controls a dummy variable for whether a firm engaged in FX hedging activity in the prior year, and the intensity of hedging in the prior year as measured by the number of keywords mentioned.

**Formula / data source**:
> Dummy = 1 if firm engaged in FX hedging in prior year. Keyword search of 10-K disclosures following Campello, Lin, Ma, and Zou (2011).

**Unit / transformation**: binary {0,1}, firm-year (lagged)

**Other reported stats**: Table 9 'FX Hedging' columns (cols 5–6).

---

### VAR_52 — FX hedging intensity (number of keywords)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3209
- **section_or_table**: §VI.A text + Table 9 notes
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> the intensity of hedging in the prior year as measured by the number of keywords mentioned.

**Formula / data source**:
> Count of FX-hedging-related keywords (from Campello, Lin, Ma, and Zou (2011) list) mentioned in prior-year 10-K.

**Unit / transformation**: count (lagged), firm-year

**Other reported stats**: Table 9 'FX Hedging' columns.

---

### VAR_53 — existing bond yields (yields to maturity on existing bonds)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3211
- **section_or_table**: §VI.B text + Table 10 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we reestimate the analysis of Table 2 controlling for yields on existing bonds (obtained from TRACE)

**Formula / data source**:
> Yields to maturity on firms' existing traded bonds. TRACE.

**Unit / transformation**: yield (%, lagged), firm-quarter

**Other reported stats**: Table 10 'Existing Bond Yields' (cols 1–2); INVESTMENT DID −0.168*** / −0.072***.

---

### VAR_54 — new bond yields (yields on new bond issues)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3211
- **section_or_table**: §VI.B text + Table 10 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> yields on new bond issues (from SDC)

**Formula / data source**:
> Yields to maturity on new bond issues. SDC.

**Unit / transformation**: yield (%), firm-quarter

**Other reported stats**: Table 10 'New Bond Yields' (cols 3–4).

---

### VAR_55 — new syndicated loan spreads / markups (all-in spread)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3211
- **section_or_table**: §VI.B text + Table 10 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> markups on new syndicated loans (from DealScan)

**Formula / data source**:
> All-in spreads/markups on new syndicated loans. WRDS–Reuters DealScan.

**Unit / transformation**: spread (bps), firm-quarter

**Other reported stats**: Table 10 'New Syndicated Loan Spreads' (cols 5–6).

**Uncertainty / caveat**: Table 10 note phrasing partially garbled ('all-d...'); confirm exact term against anchor.

---

### VAR_56 — discount rate news component of returns (equity discount rate news)

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3211
- **section_or_table**: §VI.B text + Table 10 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> for the discount rate news component of returns (from the decomposition of returns news into cash flow news and discount rate news components as in Vuolteenaho (2002)).

**Formula / data source**:
> Discount-rate-news residual from Campbell–Shiller (1988) / Vuolteenaho (2002) decomposition of firm equity returns. CRSP.

**Unit / transformation**: news component (return units), firm-quarter

**Other reported stats**: Table 10 final pair of columns.

---

### VAR_57 — first-moment instruments for USD–GBP exchange rate, price of oil, and Treasury rate (Alfaro et al. (2018))

- **status**: `LOCKED`
- **role**: Control
- **raw_or_derived**: derived
- **page**: 3200
- **section_or_table**: Footnote 23 (main); IA Table C.7 notes
- **paragraph_position**: N/A (footnote)

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> we include the firm-level first-moment instruments for the USD–GBP exchange rate, the price of oil, and the Treasury rate from alfaro2018. These variables jointly serve as proxies for changes in firms' expected profitability coinciding with the Brexit vote.

**Formula / data source**:
> Alfaro, Bloom, and Lin (2018) firm-level first-moment instruments for (i) USD–GBP exchange rate, (ii) price of oil, (iii) Treasury rate. Used in IA Table C.7 first-moment-controls robustness.

**Unit / transformation**: firm-level instrument controls

**Other reported stats**: IA Table C.7 reports the augmented INVESTMENT/EMPLOYMENT_GROWTH DID coefficients with these instruments and lists control coefficients (SIZE, TOBIN_Q, CASH_FLOW, SALES_GROWTH, CONSENSUS_EARNINGS_FORECAST, STOCK_RETURNS).

**Uncertainty / caveat**: Citation rendered 'alfaro2018' (unresolved BibTeX key) in main-paper footnote 23; resolves to Alfaro, Bloom, and Lin (2018). Distinct from the GBP first-AND-second-moment set in Table 9 (VAR_50).

---

### VAR_58 — AUTOMATION{i∈CZ} (AUTOMATION_{i∈CZ})

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3211
- **section_or_table**: §VI.C text + Table 11 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We define our first, geography-based variable capturing firms' exposure to automation technologies, AUTOMATION{i∈CZ}, by matching each firm i in our sample to a CZ (based on the firm's headquarters location).

**Formula / data source**:
> Acemoglu and Restrepo (2020) commuting-zone-level exposure to robots (robot-integrator data from Leigh and Kraft (2018)), assigned to firm i by HQ commuting zone. Table 11 notes: 'AUTOMATION{i∈CZ} is the Acemoglu and Restrepo (2020) commuting-zone-level exposure to robots for all firms i headquartered in commuting [zone].'

**Unit / transformation**: CZ-level exposure measure, firm-level (by HQ)

**Other reported stats**: Used as control in Table 11; coefficients e.g. 0.029 (INVESTMENT col 1, n.s.), 0.261*** (R&D).

**Uncertainty / caveat**: Construction detailed in IA Appendix E.1 ¶1, which refers reader to Acemoglu and Restrepo (2020) and Leigh and Kraft (2018).

---

### VAR_59 — AUTOMATIONi (AUTOMATION_i, text-based)

- **status**: `LOCKED`
- **role**: Robustness
- **raw_or_derived**: derived
- **page**: 3211
- **section_or_table**: §VI.C text (full construction in IA Appendix E.1 ¶2)
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We define AUTOMATIONi as a continuous variable that measures how frequently the top 100 automation keywords appear in each firm's business description (10-K Section 1) and management discussion (10-K Section 7). To capture cases in which a firm discusses automation efforts in only 1 year, we average the word count across the pre-Brexit years in our sample (2010–2015).

**Formula / data source**:
> AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi); top-100 automation keywords from TextRank (Mihalcea and Tarau (2004)) on Benhabib (2003) textbook; counted in 10-K Sections 1 and 7; averaged over 2010–2015 (IA Appendix E.1 ¶2).

**Unit / transformation**: continuous, log scale; firm-level (time-averaged 2010–2015)

**Other reported stats**: Distribution shown as histogram in Figure E.1 (IA p. 16); no numeric moments printed. Used as control in Table 11 (coefficients e.g. INVESTMENT 0.052 n.s.).

**Uncertainty / caveat**: Averaging window stated as '2010–2015' in main §VI.C and Figure E.1 caption, but 'all years in our sample' in IA E.1 ¶2 — confirm exact window.

---

### VAR_60 — AUTOMATION_KEYWORDSi

- **status**: `LOCKED`
- **role**: Other: intermediate input to AUTOMATIONi
- **raw_or_derived**: derived
- **page**: IA p. 16
- **section_or_table**: IA Appendix E.1 ¶2
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> AUTOMATIONi = log(1 + AUTOMATION_KEYWORDSi), where AUTOMATION_KEYWORDSi is the number of mentions of the top 100 automation-related keywords in firm i's 10-K forms.

**Formula / data source**:
> Count of mentions of the top-100 automation keywords (Table E.1) in firm i's 10-K Sections 1 and 7.

**Unit / transformation**: count, firm (per-year then averaged)

**Other reported stats**: Keyword list = Table E.1 (IA p. 17); per audit rule, the 100 keywords are parameters, not separate variables.

---

### VAR_61 — capital expenditures

- **status**: `LOCKED`
- **role**: Other: raw input to derived DVs/controls
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within INVESTMENT definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> INVESTMENT is defined as capital expenditures divided by lagged total assets.

**Formula / data source**:
> Capital expenditures, COMPUSTAT Quarterly Fundamentals (item named in prose, not by code in the paper).

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

**Uncertainty / caveat**: Paper names raw items in prose; no COMPUSTAT item codes given.

---

### VAR_62 — lagged total assets / total assets

- **status**: `LOCKED`
- **role**: Other: raw input (scaling denominator) / Sample-filter
- **raw_or_derived**: raw
- **page**: 3192
- **section_or_table**: §IV.B + Table 1 notes
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We use COMPUSTAT Quarterly to gather basic information on firm investment and financial data. … we drop … companies whose market value or book assets are lower than $10 million.

**Formula / data source**:
> Total assets, COMPUSTAT. Used (lagged) as the denominator for INVESTMENT, R&D, DIVESTITURES, CASH, NWC, CASH_FLOW, and (logged) for SIZE; also a sample filter (<$10M dropped).

**Unit / transformation**: USD, firm-quarter (lagged for scaling; logged for SIZE)

**Other reported stats**: See SIZE (VAR_40) for the logged distribution. Footnote 22: average assets of top-tercile β^UK firms = $2.81 billion in 2016:Q2.

**Uncertainty / caveat**: Serves multiple roles (scaling, SIZE, sample filter).

---

### VAR_63 — number of employees

- **status**: `LOCKED`
- **role**: Other: raw input to EMPLOYMENT_GROWTH
- **raw_or_derived**: raw
- **page**: 3192
- **section_or_table**: §IV.B
- **paragraph_position**: 2

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Firm-level employment data are taken from COMPUSTAT's Annual Fundamentals. We measure employment growth based on the change in the number of employees of the firm.

**Formula / data source**:
> Number of employees, COMPUSTAT Annual Fundamentals (firm level); YTS for U.S. establishment-level employment.

**Unit / transformation**: count, firm-year

**Other reported stats**: Employment sample = 11,345 firm-years (p. 3192).

---

### VAR_64 — R&D expenditures

- **status**: `LOCKED`
- **role**: Other: raw input to R&D ratio
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within R&D definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> R&D is defined as R&D expenditures divided by lagged total assets, considering only firms with non-missing R&D expenditures.

**Formula / data source**:
> R&D expenditures, COMPUSTAT.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_65 — sale of plant, property, and equipment (SPP&E)

- **status**: `LOCKED`
- **role**: Other: raw input to DIVESTITURES
- **raw_or_derived**: raw
- **page**: 3202
- **section_or_table**: Table 3 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> DIVESTITURES are defined as the value of SPP&E (Sale of Plant, Property, and Equipment) divided by lagged total assets.

**Formula / data source**:
> Value of sale of plant, property, and equipment, COMPUSTAT.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_66 — cash and short-term investments

- **status**: `LOCKED`
- **role**: Other: raw input to CASH
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within CASH definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> CASH is defined as cash and short-term investments divided by lagged total assets.

**Formula / data source**:
> Cash and short-term investments, COMPUSTAT. (Table 8 uses 'total cash holdings' with a net-of-cash denominator — see VAR_05 conflict.)

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_67 — working capital (net of cash)

- **status**: `LOCKED`
- **role**: Other: raw input to NWC
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within NWC definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> NON_CASH_WORKING_CAPITAL is defined as working capital (net of cash) divided by lagged total assets.

**Formula / data source**:
> Working capital net of cash, COMPUSTAT.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_68 — operating income before depreciation

- **status**: `LOCKED`
- **role**: Other: raw input to CASH_FLOW and PROFITS
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within CASH_FLOW definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> CASH_FLOW is defined as operating income before depreciation divided by lagged total assets.

**Formula / data source**:
> Operating income before depreciation, COMPUSTAT. Also numerator of PROFITS (over sales).

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_69 — sales

- **status**: `LOCKED`
- **role**: Other: raw input to SALES_GROWTH and PROFITS
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within SALES_GROWTH definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> SALES_GROWTH is defined as the year-on-year percentage change in quarterly sales.

**Formula / data source**:
> Quarterly sales, COMPUSTAT. Denominator of PROFITS; basis of SALES_GROWTH.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

---

### VAR_70 — market value of equity

- **status**: `INVENTORY_NOTE (TOBIN_Q decomposition)`
- **role**: Other: raw input to TOBIN_Q (and SIZE / sample filter via market value)
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within TOBIN_Q definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> TOBIN_Q … is calculated as the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.

**Formula / data source**:
> Market value of equity, CRSP/COMPUSTAT. Also used in $10M market-value sample filter (§IV.B).

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

- **FLAG**: `INVENTORY_NOTE: TOBIN_Q component`
  - Component of TOBIN_Q; not a paper-listed standalone variable (Claude-web over-enumerated; safe to ignore as a separate var in code).

---

### VAR_71 — book value of assets

- **status**: `LOCKED`
- **role**: Other: raw input to TOBIN_Q
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within TOBIN_Q definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> TOBIN_Q is defined as the market value of assets divided by the book value of assets …

**Formula / data source**:
> Book value of assets, COMPUSTAT. Denominator of TOBIN_Q.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

**Uncertainty / caveat**: Likely the same item as 'total assets' (VAR_62); the paper names it 'book value of assets' only inside the TOBIN_Q formula — listed separately per rule 5.

---

### VAR_72 — book value of equity

- **status**: `INVENTORY_NOTE (TOBIN_Q decomposition)`
- **role**: Other: raw input to TOBIN_Q
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within TOBIN_Q definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> … the market value of equity plus the book value of assets minus book value of equity plus deferred taxes, all divided by book value of assets.

**Formula / data source**:
> Book value of equity, COMPUSTAT.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

- **FLAG**: `INVENTORY_NOTE: TOBIN_Q component`
  - Component of TOBIN_Q; not a paper-listed standalone variable (Claude-web over-enumerated; safe to ignore as a separate var in code).

---

### VAR_73 — deferred taxes

- **status**: `INVENTORY_NOTE (TOBIN_Q decomposition)`
- **role**: Other: raw input to TOBIN_Q
- **raw_or_derived**: raw
- **page**: 3198
- **section_or_table**: Table 1 notes (within TOBIN_Q definition)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> … minus book value of equity plus deferred taxes, all divided by book value of assets.

**Formula / data source**:
> Deferred taxes, COMPUSTAT.

**Unit / transformation**: USD, firm-quarter

**Other reported stats**: N/A

- **FLAG**: `INVENTORY_NOTE: TOBIN_Q component`
  - Component of TOBIN_Q; not a paper-listed standalone variable (Claude-web over-enumerated; safe to ignore as a separate var in code).

---

### VAR_74 — FTSE100 Index / vol(FTSE100_t)

- **status**: `LOCKED`
- **role**: Other: raw input to β_i^UK (eq 13)
- **raw_or_derived**: raw
- **page**: 3191
- **section_or_table**: §IV.A.1 (equation (13) discussion)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> It also uses the volatility of the FTSE100 Index as a proxy for uncertainty in the U.K. (the relevant source of aggregate uncertainty in our setting).

**Formula / data source**:
> FTSE100 Index returns and their volatility, vol(FTSE100_t). Bloomberg equity index data. RHS regressor in eq (13).

**Unit / transformation**: index returns / return volatility, monthly (2010:M1–2014:M12)

**Other reported stats**: Implied-volatility term structure plotted in Figure 3 (p. 3194).

---

### VAR_75 — S&P 500 Index / vol(SP500)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3191
- **section_or_table**: §IV.A.1 (equation (13) controls)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) to absorb effects arising through firms' exposure to the domestic U.S. market and exchange rate fluctuations between the U.S. dollar and the British pound.

**Formula / data source**:
> S&P 500 Index return volatility, vol(SP500). Bloomberg/CRSP. Control in eq (13).

**Unit / transformation**: return volatility, monthly

**Other reported stats**: N/A

---

### VAR_76 — USD/British pound FX rate / vol(FX$£)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Control
- **raw_or_derived**: raw
- **page**: 3191
- **section_or_table**: §IV.A.1 (equation (13) controls)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> We include control variables, CONTROLS_t, consisting of vol(SP500) and vol(FX$£) into equation (13) …

**Formula / data source**:
> USD/GBP FX-rate changes and their volatility, vol(FX$£). Bloomberg currency data. Control in eq (13); FX-rate changes also used in the §VI.A dynamic levels regression.

**Unit / transformation**: FX-rate change / volatility, monthly

**Other reported stats**: N/A

**Uncertainty / caveat**: Distinct use from the lagged USD/GBP level macro control (VAR_44).

---

### VAR_77 — equity returns / vol(r_it)

- **status**: `LOCKED`
- **role**: Other: raw input (LHS of eq 13)
- **raw_or_derived**: raw
- **page**: 3191
- **section_or_table**: §IV.A.1 (equation (13))
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Equation (13) uses the volatility of equity returns, vol(r_it), as a proxy for firm income volatility, vol(v_it).

**Formula / data source**:
> Firm equity returns and their volatility, vol(r_it). CRSP. LHS of eq (13).

**Unit / transformation**: return / return volatility, monthly (firm-level)

**Other reported stats**: Quarterly buy-and-hold version reported as STOCK_RETURNS (VAR_43).

**Uncertainty / caveat**: Related to but distinct from STOCK_RETURNS (quarterly buy-and-hold control, VAR_43).

---

### VAR_78 — I/B/E/S 1-year-ahead EPS forecasts (mean and standard deviation)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Other: raw input to forecast-uncertainty figures + CONSENSUS_EARNINGS_FORECAST
- **raw_or_derived**: raw
- **page**: 3195
- **section_or_table**: §IV.C.2 text
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Beginning in 2015:Q1, we obtain the 1-year-ahead earnings per share (EPS) forecasts for each firm in our sample and compute the mean and standard deviation of forecasts.

**Formula / data source**:
> Analyst 1-year-ahead EPS forecasts (mean, SD, dispersion). I/B/E/S. Underlies Figure 4 forecast bands and CONSENSUS_EARNINGS_FORECAST (1-quarter-ahead, VAR_42).

**Unit / transformation**: EPS (USD), firm-quarter

**Other reported stats**: Figure 4 plots 1.5-SD bands around group-mean forecasts for high/low β^UK groups.

**Uncertainty / caveat**: Figure 4 uses 1-year-ahead forecasts; the regression control (VAR_42) is the standardized 1-quarter-ahead consensus — two different horizons.

---

### VAR_79 — YTS establishment-level employment / establishment counts

- **status**: `LOCKED`
- **role**: Other: raw input to establishment-level DVs
- **raw_or_derived**: raw
- **page**: 3193
- **section_or_table**: §IV.B text
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> The YTS database is compiled from historical business files from Infogroup and are linked longitudinally to track establishment location, employment, and sales information at the establishment-year level for public and private firms in the United States.

**Formula / data source**:
> Your-Economy Time-Series (YTS) database (Business Dynamics Research Consortium, U. Wisconsin); establishment-year location, employment, sales. Matched to sample firms via tickers + manual name searches.

**Unit / transformation**: establishment-year (employment counts, establishment counts)

**Other reported stats**: Sample coverage: 757,083 unique establishments; 1,809,301 establishment-year observations (2010–2016); 51,750 U.S.-based subsidiaries; final U.S. establishment-level employment-growth sample 11,345 firm-years (pp. 3193, 3201).

---

### VAR_80 — establishment openings and closings

- **status**: `LOCKED`
- **role**: Other: raw input to ESTABLISHMENT_TURNOVER
- **raw_or_derived**: raw
- **page**: 3203
- **section_or_table**: Footnote 24
- **paragraph_position**: N/A (footnote)

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Establishment turnover is defined as the sum of establishment openings and closings, divided by the lagged number of total establishments.

**Formula / data source**:
> Counts of U.S. establishment openings and closings per firm-year. YTS database.

**Unit / transformation**: counts, firm-year

**Other reported stats**: N/A

---

### VAR_81 — Hoberg and Moon (2017) Input and Output offshoring indices (raw counts)

- **status**: `LOCKED`
- **role**: Other: raw input to U.K. offshoring treatment dummies
- **raw_or_derived**: raw
- **page**: 3205
- **section_or_table**: §V.B.2 text
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> This index, derived from firms' 10-K filings, counts mentions of words related to the purchase of inputs (\"Input\") and sale of outputs (\"Output\") from each country a firm does business with within a year.

**Formula / data source**:
> Hoberg and Moon (2017) Input and Output offshoring word-count indices, by country, per firm-year. Underlies VAR_25/26/27.

**Unit / transformation**: word-count index, firm-year (summed 2010–2014 for U.K.)

**Other reported stats**: N/A

---

### VAR_82 — FIRM_i (firm-fixed effects)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Fixed effect
- **raw_or_derived**: derived
- **page**: 3197
- **section_or_table**: §IV.C.3 (equation (14) discussion)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> FIRM_i represents firm-fixed effects, INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100), and QUARTER_t are calendar-quarter dummies.

**Formula / data source**:
> Firm dummies Σ_i FIRM_i in eq (14).

**Unit / transformation**: fixed-effect dummies, firm-level

**Other reported stats**: Marked 'Yes' in all baseline tables' Fixed effects rows.

---

### VAR_83 — INDUSTRY_j (Hoberg and Phillips (2016) FIC 100)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Fixed effect
- **raw_or_derived**: derived
- **page**: 3197
- **section_or_table**: §IV.C.3 (equation (14) discussion)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> INDUSTRY_j is a dummy for each industry category j of the Hoberg and Phillips (2016) classification (FIC 100)

**Formula / data source**:
> Hoberg and Phillips (2016) FIC 100 industry dummies (text-based network industries).

**Unit / transformation**: fixed-effect dummies, industry-level (FIC 100)

**Other reported stats**: Enters mainly via INDUSTRY×QUARTER interaction (VAR_85).

---

### VAR_84 — QUARTER_t (calendar-quarter dummies)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Fixed effect
- **raw_or_derived**: derived
- **page**: 3197
- **section_or_table**: §IV.C.3 (equation (14) discussion)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> QUARTER_t are calendar-quarter dummies.

**Formula / data source**:
> Calendar-quarter dummies.

**Unit / transformation**: fixed-effect dummies, time-level

**Other reported stats**: N/A

---

### VAR_85 — INDUSTRY_j × QUARTER_t (Industry × time fixed effects)

- **status**: `LOCKED (verifier-probe false-positive resolved)`
- **role**: Fixed effect
- **raw_or_derived**: derived
- **page**: 3196
- **section_or_table**: equation (14)
- **paragraph_position**: 1

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> Y_{i,t} = α + δ[POST_t × HIGH_UK_EXPOSURE_i] + θCONTROLS_{i,t−1} + Σ_i FIRM_i + Σ_j Σ_t [INDUSTRY_j × QUARTER_t] + ϵ_{i,t}.

**Formula / data source**:
> Time-varying industry fixed effects = interaction of FIC-100 industry dummies with calendar-quarter dummies. Printed in tables as 'Industry × time'.

**Unit / transformation**: interacted fixed-effect dummies, industry-quarter

**Other reported stats**: Marked 'Yes' in baseline (tercile / 10-K) specs; 'No' in macro-control linear specs (which use Firm FE only).

---

### VAR_86 — TIME (time fixed effects)

- **status**: `INVENTORY_NOTE (table-only label)`
- **role**: Fixed effect
- **raw_or_derived**: derived
- **page**: 3207
- **section_or_table**: Table 7 Fixed-effects rows + Table 5 notes
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> NOT DEFINED IN TEXT — appears in Table 5 and Table 7 'Fixed effects' rows as separate 'Industry' and 'Time' entries (used in employment-growth specifications in place of Firm + Industry×time).

**Formula / data source**:
> Time (calendar period) fixed effects, used together with standalone Industry FE in the employment-growth / labor-unionization specifications (e.g., Table 7 cols 4–6; Table 5 cols 5–8).

**Unit / transformation**: fixed-effect dummies, time-level

**Other reported stats**: Some employment specs replace Firm FE + Industry×time with Industry FE + Time FE (Table 7 rows).

**Uncertainty / caveat**: Distinct FE structure for annual employment specs vs quarterly investment specs; confirm exact FE set per column against anchor.

- **FLAG**: `INVENTORY_NOTE: table-only label`
  - Table-only label (appears in Tables 5/7 fixed-effects rows). No body-text definition; treat as 'calendar-quarter dummies' analog of QUARTER_t.

---

### VAR_87 — firm (standard-error cluster group)

- **status**: `LOCKED`
- **role**: Standard error cluster group
- **raw_or_derived**: derived
- **page**: 3200
- **section_or_table**: Table 2 notes (recurring in all regression tables)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels.

**Formula / data source**:
> First clustering dimension (firm) for double-clustered robust standard errors.

**Unit / transformation**: clustering dimension

**Other reported stats**: N/A

---

### VAR_88 — calendar quarter (standard-error cluster group)

- **status**: `LOCKED`
- **role**: Standard error cluster group
- **raw_or_derived**: derived
- **page**: 3200
- **section_or_table**: Table 2 notes (recurring in all regression tables)
- **paragraph_position**: N/A for table-only

**Definition (verbatim from Claude-web cold read, verified present in PyMuPDF anchor)**:
> T-statistics are computed using robust standard errors (in parentheses) double-clustered at the firm and calendar quarter levels.

**Formula / data source**:
> Second clustering dimension (calendar quarter) for double-clustered robust standard errors.

**Unit / transformation**: clustering dimension

**Other reported stats**: N/A

---

## Final tally

- **LOCKED**: 84 / 88
- **INVENTORY_NOTE** (not paper drift): 4 / 88
- **Paper drift**: 0 / 88

**Next phase**: moment-fingerprint test of `scripts/campello_rebuild/` output vs Table 1 anchor (Panel A means / SDs / medians / N), then code audit against locked method (`tmp/campello_method_lockin.md`).