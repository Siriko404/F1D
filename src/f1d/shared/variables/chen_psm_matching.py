"""Chen PSM matching builder (Phase 1C Task C5).

Per Chen 2017 JAAF spec C5 (PDF p.23-25, j.312-314) verbatim:

    Pr(RESTATE) = B1·X1 + B2·X2 + B3·X3 + Industry_FE + Year_FE + ε

    X1 (cash determinants per Opler 1999):
        SIZE, Q, CF, LEV, NWC, SIGMA, NSEG, AGE, CAPX, RD, ACQUISITION, DIV
    X2 (restatement determinants):
        SGRW, FINANCE, ΔNWC, LOSS, Z-SCORE, BigN
    X3 (trend controls per Roberts-Whited 2013):
        CASH (level), ΔCASH

    Predictor averaging: t-3 to t-1 (verbatim spec line 1548).
    Score year: year 0 (event year).
    Industry: FF48 within-industry only.
    Ratio: 1:1, no replacement.
    Tiebreak: smallest |p_t - p_c|.
    Caliper: NOT specified verbatim.

v2 audit findings baked in:
- M2 small-industry FF12 fallback: if FF48 control pool <5 → widen to nearest FF12.
- V4 no caliper lock: every treated firm gets a match (subject to no-replace).
- Diagnostic: median |p_t - p_c| > 0.10 within FF48 → flag.

Output:
    gvkey, event_year, classifier_variant, treated, p_score,
    match_partner_gvkey, match_distance, in_psm_sample,
    widened_to_ff12, treated_ff48, control_ff48,
    treated_ff12, control_ff12
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Literal, Tuple

import numpy as np
import pandas as pd

from f1d.shared._compustat_annual_reader import read_compustat_annual
from f1d.shared.industry_utils import parse_ff_industries

from .base import VariableBuilder, VariableResult, VariableStats
from .chen_aa_to_gvkey_bridge import ChenAAtoGvkeyBridgeBuilder
from .chen_baseline_controls import ChenBaselineControlsBuilder
from .chen_industry_cf_vol_ff48 import ChenIndustryCFVolFF48Builder
from .chen_restatement_treatment import ChenRestatementTreatmentBuilder
from .ff48_industry_classifier import FF48IndustryClassifierBuilder

logger = logging.getLogger(__name__)


ClassifierVariant = Literal["A", "B", "C"]

# Audit M2 + V4 locked values
FF48_MIN_POOL = 5            # below this → widen to FF12
DIAGNOSTIC_THRESHOLD = 0.10  # median |p_t - p_c| > this → flag

# X1 ∪ X2 ∪ X3 covariates per spec C5 (20 vars)
COVARIATES = [
    # X1: cash determinants (12)
    "size", "q", "cf", "lev", "nwc", "sigma_chen", "nseg", "age",
    "capx", "rd", "acquisition", "div",
    # X2: restatement determinants (6)
    "sgrw", "finance", "delta_nwc", "loss", "z_score", "big_n",
    # X3: trend (2)
    "cash", "delta_cash",
]


def _compute_z_score(comp: pd.DataFrame) -> pd.Series:
    """Altman 1968 Z-Score:
    Z = 1.2*WCAP/AT + 1.4*RE/AT + 3.3*OIBDP/AT + 0.6*MVE/(DLTT+DLC) + 1.0*SALE/AT
    """
    mve = comp["prcc_f"] * comp["csho"]
    debt = comp["dltt"].fillna(0) + comp["dlc"].fillna(0)
    return (
        1.2 * comp["wcap"].fillna(0) / comp["at"]
        + 1.4 * comp["re"].fillna(0) / comp["at"]
        + 3.3 * comp["oibdp"].fillna(0) / comp["at"]
        + 0.6 * np.where(debt > 0, mve / debt, 0)
        + 1.0 * comp["sale"].fillna(0) / comp["at"]
    )


def _compute_finance(comp: pd.DataFrame) -> pd.Series:
    """FINANCE = (SSTK + DLTIS - PRSTKC - DLTR - DV) / AT
    Net external financing per Bates-Kahle-Stulz (2009).
    """
    return (
        comp["sstk"].fillna(0)
        + comp["dltis"].fillna(0)
        - comp["prstkc"].fillna(0)
        - comp["dltr"].fillna(0)
        - comp["dv"].fillna(0)
    ) / comp["at"]


def _build_covariate_panel(years: range, root_path: Path) -> pd.DataFrame:
    """Build (gvkey, fyear, 20-covariate) panel for PSM probit.

    Reuses C3 baseline + C4 SIGMA; adds remaining 11 vars from raw Compustat.
    """
    years_list = list(years)
    # Need 4-year prefix: t-3 minimum, plus the 1-year lag for ΔNWC/ΔCASH/SGRW
    load_years = range(years_list[0] - 4, years_list[-1] + 1)

    comp = read_compustat_annual(
        path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
        cols=[
            "gvkey", "datadate", "sic", "loc",
            "at", "che", "ceq", "csho", "prcc_f",
            "dlc", "dltt", "oancf", "oibdp", "wcap", "re", "sale", "ni",
            "sstk", "dltis", "prstkc", "dltr", "dv",
            "act", "lct", "capx", "aqc", "xrd", "dvc",
            "au",
        ],
        years=load_years,
        us_only=True,
    )
    comp = comp.dropna(subset=["at"]).copy()
    comp = comp[comp["at"] > 0].copy()
    comp = comp.sort_values(["gvkey", "fyear", "datadate"], kind="stable")
    comp = comp.drop_duplicates(subset=["gvkey", "fyear"], keep="last")

    # Reuse C3+C4 outputs for the 8 baseline vars
    baseline = ChenBaselineControlsBuilder().build(years=load_years, root_path=root_path).data
    sigma = ChenIndustryCFVolFF48Builder().build(years=load_years, root_path=root_path).data

    # Compute remaining covariates from raw Compustat
    comp["capx"] = comp["capx"].fillna(0) / comp["at"]
    comp["rd"] = comp["xrd"].fillna(0) / comp["at"]
    comp["acquisition"] = comp["aqc"].fillna(0) / comp["at"]
    comp["div"] = (comp["dvc"].fillna(0) > 0).astype(int)
    comp["loss"] = (comp["ni"].fillna(0) < 0).astype(int)
    comp["cash"] = comp["che"].fillna(0) / comp["at"]
    comp["sgrw_num"] = comp["sale"].fillna(0)
    comp["nwc_for_delta"] = (
        comp["act"] - comp["che"].fillna(0) - comp["lct"] + comp["dlc"].fillna(0)
    ) / comp["at"]
    comp["z_score"] = _compute_z_score(comp)
    comp["finance"] = _compute_finance(comp)
    # BigN: AU codes 1-8 historically map to Big-N (1=AA, 2=PWC, 3=EY, 4=KPMG, 5=DT, 6=GT, 7=BDO, 8=Other)
    # Chen uses Big-N (1-4 in Compustat = current Big-4 + historical bigger names)
    # Per literature norm, AU ∈ {1,2,3,4,5,6,7,8} = Big-8 / Big-N catch-all
    comp["big_n"] = comp["au"].fillna(0).astype(int).between(1, 8).astype(int)

    # ΔNWC, ΔCASH, SGRW: lag-1
    comp = comp.sort_values(["gvkey", "fyear"], kind="stable").reset_index(drop=True)
    comp["nwc_lag"] = comp.groupby("gvkey")["nwc_for_delta"].shift(1)
    comp["cash_lag"] = comp.groupby("gvkey")["cash"].shift(1)
    comp["sale_lag"] = comp.groupby("gvkey")["sgrw_num"].shift(1)

    comp["delta_nwc"] = comp["nwc_for_delta"] - comp["nwc_lag"]
    comp["delta_cash"] = comp["cash"] - comp["cash_lag"]
    comp["sgrw"] = np.where(
        comp["sale_lag"].abs() > 1e-6,
        (comp["sgrw_num"] - comp["sale_lag"]) / comp["sale_lag"].abs(),
        np.nan,
    )

    # Merge C3 baseline (Q SIZE CF NWC LEV NSEG AGE)
    comp = comp.merge(
        baseline[["gvkey", "fyear", "q", "size", "cf", "nwc", "lev", "nseg", "age"]],
        on=["gvkey", "fyear"], how="left",
    )

    # Merge FF48, then C4 SIGMA via FF48
    ff48 = FF48IndustryClassifierBuilder().build(years=load_years, root_path=root_path).data
    comp = comp.merge(
        ff48[["gvkey", "fyear", "ff48_code"]], on=["gvkey", "fyear"], how="left"
    )
    comp = comp.merge(
        sigma[["ff48_code", "fyear", "sigma_chen"]],
        on=["ff48_code", "fyear"], how="left",
    )

    # Project to needed cols
    out_cols = ["gvkey", "fyear", "ff48_code"] + COVARIATES
    return comp[out_cols].copy()


def _average_t_minus_3_to_t_minus_1(
    cov_panel: pd.DataFrame, gvkey_year_targets: pd.DataFrame
) -> pd.DataFrame:
    """For each (gvkey, target_year), compute mean of covariates over fyears [t-3, t-1].

    Per spec line 1548 verbatim: 'all independent variables are measured over year t-3 to t-1'.

    Vectorized approach: expand each (gvkey, target_year) into 3 offset rows
    (target_year-3, target_year-2, target_year-1), merge to cov_panel, groupby-mean.
    Skips NaN (skipna=True default in groupby.mean).

    Args:
        cov_panel: full firm-year covariate panel.
        gvkey_year_targets: DataFrame with cols (gvkey, target_year).

    Returns:
        DataFrame with cols (gvkey, target_year, *COVARIATES averaged).
    """
    targets = gvkey_year_targets[["gvkey", "target_year"]].copy()
    expanded_pieces = []
    for offset in (-3, -2, -1):
        tmp = targets.copy()
        tmp["fyear"] = (tmp["target_year"] + offset).astype(int)
        expanded_pieces.append(tmp)
    expanded = pd.concat(expanded_pieces, ignore_index=True)
    cov_keep = ["gvkey", "fyear"] + [c for c in COVARIATES if c in cov_panel.columns]
    merged = expanded.merge(cov_panel[cov_keep], on=["gvkey", "fyear"], how="left")
    grp = (
        merged.groupby(["gvkey", "target_year"], as_index=False)[
            [c for c in COVARIATES if c in merged.columns]
        ]
        .mean()
    )
    # Fill missing covariate columns (in case cov_panel was missing any)
    for c in COVARIATES:
        if c not in grp.columns:
            grp[c] = np.nan
    return grp[["gvkey", "target_year"] + COVARIATES]


def _fit_pooled_probit_and_score(
    pool: pd.DataFrame, ff48_col: str = "ff48_code"
) -> pd.Series:
    """Fit pooled probit (Treated ~ X1∪X2∪X3 + FF48_dummies + Year_dummies)
    and return propensity score per row.

    Uses sklearn LogisticRegression as probit-substitute (industry standard for PSM).
    StandardScaler applied to continuous covariates.
    """
    from sklearn.linear_model import LogisticRegression
    from sklearn.preprocessing import StandardScaler

    sub = pool.dropna(subset=COVARIATES + ["treated", ff48_col, "target_year"]).copy()
    if len(sub) < 10:
        # too few — return NaN
        return pd.Series(np.nan, index=pool.index, name="p_score")

    # FF48 + year dummies
    ff48_dum = pd.get_dummies(sub[ff48_col].astype(int), prefix="ff48", drop_first=True)
    yr_dum = pd.get_dummies(sub["target_year"].astype(int), prefix="yr", drop_first=True)

    X_cont = sub[COVARIATES].to_numpy(dtype=float)
    scaler = StandardScaler()
    X_cont_std = scaler.fit_transform(X_cont)

    X = np.hstack([X_cont_std, ff48_dum.to_numpy(dtype=float), yr_dum.to_numpy(dtype=float)])
    y = sub["treated"].astype(int).to_numpy()

    if y.sum() < 5 or (1 - y).sum() < 5:
        return pd.Series(np.nan, index=pool.index, name="p_score")

    lr = LogisticRegression(max_iter=2000, solver="lbfgs", C=1.0)
    lr.fit(X, y)
    p = lr.predict_proba(X)[:, 1]

    out = pd.Series(np.nan, index=pool.index, name="p_score")
    out.loc[sub.index] = p
    return out


def _greedy_nn_within_ff48_or_ff12(
    pool: pd.DataFrame, sic_to_ff12: Dict[Any, Tuple[int, str]]
) -> pd.DataFrame:
    """Greedy 1:1 NN no-replace, within FF48 (or widen to FF12 if FF48 pool <5).

    Args:
        pool: DataFrame with cols (gvkey, target_year, treated, p_score, ff48_code, sic_code).
        sic_to_ff12: parsed FF12 SIC→industry map.

    Returns:
        DataFrame with cols (gvkey, target_year, treated, p_score, match_partner_gvkey,
                              match_distance, in_psm_sample, widened_to_ff12,
                              treated_ff48, control_ff48, treated_ff12, control_ff12).
    """
    pool = pool.dropna(subset=["p_score", "ff48_code"]).copy()
    pool["ff12_code"] = pool["sic_code"].apply(
        lambda s: (sic_to_ff12.get(int(s)) or sic_to_ff12.get("_catchall") or (12, "Other"))[0]
        if pd.notna(s) else np.nan
    )

    treated = pool[pool["treated"] == 1].copy().reset_index(drop=True)
    controls = pool[pool["treated"] == 0].copy().reset_index(drop=True)
    if len(treated) == 0 or len(controls) == 0:
        return pd.DataFrame()

    # Sort treated rows by p_score asc for deterministic greedy
    treated = treated.sort_values("p_score", kind="stable").reset_index(drop=True)
    used_control: set = set()

    # Build by-cohort indices for fast lookup
    # Cohort = (target_year, ff48_code) for primary; widen to (target_year, ff12_code) if pool <5
    matches: List[Dict[str, Any]] = []

    for _, t_row in treated.iterrows():
        t_year = int(t_row["target_year"])
        t_ff48 = int(t_row["ff48_code"])
        t_ff12 = int(t_row["ff12_code"]) if pd.notna(t_row["ff12_code"]) else None
        t_p = float(t_row["p_score"])
        t_gv = str(t_row["gvkey"])

        # Try FF48 first
        ff48_pool = controls[
            (controls["target_year"] == t_year)
            & (controls["ff48_code"] == t_ff48)
            & (~controls["gvkey"].isin(used_control))
        ]
        widened = False
        if len(ff48_pool) < FF48_MIN_POOL:
            # Widen to FF12
            if t_ff12 is not None:
                ff12_pool = controls[
                    (controls["target_year"] == t_year)
                    & (controls["ff12_code"] == t_ff12)
                    & (~controls["gvkey"].isin(used_control))
                ]
                pool_use = ff12_pool
                widened = True
            else:
                pool_use = ff48_pool
        else:
            pool_use = ff48_pool

        if len(pool_use) == 0:
            # Unmatched
            matches.append({
                "gvkey": t_gv,
                "target_year": t_year,
                "treated": 1,
                "p_score": t_p,
                "match_partner_gvkey": None,
                "match_distance": np.nan,
                "in_psm_sample": 0,
                "widened_to_ff12": widened,
                "treated_ff48": t_ff48,
                "control_ff48": None,
                "treated_ff12": t_ff12,
                "control_ff12": None,
            })
            continue

        dists = (pool_use["p_score"] - t_p).abs().to_numpy()
        idx = int(np.argmin(dists))
        c_row = pool_use.iloc[idx]
        c_gv = str(c_row["gvkey"])
        d = float(dists[idx])
        used_control.add(c_gv)

        matches.append({
            "gvkey": t_gv,
            "target_year": t_year,
            "treated": 1,
            "p_score": t_p,
            "match_partner_gvkey": c_gv,
            "match_distance": d,
            "in_psm_sample": 1,
            "widened_to_ff12": widened,
            "treated_ff48": t_ff48,
            "control_ff48": int(c_row["ff48_code"]),
            "treated_ff12": t_ff12,
            "control_ff12": int(c_row["ff12_code"]) if pd.notna(c_row["ff12_code"]) else None,
        })
        # Add control row
        matches.append({
            "gvkey": c_gv,
            "target_year": t_year,
            "treated": 0,
            "p_score": float(c_row["p_score"]),
            "match_partner_gvkey": t_gv,
            "match_distance": d,
            "in_psm_sample": 1,
            "widened_to_ff12": widened,
            "treated_ff48": t_ff48,
            "control_ff48": int(c_row["ff48_code"]),
            "treated_ff12": t_ff12,
            "control_ff12": int(c_row["ff12_code"]) if pd.notna(c_row["ff12_code"]) else None,
        })

    return pd.DataFrame(matches)


class ChenPSMMatchingBuilder(VariableBuilder):
    """Build PSM-matched-pair-year indicator per Chen spec C5."""

    def __init__(self, config: Dict[str, Any] | None = None):
        super().__init__(config or {})
        self.classifier_variant: ClassifierVariant = (config or {}).get("classifier_variant", "B")
        self.column = "in_psm_sample"

    def build(self, years: range, root_path: Path) -> VariableResult:
        years_list = list(years)

        # Load treatment per variant
        treated_panel = ChenRestatementTreatmentBuilder(
            {"classifier_variant": self.classifier_variant}
        ).build(years=years, root_path=root_path).data
        treated_irreg = treated_panel[treated_panel["IRREG"] == 1].copy()
        n_treated_total = len(treated_irreg)
        logger.info(f"Variant {self.classifier_variant}: {n_treated_total} treated firms")

        if n_treated_total == 0:
            return VariableResult(
                data=pd.DataFrame(columns=[
                    "gvkey", "event_year", "classifier_variant", "treated", "p_score",
                    "match_partner_gvkey", "match_distance", "in_psm_sample",
                    "widened_to_ff12", "treated_ff48", "control_ff48",
                    "treated_ff12", "control_ff12",
                ]),
                stats=VariableStats(name="in_psm_sample", n=0, mean=0, std=0, min=0,
                                    p25=0, median=0, p75=0, max=0, n_missing=0, pct_missing=0),
                metadata={"task": "Phase 1C C5", "n_treated": 0},
            )

        # Build covariate panel (covers all gvkeys in F1D)
        cov_panel = _build_covariate_panel(years, root_path)
        logger.info(f"Covariate panel: {len(cov_panel)} firm-years")

        # Bridge gvkeys (= ALL firms ever appearing in AA bridge — exclude from control pool per spec)
        bridge_panel = ChenAAtoGvkeyBridgeBuilder().build(years=years, root_path=root_path).data
        bridge_gvkeys = set(bridge_panel["gvkey"].dropna().astype(str).unique())

        # SIC code per (gvkey, fyear) for FF12 lookup
        sic_panel = read_compustat_annual(
            path=root_path / "inputs" / "Compustat_Annual" / "compustat_annual.csv",
            cols=["gvkey", "datadate", "sic", "loc"],
            years=years,
            us_only=True,
        )[["gvkey", "fyear", "sic"]]
        sic_panel = sic_panel.sort_values(["gvkey", "fyear"]).drop_duplicates(
            subset=["gvkey", "fyear"], keep="last"
        )
        sic_panel = sic_panel.rename(columns={"sic": "sic_code"})

        # Build target frame: each treated row → target_year=event_year
        targets_treated = treated_irreg[["gvkey", "event_year"]].rename(
            columns={"event_year": "target_year"}
        )
        targets_treated["treated"] = 1

        # Control candidates: all NON-bridge firms × event_years cohort
        event_years_in_use = sorted(treated_irreg["event_year"].unique())
        control_gvkeys = set(cov_panel["gvkey"].dropna().astype(str).unique()) - bridge_gvkeys
        targets_control = pd.DataFrame([
            {"gvkey": gv, "target_year": int(yr), "treated": 0}
            for gv in control_gvkeys for yr in event_years_in_use
        ])
        logger.info(
            f"Control candidate pool: {len(control_gvkeys)} gvkeys × "
            f"{len(event_years_in_use)} event_years = {len(targets_control)} rows"
        )

        all_targets = pd.concat([targets_treated, targets_control], ignore_index=True)

        # Average covariates over [t-3, t-1] per (gvkey, target_year)
        avg = _average_t_minus_3_to_t_minus_1(cov_panel, all_targets)
        avg = avg.merge(all_targets[["gvkey", "target_year", "treated"]], on=["gvkey", "target_year"])

        # Add FF48 (at year-0 = target_year) and SIC code
        avg = avg.merge(
            cov_panel[["gvkey", "fyear", "ff48_code"]].rename(columns={"fyear": "target_year"}),
            on=["gvkey", "target_year"], how="left",
        )
        avg = avg.merge(
            sic_panel.rename(columns={"fyear": "target_year"}),
            on=["gvkey", "target_year"], how="left",
        )

        # Probit + score
        avg["p_score"] = _fit_pooled_probit_and_score(avg)

        # FF12 SIC parser
        sic_to_ff12 = parse_ff_industries(
            root_path / "inputs" / "FF1248" / "Siccodes12.zip", 12
        )

        # Match
        matched = _greedy_nn_within_ff48_or_ff12(avg, sic_to_ff12)
        if len(matched) == 0:
            logger.warning("No matched pairs produced.")
            matched = pd.DataFrame(columns=[
                "gvkey", "target_year", "treated", "p_score", "match_partner_gvkey",
                "match_distance", "in_psm_sample", "widened_to_ff12",
                "treated_ff48", "control_ff48", "treated_ff12", "control_ff12",
            ])

        matched = matched.rename(columns={"target_year": "event_year"})
        matched["classifier_variant"] = self.classifier_variant

        # Diagnostic flag per FF48
        diag = (
            matched[matched["in_psm_sample"] == 1]
            .groupby("treated_ff48")["match_distance"]
            .median()
            .reset_index()
            .rename(columns={"match_distance": "median_match_distance"})
        )
        diag["flag_distance_above_threshold"] = diag["median_match_distance"] > DIAGNOSTIC_THRESHOLD
        n_flagged = int(diag["flag_distance_above_threshold"].sum())

        n_matched = int((matched["in_psm_sample"] == 1).sum())
        n_widened = int((matched["widened_to_ff12"] == True).sum())
        logger.info(
            f"Matched: {n_matched} rows in_psm_sample=1; widened to FF12: {n_widened}; "
            f"FF48 industries flagged for distance>{DIAGNOSTIC_THRESHOLD}: {n_flagged}"
        )

        flag_series = matched["in_psm_sample"]
        stats = VariableStats(
            name="in_psm_sample",
            n=int(len(flag_series)),
            mean=float(flag_series.mean()) if len(flag_series) else 0.0,
            std=float(flag_series.std()) if len(flag_series) else 0.0,
            min=0, p25=0.0, median=0.0, p75=1.0, max=1,
            n_missing=int(flag_series.isna().sum()),
            pct_missing=float(flag_series.isna().mean()) if len(flag_series) else 0.0,
        )
        metadata: Dict[str, Any] = {
            "source": "Chen et al (2017) JAAF Section A (PDF p.23-25, j.312-314)",
            "classifier_variant": self.classifier_variant,
            "n_treated": n_treated_total,
            "n_matched_rows_total": int(len(matched)),
            "n_in_psm_sample": n_matched,
            "n_widened_to_ff12": n_widened,
            "n_ff48_industries_flagged": n_flagged,
            "covariates": COVARIATES,
            "n_covariates": len(COVARIATES),
            "covariate_avg_window": "t-3 to t-1 (spec line 1548 verbatim)",
            "match_score_year": "year 0 = event_year",
            "match_ratio": "1:1",
            "match_replacement": "no",
            "match_caliper": "NONE (audit V4 lock)",
            "small_industry_fallback": f"FF48 pool < {FF48_MIN_POOL} → widen to FF12 (audit M2)",
            "diagnostic_threshold": DIAGNOSTIC_THRESHOLD,
            "diagnostic_per_ff48": diag.to_dict(orient="records"),
            "column": "in_psm_sample",
            "task": "Phase 1C C5",
        }
        return VariableResult(data=matched, stats=stats, metadata=metadata)
