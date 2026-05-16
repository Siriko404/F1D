# scripts/claude_mem_integration/canary.py
"""Phase-1 recall-fidelity canary (spec §8). Subcommands: plant | verify.

plant  -> writes ~/.claude-mem/canary/<id>.txt with the sentinel fact
          (the Write is a real tool action -> claude-mem PostToolUse
          captures it deterministically).
verify -> queries claude-mem's own CLI search for the id; PASS iff the
          numeric value is reproduced VERBATIM and the source token is
          present. Appends a ledger row. Exit 0 on PASS, 2 on FAIL.
"""
from __future__ import annotations
import json, subprocess, sys, time, secrets
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEDGER = ROOT / "recall_canary_log.md"
CANDIR = Path.home() / ".claude-mem" / "canary"

def plant() -> str:
    CANDIR.mkdir(parents=True, exist_ok=True)
    cid = time.strftime("%Y%m%d") + "-" + secrets.token_hex(3)
    value = f"{secrets.randbelow(900000)+100000}.{secrets.randbelow(900)+100}"
    text = (f"CANARY {cid}: verification constant = {value}; "
            f"source = spec §8")
    (CANDIR / f"{cid}.txt").write_text(text, encoding="utf-8")
    rec = {"cid": cid, "value": value, "planted_epoch": int(time.time()*1000)}
    (CANDIR / f"{cid}.json").write_text(json.dumps(rec))
    print(f"PLANTED cid={cid} value={value}")
    print("Do other work this session, end it, start a NEW session, then in "
          f"that session call the mem-search MCP tool for 'CANARY {cid}', and "
          "run:  python scripts/claude_mem_integration/canary.py verify "
          f"{cid} --recalled \"<text the MCP tool returned>\"")
    return cid

def _check(text: str, value: str):
    return (value in text), ("spec §8" in text)

def verify(cid: str, recalled: str) -> bool:
    rec = json.loads((CANDIR / f"{cid}.json").read_text())
    value = rec["value"]
    # AUTHORITATIVE: the LLM-path text — what the mem-search MCP tool
    # returned this session (what the model actually sees).
    mcp_verbatim, mcp_sourced = _check(recalled, value)
    mcp_ok = mcp_verbatim and mcp_sourced
    # NON-authoritative cross-check: claude-mem CLI search.
    try:
        cli = subprocess.run(["npx", "claude-mem", "search", f"CANARY {cid}"],
                              capture_output=True, text=True, timeout=120,
                              shell=True).stdout
    except Exception as e:
        cli = f"<<cli error: {e}>>"
    cli_verbatim, cli_sourced = _check(cli, value)
    cli_ok = cli_verbatim and cli_sourced
    split = cli_ok and not mcp_ok          # CLI-pass / MCP-fail = the bug
    ok = mcp_ok and not split
    row = (f"| {time.strftime('%Y-%m-%d %H:%M')} | {cid} | {value} | "
           f"MCP(verbatim={mcp_verbatim},src={mcp_sourced}) "
           f"CLI(verbatim={cli_verbatim},src={cli_sourced}) split={split} | "
           f"{'PASS' if ok else 'FAIL'} |\n")
    if not LEDGER.exists():
        LEDGER.write_text("# Recall-fidelity ledger (spec §8: >=3 PASS, "
                          "0 FAIL; 3 DISTINCT canaries; MCP path "
                          "authoritative)\n\n"
                          "| when | cid | value | detail | result |\n"
                          "|---|---|---|---|---|\n", encoding="utf-8")
    with LEDGER.open("a", encoding="utf-8") as f:
        f.write(row)
    print(("PASS" if ok else "FAIL") + f" cid={cid} mcp_ok={mcp_ok} "
          f"cli_ok={cli_ok} split={split}")
    return ok

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("plant", "verify"):
        print('usage: canary.py plant | verify <cid> --recalled "<mcp text>"')
        sys.exit(1)
    if sys.argv[1] == "plant":
        plant()
    else:
        if "--recalled" not in sys.argv:
            print('verify requires --recalled "<text the mem-search MCP '
                  'tool returned for this cid THIS session>"')
            sys.exit(1)
        _cid = sys.argv[2]
        _recalled = sys.argv[sys.argv.index("--recalled") + 1]
        sys.exit(0 if verify(_cid, _recalled) else 2)
