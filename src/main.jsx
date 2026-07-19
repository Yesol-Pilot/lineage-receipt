import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import datahubProof from '../evidence-datahub-roundtrip.json';
import './styles.css';

const { evidence, receipt: result } = datahubProof;

function App() {
  const [written, setWritten] = useState(false);
  return <main className="app-shell">
    <aside><div className="brand">LineageReceipt</div><nav><a className="active">⌘&nbsp; Model release evidence</a><a>▣&nbsp; Release decisions</a></nav><div className="side-foot">DataHub adapter<br/>local demo</div></aside>
    <section className="workspace"><header><div><h1>Model release evidence</h1><p>Audit DataHub lineage evidence and verify the decision write-back.</p></div><button className="quiet">⌗&nbsp; Fit to view</button></header>
      <div className="lineage">{evidence.nodes.map((node, index) => <React.Fragment key={node.urn}><article className={'node '+node.state.toLowerCase()}><span className="kind">{node.kind}</span><h2>{node.name}</h2><code>{node.urn}</code><dl><dt>owner</dt><dd>{node.owner || <b>missing</b>}</dd><dt>freshness</dt><dd>{node.freshness}</dd><dt>status</dt><dd>{node.state}</dd></dl></article>{index < evidence.nodes.length - 1 && <div className="edge" aria-label="lineage connection">→</div>}</React.Fragment>)}</div>
      <footer>⌘&nbsp; DataHub lineage read &nbsp;•&nbsp; decision provenance write-back verified</footer>
    </section>
    <aside className="decision"><div><p className="label">Release decision</p><h3>{result.verdict}</h3><p className="summary">Evidence gaps block APPROVE. Resolve the following to re-run the review.</p></div><div className="gaps"><p className="label">Evidence gaps ({result.gaps.length})</p>{result.gaps.map((gap, i) => <div className="gap" key={gap.id}><span>{i + 1}</span><div><strong>{gap.title}</strong><p>{gap.detail}</p></div></div>)}</div><div className="receipt"><h4>Receipt {result.receiptId}</h4><code>model: {evidence.model}<br/>decision: {result.verdict}<br/>digest: sha256:{result.digest.slice(0, 24)}…<br/>write: {evidence.decisionWrite?.customProperty || 'not recorded'}</code><button onClick={() => setWritten(true)} disabled={written}>{written ? 'Receipt acknowledged locally' : 'Acknowledge receipt'}</button><small>{written ? 'Local acknowledgement recorded.' : 'DataHub write readback is captured in the proof fixture.'}</small></div></aside>
  </main>;
}
createRoot(document.getElementById('root')).render(<App/>);
