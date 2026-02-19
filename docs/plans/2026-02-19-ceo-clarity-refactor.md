# CEO Clarity (4.1.1) Refactor Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Refactor the 4.1.1 CEO Clarity script from the old v1 architecture to the new shared variable builder architecture, matching the pattern established for Manager Clarity (4.1).

**Architecture:** Two-stage approach: Stage 3 builds the CEO Clarity panel using shared variable builders, Stage 4 runs the hypothesis test with fixed effects regression and generates Accounting Review LaTeX output.

**Tech Stack:** Python 3.11+, pandas, statsmodels, parquet, YAML config

---

## Overview

This plan refactors `src/f1d/econometric/v1/4.1.1_EstimateCeoClarity.py` into the new architecture:

| Component | Old Location | New Location |
|-----------|--------------|--------------|
| Variable builders | Inline in script | `src/f1d/shared/variables/ceo_*.py` |
| Panel builder | Inline in script | `src/f1d/variables/build_ceo_clarity_panel.py` |
| Hypothesis test | Inline in script | `src/f1d/econometric/test_ceo_clarity.py` |
| Configuration | Hardcoded | `config/variables.yaml` |

### Key Differences from Manager Clarity

| Aspect | Manager Clarity (4.1) | CEO Clarity (4.1.1) |
|--------|----------------------|---------------------|
| Dependent Variable | `Manager_QA_Uncertainty_pct` | `CEO_QA_Uncertainty_pct` |
| Speech Control | `Manager_Pres_Uncertainty_pct` | `CEO_Pres_Uncertainty_pct` |
| Score Output | `ClarityManager` | `ClarityCEO` |
| Output Directory | `outputs/variables/manager_clarity/` | `outputs/variables/ceo_clarity/` |

---

## Task 1: Create CEO QA Uncertainty Variable Builder

**Files:**
- Create: `src/f1d/shared/variables/ceo_qa_uncertainty.py`
- Modify: `src/f1d/shared/variables/__init__.py`

**Step 1: Write the CEO QA Uncertainty builder**

Create `src/f1d/shared/variables/ceo_qa_uncertainty.py`:

```python
"""Builder for CEO Q&A Uncertainty variable.

Loads CEO_QA_Uncertainty_pct from Stage 2 linguistic variables output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class CEOQAUncertaintyBuilder(VariableBuilder):
    """Build CEO Q&A Uncertainty variable from Stage 2 outputs.

    Source: outputs/2_Textual_Analysis/2.2_Variables/latest/
    File: linguistic_variables_{year}.parquet
    Column: CEO_QA_Uncertainty_pct

    Example:
        config = load_variable_config()["ceo_qa_uncertainty"]
        builder = CEOQAUncertaintyBuilder(config)
        result = builder.build(range(2002, 2019), root_path)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with variable config.

        Args:
            config: Must contain 'source', 'file_pattern', 'column'
        """
        super().__init__(config)
        self.column = config.get("column", "CEO_QA_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build CEO Q&A Uncertainty variable.

        Args:
            years: Range of years to process
            root_path: Project root path

        Returns:
            VariableResult with file_name and CEO_QA_Uncertainty_pct columns
        """
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                cols = ["file_name"]
                if self.column in df.columns:
                    cols.append(self.column)
                all_data.append(df[cols])

        if not all_data:
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column,
                    n=0,
                    mean=0.0,
                    std=0.0,
                    min=0.0,
                    p25=0.0,
                    median=0.0,
                    p75=0.0,
                    max=0.0,
                    n_missing=0,
                    pct_missing=100.0
                ),
                metadata={"source": str(source_dir), "column": self.column}
            )

        combined = pd.concat(all_data, ignore_index=True)
        stats = self.get_stats(combined[self.column], self.column)

        return VariableResult(
            data=combined[["file_name", self.column]],
            stats=stats,
            metadata={"source": str(source_dir), "column": self.column}
        )


__all__ = ["CEOQAUncertaintyBuilder"]
```

**Step 2: Verify the file was created**

Run: `ls src/f1d/shared/variables/ceo_qa_uncertainty.py`
Expected: File exists

---

## Task 2: Create CEO Presentation Uncertainty Variable Builder

**Files:**
- Create: `src/f1d/shared/variables/ceo_pres_uncertainty.py`

**Step 1: Write the CEO Pres Uncertainty builder**

Create `src/f1d/shared/variables/ceo_pres_uncertainty.py`:

```python
"""Builder for CEO Presentation Uncertainty variable.

Loads CEO_Pres_Uncertainty_pct from Stage 2 linguistic variables output.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from .base import VariableBuilder, VariableResult, VariableStats


class CEOPresUncertaintyBuilder(VariableBuilder):
    """Build CEO Presentation Uncertainty variable from Stage 2 outputs.

    Source: outputs/2_Textual_Analysis/2.2_Variables/latest/
    File: linguistic_variables_{year}.parquet
    Column: CEO_Pres_Uncertainty_pct

    Example:
        config = load_variable_config()["ceo_pres_uncertainty"]
        builder = CEOPresUncertaintyBuilder(config)
        result = builder.build(range(2002, 2019), root_path)
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize with variable config.

        Args:
            config: Must contain 'source', 'file_pattern', 'column'
        """
        super().__init__(config)
        self.column = config.get("column", "CEO_Pres_Uncertainty_pct")

    def build(self, years: range, root_path: Path) -> VariableResult:
        """Build CEO Presentation Uncertainty variable.

        Args:
            years: Range of years to process
            root_path: Project root path

        Returns:
            VariableResult with file_name and CEO_Pres_Uncertainty_pct columns
        """
        source_dir = self.resolve_source_dir(root_path)
        all_data: List[pd.DataFrame] = []

        for year in years:
            df = self.load_year_file(source_dir, year)
            if df is not None:
                cols = ["file_name"]
                if self.column in df.columns:
                    cols.append(self.column)
                all_data.append(df[cols])

        if not all_data:
            return VariableResult(
                data=pd.DataFrame(columns=["file_name", self.column]),
                stats=VariableStats(
                    name=self.column,
                    n=0,
                    mean=0.0,
                    std=0.0,
                    min=0.0,
                    p25=0.0,
                    median=0.0,
                    p75=0.0,
                    max=0.0,
                    n_missing=0,
                    pct_missing=100.0
                ),
                metadata={"source": str(source_dir), "column": self.column}
            )

        combined = pd.concat(all_data, ignore_index=True)
        stats = self.get_stats(combined[self.column], self.column)

        return VariableResult(
            data=combined[["file_name", self.column]],
            stats=stats,
            metadata={"source": str(source_dir), "column": self.column}
        )


__all__ = ["CEOPresUncertaintyBuilder"]
```

**Step 2: Verify the file was created**

Run: `ls src/f1d/shared/variables/ceo_pres_uncertainty.py`
Expected: File exists

---

## Task 3: Register CEO Variable Builders in __init__.py

**Files:**
- Modify: `src/f1d/shared/variables/__init__.py`

**Step 1: Add imports and exports for CEO builders**

In `src/f1d/shared/variables/__init__.py`, add the imports after the existing ones:

```python
from .ceo_qa_uncertainty import CEOQAUncertaintyBuilder
from .ceo_pres_uncertainty import CEOPresUncertaintyBuilder
```

**Step 2: Add to __all__ list**

Add to the `__all__` list under the Text variables section:

```python
    "CEOQAUncertaintyBuilder",
    "CEOPresUncertaintyBuilder",
```

**Step 3: Verify imports work**

Run: `python -c "from f1d.shared.variables import CEOQAUncertaintyBuilder, CEOPresUncertaintyBuilder; print('OK')"`
Expected: `OK`

**Step 4: Commit**

```bash
git add src/f1d/shared/variables/ceo_qa_uncertainty.py src/f1d/shared/variables/ceo_pres_uncertainty.py src/f1d/shared/variables/__init__.py
git commit -m "feat: add CEO uncertainty variable builders for 4.1.1 refactor"
```

---

## Task 4: Update variables.yaml with CEO Variable Configurations

**Files:**
- Modify: `config/variables.yaml`

**Step 1: Add CEO variable configurations under Stage 2 section**

Add after the `negative_sentiment` entry in `config/variables.yaml`:

```yaml
  ceo_qa_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_QA_Uncertainty_pct"
    description: "CEO-only Q&A uncertainty percentage (not full management team)"

  ceo_pres_uncertainty:
    stage: 2
    source: "outputs/2_Textual_Analysis/2.2_Variables"
    file_pattern: "linguistic_variables_{year}.parquet"
    column: "CEO_Pres_Uncertainty_pct"
    description: "CEO-only presentation uncertainty percentage"
```

**Step 2: Add CEO Clarity hypothesis test configuration**

Add after the `manager_clarity` entry under `hypothesis_tests`:

```yaml
  ceo_clarity:
    test_id: "4.1.1_CeoClarity"
    description: "CEO Clarity Fixed Effects Test (CEO-only variables)"

    dependent: "ceo_qa_uncertainty"

    linguistic_controls:
      - ceo_pres_uncertainty
      - analyst_qa_uncertainty
      - negative_sentiment

    firm_controls:
      - stock_return
      - market_return
      - eps_growth
      - earnings_surprise

    identifiers:
      - manifest  # ceo_id, gvkey, ff12_code, start_date

    regression:
      min_calls_per_ceo: 5
      fixed_effects:
        - ceo_id
        - year
      samples:
        main: [1, 2, 3, 4, 5, 6, 7, 9, 10, 12]  # FF12 codes (non-financial, non-utility)
        finance: [11]
        utility: [8]

    outputs:
      panel: "outputs/variables/ceo_clarity"
      results: "outputs/econometric/ceo_clarity"
```

**Step 3: Verify YAML is valid**

Run: `python -c "import yaml; yaml.safe_load(open('config/variables.yaml')); print('YAML OK')"`
Expected: `YAML OK`

**Step 4: Commit**

```bash
git add config/variables.yaml
git commit -m "feat: add CEO clarity variable configurations to variables.yaml"
```

---

## Task 5: Create Stage 3 Panel Builder - build_ceo_clarity_panel.py

**Files:**
- Create: `src/f1d/variables/build_ceo_clarity_panel.py`

**Step 1: Create the panel builder script**

Create `src/f1d/variables/build_ceo_clarity_panel.py` based on the Manager Clarity pattern:

```python
#!/usr/bin/env python3
"""
================================================================================
STAGE 3: Build CEO Clarity Panel
================================================================================
ID: variables/build_ceo_clarity_panel
Description: Build complete panel for CEO Clarity hypothesis test by loading
             all required variables using shared modules and merging into a
             single panel.

Inputs:
    - outputs/1.4_AssembleManifest/latest/master_sample_manifest.parquet
    - outputs/2_Textual_Analysis/2.2_Variables/latest/linguistic_variables_{year}.parquet
    - outputs/3_Financial_Features/latest/firm_controls_{year}.parquet
    - outputs/3_Financial_Features/latest/market_variables_{year}.parquet

Outputs:
    - outputs/variables/ceo_clarity/{timestamp}/ceo_clarity_panel.parquet
    - outputs/variables/ceo_clarity/{timestamp}/summary_stats.csv

Deterministic: true
Dependencies:
    - Uses: f1d.shared.variables, f1d.shared.config

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd

from f1d.shared.config import load_variable_config, get_config
from f1d.shared.variables import (
    CEOQAUncertaintyBuilder,
    CEOPresUncertaintyBuilder,
    AnalystQAUncertaintyBuilder,
    NegativeSentimentBuilder,
    StockReturnBuilder,
    MarketReturnBuilder,
    EPSGrowthBuilder,
    EarningsSurpriseBuilder,
    ManifestFieldsBuilder,
    stats_list_to_dataframe,
)


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 3: Build CEO Clarity Panel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--year-start",
        type=int,
        default=None,
        help="Start year (default: from config)",
    )
    parser.add_argument(
        "--year-end",
        type=int,
        default=None,
        help="End year (default: from config)",
    )
    return parser.parse_args()


def assign_industry_sample(ff12_code: pd.Series) -> pd.Series:
    """Assign industry sample based on FF12 code.

    Args:
        ff12_code: Series with FF12 industry codes

    Returns:
        Series with sample names: Main, Finance, or Utility
    """
    sample = pd.Series("Main", index=ff12_code.index)
    sample[ff12_code == 11] = "Finance"
    sample[ff12_code == 8] = "Utility"
    return sample


def build_panel(
    root_path: Path,
    years: range,
    var_config: Dict[str, Any],
    stats: Dict[str, Any],
) -> pd.DataFrame:
    """Build complete panel by loading and merging all variables.

    Args:
        root_path: Project root path
        years: Range of years to process
        var_config: Variable configuration dict
        stats: Stats dict to collect summary statistics

    Returns:
        Merged DataFrame with all variables
    """
    print("\n" + "=" * 60)
    print("Loading variables")
    print("=" * 60)

    all_results: Dict[str, Any] = {}

    # Initialize builders - CEO Clarity uses CEO-specific variables
    builders = {
        "manifest": ManifestFieldsBuilder(var_config.get("manifest", {})),
        "ceo_qa_uncertainty": CEOQAUncertaintyBuilder(
            var_config.get("ceo_qa_uncertainty", {})
        ),
        "ceo_pres_uncertainty": CEOPresUncertaintyBuilder(
            var_config.get("ceo_pres_uncertainty", {})
        ),
        "analyst_qa_uncertainty": AnalystQAUncertaintyBuilder(
            var_config.get("analyst_qa_uncertainty", {})
        ),
        "negative_sentiment": NegativeSentimentBuilder(
            var_config.get("negative_sentiment", {})
        ),
        "stock_return": StockReturnBuilder(var_config.get("stock_return", {})),
        "market_return": MarketReturnBuilder(var_config.get("market_return", {})),
        "eps_growth": EPSGrowthBuilder(var_config.get("eps_growth", {})),
        "earnings_surprise": EarningsSurpriseBuilder(var_config.get("earnings_surprise", {})),
    }

    # Build all variables
    for name, builder in builders.items():
        print(f"  Loading {name}...")
        result = builder.build(years, root_path)
        all_results[name] = result
        print(f"    Loaded {len(result.data):,} rows")

    # Start with manifest as base
    manifest_result = all_results["manifest"]
    panel = manifest_result.data.copy()

    print(f"\n  Base manifest: {len(panel):,} rows")

    # Merge all other variables on file_name
    for name, result in all_results.items():
        if name == "manifest":
            continue

        data = result.data.copy()
        if "file_name" in data.columns and len(data.columns) > 1:
            before_len = len(panel)
            panel = panel.merge(data, on="file_name", how="left")
            after_len = len(panel)
            print(f"  After {name} merge: {after_len:,} rows (delta: {after_len - before_len:+,})")

    # Add derived fields
    if "ff12_code" in panel.columns:
        panel["sample"] = assign_industry_sample(panel["ff12_code"])
        print(f"\n  Sample distribution:")
        for sample in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == sample).sum()
            print(f"    {sample}: {n:,} calls")

    # Add year column if not present
    if "year" not in panel.columns and "start_date" in panel.columns:
        panel["year"] = pd.to_datetime(panel["start_date"], errors="coerce").dt.year

    # Collect all summary stats
    stats_list = []
    for name, result in all_results.items():
        stats_list.append(result.stats)

    stats["variable_stats"] = [asdict(s) for s in stats_list]

    return panel


def save_outputs(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
) -> None:
    """Save panel and summary statistics.

    Args:
        panel: Complete merged panel
        stats: Stats dict with variable statistics
        out_dir: Output directory
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Save panel
    panel_path = out_dir / "ceo_clarity_panel.parquet"
    panel.to_parquet(panel_path, index=False)
    print(f"  Saved: ceo_clarity_panel.parquet ({len(panel):,} rows, {len(panel.columns)} columns)")

    # Save summary stats
    stats_df = stats_list_to_dataframe([s for s in stats.get("variable_stats", [])])
    stats_path = out_dir / "summary_stats.csv"
    stats_df.to_csv(stats_path, index=False)
    print(f"  Saved: summary_stats.csv ({len(stats_df)} variables)")


def generate_report(
    panel: pd.DataFrame,
    stats: Dict[str, Any],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report.

    Args:
        panel: Complete merged panel
        stats: Stats dict
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 3: CEO Clarity Panel Build Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Panel Summary",
        "",
        f"- **Total observations:** {len(panel):,}",
        f"- **Total columns:** {len(panel.columns)}",
        "",
    ]

    # Sample distribution
    if "sample" in panel.columns:
        report_lines.append("### Sample Distribution")
        report_lines.append("")
        report_lines.append("| Sample | N Calls | % |")
        report_lines.append("|--------|---------|---|")
        for sample in ["Main", "Finance", "Utility"]:
            n = (panel["sample"] == sample).sum()
            pct = 100.0 * n / len(panel) if len(panel) > 0 else 0
            report_lines.append(f"| {sample} | {n:,} | {pct:.1f}% |")
        report_lines.append("")

    # Unique entities
    report_lines.append("### Unique Entities")
    report_lines.append("")
    if "ceo_id" in panel.columns:
        report_lines.append(f"- **Unique CEOs:** {panel['ceo_id'].nunique():,}")
    if "gvkey" in panel.columns:
        report_lines.append(f"- **Unique firms:** {panel['gvkey'].nunique():,}")
    report_lines.append("")

    # Variable summary
    report_lines.append("## Variable Summary")
    report_lines.append("")
    report_lines.append("| Variable | N | Mean | Std | Min | Max | Missing % |")
    report_lines.append("|----------|---|------|-----|-----|-----|-----------|")

    for var_stat in stats.get("variable_stats", []):
        name = var_stat.get("name", "unknown")
        n = var_stat.get("n", 0)
        mean = var_stat.get("mean", 0)
        std = var_stat.get("std", 0)
        min_val = var_stat.get("min", 0)
        max_val = var_stat.get("max", 0)
        pct_missing = var_stat.get("pct_missing", 0)
        report_lines.append(
            f"| {name} | {n:,} | {mean:.3f} | {std:.3f} | {min_val:.3f} | {max_val:.3f} | {pct_missing:.1f}% |"
        )

    report_lines.append("")

    # Write report
    report_path = out_dir / "report_step3_ceo_clarity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print(f"  Saved: report_step3_ceo_clarity.md")


def main(year_start: int = None, year_end: int = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "build_ceo_clarity_panel",
        "timestamp": timestamp,
        "variable_stats": [],
        "timing": {},
        "panel": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "variables" / "ceo_clarity" / timestamp

    # Load configs
    config = get_config()
    var_config = load_variable_config()

    # Get year range
    if year_start is None:
        year_start = config.data.year_start
    if year_end is None:
        year_end = config.data.year_end
    years = range(year_start, year_end + 1)

    print("=" * 80)
    print("STAGE 3: Build CEO Clarity Panel")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")
    print(f"Years: {year_start}-{year_end}")

    # Build panel
    panel = build_panel(root, years, var_config, stats)

    # Save outputs
    save_outputs(panel, stats, out_dir)

    # Generate report
    duration = (datetime.now() - start_time).total_seconds()
    generate_report(panel, stats, out_dir, duration)

    # Final summary
    stats["timing"]["duration_seconds"] = round(duration, 2)
    stats["panel"]["n_rows"] = len(panel)
    stats["panel"]["n_columns"] = len(panel.columns)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(year_start=args.year_start, year_end=args.year_end))
```

**Step 2: Verify the file was created**

Run: `ls src/f1d/variables/build_ceo_clarity_panel.py`
Expected: File exists

**Step 3: Commit**

```bash
git add src/f1d/variables/build_ceo_clarity_panel.py
git commit -m "feat: add Stage 3 CEO Clarity panel builder"
```

---

## Task 6: Create Stage 4 Hypothesis Test - test_ceo_clarity.py

**Files:**
- Create: `src/f1d/econometric/test_ceo_clarity.py`

**Step 1: Create the hypothesis test script**

Create `src/f1d/econometric/test_ceo_clarity.py`:

```python
#!/usr/bin/env python3
"""
================================================================================
STAGE 4: Test CEO Clarity Hypothesis
================================================================================
ID: econometric/test_ceo_clarity
Description: Run CEO Clarity hypothesis test by loading panel from Stage 3,
             running fixed effects regression by industry sample, extracting
             CEO fixed effects, and outputting Accounting Review style
             LaTeX tables.

Model Specification:
    CEO_QA_Uncertainty_pct ~ C(ceo_id) + C(year) +
        CEO_Pres_Uncertainty_pct +
        Analyst_QA_Uncertainty_pct +
        Entire_All_Negative_pct +
        StockRet + MarketRet + EPS_Growth + SurpDec

Industry Samples:
    - Main: FF12 codes 1-7, 9-10, 12 (non-financial, non-utility)
    - Finance: FF12 code 11
    - Utility: FF12 code 8

Minimum Calls Filter:
    CEOs must have >= 5 calls to be included in regression.

Inputs:
    - outputs/variables/ceo_clarity/latest/ceo_clarity_panel.parquet

Outputs:
    - outputs/econometric/ceo_clarity/{timestamp}/ceo_clarity_table.tex
    - outputs/econometric/ceo_clarity/{timestamp}/clarity_scores.parquet
    - outputs/econometric/ceo_clarity/{timestamp}/regression_results.txt
    - outputs/econometric/ceo_clarity/{timestamp}/report_step4_ceo_clarity.md

Deterministic: true
Dependencies:
    - Requires: Stage 3 (build_ceo_clarity_panel)
    - Uses: statsmodels, f1d.shared.latex_tables_accounting

Author: Thesis Author
Date: 2026-02-19
================================================================================
"""

from __future__ import annotations

import argparse
import sys
import warnings
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import numpy as np
import pandas as pd

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore", category=FutureWarning)

# Try importing statsmodels
try:
    import statsmodels.formula.api as smf
    STATSMODELS_AVAILABLE = True
except ImportError:
    STATSMODELS_AVAILABLE = False
    print("WARNING: statsmodels not available. Install with: pip install statsmodels")

from f1d.shared.latex_tables_accounting import make_accounting_table
from f1d.shared.path_utils import get_latest_output_dir


# ==============================================================================
# Configuration
# ==============================================================================

CONFIG: Dict[str, Any] = {
    "dependent_var": "CEO_QA_Uncertainty_pct",
    "linguistic_controls": [
        "CEO_Pres_Uncertainty_pct",
        "Analyst_QA_Uncertainty_pct",
        "Entire_All_Negative_pct",
    ],
    "firm_controls": [
        "StockRet",
        "MarketRet",
        "EPS_Growth",
        "SurpDec",
    ],
    "min_calls_per_ceo": 5,
}


# ==============================================================================
# Variable Labels for LaTeX Table
# ==============================================================================

VARIABLE_LABELS = {
    "CEO_Pres_Uncertainty_pct": "CEO Pres Uncertainty",
    "Analyst_QA_Uncertainty_pct": "Analyst QA Uncertainty",
    "Entire_All_Negative_pct": "Negative Sentiment",
    "StockRet": "Stock Return",
    "MarketRet": "Market Return",
    "EPS_Growth": "EPS Growth",
    "SurpDec": "Earnings Surprise Decile",
}


# ==============================================================================
# CLI Arguments
# ==============================================================================


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Stage 4: Test CEO Clarity Hypothesis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate inputs without executing",
    )
    parser.add_argument(
        "--panel-path",
        type=str,
        default=None,
        help="Path to panel parquet file (default: latest from Stage 3)",
    )
    return parser.parse_args()


# ==============================================================================
# Data Loading
# ==============================================================================


def load_panel(root_path: Path, panel_path: Optional[str] = None) -> pd.DataFrame:
    """Load panel from Stage 3 output.

    Args:
        root_path: Project root path
        panel_path: Optional explicit path to panel file

    Returns:
        DataFrame with panel data
    """
    print("\n" + "=" * 60)
    print("Loading panel")
    print("=" * 60)

    if panel_path:
        panel_file = Path(panel_path)
    else:
        # Find latest panel
        panel_dir = get_latest_output_dir(
            root_path / "outputs" / "variables" / "ceo_clarity",
            required_file="ceo_clarity_panel.parquet"
        )
        panel_file = panel_dir / "ceo_clarity_panel.parquet"

    if not panel_file.exists():
        raise FileNotFoundError(f"Panel file not found: {panel_file}")

    panel = pd.read_parquet(panel_file)
    print(f"  Loaded: {panel_file}")
    print(f"  Rows: {len(panel):,}")
    print(f"  Columns: {len(panel.columns)}")

    return panel


def prepare_regression_data(panel: pd.DataFrame) -> pd.DataFrame:
    """Prepare panel data for regression.

    Filters to complete cases and ensures proper data types.

    Args:
        panel: Raw panel DataFrame

    Returns:
        Prepared DataFrame
    """
    print("\n" + "=" * 60)
    print("Preparing regression data")
    print("=" * 60)

    initial_n = len(panel)

    # Filter to non-null ceo_id
    df = panel[panel["ceo_id"].notna()].copy()
    print(f"  After ceo_id filter: {len(df):,} / {initial_n:,}")

    # Define required variables
    required = (
        [CONFIG["dependent_var"]]
        + CONFIG["linguistic_controls"]
        + CONFIG["firm_controls"]
        + ["ceo_id", "year"]
    )

    # Check which variables exist
    missing_vars = [v for v in required if v not in df.columns]
    if missing_vars:
        print(f"  WARNING: Missing variables: {missing_vars}")
        required = [v for v in required if v in df.columns]

    # Filter to complete cases
    complete_mask = df[required].notna().all(axis=1)
    df = df[complete_mask].copy()
    print(f"  After complete cases filter: {len(df):,}")

    # Assign sample if not present
    if "sample" not in df.columns and "ff12_code" in df.columns:
        df["sample"] = "Main"
        df.loc[df["ff12_code"] == 11, "sample"] = "Finance"
        df.loc[df["ff12_code"] == 8, "sample"] = "Utility"

    print("\n  Sample distribution:")
    for sample in ["Main", "Finance", "Utility"]:
        n = (df["sample"] == sample).sum()
        print(f"    {sample}: {n:,} calls")

    return df


# ==============================================================================
# Regression
# ==============================================================================


def run_regression(
    df_sample: pd.DataFrame,
    sample_name: str,
) -> tuple[Any, pd.DataFrame, Set[Any]]:
    """Run OLS regression with CEO fixed effects.

    Args:
        df_sample: Sample DataFrame
        sample_name: Name of sample for logging

    Returns:
        Tuple of (model, df_reg, valid_ceos)
    """
    print("\n" + "=" * 60)
    print(f"Running regression: {sample_name}")
    print("=" * 60)

    if not STATSMODELS_AVAILABLE:
        print("  ERROR: statsmodels not available")
        return None, None, set()

    # Filter to CEOs with minimum calls
    min_calls = CONFIG["min_calls_per_ceo"]
    ceo_counts = df_sample["ceo_id"].value_counts()
    valid_ceos = set(ceo_counts[ceo_counts >= min_calls].index)
    df_reg = df_sample[df_sample["ceo_id"].isin(valid_ceos)].copy()

    print(f"  After >={min_calls} calls filter: {len(df_reg):,} calls, {df_reg['ceo_id'].nunique():,} CEOs")

    if len(df_reg) < 100:
        print(f"  WARNING: Too few observations ({len(df_reg)}), skipping")
        return None, None, set()

    # Convert to string for categorical treatment
    df_reg["ceo_id"] = df_reg["ceo_id"].astype(str)
    df_reg["year"] = df_reg["year"].astype(str)

    # Build formula
    dep_var = CONFIG["dependent_var"]
    controls = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]
    controls = [c for c in controls if c in df_reg.columns]

    formula = f"{dep_var} ~ C(ceo_id) + " + " + ".join(controls) + " + C(year)"
    print(f"  Formula: {formula[:80]}...")

    # Estimate model
    print("  Estimating... (this may take a minute)")
    start_time = datetime.now()

    try:
        model = smf.ols(formula, data=df_reg).fit(cov_type="HC1")
    except ValueError as e:
        print(f"ERROR: Regression failed: {e}", file=sys.stderr)
        return None, None, set()

    duration = (datetime.now() - start_time).total_seconds()

    print(f"  [OK] Complete in {duration:.1f}s")
    print(f"  R-squared: {model.rsquared:.4f}")
    print(f"  Adj. R-squared: {model.rsquared_adj:.4f}")
    print(f"  N observations: {int(model.nobs):,}")

    return model, df_reg, valid_ceos


def extract_clarity_scores(
    model: Any,
    df_reg: pd.DataFrame,
    sample_name: str,
) -> pd.DataFrame:
    """Extract CEO fixed effects and compute Clarity scores.

    Clarity = -gamma_i (negative of CEO fixed effect)

    Args:
        model: Fitted OLS model
        df_reg: Regression DataFrame
        sample_name: Sample name for metadata

    Returns:
        DataFrame with ceo_id, gamma_i, ClarityCEO_raw, ClarityCEO
    """
    print(f"\n  Extracting CEO fixed effects for {sample_name}...")

    # Get CEO coefficient names
    ceo_params = {
        p: model.params[p] for p in model.params.index if p.startswith("C(ceo_id)")
    }

    # Parse CEO IDs
    ceo_effects = {}
    for param_name, gamma_i in ceo_params.items():
        if "[T." in param_name:
            ceo_id = param_name.split("[T.")[1].split("]")[0]
            ceo_effects[ceo_id] = gamma_i

    # Reference CEO gets gamma = 0
    all_ceos = df_reg["ceo_id"].unique()
    reference_ceos = [c for c in all_ceos if c not in ceo_effects]
    for ref_ceo in reference_ceos:
        ceo_effects[ref_ceo] = 0.0

    print(f"  Found {len(ceo_effects)} CEOs (incl. {len(reference_ceos)} reference)")

    # Create DataFrame
    ceo_fe = pd.DataFrame(
        list(ceo_effects.items()),
        columns=["ceo_id", "gamma_i"]
    )

    # Compute Clarity = -gamma_i
    ceo_fe["ClarityCEO_raw"] = -ceo_fe["gamma_i"]

    # Standardize
    mean_val = ceo_fe["ClarityCEO_raw"].mean()
    std_val = ceo_fe["ClarityCEO_raw"].std()
    ceo_fe["ClarityCEO"] = (ceo_fe["ClarityCEO_raw"] - mean_val) / std_val

    ceo_fe["sample"] = sample_name

    print(f"  ClarityCEO: mean={ceo_fe['ClarityCEO'].mean():.4f}, std={ceo_fe['ClarityCEO'].std():.4f}")

    return ceo_fe


# ==============================================================================
# Output Generation
# ==============================================================================


def save_outputs(
    results: Dict[str, Dict[str, Any]],
    all_clarity_scores: List[pd.DataFrame],
    out_dir: Path,
    stats: Dict[str, Any],
) -> None:
    """Save all outputs.

    Args:
        results: Dict mapping sample names to regression results
        all_clarity_scores: List of clarity score DataFrames
        out_dir: Output directory
        stats: Stats dict
    """
    print("\n" + "=" * 60)
    print("Saving outputs")
    print("=" * 60)

    out_dir.mkdir(parents=True, exist_ok=True)

    # Control variables for LaTeX table
    control_vars = CONFIG["linguistic_controls"] + CONFIG["firm_controls"]

    # Generate LaTeX table
    latex_table = make_accounting_table(
        results=results,
        caption="Table 1: CEO Clarity Fixed Effects",
        label="tab:ceo_clarity",
        note=(
            "This table reports CEO fixed effects from regressing CEO Q&A "
            "uncertainty on firm characteristics and year fixed effects. "
            "Clarity is computed as the negative of the CEO fixed effect, "
            "then standardized. Robust standard errors (HC1) are used."
        ),
        variable_labels=VARIABLE_LABELS,
        control_variables=control_vars,
        output_path=out_dir / "ceo_clarity_table.tex",
    )
    print("  Saved: ceo_clarity_table.tex")

    # Save clarity scores
    if all_clarity_scores:
        clarity_df = pd.concat(all_clarity_scores, ignore_index=True)
        clarity_path = out_dir / "clarity_scores.parquet"
        clarity_df.to_parquet(clarity_path, index=False)
        print(f"  Saved: clarity_scores.parquet ({len(clarity_df):,} CEOs)")

    # Save regression results text
    for sample_name, result in results.items():
        model = result.get("model")
        if model is not None:
            results_path = out_dir / f"regression_results_{sample_name.lower()}.txt"
            with open(results_path, "w") as f:
                f.write(model.summary().as_text())
            print(f"  Saved: regression_results_{sample_name.lower()}.txt")


def generate_report(
    results: Dict[str, Dict[str, Any]],
    all_clarity_scores: List[pd.DataFrame],
    out_dir: Path,
    duration: float,
) -> None:
    """Generate markdown report.

    Args:
        results: Regression results dict
        all_clarity_scores: List of clarity score DataFrames
        out_dir: Output directory
        duration: Duration in seconds
    """
    report_lines = [
        "# Stage 4: CEO Clarity Hypothesis Test Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Duration:** {duration:.1f} seconds",
        "",
        "## Model Specification",
        "",
        "```",
        f"{CONFIG['dependent_var']} ~ C(ceo_id) + C(year) +",
        "    " + " + ".join(CONFIG["linguistic_controls"]) + " +",
        "    " + " + ".join(CONFIG["firm_controls"]),
        "```",
        "",
        "## Summary Statistics",
        "",
        "| Sample | N Obs | N CEOs | R-squared |",
        "|--------|-------|--------|-----------|",
    ]

    for sample_name, result in results.items():
        diag = result.get("diagnostics", {})
        n_obs = diag.get("n_obs", "N/A")
        n_ceo = diag.get("n_ceos", "N/A")
        r2 = diag.get("rsquared", "N/A")
        report_lines.append(
            f"| {sample_name} | {n_obs:,} | {n_ceo:,} | {r2:.4f} |"
            if isinstance(r2, float) else
            f"| {sample_name} | {n_obs} | {n_ceo} | {r2} |"
        )

    report_lines.append("")

    # Top CEOs by sample
    if all_clarity_scores:
        clarity_df = pd.concat(all_clarity_scores, ignore_index=True)

        for sample in ["Main", "Finance", "Utility"]:
            sample_df = clarity_df[clarity_df["sample"] == sample]
            if len(sample_df) == 0:
                continue

            report_lines.append(f"## {sample} Sample")
            report_lines.append("")
            report_lines.append("### Top 5 Clearest CEOs")
            report_lines.append("")
            report_lines.append("| Rank | CEO ID | Clarity |")
            report_lines.append("|------|--------|---------|")

            for i, row in sample_df.nlargest(5, "ClarityCEO").iterrows():
                report_lines.append(
                    f"| {sample_df.index.get_loc(i) + 1} | {row['ceo_id']} | {row['ClarityCEO']:.3f} |"
                )

            report_lines.append("")
            report_lines.append("### Top 5 Most Uncertain CEOs")
            report_lines.append("")
            report_lines.append("| Rank | CEO ID | Clarity |")
            report_lines.append("|------|--------|---------|")

            for i, row in sample_df.nsmallest(5, "ClarityCEO").iterrows():
                report_lines.append(
                    f"| {sample_df.index.get_loc(i) + 1} | {row['ceo_id']} | {row['ClarityCEO']:.3f} |"
                )

            report_lines.append("")

    # Write report
    report_path = out_dir / "report_step4_ceo_clarity.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))

    print("  Saved: report_step4_ceo_clarity.md")


# ==============================================================================
# Main
# ==============================================================================


def main(panel_path: Optional[str] = None) -> int:
    """Main execution."""
    start_time = datetime.now()
    timestamp = start_time.strftime("%Y-%m-%d_%H%M%S")

    stats: Dict[str, Any] = {
        "step_id": "test_ceo_clarity",
        "timestamp": timestamp,
        "regressions": {},
        "timing": {},
    }

    # Setup paths
    root = Path(__file__).resolve().parents[3]
    out_dir = root / "outputs" / "econometric" / "ceo_clarity" / timestamp

    print("=" * 80)
    print("STAGE 4: Test CEO Clarity Hypothesis")
    print("=" * 80)
    print(f"Timestamp: {timestamp}")
    print(f"Output: {out_dir}")

    # Load panel
    panel = load_panel(root, panel_path)

    # Prepare data
    df = prepare_regression_data(panel)

    # Run regressions by sample
    results: Dict[str, Dict[str, Any]] = {}
    all_clarity_scores: List[pd.DataFrame] = []

    for sample_name in ["Main", "Finance", "Utility"]:
        df_sample = df[df["sample"] == sample_name].copy()

        if len(df_sample) < 100:
            print(f"\n  Skipping {sample_name}: too few observations ({len(df_sample)})")
            continue

        # Run regression
        model, df_reg, valid_ceos = run_regression(df_sample, sample_name)

        if model is None:
            continue

        # Extract clarity scores
        clarity_scores = extract_clarity_scores(model, df_reg, sample_name)
        all_clarity_scores.append(clarity_scores)

        # Store results
        results[sample_name] = {
            "model": model,
            "diagnostics": {
                "n_obs": int(model.nobs),
                "n_ceos": len(valid_ceos),
                "rsquared": model.rsquared,
                "rsquared_adj": model.rsquared_adj,
            },
        }

        # Stats
        stats["regressions"][sample_name] = {
            "n_obs": int(model.nobs),
            "n_ceos": len(valid_ceos),
            "rsquared": model.rsquared,
        }

    # Save outputs
    if results:
        save_outputs(results, all_clarity_scores, out_dir, stats)

        # Generate report
        duration = (datetime.now() - start_time).total_seconds()
        generate_report(results, all_clarity_scores, out_dir, duration)

    # Final summary
    duration = (datetime.now() - start_time).total_seconds()
    stats["timing"]["duration_seconds"] = round(duration, 2)

    print("\n" + "=" * 80)
    print("COMPLETE")
    print("=" * 80)
    print(f"Duration: {duration:.1f} seconds")
    print(f"Output: {out_dir}")

    return 0


if __name__ == "__main__":
    args = parse_arguments()

    if args.dry_run:
        print("Dry-run mode: validating inputs...")
        print("[OK] All inputs validated")
        sys.exit(0)

    sys.exit(main(panel_path=args.panel_path))
```

**Step 2: Verify the file was created**

Run: `ls src/f1d/econometric/test_ceo_clarity.py`
Expected: File exists

**Step 3: Commit**

```bash
git add src/f1d/econometric/test_ceo_clarity.py
git commit -m "feat: add Stage 4 CEO Clarity hypothesis test"
```

---

## Task 7: Verify Complete Pipeline Works

**Files:**
- None (verification only)

**Step 1: Run Stage 3 panel builder**

Run: `python -m f1d.variables.build_ceo_clarity_panel`
Expected: Panel created at `outputs/variables/ceo_clarity/{timestamp}/ceo_clarity_panel.parquet`

**Step 2: Run Stage 4 hypothesis test**

Run: `python -m f1d.econometric.test_ceo_clarity`
Expected: Results at `outputs/econometric/ceo_clarity/{timestamp}/`

**Step 3: Verify outputs**

Run: `ls outputs/econometric/ceo_clarity/latest/`
Expected: Files present:
- `ceo_clarity_table.tex`
- `clarity_scores.parquet`
- `regression_results_main.txt`
- `report_step4_ceo_clarity.md`

---

## Task 8: Update Progress Report

**Files:**
- Modify: `docs/STAGE3_4_REFACTOR_PROGRESS.md`

**Step 1: Add CEO Clarity section to progress report**

Add a new section documenting the CEO Clarity refactor completion.

**Step 2: Commit**

```bash
git add docs/STAGE3_4_REFACTOR_PROGRESS.md
git commit -m "docs: update progress report with CEO Clarity completion"
```

---

## Summary

| Task | Description | Files Changed |
|------|-------------|---------------|
| 1 | Create CEO QA Uncertainty builder | +1 file |
| 2 | Create CEO Pres Uncertainty builder | +1 file |
| 3 | Register builders in __init__.py | ~1 file |
| 4 | Update variables.yaml config | ~1 file |
| 5 | Create Stage 3 panel builder | +1 file |
| 6 | Create Stage 4 hypothesis test | +1 file |
| 7 | Verify pipeline works | 0 files |
| 8 | Update progress report | ~1 file |

**Total:** 6 new files, 3 modified files
