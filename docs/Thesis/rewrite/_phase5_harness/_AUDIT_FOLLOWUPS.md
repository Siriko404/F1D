# Audit follow-ups -- candidate findings surfaced DURING fixes (not yet adjudicated)

Queue these into the MED/LOW adjudication pass. Each is logged, NOT fixed.

## CF-1 (from H1 advisor check, 2026-06-28) -- regressor vs regressand citation precision
- WHERE: section 2.3, the generated-regressand paragraph (l.201 of the clone wrapper).
- POINT: Pagan(1984) is titled for generated *regressors* (RHS); the kept sentence says
  "\citet{dwz} themselves use the residual *as a regressor* in their own second step." But the
  thesis uses UncResCEO as a generated *regressand* (the DV) -- the same paragraph states this.
  So the cited precedent (Pagan + DWZ-as-regressor) is the regressor case, while our use is the
  regressand case. A DWZ-faithful examiner could note the chain does not cleanly cover the
  regressand setting (and the right correction differs between the two cases).
- WHY NOT FIXED IN H1: the H1 fix only removes the unsupported "no-change" claim; uncorrected SEs
  are honest whichever case applies, so the fix is robust to this. Severity likely LOW-MED.
- CANDIDATE RESOLUTIONS (for Sina, later): (a) state the regressand (LHS) case is generally milder
  than the regressor case Pagan addresses -- but this needs a citation; do NOT assert it unsourced;
  (b) add a generated-regressand-specific reference; (c) leave as-is if judged defensible. Decide
  during adjudication, not unilaterally.
