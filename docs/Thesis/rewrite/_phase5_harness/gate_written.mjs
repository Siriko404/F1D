// Gate the already-written 17 sections (written_prose.json) against their briefs -- 0 agents.
// Section-level allowed sets (so writer para_id formats don't cause false "unknown paragraph").
// Reports per section: which paragraphs carry a fabricated number / hardcoded table / forbidden
// word / bad cite / broken LaTeX -> tells us what the boss must fix before we spend red-team tokens.
import { runGates } from "./gates.mjs";
import fs from "fs";

const H = new URL(".", import.meta.url);
const WRITTEN = JSON.parse(fs.readFileSync(new URL("written_prose.json", H), "utf8"));
const BRIEFS = JSON.parse(fs.readFileSync(new URL("briefs.json", H), "utf8"));
const briefOf = (s) => BRIEFS.find((b) => b.stem === s.stem || b.section === s.section);

let totalBlocks = 0, dirty = 0;
for (const sec of WRITTEN) {
  const b = briefOf(sec);
  const blocks = [], flags = [];
  for (const p of sec.paragraphs) {
    const r = runGates({
      prose: p.final_prose || "",
      allowedTokens: b.allowed_tokens_all || [],
      allowedKeys: b.allowed_cites_all || [],
      numberTables: b.number_table_map_all || null,
      props: [],                       // skip bijection at input-gate (para_id formats vary)
    });
    blocks.push(...r.blocks.map((x) => `${p.para_id}: ${x}`));
    flags.push(...r.flags.map((x) => `${p.para_id}: ${x}`));
  }
  totalBlocks += blocks.length;
  if (blocks.length) dirty++;
  const tag = blocks.length ? "DIRTY" : "clean";
  console.log(`[${tag}] ${sec.section.padEnd(9)} ${sec.paragraphs.length} paras  blocks=${blocks.length} flags=${flags.length}`);
  for (const x of blocks.slice(0, 6)) console.log(`        BLOCK ${x}`);
}
console.log(`\n${"=".repeat(50)}`);
console.log(`${WRITTEN.length} sections | ${dirty} DIRTY | ${totalBlocks} total blocks`);
console.log(dirty === 0 ? "ALL INPUT PROSE GATE-CLEAN" : "some sections need boss fixes (expected for raw drafts)");
