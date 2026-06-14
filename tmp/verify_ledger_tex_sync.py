# Verify every §2 ledger's final_prose is present VERBATIM in thesis_draft.tex.
# json.load gives the UNESCAPED string (\\citet -> \citet), which is what the raw .tex contains,
# so a substring test is the correct drift check. Line endings normalized (\r\n -> \n) to avoid
# false mismatches. Outcomes per paragraph: MATCH | MISMATCH (drift) | EMPTY (ledger not synced).
import json, pathlib, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
TEX = (ROOT / "docs/Thesis/thesis_draft.tex").read_text(encoding="utf-8").replace("\r\n", "\n")

def diagnose(fp, tex):
    # find first 60 chars of fp in tex; walk to first divergence
    head = fp[:60]
    idx = tex.find(head)
    if idx == -1:
        # try a shorter anchor
        idx2 = tex.find(fp[:25])
        if idx2 == -1:
            return "  start-anchor NOT FOUND in .tex (prose absent or heavily reworded)"
        idx = idx2
    seg = tex[idx: idx + len(fp)]
    k = 0
    while k < min(len(fp), len(seg)) and fp[k] == seg[k]:
        k += 1
    return (f"  first divergence at char {k}:\n"
            f"    LEDGER: ...{fp[max(0,k-35):k]}<<HERE>>{fp[k:k+35]}...\n"
            f"    .TEX  : ...{seg[max(0,k-35):k]}<<HERE>>{seg[k:k+35]}...")

rows, any_drift = [], False
for sub in ["2.1", "2.2", "2.3", "2.4", "2.5"]:
    d = json.loads((ROOT / f"docs/Thesis/rewrite/section{sub}_paragraph_ledger.json").read_text(encoding="utf-8"))
    for pk, p in d.get("paragraphs", {}).items():
        fp = (p.get("final_prose") or "").replace("\r\n", "\n").strip()
        if not fp:
            rows.append((sub, pk, "EMPTY", len(fp))); continue
        status = "MATCH" if fp in TEX else "MISMATCH"
        if status == "MISMATCH":
            any_drift = True
        rows.append((sub, pk, status, len(fp)))

print(f"{'SUB':5} {'PARA':5} {'STATUS':9} {'len':>6}")
print("-" * 32)
for sub, pk, st, ln in rows:
    mark = "  <<< DRIFT" if st == "MISMATCH" else ("  (ledger not synced)" if st == "EMPTY" else "")
    print(f"{sub:5} {pk:5} {st:9} {ln:6d}{mark}")

print("\nSUMMARY:",
      f"{sum(r[2]=='MATCH' for r in rows)} MATCH,",
      f"{sum(r[2]=='MISMATCH' for r in rows)} MISMATCH,",
      f"{sum(r[2]=='EMPTY' for r in rows)} EMPTY")

# diagnose every mismatch
for sub, pk, st, ln in rows:
    if st == "MISMATCH":
        d = json.loads((ROOT / f"docs/Thesis/rewrite/section{sub}_paragraph_ledger.json").read_text(encoding="utf-8"))
        fp = d["paragraphs"][pk]["final_prose"].replace("\r\n", "\n").strip()
        print(f"\n### MISMATCH {sub} {pk}:")
        print(diagnose(fp, TEX))

print("\nVERDICT:", "DRIFT DETECTED -- investigate" if any_drift else "NO DRIFT (every populated final_prose is verbatim in .tex)")
