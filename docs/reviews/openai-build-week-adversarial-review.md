# OpenAI Build Week adversarial review

Review date: 2026-07-19  
Scope: public LineageReceipt submission `1103953`  
Review mode: cold-judge replay and evidence readback; the repaired candidate received `REPAIR / 82` because public redeploy/readback is still pending.

## Verdict

`CONDITIONAL_PASS` for submission compliance and technical reproducibility. The project is submitted and editable until the deadline. The repaired local candidate scored `82`; public push/deploy/readback remains a separate gated step before a final award-strength `PASS`.

## Required-entry checks

| Requirement | Evidence | Status |
| --- | --- | --- |
| Repaired candidate | Local `be68bff` renders the four-node DataHub chain and `REPAIR / LR-46633A` | PASS_CANDIDATE |
| Public demo readback | [live demo](https://016lineage-receipt.vercel.app) remains on the superseded pre-repair `LR-2842C6` until the independent PASS gate | PENDING_REDEPLOY |
| Public source and license | [GitHub repository](https://github.com/Yesol-Pilot/lineage-receipt), Apache-2.0 `LICENSE` | PASS |
| Judge setup path | `README.md` plus pinned `requirements.txt` and npm lockfile | PASS |
| Codex/GPT-5.6 explanation | README, project story, and narrated demo | PASS |
| Demo length and audio | [YouTube demo](https://youtu.be/F5peo6DJD3c), 53.45 seconds, public, H.264/AAC | PASS |
| Developer Tools installation/testing path | Devpost Additional Info and README include Node/Python/DataHub Quickstart commands | PASS |
| `/feedback` Session ID | Devpost Additional Info stores the current Codex thread ID | PASS_WITH_SEMANTIC_RISK |

## Adversarial findings

### F1 — Python SDK setup ambiguity (resolved)

The first public README assumed the judge already had the DataHub SDK. That was a realistic cold-start failure. The repair added `requirements.txt` with `acryl-datahub==1.6.0.15`, a venv install path, and the exact Quickstart/token/round-trip commands. The live replay returned four URNs, three explicit gaps, and `REPAIR / LR-46633A` after the DataHub write-back.

### F2 — JavaScript dependency drift (resolved)

The manifest used `latest` ranges even though the lockfile had concrete versions. The manifest is now pinned to the tested versions (`react`/`react-dom` 19.2.7, `vite` 8.1.5, `@vitejs/plugin-react` 6.0.3), and `npm install --package-lock-only --ignore-scripts` reports no vulnerabilities.

### F3 — Session-ID semantics (open, low/medium risk)

The required field is populated with the Codex thread ID used for the project work and Devpost accepted the submission. Devpost does not expose a public semantic validation of that identifier, so this remains a documentation risk rather than a code defect. Do not replace it with an invented ID.

### F4 — Competitive outcome (open)

Technical compliance is not a prize guarantee. The independent Claude review must score problem sharpness, visible differentiation, demo pacing, and judge confidence. Any `REPAIR` finding becomes the next repair target before the final readback.

### F5 — Independent Claude repair targets (in progress)

The first independent review identified fail-open freshness handling, a misleading padded FNV-1a digest, missing fixture-to-engine binding, and stale dual-hackathon/video identity text. The local repair changes fail closed on freshness, use SHA-256 in both engines, add a fixture-consistency test, and reconcile README/evidence metadata. A follow-up candidate commit `94a6cf3` also makes the evidence navigation and `Fit to view` controls actionable. The second independent review closed the original code blockers; public push/deploy/readback remains explicitly pending.

## Evidence commands

```bash
npm test
npm run build
npm audit --omit=dev --audit-level=high
python scripts/datahub_roundtrip.py --write-decision
```

Official reference: [OpenAI Build Week rules](https://openai.devpost.com/rules).
