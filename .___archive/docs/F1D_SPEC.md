Below is a **deterministic, minimal, step‑by‑step build spec** for the *Clarity (F1D)* measure using only (i) earnings‑call transcripts, (ii) the Loughran–McDonald (LM) dictionary, and (iii) the unified info file that links transcript file names to firm metadata. It implements your two hard rules:

* **R1. QA‑only**: keep **only** Q&A context. (We rely on the `context` field in the transcript speaker data, which is “qa” or “pres”.)  
* **R2. Metric definition**: **F1D = (# tokens found in Uncertainty ∪ Weak_Modal) / (# total word tokens)** computed **only over managerial speech** within Q&A. (No “per‑k words” scaling; it is a pure proportion.) This is the dictionary version of the F1 Clarity factor described in your proposal; we ignore the LLM variant per your instruction. 

Heavy compute (tokenization + dictionary lookup) is in **C++**. Light ETL/glue (file checks, exact‑row dedup, joins, yearly sharding, and reporting) is in **Python**. **No script accepts flags**; each one runs end‑to‑end with hardcoded assumptions.

---

## 0) Inputs (read‑only) and their key fields

1. **Transcripts (speaker data, 2002–2018)** — Apache Parquet, one file per year, columns:
   `file_name, speaker_name, employer, role, speaker_number, speaker_text, context, section, last_update`
   The `context` flag is used to select **Q&A only**; we will further subselect managerial speech.  

2. **LM Master Dictionary (1993–2024)** — CSV, columns include:
   `Word` (UPPERCASE), `Uncertainty`, `Weak_Modal`, … (others ignored for F1D). We select tokens where `Uncertainty>0` **or** `Weak_Modal>0`. Examples include **MAY**, **COULD**, **APPROXIMATELY**, **BELIEVE** (as seen in profiling). 

3. **Unified Info** — Parquet, one row per transcript *occurrence*, mapping `file_name` → firm/event info, incl. `company_name`, `start_date`, `business_quarter`, identifiers (`company_ticker`, `permno`), and data‑quality fields. This table **does contain duplicate `file_name` values** (often with differing metadata). 

> **Important constraint for Unified Info**: **do not deduplicate** its rows unless they are **bit‑for‑bit identical**. For same‑`file_name` rows that are **not identical**, **do not drop** them; instead, **write a review CSV** listing all such collisions (details below). 

---

## 1) Outputs (authoritative datasets) & schemas

All “large” outputs are **year‑sharded** (one file per calendar year extracted from `start_date` or, if missing, the speaker data’s source year). Single logical tables are named here; their physical materialization is `…_YYYY.parquet` or `…_YYYY.parquet`.

### O1. `lm_Clarity_dictionary.parquet`  (Python; small)

* **Purpose**: compact dictionary for C++ lookup.
* **Schema** :

  * `token` (STRING, uppercase A–Z only) — LM word normalized to `[A–Z]+`
  * `source_flag` (STRING) — `"UNCERTAINTY"`, `"WEAK_MODAL"`, or `"BOTH"`

### O2. `qa_manager_docs_YYYY.parquet`  (Python; large, sharded)

* **Purpose**: one concatenated “document” per **call** (one row per unique `file_name`) containing **managerial Q&A** text only, to be tokenized in C++.
* **Schema** (parquet):

  * `file_name` (STRING) — transcript id from speaker data
  * `doc_text` (STRING) — concatenated managerial Q&A text for that call
  * `approx_char_len` (INT) — length of `doc_text` (diagnostic)
  * `year` (INT) — call year from Unified Info `start_date` (fall back to `source_file_year`)

> Note: We do **not** drop or alter Unified Info duplicates; this table is **keyed by `file_name`** from speaker data only.

### O3. `f1d_call_YYYY.parquet`  (C++; large, sharded)

* **Purpose**: call‑level counts produced by C++ tokenizer+matcher.
* **Schema**:

  * `file_name` (STRING)
  * `total_word_tokens` (INT) — tokens matching regex `[A–Z]+` after normalization
  * `Clarity_hits` (INT) — token count in **Uncertainty ∪ Weak_Modal**
  * `f1d_pct` (FLOAT) — `Clarity_hits / total_word_tokens`
  * `top5_matches` (ARRAY<STRING>) — top 5 matched tokens by frequency (diagnostic)
  * `process_version` (STRING) — static version string for determinism (e.g., `"F1D.1.0"`)

### O4. `f1d_panel_YYYY.parquet`  (Python; final, sharded)

* **Purpose**: **firm–quarter** panel (ALL firms), aggregated from calls.
* **Aggregation**: within a firm–quarter, **sum** `Clarity_hits` and **sum** `total_word_tokens`; set `f1d_pct = sum(Clarity_hits)/sum(total_word_tokens)`.
* **Schema**:

  * `permno` (STRING or INT) — as in Unified Info (may be missing for some)
  * `company_name` (STRING)
  * `company_id`
  * `cusip`
  * `sedol`
  * `isin`
  * `company_ticker`
  * `business_quarter` (STRING, e.g., `"2014Q3"`)
  * `num_calls` (INT) — count of distinct `file_name` contributing in one business quarter
  * `sum_total_word_tokens` (INT)
  * `sum_Clarity_hits` (INT)
  * `f1d_pct` (FLOAT)
  * `any_mapping_issues` (BOOL) — TRUE if `file_name` had multiple Unified Info rows

### O5. **Review & QA reports** (CSV/MD per step; small)

* `unified_info_duplicate_file_names.csv` — all `file_name` with **>1 non‑identical** rows, with diff hints
* `report_step_00.md`, `report_step_01.md`, … `report_step_04.md` — human‑readable step summaries (metrics listed below)

---

## 2) Processing steps (each = one script/binary; **no flags**)

> **Naming** below is illustrative; you may adopt simple sequential names. Each step writes its own `report_step_XX.md`. The only required precondition is that the three input assets exist in the working directory: **unified info**, **speaker_data_YYYY.parquet (for all years)**, **LM dictionary CSV**.

### **STEP 00 (Python, light): Unified Info sanity check & exact‑row dedup**

**Script:** `00_unified_info_check.py` (run: `python 00_unified_info_check.py`)

* **Inputs**: `Unified-info.parquet`.
* **Process**:

  1. **Exact‑row dedup only**: drop rows that are **bit‑for‑bit identical across all columns**; keep one.
  2. **Collision scan**: for any `file_name` with **>1** remaining rows (i.e., not identical), **do not dedup**; instead record **all rows** to `unified_info_duplicate_file_names.csv` along with a machine diff summary (which columns differ).
  3. **Emit mapping view** used downstream (not persisted): in‑memory map `file_name → [candidate rows]`.
* **Outputs**:

  * `unified_info_duplicate_file_names.csv` (review list; non‑identical only).
  * `report_step_00.md` with: total rows, exact duplicates removed, count of non‑identical collisions, top varying columns among collisions, coverage by year.
* **Notes**: We are **not** changing the non‑identical duplicates; we’re just surfacing them. 

---

### **STEP 01 (Python, light): Build the “Clarity” dictionary file**

**Script:** `01_build_lm_Clarity_dictionary.py`

* **Inputs**: `Loughran-McDonald_MasterDictionary_1993-2024.csv`
* **Process**:

  1. Normalize `Word` to uppercase and keep tokens that match regex `[A-Z]+`.
  2. Select rows where `Uncertainty>0 OR Weak_Modal>0`.
  3. Write `lm_Clarity_dictionary.parquet` with columns (`token`, `source_flag`).
* **Outputs**:

  * `lm_Clarity_dictionary.parquet` (small).
  * `report_step_01.md` with counts: total LM rows, selected Uncertainty count (~297), selected Weak_Modal count (~27), union size, examples (e.g., **MAY, COULD, APPROXIMATELY, BELIEVE**), and any dropped non‑alpha tokens. 

---

### **STEP 02 (Python, light): Extract QA‑only managerial documents**

**Script:** `02_make_qa_manager_docs.py`

* **Inputs**: all `speaker_data_YYYY.parquet` (2002–2018) + `Unified-info.parquet` (read‑only map from STEP 00).
* **Goal**: per `file_name`, concatenate **only** **managerial** speech from **Q&A** (`context == 'qa'`) into a single `doc_text`.
* **Managerial filter (minimal, deterministic)**:

  * **Include** a turn if **any** is true:

    * `employer == company_name` (after trimming and case‑folding), where `company_name` comes from Unified Info joined on `file_name`. 
    * `role` contains one of the exact case‑insensitive substrings:
    
      PRESIDENT
      VP
      DIRECTOR
      CEO
      EVP
      SVP
      CFO
      OFFICER
      CHIEF
      EXECUTIVE
      HEAD
      CHAIRMAN
      SENIOR
      MANAGER
      COO
      TREASURER
      SECRETARY
      MD
      DEPUTY
      CONTROLLER
      GM
      PRINCIPAL
      CAO
      CIO
      CTO
      CMO
      LEADER
      LEAD
      CCO
      COORDINATOR
      AVP
      ADMINISTRATOR
      CHAIRWOMAN
      CHAIRPERSON
      SUPERINTENDENT
      DEAN
      COMMISSIONER
      CA
      GOVERNOR
      SUPERVISOR
      COACH
      PROVOST
      CAPTAIN
      CHO
      RECTOR

  * **Exclude** a turn if **any** is true:
    * `role` or `speaker_name` contains `Analyst` or `Operator` (or `Editor`, `Moderator`, `??`).

* **Join policy for `company_name`**: if `file_name` maps to **multiple** Unified Info rows (non‑identical), **do not** drop any; for inclusion test we take the **first** row **by** `validation_timestamp` then `start_date` (stable tie‑break: lexicographic on all columns). Log this selection and set `any_mapping_issues=TRUE` downstream. 
* **Output**: write **one row per unique `file_name` present in speaker data** to `qa_manager_docs_YYYY.parquet` with schema shown in **O2**.
* **Report (`report_step_02.md`)**: per year—total turns; Q&A turns kept; managerial turns kept; turns dropped by each exclusion rule; number of `file_name` with mapping collisions; top 20 `role` strings observed; share of empty `role`/`employer` (known in 2002 and 2014).  

> This step enforces **R1 (QA‑only)** and the “managerial speech” subset using minimal, transparent rules grounded in available fields. The need for Q&A and speaker fields is documented in the transcript profiles.  

---

### **STEP 03 (C++, heavy): Tokenize & count dictionary hits**

**Binary:** `03_f1d_tokenize_and_count` (run: `./03_f1d_tokenize_and_count`)

* **Inputs** (read from working dir without args):

  * `lm_Clarity_dictionary.parquet` (from STEP 01)
  * `qa_manager_docs_*.parquet` (all years from STEP 02)
* **Deterministic, minimal algorithm**:

  1. **Load dictionary** into an `unordered_set<string>` of uppercase tokens.
  2. For each row in `qa_manager_docs_YYYY.parquet`:

     * Normalize `doc_text` to uppercase ASCII; replace any non‑letter (`[^A–Z]`) with a single space; collapse spaces.
     * **Tokenize** by spaces into words matching `[A–Z]+`.
     * `total_word_tokens =` number of tokens.
     * `Clarity_hits =` count of tokens that are in the dictionary set. *(Only **Uncertainty** and **Weak_Modal** tokens qualify; **Strong_Modal** is ignored by construction.)* 
     * `f1d_pct = Clarity_hits / max(total_word_tokens, 1)`; if denominator is 0, emit NaN.
     * Keep frequency counts to emit `top5_matches`.
  3. Write `f1d_call_YYYY.parquet` for each input year with schema **O3**.
* **Report (`report_step_03.md`)**: per year—#calls processed, total tokens, % calls with 0 tokens, global top 25 matched tokens (expect **MAY**, **COULD**, **APPROXIMATELY**, **BELIEVE**, …), distribution of `f1d_pct` (p1/median/p99), and a determinism note (hash of dictionary file, code version).

> This step implements **R2 (the metric formula)** exactly as a proportion of tokens over managerial Q&A, consistent with your F1D construct definition. 

---

### **STEP 04 (Python, light): Build the firm–quarter panel (ALL firms)**

**Script:** `04_build_f1d_panel.py`

* **Inputs**: `f1d_call_*.parquet` + `Unified-info.parquet`.
* **Process**:

  1. **Join mapping**: link each `file_name` in `f1d_call` to Unified Info to fetch `permno`, `company_name`, `business_quarter`. If **multiple** Unified Info rows exist for the same `file_name`, pick the **first** by `validation_timestamp` then `start_date` (record this choice; mark `any_mapping_issues=TRUE`). **Do not** alter the Unified Info table. 
  2. **Aggregate to firm–quarter**: for each `(permno, company_name, business_quarter)`:

     * `sum_total_word_tokens = Σ total_word_tokens`
     * `sum_Clarity_hits = Σ Clarity_hits`
     * `num_calls = count_distinct(file_name)`
     * `f1d_pct = sum_Clarity_hits / max(sum_total_word_tokens, 1)`
  3. **Write per‑year** `f1d_panel_YYYY.parquet` (year from `business_quarter`’s calendar year).
* **Output**: schema **O4**.
* **Report (`report_step_04.md`)**: rows by year; fraction with missing `permno`; distribution of `num_calls`; basic percentiles of `f1d_pct`; count of records with `any_mapping_issues=TRUE`.

> **Scope**: No industry filters here; the panel includes **ALL firms**. You can perform industry exclusions later. 

---

## 3) Determinism & simplicity rules (applies to all steps)

* **No CLI flags**: paths and years are discovered automatically (glob patterns in Python; fixed input file names).
* **Stable selection**: whenever multiple Unified Info rows are present for a `file_name`, the selection rule is **fixed** (first by `validation_timestamp`, then by `start_date`, then by full‑row lexical order). The **entire set** of non‑identical duplicates is still exported to `unified_info_duplicate_file_names.csv`. 
* **Text normalization**: C++ uses the same regex (`[^A–Z] → space`) for all inputs; dictionary and text are both uppercased; token = `[A–Z]+`.
* **Word denominator**: only alphabetic tokens count toward `total_word_tokens`. Numbers, symbols, and empty tokens are excluded.
* **Shard policy**: any table that would exceed ~1 file is written one file per **calendar year**.
* **No folder architecture** is mandated here; scripts read inputs from the working directory and write outputs into the same directory (or an `out/` subfolder if you prefer). The spec does **not** prescribe a directory tree.

---

## 4) Step reports — exact content to emit

Each step writes a **markdown** report containing:

* **Inputs discovered** (file list, sizes), **row counts** in/out, **filters applied**, **collisions/decisions made**, and key **percentiles** or **top‑values**.
* **Hashes**: SHA‑256 of the main input(s) and produced file(s) for reproducibility.
* **Wall‑clock timing** (optional) and **process_version**.

**Examples of mandatory metrics**:

* *STEP 00*: total rows; exact duplicates removed; # `file_name` with >1 non‑identical rows; top 10 columns with differences. 
* *STEP 01*: |Uncertainty|, |Weak_Modal|, |Union|, sample tokens (**MAY**, **COULD**, **APPROXIMATELY**, **BELIEVE**, …). 
* *STEP 02*: per year—Q&A share (validated against data: Q&A dominates in these years); managerial turns kept; missing `role`/`employer` shares; # `file_name` with mapping collisions.  
* *STEP 03*: per year—total tokens, % zero‑token docs, top 25 matched tokens, f1d_pct percentiles.
* *STEP 04*: per year—firm‑quarters produced, % missing `permno`, `num_calls` distribution, f1d_pct percentiles, # with `any_mapping_issues`.

---

## 5) Exact formulas & definitions (for the developer)

* **Dictionary**:
  `Clarity_DICTIONARY = { Word | (Uncertainty > 0) OR (Weak_Modal > 0) }` from the LM CSV. Tokens are normalized to uppercase and must match `[A–Z]+`. 

* **Doc‑level counts (C++)**:
  `total_word_tokens(doc) = count( w ∈ doc | w ∈ [A–Z]+ )`
  `Clarity_hits(doc) = count( w ∈ doc | w ∈ Clarity_DICTIONARY )`
  `f1d_pct(doc) = Clarity_hits(doc) / total_word_tokens(doc)` (NaN if 0/0)

* **Firm–quarter aggregation (Python)**:
  For each `(permno, company_name, business_quarter)`
  `sum_total_word_tokens = Σ_doc total_word_tokens(doc)`
  `sum_Clarity_hits       = Σ_doc Clarity_hits(doc)`
  `f1d_pct              = sum_Clarity_hits / max(sum_total_word_tokens, 1)`

* **QA‑only + Managerial‑only**: Keep transcript turns where `context == "qa"` and the managerial filter passes (see STEP 02).  

---

## 6) Known limitations (deliberate, to keep it minimal)

* **Ambiguity of “MAY” (month vs modal)**: We **intentionally** count **MAY** as a modal if it appears; no date disambiguation is attempted (consistent with a minimal dictionary metric). 
* **Speaker attribution gaps**: Early years have many empty `role`/`employer`; our inclusion rules are conservative (favor clear executives and exclude analysts/operators/brokers). This keeps the measure stable but may under‑include some manager turns. 
* **Unified Info duplicates**: We **never** edit/drop non‑identical duplicate rows; we only log them and use a deterministic selection at join time to avoid double counting. 

---

## 7) Minimal build plan (what to run, in order)

1. `python 00_unified_info_check.py`
2. `python 01_build_lm_Clarity_dictionary.py`
3. `python 02_make_qa_manager_docs.py`
4. `./03_f1d_tokenize_and_count`
5. `python 04_build_f1d_panel.py`

Each script/binary can be re‑run idempotently; outputs overwrite with the same content given the same inputs.
