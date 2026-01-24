---
phase: 04-financial-econometric
plan: 01
type: execute
wave: 1
depends_on: ["03-text-processing"]
files_modified: []
autonomous: true

must_haves:
  truths:
    - "stats.json exists in each timestamped output directory (Step 3 and Step 4 scripts)"
    - "stats.json files are valid JSON (parseable)"
    - "stats.json contains financial and econometric metrics"
    - "Panel balance diagnostics included"
    - "Correlation matrix exported as CSV"
    - "Descriptive statistics (N, Mean, SD, Min, P25, Median, P75, Max) available"
    - "Merge diagnostics captured for all Step 3 scripts"
    - "Regression diagnostics captured for all Step 4 scripts"
    - "Console output matches log file content"
    - "Summary tables display correctly with formatted numbers"
  artifacts:
    - path: "4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json"
      provides: "Financial feature construction metrics and merge diagnostics"
    - path: "4_Outputs/3.1_FirmControls/latest/stats.json"
      provides: "Firm control variable statistics"
    - path: "4_Outputs/3.2_MarketVariables/latest/stats.json"
      provides: "Market variable statistics"
    - path: "4_Outputs/3.3_EventFlags/latest/stats.json"
      provides: "Event flag statistics"
    - path: "4_Outputs/4.1_EstimateCeoClarity/latest/stats.json"
      provides: "CEO clarity estimation metrics and regression diagnostics"
    - path: "4_Outputs/4.2_LiquidityRegressions/latest/stats.json"
      provides: "Liquidity regression metrics"
    - path: "4_Outputs/4.3_TakeoverHazards/latest/stats.json"
      provides: "Takeover hazard regression metrics"
    - path: "4_Outputs/final_summary_statistics/descriptive_stats.csv"
      provides: "Descriptive statistics (SUMM-01)"
    - path: "4_Outputs/final_summary_statistics/correlation_matrix.csv"
      provides: "Correlation matrix (SUMM-02)"
    - path: "4_Outputs/final_summary_statistics/panel_balance.csv"
      provides: "Panel balance diagnostics (SUMM-03)"
  key_links:
    - from: "stats.json (Step 3 scripts)"
      to: "STAT-01-09 + financial-specific"
      via: "field validation"
      pattern: "merge_diagnostics|financial_features|panel_balance"
    - from: "stats.json (Step 4 scripts)"
      to: "STAT-01-09 + econometric-specific"
      via: "field validation"
      pattern: "regression_diagnostics|model_fit|residuals|liquidity|hazards"
    - from: "descriptive_stats.csv"
      to: "SUMM-01"
      via: "CSV format"
      pattern: "N|Mean|SD|Min|P25|Median|P75|Max"
    - from: "correlation_matrix.csv"
      to: "SUMM-02"
      via: "CSV format"
      pattern: "correlation"
    - from: "panel_balance.csv"
      to: "SUMM-03"
      via: "CSV format"
      pattern: "panel|balance|t|firms|observations"
---

<objective>
Roll out the statistics pattern (STAT-01-12) to all Steps 3-4 scripts with financial and econometric metrics and generate final dataset summary statistics.

Purpose: Apply the validated statistics framework from Phase 1 and 3 to Steps 3-4 scripts, adding domain-specific metrics for financial features, econometric models, and panel data. Generate comprehensive summary statistics for the final dataset.

Output: Updated Steps 3-4 scripts with inline statistics, producing stats.json files with financial and econometric metrics, plus CSV exports of descriptive statistics, correlation matrix, and panel balance diagnostics.
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
@.planning/phases/03-text-processing/SUMMARY.md
</context>

<tasks>

<task type="auto">
  <name>Task 1: Add inline stats helpers to 3.0_BuildFinancialFeatures.py</name>
  <files>2_Scripts/3.0_BuildFinancialFeatures.py</files>
  <action>
Apply the inline statistics pattern to 3.0_BuildFinancialFeatures.py with financial feature metrics and merge diagnostics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture financial feature construction metrics:
     - Merge success rates (rows before/after each merge)
     - Key preservation rate (firms retained after merges)
     - Financial feature distributions (market cap, book-to-market, leverage, etc.)
     - Feature completion rates
     - Panel balance metrics
     - Merge conflict diagnostics

3. **Integration points:**
   - Record input checksums after loading source data
   - Track merge timing for each data source
   - Calculate row counts before/after each merge
   - Compute distributions for each financial feature
   - Identify missing data patterns post-merge
   - Calculate panel balance metrics
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "3.0_BuildFinancialFeatures",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "source_databases": ["CRSP", "Compustat", "Execucomp"],
    "initial_firms": int,
    "initial_obs": int
  },
  "processing": {
    "merges": {
      "merge_1": {
        "source": "...",
        "rows_before": int,
        "rows_after": int,
        "rows_lost": int,
        "rows_lost_percent": float,
        "key_columns": [...],
        "merge_type": "inner/left/right"
      },
      ...
    },
    "financial_features": {
      "feature_name": {
        "n": int,
        "mean": float,
        "std": float,
        "min": float,
        "p25": float,
        "median": float,
        "p75": float,
        "max": float,
        "missing_count": int,
        "missing_percent": float
      },
      ...
    },
    "panel_balance": {
      "total_firms": int,
      "total_observations": int,
      "years": int,
      "avg_observations_per_firm": float,
      "min_observations_per_firm": int,
      "max_observations_per_firm": int,
      "firms_with_complete_data": int,
      "complete_data_percent": float
    },
    "merge_diagnostics": {
      "total_merges": int,
      "successful_merges": int,
      "failed_merges": 0,
      "key_preservation_rate": float,
      "data_loss_rate": float,
      "duplicate_keys_found": int
    },
    "feature_completion_rates": {
      "feature_name": float,
      ...
    }
  },
  "output": {
    "files": [...],
    "final_firms": int,
    "final_obs": int,
    "features_added": int
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
  Script runs successfully and produces stats.json with all required financial feature and merge metrics.
  </verify>
  <done>
  3.0_BuildFinancialFeatures.py updated with inline stats helpers and produces stats.json with financial feature metrics.
  </done>
</task>

<task type="auto">
  <name>Task 2: Add inline stats helpers to 3.1_FirmControls.py</name>
  <files>2_Scripts/3.1_FirmControls.py</files>
  <action>
Apply the inline statistics pattern to 3.1_FirmControls.py with firm control metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture firm control variable metrics:
     - Control variable distributions (size, age, profitability, etc.)
     - Variable construction success rates
     - Outlier detection for controls
     - Correlation summaries among controls
     - Missing data patterns

3. **Integration points:**
   - Record input checksums after loading financial features
   - Track control variable construction timing
   - Calculate distributions for each control variable
   - Identify outliers using IQR or z-score methods
   - Compute correlation matrix for controls
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "3.1_FirmControls",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_firms": int,
    "total_obs": int
  },
  "processing": {
    "controls_constructed": [...],
    "control_distributions": {
      "control_name": {
        "n": int,
        "mean": float,
        "std": float,
        "min": float,
        "p25": float,
        "median": float,
        "p75": float,
        "max": float,
        "missing_count": int,
        "missing_percent": float
      },
      ...
    },
    "outliers": {
      "control_name": {
        "outlier_count": int,
        "outlier_percent": float,
        "method": "IQR|zscore",
        "threshold": float
      },
      ...
    },
    "control_correlations": {
      "control_pair": float,
      ...
    },
    "construction_success": {
      "total_controls": int,
      "successfully_constructed": int,
      "failed": 0
    }
  },
  "output": {
    "files": [...],
    "controls_added": int,
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
  Script runs successfully and produces stats.json with all required firm control metrics.
  </verify>
  <done>
  3.1_FirmControls.py updated with inline stats helpers and produces stats.json with firm control metrics.
  </done>
</task>

<task type="auto">
  <name>Task 3: Add inline stats helpers to 3.2_MarketVariables.py</name>
  <files>2_Scripts/3.2_MarketVariables.py</files>
  <action>
Apply the inline statistics pattern to 3.2_MarketVariables.py with market variable metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture market variable metrics:
     - Market variable distributions (returns, volatility, trading volume, etc.)
     - Market-wide summary statistics (index returns, market volatility)
     - Variable construction success rates
     - Cross-sectional distributions
     - Time-series trends

3. **Integration points:**
   - Record input checksums after loading market data
   - Track market variable construction timing
   - Calculate distributions for each market variable
   - Compute market-wide aggregates
   - Document time-series properties
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "3.2_MarketVariables",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_firms": int,
    "total_obs": int,
    "date_range": {"start": "...", "end": "..."}
  },
  "processing": {
    "market_variables": {
      "variable_name": {
        "n": int,
        "mean": float,
        "std": float,
        "min": float,
        "p25": float,
        "median": float,
        "p75": float,
        "max": float,
        "missing_count": int,
        "missing_percent": float
      },
      ...
    },
    "market_wide": {
      "average_market_return": float,
      "market_volatility": float,
      "trading_volume_avg": float,
      "number_of_trading_days": int
    },
    "time_series_properties": {
      "returns_autocorrelation": float,
      "volatility_clustering": bool,
      "stationarity_test": {...}
    },
    "construction_success": {
      "total_variables": int,
      "successfully_constructed": int,
      "failed": 0
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
  Script runs successfully and produces stats.json with all required market variable metrics.
  </verify>
  <done>
  3.2_MarketVariables.py updated with inline stats helpers and produces stats.json with market variable metrics.
  </done>
</task>

<task type="auto">
  <name>Task 4: Add inline stats helpers to 3.3_EventFlags.py</name>
  <files>2_Scripts/3.3_EventFlags.py</files>
  <action>
Apply the inline statistics pattern to 3.3_EventFlags.py with event flag metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture event flag metrics:
     - Event occurrence counts by type
     - Event frequency statistics
     - Cross-sectional distribution of events
     - Time-series patterns in events
     - Overlap analysis (if multiple events)
     - Event clustering detection

3. **Integration points:**
   - Record input checksums after loading event data
   - Track event flag construction timing
   - Count events by type and period
   - Calculate event frequencies
   - Analyze event distributions
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "3.3_EventFlags",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_firms": int,
    "total_obs": int
  },
  "processing": {
    "event_flags": {
      "flag_name": {
        "total_events": int,
        "firms_affected": int,
        "event_frequency": float,
        "events_per_100_observations": float,
        "concentration": {"top_10_percent": float, "top_25_percent": float},
        "time_series": {"has_trend": bool, "clustering_detected": bool}
      },
      ...
    },
    "event_overlaps": {
      "overlap_matrix": {...},
      "simultaneous_events": int
    },
    "event_distribution": {
      "firms_with_no_events": int,
      "firms_with_one_event": int,
      "firms_with_multiple_events": int
    },
    "construction_success": {
      "total_flags": int,
      "successfully_constructed": int,
      "failed": 0
    }
  },
  "output": {
    "files": [...],
    "flags_added": int,
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
  Script runs successfully and produces stats.json with all required event flag metrics.
  </verify>
  <done>
  3.3_EventFlags.py updated with inline stats helpers and produces stats.json with event flag metrics.
  </done>
</task>

<task type="auto">
  <name>Task 5: Add inline stats helpers to 4.1_EstimateCeoClarity.py (main script)</name>
  <files>2_Scripts/4.1_EstimateCeoClarity.py</files>
  <action>
Apply the inline statistics pattern to 4.1_EstimateCeoClarity.py with regression and estimation metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture regression estimation metrics:
     - Model specification details
     - Sample size and coverage
     - Regression coefficients and statistics
     - Model fit statistics (R-squared, adjusted R-squared, F-statistic)
     - Residual diagnostics
     - Multicollinearity diagnostics (VIF)
     - Influence diagnostics (leverage, Cook's distance)

3. **Integration points:**
   - Record input checksums after loading estimation data
   - Track estimation timing
   - Capture model specification
   - Extract regression coefficients and statistics
   - Compute model fit measures
   - Run residual diagnostics
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "4.1_EstimateCeoClarity",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_obs": int,
    "estimation_sample": int
  },
  "processing": {
    "model_specification": {
      "dependent_variable": "...",
      "independent_variables": [...],
      "controls": [...],
      "fixed_effects": [...],
      "estimation_method": "OLS|FE|RE|IV|GMM",
      "clustering": [...]
    },
    "regression_results": {
      "n_obs": int,
      "n_firms": int,
      "r_squared": float,
      "adjusted_r_squared": float,
      "f_statistic": float,
      "f_p_value": float,
      "coefficients": {
        "variable_name": {
          "estimate": float,
          "std_error": float,
          "t_statistic": float,
          "p_value": float,
          "ci_lower": float,
          "ci_upper": float
        },
        ...
      }
    },
    "model_diagnostics": {
      "residuals": {
        "mean": float,
        "std": float,
        "skewness": float,
        "kurtosis": float,
        "normality_test": {...}
      },
      "multicollinearity": {
        "max_vif": float,
        "avg_vif": float,
        "variables_high_vif": [...]
      },
      "influence": {
        "high_leverage_points": int,
        "high_cooks_distance": int
      }
    }
  },
  "output": {
    "files": [...],
    "estimated_coefficients": int,
    "predictions_generated": bool
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
  Script runs successfully and produces stats.json with all required regression metrics.
  </verify>
  <done>
  4.1_EstimateCeoClarity.py updated with inline stats helpers and produces stats.json with regression metrics.
  </done>
</task>

<task type="auto">
  <name>Task 6: Add inline stats helpers to 4.2_LiquidityRegressions.py</name>
  <files>2_Scripts/4.2_LiquidityRegressions.py</files>
  <action>
Apply the inline statistics pattern to 4.2_LiquidityRegressions.py with liquidity regression metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
import statsmodels.api as sm
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture liquidity regression metrics:
     - Liquidity measure distributions
     - Multiple model specifications (if applicable)
     - Sample size for each specification
     - Model fit statistics for each specification
     - Liquidity-related coefficient significance
     - Robustness check results

3. **Integration points:**
   - Record input checksums after loading liquidity data
   - Track regression estimation timing
   - Compute liquidity measure statistics
   - Capture results for each specification
   - Document robustness checks
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "4.2_LiquidityRegressions",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_obs": int,
    "liquidity_measures": [...]
  },
  "processing": {
    "liquidity_measures": {
      "measure_name": {
        "n": int,
        "mean": float,
        "std": float,
        "min": float,
        "p25": float,
        "median": float,
        "p75": float,
        "max": float,
        "missing_count": int,
        "missing_percent": float
      },
      ...
    },
    "regression_specifications": {
      "specification_1": {
        "dependent_variable": "...",
        "independent_variables": [...],
        "n_obs": int,
        "r_squared": float,
        "adjusted_r_squared": float,
        "f_statistic": float,
        "liquidity_coefficient": float,
        "liquidity_t_stat": float,
        "liquidity_p_value": float
      },
      ...
    },
    "robustness_checks": {
      "alternative_measures": int,
      "alternative_specifications": int,
      "results_consistent": bool
    }
  },
  "output": {
    "files": [...],
    "specifications_estimated": int,
    "liquidity_effects_documented": bool
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
  Script runs successfully and produces stats.json with all required liquidity regression metrics.
  </verify>
  <done>
  4.2_LiquidityRegressions.py updated with inline stats helpers and produces stats.json with liquidity regression metrics.
  </done>
</task>

<task type="auto">
  <name>Task 7: Add inline stats helpers to 4.3_TakeoverHazards.py</name>
  <files>2_Scripts/4.3_TakeoverHazards.py</files>
  <action>
Apply the inline statistics pattern to 4.3_TakeoverHazards.py with hazard model metrics:

1. **Add imports for stats helpers:**
```python
import time
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd
from lifelines import CoxPHFitter
import statsmodels.api as sm
```

2. **Create StatsHelper class inline:**
   - Track input file checksums
   - Record start/end timestamps
   - Capture hazard model metrics:
     - Event occurrence statistics (takeovers)
     - Survival analysis sample size
     - Censoring statistics
     - Hazard model coefficients
     - Model fit statistics (log-likelihood, AIC, BIC)
     - Baseline hazard characteristics
     - Proportional hazards assumption tests

3. **Integration points:**
   - Record input checksums after loading takeover data
   - Track hazard model estimation timing
   - Compute event occurrence statistics
   - Capture censoring information
   - Extract model coefficients and fit statistics
   - Test proportional hazards assumption
   - Write stats.json to output directory before script completion

4. **Metrics to capture:**
```python
{
  "step_id": "4.3_TakeoverHazards",
  "timestamp": "...",
  "input": {
    "files": ["..."],
    "checksums": {...},
    "total_firms": int,
    "total_observations": int
  },
  "processing": {
    "event_statistics": {
      "total_takeovers": int,
      "takeover_rate": float,
      "firms_taken_over": int,
      "censored_observations": int,
      "censoring_rate": float
    },
    "hazard_model": {
      "estimation_method": "CoxPH|Weibull|LogNormal",
      "n_obs": int,
      "n_events": int,
      "log_likelihood": float,
      "aic": float,
      "bic": float,
      "concordance": float,
      "coefficients": {
        "variable_name": {
          "estimate": float,
          "std_error": float,
          "z_statistic": float,
          "p_value": float,
          "hazard_ratio": float,
          "ci_lower": float,
          "ci_upper": float
        },
        ...
      }
    },
    "model_diagnostics": {
      "proportional_hazards_test": {
        "test_statistic": float,
        "p_value": float,
        "assumption_holds": bool
      },
      "baseline_hazard": {
        "shape": "...",
        "mean": float,
        "std": float
      }
    }
  },
  "output": {
    "files": [...],
    "hazard_coefficients": int,
    "baseline_hazard_estimated": bool
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
  Script runs successfully and produces stats.json with all required hazard model metrics.
  </verify>
  <done>
  4.3_TakeoverHazards.py updated with inline stats helpers and produces stats.json with hazard model metrics.
  </done>
</task>

<task type="auto">
  <name>Task 8: Run all Step 3 scripts and verify stats.json</name>
  <files></files>
  <action>
Execute all Step 3 scripts and validate their stats.json outputs:

1. **Run scripts in sequence:**
```bash
python 2_Scripts/3.0_BuildFinancialFeatures.py
python 2_Scripts/3.1_FirmControls.py
python 2_Scripts/3.2_MarketVariables.py
python 2_Scripts/3.3_EventFlags.py
```

2. **Verify stats.json files exist:**
```bash
ls -la 4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json
ls -la 4_Outputs/3.1_FirmControls/latest/stats.json
ls -la 4_Outputs/3.2_MarketVariables/latest/stats.json
ls -la 4_Outputs/3.3_EventFlags/latest/stats.json
```

3. **Validate JSON syntax for all files:**
```bash
python -c "import json; json.load(open('4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json')); print('3.0: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/3.1_FirmControls/latest/stats.json')); print('3.1: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/3.2_MarketVariables/latest/stats.json')); print('3.2: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/3.3_EventFlags/latest/stats.json')); print('3.3: Valid JSON')"
```

4. **Check required fields for 3.0:**
```python
import json

with open('4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json') as f:
    stats = json.load(f)

required_keys = ['step_id', 'timestamp', 'input', 'processing', 'output', 'timing', 'missing_values']
for key in required_keys:
    assert key in stats, f"3.0 Missing key: {key}"

assert 'merges' in stats['processing'], "3.0 Missing processing.merges"
assert 'financial_features' in stats['processing'], "3.0 Missing processing.financial_features"
assert 'panel_balance' in stats['processing'], "3.0 Missing processing.panel_balance"
assert 'merge_diagnostics' in stats['processing'], "3.0 Missing processing.merge_diagnostics"

print("3.0 stats.json: All required fields present")
```

5. **Check required fields for 3.1, 3.2, 3.3:**
```python
scripts = ['3.1_FirmControls', '3.2_MarketVariables', '3.3_EventFlags']
for script in scripts:
    with open(f'4_Outputs/{script}/latest/stats.json') as f:
        stats = json.load(f)
    assert script in stats['step_id'], f"{script} step_id mismatch"
    assert 'control_distributions' in stats['processing'] or 'market_variables' in stats['processing'] or 'event_flags' in stats['processing'], f"{script} Missing domain-specific metrics"
    print(f"{script} stats.json: All required fields present")
```

6. **Verify panel balance metrics in 3.0:**
```python
with open('4_Outputs/3.0_BuildFinancialFeatures/latest/stats.json') as f:
    stats = json.load(f)

panel_balance = stats['processing']['panel_balance']
assert 'total_firms' in panel_balance, "3.0 Missing panel_balance.total_firms"
assert 'total_observations' in panel_balance, "3.0 Missing panel_balance.total_observations"
assert 'avg_observations_per_firm' in panel_balance, "3.0 Missing panel_balance.avg_observations_per_firm"

print("3.0 panel_balance metrics verified")
```
  </action>
  <verify>
  All four Step 3 scripts run successfully and produce valid stats.json files with required financial and event metrics.
  </verify>
  <done>
  All Step 3 scripts executed successfully with complete statistics outputs.
  </done>
</task>

<task type="auto">
  <name>Task 9: Run all Step 4 scripts and verify stats.json</name>
  <files></files>
  <action>
Execute all Step 4 scripts and validate their stats.json outputs:

1. **Run scripts in sequence:**
```bash
python 2_Scripts/4.1_EstimateCeoClarity.py
python 2_Scripts/4.2_LiquidityRegressions.py
python 2_Scripts/4.3_TakeoverHazards.py
```

2. **Verify stats.json files exist:**
```bash
ls -la 4_Outputs/4.1_EstimateCeoClarity/latest/stats.json
ls -la 4_Outputs/4.2_LiquidityRegressions/latest/stats.json
ls -la 4_Outputs/4.3_TakeoverHazards/latest/stats.json
```

3. **Validate JSON syntax for all files:**
```bash
python -c "import json; json.load(open('4_Outputs/4.1_EstimateCeoClarity/latest/stats.json')); print('4.1: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/4.2_LiquidityRegressions/latest/stats.json')); print('4.2: Valid JSON')"
python -c "import json; json.load(open('4_Outputs/4.3_TakeoverHazards/latest/stats.json')); print('4.3: Valid JSON')"
```

4. **Check required fields for 4.1:**
```python
import json

with open('4_Outputs/4.1_EstimateCeoClarity/latest/stats.json') as f:
    stats = json.load(f)

required_keys = ['step_id', 'timestamp', 'input', 'processing', 'output', 'timing', 'missing_values']
for key in required_keys:
    assert key in stats, f"4.1 Missing key: {key}"

assert 'model_specification' in stats['processing'], "4.1 Missing processing.model_specification"
assert 'regression_results' in stats['processing'], "4.1 Missing processing.regression_results"
assert 'model_diagnostics' in stats['processing'], "4.1 Missing processing.model_diagnostics"

print("4.1 stats.json: All required fields present")
```

5. **Check required fields for 4.2 and 4.3:**
```python
scripts = {'4.2_LiquidityRegressions': 'liquidity_measures', '4.3_TakeoverHazards': 'event_statistics'}
for script, required_metric in scripts.items():
    with open(f'4_Outputs/{script}/latest/stats.json') as f:
        stats = json.load(f)
    assert script in stats['step_id'], f"{script} step_id mismatch"
    assert required_metric in stats['processing'], f"{script} Missing processing.{required_metric}"
    print(f"{script} stats.json: All required fields present")
```

6. **Verify regression diagnostics in 4.1:**
```python
with open('4_Outputs/4.1_EstimateCeoClarity/latest/stats.json') as f:
    stats = json.load(f)

regression_results = stats['processing']['regression_results']
assert 'n_obs' in regression_results, "4.1 Missing regression_results.n_obs"
assert 'r_squared' in regression_results, "4.1 Missing regression_results.r_squared"
assert 'f_statistic' in regression_results, "4.1 Missing regression_results.f_statistic"
assert 'coefficients' in regression_results, "4.1 Missing regression_results.coefficients"

model_diagnostics = stats['processing']['model_diagnostics']
assert 'residuals' in model_diagnostics, "4.1 Missing model_diagnostics.residuals"
assert 'multicollinearity' in model_diagnostics, "4.1 Missing model_diagnostics.multicollinearity"

print("4.1 regression diagnostics verified")
```
  </action>
  <verify>
  All three Step 4 scripts run successfully and produce valid stats.json files with required econometric and regression metrics.
  </verify>
  <done>
  All Step 4 scripts executed successfully with complete statistics outputs.
  </done>
</task>

<task type="auto">
  <name>Task 10: Generate final descriptive statistics (SUMM-01)</name>
  <files></files>
  <action>
Generate comprehensive descriptive statistics for the final dataset:

1. **Create descriptive statistics script:**
```python
import pandas as pd
import numpy as np
from pathlib import Path

# Load final dataset
final_df = pd.read_csv('4_Outputs/final_dataset.csv')

# Select key variables for summary statistics
key_variables = [
    'ceo_clarity',
    'firm_size',
    'market_to_book',
    'leverage',
    'profitability',
    'liquidity',
    'volatility',
    'takeover_hazard'
]

# Calculate descriptive statistics (SUMM-01)
desc_stats = final_df[key_variables].describe(percentiles=[.25, .5, .75]).T
desc_stats = desc_stats[['count', 'mean', 'std', 'min', '25%', '50%', '75%', 'max']]
desc_stats.columns = ['N', 'Mean', 'SD', 'Min', 'P25', 'Median', 'P75', 'Max']

# Round to appropriate precision
desc_stats = desc_stats.round(4)

# Export to CSV
output_dir = Path('4_Outputs/final_summary_statistics')
output_dir.mkdir(parents=True, exist_ok=True)
desc_stats.to_csv(output_dir / 'descriptive_stats.csv')

print(f"Descriptive statistics exported to {output_dir / 'descriptive_stats.csv'}")
```

2. **Create output directory:**
```bash
mkdir -p 4_Outputs/final_summary_statistics
```

3. **Run descriptive statistics script:**
```bash
python 2_Scripts/generate_descriptive_stats.py
```

4. **Verify output:**
```bash
cat 4_Outputs/final_summary_statistics/descriptive_stats.csv
```
  </action>
  <verify>
  Descriptive statistics CSV exists with columns N, Mean, SD, Min, P25, Median, P75, Max for key variables.
  </verify>
  <done>
  Descriptive statistics (SUMM-01) generated and exported as CSV.
  </done>
</task>

<task type="auto">
  <name>Task 11: Generate correlation matrix (SUMM-02)</name>
  <files></files>
  <action>
Generate correlation matrix for regression variables:

1. **Create correlation matrix script:**
```python
import pandas as pd
from pathlib import Path

# Load final dataset
final_df = pd.read_csv('4_Outputs/final_dataset.csv')

# Select regression variables
regression_vars = [
    'ceo_clarity',
    'firm_size',
    'market_to_book',
    'leverage',
    'profitability',
    'liquidity',
    'volatility',
    'takeover_hazard'
]

# Calculate correlation matrix (SUMM-02)
corr_matrix = final_df[regression_vars].corr(method='pearson')

# Export to CSV
output_dir = Path('4_Outputs/final_summary_statistics')
output_dir.mkdir(parents=True, exist_ok=True)
corr_matrix.to_csv(output_dir / 'correlation_matrix.csv')

print(f"Correlation matrix exported to {output_dir / 'correlation_matrix.csv'}")
```

2. **Run correlation matrix script:**
```bash
python 2_Scripts/generate_correlation_matrix.py
```

3. **Verify output:**
```bash
cat 4_Outputs/final_summary_statistics/correlation_matrix.csv
```
  </action>
  <verify>
  Correlation matrix CSV exists with pairwise correlations for all regression variables.
  </verify>
  <done>
  Correlation matrix (SUMM-02) generated and exported as CSV.
  </done>
</task>

<task type="auto">
  <name>Task 12: Generate panel balance diagnostics (SUMM-03)</name>
  <files></files>
  <action>
Generate panel balance diagnostics:

1. **Create panel balance script:**
```python
import pandas as pd
import numpy as np
from pathlib import Path

# Load final dataset
final_df = pd.read_csv('4_Outputs/final_dataset.csv')

# Panel balance diagnostics (SUMM-03)
panel_stats = {
    'total_firms': final_df['firm_id'].nunique(),
    'total_observations': len(final_df),
    'years': final_df['year'].nunique(),
    'avg_observations_per_firm': len(final_df) / final_df['firm_id'].nunique(),
    'min_observations_per_firm': final_df['firm_id'].value_counts().min(),
    'max_observations_per_firm': final_df['firm_id'].value_counts().max(),
    'median_observations_per_firm': final_df['firm_id'].value_counts().median()
}

# Per-year breakdown
yearly_stats = final_df.groupby('year').agg({
    'firm_id': 'nunique',
    'observation_id': 'count'
}).reset_index()
yearly_stats.columns = ['Year', 'Number_of_Firms', 'Number_of_Observations']

# Calculate firms with complete data
years_present = final_df['year'].unique()
complete_firms = final_df.groupby('firm_id').filter(
    lambda x: set(x['year'].unique()) == set(years_present)
)
panel_stats['firms_with_complete_data'] = complete_firms['firm_id'].nunique()
panel_stats['complete_data_percent'] = (
    panel_stats['firms_with_complete_data'] / panel_stats['total_firms'] * 100
)

# Export to CSV
output_dir = Path('4_Outputs/final_summary_statistics')
output_dir.mkdir(parents=True, exist_ok=True)

# Export panel summary
pd.DataFrame([panel_stats]).to_csv(
    output_dir / 'panel_balance.csv',
    index=False
)

# Export yearly breakdown
yearly_stats.to_csv(
    output_dir / 'panel_yearly_breakdown.csv',
    index=False
)

print(f"Panel balance diagnostics exported to {output_dir}")
```

2. **Run panel balance script:**
```bash
python 2_Scripts/generate_panel_balance.py
```

3. **Verify output:**
```bash
cat 4_Outputs/final_summary_statistics/panel_balance.csv
cat 4_Outputs/final_summary_statistics/panel_yearly_breakdown.csv
```
  </action>
  <verify>
  Panel balance diagnostics CSV exists with total firms, observations, years, and complete data percentages.
  </verify>
  <done>
  Panel balance diagnostics (SUMM-03) generated and exported as CSV.
  </done>
</task>

<task type="auto">
  <name>Task 13: Create SUMMARY.md</name>
  <files>.planning/phases/04-financial-econometric/SUMMARY.md</files>
  <action>
Create a summary document at `.planning/phases/04-financial-econometric/SUMMARY.md` documenting:

1. **Implementation Summary:**
   - Step 3 scripts updated: 3.0, 3.1, 3.2, 3.3
   - Step 4 scripts updated: 4.1, 4.2, 4.3
   - Inline stats helpers added to each
   - Financial and econometric metrics implemented

2. **Metrics Coverage:**
   | Script | Metrics Added | Key Fields |
   |--------|---------------|------------|
   | 3.0 | Financial Features + Merge Diagnostics | merges, financial_features, panel_balance, merge_diagnostics |
   | 3.1 | Firm Controls | control_distributions, outliers, control_correlations |
   | 3.2 | Market Variables | market_variables, market_wide, time_series_properties |
   | 3.3 | Event Flags | event_flags, event_overlaps, event_distribution |
   | 4.1 | CEO Clarity Estimation | model_specification, regression_results, model_diagnostics |
   | 4.2 | Liquidity Regressions | liquidity_measures, regression_specifications, robustness_checks |
   | 4.3 | Takeover Hazards | event_statistics, hazard_model, model_diagnostics |

3. **Final Dataset Statistics:**
   - Descriptive statistics (SUMM-01): N, Mean, SD, Min, P25, Median, P75, Max
   - Correlation matrix (SUMM-02): Pairwise correlations
   - Panel balance diagnostics (SUMM-03): Total firms, observations, years, complete data

4. **Sample stats.json outputs (sanitized):**
   - 3.0 sample structure
   - 4.1 sample structure
   - 4.3 sample structure

5. **Issues Found (if any):**
   - Issue description
   - Severity
   - Resolution

6. **Pattern Validation:**
   - STAT-01-09 requirements met in all scripts
   - Financial-specific metrics successfully integrated
   - Econometric-specific metrics successfully integrated
   - Consistent formatting across all outputs
   - Panel balance diagnostics available

7. **Final Dataset Summary:**
   - Total firms
   - Total observations
   - Years covered
   - Key variable distributions
   - Correlation insights
   - Panel completeness

8. **Next Steps:**
   - All Steps 3-4 scripts have comprehensive statistics
   - Final dataset summary statistics complete
   - Ready for analysis and reporting
   - Any refinements needed

Write to `.planning/phases/04-financial-econometric/SUMMARY.md`
  </action>
  <verify>
  Summary document exists and documents all metrics coverage, implementation details, and final dataset statistics.
  </verify>
  <done>
  Complete summary document created for Phase 4 financial and econometric rollout.
  </done>
</task>

</tasks>

<verification>
- [ ] 3.0_BuildFinancialFeatures.py updated with inline stats helpers
- [ ] 3.0 stats.json exists and contains financial feature metrics
- [ ] 3.0 stats.json includes merge diagnostics
- [ ] 3.0 stats.json includes panel balance metrics
- [ ] 3.1_FirmControls.py updated with inline stats helpers
- [ ] 3.1 stats.json exists and contains firm control metrics
- [ ] 3.1 stats.json includes control distributions
- [ ] 3.1 stats.json includes outlier detection
- [ ] 3.2_MarketVariables.py updated with inline stats helpers
- [ ] 3.2 stats.json exists and contains market variable metrics
- [ ] 3.2 stats.json includes market-wide statistics
- [ ] 3.2 stats.json includes time-series properties
- [ ] 3.3_EventFlags.py updated with inline stats helpers
- [ ] 3.3 stats.json exists and contains event flag metrics
- [ ] 3.3 stats.json includes event occurrence statistics
- [ ] 3.3 stats.json includes event distribution
- [ ] 4.1_EstimateCeoClarity.py updated with inline stats helpers
- [ ] 4.1 stats.json exists and contains regression metrics
- [ ] 4.1 stats.json includes model specification
- [ ] 4.1 stats.json includes regression results
- [ ] 4.1 stats.json includes model diagnostics
- [ ] 4.2_LiquidityRegressions.py updated with inline stats helpers
- [ ] 4.2 stats.json exists and contains liquidity regression metrics
- [ ] 4.2 stats.json includes liquidity measure distributions
- [ ] 4.2 stats.json includes regression specifications
- [ ] 4.3_TakeoverHazards.py updated with inline stats helpers
- [ ] 4.3 stats.json exists and contains hazard model metrics
- [ ] 4.3 stats.json includes event statistics
- [ ] 4.3 stats.json includes hazard model coefficients
- [ ] All stats.json files are valid JSON
- [ ] All stats.json files contain STAT-01-09 base fields
- [ ] All Step 3 scripts run successfully
- [ ] All Step 4 scripts run successfully
- [ ] Descriptive statistics CSV exists (SUMM-01)
- [ ] Descriptive statistics includes N, Mean, SD, Min, P25, Median, P75, Max
- [ ] Correlation matrix CSV exists (SUMM-02)
- [ ] Panel balance diagnostics CSV exists (SUMM-03)
- [ ] Log files contain summary tables
- [ ] SUMMARY.md created
</verification>

<success_criteria>
Phase 4 complete when:
1. All four Step 3 scripts (3.0, 3.1, 3.2, 3.3) have inline stats helpers
2. All three Step 4 scripts (4.1, 4.2, 4.3) have inline stats helpers
3. All scripts produce valid stats.json files
4. 3.0 stats.json includes financial features, merge diagnostics, and panel balance metrics
5. 3.1 stats.json includes firm control distributions and outlier detection
6. 3.2 stats.json includes market variables and time-series properties
7. 3.3 stats.json includes event flags and occurrence statistics
8. 4.1 stats.json includes model specification, regression results, and diagnostics
9. 4.2 stats.json includes liquidity measures and regression specifications
10. 4.3 stats.json includes hazard model coefficients and event statistics
11. Descriptive statistics CSV exists with SUMM-01 requirements
12. Correlation matrix CSV exists with SUMM-02 requirements
13. Panel balance diagnostics CSV exists with SUMM-03 requirements
14. All scripts run successfully without errors
15. SUMMARY.md documents the implementation and final dataset statistics
16. Pattern is fully rolled out across Steps 3-4 with comprehensive financial and econometric metrics
</success_criteria>

<output>
After completion, create `.planning/phases/04-financial-econometric/SUMMARY.md`
</output>
