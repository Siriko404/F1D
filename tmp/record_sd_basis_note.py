# Record the SD-basis finding as an ADDITIVE top-level note in claim_findings_ledger.json so the
# Sec 3/4 planners inherit it. Touches NO existing claim/number/coefficient -- adds one key only.
# JSON-aware; idempotent; validate at end.
import json, pathlib
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
F = ROOT / "docs/Thesis/rewrite/claim_findings_ledger.json"
d = json.loads(F.read_text(encoding="utf-8"))

KEY = "_sd_basis_note_2026_06_14"
note = {
    "issue": ("The all-universe Table 1 rebuild (commit a65872f2, 06-14) changed the reported UncResCEO SD. "
        "Two LEGITIMATE SDs now coexist: 0.3010 (all-universe, N=44,900 -- the current Table 1) and 0.3072 "
        "(the UncRes-equation estimation universe, N=27,622 -- the run-up sample). 0.3072 is NOT a stale "
        "headline; it is the estimation-sample SD."),
    "live_prose_status": ("SAFE. The locked Sec 2.5 prose cites only the FB percentages (5%/1.5%/2.2%), never an "
        "SD value. Verified programmatically (tmp/verify_sd_basis.py): the FB rounds to 5/1.5/2.2 under BOTH SDs "
        "(0.3010 -> 5.28/1.51/2.19; 0.3072 -> 5.17/1.48/2.15). No error in any committed prose."),
    "C5_note_kept": "The C5 risk note 'vs UncRes SD 0.3072' uses the estimation-sample SD; correct, kept as-is.",
    "SEC_3_REWRITE_DECISION": ("The old Sec 3 prose (commit 81efc78) says 'fifteen percent of a SD (0.3072, "
        "Table 1 Panel B)'. That POINTER is now stale -- the all-universe Table 1 shows 0.3010 and has no Panel B. "
        "When Sec 3.2 is planned/written: pick the SD basis (estimation-sample 0.3072 with a footnote, OR "
        "all-universe Table-1 0.3010) and cite it correctly. Magnitude (~15%) is robust either way (15.0% vs 15.3%)."),
}

if d.get(KEY) == note:
    print("idempotent: note already present + identical; no change.")
else:
    d[KEY] = note
    F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(F.read_text(encoding="utf-8"))  # validate
    print(f"OK: added {KEY} to claim_findings_ledger.json; JSON valid; no existing key altered.")
