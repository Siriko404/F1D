# Campello rebuild — FULL variable forensic audit (REOPENED 2026-05-17)

Sources are **programmatic PDF extractions** (pdfplumber 0.11.9) from
`docs/papers/campello_etal_2022_brexit_jfqa.pdf` + corrigendum. NO hand
transcription. Artifacts: `tmp/campello_pdf_extract/`
(`table1_pdfpage21.txt`, `table8_pdfpage31.txt`, `corrigendum.txt`).

Method (systematic-debugging Phase 2): per variable —
verbatim definition + reported summary-stat fingerprint  vs  our builder
vs  verdict. **Fingerprint is decisive and is computed programmatically,
not eyeballed.**

Campello Table 1 Panel A (universe), programmatic extract p21 L372–383:
| var | mean | SD | median | IQR | N |
|---|---|---|---|---|---|
| CASH | 0.22 | 0.25 | 0.12 | 0.27 | 78,044 |
| TOBIN_Q | 2.11 | 1.59 | 1.57 | 1.26 | 73,353 |
| CASH_FLOW | 0.01 | 0.06 | 0.03 | 0.04 | 75,287 |
| SIZE (log assets) | 6.19 | 2.08 | 6.15 | 3.08 | 78,062 |
| SALES_GROWTH | 0.16 | 0.62 | 0.06 | 0.23 | 71,637 |
| CONSENSUS_EARN_FCST | 0.07 | 3.51 | 0.09 | 2.05 | 42,031 |
| STOCK_RETURNS | 0.03 | 0.24 | 0.02 | 0.25 | 67,226 |
Panel B treated CASH 0.20/0.24/0.11; Panel C control 0.17/0.18/0.11.
Window: 2010:Q1–2015:Q4. All vars winsorized 1% (p21 L197–198).

## A. DEPENDENT VARIABLE — TEXTUAL CONFLICT (empirical test PENDING)

- Table 1 verbatim (p21 L29–30): "CASH is defined as cash and short-term
  investments divided by **lagged total assets**." ⇒ cheq_t / atq_{t-1}
- Table 8 caption verbatim (p31 L24): "...divided by lagged total assets
  **net of cash holdings**." ⇒ cheq_t / (atq_{t-1} − cheq_{t-1})
- Corrigendum (corrigendum.txt L100–101): only adds missing appendices
  A/B; **does NOT touch Table 1/8 or the CASH definition**. Conflict is
  intrinsic to the published paper.
- Our rebuild = Table 8 caption (net-of-cash), Sina-ratified 2026-05-17.
  ⚠ **SUPERSEDED — see §F.2**: 2026-05-17 Sina authorized switching the
  canonical DV to the Table-1 plain denominator (cheq_t/atq_{t-1}) after
  the 4-table evidence; this §A "net-of-cash ratified" line is historical.

CORRECTION (advisor, firm algebra — supersedes my earlier "2–3× ⇒
denominator" claim, which was WRONG): if cheq/atq = r then
cheq/(atq−cheq) = r/(1−r). At r=0.12 → 0.136 (+14%); r=0.20 → 0.25
(+25%). Net-of-cash CANNOT produce a 2–3× gap. My earlier 0.32–0.52 vs
0.12 comparison was apples-to-oranges (our 4-qtr post-winsor cell means
vs Campello full-window N=78,044 stats). **DV status = unresolved
ambiguity; requires the programmatic moment-fingerprint test below, NOT
a reversal on faulty math.** No spec change recommended yet.

## B. FIRM CONTROLS — formula vs p21 verbatim (moments UNVERIFIED)

| var | our builder | formula verdict | moment check |
|---|---|---|---|
| TOBIN_Q | (cshoq·prccq+atq−ceqq+txditcq)/atq | MATCH verbatim | PENDING vs 2.11/1.57 |
| CASH_FLOW | oibdpq_t/atq_{t-1} (cal-prev-Q) | MATCH | PENDING vs 0.01/0.03 |
| SIZE | ln(atq) lagged 1Q | MATCH | PENDING vs 6.19/6.15 |
| SALES_GROWTH | (saleq_t−saleq_{t-4})/saleq_{t-4} | MATCH | PENDING vs 0.16/0.06 |
| STOCK_RETURNS | Π(1+RET)−1 CRSP total (paper-silent;Sina) | MATCH (defensible) | PENDING vs 0.03/0.02 |
| CONSENSUS | within-firm z-score (SD≈1 by constr.) | **DEVIATION** | Campello SD **3.51** ≠ z-score |

CONSENSUS detail: Campello "standardized mean 1-qtr-ahead EPS" reports
SD 3.51 / IQR 2.05 (p21 L382). A unit-variance z-score has SD≈1 → our
operationalization is NOT Campello's "standardized". Real deviation,
well-evidenced. Builder docstring already flagged this as Sina-chosen.

## C. STILL UNAUDITED (audit is PARTIAL — user asked for ALL)
- βᵁᴷ eq-(13): firm vol, vol(FTSE100), vol(SP500), vol(FX$£),
  window/form — **prior load-bearing suspect** (near-unidentification).
- Treatment tercile cut (step3); step1 filters + atq/saleq lag dir
  (e7a219b — re-verify); POST; FIC100×qtr FE; winsor mechanics.

## RESULTS — programmatic moment fingerprint (run 2026-05-17,
`_diag_moment_fingerprint.py`; both sides machine-derived, NOT typed;
rebuild on 2010Q1-2015Q4, 1% winsor within qtr; UNIVERSE = step1 set)

| var | rebuild mean / SD / med | Campello mean / SD / med | verdict |
|---|---|---|---|
| **CASH (Table-1 denom cheq/atq_l1)** | **0.212 / 0.235 / 0.126** | **0.220 / 0.250 / 0.120** | **NEAR-EXACT MATCH** |
| CASH (Table-8 denom, our rebuild) | 0.609 / 1.651 / 0.144 | 0.220 / 0.250 / 0.120 | **FAILS** (mean 2.8×, SD 6.6×) |
| stock_return | 0.031 / 0.221 / 0.023 | 0.030 / 0.240 / 0.020 | MATCH |
| tobins_q | 2.153 / 1.566 / 1.627 | 2.110 / 1.590 / 1.570 | MATCH |
| cash_flow | 0.020 / 0.054 / 0.029 | 0.010 / 0.060 / 0.030 | MATCH (med/SD; mean ~2× but ~0.01–0.02) |
| sales_growth | 0.153 / 0.523 / 0.065 | 0.160 / 0.620 / 0.060 | MATCH |
| SIZE ln(atq) | 6.622 / 1.909 / 6.577 | 6.190 / 2.080 / 6.150 | formula OK; ~0.43 high (sample comp, minor) |
| **consensus_eps** | **−0.000 / 0.793 / −0.083** | **0.070 / 3.510 / 0.090** | **DEVIATION** (z-score SD≈1 ≠ Campello SD 3.51) |
Treated/Control: Table-1-denom CASH med 0.102 / 0.119 ≈ Campello B/C 0.11.

### Evidence-grounded findings
1. **DV denominator = strongest lead (Sina-gated).** The Table-1 plain
   denominator (cheq/atq_{t-1}) reproduces Campello's CASH fingerprint on
   ALL THREE moments + treated/control (0.21/0.24/0.13 ≈ 0.22/0.25/0.12).
   Our rebuild's Table-8-caption net-of-cash denominator gives mean 0.61
   (2.8×), SD 1.65 (6.6×) — does NOT reproduce the variable Campello
   actually summarized. Paper is internally inconsistent (Table 1 def vs
   Table 8 caption); the empirical fingerprint says the analyzed CASH has
   the plain-denominator distribution. (Advisor's median-algebra caveat
   stands — median only moves +14%; the divergence is in mean/SD via the
   net-of-cash right tail. The corrected finding rests on mean+SD, not the
   discredited "uniform 2–3×" claim.)
2. **CONSENSUS_EARNINGS_FORECAST = confirmed deviation.** Within-firm
   z-score (SD 0.79) ≠ Campello "standardized" (SD 3.51); medians even
   differ in sign. Operationalization is not Campello's.
3. **stock_return, tobins_q, cash_flow, sales_growth = MATCH** —
   Campello-verbatim, empirically validated on the fingerprint.
4. SIZE: formula verbatim-correct; moments mildly high = sample
   composition (βᵁᴷ-estimable set is larger firms), not a defect.

### Sample caveat (advisor, honest)
Rebuild UNIVERSE N=59,852 vs Campello Panel A N=78,044; βᵁᴷ-estimable set
(~2,717 gvkeys) skews LARGER-firm — SIZE med 6.58 vs Campello 6.15
(+0.43). Variable *construction* matches the fingerprint, but our
"universe" is NOT Campello's universe. Not a defect; a sample-selection
caveat that the βᵁᴷ-stage / step1 audit must carry forward.

### Mechanism (advisor, settled)
Median moves only +14% (r/(1−r), as predicted). The DV failure is
**right-tail explosion**: cash-rich firms ⇒ atq−cheq→small ⇒ ratio
huge ⇒ mean 0.61 / SD 1.65. 1% winsor clips but does not tame the
asymmetry. Finding rests on mean+SD; the "uniform 2–3×" claim is dead.

### DV-FIX TEST RESULT (step10_cash_t1denom.py, Sina-authorized GO 2026-05-17)
ONE change vs step7 = CASH denom → cheq/atq_{t-1} (Table-1). Everything
else byte-identical. Canonical step7 untouched (non-destructive clone).
- CASH moments (estimation sample, winsor): mean +0.176 / SD 0.193 /
  med +0.107 / N 18,632  ≈ Campello Panel B/C (0.17–0.20 / 0.11)
  ⇒ Table-1 denom **reproduces Campello's CASH fingerprint** (confirmed).
- δ̂(POST·HIGH) = **−0.00734** SE 0.00494 t −1.49 p 0.137 R²w 0.0895.
  vs step7 Table-8 denom −0.03288 (R²w 0.033) ; Campello +0.231***.
VERDICT (per advisor decision rule): DV denominator = **REAL defect,
necessary-NOT-sufficient**. Fix corrects the CASH distribution + the
contaminated regression (R²w 0.033→0.090, SE 0.027→0.005) but δ̂ stays
negative & NS — does NOT recover +0.231***. ⇒ ≥1 more defect; prime
suspect = βᵁᴷ eq-(13) (also the only thing that can explain the Step-8
placebo failure: pre-trend in high-βᵁᴷ firms ⇐ treatment-assignment var).
DV spec change (Table-8→Table-1 denom) is Sina-gated (reverses a
ratified decision); test artifact only, step7 unchanged.

## D. βᵁᴷ eq-(13) AUDIT — DONE (2026-05-17, Sina GO; programmatic, no fixes)

Sources = clean pdfplumber extracts `tmp/campello_pdf_extract/buk_pdfpage{14,16,17,18}.txt`
(re-derives prior on-record conclusion from HALLUCINATION-FREE extracts, not
the now-suspect `tmp/campello_pages`). Code = `step2_beta_uk.py`,
`step3_treatment.py` (full reads). Output = `step2_beta_uk/2026-05-17_193352/
summary.json`.

### Spec elements — VERBATIM vs our code (every estimable element FAITHFUL)
| element | paper verbatim (programmatic) | our step2 | verdict |
|---|---|---|---|
| eq-(13) form | p14 L28: `vol(r_it)=α_i+βUK_i·vol(FTSE100_t)+θ·CONTROLS_t+ε_it` | `vol_r ~ 1+vol_ftse+vol_sp500+vol_fx` per gvkey | **MATCH** |
| LHS | p14 L31 "volatility of equity returns vol(r_it)" | CRSP RET monthly vol | MATCH |
| controls | p14 L37 "CONTROLS_t consisting of vol(SP500) and vol(FX$£)" | vol_sp500 + vol_fx | **MATCH** |
| estimator | p14 L25 "estimate equation (12) for each firm i" | per-gvkey OLS | **MATCH** (per-firm) |
| window/freq | p16 L42 "monthly data from 2010:M1 to 2014:M12" | 2010M1–2014M12 monthly, ≤60 obs | **MATCH** |
| vol() build | p14 L23 "Following Bloom (2014)" — paper-SILENT | std(ddof=1) daily ret within month | paper-silent; Sina-ratified; text-exhausted (NOT reopened) |
| vendors | p16 L36 "CRSP stock price + Bloomberg index/currency" | CRSP RET / Yahoo FTSE / CRSP sprtrn / BoE FX | forced sub (no Bloomberg lic.); Sina ruled credible — NOT cause |
| tercile rule | p16 L166 "upper (bottom) tercile of the nonnegative range of the βUK distribution"; βUK<0 excluded both | step3 equal-count nonneg tercile, βUK<0 excluded | **MATCH** (method) |

### fn13 (p14 L243-254, programmatic) — CUTS AGAINST the noise hypothesis
Verbatim: "the volatility of equity returns may be an **imperfect proxy** for
the volatility of firm income"; βUK vs βUK_CF rank-corr **0.8**, **86%
top-tercile overlap**; "**As shown in Table C6, our inferences are unchanged
whether using βUK or βUK_CF to conduct our tests.**"
⚠ CORRECTION (advisor 2026-05-17; supersedes the earlier "paper concedes
βᵁᴷ is noisy ⇒ supports noise-as-cause" framing): the proxy IS imperfect
(verbatim), BUT fn13's actual point is **robustness to that noise** —
Campello's +0.231\*\*\* survives swapping in a βᵁᴷ that agrees only 86% at
the top tercile. Their noisy measure replicated *for them*. fn13 is
therefore evidence **AGAINST** "βᵁᴷ noise explains our non-replication,"
not for it. The original inference here was wrong; the verbatim quote is
unchanged.

### Distribution fingerprint — Campello vs ours (decisive)
Campello (p16 verbatim): nonneg-range cuts control<0.28 / treated>0.68;
449 treated / 360 control. ⚠ Campello NEVER published βᵁᴷ summary stats —
449/360 + cuts 0.28/0.68 are compatible with MANY distribution shapes; the
"modest spread / clean structure" inference is weakly anchored, do not
over-read it. Only the %-negative and tail comparisons are anchored, and
even those are inferred.
Ours (`summary.json` 193352): the like-for-like comparison is the
**step1-matched panel** (n=2,521), NOT full-CRSP 5,648 (the earlier
5,648-vs-~1,200 line conflated universes — corrected). Matched: mean 0.18,
median 0.133, **std 1.05**, **pct_negative 38.6%**, p01 **−2.85**, p99
**+2.90**, **p33 = −0.072 (NEGATIVE)**. Nonneg matched ≈ 2,521·(1−0.386) ≈
**~1,547** vs Campello implied ~1,200–1,400 — **same order of magnitude;
firm count is NOT the big mismatch.**
The well-anchored divergence is the **negative tail**: ~39% of our matched
βᵁᴷ < 0 with p33 itself negative, and symmetric ±3 tails on a coefficient
whose median is 0.13 — the signature of imprecise per-firm eq-(13) OLS
(≤60 monthly obs; vol(FTSE)/vol(SP500)/vol(FX) co-move 2010–2014; prior
on-record ρ(volFTSE,volSP500)=0.868, 76% of neg-βᵁᴷ |t|<1). Cut *values*
≈ match (ours ~0.24/0.63 vs 0.28/0.68 — corroborates step3 method; the
contaminated βᵁᴷ misclassifies *which* firms land per tercile, cuts intact).
This **re-confirms** the prior on-record conclusion from clean extracts —
it is confirmation, NOT new information (the case was reopened for new
evidence; none surfaced — a legitimate but non-novel outcome).

### Evidence-grounded finding (NO verdict — gated on Sina)
SOLID (verbatim, not disputed): βᵁᴷ non-replication is **NOT a code defect
and NOT a step3 defect**. Every estimable spec element (form, LHS, controls,
per-firm estimator, window, frequency, tercile rule) is **VERBATIM-FAITHFUL**
to the programmatically extracted paper. The ≤60-obs ceiling is *Campello's
own design*, not our deviation. DV is necessary-not-sufficient (§A: Table-1
denom δ̂ −0.007 NS).

⚠ UNRECONCILED — the "near-unidentification noise" diagnosis is NOT settled.
Two findings on the table do not fit the same mechanism:
- (i) our βᵁᴷ has ~39% negative + ±3 tails ⇒ *imprecision* story.
- (ii) Step-8 placebo on a FAKE pre-event = δ̂ **−0.104\*\*\*** (significant,
  sign-flipped). Pure measurement noise in the treatment dummy →
  **attenuation toward 0 / NULL placebo**, NOT a significant pre-trend.
  A significant fake-pre-event effect is the signature of **selection on a
  confounder** (high-βᵁᴷ firms systematically differ pre-event on something
  driving cash dynamics — industry mix not absorbed by FIC100×qtr FE, size
  [SIZE skew +0.43], leverage/payout, etc.) — a DIFFERENT diagnosis than
  imprecise OLS. fn13 (corrected above) also cuts against pure-noise:
  Campello's noisy measure replicated for them.
⇒ Verdict downgraded from "near-unidentification (settled)" to **"βᵁᴷ-tercile
assignment is the binding constraint; mechanism = imprecision vs.
selection-on-confounder is UNRESOLVED."** step3 stays a faithful messenger
either way (method verbatim, cuts near-match).

### DISCRIMINATING DIAGNOSTIC (flagged; Sina-GATED; NOT a spec deviation)
**Random-tercile placebo:** randomly assign treated/control with the SAME
N's, SAME panel/controls/FE/double-clustered SE, re-fit eq-(14) ×100 draws.
NO recipe change (treatment label re-shuffle only) ⇒ not a spec deviation.
- If δ̂ ≈ 0 across draws but βᵁᴷ-tercile δ̂ = −0.033 ⇒ βᵁᴷ selects on
  something (selection-on-confounder, not just noise).
- If random draws ALSO yield ~−0.03 with right tail to \* ⇒ panel/FE/sample
  artifact, not βᵁᴷ at all.
This is the only ~5-min test that empirically separates (i) vs (ii). It is
the next decision-relevant action — Sina decides whether to run it.

### ONLY untested levers — BOTH are spec DEVIATIONS, Sina-GATED, NOT executed
- (a) weekly vol() ⇒ ~260 obs/firm vs ≤60 (precision↑) — but p16 L42 says
  "monthly data" ⇒ documented deviation, not verbatim.
- (b) drop collinear vol(SP500) — but p14 L37 verbatim INCLUDES it ⇒ deviation.
⚠ SEQUENCING: levers (a)/(b) are *precision* levers — only decision-relevant
IF the discriminating random-tercile placebo confirms mechanism (i)
imprecision. If it instead shows selection-on-confounder or a panel/FE
artifact, (a)/(b) would be chasing the wrong cause. Run the placebo FIRST.
The verbatim spec, faithfully implemented, does not replicate +0.231. That
is the honest forensic state. Interpretive verdict is Sina's only;
off-ramp forbidden; no spec change without explicit Sina authorization.

### Still UNAUDITED (lower priority — βᵁᴷ + step3 now CLOSED)
step1 filters + atq/saleq lag direction (commit e7a219b — re-verify); POST
construction; FIC100×qtr FE; winsor mechanics; consensus_eps remediation
(forecast/price, §B). No spec change; no verdict (gated on Sina).

## E. FULL SUMMARY-STATS COMPARE — Panels A/B/C (2026-05-17, Sina req.)

Artifact: `tmp/campello_summary_stats_compare_2026_05_17.md`
(`_diag_summary_stats_full.py`; reuses validated fingerprint machinery).
Campello publishes ONLY mean/SD/median/IQR/N (no min/max/pctiles —
min/max comparison IMPOSSIBLE; ours-only RAW min/max = garbage sniff).
Winsor 1% within qtr (Campello convention); window 2010Q1–2015Q4. Scopes
Universe/Treated/Control ≈ Campello Panel A/B/C.

**RESULT — inputs are NOT garbage. 6 firm controls + Table-1 CASH match
Campello across ALL THREE panels:**
| var | Universe (A) | Treated (B) | Control (C) | verdict |
|---|---|---|---|---|
| CASH_T1 (cheq/atq_l1) | 0.212/0.236/0.126 vs 0.220/0.250/0.120 | 0.195/0.102 vs 0.200/0.110 | 0.181/0.119 vs 0.170/0.110 | **MATCH ×3** |
| SIZE | 6.62 vs 6.19 | 6.32 vs 6.11 | **7.22 vs 7.25 (near-exact)** | MATCH ×3 |
| STOCK_RETURNS | 0.031/0.023 vs 0.030/0.020 | 0.015/0.003 vs 0.020/0.000 | 0.037/0.032 vs 0.040/0.030 | MATCH ×3 |
| TOBIN_Q | 2.15/1.63 vs 2.11/1.57 | 2.03/1.47 vs 1.92/1.41 | 2.13/1.71 vs 1.98/1.62 | MATCH ×3 |
| CASH_FLOW | 0.020/0.029 vs 0.010/0.030 | 0.015/0.024 vs 0.010/0.020 | 0.030/0.033 vs 0.030/0.030 | MATCH ×3 |
| SALES_GROWTH | 0.153/0.065 vs 0.160/0.060 | 0.207/0.064 vs 0.180/0.060 | 0.100/0.061 vs 0.100/0.060 | MATCH ×3 |

**Only 2 CHECK flags — both already on record, NOT garbage:**
- **CASH_T8** (net-of-cash, our ratified DV): mean 0.61/SD 1.65 vs C
  0.22/0.25, all 3 panels; RAW max +1409/+508 ⇒ right-tail explosion =
  the §A DV defect, re-confirmed cross-panel.
- **CONSENSUS_EPS**: SD 0.79 vs C 3.51 all 3 panels; RAW bounded **±2.5**
  ⇒ confirms the §B within-firm z-score standardization deviation is a
  construction CHOICE, not bad vendor data.

RAW garbage sniff: pre-winsor tails exist (CASH_T1 max 953, TOBIN_Q 269,
CASH_FLOW −3.98) but winsorized moments match Campello (who also winsors
1%) ⇒ tails are normal small-denominator firm-qtrs, handled by winsor,
NOT garbage.

**Implication:** the non-replication is NOT a control-variable or input-
data garbage problem — inputs reproduce Campello's distribution on
universe AND on the βᵁᴷ-tercile sub-panels. Localizes the gap further to
(1) βᵁᴷ-tercile assignment (§D, mechanism unresolved) and (2) the
DV-denominator decision (§A, Sina-gated). Minor pre-treatment note: our
CASH_T1 treated med 0.102 < control 0.119 (Campello B=C=0.11, flat) — a
small treated/control cash imbalance worth keeping in view for the §D
selection-on-confounder hypothesis; do not over-read (IQRs overlap). No
spec change; no verdict (gated on Sina).

### E.1 Sharpened implication + caveats (advisor 2026-05-17)
**Tilts §D toward selection-on-confounder (ii), away from pure-noise (i):**
if βᵁᴷ were pure noise, tercile assignment ≈ random ⇒ NO systematic
treated-vs-control observable differences. But our terciles reproduce
Campello's sorting (control LARGER than treated: ours SIZE 7.22 vs 6.32;
theirs 7.25 vs 6.11; same direction on returns/Q/CF/SG). Systematic
sorting is hard for "imprecise OLS noise" to produce ⇒ this is today's
most decision-relevant new evidence; the §D mechanism leans (ii).
**DV finding stronger:** Campello Panel B/C report ONE CASH (Table-1
denom); our CASH_T1 reproduces their treated/control 0.11 (0.102/0.119),
CASH_T8 does NOT — net-of-cash misses Panel B/C too, not just A. Empirical
case that the *analyzed* DV is the plain denominator is now stronger
(still Sina-gated).
**Caveats (do not over-read "MATCH ×3"):**
1. FLAG rule is a lenient HINT (mean&med within 25% & same sign), NOT
   strict equivalence — e.g. CASH_FLOW Universe mean 0.020 vs C 0.010 is
   2× off but flagged MATCH on median. Read as "same ballpark," not "=".
2. Count gap NOT dismissed: ours treated **565 vs 449** (+26%), control
   **482 vs 360** (+34%). Moments match but the βᵁᴷ-tercile firm COUNT is
   still a deviation (consistent w/ §D distribution-shape finding).
3. Diagnostic is **pooled cross-sectional** (2010Q1–2015Q4). It does NOT
   test POST construction, atq/saleq lag wiring, or 2016Q3–Q4 / FE
   quarter structure — those remain genuinely UNAUDITED. "Localized to
   βᵁᴷ+DV" is reasonable, not *proven*.
**Indicated next action (Sina-gated):** random-tercile placebo (§D) — now
sharper: same observable firm profiles as Campello's terciles but
different DiD outcome ⇒ the placebo is the cleanest ~5-min test to
discriminate selection vs imprecision vs panel-FE artifact.
⚠ STATUS 2026-05-17: placebo built (`_diag_random_tercile_placebo.py`,
exact step7 clone, clone-fidelity gate) but **DEPRIORITIZED by Sina** —
"no need for the placebo, we have significant deviations in our variables
and must check ALL devs." Redirected to auditing the produced variables
(§F/§G). Placebo script retained, not run.

## F. CASH_T8 AUDIT — produced DV (2026-05-17, Sina-directed)

Target: the variable WE produce as the canonical DV (step7 `_cash_dv()`).
Question: is the deviation purely the definitional CHOICE, or a CHOICE +
an implementation defect?

Table-8 caption verbatim (programmatic, `table8_pdfpage31.txt` L23-24):
"Table 8 reports output from equation (14)… **CASH is defined as total
cash holdings divided by lagged total assets net of cash holdings.**"
Table-1 note verbatim (`table1_pdfpage21.txt`): "CASH is defined as cash
and short-term investments divided by **lagged total assets**." (numerator
identical = cheq; only the denominator differs ⇒ a paper internal
inconsistency, not a numerator question).

`step7._cash_dv()` (full read): `cheq`/`(atq_l1 − cheq_l1)`,
`atq_l1`/`cheq_l1` via `_prev_q` calendar-quarter lag, filter
`cheq.notna() & denom>0`, 1% winsor within qtr (step7 L172-173).
**VERDICT: verbatim-FAITHFUL to the Table-8 caption; NO implementation
defect.** Calendar lag correct; `denom>0` guard correct/necessary (drops
lagged-non-cash-assets ≤ 0). The deviation is **100% the definitional
choice** (which of the paper's two conflicting CASH definitions we follow).

NEW HARDENING — winsor-invariance argument: both CASH_T1 and CASH_T8 get
the SAME 1% within-qtr winsor = Campello's own stated convention ("all
variables winsorized at 1%"). Under that identical winsor: CASH_T1 →
0.21/0.24/0.13 ≈ Campello 0.22/0.25/0.12 (all 3 panels); CASH_T8 →
0.61/1.65 (SD 6.6×). Had Campello used net-of-cash + 1% winsor, his
Table-1 CASH would read ≈0.6, not 0.22. Since it reads 0.22, **the CASH
Campello actually summarized/analyzed is the plain-denominator (Table-1)
definition; the Table-8 caption "net of cash" is the paper's error.**
This is now primary-source-grounded, not just a fingerprint coincidence.

### F.1 DECISIVE — supplementary Table C.2 (Sina-directed, 2026-05-17)
Sina epistemic correction (accepted): a top-tier paper is not "wrong";
asserting so while a primary source is unread is an over-claim. Extracted
`campello_etal_2022_brexit_supplementary.pdf` (19pp,
`_extract_campello_supplementary.py` → `supp_FULL.txt`). Supplementary
structure: App A=Model, B=Proofs, C=Robustness, D=Timeline, E=Automation
(the corrigendum's "missing A/B" = MATH, NOT variable defs ⇒ no
definitions appendix overrides Table 1/8).
**Supplementary Table C.2 "Summary Statistics: Matched Sample" (p7,
programmatic verbatim) — a 4th Campello-reported CASH:**
| | Treated | Control |
|---|---|---|
| Panel A (βᵁᴷ market-based) | **0.175** | **0.164** |
| Panel B (textual) | **0.232** | **0.194** |
⇒ FOUR independent Campello CASH tables (Tbl1 A 0.22 / B 0.20 / C 0.17;
suppl. C.2 0.16–0.23) **ALL plain-denominator magnitude; ZERO at
net-of-cash ~0.6.**
**RESOLUTION (honors "paper = gospel"):** the gospel = the numbers the
authors computed; all 4 are internally consistent at plain denominator
`cheq_t/atq_{t-1}`. The lone inconsistent element is the Table-8 *caption
prose* "net of cash holdings" (most plausibly bled from the adjacent NWC
definition in the SAME caption — NWC = "working capital (net of cash)").
Faithful reading defers to the authors' consistent numbers, NOT the
inconsistent prose. **Framing corrected: NOT "paper error" — OUR error is
operationalizing the literal caption phrase as the DV (CASH_T8) instead
of the definition consistent with every Campello-reported number
(CASH_T1).** The evidentially-correct DV = Table-1 plain denominator.
⚠ ACTION = switch canonical step7 DV CASH_T8 → CASH_T1: this REVERSES a
Sina-ratified decision ⇒ requires explicit Sina authorization (locked
process; not auto-applied). Necessary-NOT-sufficient: §A DV-fix
(step10, Table-1 denom) gave δ̂ −0.007 NS — corrects the DV distribution
but does not alone recover +0.231; βᵁᴷ-tercile (§D) remains in play.
No verdict; off-ramp forbidden.

### F.2 EXECUTED — Sina authorized the switch (2026-05-17)
Sina: "since T1 matches the summary stats, i think T1 is correct. this
although must be reported to the authors." ⇒ canonical DV switched.
- `step7_fullpanel_hypothesis.py` `_cash_dv()`: net-of-cash →
  **CASH = cheq_t / atq_{t-1}** (`cheq.notna() & atq_l1>0`); docstring +
  summary.json (`cash_dv_definition`, `cash_dv_tex`) updated;
  `gen_thesis_t8_table.py` now reads the DV note from JSON (no hardcode).
- step7 re-run: **δ̂(POST·HIGH) = −0.00734  SE 0.00494  t −1.487
  p 0.137  N 18,632  firms 898  R²w 0.0895** — bit-matches the validated
  step10 DV-fix test (switch correctly applied). vs Campello +0.231\*\*\*.
  Sanity gate: N = 18,632 = the prior net-of-cash N exactly — the filter
  swap (denom>0 → atq_l1>0) moved ZERO rows (control-dropna upstream is
  the binding sample constraint), so ONLY the DV values changed, nothing
  else. δ̂ moved −0.0329 → −0.0073: DV now correct but **still negative,
  still NS, still nowhere near +0.231 — the switch did NOT fix the
  result** (necessary-not-sufficient, as stated).
- `_campello_rebuild_t8.tex` regenerated (CASH col now −0.0073, DV note
  = Table-1); `thesis_tables.pdf` recompiled (13pp, clean), opened Edge.
- Author-report DRAFT prepared: `tmp/campello_author_report_draft_2026_05_17.md`
  — **NOT sent** (outward-facing; needs Sina review + explicit send auth).
- Standing: necessary-NOT-sufficient — DV now correct but δ̂ still −0.007
  NS, NOT +0.231. βᵁᴷ-tercile (§D, mechanism unresolved) + remaining
  deviations (§G consensus z-score; MINOR under-dispersion cluster)
  still open. No replication verdict (gated on Sina); off-ramp forbidden.
- ⚠ CONSISTENCY CLEANUP PENDING (Sina auth): `step6_controls_did.py`
  `_cash_dv` is STILL net-of-cash — anyone running step6 now gets a DV
  inconsistent with canonical step7. step10 = the now-redundant T1 test
  clone. Neither deleted/edited (no cleanup w/o auth); flagged so it
  doesn't surprise later. step7 is the sole canonical DV path.

## G. CONSENSUS_EPS AUDIT — produced control (2026-05-17, Sina-directed)

Table-1 note verbatim: "CONSENSUS_EARNINGS_FORECAST is defined as the
**standardized mean 1-quarter-ahead earnings per share forecast**."
Campello Panel A: mean 0.07, SD **3.51**, med 0.09, IQR 2.05, N 42,031.

`brexit_consensus_eps.py` (full read):
- IBES Detail, MEASURE=EPS, **FPI=6** (FQ1 = 1-quarter-ahead) ✓ correct
  convention; mean of per-analyst VALUE per (gvkey,fpedats) ✓ = consensus
  (mean) forecast. 4-layer CCM linking (CUSIP8/OFTIC/TICKER time-varying)
  ✓ sound. **NO selection / aggregation / linking defect.**
- Standardization = **within-firm z-score** over 2000–2025:
  z=(mean_eps−μ_i)/σ_i (`_within_firm_zscore`, L183-194).
**VERDICT: no data/build defect; the deviation is the standardization
CHOICE — and it is provably scale-inconsistent with Campello.** A
within-firm z-score has **SD ≈ 1 by construction**; pooled it cannot
produce Campello's reported **SD 3.51**. Our post-winsor SD 0.79 (§E) is
exactly the z-score signature.

⚠ CONFLICT with prior advisor lever (surfaced, not silently switched):
earlier advisor recommended trying **forecast/price** for consensus_eps
(ledger §B "Still UNAUDITED"). Primary-source contradiction: forecast/price
≈ earnings-yield scale (~0.0–0.1) ⇒ SD **≪ 1**, even FURTHER from 3.51
than the z-score — **wrong direction**. Campello's SD 3.51 / mean 0.07 /
med 0.09 / IQR 2.05 describes a WIDE, near-symmetric distribution ⇒ the
consistent candidate is **raw consensus EPS in dollars** (no scaling, or a
small-denominator deflation that EXPANDS dispersion), NOT a compressing
transform. Recommend the Sina-gated next test = raw-$ mean_eps moment
fingerprint vs 3.51/0.09/2.05 (NOT forecast/price). Secondary, still open:
the builder's flagged fpedats-forward vs runner-shift(1) lag ambiguity
(does shift drop the "1Q-AHEAD" property) — unresolved, separate from the
scale mismatch.

### G.1 raw-$ test EXECUTED → REFUTED (Sina-chosen §G, 2026-05-17)
`_diag_consensus_raw_test.py` (builder's own validated loaders; raw
mean_eps $ vs z-score vs Campello; 1% winsor within qtr; 2010Q1-2015Q4;
IBES 2009-2016). Programmatic, both sides machine-derived. Artifact:
`tmp/campello_consensus_raw_test_2026_05_17.md`.
| scope | raw-$ SD | z SD | **Campello SD** | raw-$ med | Campello med |
|--|--|--|--|--|--|
| Univ (A) | 0.97 | 0.86 | **3.51** | +0.25 | 0.09 |
| Treat (B) | 1.49 | 0.89 | **3.40** | +0.16 | 0.01 |
| Ctrl (C) | 0.62 | 0.84 | **2.33** | +0.39 | 0.04 |
**raw-$ REFUTED**: SD ≈ 1 (≪ Campello 3.5) AND median +0.25 (Campello
≈0). Neither our z-score NOR raw-$ reproduces Campello. Under identical
1% winsor, Campello's CONSENSUS is **near-zero-centered AND heavy-tailed**
(mean/med ≈ 0, SD 3.51 ≫ IQR 2.05 ⇒ SD/IQR ≈ 1.7). That shape is NOT
raw EPS-$ (positive-centered, SD≈1), NOT a z-score (SD≈1), and NOT
forecast/price (earnings-yield ≈0.0–0.15 ⇒ SD ≪ 1, compresses FURTHER —
prior advisor forecast/price lever now empirically corroborated as
WRONG-DIRECTION). A near-zero-centered SD≫IQR heavy-tailed variable is
the signature of a demeaned/surprise or small-denominator-ratio measure
(e.g., forecast scaled by a tiny per-share base, or a forecast
revision/surprise), but Campello's text ("standardized") does not pin it
and the JFQA gives no formula. **STATUS (advisor-calibrated): CONSENSUS_EPS
= confirmed deviation; TWO candidates refuted (z-score: tested→failed;
raw-$: tested→failed) + forecast/price argued & empirically corroborated
wrong-direction. NOT vol()-style exhaustion — remaining candidates
untested; text underspecified.**
⚠ ONE specific UNTESTED candidate (advisor, likely the right one):
"standardized" may name the **IBES estimate BASIS**, not a statistical
transform. IBES ships parallel files — *Primary/Unadjusted* (per-share as
reported) vs *Standardized* (harmonized for splits/exclusions/accounting,
retroactively comparable). Our builder loads generic
`inputs/tr_ibes/tr_ibes_*.parquet` without selecting a basis. If we hold
one basis and Campello used the other, magnitude diverges (compounds in
split-heavy firms). ONE-SHOT testable: inspect `tr_ibes` schema for a
basis flag (often `PDF`/`BASIS`) or a second IBES file. Flag to Sina —
do NOT auto-execute (turn-by-turn).
Sample caveat (advisor): tested on step1 ∩ βᵁᴷ-estimable (~larger firms,
more analyst coverage ⇒ tighter consensus) — NOT Campello's full
COMPUSTAT. Composition partially attenuates the SD gap but cannot close
3.6× (refutation stands well clear of 3.51).
Bounded impact: 1 of 6 firm controls; DV + other 5 controls + SIZE clean;
NOT the βᵁᴷ binding constraint. Anti-thrash: no more transform-guessing
without Sina direction. No spec change; no verdict (gated). Off-ramp
forbidden.

### G.2 'standardized' candidate SWEEP → SUE class IDENTIFIED (2026-05-18, systematic-debugging Phase 3, Sina /goal: match summary stats)

Reference reading EXHAUSTED first: paper BODY (buk_pdfpage20 L31) =
"we add 1-quarter-ahead consensus earnings forecasts to our model" (no
def); footnote 19 = "informal tests" only; `standardiz` occurs EXACTLY
ONCE in the whole extracted paper+supplement corpus (Table-1 caption) —
no formula, no citation, no appendix def ⇒ genuine vagueness. IBES Detail
file ships an `ACTUAL` column (realized EPS) — surprise was on hand.

`_diag_consensus_standardized_sweep.py` (IBES Detail EPS/FPI=6 2009-2016,
consensus=mean across analysts, 7 operators, ONE variable varied, scopes
/1%-winsor/window fixed, Campello programmatic). Result vs Campello
(A/B/C SD 3.51/3.40/2.33, med 0.09/0.01/0.04, IQR 2.05/1.83/2.40,
center≈0):

| cand | SD A/B/C | med A/B/C | verdict |
|--|--|--|--|
| raw | 0.97/1.47/0.62 | +0.25/+0.16/+0.39 | REFUTED (level, confirms G.1) |
| zfirm | 0.86/0.89/0.84 | +0.06/+0.09/+0.08 | REFUTED (SD≈1, confirms §B/G) |
| zxsec | 0.018 | — | degenerate (winsor-collapsed) |
| f_over_disp | 21.7/16.3/24.1 | +9.4/+4.5/+15 | REFUTED (huge +center) |
| sue_abs (Δ/|act|) | 0.77/1.20/0.59 | ≈0 | center✓ SD too tight |
| **sue_disp (act−fcst)/σ_analyst** | **3.33/4.05/3.25** | +0.58/+0.28/+0.67 | **SHAPE MATCH** (SD+IQR+heavy tail); center +0.6–0.9 off |
| rev_disp | 8.2/7.0/9.5 | +0.38/+0.25/+0.49 | REFUTED (over-dispersed) |

**FINDING: CONSENSUS_EARNINGS_FORECAST = Standardized Unexpected Earnings
class** = (actual − consensus forecast) / σ(analyst estimates). Only
operator reproducing Campello's unique fingerprint (center≈0, SD 2.3-3.5,
IQR~2, SD≫IQR); every level/z/price/dispersion-level form refuted by
SHAPE, not just magnitude. Builder within-firm z-score = WRONG VARIABLE
CLASS, not a mild deviation. Supersedes §B/§G/§G.1 "minor under-dispersion
z-score deviation" and the §G.1 advisor "IBES-basis" lead (untested but
now lower-priority: basis shifts level, cannot recenter to 0 — SUE does).

RESIDUAL (root cause not fully closed): scale matches, LOCATION shifted
+0.6–0.9 vs Campello ≈0. Survives 1% winsor ⇒ structural, not outliers.
Most likely = IBES `ACTUAL` period-basis ≠ FPI=6 quarterly forecast
(annual actual vs quarterly fcst inflates numerator by ~constant), OR
deflator = stock price (Compustat prccq) not analyst-σ. Paper SILENT on
deflator + alignment ⇒ NOT primary-source-resolvable. Round-2 fork is a
Sina scope decision (IBES-only ACTUAL-alignment vs Compustat-price
join vs accept SUE-class). Artifact:
`tmp/campello_consensus_standardized_sweep_2026_05_18.md`. No spec change
(builder edit Sina-gated); no replication verdict (gated); off-ramp
forbidden.

### G.3 SUE round 2 (clean snapshot + deflator matrix) → CLASS confirmed, EXACT recipe NOT IBES-Detail-derivable (2026-05-18)

Sina-authorized "try the surprise formula to see if it's fixed."
Phase-1 data inspect (programmatic, tr_ibes 2014): `ACTUAL` is
period-aligned (1 distinct value / (gvkey,fpedats) for 18,158/18,699 —
NOT annual mismatch); clean dollar surprise (A−F) median = +$0.009 ≈ 0
(matches Campello center). Round-2 (`_diag_consensus_sue_round2.py`):
consensus+σ from each analyst's LATEST pre-period estimate (kills the
"staleness" root-cause hypothesis — center offset SURVIVED, so that
hypothesis REFUTED). Deflator matrix vs Campello (A/B/C SD 3.51/3.40/
2.33, center≈0):

| deflator | center med A/B/C | SD A/B/C | |
|--|--|--|--|
| σ_analyst (sue_pre/120) | +0.65/+0.34/+0.71 | 3.79/4.25/3.74 | SD✓ center✗ |
| firm time-series σ (FOS SUE) | +0.21/+0.09/+0.27 | 1.01/1.02/1.00 | both✗ |
| \|forecast\| | +0.04/+0.03/+0.03 | 1.19/2.09/0.98 | center✓ SD✗ |
| z-of-forecast (clean snap) | — | 0.019 (collapsed) | z can't reach 3.5 |

**No IBES-Detail-reconstructable deflator reproduces center≈0 AND
SD~3.5 on all 3 panels simultaneously.** 3 grounded hypotheses, each
trades one moment for the other ⇒ systematic-debugging Phase-4.5
"question architecture", NOT more transform-guessing.

ARCHITECTURE FINDING: variable CLASS = Standardized Unexpected Earnings
(robust — SD/IQR shape reproduced ×3 rounds; level/z-score/price all
refuted by shape). Builder within-firm z-score = wrong class (stands).
EXACT operationalization NOT closable from our data: Campello almost
certainly used the **IBES Summary Statistics** file (precomputed
MEANEST consensus + STDEV, IBES's own 1Q-ahead statistical-period
convention — the canonical consensus source). We hold ONLY IBES
**Detail** (`tr_ibes_*.parquet`, one row/analyst: value, analys, no
summary file in `inputs/tr_ibes/`; codebook + glob confirm).
Detail-reconstructed consensus/σ ≠ IBES-Summary bit-equivalent ⇒ a
DATA-SOURCE mismatch, not a code bug. This is a forward hypothesis
(NOT an off-ramp): the recipe is identifiable IF the IBES Summary
file is obtained. Bounded impact unchanged: 1 of 6 firm controls; DV
+ 5 controls + SIZE clean; NOT the βᵁᴷ binding constraint. Artifacts:
`tmp/campello_consensus_standardized_sweep_2026_05_18.md`,
`tmp/campello_consensus_sue_round2_2026_05_18.md`. No spec change
(Sina-gated); no verdict (gated); off-ramp forbidden.

### G.4 IBES statsum (canonical source) → SCALE SOLVED, center residual (2026-05-18)

Sina obtained the IBES Summary file → `inputs/tr_ibes/ibes_statsum.zip`
(unextracted, single CSV, 10.4M rows; MOVED not copied, storage). Schema
confirmed = statsum: MEANEST/STDEV/MEDEST/ACTUAL/STATPERS/FISCALP/FPI/
ESTFLAG. ESTFLAG all 'P' ⇒ the prior advisor "IBES basis" lead is MOOT
(only Primary in pull). CURCODE: foreign rows = the garbage tails
(filtered USD). `_diag_consensus_statsum.py`: EPS/QTR/FPI=6/USD/US,
horizon≥0, CCM 3-key gvkey, SUE=(ACTUAL−MEANEST)/STDEV using IBES NATIVE
consensus+σ at its own STATPERS, 2 snapshots (snap_last / snap_q≈90d),
1% winsor within cal_yr_qtr, 2010Q1-2015Q4. 656,754 rows / 11,101 firms.
Best (snap_q, sue_mean) vs Campello:

| panel | Campello m/SD/med/IQR | statsum m/SD/med/IQR |
|--|--|--|
| A | 0.07 / **3.51** / 0.09 / 2.05 | +0.59 / **3.58** / +0.50 / 3.00 |
| B | 0.01 / **3.40** / **0.01** / 1.83 | +0.16 / 3.81 / **+0.00** / 3.00 |
| C | 0.07 / **2.33** / 0.04 / 2.40 | +0.71 / 3.56 / +0.55 / 2.75 |

**SCALE SOLVED**: native STDEV deflator makes SD match (A 3.58≈3.51,
B 3.81≈3.40) — Detail reconstruction NEVER got SD+center jointly; this
does on B (median 0.00 ≈ Campello 0.01). Confirms chain: canonical
source ✓ + SUE class ✓ + native-STDEV deflator ✓. NOT a full
replication: A & C carry ~+0.5 median offset (systematic positive
surprise ≈½ STDEV = expectations walk-down); IQR ~3.0 vs ~2.0.
Scale solved, location/tail-shape residual remains.

NEXT SINGLE HYPOTHESIS (Sina-gated, NOT auto-run — anti-thrash):
Campello's verbatim = "the standardized **mean … forecast**" (NO
actual/surprise/realized in the definition). ⇒ numerator likely the
**consensus revision** `(MEANEST_t − MEANEST_{prev STATPERS})/STDEV`
— a property of the forecast itself, needs no realized actual,
symmetric (center≈0), peaked+fat-tailed (Campello SD/IQR≈1.71).
statsum's monthly STATPERS series builds it directly. Off-ramp
forbidden; forward path. No spec change (Sina-gated); no verdict
(gated).

### G.5 forecast-only revision REFUTED → explicit-text vs reported-moments INCOMPATIBLE (2026-05-18)

Sina fidelity constraint (2026-05-18): explicit def "standardized mean
1-qtr-ahead EPS forecast" has NO actual/surprise ⇒ any SUE deviates;
test forecast-only. `_diag_consensus_revision.py` (statsum, NO ACTUAL
read, ΔMEANEST/STDEV across monthly STATPERS, 2 snapshots + cum + sign):
rev_step_last SD **0.47/0.62/0.43** (Campello 3.51/3.40/2.33), med
0.000; rev_cum_q ≡0; rev_step_q N=0 (90d snap = first statpers, Δ
undefined). Month-over-month consensus revisions are mostly EXACTLY 0
(analysts rarely revise) ⇒ SD ~0.4, order of magnitude below 3.5. Real
data behaviour, robust. **Forecast-only revision REFUTED.**

DECISIVE CRUX (forecast-only inventory now exhausted): z-of-level
(SD≡1), forecast/STDEV (+15 center), within-firm z (0.8), x-sec z
(collapse), standardized revision (0.4) — **every forecast-only form
refuted vs Campello's own reported SD 3.51**. ONLY `(actual−MEANEST)/
STDEV` (SUE, statsum native) reproduces center≈0 + SD 3.58≈3.51 (§G.4).
SUE requires `actual`, absent from the one-line explicit def.

⇒ **Explicit-definition fidelity and reported-statistics fidelity are
INCOMPATIBLE for CONSENSUS** — cannot satisfy both. STRUCTURALLY
IDENTICAL to the CASH T1/T8 case (§A/§F): paper's explicit phrase vs
paper's own numbers conflict for one variable; there Sina ruled
reported numbers = gospel, caption phrase = slip (4-table evidence).
Exact parallel here: reported SD 3.51 only producible by surprise/SUE.
Interpretive verdict GATED on Sina (same as CASH); off-ramp forbidden
(this is a faithful finding, not surrender). No spec/builder change
(Sina-gated). Artifact: `tmp/campello_consensus_revision_2026_05_18.md`.
Bounded impact unchanged: 1 of 6 controls; DV+5 controls+SIZE clean;
NOT the βᵁᴷ binding constraint.

### G.6 step7 sensitivity: CONSENSUS swap does NOT flip the sign (2026-05-18, Sina-authorized)

`_diag_step7_consensus_sue_sensitivity.py` (imports step7's own
helpers — no code drift; one variable isolated; COMMON sample). Same
eq-(14) PanelOLS, same 16,036 fq / 818 firms, ONLY the consensus
column swapped:

| consensus | δ̂ | SE | p | N |
|--|--|--|--|--|
| builder z-score (step7 baseline) | −0.00781 | 0.00560 | 0.163 | 16,036 |
| IBES statsum SUE (best §G.4 match) | −0.00835 | 0.00559 | 0.136 | 16,036 |

Δδ̂ (SUE − z) = **−0.00054** (more negative, NOT toward Campello
+0.231***). **SUE does NOT solve the negative sign** — negative→
negative, NS→NS. Consistent with §F.2 (larger DV lever moved δ̂ only
−0.033→−0.007) and §D (βᵁᴷ-tercile = binding constraint, not a
control). PROVES empirically: CONSENSUS_EPS operationalization is a
non-driver of the non-replication; 1 of 6 controls cannot flip
−0.008 NS → +0.231***. ⇒ The §G.5 interpretive crux (explicit-text
z-score vs reported-stats SUE) is now DECOUPLED from the thesis
headline — either ruling leaves δ̂ unchanged. CONSENSUS thread CLOSED
as non-driver; binding constraint remains §D βᵁᴷ-tercile. Artifact:
console (no parquet — read-only sensitivity). No builder/spec change;
no commit; no replication verdict (gated). Off-ramp forbidden.

### G.7 SINA RATIFIED VERDICT — keep explicit definition, report non-replication (2026-05-18)

Sina decision (verbatim intent, 2026-05-18): "reverse the sue. we keep
their own definition of the … thing and report a non replication."
This is the §G.5-gated interpretive call, now MADE by Sina (his to
raise — not an off-ramp; off-ramp rule binds the assistant, not Sina).

RULING:
1. **No SUE adoption.** SUE was diagnostic-only (`_diag_*` scripts);
   NEVER wired into the builder or step7 ⇒ ZERO code revert, zero
   commits to undo. `brexit_consensus_eps.py` stays = within-firm
   z-score (the best-faith literal reading of the underspecified
   "standardized"; the builder docstring itself flags the ambiguity —
   there is no verbatim formula in the paper).
2. **CONSENSUS_EARNINGS_FORECAST = documented component-level
   NON-REPLICATION.** Under Campello's explicit one-line definition
   ("standardized mean 1-qtr-ahead EPS forecast"), our faithful
   z-score reading yields SD ≈ 0.79–0.86 vs Campello reported SD
   3.51/3.40/2.33. The only construction reproducing the reported
   moments is SUE = (actual−consensus)/STDEV (§G.4, statsum: SD
   3.58≈3.51), which injects a realized-`actual` term ABSENT from the
   explicit definition. Sina rules: honor the explicit definition over
   the reported number ⇒ report honest non-replication of this
   control's reported summary statistic.
3. **Divergence from CASH precedent — by Sina, defensible, recorded.**
   CASH (§F): reported numbers = gospel (4 mutually-consistent tables
   + plausible caption-slip). CONSENSUS: one-line def vs one SD;
   matching requires inventing an unnamed `actual` term ⇒ keep
   definition. Different facts ⇒ different ruling; not a contradiction.
4. **Headline impact = NONE (already proven, §G.6).** δ̂ −0.008 NS
   under either consensus operationalization (Δ 0.0005). This
   component non-replication does NOT affect the thesis main result;
   binding constraint stays §D βᵁᴷ-tercile.

CONSENSUS_EPS THREAD CLOSED (Sina-ratified). Diagnostic scripts +
§G.1–§G.7 RETAINED as the audit evidence basis (do NOT delete —
audit integrity). Downstream, Sina-gated (NOT auto-done, turn-by-turn):
(a) thesis prose/table framing of the documented non-replication;
(b) optional inclusion of the CONSENSUS definition under-specification
in the author-report draft (separate from the CASH inconsistency).
No commit (unauthorized). No builder/spec change. Off-ramp forbidden.

### G.8 §G.7 CORRECTED — final CONSENSUS = statsum MEANEST z (Sina-ratified, BUILT) (2026-05-18)

§G.7 MISREAD Sina's ruling: I took "keep their definition" as "keep
the OLD Detail-file within-firm z-score builder." Sina clarified
(repeated, emphatic): the final DiD table must have CONSENSUS **built
from the IBES SUMMARY (statsum)** source. 3-step done; corrected on
merit: Campello "standardized **mean** 1Q-ahead forecast"; statsum
MEANEST *is* that mean forecast from the canonical source; "reverse
the sue" = drop the `actual` term, NOT drop the statsum source;
"standardized" = z-score (Sina's own stated definition). The Detail
z-score was always our arbitrary reconstruction.

RATIFIED FINAL CONSTRUCT (BUILT, in the canonical table):
CONSENSUS_EARNINGS_FORECAST = pooled z-score of IBES-summary
`statsum` MEANEST at the 1-quarter-ahead snapshot (~90d STATPERS;
EPS/QTR/FPI=6/USD/US; CCM gvkey). Forecast-only (NO ACTUAL — SUE
reversed). Reported as honest non-replication of the Campello
CONSENSUS reported moment (z ⇒ SD≈1 vs reported 3.51); this was
Sina's §G.5 interpretive call.

EXECUTED: `_build_final_did_statsum_consensus.py` (imports step7
helpers, no drift; only consensus source swapped) → new canonical
step7 output `step7_fullpanel_hypothesis/2026-05-18_012923/` →
`gen_thesis_t8_table.py` regenerated `_campello_rebuild_t8.tex` →
`thesis_tables.pdf` recompiled (13pp, latexmk exit 0, reopened Edge).

FINAL TABLE (tab:h1_5_brexit_did):
δ̂(POST·HIGH) CASH = **−0.0075** SE 0.0048 p 0.118 **N 18,661 / 891
firms** vs Campello **+0.231\*\*\*** SE 0.059 N 17,170. Consensus EPS
row = −0.0031\*\*\* (was +0.0043\*\* under Detail z) — control changes,
**headline δ̂ unchanged** (−0.0073→−0.0075), re-confirming §G.6
(consensus operationalization immaterial to the result). Sign-and-
significance NON-REPLICATION stands; binding constraint = §D βᵁᴷ
(placebo `brm8qlkhh` still running). Builders unchanged on disk;
new step7 output dir written; NOT git-committed (unauthorized).
§G.7's "keep Detail z-score" SUPERSEDED by this entry.

### G.9 statsum-z DEGENERACY BUG found + fixed; summary-stats table refreshed (2026-05-18)

Sina: "the table is stale. update it for other variables also."
Regenerated the full summary-stats compare (all 8 vars fresh from
latest step1/step3) + swapped CONSENSUS_EPS source to the ratified
`_statsum_meanest_z` (single source of truth, no drift).

BUG caught in first refresh (Iron Law, not papered over): the §G.8
`_statsum_meanest_z` standardized RAW MEANEST with a POOLED mean/SD;
statsum MEANEST carries data-error tails (|MEANEST|≫1e2) even after
USD/US filter ⇒ pooled SD blows up ⇒ z degenerate (SD 0.000, IQR
0.000, RAW z∈[−142,+0.01]). The §G.8 final-DiD build used this
degenerate control (its "immateriality" was partly artefactual).
ROOT-CAUSE FIX (faithful, not symptom-chasing): Campello verbatim
"All variables are winsorized at the 1% level" — apply the paper's
OWN 1% winsor to MEANEST (within cal_yr_qtr) BEFORE standardizing.
A z-score of un-winsorized data-error tails is not a valid
standardization.

RE-RAN final DiD + summary-stats + both tex + recompiled (latexmk
exit 0, 13pp, Edge). Final state:
- **DiD headline UNCHANGED**: δ̂ = **−0.00750** SE 0.00477 p 0.116
  N 18,661 / 891 firms (step7 `2026-05-18_013848`) vs Campello
  **+0.231\*\*\*** — consensus still immaterial (§G.6), now with a
  VALID (non-degenerate) control.
- **CONSENSUS_EPS** (ratified statsum MEANEST winsor→z): mean
  +0.069/+0.057/+0.096 (A/B/C) vs Campello +0.07/+0.01/+0.07 —
  **center MATCHES**; SD 0.137/0.178/0.085 vs 3.51/3.40/2.33, IQR
  ~0.07 vs ~2 — the documented NON-REPLICATION (z ⇒ SD≪3.51;
  Sina-ruled §G.7/§G.8). Flagged CHECK, real numbers (not
  degenerate).
- **ALL OTHER VARIABLES MATCH** Campello across A/B/C (CASH_T1,
  SIZE, STOCK_RETURNS, TOBIN_Q, CASH_FLOW, SALES_GROWTH) — inputs
  sound. CASH_T8 = superseded net-of-cash (CHECK by design, §F.2).
Artifacts refreshed: `tmp/campello_summary_stats_compare_2026_05_17.md`,
`docs/Draft/_campello_summary_stats.tex`, `_campello_rebuild_t8.tex`,
`thesis_tables.pdf`. No git commit (unauthorized). Builders unchanged
on disk. §D βᵁᴷ placebo `brm8qlkhh` still running.

### G.10 thesis-deliverable trims (Sina 2026-05-18)

Sina: "drop cash T8, also drop the row macro controls from the brexit
table." Both done at the GENERATOR layer (programmatic, no hand-edit):
- `gen_summary_stats_tex.py`: skip rows where var startswith `CASH_T8`
  (+ notes clause rewritten — no longer references CASH_T8; "lone
  CHECK row CONSENSUS_EPS"; removed the false "$z$⇒SD≈1" claim that
  contradicted the table's measured SD ~0.14, now "dispersion far
  below Campello SD 3.51"). CASH_T8 STILL retained in the audit
  artifact `campello_summary_stats_compare_2026_05_17.md` + §F (the
  net-of-cash refutation evidence is preserved; only the thesis
  deliverable table drops it).
- `gen_thesis_t8_table.py`: removed the `Macro controls & Absorbed`
  table row (the methodology note that macro is FE-absorbed stays —
  accurate, explains the row's absence).
Both tex regenerated, `thesis_tables.pdf` recompiled (latexmk exit 0),
grep-verified: zero `Macro controls` / `CASH_T8` in the generated
tex. DiD numbers unchanged (generator-only change). No git commit
(unauthorized).

## H. TEXTUAL-SEARCH treatment arm (Sina-authorized 2026-05-18)

§D βᵁᴷ placebo `brm8qlkhh` was **Sina-killed** (not completed; §D
mechanism discriminator OFF, not re-running). Sina: "go for the
textual arm."

### H.1 spec pinned (verbatim, programmatic) + col-4 benchmark
Campello §IV.A.2 (buk_pdfpage14.txt L225-257): 9 keywords —
Brexit, Great Britain, Uncertainty (body) + Referendum, Uncertain,
United Kingdom, UK, U.K., G.B. (fn14). Treated = >5 entries in 2015
10-K; control = 0; 1-5 excluded. Campello realized 807/433
(buk_pdfpage16 L181-184). **Col-4 benchmark (programmatic
table8_pdfpage31 L298-308): Campello CASH textual-treatment δ̂ =
+0.357\*\*\* SE 0.062 N 24,195 R² 0.24** (POST×HIGH_10K_ENTRIES;
βᵁᴷ CASH +0.231\*\*\* stays col-3). Table 8 reports BOTH treatments
side-by-side (6 cols: CASH/NWC/PROFITS × βᵁᴷ/textual).

### H.2 fresh ETL built + run (`step3b_textual_treatment.py`)
Spec authority = paper (verbatim); archived `parse_10k_keywords.py`
consulted for data-plumbing ONLY (zip/SRAF-filename/dual-regex/
CCM-CIK), re-implemented fresh (locked process). CCM LINKPRIM∈{P,C}
LINKTYPE∈{LU,LC} (rebuild convention; archived used P-only — noted,
data-plumbing not Campello spec). Streamed 826 MB in-place
(memory-aware), 220s. Output `step3b_textual_treatment/
2026-05-18_021740/`. Result vs Campello:

| | ours | Campello |
|--|--|--|
| filings parsed | 9,270 (0 err) | — |
| CIKs (post-dedupe) | 7,813 | — |
| CIK→gvkey mapped | 4,083 (**unmapped 3,730 = 48%**) | — |
| treated (>5) | **3,037** | 807 |
| control (==0) | **278** | 433 |
| excluded (1-5) | 768 | — |

3 deviations (all characterized, none a code defect): (1) treated
3.8× over — the PRE-FLAGGED generic-keyword gap (Uncertainty/
Uncertain dominate; undisclosed Campello scoping constraint;
documented-deviation, verdict Sina-gated, cf CONSENSUS/CASH);
(2) control under (278<433) — same broad-match mechanism (fewer
exact-zeros); (3) 48% CIK unmapped — consistent w/ EDGAR≫Compustat
universe (SRAF all-filers vs CCM subset; archived P-only precedent +
literature norm) but NOT programmatically isolated this run. Control
278 = binding DiD scarcity (workable w/ FE; Campello's own 807/433).
CHECKPOINT (turn-by-turn): wire step3→DiD now (documented-deviation
arm, over-count pre-authorized) vs unmapped-diagnostic first — Sina's
call. No commit; no verdict (gated). off-ramp forbidden.

### H.3 textual-arm eq-(14) DiD — RAN (Sina: keep words, D3 deferred)

Sina 2026-05-18: "we keep the words" (verbatim 9-word list stays;
over/under-count = documented deviation). Confirmed step3b uses
Campello's **verbatim ABSOLUTE rule** (>5 treated / ==0 control /
1-5 excluded) — NOT p33/p67 terciles (terciles = the βᵁᴷ arm's rule;
applying them here would deviate from §IV.A.2). D3 (48% unmapped)
deferred per Sina ("after the fix").

`_build_textual_did.py` — canonical eq-(14) clone, imports step7 +
§G.8 statsum-z consensus (no drift); ONLY treatment swapped step3
βᵁᴷ → step3b textual. Result:

| | δ̂ | SE | p | N | firms |
|--|--|--|--|--|--|
| **Rebuild CASH textual** | **+0.00986** | 0.00828 | 0.234 | 38,299 | 1,782 |
| Campello T8 col.2 (textual CASH) | +0.357 | 0.062 | <0.01 | 24,195 | — |
| (ref) Rebuild CASH βᵁᴷ | −0.00750 | 0.00477 | 0.116 | 18,661 | 891 |

**Key:** textual arm is **SIGN-CORRECT (+, matches Campello's
direction)** — unlike the βᵁᴷ arm (negative). But NS (p 0.23) and
~36× below +0.357. ⇒ directional agreement, magnitude/significance
non-replication. Larger N (38,299) consistent with treated
over-count. Output `step7b_textual_did/2026-05-18_023324/`
(step7-schema summary.json, campello_reference = T8 col.2
+0.357\*\*\* programmatic). NOT a verdict (Sina-gated); off-ramp
forbidden. Next: wire as a table column (layout = Sina-gated
presentation decision); generator extension + recompile pending.
No git commit.

### H.4 §1+7-scoped textual arm — supplement diligence → sample match, effect NOT (2026-05-18)

Sina paused step3b2(7-kw) for a supplement check (good call). Finding
(firm, programmatic supp_FULL.txt L1341-1343, Appendix E AUTOMATION,
verbatim): Campello's text measures parse 10-K **Item 1 (Business) +
Item 7 (MD&A)** only — explicit for automation, implied-by-house-
convention for Brexit (§IV.A.2 silent on scope). Nothing else missed:
Brexit 9-word list + >5/0 rule fully complete in supplement (repeated
verbatim ×3, no extra words/threshold/proximity). Sina: "implement
sec1+7" (9-kw verbatim kept; the 7-kw drop NOT taken).

`step3b3_textual_treatment_sec17.py` (fresh; LM longest-span Item
parse; TOC skipped; §1+7-unparseable EXCLUDED no fallback) →
`_build_textual_did_sec17.py`. Results vs full-filing & Campello:

| arm | treated | control | δ̂ | p | N |
|--|--|--|--|--|--|
| textual full-filing 9-kw (step3b) | 3,037 | 278 | +0.00986 | 0.234 | 38,299 |
| **textual §1+7 9-kw (step3b3)** | **1,458** | **465** | **+0.00152** | 0.771 | **22,625** |
| Campello T8 col.2 textual | 807 | 433 | +0.357\*\*\* | <.01 | 24,195 |

**Diligence win:** §1+7 ⇒ control **465≈433** (was 278; 36%-under →
+7%), N **22,625≈24,195** — Campello's textual SAMPLE/universe
structurally reproduced via the supplement-derived scope. §1+7
parse-fail 2,117 (≈23%) excluded (non-standard 10-Ks; reported).
**Effect still NON-replicated:** δ̂ +0.0015 sign-correct (+) but
~235× below +0.357, p 0.77 (weaker than full-filing +0.0099).
Consistent overall pattern: rebuild reproduces Campello's
sample/structure, NOT the effect size. Residual treated over (1,458
vs 807) ≈ the generic uncertainty/uncertain breadth (Sina's original
7-kw instinct — untaken; could be a further labeled variant).

OOM FIX (canonical, behavior-preserving): shared §G.8
`_statsum_meanest_z()` whole-CSV read OOM'd under memory pressure →
chunked filter-early read. NUMERICALLY IDENTICAL (same mask;
order-independent downstream); bounds memory (Sina memory-aware
rule). All DiD runners affected equally; βᵁᴷ δ̂ unchanged by
construction.

CASH arms summary: βᵁᴷ −0.0075 | txt-full +0.0099 | txt-§1+7
+0.0015 | UncResCEO +0.0074 — all NS; Campello βᵁᴷ +0.231\*\*\* /
txt +0.357\*\*\*. NEXT: wire both textual arms into the table beside
βᵁᴷ-CASH/UncResCEO/Campello (Sina layout directive); generator 5-col
+ recompile. No commit; no verdict (gated); off-ramp forbidden.

### H.5 final table WIRED — 6-col, both textual arms (Sina layout directive)

`gen_thesis_t8_table.py` rewritten 3-col→6-col (JSON-driven, no
hardcoded numbers): (1) CASH βᵁᴷ | (2) CASH textual full-10K | (3)
CASH textual §1+7 | (4) UncResCEO | (5) Campello T8 col.1 βᵁᴷ | (6)
Campello T8 col.2 textual — mirrors Campello Table 8's own dual-
treatment structure (per Sina "both textual arms together side by
side cash and uncres and campello"). Sources: step7
2026-05-18_013848 + step7b 023324 + step7b3 025316 + step9 220005.

Final table (`tab:h1_5_brexit_did`, thesis_tables.pdf, recompiled
latexmk exit 0, Edge):

| | δ̂ | SE | N |
|--|--|--|--|
| (1) CASH βᵁᴷ | −0.0075 | 0.0048 | 18,661 |
| (2) CASH textual full-10K | +0.0099 | 0.0083 | 38,299 |
| (3) CASH textual §1+7 | +0.0015 | 0.0052 | 22,625 |
| (4) UncResCEO | +0.0074 | 0.0304 | 7,142 |
| (5) Campello βᵁᴷ | **+0.231\*\*\*** | 0.059 | 17,170 |
| (6) Campello textual | **+0.357\*\*\*** | 0.062 | 24,195 |

All 4 rebuild arms NS; both textual sign-correct (+) vs Campello,
βᵁᴷ sign-wrong (−); none near Campello magnitudes. Notes document:
verbatim 9-kw kept, §1+7 = Campello Appendix-E house-convention
scope, treated/control deviations (3,037/278 full; 1,458/465 §1+7 vs
807/433), no replication verdict (gated).

LaTeX bug found+fixed (Iron Law, log-read): JSON `campello_reference.
source` for the textual benchmark contained `×` + unescaped `_`
(`POST×HIGH_10K_ENTRIES`, `table8_pdfpage31.txt`) → "Missing $" at
first compile (exit 12). Added `_tex()` escaper applied to the two
JSON-sourced source strings (cash_dv_tex left as intentional LaTeX).
Recompiled exit 0; grep-verified 6-col structure + δ̂/N rows.

Sina's textual-arm directive COMPLETE: §1+7 implemented, both textual
arms in the table beside βᵁᴷ-CASH/UncResCEO/Campello. No git commit
(unauthorized). No verdict (gated). off-ramp forbidden.

### H.6 table trim (Sina 2026-05-18): drop full-10K col + minimal notes

Sina: "make the notes minimal. drop the full 10k column." Generator
6-col→**5-col** (`lccccc`): (1) CASH βᵁᴷ | (2) CASH textual §1+7 |
(3) UncResCEO | (4) Campello βᵁᴷ | (5) Campello textual. The
full-filing textual arm (step7b, +0.0099/N 38,299) removed from the
deliverable (its ETL/DiD artifacts + §H.1-H.4 retained as audit
record; only the thesis table drops it — §1+7 is the kept textual
arm, Campello-house-convention-faithful). Notes collapsed ~6
paragraphs → 1 tight paragraph. Campello N/R² verbatim-confirmed
present (17,170/0.21 βᵁᴷ; 24,195/0.24 textual; table8_pdfpage31
L307-308). grep-verified no full-10K residue; recompiled latexmk
exit 0, Edge. JSON-driven, no hardcoded numbers. No git commit;
no verdict (gated).

### H.7 UncResCEO × §1+7-textual added (Sina 2026-05-18)

Sina: "do uncres for textual sec1and7 also". Built
`_build_uncres_did_sec17.py` — UncResCEO DV (reuse step9
`_uncres_dv`) × §1+7-textual treatment (step3b3) on the canonical
statsum-z stack (so CASH§1+7 vs UncRes§1+7 differ ONLY in DV; clean
comparison). NB consensus = §G.8 statsum-z vs step9 (UncRes×βᵁᴷ)
Detail-z — immaterial (§G.6 ~0.0005), noted not silently mixed.
Result: δ̂ **−0.03387** SE 0.03071 p 0.270 N 9,851 / 548 firms
(R²w −0.0016). vs UncRes×βᵁᴷ +0.0074 — UncRes sign flips by
treatment (βᵁᴷ +, §1+7 −), both NS; no Campello UncRes benchmark
(novel). Output `step9b_uncres_textual_sec17/2026-05-18_035718`.

Generator → **6-col** (symmetric DV×treatment): (1) CASH βᵁᴷ |
(2) CASH §1+7 | (3) UncRes βᵁᴷ | (4) UncRes §1+7 | (5) Campello βᵁᴷ
| (6) Campello textual. δ̂ −0.0075 | +0.0015 | +0.0074 | −0.0339 |
0.231\*\*\* | 0.357\*\*\* ; N 18,661/22,625/7,142/9,851/17,170/24,195.
grep-verified, latexmk exit 0, Edge. JSON-driven. No git commit;
no verdict (gated); off-ramp forbidden.

### H.8 treated/control counts added to table notes (Sina 2026-05-18)

Sina: "write the treat/control firm counts in the notes." Added a
notes clause, JSON-sourced (no hardcoding): βᵁᴷ ours from
step3_treatment `counts_step1_panel` (565/482), Campello from
`campello_reference_counts` (449/360); textual §1+7 ours from
step3b3 `treated`/`control` (1,458/465), Campello from
`campello_realized` (807/433). Plus the assignment-universe vs
estimation-sample (listwise attrition) note explaining why the
\emph{Firms} row is smaller. Generator reads step3_treatment +
step3b3 summary.json live. Recompiled latexmk exit 0, Edge. No git
commit; no verdict (gated).
