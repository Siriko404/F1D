# -*- coding: utf-8 -*-
"""Build harness_phaseB.mjs: inject phaseB_data.json + gates.mjs into harness_phaseB.template.mjs.
ASCII-clean, LF-only, wrap-checked, and asserted under the Workflow 512KB script cap."""
import re, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
tmpl = (H / "harness_phaseB.template.mjs").read_text(encoding="utf-8")
data = (H / "phaseB_data.json").read_text(encoding="utf-8")          # already ASCII (ensure_ascii=True)
gates = (H / "gates.mjs").read_text(encoding="utf-8")
gates_inline = re.sub(r'^export\s+', '', gates, flags=re.M)

for ph, n in (("__DATA__", tmpl.count("__DATA__")), ("__GATES__", tmpl.count("__GATES__"))):
    if n != 1:
        print(f"[FAIL] placeholder {ph} appears {n}x (must be exactly 1)"); sys.exit(1)

out = tmpl.replace("__DATA__", data.strip()).replace("__GATES__", gates_inline)

TRANSLIT = {"—": "--", "–": "-", "§": "Sec.", "’": "'", "‘": "'",
            "“": '"', "”": '"', "→": "->", "…": "...", "×": "x",
            "≥": ">=", "≤": "<=", "±": "+/-", "²": "2", "≈": "~",
            "é": "e", "·": " - "}
for k, v in TRANSLIT.items():
    out = out.replace(k, v)
out = out.replace("\r\n", "\n").replace("\r", "\n")
bad = [(i, c) for i, c in enumerate(out) if ord(c) > 0x7f or (ord(c) < 0x20 and c not in "\n\t")]
if bad:
    print(f"[FAIL] {len(bad)} non-ASCII/ctrl chars remain (first @ {bad[0][0]}: {bad[0][1]!r})"); sys.exit(1)

CAP = 524288
if len(out) > CAP:
    print(f"[FAIL] {len(out)} bytes > Workflow cap {CAP}"); sys.exit(1)

dest = H / "harness_phaseB.mjs"
dest.write_text(out, encoding="ascii", newline="\n")
print(f"[ok] wrote {dest.name}: {len(out)} chars ({CAP - len(out)} under cap), pure ASCII, LF-only")

checker = r'''
const fs=require('fs');
let src=fs.readFileSync(process.argv[1],'utf8').replace('export const meta','const meta');
try { new Function('agent','parallel','pipeline','log','phase','args','budget','workflow','(async()=>{'+src+'})');
  console.log('[ok] syntax wrap-check passed'); }
catch(e){ console.error('[FAIL] syntax: '+e.message); process.exit(1); }
'''
(H / "_wrapcheckB.cjs").write_text(checker, encoding="ascii", newline="\n")
r = subprocess.run(["node", str(H / "_wrapcheckB.cjs"), str(dest)], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
sys.exit(r.returncode)
