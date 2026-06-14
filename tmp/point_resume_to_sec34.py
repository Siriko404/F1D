# Additive pointer: make _RESUME_STATE.json surface the Sec 3/4 planning doc + the opus-spawn blocker,
# so the post-compaction agent reads it first. Touches only one new top-level key. JSON-aware; idempotent.
import json, pathlib
ROOT = pathlib.Path(r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D")
F = ROOT / "docs/Thesis/rewrite/_RESUME_STATE.json"
d = json.loads(F.read_text(encoding="utf-8"))
KEY = "SECTION_3_4_PLANNING_2026_06_14"
val = ("[CURRENT after the 2026-06-14 session] §2 is DONE. Work moved to Section 3/4 proposition planning. "
    "READ docs/Thesis/rewrite/section34_planning_RESUME.md FIRST -- it holds the ratified 8-unit manifest, the "
    "8-agent workflow design (schemas + red-team rubric + reason/evidence-atomic), the §3/§4 content scaffold "
    "(5 subsections; §4.2/C7 DROPPED), and the OPEN DECISIONS. Two input-fixes committed this session: "
    "93a39904 (variable_ledger refresh) + 08b27919 (SD-basis verify + _sd_basis_note). "
    "BLOCKER (do NOT spend the agent fleet until resolved): my probes show subagents run claude-sonnet-4-6 even "
    "with model:'opus'; the USER DISPUTES this ('I've spawned opus a thousand times'). Resolve the opus-spawn "
    "question FIRST (try full id 'claude-opus-4-8' / a subagent_type that pins opus / re-probe + confirm the "
    "assistant-message model). See the doc's BLOCKER section.")
if d.get(KEY) == val:
    print("idempotent: pointer already present; no change.")
else:
    d[KEY] = val
    F.write_text(json.dumps(d, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    json.loads(F.read_text(encoding="utf-8"))
    print("OK: added", KEY, "to _RESUME_STATE.json; JSON valid.")
