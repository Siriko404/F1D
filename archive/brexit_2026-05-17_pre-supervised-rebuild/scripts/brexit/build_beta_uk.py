"""CLI wrapper: run BrexitBetaUKBuilder + persist output to outputs/variables/.

Usage:
    python -m scripts.brexit.build_beta_uk
        [--root <path>] [--out outputs/variables/brexit_treatment_beta_uk]

Output written to ``<out>/<YYYY-MM-DD_HHMMSS>/`` containing:
    - beta_uk_per_firm.parquet (gvkey, beta_uk, beta_se, n_obs, HIGH_BETA_UK)
    - run_manifest.json (estimation window, breakpoints, n_treated/n_control, runtime)
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

# Allow running as script or module.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.brexit_treatment_beta_uk import BrexitBetaUKBuilder


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Project root")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/variables/brexit_treatment_beta_uk"),
        help="Output base dir (timestamp subdir created automatically)",
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    builder = BrexitBetaUKBuilder()
    result = builder.build(years=range(2010, 2015), root_path=args.root)
    runtime = time.time() - t0

    parquet_path = out_dir / "beta_uk_per_firm.parquet"
    result.data.to_parquet(parquet_path, index=False)

    manifest = {
        "builder": "BrexitBetaUKBuilder",
        "timestamp": ts,
        "runtime_seconds": round(runtime, 2),
        "rows": int(len(result.data)),
        "output_parquet": str(parquet_path.relative_to(args.root)),
        **result.metadata,
    }
    manifest_path = out_dir / "run_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] BrexitBetaUKBuilder complete in {runtime:.1f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     manifest: {manifest_path}")
    print(f"     n_rows: {len(result.data):,}")
    print(f"     n_treated (HIGH_BETA_UK=1): {(result.data['HIGH_BETA_UK']==1).sum():,}")
    print(f"     n_control (HIGH_BETA_UK=0): {(result.data['HIGH_BETA_UK']==0).sum():,}")
    bp = result.metadata.get("tercile_breakpoints", {}) or {}
    mode = bp.get("mode", "unknown")
    print(f"     classifier mode: {mode}")
    if mode == "top_n_match":
        print(f"     top threshold β^UK   ≥ {bp.get('top_threshold_beta_uk', float('nan')):.4f}")
        print(f"     bottom threshold β^UK ≤ {bp.get('bottom_threshold_beta_uk', float('nan')):.4f}")
        print(f"     nonneg pool: {bp.get('n_nonneg', 0):,}; negatives dropped: {bp.get('n_negative_dropped', 0):,}")
    else:
        p33 = bp.get("p33_used", bp.get("p33_nonneg", float("nan")))
        p67 = bp.get("p67_used", bp.get("p67_nonneg", float("nan")))
        print(f"     tercile breakpoints: p33={p33:.4f}, p67={p67:.4f}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
