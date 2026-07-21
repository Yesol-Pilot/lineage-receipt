# DataHub Agent Hackathon adversarial review

Review date: 2026-07-21 19:13 KST  
Scope: current local candidate after adding `scripts/datahub_mcp_audit.py`  
Reviewer: Codex main, static/cold-start review (not an independent Claude verdict)

## Verdict

`REPAIR / NOT READY FOR PUBLIC SUBMISSION`.

The candidate now contains a genuine MCP client path and passes its isolated
transport proof, but the official `mcp-server-datahub==0.6.0` end-to-end read
has not been proven on a live DataHub GMS in this environment. Docker Desktop's
service is stopped and cannot be started by the current Windows user. No
GitHub, Vercel, YouTube, or Devpost public write is authorized until that gate
and an independent review are closed.

## Findings

| ID | Finding | Evidence | Status |
| --- | --- | --- | --- |
| F1 | The old SDK `MetadataChangeProposal` path alone would not satisfy the DataHub MCP requirement. | Current code now starts the official MCP server and calls `get_entities` plus upstream/downstream `get_lineage`; `requirements.txt` pins `mcp-server-datahub==0.6.0`. | RESOLVED |
| F2 | MCP transport and receipt binding must be proven, not described. | Isolated stdio test server: `MCP_READ_SUCCESS`, `REPAIR / LR-4BFBA6`, 3 tool calls, fallback 0; stdout at `D:\00.test\010.tmp-output\lineage-receipt-verification\20260721-datahub-mcp-transport5.stdout.json`. | RESOLVED_FOR_TRANSPORT |
| F3 | Official server package launches, but local GMS is unavailable. | Official server preflight registers read-only tools, then retries `127.0.0.1:18080/config` and receives connection refused; stdout at `D:\00.test\010.tmp-output\lineage-receipt-verification\20260721-datahub-mcp-server-preflight2.stdout.json`. | OPEN P0 |
| F4 | Process-instance fields may not be exposed by every DataHub server version. | Adapter derives process/deployment URNs when present and records `lineageFallbackFields` when it must retain fixture context. | MITIGATED / MUST READ BACK |
| F5 | New-project eligibility must be disclosed. | First repository commit is 2026-07-19, inside the July 6–August 10 submission period; the earlier OpenAI Build Week entry is disclosed in README and release record. | RESOLVED_WITH_DISCLOSURE |
| F6 | Technical compliance is not an award prediction. | No independent Claude review exists for this current HEAD; previous Claude PASS was for an earlier OpenAI candidate. | OPEN |

## Required closeout

1. Start DataHub Quickstart and capture `python scripts/datahub_mcp_audit.py`
   stdout with the official server (no transport override).
2. Re-run `npm test`, `npm run build`, both Python test suites, and the MCP
   adapter against that same candidate; preserve stdout and receipt hashes.
3. Run the independent ClaudeNeo review against the exact current HEAD and
   preserve its stdout. A textual “PASS” without stdout is not evidence.
4. Only after all three gates pass may the public submission fields be updated.

Official references: [DataHub hackathon rules](https://datahub.devpost.com/rules)
and [DataHub MCP Server guide](https://docs.datahub.com/docs/features/feature-guides/mcp).
