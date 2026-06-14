# 3 user edits to 2.5 (2026-06-14), programmatic ledger->.tex w/ count + drift guards. Fail-closed.
# (1) add verified one-tailed sig levels in the coef parens (P2); (2) cut median tail (P4); (3) cut PRisk-undermining closer (P2).
import json

LED = "docs/Thesis/rewrite/section2.5_paragraph_ledger.json"
TEX = "docs/Thesis/thesis_draft.tex"

reps = [
    # P2: significance levels in the same parens (verified _tables_from_bible.tex col 1: PRisk*** p<.01; US-EPU** p<.05; GEPU** p<.05; one-tailed for IVs)
    ("political risk of \\citet{hassan2020} (coefficient $0.0001$);",
     "political risk of \\citet{hassan2020} (coefficient $0.0001$, $p<0.01$);"),
    ("\\citet{baker2016} ($0.0124$);",
     "\\citet{baker2016} ($0.0124$, $p<0.05$);"),
    ("\\citet{davis2016} ($0.0181$).",
     "\\citet{davis2016} ($0.0181$, $p<0.05$)."),
    # P2: cut the PRisk-undermining closer entirely (leading space removed)
    (" The political-risk coefficient, while significant, is small in level; the policy-uncertainty indices, being external to the call, provide the cleaner benchmark.",
     ""),
    # P4: cut the unnecessary median tail
    ("for calls above the median, which is zero, since most calls draw no cash scrutiny at all.",
     "for calls above the median."),
]

# --- TEX ---
tex = open(TEX, encoding="utf-8", newline="").read()
for old, new in reps:
    assert tex.count(old) == 1, f"TEX: expected 1 occurrence, got {tex.count(old)}: {old!r}"
    tex = tex.replace(old, new)
for _, new in reps:
    if new:
        assert new in tex, f"TEX: new fragment missing: {new!r}"

# --- LEDGER (P2, P4 final_prose) ---
d = json.load(open(LED, encoding="utf-8"))
for old, new in reps:
    hits = [k for k in ("P2", "P4") if old in d["paragraphs"][k]["final_prose"]]
    assert len(hits) == 1, f"LEDGER: {old!r} matched paragraphs {hits}"
    k = hits[0]
    d["paragraphs"][k]["final_prose"] = d["paragraphs"][k]["final_prose"].replace(old, new)

# guards: dash-free + competition-free + placeholder intact + ledger==tex verbatim
for k in ("P1", "P2", "P4", "P5"):
    fp = d["paragraphs"][k]["final_prose"]
    assert "---" not in fp and "--" not in fp, f"{k} dash"
    assert fp in tex, f"{k} final_prose not verbatim in tex after edit"
assert "PLACEHOLDER-FB" in tex, "FB placeholder lost"
for w in ("hoberg", "competition", "discriminant"):
    assert w not in tex.lower(), f"'{w}' in tex"

open(TEX, "w", encoding="utf-8", newline="").write(tex)
open(LED, "w", encoding="utf-8", newline="\n").write(json.dumps(d, indent=2, ensure_ascii=False) + "\n")
json.load(open(LED, encoding="utf-8"))
print("OK: 3 edits applied to ledger + tex (sig levels p<0.01/p<0.05/p<0.05; median tail cut; PRisk closer cut). Guards passed.")
