# Assemble the Phase-C final_prose from the 5 paragraph ledgers into a readable markdown preview
# (NOT LaTeX -- the .tex push is Phase D, after the user verifies). Also prints 3.4 to stdout.
import json, pathlib
DEST = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\docs\Thesis\rewrite")
TITLES = {"3.1": "3.1 Data, Sample, and Variable Construction", "3.2": "3.2 Main Analysis 1: The Pre-Announcement Run-Up",
          "3.3": "3.3 Main Analysis 2: Differential Timing Around the Announcement", "3.4": "3.4 Main Analysis 3: Cash-Specificity",
          "4.1": "4.1 Ruling Out Analyst Scrutiny"}
out = ["# Section 3 / 4 prose preview (Phase C; from the paragraph ledgers, NOT yet in the .tex)\n"]
for sid in ["3.1", "3.2", "3.3", "3.4", "4.1"]:
    led = json.loads((DEST / f"section{sid}_paragraph_ledger.json").read_text(encoding="utf-8"))
    out.append(f"\n## {TITLES[sid]}\n")
    for para in led["paragraphs"]:
        out.append(f"\n**[{para['para_id']}]**  {para['final_prose']}\n")
(DEST / "sec34_prose_preview.md").write_text("\n".join(out), encoding="utf-8")
print("wrote sec34_prose_preview.md\n")
# print 3.4 to stdout for inline review
led = json.loads((DEST / "section3.4_paragraph_ledger.json").read_text(encoding="utf-8"))
print("===== 3.4 Cash-Specificity (drafted prose) =====")
for para in led["paragraphs"]:
    print(f"\n[{para['para_id']}]\n{para['final_prose']}")
