"""CLI wrapper: BrexitPSMMatchingBuilder + persist to outputs/variables/."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.brexit_psm_matching import BrexitPSMMatchingBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("outputs/variables/brexit_psm_matching"))
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    builder = BrexitPSMMatchingBuilder()
    result = builder.build(years=range(2010, 2017), root_path=args.root)
    runtime = time.time() - t0

    parquet_path = out_dir / "psm_matched_per_firm.parquet"
    result.data.to_parquet(parquet_path, index=False)
    manifest = {
        "builder": "BrexitPSMMatchingBuilder",
        "timestamp": ts,
        "runtime_seconds": round(runtime, 2),
        "rows": int(len(result.data)),
        **result.metadata,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] BrexitPSMMatchingBuilder complete in {runtime:.2f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     n_total_rows: {manifest['n_total_rows']:,}")
    print(f"     n_matched: {manifest['n_matched_rows']:,}")
    for d in manifest["diagnostics_per_treatment"]:
        print(f"     {d['label']:10s} treated={d['n_treated']:>4d}, control={d['n_control']:>4d}, "
              f"matched_pairs={d['n_matched_pairs']:>4d}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
