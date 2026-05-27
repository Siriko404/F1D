"""Try multiple tickers/sources for FTSE 100 implied vol."""
import warnings; warnings.filterwarnings("ignore")
import yfinance as yf

# Various candidate tickers for FTSE 100 implied volatility
tickers = ["^VFTSE", "VFTSE", "V1X.L", "VFTSE.L", "VOL.L", "UKX-VOL",
           "^FTUK", "^UKX-V", "I.AVI.L", "AVI.L"]

for t in tickers:
    try:
        df = yf.download(t, start="2010-01-01", end="2015-01-31", progress=False, auto_adjust=False)
        if len(df):
            print(f"{t}: {len(df)} rows ✓  first={df.index[0]}  last={df.index[-1]}")
        else:
            print(f"{t}: empty")
    except Exception as e:
        print(f"{t}: ERROR {e}")
