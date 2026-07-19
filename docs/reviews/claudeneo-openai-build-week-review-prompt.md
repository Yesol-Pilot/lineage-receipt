# ClaudeNeo independent judge review prompt

You are an independent, skeptical judge for OpenAI Build Week 2026. Review the
LineageReceipt submission at the current repository HEAD. Do not trust prior
Codex claims or the existing `PASS` language. This is a read-only review: do
not edit files, commit, push, deploy, or publish anything.

## Objective

Decide whether LineageReceipt is merely compliant or genuinely competitive for
an OpenAI Build Week Developer Tools prize. Score the actual artifact, not the
effort spent building it.

## Required checks

1. Read `README.md`, `requirements.txt`, `package.json`, `package-lock.json`,
   `engine/release-audit.mjs`, `scripts/datahub_roundtrip.py`, the React UI,
   `LICENSE`, `evidence-datahub-roundtrip.json`, and
   `docs/reviews/openai-build-week-adversarial-review.md`.
2. Verify that the install and test path is complete, deterministic, and
   realistic for a cold-start judge.
3. Verify that the deterministic engine is safe: no hidden approval,
   timestamp-sensitive false PASS, digest mismatch, or misleading receipt.
4. Evaluate visible product quality, information hierarchy, differentiation,
   problem sharpness, and whether a judge understands the value within the
   first 30 seconds of the demo.
5. Evaluate the public demo/readback claims against the repository evidence.
6. Treat the `/feedback` Session ID as a semantic risk unless the repository
   provides evidence that it is the actual Codex project session. Never invent
   an ID.

## Output contract

Return only a structured review with these exact sections:

- `VERDICT`: `PASS`, `REPAIR`, or `HOLD`
- `SCORE`: integer 0-100
- `PRIZE_CASE`: three sentences on why a judge would or would not shortlist it
- `BLOCKING_FINDINGS`: numbered list with severity, evidence path, and exact repair
- `NON_BLOCKING_FINDINGS`: numbered list with severity and evidence path
- `REQUIRED_REVIEW_EVIDENCE`: the smallest evidence set needed to close each blocker
- `REVIEW_BOUNDARY`: what you could not verify and why

Use `REPAIR` for any blocker that could materially reduce judging strength or
rule compliance. Use `PASS` only when the artifact is both compliant and
credible as a prize contender. Do not soften findings because the project is
already submitted.
