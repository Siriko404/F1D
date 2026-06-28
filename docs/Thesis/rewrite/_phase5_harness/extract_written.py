# Extract the already-written prose for all 17 sections from the (paused) workflow journal+agent files.
# Prefers the editor-merged result (agent labelled "section editor", section from its prompt); falls back
# to a block-writer draft. Output: written_prose.json = [{stem, section, paragraphs:[{para_id,final_prose}]}].
import json, re, glob, os, sys

WD = r"C:\Users\sinas\.claude\projects\C--Users-sinas-OneDrive-Desktop-Projects-Thesis-Bmad-Data-Data-Datasets-Datasets-Data-Processing-F1D\e514389f-0c61-4e93-9f33-08043f70a4c0\subagents\workflows\wf_2363f61d-69a"
H = r"C:\Users\sinas\OneDrive\Desktop\Projects\Thesis_Bmad\Data\Data\Datasets\Datasets\Data_Processing\F1D-phase3\docs\Thesis\rewrite\_phase5_harness"
BRIEFS = json.load(open(os.path.join(H, "briefs.json"), encoding="utf-8"))
STEMS = [(b["stem"], b["section"]) for b in BRIEFS]

def tool_inputs(text):
    """yield every StructuredOutput tool_use input object found in an agent jsonl."""
    for ln in text.splitlines():
        try:
            env = json.loads(ln)
        except Exception:
            continue
        for blk in (env.get("message", {}).get("content", []) or []):
            if isinstance(blk, dict) and blk.get("type") == "tool_use" and isinstance(blk.get("input"), dict):
                yield blk["input"]

editor_merge = {}   # section -> paragraphs
writer_draft = {}   # section -> paragraphs (first found)

for f in glob.glob(os.path.join(WD, "agent-*.jsonl")):
    t = open(f, encoding="utf-8", errors="ignore").read()
    is_editor = "You are the section editor" in t
    if is_editor:
        m = re.search(r'SECTION ([0-9.]+|abstract) \\?\(', t)   # from brmain header (quote may be JSON-escaped)
        sec = m.group(1) if m else None
        for inp in tool_inputs(t):
            if sec and "paragraphs" in inp and inp.get("paragraphs"):
                editor_merge[sec] = inp["paragraphs"]
    # block-writer drafts (section-tagged)
    if "Write the FINAL LaTeX prose for ALL of the following sections" in t:
        for inp in tool_inputs(t):
            for s in inp.get("sections", []) or []:
                sec = str(s.get("section"))
                if s.get("paragraphs") and sec not in writer_draft:
                    writer_draft[sec] = s["paragraphs"]

written = []
report = []
for stem, sec in STEMS:
    if sec in editor_merge:
        written.append({"stem": stem, "section": sec, "paragraphs": editor_merge[sec]}); report.append((sec, "MERGED", len(editor_merge[sec])))
    elif sec in writer_draft:
        written.append({"stem": stem, "section": sec, "paragraphs": writer_draft[sec]}); report.append((sec, "draft", len(writer_draft[sec])))
    else:
        report.append((sec, "MISSING", 0))

out = os.path.join(H, "written_prose.json")
json.dump(written, open(out, "w", encoding="utf-8"), ensure_ascii=True)
print(f"sections found: {len(written)}/17  -> {out}")
for sec, src, n in report:
    print(f"  {sec:10} {src:7} {n} paras")
missing = [s for s, src, n in report if src == "MISSING"]
print("MISSING:", missing if missing else "none")
