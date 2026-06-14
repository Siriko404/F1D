# 2.1-P7 softening (user "correct it now"): cut "and we do not try" (it wrongly implies we
# ran no identification; the two readings are genuinely unidentifiable) + remove the resolved
# TODO comment. Updates BOTH the .tex and the 2.1 ledger prose, count-guarded. Convention:
# programmatic transfer, fail-closed.
import json
import pathlib

ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = ROOT / "docs" / "Thesis" / "thesis_draft.tex"
LED = ROOT / "docs" / "Thesis" / "rewrite" / "section2.1_paragraph_ledger.json"
OLD = "Our design cannot distinguish them, and we do not try."
NEW = "Our design cannot distinguish them."

# --- .tex: remove the TODO comment line FIRST (it also contains OLD), then shorten the prose ---
tex = TEX.read_text(encoding="utf-8")
lines = tex.splitlines(keepends=True)
n0 = len(lines)
lines = [ln for ln in lines if not ln.lstrip().startswith("% TODO(scrutiny-reframe 2026-06-13)")]
assert n0 - len(lines) == 1, f"expected to drop exactly 1 TODO line, dropped {n0 - len(lines)}"
tex = "".join(lines)
assert tex.count(OLD) == 1, f"TEX: expected 1 prose occ of OLD after TODO removal, got {tex.count(OLD)}"
tex = tex.replace(OLD, NEW)
assert "and we do not try" not in tex, "TEX: 'and we do not try' still present"
TEX.write_text(tex, encoding="utf-8")

# --- ledger prose: same phrase edit; validate JSON ---
led = LED.read_text(encoding="utf-8")
assert led.count(OLD) == 1, f"LEDGER: expected 1 occ of OLD, got {led.count(OLD)}"
led = led.replace(OLD, NEW)
assert "and we do not try" not in led, "LEDGER: phrase still present"
json.loads(led)  # fail closed if JSON broke
LED.write_text(led, encoding="utf-8")

print("OK: P7 softened in .tex + 2.1 ledger; TODO comment removed; JSON valid.")
