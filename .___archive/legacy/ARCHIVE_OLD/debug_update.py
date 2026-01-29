"""Quick debug test for update persistence"""
import pandas as pd

# Create test dataframe
df = pd.DataFrame({
    'file_name': ['a', 'b', 'c', 'd', 'e'],
    'value': [1, 2, 3, 4, 5]
})

# Initialize column with None
df['gvkey'] = None

print("Before update:")
print(df)
print(f"gvkey null count: {df['gvkey'].isna().sum()}")

# Test .at[] update
df.at[0, 'gvkey'] = 'ABC123'
df.at[2, 'gvkey'] = 'DEF456'

print("\nAfter .at[] update:")
print(df)
print(f"gvkey null count: {df['gvkey'].isna().sum()}")

# Check if filter works
unmatched = df['gvkey'].isna()
print(f"\nUnmatched rows: {unmatched.sum()}")
print(df[unmatched])
