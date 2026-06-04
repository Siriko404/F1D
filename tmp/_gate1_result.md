# GATE-1 / Link-1 external validity — RESULT (PASS) 2026-06-03

**Test:** `STOCK_score_call ~ CashRatio + firm FE + time FE`, firm-clustered SE.
STOCK sub-score only (cash level + liquidity; DISPOSITION excluded).
Does analyst cash-attention track the firm's actual cash holdings? **YES.**

## Sample
- Cache: `tmp/_cash_stock_score_call.parquet` (307,651 calls, all years 2002-2018; STOCK lexicon v1).
- Joined to `outputs/variables/h1_cash_holdings/2026-04-19_182724/h1_cash_holdings_panel.parquet` on `file_name` (panel already carries gvkey + CashRatio=cheq/atq).
- Main sample (drop ff12 8/11 finance/utility), CashRatio winsor 1/99, require ≥3 analyst Q&A turns.
- **N = 75,087 calls | 1,868 firms | 68 cal quarters.**

## Results
| Spec | β | SE | t | p |
|---|---|---|---|---|
| Linear (omnibus) | **+0.00753** | 0.00094 | +8.03 | <.0001 *** |
| High-cash dummy 1[CashRatio≥p67] (PRIMARY, Jensen) | **+0.00175** | 0.00023 | +7.50 | <.0001 *** |

High-cash effect = +0.00175 on a base mean of 0.0042 share = **+42% relative**.

## Binscatter (residualized firm+time FE) — shape
Monotone increasing; low-cash deciles are the LOWEST (no distress-tail elevation):
```
d1  cashresid -0.140  stock -0.00079
...
d5  cashresid -0.010  stock -0.00008
...
d10 cashresid +0.157  stock +0.00130
```
→ The advisor's non-monotone false-null worry did NOT materialize. Linear AND high-cash both clean positive.

## Raw tercile means (cross-sectional, contaminated — FE estimate is the valid one)
low 0.0031 < mid 0.0047 ≈ high 0.0048. Cross-sectionally high≈mid (big mature firms muddy it);
the within-firm (FE) high-cash contrast is clean positive (+0.00175***).

## Verdict
**Link-1 GREEN.** The cash-attention measure has external validity — analysts demonstrably
talk more about cash when the firm holds more cash. CashScrutiny is a valid regressor.
Unblocks **Link-2**: `UncResCEO ~ CashScrutiny×HighCash + CashScrutiny + HighCash + firm/time FE`.

Scripts: `tmp/_build_stock_score_cache.py`, `tmp/_gate1_link1_stock_cashratio.py`.
Still open: Gate-2 (Sina adjudicates 6 borderline gold snippets) before final measure lock.
