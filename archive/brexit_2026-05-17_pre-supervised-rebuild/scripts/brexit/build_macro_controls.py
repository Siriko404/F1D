"""CLI wrapper: run BrexitMacroControlsBuilder + persist to outputs/variables/."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.brexit_macro_controls import BrexitMacroControlsBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("outputs/variables/brexit_macro"))
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    builder = BrexitMacroControlsBuilder()
    result = builder.build(years=range(2010, 2017), root_path=args.root)
    runtime = time.time() - t0

    parquet_path = out_dir / "brexit_macro_quarterly.parquet"
    result.data.to_parquet(parquet_path, index=False)
    manifest = {
        "builder": "BrexitMacroControlsBuilder",
        "timestamp": ts,
        "runtime_seconds": round(runtime, 3),
        "rows": int(len(result.data)),
        "output_parquet": str(parquet_path.relative_to(args.root)),
        **result.metadata,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] BrexitMacroControlsBuilder complete in {runtime:.2f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     rows: {len(result.data)} (expect 28)")
    print(f"     NaN counts: {manifest['n_nan_per_column']}")
    print(result.data.to_string(index=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
