# Fix B (PRisk gloss): the prose "share...of political risk" is faithful to Hassan's own words,
# but PRisk is a weighted, 99th-pct-capped, SCALED bigram index (Table 1 mean 99.6 / max 1192),
# not a 0-100% share. Insert "scaled measure of" so a referee doesn't read "share = 99.6" as a
# percentage. No scaling-constant claim (unverified). tex + 2.5 ledger, count-guarded.
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
LED = ROOT / "docs" / "Thesis" / "rewrite" / "section2.5_paragraph_ledger.json"

OLD = "the share of a firm's earnings call devoted to political risk of \\citet{hassan2020}"
NEW = "\\citet{hassan2020}'s scaled measure of the share of a firm's earnings call devoted to political risk"

tex = TEX.read_text(encoding="utf-8")
assert tex.count(OLD) == 1, f"TEX: expected 1 occ, got {tex.count(OLD)}"
TEX.write_text(tex.replace(OLD, NEW), encoding="utf-8")

ledn = 0
if LED.exists():
    led = LED.read_text(encoding="utf-8")
    ledn = led.count(OLD)
    if ledn:
        led = led.replace(OLD, NEW)
        json.loads(led)
        LED.write_text(led, encoding="utf-8")
print(f"OK: PRisk gloss -> 'scaled measure of...' in tex(1) + ledger({ledn}).")
