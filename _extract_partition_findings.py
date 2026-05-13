"""Programmatic per-IV sig-pattern extraction. One-shot, throwaway.

Reads latest suite_spec_*.json for each suite, computes per-IV sig counts
split by contemp vs lead DV, beta range, sample size range. Writes CSV +
prints parent-vs-.r side-by-side comparison."""
import json
import glob
import os
from collections import defaultdict

ROOT = "outputs/econometric"
OUT_CSV = "_partition_findings.csv"


def load_latest_specs():
    specs = glob.glob(f"{ROOT}/*/2*/suite_spec_*.json")
    suite_files = defaultdict(list)
    for p in specs:
        parts = p.split(os.sep)
        suite_dir, ts, fname = parts[-3], parts[-2], parts[-1]
        suite_files[suite_dir].append((ts, p, fname))
    out = {}
    for suite_dir, lst in suite_files.items():
        # latest by ts; if multiple specs in same ts (dual-emit), keep all
        latest_ts = max(t[0] for t in lst)
        latest = [(p, f) for t, p, f in lst if t == latest_ts]
        out[suite_dir] = latest
    return out


def is_lead_col(dv: str, base_dvs_in_spec: list) -> bool:
    return "_lead" in dv


def sig_level(p):
    if p is None:
        return None
    if p < 0.01:
        return 3
    if p < 0.05:
        return 2
    if p < 0.10:
        return 1
    return 0


def analyze_spec(spec_path: str):
    with open(spec_path) as f:
        s = json.load(f)
    suite_id = s["suite_id"]
    ivs = [iv["name"] for iv in s.get("ivs", [])]
    cols = s.get("columns", [])
    if not ivs or not cols:
        return None
    # Determine contemp vs lead per col
    base_dvs = set()
    for c in cols:
        dv = c["dv"]
        if "_lead" not in dv:
            base_dvs.add(dv)
    rows = []
    n_obs_all = [c["n_obs"] for c in cols]
    for iv in ivs:
        contemp = {0: 0, 1: 0, 2: 0, 3: 0}
        lead = {0: 0, 1: 0, 2: 0, 3: 0}
        contemp_total = 0
        lead_total = 0
        betas = []
        ses = []
        for c in cols:
            coefs = c.get("coefs", {})
            if iv not in coefs:
                continue
            cd = coefs[iv]
            p = cd.get("p_one") if cd.get("p_one") is not None else cd.get("p_two")
            beta = cd.get("beta")
            se = cd.get("se")
            lvl = sig_level(p)
            is_lead = is_lead_col(c["dv"], base_dvs)
            if is_lead:
                lead_total += 1
                if lvl is not None and lvl > 0:
                    for L in range(1, lvl + 1):
                        lead[L] += 1
            else:
                contemp_total += 1
                if lvl is not None and lvl > 0:
                    for L in range(1, lvl + 1):
                        contemp[L] += 1
            if beta is not None:
                betas.append(beta)
            if se is not None:
                ses.append(se)
        rows.append({
            "suite_id": suite_id,
            "iv": iv,
            "contemp_total": contemp_total,
            "contemp_p10": contemp[1],
            "contemp_p05": contemp[2],
            "contemp_p01": contemp[3],
            "lead_total": lead_total,
            "lead_p10": lead[1],
            "lead_p05": lead[2],
            "lead_p01": lead[3],
            "beta_min": min(betas) if betas else None,
            "beta_max": max(betas) if betas else None,
            "beta_abs_max": max((abs(b) for b in betas), default=None),
            "se_med": sorted(ses)[len(ses)//2] if ses else None,
            "n_min": min(n_obs_all),
            "n_max": max(n_obs_all),
            "tail_dir": s.get("tail", {}).get("direction"),
            "model_family": s.get("model_family"),
        })
    return rows


def main():
    latest = load_latest_specs()
    all_rows = []
    for suite_dir, specs in sorted(latest.items()):
        for path, fname in specs:
            rows = analyze_spec(path)
            if rows:
                for r in rows:
                    r["dir"] = suite_dir
                    all_rows.append(r)

    # Write CSV
    cols = ["suite_id", "iv", "tail_dir", "model_family",
            "contemp_total", "contemp_p10", "contemp_p05", "contemp_p01",
            "lead_total", "lead_p10", "lead_p05", "lead_p01",
            "beta_min", "beta_max", "beta_abs_max", "se_med",
            "n_min", "n_max", "dir"]
    with open(OUT_CSV, "w") as f:
        f.write(",".join(cols) + "\n")
        for r in all_rows:
            f.write(",".join(str(r.get(c, "")) for c in cols) + "\n")
    print(f"Wrote {len(all_rows)} rows -> {OUT_CSV}")

    # Print parent-vs-.r side-by-side
    by_suite_id = defaultdict(list)
    for r in all_rows:
        by_suite_id[r["suite_id"]].append(r)

    print("\n" + "=" * 100)
    print("PARENT vs .r PARTITION COMPARISON (per IV: contemp_p10/p05/p01 | lead_p10/p05/p01)")
    print("=" * 100)
    parent_ids = sorted([sid for sid in by_suite_id if not sid.endswith(".r")])
    for parent in parent_ids:
        rid = parent + ".r"
        if rid not in by_suite_id:
            continue
        # Gather per-IV
        p_rows = {r["iv"]: r for r in by_suite_id[parent]}
        r_rows = {r["iv"]: r for r in by_suite_id[rid]}
        all_ivs = sorted(set(list(p_rows.keys()) + list(r_rows.keys())))
        print(f"\n--- {parent} -> {rid} (tail={p_rows[next(iter(p_rows))]['tail_dir']}, n_parent={p_rows[next(iter(p_rows))]['n_min']}-{p_rows[next(iter(p_rows))]['n_max']}, n_r={r_rows[next(iter(r_rows))]['n_min']}-{r_rows[next(iter(r_rows))]['n_max']}) ---")
        # Header
        print(f"  {'IV':<15s} | {'PARENT contemp/lead':<25s} | {'.r     contemp/lead':<25s}")
        for iv in all_ivs:
            pr = p_rows.get(iv)
            rr = r_rows.get(iv)
            p_str = f"{pr['contemp_p10']}/{pr['contemp_p05']}/{pr['contemp_p01']} of {pr['contemp_total']} | {pr['lead_p10']}/{pr['lead_p05']}/{pr['lead_p01']} of {pr['lead_total']}" if pr else "NOT IN PARENT"
            r_str = f"{rr['contemp_p10']}/{rr['contemp_p05']}/{rr['contemp_p01']} of {rr['contemp_total']} | {rr['lead_p10']}/{rr['lead_p05']}/{rr['lead_p01']} of {rr['lead_total']}" if rr else "NOT IN .r"
            print(f"  {iv:<15s} | {p_str:<40s} | {r_str:<40s}")


if __name__ == "__main__":
    main()
