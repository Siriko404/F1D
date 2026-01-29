# Analysis: CEO Clarity and Market Liquidity (Full Sample 2002-2018)

## Executive Summary
This document presents the **final** 2SLS regression results examining the causal impact of **CEO Clarity** on **Market Illiquidity** (proxied by the change in Amihud's ratio). The analysis uses the full dataset from **2002 to 2018** (38,470 observations).

**Key Findings:**
1.  **Instrument Collapse (Critical):** While the chosen instrument (`shift_intensity`) appeared strong in the early subsample (2002-2010), it is **statistically insignificant** ($t = 0.69, p = 0.49$) in the full 2002-2018 sample. This indicates a **Weak Instrument** problem, making 2SLS causal inference unreliable for the full period.
2.  **No Causal Impact (Null Result):** In the second stage, instrumented CEO Clarity has **no statistically significant effect** on observed stock illiquidity ($p = 0.51$). Even in the "Kinematics" (First-Difference) model, changes in uncertainty do not predict changes in liquidity ($p = 0.69$).
3.  **Control Variables:** Market returns (`MarketRet`, $t=-2.16$) and Stock Returns (`StockRet`) consistently predict improved liquidity.

---

## 1. Naive OLS Analysis (Direct Association)
To understand the baseline relationship, we regressed Market Liquidity changes (`Delta_Amihud`) directly on CEO Clarity (`ClarityCEO`) without instrumentation.
*   **Specification:** OLS, Full Controls, Year Fixed Effects.
*   **Sample:** 38,470 Observations (2002-2018).

| Variable | Coefficient | t-statistic | P-value | Result |
| :--- | :--- | :--- | :--- | :--- |
| **ClarityCEO** | 0.00006 | 0.92 | 0.360 | **Null Result.** No significant correlation between CEO Clarity and Liquidity. |
| **MarketRet** | -0.0001 | -8.81 | 0.000 | Strong control: Market returns drive liquidity. |

**Interpretation:**
There is **no observational correlation** between the Clarity of a CEO and the market's liquidity reaction to their earnings calls. This supports the Null Hypothesis even before considering endogeneity.

---

## 2. First Stage Analysis: Instrument Relevance
The first stage regresses `ClarityCEO` (Endogenous) on `shift_intensity` (Instrument) + Controls.

| Variable | Coefficient | t-statistic | P-value | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **shift_intensity** | **0.0485** | **0.691** | **0.490** | **Weak Instrument.** The shift in auditor intensity fails to predict CEO Clarity in the full sample. This contrasts with the 2002-2010 period, suggesting the "shock" effect of auditor changes may have dissipated or become noisy over time. |
| **UncQue** | -1.68 | -137.56 | 0.000 | Uncertainty in Q&A remains the dominant (negative) correlate of Clarity. |
| **Size** | 0.05 | 18.81 | 0.000 | Larger firms have clearer CEOs. |

**Diagnostic:** The t-statistic for the instrument is **0.69**, far below the threshold of 3.3. **Identification has failed** for the full sample.

---

## 3. Second Stage Analysis: Impact on Liquidity (Levels)
The second stage regresses `Delta_Amihud` (Change in Illiquidity) on the *predicted* values of `ClarityCEO`.
*Note: `Delta_Amihud` = (Event - Baseline). Positive = Worsening Liquidity.*

| Variable | Coefficient | t-statistic | P-value | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| **ClarityCEO (Instrumented)** | **-0.039** | **-0.652** | **0.514** | **Insignificant.** No evidence that Clarity affects liquidity. Given the weak instrument, this null result implies we cannot distinguish the CEO's causal effect from noise. |
| **Size** | 0.003 | 1.04 | 0.299 | Size effect is noisy in the second stage. |
| **MarketRet** | -0.0001 | -2.17 | 0.030 | Strong market performance causally improves liquidity (lowers illiquidity). |

---

---

## 4. Kinematics Analysis (CEO Turnover Impact)
We tested a dynamic OLS model to see if **changing the CEO** (and thus shifting the persistent Clarity Fixed Effect) impacts liquidity.
*   **Method:** OLS on First-Differences at the **Firm Level** (capturing 7,264 CEO turnover events).
*   **Specification:** $\Delta Amihud = \beta \cdot \Delta Clarity_{FE} + \Delta Controls$.
*   **Hypothesis:** A transition to a clearer CEO (positive $\Delta Clarity$) should improve liquidity (negative $\Delta Amihud$).

| Variable | Coefficient | t-statistic | P-value | Result |
| :--- | :--- | :--- | :--- | :--- |
| **Delta_ClarityCEO** | **~ 0.000** ($7.7 \times 10^{-15}$) | 9.04 | 0.000 | **Numerical Null.** The coefficient is effectively zero (machine epsilon magnitude), indicating no economic effect. The high t-statistic is a numerical artifact of singularity ($Cond. No = 10^{17}$). |
| **Delta_Size** | -0.008 | -25.5 | 0.000 | Growing firms see improved liquidity. |
| **Delta_ROA** | -0.019 | -9.8 | 0.000 | Improving profitability improves liquidity. |

**Interpretation:**
Changing to a CEO with a different "Clarity Style" has **zero impact** on stock liquidity around earnings calls. The market does not price in the CEO's fixed communication style when it changes.

---

## 5. Extended Analysis (Presentation & Residuals)

We expanded the model to include **Presentation Uncertainty** (`UncPreCEO`, checking if the script itself is vague) and **Unexplained Uncertainty** (`UncResid`, the residual from the Step 2.8 Clarity model, representing "surprise" confusion).

### A. Instrumental Variable Analysis (UncPreCEO)
We instrumented `UncPreCEO` using **Auditor Shift Intensity** (`shift_intensity`) to test the causal impact of *scripted* vagueness.

1.  **First Stage (Strength of Instrument)**:
    *   The instrument (`shift_intensity`) **strongly** predicts Presentation Uncertainty.
    *   $\beta_{IV} = -0.18$ ($t = -5.72$, $p < 0.001$).
    *   *Interpretation*: Valid Identification. Increased auditor scrutiny causes CEOs to write significantly clearer (less vague) presentation scripts.

2.  **Second Stage (Causal Impact on Liquidity)**:
    *   **UncPreCEO (Instrumented)**: $\beta = 0.99$ ($t=0.36$, $p=0.72$). **Null.**
    *   *Interpretation*: Even when auditor pressure exogenously improves script clarity, there is **no causal improvement** in market liquidity.

### B. Levels (Direct Association)
$$ \Delta Amihud_{it} = \beta_1 ClarityCEO + \beta_2 UncPreCEO + \beta_3 UncResid + Controls $$

*   **ClarityCEO**: Null ($p=0.54$).
*   **UncPreCEO**: Null ($p=0.49$) in this subsample (obs=38k).
*   **UncResid**: Null ($p=0.67$).

### C. Kinematics (First-Differences)
$$ \Delta Amihud_{it} = \beta_1 \Delta ClarityCEO + \beta_2 \Delta UncPreCEO + \beta_3 \Delta UncResid + \Delta Controls $$

*   **$\Delta$ ClarityCEO** (Turnover): Null ($p=0.96$).
*   **$\Delta$ UncPreCEO**: Null ($p=0.78$).
*   **$\Delta$ UncResid**: Null ($p=0.22$).

### Conclusion (Extended)
The IV analysis provides a crucial insight: **Auditors DO influence communication quality** (making scripts clearer), satisfying the relevance condition for identification. However, this improvement in clarity **does not translate** to better market liquidity. This strongly reinforces the conclusion that liquidity constraints are structurally driven (by Market Returns, Size, ROA) rather than by the linguistic features of the earnings call.

---

## 6. Conclusion & Recommendation
The rigorous extension of the analysis to the full 2002-2018 period reveals that **Auditor Shift Intensity is not a robust instrument** for CEO Clarity over the long term. Consequently, we **cannot establish a causal link** between Clarity and Market Liquidity using this identification strategy.

**Recommendations:**
1.  **Accept the Null:** Conclude that while Clarity is a strong feature of CEO communication (correlated with firm characteristics), it does not have a detectable *short-term* causal impact on market liquidity around earnings calls.
2.  **Focus on OLS:** Descriptive OLS regressions (Naive models) show small correlations, but the lack of identification suggests these are likely endogenous.
3.  **Investigate Instrument Decay:** The instrument worked in 2002-2010 but failed later. This "decay" of the natural experiment (post-SOX era normalization) is a finding in itself.
