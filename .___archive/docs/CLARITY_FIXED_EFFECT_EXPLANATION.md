# Why ClarityCEO is Constant (and ΔClarity ≈ 0)

## 1. The Definition: Clarity as a "Fixed Effect"

In Step 2.8 of our pipeline (and in the reference literature), **ClarityCEO** is defined not as a raw score for a specific call, but as a **persistent personal trait** of the CEO. 

It is calculated using a **Fixed Effects Regression**:

$$ UncAns_{i,j,t} = \gamma_i + \beta_1 UncPre_{i,t} + \beta_2 Controls_{i,t} + \alpha_t + \epsilon_{i,j,t} $$

Where:
- $UncAns_{i,j,t}$ is the uncertainty in the Q&A session.
- $\gamma_i$ (Gamma) is the **CEO Fixed Effect**. This is the specific parameter we extract.
- **ClarityCEO** is defined as $- \gamma_i$ (standardized).

### Key Concept: Time-Invariance
A "Fixed Effect" in econometrics is, by definition, **time-invariant**. It represents the average deviation of that specific individual from the baseline, holding everything else constant.

*   **Example**: 
    *   Steve Jobs (CEO_ID: 123) has a calculated $\gamma_{123} = -0.5$.
    *   **Q1 2008**: His Clarity Score is 0.5.
    *   **Q2 2008**: His Clarity Score is 0.5.
    *   **Q3 2008**: His Clarity Score is 0.5.
    *   ...
    *   **Q4 2011**: His Clarity Score is 0.5.

No matter how the market crashes or the earnings change, **this specific metric** (`ClarityCEO`) remains locked to his identity.

---

## 2. The Consequence for Kinematics (Differencing)

The "Kinematics" analysis (Step 2.9c) attempts to measure how *changes* in clarity affect *changes* in liquidity. It uses **First Differences** ($\Delta$).

### Scenario A: Differencing by CEO (Current Approach in 2.9c)
We grouped the data by `CEO_ID` to see how a CEO's clarity evolves.

$$ \Delta Clarity_t = Clarity_t - Clarity_{t-1} $$

Since $Clarity_t$ and $Clarity_{t-1}$ are identical for the same CEO:

$$ \Delta Clarity_t = 0.5 - 0.5 = 0 $$

**Result**: 
- The variable `D1_ClarityCEO` is effectively a vector of zeros (with minor noise if standardization baselines shift slightly, but theoretically zero).
- **Regression Result**: The regression $ \Delta Liquidity \sim \Delta Clarity $ finds a coefficient of ~0 because the independent variable has no variance. It explains nothing because it never changes.

### Scenario B: Differencing by Firm (Turnover Analysis)
If we grouped by `gvkey` (Firm ID), we would capture the moment one CEO leaves and another joins.

*   **Q1**: Steve Jobs (Clarity = 0.5)
*   **Q2**: Tim Cook (Clarity = 0.2) implies he is "vaguer".

$$ \Delta Clarity_{Q2} = 0.2 - 0.5 = -0.3 $$

In this scenario, we would have non-zero values **only** at the specific quarters where turnover occurs. For the vast majority of quarters (where Tim Cook stays CEO), the delta returns to 0.

---

## 3. What Varies? (The Alternative)

While `ClarityCEO` is constant, the input components vary every quarter:

1.  **MaPresUnc_pct (Presentation Uncertainty)**: The % of uncertain words in the prepared script. This changes every quarter based on the script writers and current events.
2.  **MaQaUnc_pct (Q&A Uncertainty)**: The actual unadjusted uncertainty in the Q&A. This varies every quarter.
3.  **Residual Uncertainty (`UncResid`)**: The portion of Q&A uncertainty *not* explained by the CEO's fixed style. This represents whether the CEO was *unusually* vague today compared to their normal self.

### Recommendation using 2.9c Findings
The result in 2.9c showed:
*   $\Delta Clarity \approx 0$ (Expected, as explained above).
*   $\Delta MaPresUnc \neq 0$ and had a significant coefficient.

This confirms that markets react to the **time-varying** components of information (the script, the specific Q&A performance) rather than the **time-invariant** personality trait of the CEO (which is already "priced in" by the market knowing who the CEO is).
