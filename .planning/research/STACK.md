# Technology Stack

**Project:** F1D Data Pipeline Observability & Documentation
**Researched:** 2026-01-22
**Mode:** Stack dimension for observability additions

## Executive Summary

This stack recommendation focuses on **lightweight additions** to an existing pandas/numpy-based research pipeline. The goal is comprehensive descriptive statistics and documentation without restructuring the existing architecture.

**Key principle:** Use what you already have (pandas, numpy) enhanced with minimal targeted libraries. Avoid heavy profiling frameworks designed for web-scale data engineering.

## Recommended Stack

### Core Framework (Already In Place)
| Technology | Version | Purpose | Why Keep |
|------------|---------|---------|----------|
| pandas | 3.0.x | Data manipulation | Already used, mature `df.describe()` and statistical methods. |
| numpy | 2.x | Numerical operations | Already used, provides fast array statistics. |
| PyYAML | 6.x | Config loading | Already used for `project.yaml`. |

**Note:** pandas 3.0.0 was released January 21, 2026, requiring Python >=3.11. If the project uses an older Python, stay on pandas 2.2.x (Python >=3.9).

### Statistics Reporting (New Additions)

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| skimpy | 0.0.20 | Console statistics display | **PRIMARY CHOICE.** Lightweight, produces rich console-formatted summary statistics like R's `skimr`. Works with both pandas and Polars DataFrames. Minimal dependencies. MIT license. |
| scipy.stats | 1.17.x | Statistical tests | For normality tests, distribution fitting if needed. Already a common dependency in academic research. Only add if statistical tests are required beyond descriptive stats. |

**Confidence: HIGH** - Verified via PyPI (skimpy 0.0.20 released Jan 3, 2026; scipy 1.17.0 released Jan 10, 2026).

### Console Formatting

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| rich | 14.2.x | Formatted console output | **RECOMMENDED.** skimpy uses rich internally. If adding more console formatting beyond skimpy, use rich directly for tables, progress bars, and styled output. Already production-stable. |
| tabulate | 0.9.x | Simple table formatting | **ALTERNATIVE.** If rich is too heavy or you want plain-text tables compatible with log files. Supports markdown, grid, and plain formats. Last release Oct 2022 but stable and widely used. |

**Confidence: HIGH** - Verified via PyPI (rich 14.2.0 Oct 2025).

### Structured Output

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| json (stdlib) | N/A | JSON output | **USE STDLIB.** Python's built-in json module is sufficient for stats export. No extra dependency. |
| pandas.to_json() | N/A | DataFrame to JSON | Already available. Use `orient='records'` or `orient='table'` for structured output. |
| pandas.to_csv() | N/A | CSV output | Already available. Ideal for stats tables that academic reviewers can open in Excel. |

**Confidence: HIGH** - Standard library, no verification needed.

### Timing & Profiling

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| time (stdlib) | N/A | Basic timing | **USE STDLIB.** `time.perf_counter()` for high-resolution step timing. Zero dependencies. |
| contextlib (stdlib) | N/A | Context managers | Create reusable timing context managers for step profiling. |

**Confidence: HIGH** - Standard library.

### Documentation

| Technology | Version | Purpose | Why |
|------------|---------|---------|-----|
| Markdown | N/A | README format | **Standard for GitHub.** Academic reviewers expect README.md. No tooling needed beyond text editor. |
| Python docstrings | N/A | Code documentation | Already using contract headers. Expand with NumPy-style docstrings if API documentation is needed. |

## Alternatives Considered

| Category | Recommended | Alternative | Why Not Alternative |
|----------|-------------|-------------|---------------------|
| EDA/Profiling | skimpy | ydata-profiling | ydata-profiling (v4.18.1) is excellent but overkill for this use case. It generates full HTML reports with visualizations, correlations, interactions. Too heavy for "add stats to each script" - designed for one-time EDA exploration, not pipeline observability. Also has significant dependencies. |
| Console display | rich/skimpy | prettytable | prettytable is simpler but less feature-rich. rich is already a transitive dependency via skimpy. |
| Stats export | stdlib json | dataclasses-json | Unnecessary complexity. pandas + json stdlib handles all needs. |
| Profiling | time stdlib | memory_profiler, line_profiler | Only needed for debugging performance issues, not for routine observability. Adds complexity. |

## What NOT to Use

| Technology | Why Avoid |
|------------|-----------|
| **ydata-profiling** | Overkill. Designed for interactive EDA, not embedded pipeline stats. Heavy dependencies (400KB wheel + Jinja2, pandas, scipy, etc.). Creates HTML reports rather than console+file output. |
| **dataprep** | Similar to ydata-profiling - designed for exploratory analysis, not pipeline observability. |
| **Great Expectations** | Data validation framework, not observability. Overkill for descriptive statistics. |
| **Dagster/Prefect/Airflow observability** | Wrong paradigm. These are orchestration tools. The existing pipeline is script-based, not DAG-based. |
| **Prometheus/Grafana** | Designed for production services, not batch research pipelines. |
| **pandas-profiling** | Deprecated name for ydata-profiling. Same concerns apply. |
| **sweetviz** | HTML report generation for EDA. Same concerns as ydata-profiling. |

## Installation

```bash
# Minimal addition (skimpy bundles rich as dependency)
pip install skimpy>=0.0.20

# If scipy.stats is needed for statistical tests
pip install scipy>=1.17.0

# For simple markdown table generation without rich styling
pip install tabulate>=0.9.0
```

### Requirements Addition

Add to project requirements:
```
# Observability additions
skimpy>=0.0.20        # Console statistics display
tabulate>=0.9.0       # Plain-text table formatting (optional)
# scipy>=1.17.0       # Only if statistical tests needed
```

## Usage Patterns

### Pattern 1: Quick DataFrame Summary to Console

```python
from skimpy import skim

# Prints formatted summary to console
skim(df)
```

### Pattern 2: Stats to Dual Log (Console + File)

```python
import pandas as pd
import json
from datetime import datetime

def compute_stats(df, name):
    """Compute descriptive statistics for a DataFrame."""
    stats = {
        'name': name,
        'timestamp': datetime.now().isoformat(),
        'shape': {'rows': len(df), 'columns': len(df.columns)},
        'dtypes': df.dtypes.value_counts().to_dict(),
        'missing': df.isnull().sum().to_dict(),
        'numeric_summary': df.describe().to_dict()
    }
    return stats

def log_stats(stats, print_fn, json_path=None):
    """Log stats to console and optionally to JSON file."""
    print_fn(f"Dataset: {stats['name']}")
    print_fn(f"  Shape: {stats['shape']['rows']:,} rows x {stats['shape']['columns']} columns")
    print_fn(f"  Missing: {sum(stats['missing'].values()):,} total null values")
    
    if json_path:
        with open(json_path, 'w') as f:
            json.dump(stats, f, indent=2, default=str)
```

### Pattern 3: Step Timing Context Manager

```python
import time
from contextlib import contextmanager

@contextmanager
def timed_step(name, print_fn):
    """Context manager for timing pipeline steps."""
    print_fn(f"[START] {name}")
    start = time.perf_counter()
    try:
        yield
    finally:
        elapsed = time.perf_counter() - start
        print_fn(f"[END] {name}: {elapsed:.2f}s")
```

### Pattern 4: Rich Tables for Console (if skimpy insufficient)

```python
from rich.console import Console
from rich.table import Table

def print_stats_table(stats_dict, console=None):
    """Print statistics as a rich table."""
    if console is None:
        console = Console()
    
    table = Table(title="Variable Statistics")
    table.add_column("Variable", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Mean", justify="right")
    table.add_column("Std", justify="right")
    
    for var, stat in stats_dict.items():
        table.add_row(var, str(stat['count']), f"{stat['mean']:.2f}", f"{stat['std']:.2f}")
    
    console.print(table)
```

## Integration with Existing Pipeline

The existing pipeline already has:
- `DualWriter` class for console+file logging
- `print_dual()` function for synchronized output
- Timestamped output directories
- YAML config loading

**Recommendation:** Keep these patterns. Add statistics computation functions that use `print_dual()` for output. Store structured stats in JSON alongside existing parquet outputs.

## Version Compatibility Matrix

| Library | Min Python | Notes |
|---------|------------|-------|
| pandas 3.0.x | 3.11+ | Major release Jan 2026 |
| pandas 2.2.x | 3.9+ | Use if Python < 3.11 |
| skimpy 0.0.20 | 3.10+ | Production stable |
| scipy 1.17.x | 3.11+ | Current release |
| scipy 1.14.x | 3.10+ | Use if Python < 3.11 |
| rich 14.x | 3.8+ | Wide compatibility |
| tabulate 0.9.x | 3.7+ | Wide compatibility |

## Confidence Assessment

| Recommendation | Confidence | Reason |
|----------------|------------|--------|
| Use skimpy for console stats | HIGH | Verified current on PyPI, purpose-built for this use case |
| Use pandas built-in methods | HIGH | Standard practice, already in use |
| Avoid ydata-profiling | HIGH | Overkill verified via documentation review |
| Use stdlib for timing | HIGH | Standard practice, no dependencies |
| Use tabulate for plain tables | MEDIUM | Stable but not updated since Oct 2022 |
| Version recommendations | HIGH | All verified via PyPI as of Jan 2026 |

## Sources

- PyPI: ydata-profiling 4.18.1 (https://pypi.org/project/ydata-profiling/) - Released Jan 13, 2026
- PyPI: skimpy 0.0.20 (https://pypi.org/project/skimpy/) - Released Jan 3, 2026  
- PyPI: pandas 3.0.0 (https://pypi.org/project/pandas/) - Released Jan 21, 2026
- PyPI: rich 14.2.0 (https://pypi.org/project/rich/) - Released Oct 9, 2025
- PyPI: tabulate 0.9.0 (https://pypi.org/project/tabulate/) - Released Oct 6, 2022
- PyPI: scipy 1.17.0 (https://pypi.org/project/scipy/) - Released Jan 10, 2026
- Existing project: config/project.yaml, 2_Scripts/*.py (reviewed for current patterns)
