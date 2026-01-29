
# Firm Drop Waterfall Analysis
## Why do we only have ~2,400 firms in the final output when Execucomp has ~3,200 firms (active 2002-2018)? ##

We investigated the **796 missing firms** (3,215 - 2,419):

| Drop Reason | Firms Lost | % of Drop | Explanation |
| :--- | :--- | :--- | :--- |
| **No Earnings Calls** | **692** | **86.9%** | Firms present in Execucomp but have **ZERO** linked calls in our dataset. |
| **< 5 Calls Filtering** | **94** | **11.8%** | Firms removed because their CEO had fewer than 5 calls (Quality Threshold). |
| **Temporal Mismatch** | **10** | **1.3%** | Firms have calls, but they don't overlap with the CEO's tenure dates. |

**Conclusion**: The drop is primarily due to **missing earnings call data** for ~700 S&P 1500 firms in our input `Unified-info` dataset, not a processing error.

### Conclusion
The pipeline is functioning correctly.
1. We capture 96.5% of "Matchable" calls (non-Execucomp calls are ignored).
2. We successfully process 2,419 out of 3,215 Execucomp firms (75% coverage).
3. The remaining 25% are lost safely due to missing inputs or quality filters.


