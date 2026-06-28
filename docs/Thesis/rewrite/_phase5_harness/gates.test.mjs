// gates.test.mjs — unit-test the deterministic spine on synthetic §4.5-PARA1 prose
// (throwaway test data, NOT thesis content). Proves: correct prose passes; each planted
// violation is BLOCKED/FLAGGED by the right gate. Run: node gates.test.mjs
import { runGates } from "./gates.mjs";

// §4.5-PARA1 real allowed set (from the locked ledger)
const allowedTokens = ["+0.0033**","+0.0391***","-0.0348",".0008",".0011","0.0015","0.0026",
  "0.0027","0.003","0.0078***","0.0086***","0.0140","0.026","0.0272","0.0967","0.3233***"];
const allowedKeys = ["harford1999","shleifer_vishny2003","louis2004"];
const props = [{ prop_id: "4.5-PARA1-a", signature: "+0.0391***" },
               { prop_id: "4.5-PARA1-b", signature: "0.0086***" }];

// CORRECT synthetic prose: only allowed numbers, valid cite, both props rendered, balanced LaTeX
const CORRECT = String.raw`The pre-announcement run-up survives dropping the first-deal restriction. On the all-deals-stacked panel the cash arm shows elevated residual uncertainty ($+0.0391^{***}$) and a rising cash ratio ($+0.0033^{**}$), while the stock arm is a flat null ($-0.0348$, n.s.). In binary forward form, higher residual uncertainty is associated with a deal announced next quarter (LPM $0.0086^{***}$, logit $0.3233^{***}$), and it survives firm and year-quarter fixed effects ($0.0078^{***}$, within-$R^2$ 0.003) \citep{harford1999}.`;

const base = { prose: CORRECT, allowedTokens, allowedKeys, props };
let pass = 0, fail = 0;
const check = (name, cond) => { console.log(`  [${cond ? "OK " : "FAIL"}] ${name}`); cond ? pass++ : fail++; };

console.log("== gate spine unit test ==\n");
// 1. correct prose passes cleanly
const r0 = runGates(base);
check("CORRECT prose passes (0 blocks, 0 flags)", r0.pass && r0.flags.length === 0);

// 2. fabricated number -> number gate blocks
const r1 = runGates({ ...base, prose: CORRECT.replace("0.0391", "0.0492") });
check("FABRICATED number 0.0492 -> blocked", !r1.pass && r1.blocks.some(b => b.includes("0.0492") && b.includes("fabricated")));

// 3. star inflation (over-claim significance) -> number gate blocks
const r2 = runGates({ ...base, prose: CORRECT.replace("$-0.0348$", "$-0.0348^{**}$") });
check("STAR-INFLATE -0.0348** -> blocked (over-claims significance)", !r2.pass && r2.blocks.some(b => b.includes("0.0348") && b.includes("stars")));

// 4. honesty violation -> honesty gate blocks
const r3 = runGates({ ...base, prose: CORRECT.replace("a flat null", "suppressed") });
check("HONESTY 'suppressed' -> blocked", !r3.pass && r3.blocks.some(b => b.includes("suppress")));

// 5. unknown citation -> cite gate blocks
const r4 = runGates({ ...base, prose: CORRECT.replace("harford1999", "jensen1986") });
check("BAD CITE jensen1986 -> blocked", !r4.pass && r4.blocks.some(b => b.includes("jensen1986")));

// 6. dropped prop (remove PARA1-b numbers) -> bijection flags
const r5 = runGates({ ...base, prose: CORRECT.split("In binary forward form")[0] });
check("DROPPED PARA1-b -> flagged by bijection", r5.flags.some(f => f.includes("4.5-PARA1-b")));

// 7. broken LaTeX (unbalanced brace) -> latex gate blocks
const r6 = runGates({ ...base, prose: CORRECT.replace("\\citep{harford1999}", "\\citep{harford1999") });
check("BROKEN LaTeX (unbalanced brace) -> blocked", !r6.pass && r6.blocks.some(b => b.includes("brace")));

// 8. a clean magnitude citation (bare value, no stars) must NOT block
const r7 = runGates({ ...base, prose: CORRECT + " The 0.0391 figure is about fifteen percent of a residual standard deviation." });
check("MAGNITUDE cite (bare 0.0391, no stars) -> allowed", r7.pass);

// ---- REALISTIC-PROSE tests (the gate must PASS good prose, not only BLOCK bad) ----
// 9. back-reference: a section number recapped in another sentence (section-level set) -> passes
const r8 = runGates({ ...base, prose: String.raw`Recapping, the binary forward result ($0.0086^{***}$) reinforces the run-up established above.` });
check("BACK-REFERENCE to a section number -> passes", r8.pass);
// 10. rounded figure -> FLAG (audit restores exact), NOT a hard block
const r9 = runGates({ ...base, prose: CORRECT + " The fixed-effects point estimate is about 0.008." });
check("ROUNDING 0.008 (from 0.0078) -> FLAGGED not blocked", r9.pass && r9.flags.some(f => f.includes("0.008") && f.includes("rounded")));
// 11. percentage + 4-digit year -> not coefficient-shaped, must NOT false-block
const r10 = runGates({ ...base, prose: CORRECT + " The deal rate is 2.84\\% across 2002--2018." });
check("PERCENTAGE 2.84% + year 2002 -> not false-blocked", r10.pass);

console.log(`\n${"=".repeat(40)}\n${fail === 0 ? "ALL GATES WORK" : "GATES BROKEN"}: ${pass} pass, ${fail} fail`);
process.exit(fail === 0 ? 0 : 1);
