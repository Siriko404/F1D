"""Continuous validation + keystone test, EXACT thesis spec (G.build + G.run = empire_building_did).

VALIDATION: cash UncResCEO must reproduce ~ +0.0461*** (the published run-up) -> proves harness correct.
KEYSTONE  : UncPreCEO (scripted presentation tone), cash vs stock arms.
            masking framing predicts STOCK UncPreCEO NEGATIVE (scripted tone managed down).

Run from F1D: python <path>/test_masking_continuous.py
"""
import glob, sys, warnings
from pathlib import Path
import pandas as pd
warnings.filterwarnings("ignore")

ROOT = Path(".").resolve(); sys.path.insert(0, str(ROOT / "scripts"))
import gen_empire_did_table as G


def latest(pat):
    h = sorted(glob.glob(str(ROOT / pat)))
    return h[-1] if h else None


p, s, m = G.base_panel(), G.sdc(), G.manifest()
upf = latest("outputs/variables/ceo_clarity_extended/*/ceo_clarity_extended_panel.parquet")
up = pd.read_parquet(upf, columns=["file_name", "UncPreCEO"]).drop_duplicates("file_name")
p = p.merge(up, on="file_name", how="left")

print(f"{'arm':6}{'DV':12}{'beta':>11}{'se':>10}{'p2':>9}   N / firms")
print("-" * 70)
for arm, mask in {"cash": s["pc"] >= 50, "stock": s["ps"] >= 50}.items():
    q, n = G.build(p, s, m, mask)
    for dv in ["UncResCEO", "UncPreCEO"]:
        r = G.run(q, dv)
        print(f"{arm:6}{dv:12}{r['beta']:+.4f}{'':>3}{r['se']:.4f}{'':>3}{r['p2']:.4f}{'':>2}"
              f"{G.stars(r['p2']):<3} {r['n']:,}/{r['n_firms']:,}")
print("-" * 70)
print("Validation: cash UncResCEO ~ +0.0461*** = harness OK.")
print("Keystone:  STOCK UncPreCEO < 0 (sig) would confirm scripted-tone management.")
