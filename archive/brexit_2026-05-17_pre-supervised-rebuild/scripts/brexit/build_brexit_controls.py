"""CLI wrapper: run all 4 Brexit-verbatim firm-control builders and persist outputs.

Per ~/.claude/plans/tender-popping-origami.md modules #7-#10 (Brexit-verbatim
controls per audit MAJOR-3). One Compustat read serves all 4 builders for
efficiency, but each writes its own timestamped output directory matching
F1D's get_latest_output_dir() convention.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import List, Tuple

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from f1d.shared.variables.base import VariableResult
from f1d.shared.variables.brexit_tobins_q import BrexitTobinsQBuilder
from f1d.shared.variables.brexit_sales_growth import BrexitSalesGrowthBuilder
from f1d.shared.variables.brexit_stock_return import BrexitStockReturnBuilder
from f1d.shared.variables.brexit_cash_flow import BrexitCashFlowBuilder


def _run_builder(name: str, builder, root: Path, out_base: Path, ts: str) -> Tuple[str, float, int]:
    out_dir = out_base / name / ts
    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    result: VariableResult = builder.build(years=range(2010, 2017), root_path=root)
    dt = time.time() - t0
    parquet_path = out_dir / f"{name}.parquet"
    result.data.to_parquet(parquet_path, index=False)
    manifest = {
        "builder": type(builder).__name__,
        "timestamp": ts,
        "runtime_seconds": round(dt, 2),
        "rows": int(len(result.data)),
        **result.metadata,
    }
    (out_dir / "run_manifest.json").write_text(json.dumps(manifest, indent=2, default=str))
    return name, dt, len(result.data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--out-base", type=Path, default=Path("outputs/variables"))
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(message)s")

    ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    builders = [
        ("brexit_tobins_q", BrexitTobinsQBuilder()),
        ("brexit_sales_growth", BrexitSalesGrowthBuilder()),
        ("brexit_stock_return", BrexitStockReturnBuilder()),
        ("brexit_cash_flow", BrexitCashFlowBuilder()),
    ]
    summary: List[Tuple[str, float, int]] = []
    for name, b in builders:
        print(f"\n=== {name} ===")
        summary.append(_run_builder(name, b, args.root, args.out_base, ts))

    print("\n" + "="*60)
    print("4 Brexit-verbatim controls — summary")
    for name, dt, n in summary:
        print(f"  {name:25s} {dt:>5.1f}s  {n:,} rows")
    print(f"  {'TOTAL':25s} {sum(s[1] for s in summary):>5.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
