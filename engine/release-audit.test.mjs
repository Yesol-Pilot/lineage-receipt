import test from 'node:test';
import assert from 'node:assert/strict';
import { auditRelease } from './release-audit.mjs';

const base = { model: 'm@1', nodes: [{ kind: 'FeatureSet', freshness: '2026-06-01' }, { kind: 'MLModel', owner: null }], rollbackRunbook: null };
test('blocks release when DataHub evidence has three gaps', () => { const r = auditRelease(base, '2026-07-19'); assert.equal(r.verdict, 'REPAIR'); assert.equal(r.gaps.length, 3); });
test('approves a complete release and keeps receipt stable', () => { const v = { model: 'm@1', nodes: [{ kind: 'FeatureSet', freshness: '2026-07-19' }, { kind: 'MLModel', owner: 'ml' }], rollbackRunbook: 'urn:li:document:rollback' }; const a = auditRelease(v, '2026-07-19'); assert.equal(a.verdict, 'APPROVE'); assert.equal(a.receiptId, auditRelease(v, '2026-07-19').receiptId); });
