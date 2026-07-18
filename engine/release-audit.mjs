export function auditRelease(evidence, today = new Date().toISOString().slice(0, 10)) {
  const gaps = [];
  const model = evidence.nodes.find((node) => node.kind === 'MLModel');
  const feature = evidence.nodes.find((node) => node.kind === 'FeatureSet');
  if (!model?.owner) gaps.push({ id: 'missing-owner', title: 'Missing owner', detail: `${evidence.model} has no owner recorded in DataHub.` });
  if (feature && daysBetween(feature.freshness, today) > 7) gaps.push({ id: 'stale-feature', title: 'Stale feature freshness', detail: `Feature set freshness is ${feature.freshness}; it is older than 7 days.` });
  if (!evidence.rollbackRunbook) gaps.push({ id: 'no-rollback', title: 'No rollback runbook', detail: 'No rollback runbook is linked to the production deployment.' });
  const canonical = JSON.stringify({ model: evidence.model, gaps: gaps.map((gap) => gap.id) });
  const digest = stableFingerprint(canonical);
  return { verdict: gaps.length ? 'REPAIR' : 'APPROVE', gaps, digest, receiptId: `LR-${digest.slice(0, 6).toUpperCase()}` };
}
function daysBetween(from, to) { return Math.round((Date.parse(to) - Date.parse(from)) / 86400000); }
function stableFingerprint(value) {
  let hash = 0x811c9dc5;
  for (let i = 0; i < value.length; i += 1) {
    hash ^= value.charCodeAt(i);
    hash = Math.imul(hash, 0x01000193) >>> 0;
  }
  return hash.toString(16).padStart(8, '0').repeat(8);
}
