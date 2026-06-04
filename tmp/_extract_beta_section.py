import fitz
doc = fitz.open(r"docs\papers\campello_etal_2022_brexit_jfqa.pdf")
# Pages 20-22 = Table 1 variable definitions
for i in [20, 21, 22]:
    print(f"==== PAGE {i+1} ====")
    print(doc[i].get_text())
    print()
