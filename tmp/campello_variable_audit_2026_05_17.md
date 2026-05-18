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

### Still UNAUDITED (audit remains PARTIAL — next batch = βᵁᴷ, IN PROGRESS)
βᵁᴷ eq-(13): firm vol, vol(FTSE100/SP500/FX), window/form (PRIOR
load-bearing suspect); step3 tercile cut; step1 filters + lag direction;
POST; FIC100×qtr FE; winsor mechanics. No spec change; no verdict
(gated on Sina). Off-ramp forbidden.
