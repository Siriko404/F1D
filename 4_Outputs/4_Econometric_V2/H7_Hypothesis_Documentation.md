# H7: Managerial Speech Uncertainty and Stock Illiquidity

**Generated:** 2026-02-10
**Source Script:** `2_Scripts/4_Econometric_V2/4.7_H7IlliquidityRegression.py`
**Results Date:** 2026-02-06 18:59:39

---

## Hypothesis Statements

### Theoretical Motivation

Managerial speech uncertainty may affect stock market liquidity through information channels:

#### Information Asymmetry Channel

Higher speech uncertainty increases information asymmetry between insiders and outsiders, leading to:
- **Adverse selection:** informed traders trade against uninformed traders
- **Wider bid-ask spreads:** market makers widen spreads to compensate for adverse selection risk
- **Lower trading volume:** investors reduce trading when information quality is poor
- **Higher illiquidity:** Amihud (2002) illiquidity measure increases

#### Predictions

**H7a:** Higher speech uncertainty leads to HIGHER stock illiquidity (lower liquidity).

$$H_7a: \beta > 0$$

A positive coefficient indicates that uncertainty increases illiquidity (worsens liquidity).

---

## Model Specification

### Regression Equation

$$
\text{Illiquidity}_{i,t} = \beta_0 + \beta_1 \cdot \text{Uncertainty}_{i,t} + \boldsymbol{\gamma} \cdot \text{Controls}_{i,t} + \alpha_i + \delta_t + \varepsilon_{i,t}
$$

where:
- $\text{Illiquidity}_{i,t}$ = Amihud (2002) illiquidity measure (see below)
- $\text{Uncertainty}_{i,t}$ = Speech uncertainty measure (4 primary variants)
- $\text{Controls}_{i,t}$ = Firm-level control variables (size, turnover, volatility, etc.)
- $\alpha_i$ = Firm fixed effects
- $\delta_t$ = Year fixed effects
- $\varepsilon_{i,t}$ = Error term

### Estimation Method

- **Estimator:** PanelOLS (Fixed Effects)
- **Fixed Effects:** Firm + Year
- **Standard Errors:** Clustered at firm level
- **Sample Period:** 2002-2018

### Dependent Variable

**Amihud (2002) Illiquidity Measure:**

$$
\text{Illiquidity}_{i,t} = \frac{1}{D_{i,t}} \sum_{d=1}^{D_{i,t}} \frac{|R_{i,d}|}{\text{Volume}_{i,d}}
$$

where:
- $R_{i,d}$ = Daily return
- $\text{Volume}_{i,d}$ = Daily trading volume (in dollars)
- $D_{i,t}$ = Number of trading days in year $t$

**Interpretation:** Higher values indicate HIGHER illiquidity (worse market quality). The measure captures the price impact of order flow—large absolute returns per dollar of trading volume indicate illiquidity.

**Sample statistics:**
- Mean: 0.0164
- Standard deviation: 0.0804
- Distribution: Right-skewed (few highly illiquid stocks)

---

## Primary Results

### Complete Results Table

| Uncertainty Measure | N | R² | β (SE) | t-stat | p (one-tailed) | FDR q | Significant? |
|---|---|---|---|---|---|---|---|
| Manager_QA_Uncertainty_pct | 26,135 | 0.0000 | 0.001253 (0.004389) | 0.29 | 0.3876 | 0.7753 | No |
| CEO_QA_Uncertainty_pct | 26,135 | 0.0000 | -0.004695 (0.003595) | -1.31 | 0.9041 | 0.9041 | No |
| Manager_Pres_Uncertainty_pct | 26,135 | 0.0000 | 0.004314 (0.005298) | 0.81 | 0.2078 | 0.7753 | No |
| CEO_Pres_Uncertainty_pct | 26,135 | 0.0000 | -0.001826 (0.005133) | -0.36 | 0.6390 | 0.8520 | No |

**Note:** Significance level: FDR-corrected p < 0.05, one-tailed (β > 0). H7a predicts β > 0 (uncertainty increases illiquidity). t-stats are calculated as coefficient/SE. FDR q is Benjamini-Hochberg corrected p-value for multiple testing.

---

## FDR Correction Results

### Multiple Testing Correction

| Uncertainty Measure | p (original) | p (FDR) | FDR Sig? |
|---|---|---|---|
| Manager_QA_Uncertainty_pct | 0.3876 | 0.7753 | No |
| CEO_QA_Uncertainty_pct | 0.9041 | 0.9041 | No |
| Manager_Pres_Uncertainty_pct | 0.2078 | 0.7753 | No |
| CEO_Pres_Uncertainty_pct | 0.6390 | 0.8520 | No |

**FDR Summary:**
- **Significant after FDR correction (q < 0.05):** 0/4
- **Significant uncorrected (p < 0.05):** 0/4
- **Lowest uncorrected p-value:** 0.2078 (not significant)

---

## Hypothesis Test Outcome

### H7a: β > 0 (Uncertainty → Higher Illiquidity)

**Result: NOT SUPPORTED**

- **Significant measures (FDR-corrected q < 0.05):** 0/4
- **Significant measures (uncorrected p < 0.05):** 0/4
- **Direction:** 2/4 positive (as hypothesized), 2/4 negative (opposite)
- **All p-values:** > 0.20 (far from significance)

**Interpretation:** No evidence that managerial speech uncertainty affects stock illiquidity. The coefficients are very small and statistically insignificant. The mixed direction (2 positive, 2 negative) suggests no systematic relationship.

---

## Sample Statistics

| Statistic | Value |
|---|---|
| **Total Observations** | 26,135 |
| **Firms** | 2,283 |
| **Sample Period** | 2002-2018 |
| **R²** | 0.0000 (all specifications) |
| **Dependent Variable Mean** | 0.016394 |
| **Dependent Variable Std** | 0.080429 |

### Sample Characteristics

- **Observations per firm:** Average 11.4 years per firm (26,135 / 2,283)
- **Unbalanced panel:** Some firms enter/exit sample during period
- **Annual observations:** Illiquidity measured at yearly frequency

### Model Fit

The R² = 0.0000 indicates that:
- Speech uncertainty explains virtually none of the illiquidity variation
- Most illiquidity variation is driven by unobserved factors
- Firm and year fixed effects absorb substantial variation

---

## Robustness Specifications

### Specification Comparison

| Spec | Entity FE | Time FE | Cluster | N | Signif (p<0.05) | Avg β |
|---|---|---|---|---|---|---|
| **primary** | Yes | Yes | firm | 26,135 | 0/4 | -0.000239 |
| **firm_only** | Yes | No | firm | 26,135 | 0/4 | -0.000144 |
| **pooled** | No | No | firm | 26,135 | 0/4 | -0.011523 |
| **double_cluster** | Yes | Yes | firm+year | 26,135 | 0/4 | -0.000239 |

**Robustness finding:** 0/4 measures significant across all specifications. Results are consistently null regardless of fixed effects or clustering strategy.

---

## Robustness Tests

### Alternative Dependent Variables

**Roll (1984) Illiquidity:** 0/4 significant, avg β = -0.000234
- Alternative illiquidity measure based on bid-ask spreads
- Also shows null effects

**Log Amihud Illiquidity:** 0/4 significant, avg β = -0.000000
- Log-transformed Amihud measure
- Also shows null effects

### Alternative Independent Variables

**CEO only:** 0/2 significant, avg β = -0.003260
- Only CEO speech measures
- Null results

**Presentation only:** 0/2 significant, avg β = 0.001244
- Only presentation speech measures
- Null results

**QA only:** 0/2 significant, avg β = -0.001721
- Only Q&A speech measures
- Null results

### Timing Tests

No timing tests were run (concurrent, forward, lead specifications not implemented).

### Robustness Summary

**Total robustness tests:** 14 specifications (4 primary + 10 alternative)

**Significant results (p < 0.05):** 0/14 (0.0%)

**Robustness Assessment:** Results are NOT ROBUST—no specifications show significant effects. The null finding is consistent across:
- Alternative illiquidity measures (Amihud, Roll, log Amihud)
- Alternative speech measures (CEO, presentation, QA only)
- Alternative specifications (primary, firm_only, pooled, double_cluster)

---

## Economic Interpretation

### Coefficient Magnitude

For **Manager_QA_Uncertainty_pct**, β = 0.001253 (SE = 0.004389, p = 0.3876):

$$
\frac{\partial \text{Illiquidity}}{\partial \text{Uncertainty}} = 0.001253
$$

**Interpretation:**
- A 1 percentage point increase in uncertainty increases illiquidity by 0.001253
- This effect is not statistically significant (p = 0.3876)
- Economic magnitude is negligible

**Economic significance:**
- Mean illiquidity: 0.0164
- Std illiquidity: 0.0804
- A 1 pp increase in uncertainty changes illiquidity by 0.001253
- This represents 1.6% of mean illiquidity or 1.6% of one standard deviation
- Effect is too small to be economically meaningful even if significant

### Negative Coefficients

For **CEO_QA_Uncertainty_pct**, β = -0.004695 (SE = 0.003595, p = 0.9041):

$$
\frac{\partial \text{Illiquidity}}{\partial \text{Uncertainty}} = -0.004695
$$

**Interpretation:**
- Negative coefficient (opposite of hypothesized direction)
- Not statistically significant
- Suggests no systematic relationship

---

## Mechanism Analysis

### Why Speech Uncertainty May Not Affect Illiquidity

**Potential explanations for null findings:**

1. **Market efficiency:** Stock prices may incorporate all publicly available information, including speech quality. Market participants may already price in communication quality.

2. **Alternative information sources:** Investors may rely more on financial statements, SEC filings, earnings guidance, and private research than managerial speech during conference calls.

3. **Measurement:** The Amihud illiquidity measure may not capture the dimension of market quality affected by speech uncertainty. Alternative measures (bid-ask spreads, price impact) also show null results.

4. **Sample composition:** The sample (26,135 observations, 2,283 firms) may be dominated by liquid stocks where illiquidity variation is limited. Small, illiquid stocks may drive both uncertainty and illiquidity, but firm fixed effects absorb this between-firm variation.

5. **Within-firm vs. between-firm:**
   - **Between-firm:** Some firms may have persistently high uncertainty and high illiquidity (correlation)
   - **Within-firm:** Changes in uncertainty over time may not affect illiquidity (causation)
   - Firm fixed effects control for between-firm differences, leaving only within-firm variation

---

## Limitations

### Statistical Power

The sample size (26,135 observations) provides reasonable power, but:
- R² = 0.0000 suggests very limited explanatory power
- Large standard errors relative to coefficients
- Small effect sizes (if any)

### Measurement Issues

1. **Illiquidity measurement:** Amihud measure may not capture all dimensions of liquidity
2. **Speech measurement:** Uncertainty measures may not capture the information dimensions relevant to market makers
3. **Timing:** Annual frequency may miss short-term liquidity effects

### Alternative Channels

Speech uncertainty may affect stock prices through channels other than liquidity:
- **Returns:** Cost of equity capital, stock returns
- **Volatility:** Return volatility, idiosyncratic risk
- **Analyst behavior:** Forecast accuracy, recommendation changes

These channels are not tested in H7.

---

## Conclusion

**H7a:** Managerial speech uncertainty does **NOT** significantly affect stock illiquidity. None of the 4 primary uncertainty measures show statistically significant effects at the 5% level (uncorrected or FDR-corrected).

**Robustness:** The null finding is highly robust across 14 specifications:
- Alternative illiquidity measures (Amihud, Roll, log Amihud)
- Alternative speech measure subsets (CEO, presentation, QA only)
- Alternative specifications (primary, firm_only, pooled, double_cluster)

**Overall:** No evidence that managerial speech uncertainty affects stock market liquidity as measured by the Amihud (2002) illiquidity measure. The R² = 0.0000 indicates that speech uncertainty explains virtually none of the cross-sectional or time-series variation in illiquidity after controlling for firm and year fixed effects.

**Implications:**
1. Market makers and traders may not incorporate managerial speech uncertainty into liquidity provision decisions
2. Information asymmetry from speech uncertainty may not translate into measurable illiquidity effects
3. Alternative market quality measures (returns, volatility) may be more relevant channels
4. Firm fixed effects absorb between-firm variation, suggesting illiquidity is primarily a firm-specific trait not affected by within-firm changes in speech

**Interpretation:** The null findings may reflect:
1. Genuinely zero causal effect (speech uncertainty doesn't affect liquidity)
2. Market efficiency (prices already incorporate speech quality)
3. Measurement limitations (illiquidity measure doesn't capture relevant dimension)
4. Within-firm identification (firm FE absorb between-firm correlation)

**Future research directions:**
1. Test alternative market quality measures (bid-ask spreads, price impact, trading volume)
2. Test alternative channels (returns, volatility, analyst behavior)
3. Explore between-firm differences (without firm FE) to see if correlated traits matter
4. Examine asymmetric effects (small vs. large firms, high vs. low liquidity stocks)

---

*This documentation provides complete regression results for academic supervisor review and thesis defense.*
