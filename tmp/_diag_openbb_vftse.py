"""Use openbb to search for FTSE100 implied volatility data."""
import warnings; warnings.filterwarnings("ignore")
from openbb import obb

# Try index price for VFTSE under various symbols and providers
symbols = ["VFTSE", "^VFTSE", "VIX", "^VIX", "FTSE100VIX", "FTSEIVI", "UKX-VOL"]
providers = ["yfinance", "fmp", "polygon", "intrinio", "tiingo", "fred"]

for sym in symbols:
    for prov in providers:
        try:
            r = obb.index.price.historical(symbol=sym, start_date="2014-01-01",
                                          end_date="2014-06-30", provider=prov)
            df = r.to_df() if hasattr(r, "to_df") else r
            if df is not None and len(df) > 0:
                print(f"{sym} @ {prov}: {len(df)} rows ✓  cols={list(df.columns)[:5]}")
                print(df.head(2))
                break
        except Exception as e:
            pass  # silent

# Try search
print("\nSearching for 'FTSE volatility' indexes via openbb...")
try:
    r = obb.index.search(query="FTSE Volatility")
    df = r.to_df() if hasattr(r, "to_df") else r
    print(df.head(10) if df is not None else "empty")
except Exception as e:
    print(f"search error: {e}")
