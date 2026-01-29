# Analysis of Takeover Hazards (Step 2.10)

## Overview
This analysis examines how CEO communication clarity affects takeover vulnerability. We use both:
1. **ClarityCEO** (CEO Fixed Effect) - Time-invariant individual CEO style
2. **MaPresUnc_pct** (Call-Level) - Presentation uncertainty in specific earnings calls

**Sample:** 75,379 firm-quarters (2002-2020) with 95.4% CEO clarity coverage

| Event Type | N | % |
|------------|---|---|
| Uninvited (Hostile+Unsolicited) | 1,528 | 2.0% |
| Friendly | 11,732 | 15.6% |
| Censored (No Takeover) | 62,119 | 82.4% |

---

## Key Results Summary

| Variable | All Takeovers (HR) | Uninvited (HR) | Friendly (HR) |
|----------|-------------------|----------------|---------------|
| **ClarityCEO** | 1.04 (**) | ** 1.17 (***) ** | 1.02 (ns) |
| **MaPresUnc_pct** | 0.44 (***) | ** 0.15 (***) ** | 0.49 (***) |
| **F1_PO** (Peer Surprise) | 1.21 (***) | ** 2.04 (***) ** | 1.14 (***) |
| **F1_HO** (History Surprise) | 1.12 (***) | 0.97 (ns) | 1.14 (***) |

*HR = Hazard Ratio. HR > 1 increases takeover risk, HR < 1 reduces it.*

---

## Hypothesis 5: Vagueness Levels & Takeover Likelihood

### CEO Clarity (Fixed Effect)
- **ClarityCEO HR = 1.04** (p < 0.001)
- **Interpretation:** CEOs with *higher* clarity scores (clearer communicators) have a 4% higher takeover hazard per unit increase.
- **Note:** ClarityCEO is defined as *absence* of uncertainty, so positive coefficient means *clarity increases risk* (or equivalently, *vagueness protects*).

### Call-Level Presentation Uncertainty
- **MaPresUnc_pct HR = 0.44** (p < 0.001)
- **Interpretation:** A one-unit increase in presentation uncertainty reduces the hazard of being taken over by **56%**. Vagueness acts as a **defensive fog**.

---

## Hypothesis 6: Differential Sensitivity (Uninvited vs. Friendly)

### ClarityCEO
| Takeover Type | HR | p-value | Interpretation |
|---------------|--------|---------|----------------|
| **Uninvited** | **1.17** | <0.001 | Hostile raiders target *clear* CEOs |
| **Friendly** | 1.02 | 0.051 (ns) | Friendly acquirers neutral to CEO style |

**Insight:** Uninvited acquirers are ~17% more likely to target clear-communicating CEOs per unit of clarity. This suggests hostile raiders exploit **information availability**: clear CEOs reveal more about firm operations, enabling value identification.

### Peer Surprise (F1_PO)
| Takeover Type | HR | p-value | Interpretation |
|---------------|--------|---------|----------------|
| **Uninvited** | **2.04** | <0.001 | Abnormal vagueness provokes hostile bids |
| **Friendly** | 1.14 | <0.001 | Slight increase for friendly |

**Critical Finding:** When a CEO is *unexpectedly vague* compared to industry peers, the hazard of an uninvited takeover bid **doubles** (HR = 2.04). Hostile acquirers interpret peer-deviation as a signal worth attacking.

### History Surprise (F1_HO)
| Takeover Type | HR | p-value | Interpretation |
|---------------|--------|---------|----------------|
| **Uninvited** | 0.97 | 0.67 (ns) | Hostile raiders don't monitor firm history |
| **Friendly** | **1.14** | <0.001 | Friendly acquirers track firm trajectories |

**Interpretation:** Friendly acquirers conduct long-term due diligence and detect when vagueness increases relative to *firm's own history*. Hostile raiders lack this longitudinal view.

---

## Hypothesis 7: Kinematics (Velocity & Acceleration)

| Variable | All (p) | Uninvited (p) | Friendly (p) |
|----------|---------|---------------|--------------|
| F1_HO_v (Velocity) | 0.18 (ns) | 0.94 (ns) | 0.14 (ns) |
| F1_HO_a (Acceleration) | 0.24 (ns) | 0.99 (ns) | 0.20 (ns) |

**Result: NOT SUPPORTED**  
Neither velocity nor acceleration of uncertainty changes predict takeover timing. The market responds to **levels and shocks**, not derivatives.

---

## Control Variables

| Variable | Uninvited HR | Friendly HR | Interpretation |
|----------|--------------|-------------|----------------|
| **Size** | 1.07 (***) | 0.96 (***) | Larger firms attract hostile bids, deter friendly |
| **BM** | 1.29 (***) | 0.90 (***) | Value firms (high BM) attract raiders |
| **Leverage** | 0.51 (***) | 1.35 (***) | Leverage: defense vs. hostile, magnet for friendly |
| **ROA** | 0.35 (ns) | 0.24 (***) | Poor profitability attracts friendly restructuring |

---

## Cumulative Incidence (18 years)
- **Uninvited (Hostile+Unsolicited):** 2.5%
- **Friendly:** 24.4%

---

## Conclusions

1. **CEO Clarity Makes You a Target (for Raiders)**
   - ClarityCEO HR=1.17 for uninvited bids. Hostile acquirers exploit transparency.

2. **Call-Level Vagueness Protects**
   - MaPresUnc_pct HR=0.15 for uninvited bids. Vagueness is a "fog of war" defense.

3. **Peer Surprises Provoke Attacks**
   - F1_PO HR=2.04 for uninvited bids. Abnormal vagueness triggers hostile attention.

4. **Friendly Acquirers Monitor History**
   - F1_HO significant only for friendly bids. They track firm-specific trajectories.

5. **Kinematics Don't Matter**
   - Velocity/acceleration of vagueness not predictive. Levels dominate.

**Managerial Implication:** CEOs face a **clarity paradox**: transparency attracts hostile raiders, but sudden opacity also signals distress. The safest strategy is *consistently moderate* vagueness.
