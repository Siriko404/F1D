
import os
from pathlib import Path

root = Path(r"c:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D\1_Inputs")
with open("files_list.txt", "w") as f:
    for path in root.rglob("*"):
        if path.is_file():
            f.write(f"{path.name} | {path.parent.name}\n")
