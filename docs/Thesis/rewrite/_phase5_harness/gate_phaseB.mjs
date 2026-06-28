// Gate the cite-fixed phaseB_data.json (each section carries its own gate sets) -- confirm input clean.
import { runGates } from "./gates.mjs";
import fs from "fs";
const DATA = JSON.parse(fs.readFileSync(new URL("phaseB_data.json", import.meta.url), "utf8"));
let dirty = 0, total = 0;
for (const s of DATA) {
  const blocks = [];
  for (const p of s.paragraphs) {
    const r = runGates({
      prose: p.final_prose || "",
      allowedTokens: s.allowed_tokens_all || [],
      allowedKeys: s.allowed_cites_all || [],
      numberTables: s.number_table_map_all || null,
      props: [],
    });
    blocks.push(...r.blocks.map((x) => `${p.para_id}: ${x}`));
  }
  total += blocks.length;
  if (blocks.length) { dirty++; console.log(`[DIRTY] ${s.section}`); blocks.slice(0, 6).forEach((x) => console.log("   " + x)); }
}
console.log(`\n${DATA.length} sections | ${dirty} dirty | ${total} blocks`);
console.log(dirty === 0 ? "PHASE-B INPUT GATE-CLEAN (17/17)" : "STILL DIRTY");
process.exit(dirty === 0 ? 0 : 1);
