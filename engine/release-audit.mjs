import { createHash } from 'node:crypto';

export function auditRelease(evidence, today) {
  if (!today) throw new TypeError('today is required for a deterministic release audit');
  const gaps = [];
  const nodes = evidence.nodes ?? [];
  const model = nodes.find((node) => node.kind === 'MLModel');
  const feature = nodes.find((node) => node.kind === 'FeatureSet');
  if (!model?.owner) gaps.push({ id: 'missing-owner', title: 'Missing owner', detail: `${evidence.model} has no owner recorded in DataHub.` });
  const freshnessAge = feature?.freshness ? daysBetween(feature.freshness, today) : null;
  if (freshnessAge === null) gaps.push({ id: 'missing-freshness', title: 'Missing freshness evidence', detail: 'Feature set freshness is missing or invalid in DataHub.' });
  else if (freshnessAge > 7) gaps.push({ id: 'stale-feature', title: 'Stale feature freshness', detail: `Feature set freshness is ${feature.freshness}; it is older than 7 days.` });
  if (!evidence.rollbackRunbook) gaps.push({ id: 'no-rollback', title: 'No rollback runbook', detail: 'No rollback runbook is linked to the production deployment.' });
  const canonical = JSON.stringify({ model: evidence.model, gaps: gaps.map((gap) => gap.id) });
  const digest = stableFingerprint(canonical);
  return { verdict: gaps.length ? 'REPAIR' : 'APPROVE', gaps, digest, receiptId: `LR-${digest.slice(0, 6).toUpperCase()}` };
}
function daysBetween(from, to) {
  const fromMs = Date.parse(from);
  const toMs = Date.parse(to);
  if (Number.isNaN(fromMs) || Number.isNaN(toMs)) return null;
  return Math.round((toMs - fromMs) / 86400000);
}
function stableFingerprint(value) {
  return createHash('sha256').update(value, 'utf8').digest('hex');
}
