### 1. The Linguistic Variable Mapping
The paper is very specific that the regression requires splitting the conference call into parts (Answers vs. Presentation vs. Questions). Most raw linguistic datasets provide a score for the *entire* call. I need to know if your `f1d_enriched` file actually supports this split.

*   **Variable $Y$ ($UncAnsCEO$):** What is the exact column name for uncertainty frequency in **CEO Answers**?
    *   **Clarification Needed:** I have identified two potential candidates in the dataset: `MaQaUnc_hits` (raw count of uncertainty words) and `MaQaUnc_pct` (percentage of uncertainty words). The paper uses the term "frequency". Does this refer to the raw count or the normalized percentage?
*   **Variable $X_{speech}$ ($UncPreCEO$):** What is the exact column name for uncertainty frequency in the **Presentation**?
    *   **Clarification Needed:** Similarly, should I map this to `MaPresUnc_hits` or `MaPresUnc_pct`?
*   **Variable $X_{que}$ ($UncQue$):** What is the exact column name for uncertainty frequency in **Analyst Questions**?
    *   **Clarification Needed:** Should I map this to `AnaQaUnc_hits` or `AnaQaUnc_pct`?
*   [cite_start]**Variable $X_{neg}$ ($NegCall$):** The paper controls for "Negativity"[cite: 376]. What is the column name for the percentage of negative words?
    *   **Clarification Needed:** I have `EntireCallNeg_pct` available. Is this "Entire Call" scope correct, or does the paper require negativity restricted to a specific section (e.g., just the Q&A)?

### 2. The Financial Controls Status
Equation 4 explicitly controls for firm characteristics to isolate style . These are rarely found in "enriched linguistic" files (which usually just contain text analysis).

*   **Earnings Surprise ($SurpDec$):** Do you have a column for **Earnings Surprise Deciles**?
    *   **Clarification Needed:** The `f1d_enriched` file does not contain this. However, I verified that `1_Inputs/tr_ibes` contains `MEANEST` (Analyst Consensus) and `ACTUAL` (Actual Earnings). Do you want me to engineer this feature by calculating $(Actual - Mean) / Price$ and then deciling it, or are you expecting a pre-calculated "Surprise" column from a different source?
*   **Performance Metrics:** Do you have columns for **EPS Growth**, **Stock Returns**, and **Market Returns** in this specific file?
    *   **Clarification Needed (EPS Growth):** The standard Compustat variable `epspxq` is **missing** from `1_Inputs/comp_na_daily_all`. I can calculate **Basic EPS** using `ibq` (Income Before Extraordinary Items) divided by `cshoq` (Common Shares Outstanding). Is this calculated Basic EPS acceptable for your "EPS Growth" control, or does the paper strictly require **Diluted EPS** (which would require sourcing missing data)?
    *   **Clarification Needed (Stock Returns):** I have daily `RET` in `1_Inputs/CRSP_DSF`. What is the exact **time window** for the "Stock Returns" control variable? (e.g., Cumulative return over the fiscal quarter? Buy-and-hold return around the earnings announcement window $[-1, +1]$?)
    *   **Clarification Needed (Market Returns):** I have both `vwretd` (Value-Weighted Index including dividends) and `sprtrn` (S&P 500 Return) in `1_Inputs/CRSP_DSF`. Which specific market index does the paper uses for the $Market Returns$ control?

### 3. The Time-Series Granularity
*   **Time Fixed Effects ($Year_t$):** The paper typically uses **Year** fixed effects . However, some implementations use **Year-Quarter**.
    *   **Clarification Needed:** The dataset contains `start_date` (Calendar Date) and `business_quarter` (e.g., 2017Q2). Does the paper's "Year" fixed effect refer to the **Calendar Year** of the call, or the **Fiscal Year** of the firm? (If Fiscal Year is required, I need to link to Compustat's `fyearq`, as it is not currently in `f1d_enriched`).

### 4. Regression Configuration
To make the spec deterministic, I need to define the error handling and statistical rigor:
*   **Standard Errors:** The paper clusters standard errors by **Manager** ($CEO_{i}$) .
    *   **Clarification Needed:** I have confirmed `ceo_id` is present in the dataset. Do you need me to validate that this ID is unique per manager across different firms (to ensure proper clustering), or is the current `ceo_id` sufficient?
*   **Handling Nulls:** If a record has a valid `UncAns` score but is missing `EPS_Growth` (Control), does the developer **drop the row** or **impute** (fill) the value?
    *   **Clarification Needed:** Since the financial controls will come from an external join (which I have not yet performed), there will inevitably be unmatched records. What is the strict policy for the final regression sample: **(A) Listwise Deletion** (drop any call with missing controls), or **(B) Imputation** (fill missing controls with industry means/zeros)? This decision fundamentally changes the pipeline implementation.