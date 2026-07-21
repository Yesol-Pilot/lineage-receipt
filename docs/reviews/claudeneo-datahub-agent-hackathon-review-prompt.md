# ClaudeNeo independent DataHub hackathon review prompt

You are an independent, skeptical judge for the DataHub Agent Hackathon.
Review the exact current repository HEAD. Do not trust prior Codex claims,
existing `PASS` language, or the fact that the project was submitted to another
hackathon. This is a read-only review: do not edit, commit, push, deploy,
publish, or log into any account.

## Objective

Decide whether the current LineageReceipt artifact is eligible, working, and
competitive for the **Production ML Agents** category. Score the artifact and
the evidence, not the effort spent building it.

## Required checks

1. Read `README.md`, `requirements.txt`, `package.json`, `engine/release-audit.mjs`,
   `scripts/datahub_roundtrip.py`, `scripts/datahub_mcp_audit.py`,
   `scripts/test_datahub_mcp_audit.py`, `evidence-datahub-roundtrip.json`,
   `LICENSE`, and `docs/reviews/datahub-agent-hackathon-adversarial-review.md`.
2. Verify the project uses the official `mcp-server-datahub` over MCP, advertises
   and calls `get_entities` and both directions of `get_lineage`, keeps tokens
   out of stdout/repository content, and binds the returned metadata to the
   deterministic receipt.
3. Check the cold-start setup: pinned dependencies, DataHub Quickstart/GMS
   configuration, failure behavior when GMS is unavailable, and whether a
   judge can reproduce the proof without private credentials.
4. Check eligibility under the official “New Projects Only” rule. The first
   commit is 2026-07-19 within the July 6–August 10 submission period; the prior
   OpenAI Build Week work is disclosed. Treat any hidden pre-existing work as a
   blocker.
5. Evaluate visible product quality, technical differentiation, real-world ML
   usefulness, and whether the demo proves more than metadata display.
6. Treat the absence of a live official GMS stdout artifact as an open blocker;
   the isolated transport-override test is not equivalent to the official
   end-to-end proof.

## Output contract

Return only a structured review with these exact sections:

- `VERDICT`: `PASS`, `REPAIR`, or `HOLD`
- `SCORE`: integer 0-100
- `PRIZE_CASE`: three sentences on why a judge would or would not shortlist it
- `BLOCKING_FINDINGS`: numbered list with severity, evidence path, and exact repair
- `NON_BLOCKING_FINDINGS`: numbered list with severity and evidence path
- `REQUIRED_REVIEW_EVIDENCE`: the smallest evidence set needed to close each blocker
- `REVIEW_BOUNDARY`: what you could not verify and why

Use `REPAIR` for any rule, MCP integration, or end-to-end evidence blocker. Use
`PASS` only if the current HEAD is both eligible and credible as a prize
contender with no missing official-GMS proof. Do not edit files or create a
public write as part of the review.
