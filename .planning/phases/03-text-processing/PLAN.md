---
phase: 03-text-processing
plan: 01
type: execute
wave: 1
depends_on: ["01-template-pilot"]
files_modified: []
autonomous: true

must_haves:
  truths:
    - "stats.json exists in each timestamped output directory (2.1, 2.2, 2.3)"
    - "stats.json files are valid JSON (parseable)"
    - "stats.json contains text processing metrics (tokenization, vocabulary, text variables)"
    - "Per-year breakdowns included for tokenization statistics"
    - "Dictionary version and vocabulary coverage documented"
    - "Console output matches log file content"
    - "Summary tables display correctly with formatted numbers"
  artifacts:
    - path: "4_Outputs/2.1_TokenizeAndCount/latest/stats.json"
      provides: "Tokenization metrics (word counts, vocabulary, per-year breakdowns)"
    - path: "4_Outputs/2.2_ConstructVariables/latest/stats.json"
      provides: "Text variable summaries (clarity, tone distributions)"
    - path: "4_Outputs/2.3_VerifyStep2/latest/stats.json"
      provides: "Verification diagnostics and summary statistics"
  key_links:
    - from: "stats.json (2.1)"
      to: "STAT-01-09 + text-specific"
      via: "field validation"
      pattern: "tokenization|vocabulary|per_year|word_count"
    - from: "stats.json (2.2)"
      to: "STAT-01-09 + variable-specific"
      via: "field validation"
      pattern: "clarity|tone|distribution"
    - from: "stats.json (2.3)"
      to: "STAT-01-09 + verification"
      via: "field validation"
      pattern: "verification|diagnostics"
---

<objective>
Roll out the statistics pattern (STAT-01-12) to all Step 2 scripts with text processing metrics.

Purpose: Apply the validated statistics framework from Phase 1 to Step 2 text processing scripts, adding domain-specific metrics for tokenization, text variables, and verification.

Output: Updated Step 2 scripts with inline statistics, producing stats.json files with text processing metrics.
</objective>

<execution_context>
@~/.config/opencode/get-shit-done/workflows/execute-plan.md
@~/.config/opencode/get-shit-done/templates/summary.md
</execution_context>

<context>
@.planning/PROJECT.md
@.planning/ROADMAP.md
@.planning/STATE.md
@.planning/phases/01-template-pilot/01-03-SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add inline stats helpers to 2.1_TokenizeAndCount.py</name>
  <files>2_Scripts/2.1_TokenizeAndCount.py</files>
  <action>
Apply the inline statistics pattern to 2.1_TokenizeAndCount.py with tokenization metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
from collections import Counter
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture tokenization-specific metrics:
     - Total words/token counts
     - Vocabulary size (unique words)
     - Per-year word count breakdowns
     - Word count distribution (min, max, mean, median)
     - Dictionary version used
     - Vocabulary coverage percentage

3. **Integration points:**
   - Record input checksums after loading text data
   - Track tokenization timing
   - Calculate vocabulary metrics after tokenization
   - Compute per-year breakdowns (if year column exists)
   - Calculate word count distributions
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "2.1_TokenizeAndCount",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_documents": int,
    "total_raw_words": int
  },
  "processing": {
    "tokenizer_type": "...",
    "dictionary_version": "...",
    "vocabulary_size": int,
    "total_tokens": int,
    "unique_tokens": int,
    "per_year_breakdown": {
      "year": {"token_count": int, "unique_tokens": int, "doc_count": int},
      ...
    },
    "word_count_distribution": {
      "min": int,
      "max": int,
      "mean": float,
      "median": float,
      "percentiles": {"p25": float, "p50": float, "p75": float, "p90": float, "p95": float}
    },
    "vocabulary_coverage": float,
    "avg_tokens_per_document": float
  },
  "output": {
    "files": [...],
    "final_tokens": int,
    "vocabulary_file": "..."
  },
  "timing": {
    "start_iso": "...",
    "end_iso": "...",
    "duration_seconds": float
  },
  "missing_values": {...}
}
```
  </action>
  <verify>
  Script runs successfully and produces stats.json with all required tokenization metrics.
  </verify>
  <done>
  2.1_TokenizeAndCount.py updated with inline stats helpers and produces stats.json with tokenization metrics.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add inline stats helpers to 2.2_ConstructVariables.py</name>
  <files>2_Scripts/2.2_ConstructVariables.py</files>
  <action>
Apply the inline statistics pattern to 2.2_ConstructVariables.py with text variable metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture text variable metrics:
     - Clarity score distributions (min, max, mean, median)
     - Tone measure distributions (positive, negative, neutral, etc.)
     - Variable completion rates
     - Correlation summaries (if applicable)
     - Extreme value counts

3. **Integration points:**
   - Record input checksums after loading tokenized data
   - Track variable construction timing
   - Calculate distributions for each text variable
   - Identify extreme/outlier values
   - Document variable ranges
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "2.2_ConstructVariables",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_documents": int,
    "total_tokens": int
  },
  "processing": {
    "variables_constructed": [...],
    "clarity_distribution": {
      "variable_name": {
        "min": float,
        "max": float,
        "mean": float,
        "median": float,
        "std": float,
        "missing_count": int,
        "missing_percent": float
      },
      ...
    },
    "tone_distribution": {
      "positive": {"mean": float, "std": float, "percentile_90": float},
      "negative": {"mean": float, "std": float, "percentile_90": float},
      "neutral": {"mean": float, "std": float, "percentile_90": float},
      ...
    },
    "extreme_values": {
      "variable_name": {
        "high_count": int,
        "low_count": int,
        "thresholds": {"high": float, "low": float}
      }
    },
    "variable_completion_rates": {
      "variable_name": float,
      ...
    }
  },
  "output": {
    "files": [...],
    "variables_added": int,
    "final_columns": int
  },
  "timing": {
    "start_iso": "...",
    "end_iso": "...",
    "duration_seconds": float
  },
  "missing_values": {...}
}
```
  </action>
  <verify>
  Script runs successfully and produces stats.json with all required text variable metrics.
  </verify>
  <done>
  2.2_ConstructVariables.py updated with inline stats helpers and produces stats.json with text variable metrics.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add inline stats helpers to 2.3_VerifyStep2.py</name>
  <files>2_Scripts/2.3_VerifyStep2.py</files>
  <action>
Apply the inline statistics pattern to 2.3_VerifyStep2.py with verification diagnostics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture verification metrics:
     - Check pass/fail counts
     - Data integrity verification results
     - Schema validation results
     - Consistency check results
     - Error/warning counts by category
     - Final dataset summary

3. **Integration points:**
   - Record input checksums after loading processed data
   - Track verification timing
   - Count checks passed/failed
   - Categorize errors and warnings
   - Document integrity issues found
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "2.3_VerifyStep2",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_documents": int
  },
  "processing": {
    "verification_checks": {
      "total_checks": int,
      "passed": int,
      "failed": int,
      "warnings": int
    },
    "check_results": {
      "check_name": {
        "status": "pass/fail/warning",
        "details": "...",
        "affected_rows": int
      },
      ...
    },
    "data_integrity": {
      "schema_valid": bool,
      "no_duplicates": bool,
      "no_nulls_in_key_columns": bool,
      "date_ranges_valid": bool,
      "issues_found": [...]
    },
    "consistency_checks": {
      "token_count_consistent": bool,
      "variable_ranges_valid": bool,
      "year_continuity": bool
    },
    "error_categories": {
      "data_quality": int,
      "schema": int,
      "consistency": int,
      "missing_data": int
    }
  },
  "output": {
    "files": [...],
    "verification_passed": bool,
    "issues_to_address": int
  },
  "timing": {
    "start_iso": "...",
    "end_iso": "...",
    "duration_seconds": float
  },
  "missing_values": {...}
}
```
  </action>
  <verify>
  Script runs successfully and produces stats.json with all required verification metrics.
  </verify>
  <done>
  2.3_VerifyStep2.py updated with inline stats helpers and produces stats.json with verification metrics.
  </done>
</task>

<task type="auto">
  <name>Task 4: Run all Step 2 scripts and verify stats.json</name>
  <files></files>
  <action>
Execute all three Step 2 scripts and validate their stats.json outputs:

1. **Run scripts in sequence:**
```bash
python 2_Scripts/2.1_TokenizeAndCount.py
python 2_Scripts/2.2_ConstructVariables.py
python 2_Scripts/2.3_VerifyStep2.py
```

2. **Verify stats.json files exist:**
```bash
ls -la 4_Outputs/2.1_TokenizeAndCount/latest/stats.json
ls -la 4_Outputs/2.2_ConstructVariables/latest/stats.json
ls -la 4_Outputs/2.3_VerifyStep2/latest/stats.json
```

3. **Validate JSON syntax for all files:**
```bash
python -c "import json; json.load(open('4_Outputs/2.1_TokenizeAndCount/latest/stats.json')); print('2.1: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/2.2_ConstructVariables/latest/stats.json')); print('2.2: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/2.3_VerifyStep2/latest/stats.json')); print('2.3: Valid JSON')"
```

4. **Check required fields for 2.1:**
```python
import json

with open('4_Outputs/2.1_TokenizeAndCount/latest/stats.json') as f:
    stats = json.load(f)

required_keys = ['step_id', 'timestamp', 'input', 'processing', 'output', 'timing', 'missing_values']
for key in required_keys:
    assert key in stats, f"2.1 Missing key: {key}"

processing_fields = ['tokenizer_type', 'vocabulary_size', 'total_tokens', 'per_year_breakdown', 'word_count_distribution']
for field in processing_fields:
    assert field in stats['processing'], f"2.1 Missing processing.{field}"

print("2.1 stats.json: All required fields present")
```

5. **Check required fields for 2.2:**
```python
with open('4_Outputs/2.2_ConstructVariables/latest/stats.json') as f:
    stats = json.load(f)

assert 'clarity_distribution' in stats['processing'], "2.2 Missing clarity_distribution"
assert 'tone_distribution' in stats['processing'], "2.2 Missing tone_distribution"
assert 'variable_completion_rates' in stats['processing'], "2.2 Missing variable_completion_rates"

print("2.2 stats.json: All required fields present")
```

6. **Check required fields for 2.3:**
```python
with open('4_Outputs/2.3_VerifyStep2/latest/stats.json') as f:
    stats = json.load(f)

assert 'verification_checks' in stats['processing'], "2.3 Missing verification_checks"
assert 'data_integrity' in stats['processing'], "2.3 Missing data_integrity"
assert 'consistency_checks' in stats['processing'], "2.3 Missing consistency_checks"

print("2.3 stats.json: All required fields present")
```

7. **Verify log files contain summary tables:**
```bash
grep "STATISTICS SUMMARY" 3_Logs/2.1_TokenizeAndCount/*.log | tail -1
grep "STATISTICS SUMMARY" 3_Logs/2.2_ConstructVariables/*.log | tail -1
grep "STATISTICS SUMMARY" 3_Logs/2.3_VerifyStep2/*.log | tail -1
```
  </action>
  <verify>
  All three scripts run successfully and produce valid stats.json files with required metrics.
  </verify>
  <done>
  All Step 2 scripts executed successfully with complete statistics outputs.
  </done>
</task>

<task type="auto">
  <name>Task 5: Create SUMMARY.md</name>
  <files>.planning/phases/03-text-processing/SUMMARY.md</files>
  <action>
Create a summary document at `.planning/phases/03-text-processing/SUMMARY.md` documenting:

1. **Implementation Summary:**
   - Scripts updated: 2.1, 2.2, 2.3
   - Inline stats helpers added to each
   - Text processing metrics implemented

2. **Metrics Coverage:**
   | Script | Metrics Added | Key Fields |
   |--------|---------------|------------|
   | 2.1 | Tokenization | vocabulary_size, per_year_breakdown, word_count_distribution |
   | 2.2 | Text Variables | clarity_distribution, tone_distribution, completion_rates |
   | 2.3 | Verification | verification_checks, data_integrity, consistency_checks |

3. **Sample stats.json outputs (sanitized):**
   - 2.1 sample structure
   - 2.2 sample structure
   - 2.3 sample structure

4. **Issues Found (if any):**
   - Issue description
   - Severity
   - Resolution

5. **Pattern Validation:**
   - STAT-01-09 requirements met in all scripts
   - Text-specific metrics successfully integrated
   - Consistent formatting across all outputs

6. **Next Steps:**
   - Ready for Phase 4: Step 3 script rollout
   - Any refinements needed

Write to `.planning/phases/03-text-processing/SUMMARY.md`
  </action>
  <verify>
  Summary document exists and documents all metrics coverage and implementation details.
  </verify>
  <done>
  Complete summary document created for Phase 3 text processing rollout.
  </done>
</task>

</tasks>

<verification>
- [ ] 2.1_TokenizeAndCount.py updated with inline stats helpers
- [ ] 2.1 stats.json exists and contains tokenization metrics
- [ ] 2.1 stats.json includes per-year breakdowns
- [ ] 2.1 stats.json includes word count distributions
- [ ] 2.1 stats.json includes vocabulary coverage
- [ ] 2.2_ConstructVariables.py updated with inline stats helpers
- [ ] 2.2 stats.json exists and contains text variable metrics
- [ ] 2.2 stats.json includes clarity distributions
- [ ] 2.2 stats.json includes tone distributions
- [ ] 2.2 stats.json includes variable completion rates
- [ ] 2.3_VerifyStep2.py updated with inline stats helpers
- [ ] 2.3 stats.json exists and contains verification metrics
- [ ] 2.3 stats.json includes verification check results
- [ ] 2.3 stats.json includes data integrity assessment
- [ ] All stats.json files are valid JSON
- [ ] All stats.json files contain STAT-01-09 base fields
- [ ] All scripts run successfully
- [ ] Log files contain summary tables
- [ ] SUMMARY.md created
</verification>

<success_criteria>
Phase 3 complete when:
1. All three Step 2 scripts (2.1, 2.2, 2.3) have inline stats helpers
2. All three scripts produce valid stats.json files
3. 2.1 stats.json includes tokenization metrics (vocabulary, per-year, word count distributions)
4. 2.2 stats.json includes text variable metrics (clarity, tone, completion rates)
5. 2.3 stats.json includes verification metrics (checks, integrity, consistency)
6. All scripts run successfully without errors
7. SUMMARY.md documents the implementation
8. Pattern is ready for rollout to Step 3 scripts in Phase 4
</success_criteria>

<output>
After completion, create `.planning/phases/03-text-processing/SUMMARY.md`
</output>
