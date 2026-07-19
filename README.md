# LineageReceipt

An evidence-first ML release agent for the DataHub Agent Hackathon. It reads a model's DataHub lineage, blocks incomplete releases, produces a stable receipt, and is designed to write the decision provenance back to DataHub.

## Current proof

`engine/release-audit.mjs` is a deterministic release rule engine. `scripts/datahub_roundtrip.py` uses the official DataHub SDK to upsert a synthetic ML graph, read its lineage, compute the same receipt, and persist the decision as ML model custom properties. No production credentials are stored in this repository.

## Run

```bash
npm install
npm run dev
npm test
```

## DataHub round-trip proof

Start a DataHub Quickstart instance, then initialize the CLI token outside this
repository (`datahub init --username datahub --password datahub`) and run:

```bash
python scripts/datahub_roundtrip.py --write-decision
```

The command prints JSON containing the DataHub input/output URNs, model training
run, deployment job, deterministic receipt, and the write-back property. The
fixture is synthetic and contains no personal or production data.

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
2. Inspect the four DataHub URNs and the `REPAIR / LR-2842C6` receipt.
3. Run `npm test` and `npm run build` locally.
4. Run `python scripts/datahub_roundtrip.py --write-decision` against a local
   DataHub Quickstart to reproduce the lineage read and decision write-back.

The fixture is synthetic and non-sensitive. The public repository is licensed
under Apache-2.0.
