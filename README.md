# LineageReceipt

An evidence-first ML release agent for the DataHub Agent Hackathon. It reads a model's DataHub lineage, blocks incomplete releases, produces a stable receipt, and is designed to write the decision provenance back to DataHub.

## Current proof

`engine/release-audit.mjs` is a deterministic release rule engine. The browser UI visualizes the same receipt and exposes the write-back handoff. The next integration step is a local DataHub Quickstart fixture and GraphQL write adapter; no production credentials are stored in this repository.

## Run

```bash
npm install
npm run dev
npm test
```

Licensed under Apache-2.0.
