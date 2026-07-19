import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { auditRelease } from './release-audit.mjs';

const base = { model: 'm@1', nodes: [{ kind: 'FeatureSet', freshness: '2026-06-01' }, { kind: 'MLModel', owner: null }], rollbackRunbook: null };
test('blocks release when DataHub evidence has three gaps', () => { const r = auditRelease(base, '2026-07-19'); assert.equal(r.verdict, 'REPAIR'); assert.equal(r.gaps.length, 3); });
test('approves a complete release and keeps receipt stable', () => { const v = { model: 'm@1', nodes: [{ kind: 'FeatureSet', freshness: '2026-07-19' }, { kind: 'MLModel', owner: 'ml' }], rollbackRunbook: 'urn:li:document:rollback' }; const a = auditRelease(v, '2026-07-19'); assert.equal(a.verdict, 'APPROVE'); assert.equal(a.receiptId, auditRelease(v, '2026-07-19').receiptId); });
test('fails closed when feature freshness is missing, invalid, or absent', () => {
  for (const feature of [{ kind: 'FeatureSet' }, { kind: 'FeatureSet', freshness: 'not-a-date' }]) {
    const result = auditRelease({ model: 'm@1', nodes: [feature, { kind: 'MLModel', owner: 'ml' }], rollbackRunbook: 'urn:li:document:rollback' }, '2026-07-19');
    assert.equal(result.verdict, 'REPAIR');
    assert.deepEqual(result.gaps.map((gap) => gap.id), ['missing-freshness']);
  }
  const absent = auditRelease({ model: 'm@1', nodes: [{ kind: 'MLModel', owner: 'ml' }], rollbackRunbook: 'urn:li:document:rollback' }, '2026-07-19');
  assert.deepEqual(absent.gaps.map((gap) => gap.id), ['missing-freshness']);
});
test('committed DataHub fixture is produced by the release engine', () => {
  const fixture = JSON.parse(readFileSync(new URL('../evidence-datahub-roundtrip.json', import.meta.url), 'utf8'));
  assert.deepEqual(auditRelease(fixture.evidence, '2026-07-19'), fixture.receipt);
});
