"""Pull only FAIL / INCONCLUSIVE blocks from all batch files into one summary."""
import re
from pathlib import Path

TMP = Path("tmp")
batches = sorted(TMP.glob("campello_var_anchor_check_batch_*.md"))

out_lines = ["# Aggregated FAIL / INCONCLUSIVE verdicts — 88-var anchor check", "", "Source: `tmp/campello_var_anchor_check_batch_*.md`", ""]

n_fail = 0
n_inc = 0
for fp in batches:
    text = fp.read_text(encoding="utf-8")
    # Split into VAR blocks
    blocks = re.split(r"(?=^## VAR_\d+)", text, flags=re.MULTILINE)
    for blk in blocks:
        m_verdict = re.search(r"\*\*VERDICT\*\*:\s*\*\*([^*]+)\*\*", blk)
        if not m_verdict:
            continue
        verdict = m_verdict.group(1).strip()
        if "FAIL" in verdict or "INCONCLUSIVE" in verdict:
            if "FAIL" in verdict: n_fail += 1
            else: n_inc += 1
            out_lines.append(f"### From `{fp.name}`")
            out_lines.append("")
            out_lines.append(blk.strip())
            out_lines.append("")

out_lines.insert(3, f"**Totals**: {n_fail} FAIL, {n_inc} INCONCLUSIVE (of 88 vars)")
out_lines.insert(4, "")

Path("tmp/campello_var_anchor_FAILS_summary.md").write_text("\n".join(out_lines), encoding="utf-8")
print(f"Wrote tmp/campello_var_anchor_FAILS_summary.md: {n_fail} FAIL, {n_inc} INC")
