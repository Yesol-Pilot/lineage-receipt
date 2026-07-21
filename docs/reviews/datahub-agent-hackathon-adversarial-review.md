# DataHub Agent Hackathon adversarial review

Review date: 2026-07-21 23:40 KST
Scope: current local candidate after adding `scripts/datahub_mcp_audit.py`  
Reviewer: Codex main, static/cold-start review (not an independent Claude verdict)

## Verdict

`REPAIR / CLOSEOUT PENDING`.

The candidate contains a genuine MCP client path and now has an official live
DataHub GMS readback. The live run is intentionally `MCP_READ_SUCCESS_WITH_WARNINGS`
because three process-instance lineage fields are explicitly fixture-fallback
fields; the visible receipt remains `REPAIR`. No GitHub, Vercel, YouTube, or
Devpost public write is authorized until the current-head independent review
reads this exact live evidence and closes the remaining fallback/eligibility
quality boundary.

## Findings

| ID | Finding | Evidence | Status |
| --- | --- | --- | --- |
| F1 | The old SDK `MetadataChangeProposal` path alone would not satisfy the DataHub MCP requirement. | Current code now starts the official MCP server and calls `get_entities` plus upstream/downstream `get_lineage`; `requirements.txt` pins `mcp-server-datahub==0.6.0`. | RESOLVED |
| F2 | MCP transport and receipt binding must be proven, not described. | Isolated stdio test server: `MCP_READ_SUCCESS`, `REPAIR / LR-4BFBA6`, 3 tool calls, fallback 0; stdout at `D:\00.test\010.tmp-output\lineage-receipt-verification\20260721-datahub-mcp-transport5.stdout.json`. | RESOLVED_FOR_TRANSPORT |
| F3 | Official server package must be proven against a live GMS. | Official default `uvx mcp-server-datahub@0.6.0` readback against `127.0.0.1:18080`: `MCP_READ_SUCCESS_WITH_WARNINGS`, server `datahub` 3.4.4, protocol `2025-11-25`, 3 tool calls, stdout at `D:\00.test\010.tmp-output\lineage-receipt-verification\20260721-datahub-mcp-official-live-v5.stdout.json`. | RESOLVED_WITH_WARNINGS |
| F4 | Process-instance fields may not be exposed by every DataHub server version. | Adapter now parses DataHub lineage `facets.inputs/outputs`; only `modelDeployments` remains explicitly fixture-fallback in the live receipt LR-520F80. | MITIGATED / ONE EXPLICIT FALLBACK |
| F5 | New-project eligibility must be disclosed. | First repository commit is 2026-07-19, inside the July 6–August 10 submission period; the earlier OpenAI Build Week entry is disclosed in README and release record. | RESOLVED_WITH_DISCLOSURE |
| F6 | Technical compliance is not an award prediction. | ClaudeNeo static-only review of `ad0f6d8` returned `REPAIR / 60`; stdout at `D:\00.test\010.tmp-output\claudeneo-reviews\lineage-receipt-datahub-re-review-ad0f6d8-continuation.stdout.txt`. A fresh review against the official-live fixture is still required. | OPEN P0 |

## Required closeout

1. Re-run `npm test`, `npm run build`, both Python test suites, and the MCP
   adapter against the exact candidate after the official-live fixture update;
   preserve stdout and receipt hashes.
2. Run the independent ClaudeNeo review against that exact current HEAD and
   preserve its stdout. A textual “PASS” without stdout is not evidence.
3. Resolve or explicitly accept the three `lineageFallbackFields` only if the
   independent reviewer finds the warning acceptable under the rules.
4. Only after all three gates pass may the public submission fields be updated.

Official references: [DataHub hackathon rules](https://datahub.devpost.com/rules)
and [DataHub MCP Server guide](https://docs.datahub.com/docs/features/feature-guides/mcp).
