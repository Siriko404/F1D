"""Audit v7 body prose numerical claims against suite_spec_*.json outputs.

For each thesis suite cited in body, extract per-IV sig counts at p<0.10 one-tailed,
n_obs / n_firms ranges, and report against body-prose claims.
"""
import json
from pathlib import Path
from collections import defaultdict

ROOT = Path(__file__).resolve().parents[2]
ECONO = ROOT / "outputs" / "econometric"

SUITES = {
    "H1.ceo2.decomp": "h1_cash_holdings_ceo2iv_decomp",
    "H1.ceo2.decomp.qtrexp": "h1_cash_holdings_ceo2iv_decomp_qtrexp",
    "H1.2.ceo2.decomp": "h1_2_cash_constraint_ceo2iv_decomp",
    "H1.2.ceo2.decomp.qtrexp": "h1_2_cash_constraint_ceo2iv_decomp_qtrexp",
    "H1.3.cfvol": "h1_3_cfvol_moderation",
    "H14c.spread.ceo2.decomp": "h14c_spread_bgt_level_ceo2iv_decomp",
    "H18.ceo2.decomp": "h18_cccl_received_ceo2iv_decomp",
}


def latest_spec(dirname: str) -> Path | None:
    d = ECONO / dirname
    if not d.exists():
        return None
    cands = sorted(d.glob("*/suite_spec_*.json"))
    return cands[-1] if cands else None


def summarize(spec_path: Path) -> dict:
    spec = json.loads(spec_path.read_text(encoding="utf-8"))
    cols = spec.get("columns", [])
    out = {
        "suite_id": spec.get("suite_id"),
        "title": spec.get("title"),
        "n_cols": len(cols),
        "spec_path": str(spec_path.relative_to(ROOT)),
        "iv_sig_counts": defaultdict(lambda: {"sig_p10": 0, "total": 0, "sig_cols": []}),
        "n_obs_range": [],
        "n_firms_range": [],
    }
    ivs_raw = spec.get("ivs", [])
    iv_names = {iv["name"] if isinstance(iv, dict) else iv for iv in ivs_raw}
    for col in cols:
        out["n_obs_range"].append(col.get("n_obs"))
        out["n_firms_range"].append(col.get("n_firms"))
        for k, v in col.get("coefs", {}).items():
            if k in iv_names or "_x_" in k or "Unrated" in k or "HighCFvol" in k:
                p_one = v.get("p_one")
                if p_one is not None:
                    out["iv_sig_counts"][k]["total"] += 1
                    if p_one < 0.10:
                        out["iv_sig_counts"][k]["sig_p10"] += 1
                        out["iv_sig_counts"][k]["sig_cols"].append(col.get("col"))
    if out["n_obs_range"]:
        out["n_obs_min"] = min(out["n_obs_range"])
        out["n_obs_max"] = max(out["n_obs_range"])
    if out["n_firms_range"]:
        out["n_firms_min"] = min(out["n_firms_range"])
        out["n_firms_max"] = max(out["n_firms_range"])
    return out


def main():
    print("=" * 80)
    print("v7 BODY NUMBERS AUDIT — programmatic extraction from latest suite_spec.json")
    print("=" * 80)
    for suite_id, dirname in SUITES.items():
        sp = latest_spec(dirname)
        if not sp:
            print(f"\n[NOT FOUND] {suite_id} ({dirname})")
            continue
        s = summarize(sp)
        print(f"\n--- {suite_id} ({dirname}) ---")
        print(f"  spec: {s['spec_path']}")
        print(f"  title: {s['title']}")
        print(f"  n_cols: {s['n_cols']}")
        print(f"  n_obs: min={s.get('n_obs_min')} max={s.get('n_obs_max')}")
        print(f"  n_firms: min={s.get('n_firms_min')} max={s.get('n_firms_max')}")
        print(f"  IV sig counts (p_one < 0.10):")
        for iv, c in s["iv_sig_counts"].items():
            print(f"    {iv}: {c['sig_p10']}/{c['total']}  cols: {c['sig_cols']}")


if __name__ == "__main__":
    main()
