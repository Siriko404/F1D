import pandas as pd
b = pd.read_parquet("outputs/campello_v2/20260526_211240/beta_uk.parquet")
print(f"N firms: {len(b):,}")
print(b["beta_uk"].describe().to_string())
pos = b[b["beta_uk"] >= 0]["beta_uk"]
print(f"\nPositive-beta firms: {len(pos):,}")
t1 = pos.quantile(1/3)
t2 = pos.quantile(2/3)
print(f"Tercile cutoffs (nonneg): t1={t1:.3f}, t2={t2:.3f}")
print(f"Treated (b>t2):  {(b['beta_uk']>t2).sum():,}")
print(f"Control (0<=b<t1): {((b['beta_uk']>=0) & (b['beta_uk']<t1)).sum():,}")
print(f"Negative beta: {(b['beta_uk']<0).sum():,}")
print(f"\nPaper benchmark: treated b>0.68 = 449 firms, control b<0.28 = 360 firms")
