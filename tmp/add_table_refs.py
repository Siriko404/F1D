# Task 2 (2026-06-14): add Table~\ref to the 5 tables §2 actually discusses.
# Programmatic ledger->.tex (str.replace in BOTH, count + drift + dash + competition guards).
# Same pattern as tmp/edit_2_5_p2p4.py. Refs: summary_stats (P5), h11/h24/h24b (P2),
# cash_scrutiny_validity (P4).
import json

LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"

reps = [
    # P2 -- attach each convergent table to its coefficient
    ("\\citet{hassan2020} (coefficient $0.0001$, $p<0.01$);",
     "\\citet{hassan2020} (coefficient $0.0001$, $p<0.01$; Table~\\ref{tab:h11_prisk_uncertainty});"),
    ("\\citet{baker2016} ($0.0124$, $p<0.05$);",
     "\\citet{baker2016} ($0.0124$, $p<0.05$; Table~\\ref{tab:h24_us_epu});"),
    ("\\citet{davis2016} ($0.0181$, $p<0.05$).",
     "\\citet{davis2016} ($0.0181$, $p<0.05$; Table~\\ref{tab:h24b_global_epu})."),
    # P4 -- cash-scrutiny validity result
    ("ask about cash ($0.7530$ and $0.8519$),",
     "ask about cash ($0.7530$ and $0.8519$; Table~\\ref{tab:cash_scrutiny_validity}),"),
    # P5 -- summary statistics for all variables
    ("are catalogued in the Appendix.",
     "are catalogued in the Appendix. Summary statistics for all variables used in the designs appear in Table~\\ref{tab:summary_stats}."),
]

# --- TEX ---
tex = open(TEX, encoding="utf-8", newline="").read()
for old, new in reps:
    assert tex.count(old) == 1, f"TEX: expected 1 occ, got {tex.count(old)}: {old!r}"
    tex = tex.replace(old, new)
for _, new in reps:
    assert new in tex, f"TEX: new fragment missing: {new!r}"

# --- LEDGER (P2/P4/P5 final_prose) ---
d = json.load(open(LED, encoding="utf-8"))
for old, new in reps:
    hits = [k for k in ("P1", "P2", "P4", "P5") if old in d["paragraphs"][k]["final_prose"]]
    assert len(hits) == 1, f"LEDGER: {old!r} matched {hits}"
    k = hits[0]
    d["paragraphs"][k]["final_prose"] = d["paragraphs"][k]["final_prose"].replace(old, new)

# guards: dash-free, ledger==tex verbatim, placeholder + competition unchanged
for k in ("P1", "P2", "P4", "P5"):
    fp = d["paragraphs"][k]["final_prose"]
    assert "---" not in fp and "--" not in fp, f"{k} dash"
    assert fp in tex, f"{k} final_prose not verbatim in tex"
assert "PLACEHOLDER-FB" in tex, "FB placeholder lost"
for w in ("hoberg", "competition", "discriminant"):
    assert w not in tex.lower(), f"'{w}' in tex"

open(TEX, "w", encoding="utf-8", newline="").write(tex)
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("OK: 5 table refs added (h11/h24/h24b in P2, cash_scrutiny_validity in P4, summary_stats in P5).")
