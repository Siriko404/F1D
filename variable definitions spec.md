### F1D Global Variable & Alignment Specifications

1.  **Earnings Standardization:** All variables referencing "Earnings" (Volatility, Payout Stability, Loss Dummy, ROA) must use *Income Before Extraordinary Items*. Use `ibq` for quarterly measures and `iby` for annual cumulative measures. Do not use Net Income (`niq`) or Earnings Per Share (`eps`) to avoid dimensional errors and restatement inconsistencies. If `iby`/`ibq` is entirely missing, fallback to `niy`/`niq`.
2.  **Annual Variable Extraction:** All annual flow variables (CAPEX, Dividends, Annual Sales, Annual Earnings) must be extracted exclusively from the Q4 fiscal row (e.g., `capxy`, `dvy`, `saley`, `iby`) to capture the official year-to-date total.
3.  **Look-Ahead Clarification (Contemporaneous Alignment):** This pipeline constructs a forensic panel to explain fiscal outcomes based on communication during the year. Q4 annual totals are intentionally joined back to Q1/Q2/Q3 calls of the *same fiscal year*. This is not a predictive trading backtest.
4.  **Forward Time Merges:** Any `Lead` or `t+1` forecast merge (e.g., IBES Dispersion Lead) must use a strictly forward merge (`statpers > call_date`) bounded by a 180-day tolerance to prevent matching against stale or distant-future forecasts when coverage drops.

## Leverage (one “most standard” construction)

### Definition

**Book leverage = total interest-bearing debt ÷ total assets**

[
\text{Leverage}_t=\frac{\text{Short-term interest-bearing debt}_t+\text{Long-term interest-bearing debt}_t}{\text{Total assets}_t}
]

### Components you need

* **Short-term interest-bearing debt**: debt due within 1 year (e.g., bank loans/notes payable/current portion of long-term debt).
* **Long-term interest-bearing debt**: debt due after 1 year (e.g., bonds, term loans, long-term notes).
* **Total assets**: the firm’s book total assets at the same date.

### How to construct (steps)

1. **Add** short-term + long-term **interest-bearing** debt to get **total debt**.
2. **Divide** total debt by **total assets** (same period).

## Cash holding (one most standard construction)

### Definition

[
\text{Cash holding}*{t}=\frac{\text{Cash and cash equivalents}*{t}}{\text{Total assets}_{t}}
]

### Components you need

* **Cash and cash equivalents** at time (t): cash on hand + demand deposits + highly liquid short-term investments that are treated as cash equivalents.
* **Total assets** at time (t): the firm’s total book assets on the balance sheet.

### How to construct

1. Take the firm’s **end-of-period** cash-and-cash-equivalents balance.
2. Take the firm’s **end-of-period** total assets balance.
3. Divide: cash-and-cash-equivalents ÷ total assets.



## Investment efficiency (Biddle, Hilary & Verdi 2009) — one standard construction

### What you need (firm-year inputs)

* **Capital expenditures**
* **R&D expenditures**
* **Cash paid for acquisitions**
* **Proceeds from sales of property, plant & equipment (PP&E)**
* **Total assets** (current year and prior year)
* **Sales (revenue)** (current year and prior year)
* **Industry classification** (to form industry groups)

---

### Step-by-step construction

1. **Compute total investment (scaled)**
   [
   INV_{i,t}=\frac{CAPEX_{i,t}+R&D_{i,t}+ACQ_{i,t}-SALEPPE_{i,t}}{ASSETS_{i,t-1}}
   ]

2. **Compute sales growth**
   [
   SG_{i,t}=\frac{SALES_{i,t}-SALES_{i,t-1}}{SALES_{i,t-1}}
   ]

3. **Estimate “expected investment” within each industry-year**
   Run this cross-sectional regression **separately for each (industry, year)**:
   [
   INV_{i,t+1}=\alpha_{j,t}+\beta_{j,t} \times SG_{i,t}+\varepsilon_{i,t+1}
   ]
   (where (j) indexes industry)

4. **Define investment inefficiency (and efficiency)**

* **Inefficiency**:
  [
  INEFF_{i,t+1}=|\varepsilon_{i,t+1}|
  ]
* **Efficiency** (monotone transform used in practice):
  [
  EFF_{i,t+1}=-|\varepsilon_{i,t+1}|
  ]

**Interpretation**: larger (|\varepsilon|) means actual investment deviates more from the level predicted by opportunities (proxied by sales growth) within the firm’s industry-year.


## Earnings volatility (one standard construction)

**Definition (most standard):**
The **rolling standard deviation of profitability**, where profitability is **earnings scaled by assets**.

### Components needed

* **Earnings** (an accounting earnings measure, consistently defined across firms and time)
* **Total assets**
* A **lookback window** (standard is **5 years** of annual observations)
* A **minimum-history rule** (e.g., require **at least 3** non-missing years inside the window)

### Construction (at year (t))

1. **Compute profitability each year**
   [
   p_{i,\tau}=\frac{E_{i,\tau}}{A_{i,\tau}}
   ]

2. **Compute earnings volatility as a rolling SD**
   [
   \text{EarningsVol}*{i,t}=\operatorname{SD}\left(p*{i,t-4},,p_{i,t-3},,p_{i,t-2},,p_{i,t-1},,p_{i,t}\right)
   ]

That’s it: **5-year rolling SD of earnings-to-assets** (profitability).


## Cash flow volatility (one standard construction)

**Definition (firm (i), year (t)):**
[
\text{CFVol}*{i,t}=\operatorname{SD}\left(\frac{\text{Operating Cash Flow}*{i,\tau}}{\text{Total Assets}_{i,\tau-1}}\right)\quad \text{for } \tau=t-4,\dots,t
]

### Components you need

* **Operating cash flow** (cash generated from core operations) for each year (\tau).
* **Total assets** for each year (\tau-1) (lagged one year).

### How to construct (exact steps)

1. For each year (\tau), compute the scaled cash-flow ratio:
   [
   x_{i,\tau}=\frac{\text{Operating Cash Flow}*{i,\tau}}{\text{Total Assets}*{i,\tau-1}}
   ]
2. Using the **last 5 years** ((t-4 \text{ to } t)), take the **standard deviation** of (x_{i,\tau}):
   [
   \text{CFVol}*{i,t}=\sqrt{\frac{1}{N-1}\sum*{\tau=t-4}^{t}\left(x_{i,\tau}-\bar{x}_{i,t}\right)^2}
   ]
   where (N=5) (or fewer only if you explicitly allow it; most papers require a full window).

## Firm size (single most standard construction)

**Definition**
[
\text{Firm Size}*{t}=\ln(\text{Total Assets}*{t})
]

**Components needed**

* **Total Assets at time (t)**: the balance-sheet measure of the firm’s total asset base (book value).

**How to construct**

1. Take the firm’s **total assets** for period (t).
2. Compute the **natural logarithm** of that value.

**Result**: a scale proxy with reduced skewness and more stable regression behavior.


## ROA (one most standard construction)

[
\text{ROA}_t ;=; \frac{\text{Net income}_t}{\frac{\text{Total assets}*t+\text{Total assets}*{t-1}}{2}}
]

### Components you need

* **Net income (period (t))**: profit after all expenses and taxes for the same period.
* **Total assets (end of period (t) and (t-1))**: balance-sheet total assets at the end of the current and prior period.

### Construction steps

1. Compute **average total assets**:
   [
   \text{AvgAssets}_t=\frac{\text{Assets}*t+\text{Assets}*{t-1}}{2}
   ]
2. Compute ROA:
   [
   \text{ROA}_t=\frac{\text{Net income}_t}{\text{AvgAssets}_t}
   ]


## Tobin’s Q (one most standard construction)

### Definition (standard proxy)

[
Q ;=;\frac{\text{Market value of equity} ;+; \text{Book value of debt}}{\text{Book value of total assets}}
]

### Components you need

* **Market value of equity (MVE)**:
  [
  \text{MVE} = (\text{share price at measurement date}) \times (\text{shares outstanding})
  ]
* **Book value of debt (Debt_book)**:
  [
  \text{Debt_book} = (\text{short-term interest-bearing debt}) + (\text{long-term interest-bearing debt})
  ]
* **Book value of total assets (Assets_book)**: total assets from the balance sheet.

### Construction steps

1. Compute **MVE** as price × shares.
2. Compute **Debt_book** as short-term debt + long-term debt.
3. Compute:
   [
   Q = \frac{\text{MVE} + \text{Debt_book}}{\text{Assets_book}}
   ]

That’s the common “growth opportunities” proxy used in mainstream corporate finance regressions.


## Industry capex intensity (one “most standard” construction)

**Definition (industry-year):** the **median** firm capex intensity among all firms in the same industry in year (t).

### Components you need

* **Capital expenditures** for each firm-year: (Capex_{i,t})
* **Lagged total assets** for each firm-year: (Assets_{i,t-1})
* An **industry classification** that assigns each firm to an industry (j) (e.g., a standard SIC/NAICS-style mapping)
* A **year** identifier (t)

### Construction (steps)

1. Compute **firm capex intensity**:
   [
   CapexIntensity_{i,t}=\frac{Capex_{i,t}}{Assets_{i,t-1}}
   ]

2. For each **industry (j)** and **year (t)**, compute the **cross-sectional median**:
   [
   IndustryCapexIntensity_{j,t}=\text{median}*{i \in (j,t)}\left(CapexIntensity*{i,t}\right)
   ]

That’s the standard industry-level capex intensity control used in corporate finance panels.


## Firm CAPEX intensity (one standard construction)

**Definition**
[
\text{CAPEX Intensity}*{t} ;=; \frac{\text{Capital Expenditures}*{t}}{\text{Total Assets}_{t-1}}
]

**Components you need**

* **Capital Expenditures(_t)**: cash outlays in period (t) for acquiring/constructing long-lived tangible assets (property, plant, equipment). Use the line item that captures *gross* CAPEX spending for the period.
* **Total Assets(_{t-1})**: book value of total assets at the **end of the prior period**.

**Construction steps**

1. Take **CAPEX** for period (t).
2. Take **total assets** from the end of period (t-1).
3. Divide: ( \text{CAPEX}*t / \text{Assets}*{t-1} ).

**Practical conventions**

* If ( \text{Assets}_{t-1} \le 0 ) or missing → set to missing (don’t compute).
* Often winsorize the ratio (e.g., 1st/99th percentile) due to outliers.


## Firm maturity (one most standard construction)

### Definition

Use the **retained-earnings-to-assets ratio**:

[
\text{Maturity}*{t}=\frac{\text{Retained Earnings}*{t}}{\text{Total Assets}_{t}}
]

### Components you need

* **Retained earnings (cumulative)**: the balance-sheet account that equals *cumulative net income minus cumulative dividends (and other direct equity adjustments, depending on accounting)* up to time (t).
* **Total assets**: the firm’s total asset value at time (t).

### How to construct (steps)

1. At each date (t), take **retained earnings** from the balance sheet.
2. Take **total assets** at the same date (t).
3. Compute the ratio above.

### Interpretation

* **Higher** (RE/TA) ⇒ more “mature” (more internally generated capital accumulated over time).
* **Lower/negative** (RE/TA) ⇒ younger / growth-stage / less accumulated profits (or a history of losses/dividends exceeding cumulative profits).

## Firm maturity (one most standard construction)

### Definition

Use the **retained-earnings-to-assets ratio**:

[
\text{Maturity}*{t}=\frac{\text{Retained Earnings}*{t}}{\text{Total Assets}_{t}}
]

### Components you need

* **Retained earnings (cumulative)**: the balance-sheet account that equals *cumulative net income minus cumulative dividends (and other direct equity adjustments, depending on accounting)* up to time (t).
* **Total assets**: the firm’s total asset value at time (t).

### How to construct (steps)

1. At each date (t), take **retained earnings** from the balance sheet.
2. Take **total assets** at the same date (t).
3. Compute the ratio above.

### Interpretation

* **Higher** (RE/TA) ⇒ more “mature” (more internally generated capital accumulated over time).
* **Lower/negative** (RE/TA) ⇒ younger / growth-stage / less accumulated profits (or a history of losses/dividends exceeding cumulative profits).


## Analyst dispersion (one standard construction)

**Goal:** measure how much analysts **disagree** about a firm’s earnings *before* the earnings announcement.

### Components needed (for each firm–period)

* A set of **individual analyst earnings forecasts** for the same target period (e.g., the upcoming quarter or fiscal year).
* A **snapshot date** close to (but before) the earnings announcement (common: the last trading day before the announcement, or a fixed window like 30 days prior).
* A rule to keep **one forecast per analyst** as of the snapshot (use each analyst’s **most recent** forecast on or before the snapshot).

### Construction

1. Collect all analysts’ latest forecasts as of the snapshot.
2. Compute:
   [
   \text{Dispersion} ;=; \frac{\text{Standard Deviation of forecasts}}{\left|\text{Mean of forecasts}\right|}
   ]
   (= **coefficient of variation**)

### Practical rule

* Require at least **2 analysts** (often 3+ in practice).
* If the mean forecast is **0 or extremely close to 0**, treat dispersion as missing (or use an alternative scaling, but that would be a different definition).


## Amihud illiquidity (one “most standard” construction)

### Definition (daily → annual)

For stock (i) in year (y),
[
ILLIQ_{i,y}=\frac{1}{D_{i,y}}\sum_{d=1}^{D_{i,y}}\frac{|R_{i,d}|}{DVOL_{i,d}}
]

### Components you need (per trading day (d))

* **Daily return** (R_{i,d}): close-to-close simple return
  [
  R_{i,d}=\frac{P_{i,d}-P_{i,d-1}}{P_{i,d-1}}
  ]
* **Daily dollar trading volume** (DVOL_{i,d}):
  [
  DVOL_{i,d}=P_{i,d}\times VOL_{i,d}
  ]
  where (P_{i,d}) is the daily close price and (VOL_{i,d}) is shares traded that day.
* **Trading-day count** (D_{i,y}): number of valid trading days in that year after cleaning.

### Construction steps

1. For each trading day, compute (R_{i,d}) and (DVOL_{i,d}).
2. Compute the daily ratio (|R_{i,d}|/DVOL_{i,d}).
3. Average that ratio across all valid trading days in the year to get (ILLIQ_{i,y}).

**Interpretation:** higher (ILLIQ) ⇒ less liquid (more price movement per dollar traded).


## Earnings surprise (one “most standard” construction)

**Definition**
[
\text{Earnings Surprise}*{t}=\text{Actual EPS}*{t}-\text{Expected EPS}_{t}
]

### Components you need

1. **Actual EPS for the quarter**

* The EPS number reported for that quarter (use the same EPS definition consistently across all firms).

2. **Expected EPS (market expectation right before the announcement)**

* The **consensus** expectation computed from analysts’ EPS forecasts, using only forecasts **issued before** the earnings announcement time.

3. **Announcement timestamp/date**

* To ensure forecasts are truly “pre-announcement”.

### Construction steps

1. For each firm-quarter, collect all **analyst EPS forecasts** for that quarter with forecast timestamp **< announcement timestamp**.
2. Form the **consensus expected EPS** as the **mean** of those pre-announcement forecasts.
3. Compute:
   [
   \text{Surprise}*{t}=\text{Actual EPS}*{t}-\text{Consensus Expected EPS}_{t}
   ]

### Minimal standard hygiene (still “standard”)

* Require **at least 2 forecasts** to form a consensus.
* Ensure **actual EPS and forecasts are on the same per-share basis** (split-adjusted / same share count convention), otherwise the subtraction is meaningless.



## Negative earnings dummy
Core idea

A simple indicator for loss firms (often used because losses distort ratios and signals constraints/distress).

Standard construction
NegEarnDummy
𝑡
=
1
[
Earnings
𝑡
<
0
]
NegEarnDummy
t
	​

=1[Earnings
t
	​

<0]

Common earnings definitions:

income before extraordinary items (Compustat 
𝐼
𝐵
IB)
A standard variable definition you’ll see is LOSS = 1 if negative income before extraordinary items.

Implementation notes

Decide whether “earnings” means NI, IB, EBIT, or EPS and stick to it.


## Dividend payout stability (one “most standard” construction)

**Definition (rolling smoothness of the payout ratio)**

1. Annual payout ratio (only when earnings are positive):
   [
   \text{PayoutRatio}_{t}=\frac{\text{Cash dividends paid in year }t}{\text{Earnings in year }t}
   ]

2. Dividend payout stability at year (t) = *low variability* of that ratio over a trailing window:
   [
   \text{PayoutStability}*{t}=-,SD!\left(\text{PayoutRatio}*{t-5},\ldots,\text{PayoutRatio}_{t-1}\right)
   ]
   (negative sign so **higher = more stable**.)

### Components you need

* **Cash dividends paid** over the fiscal year (cash paid to shareholders).
* **Earnings** for the same fiscal year (consistent earnings definition across firms).
* **A trailing window length** (most commonly **5 years**) and fiscal-year alignment.

### Construction steps

1. For each firm-year, compute (\text{PayoutRatio}_{t}) **only if earnings (>0)** (otherwise set missing).
2. For each firm-year (t), take the **standard deviation** of (\text{PayoutRatio}) over the prior **5 years** ((t-5 \text{ to } t-1)).
3. Multiply by (-1) to convert “more variable” into “less stable”.

### Minimal standard hygiene

* Require **at least 3 valid years** in the 5-year window to compute the SD.
* Use the **same dividend and earnings definitions** for numerator/denominator everywhere.
