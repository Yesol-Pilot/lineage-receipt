# LineageReceipt

An evidence-first ML release agent for OpenAI Build Week 2026 (Developer Tools), built with Codex and GPT-5.6. It reads a model's DataHub lineage, blocks incomplete releases, and produces a cryptographic SHA-256 digest over the canonical decision payload before writing decision provenance back to DataHub. The same public artifact was also prepared for the DataHub Agent Hackathon; this page makes the current OpenAI Build Week identity and evidence path explicit.

## Current proof

`engine/release-audit.mjs` is a deterministic release rule engine. `scripts/datahub_roundtrip.py` uses the official DataHub SDK to upsert a synthetic ML graph, read its lineage, compute the same SHA-256 digest over the canonical decision payload, and persist the decision as ML model custom properties. Missing or invalid freshness evidence fails closed as `REPAIR`; the committed fixture is covered by an engine-consistency test. No production credentials are stored in this repository.

## Run

```bash
npm install
npm run dev
npm test
```

## DataHub round-trip proof

The browser UI runs with Node.js 20.19+ (or 22.12+); the round-trip adapter requires Python
3.11+ and the pinned SDK in `requirements.txt`. From a clean checkout:

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Start a DataHub Quickstart instance, then initialize the CLI token outside this
repository (`datahub init --username datahub --password datahub`) and run:

```bash
python scripts/datahub_roundtrip.py --write-decision
```

The command prints JSON containing the DataHub input/output URNs, model training
run, deployment job, deterministic receipt, and the write-back property. The
fixture is synthetic and contains no personal or production data.

The supported judge path is a local DataHub Quickstart on a modern desktop
browser with Docker available. No account credentials are needed for the
synthetic fixture; the CLI token is stored in the user's local DataHub config,
never in this repository.

Licensed under Apache-2.0.

## OpenAI Build Week provenance

LineageReceipt is a developer tool built during the July 2026 OpenAI Build Week
submission period with Codex and GPT-5.6. Codex drove the
implementation loop, browser readback, and regression checks; GPT-5.6 was used
for product framing, rule design, and adversarial review of the evidence
boundary. The key design decision was to keep `REPAIR` visible when owner,
freshness, or rollback evidence is missing instead of manufacturing an
approval.

For judges, the fastest path is:

1. Open the live demo at <https://016lineage-receipt.vercel.app>.
2. On the repaired candidate, inspect the four DataHub URNs and the `REPAIR / LR-46633A` SHA-256 receipt. The public URL is updated only after the independent review and redeploy readback gates pass.
3. Run `npm test` and `npm run build` locally.
4. Run `python scripts/datahub_roundtrip.py --write-decision` against a local
   DataHub Quickstart to reproduce the lineage read and decision write-back.

The Python safety/fixture tests can be run independently with
`python scripts/test_datahub_roundtrip.py` after the pinned SDK install.

The fixture is synthetic and non-sensitive. The public repository is licensed
under Apache-2.0.
