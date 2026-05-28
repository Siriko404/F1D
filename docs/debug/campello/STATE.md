# Campello Brexit DiD — Fresh Rebuild State (2026-05-28, FINAL)

## FINAL STATE

**DiD regression (Spec B: Firm FE + Industry×Quarter FE, two-way clustered):**

| Metric | Current | Paper | Status |
|--------|---------|-------|--------|
| δ (interaction) | 0.102* | 0.231*** | At 44% of paper |
| SE | 0.060 | 0.059 | Match ✓ |
| p | 0.089 | <0.01 | Marginal sig |
| N | 17,195 | 17,170 | +25 ✓ |
| DiD firms | 811 | 809 | +2 ✓ |
| Within R² | 0.03 | (0.21 FE-incl) | Reporting convention ✓ |

Pipeline: `tmp/run_did_fix1.py` (current best) — beta on Compustat survivors + rank tercile + 1% CEPS winsor.

## ALL RA HYPOTHESES — STATUS

### RA Round 1 (file 19): Population + construction + tercile
1. **Population fix** — DONE. Beta on Compustat survivors. Delta: 0.067→0.107. N: 18,660→17,997.
2. **SHRCD/EXCHCD filter** — TESTED. Overshoots on HIGH, marginal on LOW.
3. **Rank tercile** — DONE. Fixed control "growth" anomaly. N: 17,997→17,195.
4. **Construction sensitivity** — DONE (see sweep below).

### RA Round 2 (file 20): R² + control count + delta
5. **R² gap** — RESOLVED. FE-inclusive vs within reporting convention.
6. **Tercile base** — TESTED. Full-distribution: 0 control (bottom third all negative).
7. **Winsorization order** — TESTED. Current (winsor-then-derive) is correct.
8. **CONSENSUS_EPS 1% winsor** — DONE. Negligible effect.
9. **CONSENSUS_EPS standardization** — TESTED. z-score vs demean, small effect.

### RA Round 3 (file 21): Attrition + construction
10. **DV formula** — TESTED. Table 8 `cheq/(atq_lag−cheq)` correct. Table 1 gives δ=0.
11. **I/B/E/S differential attrition** — AUDITED 2026-05-28. **FALSIFIED.** HIGH firms LESS covered (19.1% missing I/B/E/S) than LOW (8.6%). All stricter I/B/E/S criteria make H/L ratio WORSE. Paper's H/L=1.25 asymmetry cannot come from I/B/E/S.

### RA Round 4 (file 22): SE invariance + CF beta + I/B/E/S
12. **SE invariance argument** — ACCEPTED. Same N, SE, Var(X) → same σ_resid, but Cov(Y,X) 2.3x smaller → treatment composition.
13. **Log vs level vol** — TESTED. Log vol moves cutpoints away from paper.
14. **Min-days/min-months sweep** — TESTED (25 combinations). T2 ranges 0.62→0.69, best at MinDays=10/MinMon=12 (T2=0.6894). T1 never reaches 0.28.
15. **RET vs RETX** — TESTED. 99% identical, negligible.
16. **Data sources** — RULED OUT. Bloomberg/Yahoo/BoE identical by direct comparison.
17. **CF beta (beta^UK_i,CF)** — ATTEMPTED ×2. v1: rank corr 0.14. v2 (2026-05-28, 30+ quarters VAR, 3,484 firms): rank corr 0.22, top-tercile overlap 22.9%. CF news extremely noisy (SD=30.5 vs baseline SD=1.3). **FAILED** as diagnostic tool — firm-level VAR too noisy without paper's exact method/code.
18. **I/B/E/S asymmetric attrition** — AUDITED 2026-05-28. **FALSIFIED** (see #11 above).

### Post-exhaustion diagnostics (2026-05-28)
19. **Negative beta proportion** — 39.1% of survivor betas are negative. Full-distribution bottom tercile is entirely negative (T1=−0.078). Paper would need ≤~20% negative betas for full-distribution terciles to produce viable LOW count. Confirms distribution shape fundamentally different from paper.

## ROOT CAUSE (refined)

ALL 19 RA hypotheses tested. Three fixes applied (population, rank tercile, 1% CEPS winsor). Remaining gap irreducible without paper's exact code.

The paper never documents: CRSP share-code/exchange filters, monthly vol construction method, minimum observations per firm, winsorization of returns/betas, CF news estimation methodology, exact tercile population, or the CCM link specification. No public replication package exists (JFQA pre-2024 submission).

The SE invariance argument proves the gap is treatment composition — which firms land in which tercile. Our beta distribution has 39% negative (vs paper's implied ≤20%), cutpoints 0.25/0.67 (vs 0.28/0.68), and different tercile membership. All on identical input data.

Reproducibility ceiling confirmed. Thesis writeup: δ=0.102* as best-achievable, document the vol() underspecification as the reproducibility limitation.

## KEY FILES

### Claude-web research (docs/debug/campello/):
- `01–10`: Variable definitions, CASH/CASH_FLOW/CONSENSUS_EPS diagnostics
- `11–15`: Beta^UK_i specification, Bloom methodology, thresholds, vol() forensic
- `16–22`: Econometric process, sample construction, RA diagnosis rounds 1-4

### Scripts (tmp/):
- `run_did_fix1.py`: **CURRENT BEST** DiD pipeline
- `run_did.py`: Original (pre-fixes)
- `build_beta_uk.py`: Original beta on full CRSP
- `diag_*.py`: All diagnostic scripts (filter trace, population, SHRCD/EXCHCD, tercile base, winsor R², cash DV, log-vol, sweep, consensus)
- `diag_ibes_attrition.py`: I/B/E/S coverage audit (2026-05-28)
- `build_beta_cf.py`: CF beta v1 (rank corr 0.14)
- `build_beta_cf_v2.py`: CF beta v2 (rank corr 0.22, 2026-05-28)

### Data:
- `tmp/beta_uk_final.parquet`: β^UK_i from full CRSP (5,714 firms — needs Fix 1 rebuild for production)
