// Smoke-test the phase-B assembly (no agents): sourceFacts/thesisText build; a gate-clean patch is
// applied; a gate-breaking patch is REJECTED (original kept); final stays 17/17 OK.
import { runGates } from "./gates.mjs";
import fs from "fs";
const DATA = JSON.parse(fs.readFileSync(new URL("phaseB_data.json", import.meta.url), "utf8"));
let pass = 0, fail = 0;
const ck = (n, c) => { console.log(`  [${c ? "OK " : "FAIL"}] ${n}`); c ? pass++ : fail++; };

const gateProse = (s, prose) => runGates({ prose: prose || "", allowedTokens: s.allowed_tokens_all || [],
  allowedKeys: s.allowed_cites_all || [], numberTables: s.number_table_map_all || null, props: [] });

// 1. facts + thesis assemble without crashing
const facts = DATA.map(s => `SECTION ${s.section}: ${(s.bright_lines || []).join(" | ")}`).join("\n");
const thesis = DATA.map(s => s.paragraphs.map(p => `[${p.para_id}] ${p.final_prose}`).join("\n")).join("\n");
ck("facts + thesis assemble (non-empty)", facts.length > 100 && thesis.length > 10000);

// 2. simulate boss patches: one CLEAN rephrase + one GATE-BREAKING edit -> assemble like the harness does
const s21 = DATA.find(s => s.section === "2.1");
const p1 = s21.paragraphs[0];
const cleanPatch = p1.final_prose + " We restate this plainly for the lay reader.";   // adds no number/cite/forbidden -> clean
const dirtyPatch = p1.final_prose + " The stock arm is suppressed.";                   // forbidden word -> must be rejected
const patchMap = { [`2.1|${p1.para_id}`]: cleanPatch, [`2.1|__d__`]: dirtyPatch };

let edited = 0, rejected = 0;
const sections = DATA.map(s => {
  const paras = s.paragraphs.map(p => {
    const cand = patchMap[`${s.section}|${p.para_id}`];
    if (cand != null && cand !== p.final_prose) {
      const g = gateProse(s, cand);
      if (g.pass) { edited++; return { para_id: p.para_id, final_prose: cand }; }
      rejected++; return { para_id: p.para_id, final_prose: p.final_prose };
    }
    return { para_id: p.para_id, final_prose: p.final_prose };
  });
  const blocks = [];
  for (const p of paras) blocks.push(...gateProse(s, p.final_prose).blocks);
  return { section: s.section, status: blocks.length ? "BLOCKED" : "OK" };
});
ck("clean patch applied (edited=1)", edited === 1);

// 3. a directly gate-breaking patch is rejected
const gd = gateProse(s21, dirtyPatch);
ck("gate-breaking patch detected as dirty", !gd.pass && gd.blocks.some(b => b.includes("suppress")));

// 4. final still 17/17 OK (clean input + only clean patches applied)
const ok = sections.filter(s => s.status === "OK").length;
ck("final 17/17 OK after assembly", ok === 17);

console.log(`\n${"=".repeat(40)}\n${fail === 0 ? "PHASE-B FLOW OK" : "PHASE-B FLOW BROKEN"}: ${pass} pass, ${fail} fail (edited=${edited}, rejected=${rejected})`);
process.exit(fail === 0 ? 0 : 1);
