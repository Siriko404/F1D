# LINK-2 channel test — RESULT 2026-06-03 (diagnostic, pre-table)

**Spec:** `UncResCEO ~ CashScrutiny x HighCash + CashScrutiny + HighCash + firm FE + time FE`,
firm-clustered SE. DV = existing DWZ UncResCEO (untouched). CashScrutiny = STOCK score
(% of analyst Q&A turns on cash level/liquidity). HighCash = top-tercile CashRatio dummy.
Script: `tmp/_link2_channel_test.py`.

## Sample
N = **41,511 calls | 1,409 firms | 67 quarters** (h1 panel ∩ STOCK cache ∩ ceo_clarity_residual;
inner-join on residual imposes CEO≥5-calls). Main sample (drop fin/util), MIN_QA≥3.

## Pre-cells (advisor-locked) — BOTH PASS
- (a) **corr(CashScrutiny, UncQue) = +0.011** → |r|<0.1 → UncQue partialling is negligible →
  a NULL is interpretable (not mechanically suppressed).
- (b) **Validity transfers:** CashScrutiny ~ CashRatio β=+0.968*** (p<.0001) on this CEO≥5 sample
  (stronger than full-sample 0.85). Measure is valid here too.

## Result — interaction is the PRIMARY prediction (Jensen: evasion where idle cash high)
| Term | M1 (no ctrl) | M2 (+ctrl) |
|---|---|---|
| CashScrutiny (main) | −0.00085 (p2=.59) n.s. | −0.00083 (p2=.60) n.s. |
| HighCash | +0.00795 (p1=.10) | +0.00688 (p1=.14) |
| **CashScrutiny×HighCash (PRIMARY)** | **+0.00196 (se .0027, p1=.23)** | **+0.00245 (p1=.18)** |

**Interaction = positive sign, NOT significant** (t≈0.7). Implied slope of UncResCEO on
CashScrutiny: at HighCash=1 ≈ +0.0011; at HighCash=0 ≈ −0.0009 — directionally the story
(high-cash firms show the positive scrutiny→uncertainty tilt) but indistinguishable from zero.

## Honest reading (matches locked thesis framing)
Channel = **plausible/directional but not statistically supported**. Consistent with the locked
claim "reverse channel plausible + forward precautionary n.s." — both legs correlational, neither
rules the other out. corr=0.011 means this null is REAL, not a measurement/partialling artifact.

## RAW DIRECT effect (PRIMARY, per Sina) — `UncResCEO ~ CashScrutiny + FE`  (script `tmp/_link2b_direct_scrutiny.py`)
The raw direct effect is the proper primary test (corr(CashScrutiny,UncQue)=0.011 voided the
UncQue-partialling reason for downgrading it). N=41,512.
| variant | FE β (p2) | FE+ctrl β (p2) |
|---|---|---|
| share % (raw) | −0.00001 (.99) | +0.00019 (.88) |
| share z-score | −0.00001 (.99) | +0.00026 (.88) |
| 1[≥1 cash turn] | +0.00444 (.39) | +0.00534 (.31) |
| count cash turns | +0.00320 (.41) | +0.00438 (.27) |
| log(1+count) | +0.00569 (.38) | +0.00724 (.28) |
**NULL across all forms.** Share is dead flat; extensive/count lean + (right sign) but n.s.
(p2≈0.27–0.41). Controls don't help.

## LOGIT (binarized UncResCEO) — `tmp/_link2c_logit.py`  (ind+quarter FE, firm-clustered)
Binarized UncResCEO at 5 cutoffs (>0, ≥median, top tercile/quartile/decile) × 4 scrutiny forms.
Firm-FE logit infeasible (incidental params) → industry(ff12)+quarter FE, cross-firm ID.
**FE-only grid: NULL in all 20 cells, best p≈0.22** (any-cash-turn → 1[≥median], +.038). Signs mostly
+ at central cutoffs, flip − at top decile. (+ctrl first run blew up from unwinsorized controls;
rerun with winsor+standardized controls.) Binary recoding does NOT rescue the effect.

## STATE: raw, interaction, AND logit all NULL
The reverse (analyst-scrutiny) channel's forward test on UncResCEO is **not statistically supported**
in any form tested. Measure is valid (Link-1 β=+0.97***), but cash-scrutiny does not move UncResCEO.
Honest implication for framing: NEITHER direction (precautionary forward, scrutiny reverse) is
statistically robust on this DV — relationship is weak/correlational at best. Non-replication
conclusion is SINA'S to draw, not mine.

## EMPIRE-BUILDING UNIVERSE test (`tmp/_link12_empire_universe.py`)
Restrict to cash-acquirer gvkeys (≥50%-cash deals; empire `treat` set, 964 gvkeys, 804 in channel sample).
- **Link-1 HOLDS:** CashAttn~CashRatio β=+0.89*** (all, N=38k), +0.92*** (run-up e<0), +1.35** (8Q run-up).
  Measure valid among empire-builders too.
- **Link-2 NULL:** direct all n.s. (best any-turn +0.011 p.32 in run-up); interaction best = **run-up e<0
  +0.0070, p1=.10 / p2=.21** (marginal one-tailed, NOT sig; dies in 8Q window +0.0022 p.86). One cell of
  ~15 → multiple-comparisons caution. Restricting to empire firms does NOT rescue the channel.

## Forward levers (NOT yet tried — measurement/timing/DV, no give-up)
1. **DV sensitivity:** UncResCEO is a CEO-FE residual (sd 0.30, heavily scrubbed). Test the channel on
   raw **UncAnsCEO** (pre-residual) and on **NegCall**, to see if residualization eats a real signal.
2. **Timing:** lead UncResCEO (dodge in the NEXT call) or lag cash-scrutiny.
3. **Heterogeneity:** restrict to agency-prone / constrained / low-governance firms.
4. **Sharper evasion proxy:** Hollander "Does Silence Speak" = non-answers/refusals, not uncertainty
   (DV is DWZ-locked, so this would be a NEW outcome, flag to Sina before building).
