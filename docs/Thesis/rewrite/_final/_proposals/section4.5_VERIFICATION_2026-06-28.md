# §4.5 CHAIN-REVIEW VERIFICATION — 2026-06-28

**Verdict: all 6 props verified against primary source. 69/69 checks pass, 0 flags.**
Re-run: `python tmp/verify_45_claims.py` (committed). Ground truth, NOT memory:
- tables 5.2–5.5 → `F1D/.../firstdeal_robustness/2026-06-23_162451/rob_4tables.tex` (cells parsed programmatically)
- logits → `F1D-phase3/tmp/logit_fullcontrols_results.json` (TEST_A / TEST_B)
- FE → `F1D-phase3/tmp/fe_results.json` (TEST_A / TEST_B)

## What was checked, per aspect
| aspect | method | result |
|---|---|---|
| coefficient value | parsed from .tex cell / json key | 25/25 exact |
| stars (sig) | star-count from .tex `$^{**}$`; p-value→star from json | all match |
| sign (+/−) | signed parse; stock arms negative confirmed | all match |
| cell identity (all-deals vs first-deal) | column-index map; explicit guard that first-deal cash 0.0461 does NOT appear in PARA1-a | clean |
| standard errors | parsed from .tex SE row (line after coef) | 14/14 exact |
| internal arithmetic | cash − stock = Wald | 0.0447 − (−0.0609) = 0.1056 ✓ |
| honesty / register | no "suppress/dampen/strict specificity"; mechanism-open + concentration locks present; pooled logit not over-claimed within-firm | clean |

## Per-prop result
- **PARA1-a** (run-up table): cash UncR +0.0391\*\*\* (SE .0140), cash CshR +0.0033\*\* (.0015), stock UncR −0.0348 n.s. (.0272) — all = T5.2 all-deals panel. ✓
- **PARA1-b** (Logit A): LPM 0.0086\*\*\* (p .0011), logit 0.3233\*\*\* (p .0008), FE-LPM 0.0078\*\*\* (p .0046); N 40,004 (event-rate 2.84% = n_events 1,137), FE-N 39,557. ✓
- **PARA2-a** (timing, matched): PRE1 +0.0352\*\* (.0148), Drop PRE1−GAP 0.0363\*\* (.0156), Drop PRE1−POST 0.0544\*\*\* (.0139) — T5.3 all-deals UncRes. ✓
- **PARA2-b** (timing, by arm): cash PRE1 +0.0401\*\*\* (.0145), cash Drop PRE1−POST 0.0543\*\*\* (.0137), stock PRE1 −0.0272 n.s. (.0266), stock Drop PRE1−GAP −0.0585\* (.0355) — T5.4 all-deals. ✓
- **PARA3-a** (cash-conc Wald): Wald 0.1056\*\* (.0423), cash +0.0447\*\* (.0180), stock −0.0609 n.s. (.0385), cause CashR(m) 0.0071 n.s. (.0062), inline first-deal Wald 0.0983\*\* — T5.5 all-deals; arithmetic exact. ✓
- **PARA3-b** (Logit B): LPM 0.0613\*\* (p .030), logit 0.7478\*\* (p .028), FE-LPM 0.0644 n.s. (p .205); N 1,105 (cash 982 / stock 123, base 88.9%), FE-N 1,063. ✓

## Notes for ratification
- The single checker "flag" on first pass (deal-rate 2.84%) was a FALSE POSITIVE — my key-name search missed `TEST_A.event_rate`; confirmed = 0.02842 (n_events 1,137). No data issue.
- All numbers are MECHANICAL (BIMODAL): interpretive framing (FEATURE / answers-P5.2 / the caveats) is still deferred to Sina at the prose phase. This review certifies the NUMBERS + register locks only.
- §4.5 remains flagged `PROPOSAL` (prose_gate locked). This verification is the evidence base for Sina's unlock decision.
