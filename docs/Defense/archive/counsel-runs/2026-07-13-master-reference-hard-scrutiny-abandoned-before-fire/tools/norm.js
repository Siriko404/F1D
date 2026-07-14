// norm.js — the ONE text fold + ONE containment predicate, shared by journal.js
// (write-time) and verify-readback.js (read-back) so both checks are identical BY
// CONSTRUCTION. A drift between them was the F1 fake-quote hole: journal checked raw
// length, the matcher stripped punctuation, so a quote could collapse to "" and match all.
//
// Prove the quote is LITERALLY in the source. Fold ONLY zero-semantic transcription
// noise (things a faithful copy legitimately differs on): Unicode NFKC, invisible format
// chars, curly->straight quotes/dashes, case, whitespace runs. KEEP everything real —
// punctuation, digits, markdown (**, |, `, #). So a fabricated all-punctuation quote
// stays literal (can't collapse to "" and match all), and reformatting fails, by design.

const HIDDEN = new RegExp('[' + [0x00ad, 0x200b, 0x200c, 0x200d, 0xfeff].map((c) => String.fromCharCode(c)).join('') + ']', 'g');
const SQUOTE = new RegExp('[' + [0x2018, 0x2019, 0x201a, 0x2032].map((c) => String.fromCharCode(c)).join('') + ']', 'g');
const DQUOTE = new RegExp('[' + [0x201c, 0x201d, 0x201e, 0x2033].map((c) => String.fromCharCode(c)).join('') + ']', 'g');
const DASH = new RegExp('[' + [0x2010, 0x2011, 0x2013, 0x2014, 0x2212].map((c) => String.fromCharCode(c)).join('') + ']', 'g');

function norm(s) {
  return String(s)
    .normalize('NFKC')
    .replace(HIDDEN, '')
    .replace(SQUOTE, "'")
    .replace(DQUOTE, '"')
    .replace(DASH, '-')
    .toLowerCase()
    .replace(/\s+/g, ' ')
    .trim();
}

// Minimum locatable content, measured on FOLDED text (can't be gamed by padding with
// fold-away chars), SAME constant both gates use. 25 folded chars ~ a short phrase;
// shorter fragments appear everywhere and aren't uniquely locatable (v1 lesson M12).
const MIN_QUOTE_LEN = 25;

// containsQuote — the shared containment predicate. Grain is a blank-line-delimited
// block: the folded quote must sit inside ONE block of the RAW source. Blocks are split
// BEFORE folding — norm() collapses blank lines, so a post-fold split has nothing left
// to split on (the trap here). Kills blank-line stitching; whole-file relocation shrinks
// to block relocation (documented residual).
// Returns: null | 'not literally present' | 'spans blank-line blocks' (present in the
// file but no single block — an honest cross-paragraph quote is one item per block).
function containsQuote(rawBody, quote) {
  const nq = norm(quote);
  const body = String(rawBody).replace(/\r\n/g, '\n');
  for (const block of body.split(/\n\s*\n/)) if (norm(block).includes(nq)) return null;
  return norm(body).includes(nq) ? 'spans blank-line blocks' : 'not literally present';
}

module.exports = { norm, MIN_QUOTE_LEN, containsQuote };
