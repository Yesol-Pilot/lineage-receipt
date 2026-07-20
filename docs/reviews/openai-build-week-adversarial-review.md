# OpenAI Build Week adversarial review

Review date: 2026-07-19  
Scope: public LineageReceipt submission `1103953`  
Review mode: cold-judge replay and evidence readback; the independent ClaudeNeo re-review of `f28ef46` returned `PASS / 85` with no blockers. Public GitHub, Vercel, YouTube, and Devpost readbacks now agree with the repaired receipt.

## Verdict

`PASS` for the repaired artifact and public submission state: independent ClaudeNeo found no blockers; local execution reproduced the full test/build/audit path plus a fresh DataHub Quickstart write/readback; and the public source, live demo, video, and Devpost page all read back the current receipt `REPAIR / LR-DC2240`.

## Required-entry checks

| Requirement | Evidence | Status |
| --- | --- | --- |
| Repaired candidate | `f28ef46` renders the four-node DataHub chain and `REPAIR / LR-DC2240` with an evidence-bound SHA-256 receipt | PASS |
| Public demo readback | [live demo](https://016lineage-receipt.vercel.app) renders four DataHub URNs and `REPAIR / LR-DC2240`; old `LR-2842C6` is absent | PASS |
| Public source and license | [GitHub repository](https://github.com/Yesol-Pilot/lineage-receipt) is at public HEAD `e7259a3`; Apache-2.0 `LICENSE` is public | PASS |
| Judge setup path | Public README, current live screenshot, pinned `requirements.txt`, npm lockfile, and Devpost Additional Info contain Node/Python/DataHub Quickstart commands | PASS |
| Codex/GPT-5.6 explanation | Public README/story and the refreshed narrated demo identify Codex and GPT-5.6 collaboration | PASS |
| Demo length and audio | [YouTube demo](https://youtu.be/8LXw5IlHrzU), ~69 seconds, public H.264/AAC; title and receipt `LR-DC2240` read back via oEmbed | PASS |
| Developer Tools installation/testing path | Devpost Additional Info retains Node/Python/DataHub Quickstart commands and the current public repo/live URLs | PASS |
| `/feedback` Session ID | Devpost Additional Info stores the current Codex thread ID | PASS_WITH_SEMANTIC_RISK |

## Adversarial findings

### F1 — Python SDK setup ambiguity (resolved)

The first public README assumed the judge already had the DataHub SDK. That was a realistic cold-start failure. The repair added `requirements.txt` with `acryl-datahub==1.6.0.15`, a venv install path, and the exact Quickstart/token/round-trip commands. On 2026-07-19 22:02 KST, the local healthy DataHub Quickstart produced four URNs, three explicit gaps, `REPAIR / LR-DC2240`, `readbackDigest=dc2240…`, and exit 0; the stdout is preserved at `D:\00.test\010.tmp-output\lineagereceipt-verification\f28ef46-datahub-roundtrip.txt`. The current round-trip fails closed if the persisted verdict, receipt ID, or digest differs from the computed receipt.

### F2 — JavaScript dependency drift (resolved)

The manifest used `latest` ranges even though the lockfile had concrete versions. The manifest is now pinned to the tested versions (`react`/`react-dom` 19.2.7, `vite` 8.1.5, `@vitejs/plugin-react` 6.0.3), and `npm install --package-lock-only --ignore-scripts` reports no vulnerabilities.

### F3 — Session-ID semantics (open, low/medium risk)

The required field is populated with the Codex thread ID used for the project work and Devpost accepted the submission. Devpost does not expose a public semantic validation of that identifier, so this remains a documentation risk rather than a code defect. Do not replace it with an invented ID.

### F4 — Competitive outcome (reviewed)

Technical compliance is not a prize guarantee. ClaudeNeo independently scored the repaired candidate `PASS / 85`: shortlist-worthy for its honest, deterministic evidence boundary. The stale video identity was refreshed and publicly read back; remaining concerns are non-blocking scope/competition risks.

### F5 — Independent Claude repair targets (resolved for local candidate)

The first independent review identified fail-open freshness handling, a misleading padded FNV-1a digest, missing fixture-to-engine binding, and stale dual-hackathon/video identity text. The local repair changes fail closed on freshness, use SHA-256 in both engines, bind the digest to the normalized evidence snapshot plus gaps, add fixture/digest-binding tests, and reconcile README/evidence metadata. Candidate `94a6cf3` made the evidence navigation and `Fit to view` controls actionable; candidate `c7012bb` additionally binds receipts to evidence content; candidate `c835eb1` verifies persisted digest equality; and `f28ef46` truthfully separates public baseline state. ClaudeNeo's preserved stdout (`D:\00.test\010.tmp-output\claudeneo-reviews\lineage-receipt-independent-re-review3-20260719-215003.txt`) returned `PASS / 85` with no blockers. The final public readback confirms the repaired state across GitHub, Vercel, YouTube, and Devpost.

## Evidence commands

```bash
npm test
npm run build
npm audit --omit=dev --audit-level=high
python scripts/datahub_roundtrip.py --write-decision
```

Local execution evidence was captured at `f28ef46`: `D:\00.test\010.tmp-output\lineagereceipt-verification\f28ef46-npm-test.txt` (5/5), `f28ef46-python-test.txt` (4/4), `f28ef46-vite-build.txt`, `f28ef46-npm-audit.txt`, and `f28ef46-datahub-roundtrip.txt` (exit 0 with persisted digest equality). Public docs and the judge screenshot are now at GitHub HEAD `e7259a3`; the same screenshot is visible in the Devpost image gallery.

Official reference: [OpenAI Build Week rules](https://openai.devpost.com/rules).
