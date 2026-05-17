"""CLI wrapper: BrexitConsensusEPSBuilder + persist to outputs/variables/."""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.brexit_consensus_eps import BrexitConsensusEPSBuilder


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out", type=Path, default=Path("outputs/variables/brexit_consensus_eps"))
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    out_dir = args.out / ts
    out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    builder = BrexitConsensusEPSBuilder()
    result = builder.build(years=range(2010, 2017), root_path=args.root)
    runtime = time.time() - t0

    parquet_path = out_dir / "consensus_eps_per_firm_quarter.parquet"
    result.data.to_parquet(parquet_path, index=False)
    manifest = {
        "builder": "BrexitConsensusEPSBuilder",
        "timestamp": ts,
        "runtime_seconds": round(runtime, 2),
        "rows": int(len(result.data)),
        **result.metadata,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))

    print(f"\n[OK] BrexitConsensusEPSBuilder complete in {runtime:.1f}s")
    print(f"     parquet: {parquet_path}")
    print(f"     rows: {manifest['rows']:,}")
    print(f"     unique gvkeys: {manifest['n_unique_gvkeys_brexit']:,}")
    print(f"     z-score distribution:")
    print(result.data['consensus_eps_z'].describe())
    return 0


if __name__ == "__main__":
    sys.exit(main())
