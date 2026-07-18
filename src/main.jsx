import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { auditRelease } from '../engine/release-audit.mjs';
import './styles.css';

const evidence = {
  model: 'churn-risk@1.2.0',
  nodes: [
    { kind: 'Dataset', name: 'Training dataset', urn: 'urn:li:dataset:(urn:li:dataPlatform:s3,churn/training,PROD)', owner: 'platform-data', freshness: '2026-07-18', state: 'OK' },
    { kind: 'FeatureSet', name: 'Feature set', urn: 'urn:li:dataset:(urn:li:dataPlatform:dbt,churn/features,PROD)', owner: 'data-science', freshness: '2026-06-29', state: 'WARN' },
    { kind: 'MLModel', name: 'churn-risk model', urn: 'urn:li:mlModel:churn-risk@1.2.0', owner: null, freshness: '2026-07-18', state: 'REPAIR' },
    { kind: 'Deployment', name: 'Production deployment', urn: 'urn:li:mlModelDeployment:churn-risk-prod', owner: 'ml-platform', freshness: '2026-07-18', state: 'OK' }
  ],
  rollbackRunbook: null
};

function App() {
  const result = useMemo(() => auditRelease(evidence, '2026-07-19'), []);
  const [written, setWritten] = useState(false);
  return <main className="app-shell">
    <aside><div className="brand">LineageReceipt</div><nav><a className="active">⌘&nbsp; Model release evidence</a><a>▣&nbsp; Release decisions</a></nav><div className="side-foot">DataHub adapter<br/>local demo</div></aside>
    <section className="workspace"><header><div><h1>Model release evidence</h1><p>Audit lineage evidence for a model release and write a decision back to DataHub.</p></div><button className="quiet">⌗&nbsp; Fit to view</button></header>
      <div className="lineage">{evidence.nodes.map((node, index) => <React.Fragment key={node.urn}><article className={'node '+node.state.toLowerCase()}><span className="kind">{node.kind}</span><h2>{node.name}</h2><code>{node.urn}</code><dl><dt>owner</dt><dd>{node.owner || <b>missing</b>}</dd><dt>freshness</dt><dd>{node.freshness}</dd><dt>status</dt><dd>{node.state}</dd></dl></article>{index < evidence.nodes.length - 1 && <div className="edge" aria-label="lineage connection">→</div>}</React.Fragment>)}</div>
      <footer>⌘&nbsp; DataHub lineage read &nbsp;•&nbsp; decision provenance written back</footer>
    </section>
    <aside className="decision"><div><p className="label">Release decision</p><h3>{result.verdict}</h3><p className="summary">Evidence gaps block APPROVE. Resolve the following to re-run the review.</p></div><div className="gaps"><p className="label">Evidence gaps ({result.gaps.length})</p>{result.gaps.map((gap, i) => <div className="gap" key={gap.id}><span>{i + 1}</span><div><strong>{gap.title}</strong><p>{gap.detail}</p></div></div>)}</div><div className="receipt"><h4>Receipt {result.receiptId}</h4><code>model: {evidence.model}<br/>decision: {result.verdict}<br/>digest: {result.digest.slice(0, 24)}…</code><button onClick={() => setWritten(true)} disabled={written}>{written ? 'Decision staged locally' : 'Stage decision for DataHub'}</button><small>{written ? 'Write adapter acknowledgement recorded locally.' : 'Immutable receipt • deterministic digest recorded'}</small></div></aside>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
