// Tests for norm.js — the ONE shared literal fold (F1 fix). Locks the exact behaviour
// both gates depend on: fold only invisible/typographic noise, keep every real character.
// Built pure-ASCII via String.fromCharCode (no raw unicode in source).
const { norm, MIN_QUOTE_LEN, containsQuote } = require('./norm');
let pass = 0, fail = 0;
function t(name, cond) { if (cond) { pass++; console.log('  ok   ' + name); } else { fail++; console.log('  FAIL ' + name); } }

const RSQ = String.fromCharCode(0x2019), LDQ = String.fromCharCode(0x201c), RDQ = String.fromCharCode(0x201d);
const EN = String.fromCharCode(0x2013), EM = String.fromCharCode(0x2014), ZWSP = String.fromCharCode(0x200b), BOM = String.fromCharCode(0xfeff);

// --- KEPT: punctuation/digits/symbols are real content ---
t('all-punctuation folds to ITSELF, never to empty', norm('!!!!!') === '!!!!!');
t('empty-fold impossible for real punctuation (the F1 root)', norm('!!!!!').length > 0);
t('markdown kept verbatim', norm('**bold** | `code`') === '**bold** | `code`');
t('digits preserved: 12 !== 13', norm('grew 12%') !== norm('grew 13%'));

// --- FOLDED: only zero-semantic transcription noise ---
t('case folded', norm('The QUICK Brown') === 'the quick brown');
t('whitespace runs + newlines collapse to one space', norm('a\n\n  b\tc') === 'a b c');
t('curly single-quote -> straight', norm(RSQ + 'x' + RSQ) === "'x'");
t('curly double-quote -> straight', norm(LDQ + 'y' + RDQ) === '"y"');
t('en/em/minus dash -> hyphen', norm('a' + EN + 'b' + EM + 'c') === 'a-b-c');
const HY = String.fromCharCode(0x2010), NBH = String.fromCharCode(0x2011);
t('U+2010/2011 hyphen variants -> hyphen', norm('a' + HY + 'b' + NBH + 'c') === 'a-b-c');
t('zero-width + BOM stripped', norm('a' + ZWSP + BOM + 'b') === 'ab');

// --- whitespace-only / empty fold to empty (rejected downstream by the length floor) ---
t('whitespace-only folds to empty', norm('   \n\t  ') === '');
t('a faithful copy of a sentence is stable under fold', norm('Hello,  world!') === 'hello, world!');

t('MIN_QUOTE_LEN is 25', MIN_QUOTE_LEN === 25);

// --- containsQuote: the ONE containment predicate (block grain, split BEFORE fold) ---
const BODY = 'alpha beta gamma delta first paragraph anchor text sits here.\n\nepsilon zeta eta theta second paragraph anchor text sits here.';
t('containsQuote: in-block quote -> null (pass)', containsQuote(BODY, 'alpha beta gamma delta first paragraph anchor') === null);
t('containsQuote: quote in the SECOND block -> null (pass)', containsQuote(BODY, 'epsilon zeta eta theta second paragraph anchor') === null);
t('containsQuote: absent quote -> not literally present', containsQuote(BODY, 'this text is nowhere in the body at all') === 'not literally present');
t('containsQuote: blank-line stitch -> spans blank-line blocks', containsQuote(BODY, 'first paragraph anchor text sits here. epsilon zeta eta theta') === 'spans blank-line blocks');
t('containsQuote: hard-wrap WITHIN one block still passes', containsQuote('one two three\nfour five six seven eight nine ten.', 'three four five six') === null);
t('containsQuote: CRLF body, quote crossing the wrap passes', containsQuote('one two three\r\nfour five six seven.', 'three four five') === null);
t('containsQuote: \\r\\n\\r\\n is a block boundary (stitch fails)', containsQuote('first block text here.\r\n\r\nsecond block text here.', 'first block text here. second block text here.') === 'spans blank-line blocks');
t('containsQuote: whitespace-only line is a block boundary', containsQuote('first block text here.\n   \nsecond block text here.', 'first block text here. second block text here.') === 'spans blank-line blocks');

console.log(`\n${pass} passed, ${fail} failed`);
process.exit(fail ? 1 : 0);
