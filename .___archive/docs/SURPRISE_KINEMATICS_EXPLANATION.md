# Surprise & Kinematics: Math, Intuition, and Examples

This document details the mathematical framework and intuition behind the "Information Surprise" variables used in Step 2.10.

---

## 1. The Core Variable: $X_{i,t}$
Let **$X_{i,t}$** be the **Uncertainty Score** (e.g., `MaPresUnc_pct`) for Firm $i$ in Quarter $t$.
*   **Example Scenario**: "TechCorp" (Firm A) and "BioInc" (Firm B).
*   **Context**: Quarter 1 was calm. Quarter 2 is the 2008 Financial Crisis (everyone is uncertain).

---

## 2. The "Global Surprise": F1 (Standardized Z-Score)

### The Math
$$ F1_{i,t} = \frac{X_{i,t} - \mu_t}{\sigma_t} $$

*   $\mu_t$: The average uncertainty of **all firms** in the market at time $t$.
*   $\sigma_t$: The standard deviation of uncertainty across **all firms** at time $t$.

### The Intuition
This removes the "market mood."
*   **Q1 (Calm)**: Average uncertainty is 1%. TechCorp is 2%. TechCorp is high (F1 > 0).
*   **Q2 (Crisis)**: Average uncertainty explains to 5%. TechCorp is 5%.
    *   Raw score increased (1% -> 5%), but relative to the market, TechCorp is now **average** (F1 = 0).
    *   The "Surprise" isn't the raw value; it's the deviation from the norm.

### Example
*   **TechCorp Q2**: Raw = 5%. Market Mean = 5%. SD = 1%.
*   $$ F1_{Tech,Q2} = (5 - 5) / 1 = 0.0 $$ (No global surprise)

---

## 3. Peer-Orthogonalized Surprise: F1_PO

### The Math
$$ F1\_PO_{i,t} = F1_{i,t} - \mu_{Industry, t} $$

*   $\mu_{Industry, t}$: The average $F1$ score for all firms in the **same industry** (SIC2).

### The Intuition
This isolates the firm from its industry.
*   Maybe the specific *Tech measure* implies high uncertainty, but TechCorp is actually the *clearest* tech company, even if it's vaguer than a bank.
*   **Orthogonalization**: We define "Peer Surprise" as the part of the variance **uncorrelated** with the industry average.

### Example
*   **TechCorp Q2**: $F1 = 0.0$.
*   **Tech Industry Mean**: The industry is panicked, average $F1 = +1.0$ (1 SD above market).
*   $$ F1\_PO = 0.0 - 1.0 = -1.0 $$
*   **Interpretation**: TechCorp is **surprisingly clear** (-1.0) relative to its panicked peers.

---

## 4. History-Orthogonalized Surprise: F1_HO

### The Math
$$ F1\_HO_{i,t} = F1_{i,t} - \frac{1}{4}\sum_{k=1}^{4} F1_{i,t-k} $$

*   Subtracts the **Rolling Mean** of the firm's *own* past 4 quarters ($F1_{i,t-1}$ to $F1_{i,t-4}$).

### The Intuition
This isolates the firm from its own "personality."
*   Some CEOs are naturally vague philosophers. Their baseline $F1$ might be +2.0 always.
*   If they score +2.0 today, the market isn't surprised. It's "priced in."
*   **Surprise** happens when a philosopher-CEO suddenly becomes precise ($F1\_HO < 0$), or a precise CEO becomes vague ($F1\_HO > 0$).

### Example
*   **TechCorp Q2**: $F1 = 0.0$.
*   **TechCorp History**: Usually very precise ($F1_{avg} = -2.0$).
*   $$ F1\_HO = 0.0 - (-2.0) = +2.0 $$
*   **Interpretation**: TechCorp is **surprisingly vague** (+2.0) relative to its own high standards.

---

## 5. Interaction Term: F1_POxHO (The "Double Signal")

### The Math
$$ F1\_POxHO_{i,t} = F1\_PO_{i,t} \times F1\_HO_{i,t} $$

### The Intuition
This tells us if the two surprises **reinforce** or **cancel** each other.

| PO | HO | Product | Meaning |
|:---|:---|:--------|:--------|
| **+** (Worse than peers) | **+** (Worse than usual) | **++** (Large Pos) | **Consistent Bad News**. The CEO is visibly struggling compared to everyone. |
| **-** (Better than peers) | **-** (Better than usual) | **++** (Large Pos) | **Consistent Good News**. |
| **+** (Worse than peers) | **-** (Better than usual) | **-** (Large Neg) | **Conflicting Signal**. "Compared to peers I'm bad, but for ME this is good." |

### Example
*   TechCorp Q2: $PO = -1.0$ (Better than peers), $HO = +2.0$ (Worse than history).
*   $$ PO \times HO = -2.0 $$
*   **Interpretation**: A conflicting signal. The firm is deteriorating relative to itself (+HO), but is still the "best house in a bad neighborhood" (-PO).

---

## 6. Kinematics: Velocity and Acceleration

We apply physics concepts to the **History Surprise** ($H = F1\_HO$) because self-deviation is the strongest signal of "hidden news."

### 6a. Velocity ($v$) - "The Speed of Decay"

**Math:**
$$ v_t = H_t - H_{t-1} $$

**Intuition:**
*   $H > 0$ means "Vague".
*   $v > 0$ means "Getting Vaguer".
*   If a CEO is hiding bad news, they often don't go from clear to vague instantly. They drift. Velocity measures that drift.

**Example:**
*   Q1 $H = 1.0$ (Vague)
*   Q2 $H = 2.0$ (Very Vague)
*   $$ v = 1.0 $$ (Positive velocity = deteriorating clarity)

### 6b. Acceleration ($a$) - "The Force of Decay"

**Math:**
$$ a_t = v_t - v_{t-1} $$
$$ a_t = (H_t - H_{t-1}) - (H_{t-1} - H_{t-2}) $$

**Intuition:**
*   Is the deterioration **speeding up**?
*   In physics, Force = Mass x Acceleration. High acceleration ($a > 0$) implies an active "force" (e.g., a looming scandal) pushing the CEO rapidly away from their baseline.
*   **Jerk**: Sudden changes in acceleration often precede jumps (like M&A announcements or resignations).

**Example:**
*   **Q1**: $H=0$, $v=0$ (Stable)
*   **Q2**: $H=1$, $v=1$ (Started getting vague)
*   **Q3**: $H=4$, $v=3$ (Got vague MUCh faster)
*   $$ a_{Q3} = v_{Q3} - v_{Q2} = 3 - 1 = +2.0 $$
*   **Interpretation**: The situation is spiraling out of control.

---

## Summary of TechCorp @ Q2 (The Crisis)

| Variable | Value | Meaning |
|:---------|:------|:--------|
| **Raw** | 5% | High Uncertainty |
| **F1** | 0.0 | Average for the Crisis |
| **F1_PO** | -1.0 | Clearer than panicking peers |
| **F1_HO** | +2.0 | Much vaguer than its own history |
| **POxHO** | -2.0 | Conflicting signal |
| **Velocity** | +1.0 | Getting vaguer vs last Q |
| **Accel** | +2.0 | Getting vaguer *faster* |

**Conclusion**: Despite being "average" for the market (F1=0), the **Kinematics** (HO=+2, v>0, a>0) reveal that TechCorp is significantly deteriorating relative to its own baseline, signaling potential internal trouble distinct from the market crash.
