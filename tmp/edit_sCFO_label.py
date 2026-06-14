# Fix A (sCFO mislabel): §2.4 "scaled cash flow from operations" describes a LEVEL, but sCFO is
# the 5-yr rolling SD of oancfy/atq (= OCF volatility; ocf_volatility.py / _compustat_engine.py:356
# `.rolling("1826D",min_periods=3).std()`; config/variables.yaml:425). Spec page already says
# "cash-flow volatility". Align the prose + the Appendix I gloss. Count-guarded; ledger synced.
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
APP = ROOT / "docs" / "Thesis" / "appendix_I_cash_scrutiny.tex"
LED = ROOT / "docs" / "Thesis" / "rewrite" / "section2.4_paragraph_ledger.json"

# 1. §2.4 prose control list
tex = TEX.read_text(encoding="utf-8")
old, new = "scaled cash flow from operations", "cash-flow volatility"
assert tex.count(old) == 1, f"TEX: expected 1 occ of {old!r}, got {tex.count(old)}"
TEX.write_text(tex.replace(old, new), encoding="utf-8")

# 2. Appendix I control gloss
app = APP.read_text(encoding="utf-8")
aold, anew = "Cash Flow (sCFO)", "Cash-Flow Volatility (sCFO)"
assert app.count(aold) == 1, f"APP: expected 1 occ of {aold!r}, got {app.count(aold)}"
APP.write_text(app.replace(aold, anew), encoding="utf-8")

# 3. §2.4 ledger sync (if it holds the prose)
ledn = 0
if LED.exists():
    led = LED.read_text(encoding="utf-8")
    ledn = led.count(old)
    if ledn:
        led = led.replace(old, new)
        json.loads(led)  # fail closed if JSON broke
        LED.write_text(led, encoding="utf-8")

print(f"OK: sCFO -> 'cash-flow volatility' in tex(1) + appendix(1) + ledger({ledn}).")
