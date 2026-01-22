import pandas as pd

# 1. Check Unified-info
try:
    u = pd.read_parquet(r'c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/Unified-info.parquet')
    print(f"Unified GVKEY present: {'gvkey' in u.columns}")
    if 'gvkey' in u.columns:
        print("Unified gvkey stats:", u['gvkey'].describe())
except Exception as e:
    print("Unified Error:", e)

# 2. Check Execucomp
try:
    e = pd.read_parquet(r'c:/Users/sinas/OneDrive/Desktop/Projects/Thesis_Bmad/Data/Data/Datasets/Datasets/Data_Processing/F1D/1_Inputs/Execucomp/comp_execucomp.parquet')
    print("\nExecucomp Columns:")
    relevant = [c for c in e.columns if any(x in c.lower() for x in ['ceo', 'date', 'year', 'start', 'end', 'left', 'id'])]
    print(relevant)
    print("\nSample Data:")
    print(e[['execid', 'gvkey', 'year', 'becameceo', 'leftofc', 'ceoann']].head(10))
except Exception as e:
    print("Execucomp Error:", e)
