"""CLI wrapper: run Brexit10KTreatmentBuilder + persist to outputs/variables/.

Reads the latest cache produced by ``parse_10k_keywords.py`` and writes the
HIGH_10K treatment dummy to ``outputs/variables/brexit_treatment_10k/<ts>/``.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.brexit_treatment_10k import Brexit10KTreatmentBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("outputs/variables/brexit_treatment_10k"),
    )
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    builder = Brexit10KTreatmentBuilder()
    result = builder.build(years=range(2010, 2017), root_path=args.root)
    runtime = time.time() - t0

    parquet_path = out_dir / "treatment_10k_per_firm.parquet"
    result.data.to_parquet(parquet_path, index=False)

    manifest = {
        "builder": "Brexit10KTreatmentBuilder",
        "timestamp": ts,
        "runtime_seconds": round(runtime, 3),
        "rows": int(len(result.data)),
        "output_parquet": str(parquet_path.relative_to(args.root)),
        **result.metadata,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] Brexit10KTreatmentBuilder complete in {runtime:.2f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     n_treated (HIGH_10K=1): {manifest['n_treated_high_10k']:,}")
    print(f"     n_control (HIGH_10K=0): {manifest['n_control_zero_10k']:,}")
    print(f"     n_intermediate dropped (1-5): {manifest['n_intermediate_dropped']:,}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
