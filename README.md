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
