# -*- coding: utf-8 -*-
"""Build step: inject briefs.json + gates.mjs into harness.template.mjs -> a self-contained,
ASCII-clean harness.mjs for the Workflow tool. Then verify: zero non-ASCII / CR / ctrl bytes,
and a syntax wrap-check (lessons §6: node --check fails on top-level await; use new Function)."""
import json, re, subprocess, sys
from pathlib import Path
H = Path(__file__).resolve().parent
tmpl = (H/"harness.template.mjs").read_text(encoding="utf-8")
briefs = (H/"briefs.json").read_text(encoding="utf-8")          # already ascii (ensure_ascii=True)
gates = (H/"gates.mjs").read_text(encoding="utf-8")

# gates.mjs -> inline: drop the `export ` keywords (no module exports in the workflow body)
gates_inline = re.sub(r'^export\s+', '', gates, flags=re.M)

out = tmpl.replace("__BRIEFS__", briefs.strip()).replace("__GATES__", gates_inline)

# sanitize: transliterate common non-ASCII (template comments/prompts) -> ASCII; normalize newlines
TRANSLIT = {"—":"--","–":"-","§":"Sec.","’":"'","‘":"'","“":'"',
            "”":'"','→':"->","…":"...","×":"x","≥":">=","≤":"<=",
            "±":"+/-","²":"2","≈":"~","é":"e","·":" - "}
for k, v in TRANSLIT.items(): out = out.replace(k, v)
out = out.replace("\r\n", "\n").replace("\r", "\n")
bad = [(i, c) for i, c in enumerate(out) if ord(c) > 0x7f or (ord(c) < 0x20 and c not in "\n\t")]
if bad:
    print(f"[FAIL] {len(bad)} non-ASCII/ctrl chars remain (first @ {bad[0][0]}: {bad[0][1]!r} U+{ord(bad[0][1]):04X})"); sys.exit(1)

dest = H/"harness.mjs"
dest.write_text(out, encoding="ascii", newline="\n")
print(f"[ok] wrote {dest.name}: {len(out)} chars, pure ASCII, LF-only")

# syntax wrap-check via node (Function constructor; top-level await/return valid only in the async wrapper)
checker = r'''
const fs=require('fs');
let src=fs.readFileSync(process.argv[1],'utf8').replace('export const meta','const meta');
try {
  new Function('agent','parallel','pipeline','log','phase','args','budget','workflow',
               '(async()=>{'+src+'})');
  console.log('[ok] syntax wrap-check passed');
} catch(e) { console.error('[FAIL] syntax: '+e.message); process.exit(1); }
'''
(H/"_wrapcheck.cjs").write_text(checker, encoding="ascii", newline="\n")
r = subprocess.run(["node", str(H/"_wrapcheck.cjs"), str(dest)], capture_output=True, text=True)
print(r.stdout.strip() or r.stderr.strip())
sys.exit(r.returncode)
