# Architecture Patterns: Inline Descriptive Statistics for Research Data Pipelines

**Domain:** Research data pipeline observability and documentation
**Researched:** 2026-01-22
**Confidence:** HIGH (based on direct codebase analysis)

## Recommended Architecture

The architecture extends the existing pipeline pattern to embed statistics collection and reporting **inline within each script**, preserving the no-shared-module constraint while adding structured observability.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          EXISTING SCRIPT PATTERN                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  Contract Header → Load Config → Setup DualWriter → Process → Save Outputs │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓ EXTEND TO ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         ENHANCED SCRIPT PATTERN                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  Contract Header                                                            │
│       ↓                                                                     │
│  Load Config                                                                │
│       ↓                                                                     │
│  Setup DualWriter + Initialize stats = {}                                   │
│       ↓                                                                     │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │  PROCESSING LOOP                                                    │   │
│  │    1. Read input → stats['input_rows'] = len(df)                    │   │
│  │    2. Process    → accumulate counts, timings                       │   │
│  │    3. Transform  → stats['output_rows'] = len(result)               │   │
│  │    4. print_stat("Rows", input=X, output=Y) → formats + prints      │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│       ↓                                                                     │
│  Finalize stats (compute derived: delta_pct, per-year summaries)            │
│       ↓                                                                     │
│  Print summary table (via DualWriter → console + log)                       │
│       ↓                                                                     │
│  Save outputs:                                                              │
│    - data.parquet                                                           │
│    - stats.json          ← NEW: structured statistics                       │
│    - variable_reference.csv                                                 │
│    - report_step_X_X.md  ← ENHANCED: includes stats tables                  │
│       ↓                                                                     │
│  Update latest symlink                                                      │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Component Boundaries

| Component | Responsibility | Location | Communicates With |
|-----------|----------------|----------|-------------------|
| **DualWriter** | Mirror stdout to log file | Inline in each script | sys.stdout |
| **Stats Dict** | Accumulate metrics during processing | Local variable in main() | print_stat helper |
| **print_stat()** | Format and print individual metrics | Inline helper function | DualWriter (stdout) |
| **print_stats_summary()** | Format and print summary table | Inline helper function | DualWriter (stdout) |
| **save_stats()** | Write stats.json to output dir | Inline helper function | Output directory |
| **Report Generator** | Embed stats in markdown report | Existing report logic | stats dict |

### Data Flow for Statistics Collection

```
Input File
    │
    ├──► Read Phase
    │       │
    │       ├─ stats['input_rows'] = len(df)
    │       ├─ stats['input_columns'] = len(df.columns)
    │       └─ print(f"  Loaded {len(df):,} rows")  ← Already exists
    │
    ├──► Transform Phase (per-step specific)
    │       │
    │       ├─ stats['filter_X_removed'] = count
    │       ├─ stats['match_rate'] = matched/total
    │       └─ print(f"  Removed {count:,} rows")   ← Already exists
    │
    ├──► Output Phase
    │       │
    │       ├─ stats['output_rows'] = len(result)
    │       ├─ stats['delta_pct'] = (out-in)/in * 100
    │       └─ print(f"  Final: {len(result):,} rows")
    │
    └──► Finalize Phase
            │
            ├─ print_stats_summary(stats)  ← NEW: formatted table
            ├─ save_stats(stats, out_dir)  ← NEW: stats.json
            └─ embed_stats_in_report()     ← ENHANCED
```

## Patterns to Follow

### Pattern 1: Inline Stats Dictionary

Initialize a `stats` dictionary at the start of main() and accumulate metrics throughout processing.

**What:** Single dictionary accumulates all metrics for the run
**When:** Every script
**Why:** No shared module needed, naturally scoped to run lifetime

```python
def main():
    # ... setup ...
    
    # Initialize stats collector
    stats = {
        'step_id': '1.1_CleanMetadata',
        'timestamp': timestamp,
        'input': {},
        'processing': {},
        'output': {},
        'timing': {}
    }
    
    # During processing
    stats['input']['total_rows'] = len(df)
    
    # After filtering
    stats['processing']['duplicates_removed'] = exact_dupes
    stats['processing']['event_filter_removed'] = removed
    
    # After save
    stats['output']['final_rows'] = len(df_final)
    stats['output']['columns'] = len(df_final.columns)
```

### Pattern 2: Typed Stats Helper Function (Inline)

Define a small helper function inline to standardize metric printing.

**What:** Helper function that formats and prints metrics consistently
**When:** Replace ad-hoc print statements
**Why:** Consistent formatting, easier to parse logs programmatically

```python
def print_stat(label, before=None, after=None, value=None, indent=2):
    """Print a statistic with consistent formatting.
    
    Modes:
        - Delta mode (before/after): "  Label: 1,000 -> 800 (-20.0%)"
        - Value mode: "  Label: 1,000"
    """
    prefix = " " * indent
    if before is not None and after is not None:
        delta = after - before
        pct = (delta / before * 100) if before != 0 else 0
        sign = "+" if delta >= 0 else ""
        print(f"{prefix}{label}: {before:,} -> {after:,} ({sign}{pct:.1f}%)")
    else:
        v = value if value is not None else after
        print(f"{prefix}{label}: {v:,}")
```

**Usage:**
```python
print_stat("Rows", before=initial_rows, after=len(df_cleaned))
# Output: "  Rows: 50,000 -> 45,000 (-10.0%)"

print_stat("Unique CEOs", value=df['ceo_id'].nunique())
# Output: "  Unique CEOs: 2,345"
```

### Pattern 3: Summary Table at End of Script

Print a formatted summary table before saving outputs.

**What:** ASCII table summarizing key metrics
**When:** End of main(), before save
**Why:** Quick visual check, appears in both console and log

```python
def print_stats_summary(stats):
    """Print formatted summary table."""
    print("\n" + "=" * 60)
    print("STATISTICS SUMMARY")
    print("=" * 60)
    
    # Input/Output comparison
    print("\n| Stage     | Metric          | Value       |")
    print("|-----------|-----------------|-------------|")
    print(f"| Input     | Total Rows      | {stats['input']['total_rows']:>11,} |")
    print(f"| Output    | Final Rows      | {stats['output']['final_rows']:>11,} |")
    print(f"| Delta     | Rows Removed    | {stats['output']['total_removed']:>11,} |")
    
    # Processing breakdown
    print("\n| Filter           | Removed    | % of Input |")
    print("|------------------|------------|------------|")
    for name, count in stats['processing'].items():
        pct = count / stats['input']['total_rows'] * 100
        print(f"| {name:<16} | {count:>10,} | {pct:>9.2f}% |")
    
    print("=" * 60)
```

### Pattern 4: Structured stats.json Output

Save statistics as JSON alongside other outputs for programmatic access.

**What:** Machine-readable statistics file
**When:** Always, alongside parquet and report outputs
**Where:** `4_Outputs/{step}/{timestamp}/stats.json`
**Why:** Enables automated validation, cross-step analysis, CI checks

```python
import json

def save_stats(stats, out_dir):
    """Save statistics to JSON file."""
    stats_path = out_dir / 'stats.json'
    with open(stats_path, 'w') as f:
        json.dump(stats, f, indent=2, default=str)
    print(f"Saved: stats.json")
```

**Output format:**
```json
{
  "step_id": "1.1_CleanMetadata",
  "timestamp": "2026-01-22_143052",
  "input": {
    "total_rows": 50000,
    "columns": 25,
    "source": "Unified-info.parquet"
  },
  "processing": {
    "duplicates_removed": 123,
    "collision_rows_resolved": 45,
    "event_filter_removed": 5000,
    "date_filter_removed": 200
  },
  "output": {
    "final_rows": 44632,
    "columns": 24,
    "files": ["metadata_cleaned.parquet", "variable_reference.csv"]
  },
  "timing": {
    "total_seconds": 12.5,
    "load_seconds": 2.1,
    "process_seconds": 10.4
  }
}
```

### Pattern 5: Enhanced Report with Stats Tables

Extend existing markdown report generation to include descriptive statistics.

**What:** Embed stats tables in report_step_X_X.md
**When:** Report generation phase (already exists)
**Why:** Human-readable documentation with numbers

```python
def generate_report(stats, df_final, out_dir, timestamp):
    """Generate markdown report with embedded statistics."""
    
    report_lines = [
        f"# Step {stats['step_id']}: Report",
        "",
        f"**Timestamp**: {timestamp}",
        "",
        "## Descriptive Statistics",
        "",
        "### Row Counts",
        "",
        "| Stage | Count |",
        "|-------|-------|",
        f"| Input | {stats['input']['total_rows']:,} |",
        f"| Output | {stats['output']['final_rows']:,} |",
        f"| Removed | {stats['input']['total_rows'] - stats['output']['final_rows']:,} |",
        "",
        "### Processing Breakdown",
        "",
        "| Filter | Removed | % of Input |",
        "|--------|---------|------------|",
    ]
    
    for name, count in stats['processing'].items():
        pct = count / stats['input']['total_rows'] * 100
        report_lines.append(f"| {name} | {count:,} | {pct:.2f}% |")
    
    # Add column-level stats if applicable
    if 'column_stats' in stats:
        report_lines.extend([
            "",
            "### Variable Summary",
            "",
            "| Variable | Type | Non-Null | Unique | Min | Max | Mean |",
            "|----------|------|----------|--------|-----|-----|------|",
        ])
        for col, cs in stats['column_stats'].items():
            report_lines.append(
                f"| {col} | {cs['dtype']} | {cs['non_null']:,} | {cs.get('unique', 'N/A')} | "
                f"{cs.get('min', 'N/A')} | {cs.get('max', 'N/A')} | {cs.get('mean', 'N/A'):.2f} |"
            )
    
    report_file = out_dir / f"report_step_{stats['step_id'].replace('.', '_')}.md"
    report_file.write_text("\n".join(report_lines), encoding='utf-8')
```

## Anti-Patterns to Avoid

### Anti-Pattern 1: Shared Stats Module

**What:** Creating a `stats_utils.py` or shared module for statistics
**Why bad:** Violates inline constraint; creates dependency; complicates reproducibility
**Instead:** Copy the 3 small helper functions into each script (DRY is secondary to independence)

### Anti-Pattern 2: Logging Framework Overhead

**What:** Using Python's `logging` module with handlers, formatters, etc.
**Why bad:** Adds complexity; DualWriter already handles dual output; harder to read logs
**Instead:** Continue using print() through DualWriter; simple and effective

### Anti-Pattern 3: Stats in Logs Only

**What:** Only printing statistics to console/log without structured output
**Why bad:** Hard to aggregate across runs; can't validate programmatically; logs get deleted
**Instead:** Always save stats.json alongside parquet outputs

### Anti-Pattern 4: Inline Stats Everywhere

**What:** Computing and printing stats at every line of code
**Why bad:** Clutters output; obscures important metrics; slows processing
**Instead:** Collect in phases (input/process/output), print summary at end

### Anti-Pattern 5: Mixing Run Metadata with Data Statistics

**What:** Storing stats.json in `3_Logs/` instead of `4_Outputs/`
**Why bad:** Stats describe the DATA produced, not just the run; belongs with outputs
**Instead:** 
- `3_Logs/` = ephemeral run logs (can be deleted)
- `4_Outputs/` = timestamped artifacts including stats.json (persistent)

## Build Order Implications

### Phase Ordering for Implementation

The statistics infrastructure can be added to scripts in any order, but recommend:

```
Phase 1: Template and pilot
├── Define stats schema for one representative script (e.g., 1.1_CleanMetadata)
├── Add inline helpers (print_stat, print_stats_summary, save_stats)
├── Test: verify console output matches log file exactly
└── Test: verify stats.json is valid JSON and contains expected fields

Phase 2: Roll out to Step 1 (Sample construction)
├── 1.1_CleanMetadata.py
├── 1.2_LinkEntities.py
├── 1.3_BuildTenureMap.py
└── 1.4_AssembleManifest.py

Phase 3: Roll out to Step 2 (Text processing)
├── 2.1_TokenizeAndCount.py
└── 2.2_ConstructVariables.py

Phase 4: Roll out to Step 3-4 (Financial/Econometric)
├── 3.X scripts
└── 4.X scripts

Phase 5: Root README.md documentation
└── Comprehensive project documentation with pipeline overview
```

**Rationale:**
1. Start with a pilot to validate the pattern
2. Step 1 scripts are simpler, establish baseline
3. Step 2 has per-year loops, tests accumulation pattern
4. Steps 3-4 have complex outputs, test integration with existing reports
5. README last, after all scripts updated (can reference complete stats)

## Where Files Should Live

### Output Location Decision Matrix

| File Type | Location | Rationale |
|-----------|----------|-----------|
| `stats.json` | `4_Outputs/{step}/{timestamp}/` | Describes data produced; timestamped with run |
| `report_step_X_X.md` | `4_Outputs/{step}/{timestamp}/` | Human summary; already here |
| `variable_reference.csv` | `4_Outputs/{step}/{timestamp}/` | Data dictionary; already here |
| `{timestamp}.log` | `3_Logs/{step}/` | Ephemeral run record; already here |
| `README.md` | Project root | Project-level documentation |

### stats.json vs Log Files

**3_Logs/ (Run Records)**
- Full console output (via DualWriter)
- Can be cleaned up periodically
- For debugging "what happened during this run"

**4_Outputs/stats.json (Data Description)**
- Structured metrics about the DATA produced
- Preserved with outputs (timestamped)
- For validation "is this output reasonable?"
- Machine-readable for automated checks

## README Structure for Academic Documentation

### Root README.md Structure

```markdown
# F1D Clarity Measure Pipeline

## Overview
[2-3 paragraphs describing the project purpose and methodology]

## Data Sources
| Source | Description | Location |
|--------|-------------|----------|
| LM Dictionary | Loughran-McDonald Master Dictionary | `1_Inputs/` |
| Unified Info | Call metadata | `1_Inputs/` |
| Speaker Data | Transcript text by year | `1_Inputs/` |

## Pipeline Steps

### Step 1: Sample Construction
| Step | Script | Description | Key Outputs |
|------|--------|-------------|-------------|
| 1.1 | CleanMetadata | Filter and deduplicate metadata | metadata_cleaned.parquet |
| 1.2 | LinkEntities | Link calls to firms and CEOs | ... |

### Step 2: Textual Analysis
...

### Step 3: Financial Features
...

### Step 4: Econometric Estimation
...

## Running the Pipeline

\`\`\`bash
# Execute steps in order
python 2_Scripts/1_Sample/1.1_CleanMetadata.py
python 2_Scripts/1_Sample/1.2_LinkEntities.py
...
\`\`\`

## Output Structure

\`\`\`
4_Outputs/
├── 1.1_CleanMetadata/
│   ├── 2026-01-22_143052/
│   │   ├── metadata_cleaned.parquet
│   │   ├── variable_reference.csv
│   │   ├── stats.json                 ← Descriptive statistics
│   │   └── report_step_1_1.md
│   └── latest -> 2026-01-22_143052/
...
\`\`\`

## Variable Definitions
[Link to master variable dictionary or include inline]

## Reproducibility
- Config: `config/project.yaml`
- Random seed: 42 (pinned)
- Thread count: 1 (deterministic)

## Citation
[Academic citation format]
```

## Integration with Existing DualWriter Pattern

The existing DualWriter class needs NO modification. Statistics flow through it naturally:

```python
# Existing pattern (works unchanged)
class DualWriter:
    def __init__(self, log_path):
        self.terminal = sys.stdout
        self.log = open(log_path, 'w', encoding='utf-8')
    
    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)
        self.log.flush()
    
    def flush(self):
        self.terminal.flush()
        self.log.flush()

# Stats printing flows through automatically
sys.stdout = DualWriter(log_path)

# All prints go to both terminal and log
print_stat("Rows", before=1000, after=800)  # → terminal + log
print_stats_summary(stats)                   # → terminal + log
```

The only addition is saving `stats.json` separately for machine consumption.

## Scalability Considerations

| Concern | Current Scale | Future Scale | Approach |
|---------|--------------|--------------|----------|
| Per-script stats | ~10-20 metrics | ~50+ metrics | Nested dict structure handles growth |
| Per-year aggregation | 17 years | 50+ years | Loop accumulation already works |
| Cross-step validation | Manual | Automated | stats.json enables CI checks |
| Large column stats | ~25 columns | 100+ columns | Sample-based stats for performance |

## Sources

- **Primary:** Direct analysis of existing codebase
  - `2_Scripts/1_Sample/1.1_CleanMetadata.py` - DualWriter pattern, report generation
  - `2_Scripts/2_Text/2.1_TokenizeAndCount.py` - Per-year loop pattern
  - `2_Scripts/4_Econometric/4.1_EstimateCeoClarity.py` - Complex output pattern
  - `config/project.yaml` - Configuration structure
- **Confidence:** HIGH (patterns derived from existing working code)
