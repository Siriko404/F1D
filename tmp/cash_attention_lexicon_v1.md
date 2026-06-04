# CashScrutiny lexicon — analyst attention to firm cash holdings (LOCKED v1)

Curated via 4-round brainstorm↔advisor loop, data-fed on 544K real 2014 analyst
Q&A turns + a 90-snippet blind-labeled gold set. Custom regex n-gram matcher on
raw `speaker_text` (the pipeline's LM tokenizer is unigram-only; cite LM for
tokenization concept only, NOT for this list).

## Construct definition (label to this)
An analyst turn devotes attention to the firm's cash holdings if it questions
the **level/size of cash & liquid balances** OR **what the firm should do with
them** (retain / return / deploy).

## Two sub-scores (report separately — sizes differ ~6×; do not lump)

### STOCK  (primary — closest to "cash holdings")
LEVEL: cash holdings, cash balance(s), cash position, cash on hand,
cash on the balance sheet, cash reserves, cash and cash equivalents,
cash and equivalents, cash and short-term investments, net cash, cash pile,
cash hoard, cash stockpile, war chest, dry powder, excess cash, idle cash,
surplus cash
LIQUIDITY: liquidity, liquid assets, short-term investments, marketable securities

### DISPOSITION  (related / robustness — dominated by "dividend"; size/maturity confound)
dividend(s), share buyback(s), buyback(s), share repurchase(s), repurchase(s),
return of capital, capital return, capital allocation, capital deployment,
payout (ratio), special dividend, return cash to shareholders, uses of cash,
deploy cash/capital, cash deployment

## Exclusions (false positives confirmed in real text)
free cash flow, operating cash flow, cash-flow statement, cash flow(s),
cash conversion (cycle), cash basis, cash cow, cash compensation, non-cash,
cash register, cash crop, cash taxes, cash earnings, cash in on

## Why v1 (not v2): parsimony
v2 added a bare-"cash" context window + FCF-conditional exclude. On the gold set
they bought NO measurable gain (precision 0.75 vs 0.70 = sampling noise, n=30,
95% CI ±0.16; cash-family recall identical at 0.94). Reverted by parsimony.
Do not re-add the bare-cash window later "to fix precision."

## Validation (2014 gold set, n=90, blind-to-bucket labels)
- Precision ≈ 0.70–0.75 (flagged turns genuinely read as cash-attention → face validity holds)
- Recall ≈ 0.94 **among cash-vocabulary turns** (SCOPE-LIMITED; turns expressing
  cash-attention with zero cash vocabulary are out of measurement scope —
  estimated small, NOT bounded by this sample). Do NOT report as "94% population recall."
- Self-graded (I designed + scored): PROVISIONAL until Sina adjudicates borderlines
  #1, #20, #43, #50, #67, #78.

## Measurement unit
PRIMARY: call-level **share of analyst Q&A turns** touching cash (turn-level
binary → mean per call). Robust to one verbose analyst.
ROBUSTNESS: token-share; count of distinct analysts raising cash.
(Turn-level FP/FN largely average out at call level → 0.70/0.94 adequate for a regressor.)

## Open gates before "defensible" lock
1. **Link-1 external validity (THE test):** STOCK-score (call) ~ CashRatio + firm/time FE.
   Run on STOCK ONLY (DISPOSITION ~ CashRatio risks spurious size/maturity correlation
   via "dividend"). Be ready for null = real finding about the channel, not a measurement bug.
2. **Independent spot-check:** Sina adjudicates the 6 borderline snippets above.
