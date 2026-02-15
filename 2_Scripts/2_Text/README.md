# Text Processing (Step 2)

> **Note:** This folder contains legacy scripts kept for reference. The active versions have been migrated to `src/f1d/text/` as part of the v6.1 architecture standard. New development should use the `f1d.text.*` namespace imports.

## Purpose and Scope

This folder contains scripts for tokenizing earnings call transcripts and constructing linguistic measures (uncertainty, weak modals, tone) using the Loughran-McDonald financial sentiment dictionary. Text processing is the **second step** in the F1D pipeline, transforming raw transcript text into quantitative variables for all subsequent analyses.

**Status:** LEGACY - Migrated to src/f1d/text/
**Prerequisites:** Step 1 (Sample Construction) outputs
**Outputs:** `4_Outputs/2_Text/`

---

## Scripts Overview

| Script | Purpose | Key Outputs |
|--------|---------|-------------|
| `2.1_TokenizeAndCount.py` | Tokenize transcripts and count words | Token counts by speaker role |
| `2.2_ConstructVariables.py` | Construct LM dictionary variables | Uncertainty, tone measures |
| `2.3_VerifyStep2.py` | Verify outputs and generate reports | Validation statistics |
| `2.3_Report.py` | Generate summary reports | Descriptive statistics |

---

## Text Processing Flow

```
Raw Transcript Files
         |
         v
[2.1] TokenizeAndCount (word tokenization, speaker roles)
         |
         v
Token Counts (word counts by speaker, section)
         |
         v
[2.2] ConstructVariables (LM dictionary matching)
         |
         v
Linguistic Variables (uncertainty, weak modal, tone)
         |
         v
[2.3] VerifyStep2 (validation and reporting)
         |
         v
Final Text Variables Output
```

---

## Linguistic Measures

### Loughran-McDonald (LM) Dictionary Categories

The LM Master Dictionary (1993-2024) categorizes words into sentiment categories:

| Category | Example Words | Count in LM Dictionary |
|----------|---------------|----------------------|
| Uncertainty | uncertain, unsure, depend, approximate | 867 words |
| Weak Modal | may, might, could, possibly | 35 words |
| Negative | loss, fail, risk, concern | 2,300+ words |
| Positive | strong, growth, success, achieve | 3,500+ words |
| Tone | Net sentiment (Positive - Negative) | Derived |

### Variable Naming Convention

Variables follow the pattern: `{Speaker}_{Section}_{Measure}_pct`

**Speakers:**
- `Manager`: Firm management (CEO, CFO)
- `CEO`: Chief Executive Officer specifically
- `Analyst`: Q&A participants

**Sections:**
- `QA`: Question-and-Answer session
- `Pres`: Prepared remarks (presentation)

**Measures:**
- `Uncertainty`: LM uncertainty word count / total words
- `Weak_Modal`: Weak modal word count / total words
- `Tone`: (Positive - Negative) / total words

**Example:** `Manager_QA_Uncertainty_pct` = Manager uncertainty percentage in Q&A section

---

## Variable Construction

### Tokenization (2.1_TokenizeAndCount.py)

**Purpose:** Count words by speaker role and section.

**Process:**
1. Parse transcript XML/JSON files
2. Identify speaker segments (QA vs Presentation)
3. Classify speaker roles (Manager vs Analyst)
4. Count words per segment

**Output Variables:**
| Variable | Description |
|----------|-------------|
| Manager_Pres_Words | Word count: Manager in Presentation |
| Manager_QA_Words | Word count: Manager in Q&A |
| CEO_Pres_Words | Word count: CEO in Presentation |
| CEO_QA_Words | Word count: CEO in Q&A |
| Analyst_QA_Words | Word count: Analysts in Q&A |
| Total_Words | Total word count (all speakers, all sections) |

### Variable Construction (2.2_ConstructVariables.py)

**Purpose:** Calculate linguistic measures using LM dictionary.

**Formula:**
```
Measure_pct = (LM_Word_Count / Total_Words) * 100
```

**Output Variables:**
| Variable | Description |
|----------|-------------|
| Manager_Pres_Uncertainty_pct | Manager uncertainty % in Presentation |
| Manager_QA_Uncertainty_pct | Manager uncertainty % in Q&A |
| CEO_Pres_Uncertainty_pct | CEO uncertainty % in Presentation |
| CEO_QA_Uncertainty_pct | CEO uncertainty % in Q&A |
| Manager_Pres_Weak_Modal_pct | Manager weak modal % in Presentation |
| Manager_QA_Weak_Modal_pct | Manager weak modal % in Q&A |
| CEO_Pres_Tone_pct | CEO tone (sentiment) % in Presentation |
| CEO_QA_Tone_pct | CEO tone (sentiment) % in Q&A |

**Total Variables:** 15+ linguistic measures

---

## Input/Output Mapping

### Inputs

| Source | Location | Content |
|--------|----------|---------|
| Sample Manifest | `4_Outputs/1_Sample/` | GVKEY-year matching |
| LM Dictionary | `1_Inputs/Loughran-McDonald_MasterDictionary_1993-2024.csv` | Sentiment word lists |
| Transcripts | `1_Inputs/transcripts/` | Raw earnings call text |

### Outputs

```
4_Outputs/2_Text/
├── 2.1_TokenizeAndCount/
│   ├── token_counts.parquet
│   └── stats.json
├── 2.2_ConstructVariables/
│   ├── linguistic_variables.parquet
│   └── stats.json
└── latest/
    └── linguistic_variables.parquet (symlink to latest)
```

---

## Sample Statistics

### Text Coverage

| Metric | Value |
|--------|-------|
| Total Transcripts | ~112,000 earnings calls |
| Total Words | ~500 million words |
| Avg Words per Call | ~4,500 words |
| Avg QA Words | ~2,000 words |
| Avg Presentation Words | ~2,500 words |

### Linguistic Measure Distributions

| Variable | Mean | SD | Min | Max |
|----------|------|----|-----|-----|
| Manager_QA_Uncertainty_pct | 1.2 | 0.8 | 0 | 5.2 |
| Manager_Pres_Uncertainty_pct | 0.8 | 0.6 | 0 | 3.8 |
| Manager_QA_Weak_Modal_pct | 0.4 | 0.3 | 0 | 2.1 |
| CEO_QA_Tone_pct | 0.2 | 1.5 | -3.2 | 4.5 |

---

## Execution Notes

### Execution Order

**Sequential (must run in order):**

1. **2.1_TokenizeAndCount.py** - Tokenize and count words
2. **2.2_ConstructVariables.py** - Construct linguistic measures
3. **2.3_VerifyStep2.py** - Verify and validate outputs
4. **2.3_Report.py** - Generate summary reports

### Execution Commands

```bash
# Run full text processing
python 2_Scripts/2_Text/2.1_TokenizeAndCount.py
python 2_Scripts/2_Text/2.2_ConstructVariables.py
python 2_Scripts/2_Text/2.3_VerifyStep2.py

# Generate reports
python 2_Scripts/2_Text/2.3_Report.py
```

### Dependencies

- **Sample Manifest:** Required for GVKEY-year matching
- **LM Dictionary:** Required for linguistic classification
- **Transcripts:** Required for text processing

---

## Validation

### Quality Checks

1. **Word Counts:** Non-zero word counts for all calls
2. **Percentage Sums:** Uncertainty + Other <= 100%
3. **Missing Values:** No missing linguistic measures
4. **Outlier Detection:** No extreme values (>3 SD from mean)

### Verification Script

```bash
# Verify text processing outputs
python 2_Scripts/2_Text/2.3_VerifyStep2.py
```

---

## Relationship to Other Steps

### Upstream Dependency

- **Step 1 (Sample):** Required for GVKEY-year matching

### Downstream Consumers

All financial and econometric steps use text measures:

| Step | Usage |
|------|-------|
| Step 3 Financial (V1) | Text measures as controls |
| Step 3 Financial (V2) | Text measures as main IVs (H1-H8) |
| Step 3 Financial (V3) | Text measures for interaction (H9) |
| Step 4 Econometric (V1) | CEO clarity, tone regressions |
| Step 4 Econometric (V2) | Hypothesis testing regressions |
| Step 4 Econometric (V3) | PRisk x Uncertainty regressions |

---

## Key Design Decisions

### QA vs Presentation

**Rationale:** Q&A is spontaneous (less scripted) while Presentation is prepared. This allows testing whether communication style differs between scripted and unscripted sections.

**Variables:** Separate measures for QA and Presentation sections.

### CEO vs Manager

**Rationale:** CEO is the primary speaker, but other managers (CFO, etc.) also speak. CEO-specific measures isolate CEO communication style.

**Variables:** Both CEO-specific and Manager (all) measures.

### Percentage Measures

**Rationale:** Raw word counts vary by call length. Percentage measures standardize by total words, enabling cross-call comparison.

**Formula:** (Category Word Count / Total Words) * 100

### LM Dictionary Choice

**Rationale:** Loughran-McDonald is specifically designed for financial text, unlike general sentiment dictionaries (e.g., VADER, TextBlob) that misclassify financial terms.

**Example:** "Liability" is negative in general English but neutral in financial context.

---

## Known Issues

**Tokenization Edge Cases:**
- Numbers and dates excluded from word counts
- Hyphenated words split (e.g., "long-term" -> "long", "term")
- Acronyms counted as single words

**Speaker Classification:**
- Occasionally misclassifies speakers (e.g., Moderator as Manager)
- Manual validation applied for ambiguous cases
- Classification accuracy >95%

**Dictionary Coverage:**
- LM dictionary primarily English (foreign-language words excluded)
- Financial jargon sometimes misclassified (mitigated by context-specific lists)

---

## References

- **Loughran & McDonald (2011):** "When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks"
- **LM Master Dictionary (1993-2024):** 86,000+ financial sentiment words
- **Financial Text Analysis:** Li (2010), Tetlock (2007)

---

## Contact and Replication

For replication questions:
- `README.md` (root): Project overview
- `CLAUDE.md`: Coding conventions
- Individual script headers: Implementation details

---

*Last updated: 2026-02-14*
*Phase: 78-documentation-synchronization*
*Version: v1.0 Text Processing*
