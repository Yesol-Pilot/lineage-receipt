# Repository Governance Contract

Policy ID: `ng-repo-governance/1.0.0`
Last reviewed: 2026-08-27

## Identity

- Repository: `Yesol-Pilot/lineage-receipt`
- Lifecycle class: `service-evidence-lineage`
- Current owner: `Yesol-Pilot`
- Intended owner: `NeoGenesisAI`
- Canonical branch: `master`
- Canonical-branch target: `main`
- Visibility: `public`
- Production status: `UNKNOWN`
- Transfer state: `REQUIRED`

`UNKNOWN` means not independently verified and must never be reported as PASS.

## Purpose and current risk

Lineage Receipt is a public company evidence-lineage surface. Its records must prove where an artifact, decision, claim, or release came from without allowing mutable, forged, stale, self-approved, or privacy-unsafe receipts.

- Schema, canonicalization, hash and signature rules, actor identities, trust roots, revocation, consumers, hosting, and migration remain `UNKNOWN`.
- A lineage chain that contains hashes but does not verify bytes, parent identity, actor independence, or semantic constraints is insufficient.
- Receipt reuse, branch movement, abbreviated SHAs, mutable URLs, duplicate JSON keys, unknown fields, and unbounded timestamps must fail closed.
- Public records must not expose credentials, private content, personal paths, device identifiers, or sensitive account data.

## Required remediation

- [ ] Document record schemas, node and edge semantics, canonical bytes, full object IDs, actor roles, signatures, freshness, revocation, retention, and consumers.
- [ ] Run full-history secret, dependency, license, public-fixture, and privacy audits.
- [ ] Add strict parser, duplicate and unknown field, full SHA, tree and artifact binding, parent-chain, cycle, stale, replay, self-review, signature, revocation, redaction, availability, migration, and rollback tests.
- [ ] Separate lineage writer, deterministic verifier, dissent reviewer, signer, publisher, and consumer approval.
- [ ] Normalize `master` to `main` only after consumers, public URLs, and deployment integrations are verified.
- [ ] Transfer the repository to `NeoGenesisAI` while preserving redirects and consumer compatibility.

## Pull-request and branch rules

- One task, one branch, one isolated worktree.
- Draft inactivity limit: 14 days; maximum stack depth: 3.
- Ready WIP limit: 5; Draft WIP limit: 10.
- PRs declare schema, trust, actor, consumer compatibility, privacy, migration, and rollback impact.
- Review conversations resolve before squash merge.
- Canonical branches are not force-pushed or deleted.

## Exit criteria

The repository becomes `TRANSFERRED_COMPLIANT` only when organization ownership, immutable lineage semantics, exact-byte and parent validation, independent verification, signatures and revocation, public privacy, consumer migration, and rollback are proven.

The presence of this file alone is not compliance.
