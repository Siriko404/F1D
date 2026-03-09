# H10 Tone at the Top - Major Revision Plan (v2)

## Context

The referee report identifies 6 major concerns. Initial plan had critical flaws identified by hard-nose audit.

**Audit Summary:**
- Analyst uncertainty merge logic was BACKWARDS
- Bootstrap code was pseudocode (incomplete)
- Measurement validation (Concern 5) was MISSING
- Multi-way clustering was UNSOLVED
- Lead variable placebo semantics was WRONG
- IHS transforms for new vars not defined
- Economic significance not implemented
- Implementation order had dependency issues

---

## Corrected Implementation Plan

### Part 1: Panel Builder Modifications (`build_h10_tone_at_top_panel.py`)

#### 1.1 Local Lags for M2 (CORRECTED)

**File:** `src/f1d/variables/build_h10_tone_at_top_panel.py`

```python
# In build_turns_panel(), after line 228 (expanding mean calculation):

# Local lag specifications
# 1. Last CEO turn only (lag-1) - shift(1) gives previous value
ceo_turns["CEO_Unc_Lag1"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].shift(1)

# 2. Rolling mean of last k=2,3 CEO turns (shift(1) ensures only PRIOR turns)
# min_periods=1 allows first CEO turn to use available data
ceo_turns["CEO_Unc_Roll2"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
    lambda x: x.shift(1).rolling(2, min_periods=1).mean()
)
ceo_turns["CEO_Unc_Roll3"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
    lambda x: x.shift(1).rolling(3, min_periods=1).mean()
)

# 3. Exponentially weighted mean (alpha=0.5 gives 50% weight to most recent)
ceo_turns["CEO_Unc_ExpDecay"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].transform(
    lambda x: x.shift(1).ewm(alpha=0.5, min_periods=1).mean()
)

# 4. LEAD variable for placebo test (FUTURE CEO uncertainty)
# shift(-1) gives NEXT CEO turn's uncertainty
ceo_turns["CEO_Unc_Lead1"] = ceo_turns.groupby("file_name")["Turn_Uncertainty_pct"].shift(-1)
```

**Note:** All new variables will have NaN for boundary cases (first CEO turn for lags, last CEO turn for lead). This is correct behavior - managers can't be influenced by turns that don't exist yet.

#### 1.2 Turn Index Controls (CORRECTED)

```python
# In build_turns_panel(), after the merge_asof (line ~246):
# speaker_number IS the turn index within call (0-indexed from tokenizer)

# Rename for clarity
turns_panel = turns_panel.rename(columns={"speaker_number": "turn_index"})

# Add polynomial terms for flexible time controls
turns_panel["turn_index_sq"] = turns_panel["turn_index"] ** 2
turns_panel["turn_index_cu"] = turns_panel["turn_index"] ** 3

# Alternative: normalized turn index (0 to 1 within call)
call_max_turns = turns_panel.groupby("file_name")["turn_index"].transform("max")
turns_panel["turn_index_norm"] = turns_panel["turn_index"] / call_max_turns.clip(lower=1)
```

#### 1.3 Analyst Question Uncertainty (CORRECTED LOGIC)

**The original plan had BACKWARDS logic. Here's the correct approach:**

```python
# In build_turns_panel(), BEFORE the merge_asof:

# Step 1: Identify analyst turns
# Use role column - analysts typically have "Analyst" in role
# The employer field is unreliable (managers may have it populated)
analyst_pattern = r"\bAnalyst\b"
qa_tokens["is_analyst"] = qa_tokens["role"].str.contains(
    analyst_pattern, case=False, na=False
)

# Step 2: Compute analyst turn uncertainty
qa_tokens["Analyst_Turn_Unc_pct"] = np.where(
    qa_tokens["total_tokens"] > 0,
    (qa_tokens["Uncertainty_count"] / qa_tokens["total_tokens"]) * 100.0,
    0.0,
)

# Step 3: For each turn, get the PRECEDING turn's analyst uncertainty
# This works for ALL turns - shift(1) looks at immediately prior turn
qa_tokens["Preceding_Analyst_Unc"] = qa_tokens.groupby("file_name")["Analyst_Turn_Unc_pct"].shift(1)

# Step 4: Also flag if preceding turn was actually an analyst
qa_tokens["Preceding_Is_Analyst"] = qa_tokens.groupby("file_name")["is_analyst"].shift(1)

# Now when we create mgr_turns, Preceding_Analyst_Unc is already available
# Filter to non-CEO managers as before
mgr_turns = qa_tokens[qa_tokens["is_nonceo_mgr"]].copy()

# For merge_asof with CEO variables, we need speaker_number (turn_index)
# Make sure Preceding_Analyst_Unc is carried through
```

**Key Fix:** Instead of trying to merge analyst turns TO manager turns, we compute the preceding turn's uncertainty on the FULL qa_tokens dataframe first, then filter to managers. This correctly captures "what uncertainty did the manager hear right before speaking."

#### 1.4 Merge All CEO Variables to Manager Turns

```python
# After computing all CEO variables (expanding mean, lags, lead), merge to mgr_turns

# Columns to merge from ceo_turns
ceo_merge_cols = [
    "file_name", "turn_index",
    "CEO_Prior_QA_Unc",  # Expanding mean (baseline)
    "CEO_Unc_Lag1", "CEO_Unc_Roll2", "CEO_Unc_Roll3", "CEO_Unc_ExpDecay",  # Local lags
    "CEO_Unc_Lead1",  # Placebo lead
]

# Use merge_asof to get the LATEST CEO values strictly prior to manager turn
turns_panel = pd.merge_asof(
    mgr_turns.sort_values(["file_name", "turn_index"]),
    ceo_turns[ceo_merge_cols].sort_values(["file_name", "turn_index"]),
    on="turn_index",
    by="file_name",
    allow_exact_matches=False,  # Strictly prior
    direction="backward",
)
```

---

### Part 2: Econometric Script Modifications (`run_h10_tone_at_top.py`)

#### 2.1 IHS Transforms for All New Variables (ADDED)

```python
# In main(), after loading turns_panel (around line 617):

# Existing transforms
turns_panel["IHS_NonCEO_Turn_Unc"] = asinh(turns_panel["Turn_Uncertainty_pct"])
turns_panel["IHS_CEO_Prior_QA_Unc"] = asinh(turns_panel["CEO_Prior_QA_Unc"])

# NEW: IHS transforms for all CEO lag variables
turns_panel["IHS_CEO_Unc_Lag1"] = asinh(turns_panel["CEO_Unc_Lag1"])
turns_panel["IHS_CEO_Unc_Roll2"] = asinh(turns_panel["CEO_Unc_Roll2"])
turns_panel["IHS_CEO_Unc_Roll3"] = asinh(turns_panel["CEO_Unc_Roll3"])
turns_panel["IHS_CEO_Unc_ExpDecay"] = asinh(turns_panel["CEO_Unc_ExpDecay"])
turns_panel["IHS_CEO_Unc_Lead1"] = asinh(turns_panel["CEO_Unc_Lead1"])

# NEW: IHS transform for analyst uncertainty
turns_panel["IHS_Analyst_Unc"] = asinh(turns_panel["Preceding_Analyst_Unc"])
```

#### 2.2 M1 Without Bad Controls (CORRECTED)

```python
# Define control specifications
CALL_CONTROLS_FULL = [
    "Size", "BM", "Lev", "ROA",
    "StockRet", "MarketRet", "EPS_Growth", "SurpDec",
    "IHS_CEO_QA_Unc", "IHS_CEO_Pres_Unc",  # CEO same-call controls
]

CALL_CONTROLS_NO_CEO = [
    "Size", "BM", "Lev", "ROA",
    "StockRet", "MarketRet", "EPS_Growth", "SurpDec",
    # Exclude CEO same-call controls
]

# In main():
# Spec 1: WITHOUT CEO controls (preferred for causal interpretation)
m1_no_ceo_coef, m1_no_ceo_diag = run_call_level_model_full(
    call_sub, "IHS_CFO_QA_Unc", "ClarityStyle_Realtime", CALL_CONTROLS_NO_CEO
)

# Spec 2: WITH CEO controls (current baseline - "holding constant" interpretation)
m1_with_ceo_coef, m1_with_ceo_diag = run_call_level_model_full(
    call_sub, "IHS_CFO_QA_Unc", "ClarityStyle_Realtime", CALL_CONTROLS_FULL
)
```

#### 2.3 M2 Robustness Specifications (CORRECTED)

```python
def run_m2_specifications(df: pd.DataFrame) -> Dict[str, Tuple[pd.DataFrame, Dict]]:
    """Run all M2 specifications for robustness testing."""
    results = {}

    specs = {
        # Baseline (current)
        "baseline": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": [],
            "description": "Expanding mean (baseline)",
        },
        # Local lags (address time trend concern)
        "lag1": {
            "iv": "IHS_CEO_Unc_Lag1",
            "controls": [],
            "description": "Last CEO turn only",
        },
        "roll2": {
            "iv": "IHS_CEO_Unc_Roll2",
            "controls": [],
            "description": "Rolling 2 CEO turns",
        },
        "roll3": {
            "iv": "IHS_CEO_Unc_Roll3",
            "controls": [],
            "description": "Rolling 3 CEO turns",
        },
        "exp_decay": {
            "iv": "IHS_CEO_Unc_ExpDecay",
            "controls": [],
            "description": "Exp. weighted (alpha=0.5)",
        },
        # With time controls
        "with_turn_linear": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index"],
            "description": "Baseline + turn index",
        },
        "with_turn_quad": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index", "turn_index_sq"],
            "description": "Baseline + quadratic time",
        },
        # With analyst controls
        "with_analyst": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["IHS_Analyst_Unc"],
            "description": "Baseline + analyst uncertainty",
        },
        "full_controls": {
            "iv": "IHS_CEO_Prior_QA_Unc",
            "controls": ["turn_index", "turn_index_sq", "IHS_Analyst_Unc"],
            "description": "Baseline + all controls",
        },
        # Placebo: future CEO uncertainty should NOT predict
        "placebo_lead": {
            "iv": "IHS_CEO_Unc_Lead1",
            "controls": [],
            "description": "Placebo: FUTURE CEO uncertainty",
        },
    }

    for spec_name, spec in specs.items():
        coef_df, diag = run_turn_level_model_full(df, "IHS_NonCEO_Turn_Unc", spec["iv"], spec["controls"])
        results[spec_name] = {
            "coefficients": coef_df,
            "diagnostics": diag,
            "description": spec["description"],
        }

    return results
```

#### 2.4 Update run_turn_level_model_full to Accept Controls

```python
def run_turn_level_model_full(
    df: pd.DataFrame, dv: str, iv: str, controls: Optional[List[str]] = None
) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """
    Run Model 2 (Speaker-turn level) with Call FE + Speaker FE absorbed.
    Now supports additional controls beyond the main IV.
    """
    if controls is None:
        controls = []

    reg_df = df.copy()

    keep_cols = [
        "file_name", "speaker_name", "gvkey", "ceo_id",
        dv, iv,
    ] + controls
    keep_cols = list(set(keep_cols))  # Remove duplicates
    reg_df = reg_df.dropna(subset=keep_cols)

    if len(reg_df) < 50:
        return pd.DataFrame(), {"N": len(reg_df), "Error": "Too few obs"}

    reg_df["const"] = 1.0
    for col in [dv, iv] + controls:
        reg_df[col] = reg_df[col].astype(float)

    exog = ["const", iv] + controls

    # ... rest of function unchanged
```

#### 2.5 Clustering Strategy (CORRECTED)

**Problem:** `linearmodels.AbsorbingLS` only supports 2 cluster variables. Current: `gvkey` + `ceo_id`.

**Solution:** For M2, replace CEO clustering with CALL clustering since:
1. Call FE is already absorbed
2. The variation of interest is within-call
3. Call-level clustering captures the DGP (turns within calls)

```python
def run_turn_level_model_full(..., cluster_by_call: bool = False):
    # ...
    if cluster_by_call:
        # Cluster by firm + call (not CEO)
        clusters = reg_df[["gvkey", "file_name"]].copy()
    else:
        # Original: cluster by firm + CEO
        clusters = reg_df[["gvkey", "ceo_id"]].copy()

    clusters["gvkey"] = clusters["gvkey"].astype("category").cat.codes
    clusters.iloc[:, 1] = clusters.iloc[:, 1].astype("category").cat.codes

    res = mod.fit(cov_type="clustered", clusters=clusters)
```

Run M2 with BOTH clustering strategies for robustness.

#### 2.6 Wild Cluster Bootstrap (CORRECTED - FULLY IMPLEMENTED)

**Note:** `wildboottest` works with OLS, not directly with `AbsorbingLS`. We need to implement manually or use a workaround.

```python
import numpy as np
from scipy import stats

def wild_cluster_bootstrap(
    df: pd.DataFrame,
    dv: str,
    iv: str,
    cluster_col: str,
    n_bootstrap: int = 9999,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Wild cluster bootstrap for small samples (Utility, Finance).

    Uses Rademacher weights (±1) for residuals.
    Returns bootstrap p-value and confidence interval.

    Reference: Cameron, Gelbach, & Miller (2008)
    """
    np.random.seed(seed)

    # Prepare data
    df = df.dropna(subset=[dv, iv, cluster_col]).copy()
    df["const"] = 1.0

    # Get unique clusters
    clusters = df[cluster_col].unique()
    n_clusters = len(clusters)

    if n_clusters < 10:
        print(f"WARNING: Only {n_clusters} clusters, bootstrap may be unreliable")

    # Run baseline regression (OLS, no FE for simplicity)
    X = df[["const", iv]].values
    y = df[dv].values

    try:
        beta = np.linalg.lstsq(X, y, rcond=None)[0]
        resid = y - X @ beta
        baseline_coef = beta[1]
    except:
        return {"p_value": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "error": "Baseline regression failed"}

    # Get residuals by cluster
    cluster_resid = df.groupby(cluster_col).apply(lambda g: resid[g.index])

    # Bootstrap
    boot_coefs = []
    for _ in range(n_bootstrap):
        # Draw Rademacher weights (±1) for each cluster
        weights = np.random.choice([-1, 1], size=n_clusters)
        weight_map = dict(zip(clusters, weights))

        # Create wild residuals
        wild_resid = np.array([weight_map[c] * r for c, r in zip(df[cluster_col], resid)])

        # Create bootstrap outcome
        y_boot = X @ beta + wild_resid

        # Re-estimate
        try:
            beta_boot = np.linalg.lstsq(X, y_boot, rcond=None)[0]
            boot_coefs.append(beta_boot[1])
        except:
            continue

    if len(boot_coefs) < n_bootstrap * 0.9:
        return {"p_value": np.nan, "ci_lower": np.nan, "ci_upper": np.nan, "error": "Too many bootstrap failures"}

    boot_coefs = np.array(boot_coefs)

    # Two-sided p-value
    p_value = np.mean(np.abs(boot_coefs) >= np.abs(baseline_coef))

    # Confidence interval (percentile method)
    ci_lower = np.percentile(boot_coefs, 2.5)
    ci_upper = np.percentile(boot_coefs, 97.5)

    return {
        "p_value": p_value,
        "ci_lower": ci_lower,
        "ci_upper": ci_upper,
        "n_bootstrap": len(boot_coefs),
        "baseline_coef": baseline_coef,
    }
```

#### 2.7 Permutation Test (OPTIMIZED)

```python
def permutation_test_optimized(
    df: pd.DataFrame,
    dv: str,
    iv: str,
    group_col: str,
    n_permutations: int = 500,
    seed: int = 42,
) -> Dict[str, float]:
    """
    Permutation test: shuffle IV within groups (calls).
    Optimized to avoid full dataframe copies.

    Returns empirical p-value.
    """
    np.random.seed(seed)

    df = df.dropna(subset=[dv, iv, group_col]).copy()
    df["const"] = 1.0

    # Pre-compute baseline
    X = df[["const", iv]].values
    y = df[dv].values
    baseline_coef = np.linalg.lstsq(X, y, rcond=None)[0][1]

    # Pre-extract values
    iv_values = df[iv].values
    groups = df[group_col].values
    unique_groups = np.unique(groups)

    # Get indices for each group
    group_indices = {g: np.where(groups == g)[0] for g in unique_groups}

    perm_coefs = []
    for _ in range(n_permutations):
        # Shuffle within groups (in-place on a copy of iv_values)
        iv_shuffled = iv_values.copy()
        for g in unique_groups:
            idx = group_indices[g]
            iv_shuffled[idx] = np.random.permutation(iv_shuffled[idx])

        # Re-estimate
        X_perm = np.column_stack([np.ones(len(df)), iv_shuffled])
        try:
            coef = np.linalg.lstsq(X_perm, y, rcond=None)[0][1]
            perm_coefs.append(coef)
        except:
            continue

    perm_coefs = np.array(perm_coefs)

    # Two-sided empirical p-value
    p_value = np.mean(np.abs(perm_coefs) >= np.abs(baseline_coef))

    return {
        "p_value": p_value,
        "baseline_coef": baseline_coef,
        "perm_mean": np.mean(perm_coefs),
        "perm_std": np.std(perm_coefs),
        "n_permutations": len(perm_coefs),
    }
```

---

### Part 3: Measurement Validation (NEW - Addressing Concern 5)

#### 3.1 Stratified Sample Validation

```python
def validate_speaker_classification(
    root_path: Path,
    n_sample: int = 100,
    seed: int = 42,
) -> pd.DataFrame:
    """
    Validate CEO/CFO/Non-CEO manager classification on a stratified sample.

    Outputs a report with precision/recall for each role type.
    Manual review required for sampled turns.
    """
    np.random.seed(seed)

    # Load token data
    token_dir = get_latest_output_dir(root_path / "outputs" / "2_Textual_Analysis" / "2.1_Tokenized")
    # Load one year for sampling
    df = pd.read_parquet(token_dir / "linguistic_counts_2015.parquet")
    qa = df[df["context"].str.lower() == "qa"].copy()

    # Apply classification patterns
    ceo_pattern = r"\bCEO\b|Chief Executive"
    cfo_pattern = r"\bCFO\b|Chief\s+Financial|Financial\s+Officer|Principal\s+Financial"
    mgr_pattern = r"PRESIDENT|VP|DIRECTOR|CEO|EVP|SVP|CFO|OFFICER|CHIEF|EXECUTIVE|HEAD|CHAIRMAN|SENIOR|MANAGER|COO|TREASURER|SECRETARY|MD|DEPUTY|CONTROLLER|GM|PRINCIPAL|CAO|CIO|CTO|CMO|LEADER|LEAD|CCO|COORDINATOR|AVP|ADMINISTRATOR|CHAIRWOMAN|CHAIRPERSON|SUPERINTENDENT|DEAN|COMMISSIONER|CA|GOVERNOR|SUPERVISOR|COACH|PROVOST|CAPTAIN|CHO|RECTOR"

    qa["is_ceo"] = qa["role"].str.contains(ceo_pattern, case=False, na=False)
    qa["is_cfo"] = qa["role"].str.contains(cfo_pattern, case=False, na=False)
    qa["is_manager"] = qa["role"].str.contains(mgr_pattern, case=False, na=False)

    # Stratified sample: 25 from each category
    samples = []
    for cat, mask in [("CEO", qa["is_ceo"]), ("CFO", qa["is_cfo"]), ("NonCEO_Manager", qa["is_manager"] & ~qa["is_ceo"])]:
        cat_df = qa[mask]
        if len(cat_df) >= 25:
            sample = cat_df.sample(n=25)
        else:
            sample = cat_df
        sample["classified_as"] = cat
        samples.append(sample)

    sample_df = pd.concat(samples, ignore_index=True)

    # Output for manual review
    out_cols = ["file_name", "turn_index", "role", "speaker_name", "classified_as", "speaker_text"]
    sample_df[out_cols].to_csv(root_path / "outputs" / "validation" / "speaker_classification_sample.csv", index=False)

    print(f"Sample saved for manual review. N={len(sample_df)}")
    print("Manual review instructions:")
    print("1. Open the CSV file")
    print("2. Add a column 'true_role' with values: CEO, CFO, NonCEO_Mgr, Other")
    print("3. Compare to 'classified_as' for precision/recall")

    return sample_df
```

#### 3.2 Sensitivity by Manager Type

```python
def run_manager_type_sensitivity(df: pd.DataFrame) -> Dict[str, Tuple]:
    """Run M2 separately for CFO vs non-CFO managers vs top executives."""

    # CFO pattern (narrow)
    cfo_pattern = r"\bCFO\b|Chief\s+Financial|Financial\s+Officer|Principal\s+Financial"

    # Top executive pattern (COO, President, etc.)
    top_exec_pattern = r"\bCOO\b|President|Chief Operating"

    # Classify
    df["is_cfo"] = df["role"].str.contains(cfo_pattern, case=False, na=False)
    df["is_top_exec"] = df["role"].str.contains(top_exec_pattern, case=False, na=False)
    df["is_other_mgr"] = ~df["is_cfo"] & ~df["is_top_exec"]

    results = {}

    # CFO only
    cfo_df = df[df["is_cfo"]]
    if len(cfo_df) >= 50:
        results["cfo_only"] = run_turn_level_model_full(cfo_df, "IHS_NonCEO_Turn_Unc", "IHS_CEO_Prior_QA_Unc")

    # Top executives only
    top_df = df[df["is_top_exec"]]
    if len(top_df) >= 50:
        results["top_exec_only"] = run_turn_level_model_full(top_df, "IHS_NonCEO_Turn_Unc", "IHS_CEO_Prior_QA_Unc")

    # Other managers
    other_df = df[df["is_other_mgr"]]
    if len(other_df) >= 50:
        results["other_mgr_only"] = run_turn_level_model_full(other_df, "IHS_NonCEO_Turn_Unc", "IHS_CEO_Prior_QA_Unc")

    return results
```

---

### Part 4: Economic Significance (NEW - Addressing Concern 6)

```python
def compute_economic_significance(
    turns_panel: pd.DataFrame,
    coef: float,
    iv: str = "IHS_CEO_Prior_QA_Unc",
    dv: str = "IHS_NonCEO_Turn_Unc",
) -> Dict[str, float]:
    """
    Translate IHS coefficient to interpretable economic magnitude.

    Computes:
    - SD of IV
    - Predicted change from 25th to 75th percentile
    - As % of DV's SD
    - In basis points (approximate)
    """
    df = turns_panel.dropna(subset=[iv, dv])

    iv_sd = df[iv].std()
    iv_p25 = df[iv].quantile(0.25)
    iv_p75 = df[iv].quantile(0.75)
    dv_sd = df[dv].std()
    dv_mean = df[dv].mean()

    # One SD change in IV
    delta_1sd = coef * iv_sd

    # 25th to 75th percentile change
    delta_iqr = coef * (iv_p75 - iv_p25)

    # As % of DV SD
    pct_of_sd = (delta_1sd / dv_sd) * 100

    # Approximate basis points (IHS ≈ log for small values)
    # For larger values, this is approximate
    bps_1sd = delta_1sd * 100  # IHS units to approximate bps

    return {
        "iv_sd": iv_sd,
        "dv_sd": dv_sd,
        "delta_1sd": delta_1sd,
        "delta_iqr": delta_iqr,
        "pct_of_dv_sd": pct_of_sd,
        "approx_bps_1sd": bps_1sd,
        "iv_p25": iv_p25,
        "iv_p75": iv_p75,
        "dv_mean": dv_mean,
    }
```

---

### Part 5: Corrected Implementation Order

```
1. Panel Builder (build_h10_tone_at_top_panel.py)
   ├── 1.1 Add local lags (lag1, roll2, roll3, exp_decay)
   ├── 1.2 Add lead variable for placebo
   ├── 1.3 Add turn index controls
   ├── 1.4 Fix analyst uncertainty logic (compute on full qa_tokens, then filter)
   ├── 1.5 Merge all CEO variables to manager turns
   └── 1.6 Add manager type classification (CFO, top_exec, other)

2. Run Panel Builder
   └── python -m f1d.variables.build_h10_tone_at_top_panel

3. Econometric Script (run_h10_tone_at_top.py)
   ├── 3.1 Add IHS transforms for all new variables
   ├── 3.2 Update run_turn_level_model_full to accept controls
   ├── 3.3 Add M1 with/without CEO controls
   ├── 3.4 Add M2 robustness specifications function
   ├── 3.5 Add clustering by call option
   ├── 3.6 Add wild_cluster_bootstrap function
   ├── 3.7 Add permutation_test_optimized function
   ├── 3.8 Add economic significance calculation
   └── 3.9 Generate all robustness tables

4. Validation (NEW)
   ├── 4.1 Add validate_speaker_classification function
   └── 4.2 Add run_manager_type_sensitivity function

5. Run Econometrics
   └── python -m f1d.econometric.run_h10_tone_at_top

6. Documentation Updates
   ├── 6.1 Soften causal language
   ├── 6.2 Add robustness section with all results
   ├── 6.3 Add economic significance
   └── 6.4 Update limitations
```

---

### Part 6: New Outputs

| Output File | Description |
|-------------|-------------|
| `tone_at_top_robustness_m1.tex` | M1 with/without CEO controls |
| `tone_at_top_robustness_m2_lags.tex` | M2 with local lag specifications |
| `tone_at_top_robustness_m2_controls.tex` | M2 with turn/analyst controls |
| `tone_at_top_placebo.tex` | Lead test and permutation results |
| `tone_at_top_bootstrap.tex` | Wild cluster bootstrap for Utility/Finance |
| `tone_at_top_manager_sensitivity.tex` | CFO vs top exec vs other managers |
| `tone_at_top_economic_significance.md` | Economic magnitude interpretation |
| `speaker_classification_sample.csv` | For manual validation |

---

### Part 7: Documentation Updates

Update `docs/H10_TONE_AT_TOP_DOCUMENTATION.md`:

1. **Soften causal language**:
   - "Granger-style causality" → "within-call temporal association consistent with transmission"
   - Add caveat: "Turn ordering is determined by analyst question sequence, which may be strategic"

2. **Add robustness section** (Section 11):
   - Table of M2 lag specifications
   - Table of M2 with controls
   - Placebo test results
   - Bootstrap p-values

3. **Add bad controls discussion** (Section 6.3):
   - Explain M1 with/without CEO controls
   - Interpret difference as mechanism vs conditioning bias

4. **Add economic significance** (new Section 10.3):
   - "A one-standard-deviation increase in CEO prior Q&A uncertainty increases manager uncertainty by X IHS units (Y% of within-call SD)"
   - Report for each sample

5. **Update limitations** (Section 12):
   - Acknowledge analyst ordering is strategic
   - Note speaker classification uncertainty

---

## Files to Modify

| File | Changes | Lines |
|------|---------|-------|
| `src/f1d/variables/build_h10_tone_at_top_panel.py` | Local lags, turn controls, analyst controls, lead vars, manager type | +80 |
| `src/f1d/econometric/run_h10_tone_at_top.py` | M1 specs, M2 specs, bootstrap, permutation, economic sig | +250 |
| `docs/H10_TONE_AT_TOP_DOCUMENTATION.md` | Soften language, add robustness section | +100 |
| `requirements.txt` or `pyproject.toml` | No new packages needed (bootstrap implemented manually) | 0 |

**Total: ~430 lines of new code**

---

## Verification Checklist

- [ ] Panel builder runs without error
- [ ] All new columns present in turns_panel.parquet
- [ ] IHS transforms applied correctly
- [ ] M1 with/without CEO controls produces different results
- [ ] M2 local lags show similar pattern to baseline
- [ ] Placebo lead coefficient is ~0 (null result expected)
- [ ] Permutation p-value < 0.05 (reject null of no effect)
- [ ] Bootstrap p-values are valid for Utility sample
- [ ] Economic significance computed and documented
- [ ] All LaTeX tables generate without error

---

## User Decision

**Selected Scope: Full Suite (Recommended)**

All 6 robustness tests + bootstrap + measurement validation + economic significance will be implemented.
