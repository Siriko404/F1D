"""Phase A3 — Cross-source dedup with tier system.

Reads q{1,2A,2B,3,4}_panel_filtered.parquet, normalizes exec-name + event-date
across sources, clusters within (gvkey) by fuzzy-name + date proximity, assigns
tier based on source-count + Q2-B corroboration, picks canonical death-date per
priority Q3 > Q1 > Q2-A > Q4. Writes cross_source_candidates.parquet (one row
per cluster) + dedup_summary.json + low-score-matches.csv for collision audit.

Locked design (per plan + advisor):
  - Match key: (gvkey, exec-name fuzzy WRatio >= 88, date proximity <= 90 days)
  - Tier 4: ≥3 of {Q1,Q2A,Q3,Q4}
  - Tier 3: 2 of {Q1,Q2A,Q3,Q4}
  - Tier 2: 1 of {Q1,Q2A,Q3,Q4} + Q2-B corroborates
  - Tier 1: 1 of {Q1,Q2A,Q3,Q4} alone
  - Q2-B-only events EXCLUDED
  - Tier 1 INCLUDED in Phase B manual screen (advisor: power gate binding)
  - Canonical date priority: Q3 dod > Q1 announce > Q2-A eff_date > Q4 leftofc
  - Post-run: inspect 10 lowest-fuzzy successful matches for collision audit

Usage:
    PYTHONIOENCODING=utf-8 python scripts/adhoc/dedup_ceo_deaths_a3.py
"""

from __future__ import annotations
import json
import re
from pathlib import Path
import numpy as np
import pandas as pd
from rapidfuzz import fuzz

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data" / "raw" / "ceo_death_events"

FUZZY_THRESHOLD = 88
DATE_WINDOW_DAYS = 90

DATE_PRIORITY = ["Q3", "Q1", "Q2A", "Q4"]


# ----- Q1 headline name parser -----

# Multi-pattern: try post-"Death of" first, then pre-"died/passed away" fallback,
# then "<Title>, <NAME>" with comma separator.
# Captures up to 4 capitalized tokens, allowing optional middle initials & apostrophes.

NAME_TOKEN = r"[A-Z][\w'\.\-]{0,}"  # capitalized incl dotted initials like "W.B." or "C." or "O'Meara"
NAME_CHAIN_RE = re.compile(rf"{NAME_TOKEN}(?:\s+{NAME_TOKEN}){{1,3}}")
DIED_RE = re.compile(r"\b(died|passed\s+away|passed\s+on|has\s+passed|passes\s+away)\b", re.IGNORECASE)
DEATH_OF_RE = re.compile(r"(?:death|passing|loss)\s+of\b", re.IGNORECASE)
COMMA_BEFORE_DIED_RE = re.compile(r",\s*([^,]+?)(?:\s+(?:died|passed))", re.IGNORECASE)

TITLE_TOKENS = {
    "ceo", "cfo", "coo", "cto", "cio", "evp", "svp", "vp", "chairman", "chair",
    "president", "founder", "director", "officer", "executive", "chief", "head",
    "and", "the", "of", "its", "former", "co-founder", "cofounder", "co",
    "board", "member", "leader", "co-leader", "vice", "senior", "lead",
    "non-executive", "operations", "general", "manager", "emeritus", "long-term",
    "long", "term", "as", "by", "at", "for", "with", "to", "from",
    "mr", "mrs", "ms", "dr", "sir", "lord", "hon", "doctor",
    "ag", "inc", "corp", "company", "co", "group", "ltd", "llc",
}


def _clean_captured(name: str) -> str | None:
    parts_raw = re.split(r"\s+", name.strip(",.; ").strip())
    parts = []
    for p in parts_raw:
        bare = p.lower().strip(".,'")
        if bare in TITLE_TOKENS:
            continue
        parts.append(p)
    if len(parts) < 2:
        return None
    return " ".join(parts).upper()


def parse_q1_name(headline: str, companyname: str = "") -> str | None:
    """Multi-strategy parse. Returns normalized UPPERCASE name or None."""
    if not isinstance(headline, str):
        return None
    text = headline.strip()
    company_tokens = set()
    if isinstance(companyname, str) and companyname:
        for t in re.split(r"[\s,&\.\-/]+", companyname.upper()):
            if t and t.lower() not in TITLE_TOKENS:
                company_tokens.add(t)

    def chain_is_company(chain_str: str) -> bool:
        # If 50%+ of chain tokens are company tokens, reject
        toks = [t.upper().strip(",.") for t in chain_str.split()]
        if not toks:
            return True
        hits = sum(1 for t in toks if t in company_tokens)
        return hits >= max(1, len(toks) // 2 + 1)

    # Strategy A: "Death|Passing|Loss of ..." — scan candidates AFTER this anchor
    m_death = DEATH_OF_RE.search(text)
    if m_death:
        sub = text[m_death.end():]
        for cm in NAME_CHAIN_RE.finditer(sub):
            cand_raw = cm.group(0)
            if chain_is_company(cand_raw):
                continue
            cand = _clean_captured(cand_raw)
            if cand:
                return cand

    # Strategy B: "X ... died/passed" — find LAST valid name chain before the verb
    m_died = DIED_RE.search(text)
    if m_died:
        pre = text[:m_died.start()]
        # Try in reverse order — last chain closest to verb wins
        all_chains = list(NAME_CHAIN_RE.finditer(pre))
        for cm in reversed(all_chains):
            cand_raw = cm.group(0)
            if chain_is_company(cand_raw):
                continue
            cand = _clean_captured(cand_raw)
            if cand:
                return cand

    return None


def normalize_name(s) -> str:
    if not isinstance(s, str):
        return ""
    s = s.upper().strip()
    s = re.sub(r"[\.,]", "", s)
    s = re.sub(r"\s+", " ", s)
    s = re.sub(r"\b(JR|SR|II|III|IV|V|MR|MS|MRS|DR)\b", "", s).strip()
    return s


# ----- Per-source standardization -----

def std_q1(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["source"] = "Q1"
    df["exec_name_raw"] = df.apply(
        lambda r: parse_q1_name(r["headline"], r.get("companyname", "")), axis=1
    )
    df["exec_name"] = df["exec_name_raw"].apply(normalize_name)
    df["event_date"] = pd.to_datetime(df["announcedate_dt"], errors="coerce")
    df["source_event_id"] = df["keydevid"].astype(str)
    return df[["source", "gvkey", "exec_name", "event_date", "source_event_id", "headline"]].rename(
        columns={"headline": "src_detail"}
    )


def std_q2(df: pd.DataFrame, label: str) -> pd.DataFrame:
    df = df.copy()
    df["source"] = label
    parts = (
        df["first_name"].fillna("").astype(str) + " " +
        df["middle_name"].fillna("").astype(str) + " " +
        df["last_name"].fillna("").astype(str)
    )
    df["exec_name_raw"] = parts.str.strip().str.replace(r"\s+", " ", regex=True)
    df["exec_name"] = df["exec_name_raw"].apply(normalize_name)
    df["event_date"] = pd.to_datetime(df["eff_date_dt"], errors="coerce")
    df["source_event_id"] = df["company_fkey"].astype(str) + "|" + df["eff_date"].astype(str)
    df["src_detail"] = df["title_report"].fillna("").astype(str) + " | action=" + df["action"].fillna("").astype(str)
    return df[["source", "gvkey", "exec_name", "event_date", "source_event_id", "src_detail"]]


def std_q3(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["source"] = "Q3"
    df["exec_name"] = df["directorname"].apply(normalize_name)
    df["event_date"] = pd.to_datetime(df["dod_date_dt"], errors="coerce")
    df["source_event_id"] = df["directorid"].astype(str) + "|" + df["companyid"].astype(str)
    df["src_detail"] = df["rolename"].fillna("").astype(str) + " | " + df["companyname"].fillna("").astype(str)
    return df[["source", "gvkey", "exec_name", "event_date", "source_event_id", "src_detail"]]


def std_q4(df: pd.DataFrame) -> pd.DataFrame:
    """ExecuComp has multi-year rows per exec; collapse to one per (gvkey, execid)."""
    df = df.copy()
    df["source"] = "Q4"
    df["exec_name"] = df["exec_fullname"].apply(normalize_name)
    df["event_date"] = pd.to_datetime(df["death_date_proxy"], errors="coerce")
    df["source_event_id"] = df["execid"].astype(str)
    df["src_detail"] = "reason=" + df["reason"].fillna("").astype(str) + " | ceoann=" + df["ceoann"].fillna("").astype(str)
    out = df[["source", "gvkey", "exec_name", "event_date", "source_event_id", "src_detail"]].drop_duplicates(
        subset=["gvkey", "source_event_id"], keep="first"
    )
    return out


# ----- Clustering within gvkey -----

def cluster_gvkey(events: pd.DataFrame) -> pd.DataFrame:
    """Greedy clustering: for each event in priority order, attach to existing cluster if name+date match.

    Returns events with a 'cluster_id' column (0-indexed within gvkey).
    """
    events = events.reset_index(drop=True).copy()
    n = len(events)
    cluster_id = [-1] * n
    next_id = 0
    for i in range(n):
        if cluster_id[i] != -1:
            continue
        cluster_id[i] = next_id
        for j in range(i + 1, n):
            if cluster_id[j] != -1:
                continue
            ni, dj = events.at[i, "exec_name"], events.at[j, "exec_name"]
            di_d, dj_d = events.at[i, "event_date"], events.at[j, "event_date"]
            if not ni or not dj:
                continue
            score = fuzz.WRatio(ni, dj) if (ni and dj) else 0
            if score < FUZZY_THRESHOLD:
                continue
            if pd.isna(di_d) or pd.isna(dj_d):
                continue
            if abs((di_d - dj_d).days) > DATE_WINDOW_DAYS:
                continue
            cluster_id[j] = next_id
        next_id += 1
    events["cluster_id"] = cluster_id
    return events


def assemble_cluster(events_in_cluster: pd.DataFrame, q2b_pool_for_gvkey: pd.DataFrame) -> dict:
    """Build one output row from a cluster of primary events. Determines tier + canonical date."""
    sources = sorted(events_in_cluster["source"].unique().tolist())
    primary_sources = [s for s in sources if s in {"Q1", "Q2A", "Q3", "Q4"}]
    source_count = len(primary_sources)

    # Canonical date by priority
    canonical_date = pd.NaT
    canonical_date_source = None
    for pri in DATE_PRIORITY:
        sub = events_in_cluster[events_in_cluster["source"] == pri]
        if len(sub) > 0 and sub["event_date"].notna().any():
            canonical_date = sub["event_date"].dropna().iloc[0]
            canonical_date_source = pri
            break

    # Canonical name: pick longest non-empty name in cluster
    names = events_in_cluster.loc[events_in_cluster["exec_name"].astype(bool), "exec_name"].tolist()
    canonical_name = max(names, key=len) if names else ""

    # Q2-B corroboration: any Q2-B event for same gvkey with fuzzy>=88 to canonical_name + within ±90d of canonical_date
    q2b_match = False
    q2b_evidence = None
    if len(q2b_pool_for_gvkey) > 0 and canonical_name and pd.notna(canonical_date):
        for _, r in q2b_pool_for_gvkey.iterrows():
            if not r["exec_name"]:
                continue
            score = fuzz.WRatio(canonical_name, r["exec_name"])
            if score < FUZZY_THRESHOLD:
                continue
            if pd.isna(r["event_date"]):
                continue
            if abs((r["event_date"] - canonical_date).days) > DATE_WINDOW_DAYS:
                continue
            q2b_match = True
            q2b_evidence = r["src_detail"]
            break

    # Tier
    if source_count >= 3:
        tier = 4
    elif source_count == 2:
        tier = 3
    elif source_count == 1 and q2b_match:
        tier = 2
    elif source_count == 1:
        tier = 1
    else:
        tier = 0  # shouldn't happen for primary cluster

    # Source-specific evidence (kept for manual screen)
    by_src = {}
    for src in ["Q1", "Q2A", "Q3", "Q4"]:
        sub = events_in_cluster[events_in_cluster["source"] == src]
        if len(sub) > 0:
            by_src[f"{src}_event_id"] = "; ".join(sub["source_event_id"].astype(str).tolist())
            by_src[f"{src}_detail"] = "; ".join(sub["src_detail"].astype(str).tolist()[:1])  # truncate
            by_src[f"{src}_date"] = sub["event_date"].dropna().min() if sub["event_date"].notna().any() else pd.NaT

    return {
        "gvkey": events_in_cluster["gvkey"].iloc[0],
        "exec_name_canonical": canonical_name,
        "death_date_canonical": canonical_date,
        "death_date_source": canonical_date_source,
        "tier": tier,
        "source_count": source_count,
        "sources_matched": "+".join(primary_sources),
        "q2b_corroborates": q2b_match,
        "q2b_evidence": q2b_evidence,
        **by_src,
    }


# ----- Driver -----

def main():
    print("Loading panel-filtered sources...")
    q1 = std_q1(pd.read_parquet(DATA_DIR / "q1_panel_filtered.parquet"))
    q2a = std_q2(pd.read_parquet(DATA_DIR / "q2A_panel_filtered.parquet"), "Q2A")
    q2b = std_q2(pd.read_parquet(DATA_DIR / "q2B_panel_filtered.parquet"), "Q2B")
    q3 = std_q3(pd.read_parquet(DATA_DIR / "q3_panel_filtered.parquet"))
    q4 = std_q4(pd.read_parquet(DATA_DIR / "q4_panel_filtered.parquet"))

    # Q1 parse-failure diagnostic
    q1_parse_fail = q1["exec_name"].isna() | (q1["exec_name"] == "")
    print(f"Q1 events: {len(q1)}, name-parse failures: {q1_parse_fail.sum()}")
    # Drop Q1 events with no parsed name (cannot cross-match)
    q1 = q1[~q1_parse_fail].copy()

    primary = pd.concat([q1, q2a, q3, q4], ignore_index=True)
    print(f"Primary events (Q1+Q2A+Q3+Q4) total: {len(primary)}")
    print(f"Q2B confirm pool: {len(q2b)}")

    # Cluster within each gvkey
    print("\nClustering within-gvkey...")
    clusters = []
    low_score_audit = []
    for gvkey, grp in primary.groupby("gvkey"):
        clustered = cluster_gvkey(grp)
        # capture lowest-score successful in-cluster matches for audit
        for cid, sub in clustered.groupby("cluster_id"):
            if len(sub) > 1:
                names = sub["exec_name"].tolist()
                for i in range(len(names)):
                    for j in range(i + 1, len(names)):
                        s = fuzz.WRatio(names[i], names[j])
                        low_score_audit.append({
                            "gvkey": gvkey,
                            "name_a": names[i],
                            "name_b": names[j],
                            "score": s,
                            "source_a": sub["source"].iloc[i],
                            "source_b": sub["source"].iloc[j],
                        })
        q2b_pool = q2b[q2b["gvkey"] == gvkey]
        for cid, sub in clustered.groupby("cluster_id"):
            row = assemble_cluster(sub, q2b_pool)
            clusters.append(row)

    out = pd.DataFrame(clusters)
    print(f"\nTotal clusters (primary candidates): {len(out)}")
    print("\nTier distribution:")
    print(out["tier"].value_counts().sort_index())

    out_path = DATA_DIR / "cross_source_candidates.parquet"
    out.to_parquet(out_path, index=False)
    print(f"\nWrote: {out_path}")

    # Low-score audit (advisor blind spot #1)
    if low_score_audit:
        audit_df = pd.DataFrame(low_score_audit).sort_values("score").head(20)
        audit_path = DATA_DIR / "a3_low_score_matches_audit.csv"
        audit_df.to_csv(audit_path, index=False)
        print(f"\nLow-score matches (for collision audit, lowest 20):")
        print(audit_df.to_string())
        print(f"Wrote: {audit_path}")

    # Summary
    summary = {
        "primary_input_count": int(len(primary)),
        "q2b_pool_count": int(len(q2b)),
        "q1_parse_failures": int(q1_parse_fail.sum()),
        "total_clusters": int(len(out)),
        "tier_counts": {int(k): int(v) for k, v in out["tier"].value_counts().sort_index().items()},
        "fuzzy_threshold": FUZZY_THRESHOLD,
        "date_window_days": DATE_WINDOW_DAYS,
        "date_priority": DATE_PRIORITY,
    }
    with open(DATA_DIR / "dedup_summary.json", "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, default=str)
    print(f"\nWrote: {DATA_DIR / 'dedup_summary.json'}")


if __name__ == "__main__":
    main()
