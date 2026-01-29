import pandas as pd
df = pd.read_parquet(r'4_Outputs/3_Financial_Features/2025-12-26_203919/firm_controls_2010.parquet')
print('Columns:', df.columns.tolist())
intensity_cols = [c for c in df.columns if c.startswith('shift_intensity')]
print(f'\nShift intensity columns: {intensity_cols}')
print('\nCoverage for 2010:')
for c in intensity_cols:
    print(f'  {c}: {df[c].notna().sum():,} / {len(df):,}')
