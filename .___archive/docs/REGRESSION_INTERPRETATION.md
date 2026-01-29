# Regression Results Interpretation Guide

*A comprehensive analysis for non-experts to understand the findings*

---

## Table of Contents
1. [Executive Summary](#executive-summary)
2. [Understanding the Research Question](#understanding-the-research-question)
3. [Step 2.9b: Liquidity Regression Results](#step-29b-liquidity-regression-results)
4. [Step 2.10: Takeover Hazards Results](#step-210-takeover-hazards-results)
5. [Big Picture: What This All Means](#big-picture-what-this-all-means)

---

## Executive Summary

We ran two types of analyses:

1. **Liquidity Analysis (Step 2.9b)**: How does CEO communication clarity affect how easily investors can buy/sell a company's stock?

2. **Takeover Analysis (Step 2.10)**: How does CEO communication clarity affect the likelihood that a company becomes a takeover target?

**Key Finding**: CEO Clarity appears to increase takeover risk, but does not strongly affect market liquidity after controlling for other factors.

---

## Understanding the Research Question

### What is "CEO Clarity"?
CEO Clarity measures how clearly a CEO communicates during earnings calls. A CEO with high clarity uses simple, direct language. A CEO with low clarity uses vague, confusing, or overly complex language.

### What is "Presentation Uncertainty" (MaPresUnc_pct)?
This measures how much uncertainty language is present in the CEO's prepared remarks during the earnings call presentation section. Higher values mean the CEO is using more uncertain language like "might," "could," "uncertain," etc.

### Why Do We Care?
The hypothesis is that how CEOs communicate affects investor behavior:
- **Unclear communication** → investors are uncertain → they may trade less → stock becomes less liquid
- **Clear, confident communication** → investors pay more attention → the company may attract acquirers

---

## Step 2.9b: Liquidity Regression Results

### The Data
- **80,161 earnings call observations** (OLS model)
- **39,882 observations** (IV model, fewer due to matching requirements)
- **Dependent Variable**: Amihud Illiquidity Ratio (higher = stock is HARDER to trade)

### Model 1: Simple OLS (Ordinary Least Squares)

**What is OLS?**
OLS is like drawing the "best fit line" through a scatter plot. It finds the relationship between X (our variables) and Y (illiquidity) that minimizes prediction errors.

#### Results:
| Variable | Coefficient | t-statistic | p-value | Interpretation |
|----------|-------------|-------------|---------|----------------|
| **MaPresUnc_pct** | 0.0253 | 0.94 | 0.35 | NOT statistically significant |
| **ClarityCEO** | 0.0129 | 1.88 | 0.06 | Marginally significant (p < 0.10) |

**R² = 0.0007** (0.07% of variance explained)

#### Breaking Down the Math:

For **MaPresUnc_pct** (coefficient = 0.0253):
- **What it means**: For every 1 percentage point increase in presentation uncertainty, illiquidity increases by 0.0253 units
- **Is it significant?**: The p-value is 0.35, meaning there's a 35% chance we'd see this result even if there's NO real relationship. Scientists typically require p < 0.05 (less than 5% chance of randomness). So **NO, this is not statistically significant**.

For **ClarityCEO** (coefficient = 0.0129):
- **What it means**: CEOs who score 1 point higher on clarity have stocks with 0.0129 units higher illiquidity
- **Is it significant?**: The p-value is 0.06 (6%). This is close to the threshold. We mark it with * to indicate "marginally significant"
- **The direction is surprising**: Higher clarity → MORE illiquidity? This is counterintuitive.

**Why is R² so low?**
R² of 0.0007 means our variables explain only 0.07% of the variation in illiquidity. Stock liquidity is determined by many factors: company size, trading volume, market conditions, etc. Our linguistic variables capture only a tiny slice of what drives liquidity.

### Model 2: Instrumental Variables (IV / 2SLS)

**Why use IV?**
There's a problem with OLS called "endogeneity." Maybe companies with liquidity problems hire CEOs who speak unclearly, rather than unclear speech causing liquidity problems. We can't tell which causes which!

IV solves this using an "instrument" - something that affects our variable (MaPresUnc) but doesn't directly affect liquidity. We use **CCCL shift intensity** - a measure of regulatory changes in disclosure requirements.

**The logic**:
```
Regulatory Changes → Force CEOs to speak differently → Affects Uncertainty → Affects Liquidity
        ↑                                                                          ↑
   (Instrument)                                                     (Only through this path!)
```

#### Kleibergen-Paap F-statistic = 50.96

**What is this?**
This tests whether our instrument is "strong." If the F-stat > 10, the instrument is good. Our value of **50.96 is excellent** - meaning regulatory changes really do affect how CEOs speak.

#### IV Results:
| Variable | Coefficient | t-statistic | p-value | Interpretation |
|----------|-------------|-------------|---------|----------------|
| **MaPresUnc_pct** | -0.10 | - | 0.97 | NOT significant |
| **ClarityCEO** | 0.013 | - | 0.91 | NOT significant |

**Key insight**: After properly accounting for endogeneity, NEITHER variable is statistically significant. This suggests that CEO communication style may not causally affect stock liquidity, or the effect is too small to detect.

---

## Step 2.10: Takeover Hazards Results

### The Data
- **85,540 earnings calls** analyzed
- **2,681 takeover events** identified via CUSIP matching with SDC M&A database
- **2,393 Friendly+Neutral takeovers**
- **288 Hostile+Unsolicited (Uninvited) takeovers**

### What is Survival Analysis?

Instead of asking "Does X relate to Y?", survival analysis asks: **"How does X affect the TIME until an event happens?"**

Think of it like this:
- Regular regression: "Are taller people heavier?"
- Survival analysis: "Do taller people live longer?"

Here, the "event" is becoming a takeover target, and the "time" is measured in quarters from each earnings call.

### Understanding Hazard Ratios (HR) and Subdistribution Hazard Ratios (SHR)

**Hazard Ratio (HR)**:
- HR = 1.0: No effect on takeover risk
- HR > 1.0: INCREASES takeover risk
- HR < 1.0: DECREASES takeover risk

**Example**: HR = 1.11 means the risk of takeover is 11% higher for each 1-unit increase in the variable.

### Model 1: Cox Proportional Hazards (All Takeovers)

**What is Cox PH?**
Cox Proportional Hazards is the most common survival analysis method. It estimates how covariates (our variables) affect the "hazard rate" - the instantaneous risk of an event happening.

#### Results (N = 2,681):
| Variable | Hazard Ratio | Coefficient | p-value | Significance |
|----------|-------------|-------------|---------|--------------|
| **MaPresUnc_pct** | 0.85 | -0.16 | 0.004 | ** |
| **ClarityCEO** | 1.11 | 0.11 | <0.001 | *** |

#### Interpretation:

**MaPresUnc_pct (HR = 0.85)**:
- Each 1 percentage point increase in presentation uncertainty DECREASES takeover risk by 15%
- **Why?** When CEOs sound uncertain, investors may value the company lower, making it a less attractive acquisition target. Or, uncertainty signals hidden problems that scare off potential acquirers.
- **Statistically significant**: p = 0.004 (very unlikely by chance)

**ClarityCEO (HR = 1.11)**:
- Each 1-point increase in CEO clarity INCREASES takeover risk by 11%
- **Why?** Clear communicators may signal a well-run company that's attractive to acquirers. Or, clarity reveals information that helps acquirers identify undervalued targets.
- **Highly significant**: p < 0.001 (very strong evidence)

### Model 2: Fine-Gray Competing Risks (Friendly+Neutral Takeovers)

**What is Competing Risks?**
Normal survival analysis treats all non-events the same. But in reality, companies can exit our study due to:
1. Being acquired in a **friendly** deal
2. Being acquired in a **hostile** deal
3. Just not being acquired (censored)

These are "competing" events. Fine-Gray handles this by modeling the **subdistribution hazard** - the risk of a specific event type while keeping other event types in the risk set.

#### Results (N = 2,393 Friendly+Neutral events):
| Variable | Subdist. HR | Coefficient | p-value | Significance |
|----------|-------------|-------------|---------|--------------|
| **MaPresUnc_pct** | 0.82 | -0.20 | <0.001 | *** |
| **ClarityCEO** | 1.10 | 0.09 | <0.001 | *** |

**Interpretation for Friendly Takeovers**:
- **Uncertainty (SHR = 0.82)**: Higher uncertainty reduces friendly takeover risk by 18% per unit
- **Clarity (SHR = 1.10)**: Clearer CEOs have 10% higher friendly takeover risk per unit

Both effects are highly significant. Friendly acquirers seem to prefer companies with clear, confident leadership.

### Model 3: Fine-Gray Competing Risks (Hostile+Unsolicited Takeovers)

#### Results (N = 288 events):
| Variable | Subdist. HR | Coefficient | p-value | Significance |
|----------|-------------|-------------|---------|--------------|
| **MaPresUnc_pct** | 1.16 | 0.15 | 0.36 | NOT significant |
| **ClarityCEO** | 1.23 | 0.21 | 0.001 | *** |

**Interpretation for Hostile Takeovers**:
- **Uncertainty**: No significant effect on hostile takeover risk
- **Clarity (SHR = 1.23)**: Clearer CEOs have 23% higher hostile takeover risk per unit (p = 0.001)

**This is a striking finding**: CEO clarity significantly increases BOTH friendly and hostile takeover risk, but the effect is larger for hostile takeovers (23% vs 10%).

Possible explanations:
1. Clear communication reveals information that helps hostile bidders identify undervalued targets
2. Clarity signals strong management that hostile acquirers want to obtain
3. Clear companies may be perceived as better investments, attracting all types of interest

---

## Big Picture: What This All Means

### Summary of Findings

| Outcome | MaPresUnc Effect | ClarityCEO Effect |
|---------|------------------|-------------------|
| **Liquidity (OLS)** | No effect | Weak effect |
| **Liquidity (IV)** | No effect | No effect |
| **All Takeovers** | ↓ Risk (-15%) | ↑ Risk (+11%) |
| **Friendly Takeovers** | ↓ Risk (-18%) | ↑ Risk (+10%) |
| **Hostile Takeovers** | No effect | ↑ Risk (+23%) |

### Key Takeaways

1. **CEO Clarity Increases Takeover Risk**
   - This is the most robust finding across all survival models
   - The effect is LARGER for hostile takeovers than friendly ones
   - This challenges the assumption that clearer communication is always "better" for the company

2. **Presentation Uncertainty Reduces Friendly Takeover Risk**
   - CEOs who sound more uncertain may be signaling lower value or hidden problems
   - This discourages potential acquirers

3. **Liquidity Effects Are Weak or Absent**
   - After proper econometric controls (IV), CEO communication doesn't significantly affect stock liquidity
   - Stock liquidity is driven by factors beyond what occurs in earnings calls

### Caveats and Limitations

1. **Correlation ≠ Causation**: Even with IV, we can't perfectly establish causality
2. **Selection Bias**: Only publicly traded companies with earnings calls are included
3. **Measurement**: "Clarity" is a model-based estimate, not a perfect measure
4. **Time Period**: Results may not generalize to other market conditions

---

## Glossary

| Term | Definition |
|------|------------|
| **Amihud Ratio** | A measure of stock illiquidity; higher values = harder to trade |
| **Coefficient** | The change in Y for a 1-unit change in X |
| **Competing Risks** | When multiple event types can occur; occurrence of one prevents others |
| **Cox PH** | Cox Proportional Hazards; a survival analysis method |
| **Endogeneity** | When the "cause" and "effect" may influence each other |
| **Fine-Gray** | A method for competing risks that models subdistribution hazards |
| **Hazard Ratio** | How much a variable multiplies the risk of an event |
| **Instrument (IV)** | A variable that affects X but not Y directly |
| **KP F-stat** | Kleibergen-Paap F-statistic; tests instrument strength |
| **OLS** | Ordinary Least Squares; finding the best-fit line |
| **p-value** | Probability of seeing results by chance if no real effect exists |
| **R²** | Proportion of variance in Y explained by X |
| **Subdistribution Hazard** | Risk of a specific event while keeping competing risks in the risk set |
| **2SLS** | Two-Stage Least Squares; the IV estimation method |

---

*Generated: 2025-12-08*
