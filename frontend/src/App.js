import React, { useState, useEffect } from 'react';

const SEVERITY_COLORS = {
  P1: '#ef4444', P2: '#f97316', P3: '#eab308', P4: '#22c55e'
};

const SAMPLE_TICKETS = [
  {
    title: "Supplier sync jobs failing with 429 errors",
    description: "Since 3am UTC our nightly supplier data sync jobs have been failing. The logs show repeated 429 Too Many Requests responses from the API gateway. Approximately 200 suppliers are affected and their compliance data is now stale. The sync jobs were recently reconfigured to run in parallel."
  },
  {
    title: "Compliance report export timing out for enterprise customer",
    description: "Our largest customer (Acme Corp) cannot export their REACH compliance report. The export starts but times out after 30 seconds with no data. They have over 800 suppliers. This was working fine last week. They have a regulatory deadline tomorrow."
  },
  {
    title: "Users getting logged out every 30 minutes",
    description: "Multiple users across different companies are reporting they keep getting logged out and have to sign in again every 30 minutes. This started happening yesterday afternoon. It's affecting productivity and customers are frustrated."
  }
];

export default function App() {
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reports, setReports] = useState([]);
  const [activeTab, setActiveTab] = useState('analyze');
  const [agentStep, setAgentStep] = useState(0);

  const AGENT_STEPS = [
    { icon: '🔍', label: 'Triage Agent', desc: 'Classifying severity & category...' },
    { icon: '📋', label: 'Log Analyst Agent', desc: 'Analyzing error patterns...' },
    { icon: '🧠', label: 'Root Cause Agent', desc: 'RAG search + root cause reasoning...' },
    { icon: '✍️', label: 'Resolution Agent', desc: 'Generating RCA & customer response...' },
  ];

  useEffect(() => {
    if (activeTab === 'reports') fetchReports();
  }, [activeTab]);

  const fetchReports = async () => {
    try {
      const res = await fetch('/api/reports');
      const data = await res.json();
      setReports(data);
    } catch (e) { console.error(e); }
  };

  const analyze = async () => {
    if (!title || !description) return;
    setLoading(true);
    setResult(null);
    setAgentStep(0);

    // Simulate agent step progression
    const stepInterval = setInterval(() => {
      setAgentStep(prev => {
        if (prev >= 3) { clearInterval(stepInterval); return prev; }
        return prev + 1;
      });
    }, 4000);

    try {
      const res = await fetch('/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ title, description })
      });
      const data = await res.json();
      clearInterval(stepInterval);
      setAgentStep(4);
      setResult(data);
    } catch (e) {
      clearInterval(stepInterval);
      alert('Error: ' + e.message);
    } finally {
      setLoading(false);
    }
  };

  const loadSample = (sample) => {
    setTitle(sample.title);
    setDescription(sample.description);
    setResult(null);
  };

  return (
    <div style={{ minHeight: '100vh', background: '#0f172a', color: '#e2e8f0', fontFamily: 'system-ui, sans-serif' }}>
      {/* Header */}
      <div style={{ background: '#1e293b', borderBottom: '1px solid #334155', padding: '16px 32px', display: 'flex', alignItems: 'center', gap: 12 }}>
        <span style={{ fontSize: 24 }}>🤖</span>
        <div>
          <div style={{ fontWeight: 700, fontSize: 18, color: '#f1f5f9' }}>Autonomous Incident Response System</div>
          <div style={{ fontSize: 12, color: '#64748b' }}>Multi-Agent · RAG · Claude API · Supabase pgvector</div>
        </div>
        <div style={{ marginLeft: 'auto', display: 'flex', gap: 8 }}>
          {['analyze', 'reports'].map(tab => (
            <button key={tab} onClick={() => setActiveTab(tab)} style={{
              padding: '6px 16px', borderRadius: 6, border: 'none', cursor: 'pointer', fontSize: 13,
              background: activeTab === tab ? '#3b82f6' : '#334155',
              color: activeTab === tab ? '#fff' : '#94a3b8'
            }}>{tab === 'analyze' ? '🔬 Analyze Ticket' : '📊 Past Reports'}</button>
          ))}
        </div>
      </div>

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '32px 24px' }}>

        {activeTab === 'analyze' && (
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 24 }}>
            {/* Left panel */}
            <div>
              <div style={{ marginBottom: 16 }}>
                <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8, textTransform: 'uppercase', letterSpacing: 1 }}>Quick Load Sample</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                  {SAMPLE_TICKETS.map((s, i) => (
                    <button key={i} onClick={() => loadSample(s)} style={{
                      background: '#1e293b', border: '1px solid #334155', borderRadius: 6,
                      padding: '8px 12px', color: '#94a3b8', cursor: 'pointer', textAlign: 'left', fontSize: 12
                    }}>📌 {s.title}</button>
                  ))}
                </div>
              </div>

              <div style={{ marginBottom: 12 }}>
                <label style={{ fontSize: 12, color: '#64748b', display: 'block', marginBottom: 6 }}>TICKET TITLE</label>
                <input value={title} onChange={e => setTitle(e.target.value)}
                  placeholder="e.g. Supplier sync failing with 429 errors"
                  style={{ width: '100%', background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: '10px 12px', color: '#f1f5f9', fontSize: 14, boxSizing: 'border-box' }} />
              </div>

              <div style={{ marginBottom: 16 }}>
                <label style={{ fontSize: 12, color: '#64748b', display: 'block', marginBottom: 6 }}>TICKET DESCRIPTION</label>
                <textarea value={description} onChange={e => setDescription(e.target.value)}
                  placeholder="Describe the issue in detail..."
                  rows={6} style={{ width: '100%', background: '#1e293b', border: '1px solid #334155', borderRadius: 8, padding: '10px 12px', color: '#f1f5f9', fontSize: 14, resize: 'vertical', boxSizing: 'border-box' }} />
              </div>

              <button onClick={analyze} disabled={loading || !title || !description} style={{
                width: '100%', padding: '12px', borderRadius: 8, border: 'none',
                background: loading ? '#334155' : '#3b82f6', color: '#fff', fontSize: 15, fontWeight: 600, cursor: loading ? 'not-allowed' : 'pointer'
              }}>{loading ? '⚡ Agents Running...' : '🚀 Run Agent Pipeline'}</button>

              {/* Agent Steps */}
              {loading && (
                <div style={{ marginTop: 20, background: '#1e293b', borderRadius: 10, padding: 16 }}>
                  <div style={{ fontSize: 12, color: '#64748b', marginBottom: 12 }}>AGENT PIPELINE</div>
                  {AGENT_STEPS.map((step, i) => (
                    <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 10, opacity: i <= agentStep ? 1 : 0.3 }}>
                      <span style={{ fontSize: 18 }}>{step.icon}</span>
                      <div>
                        <div style={{ fontSize: 13, color: i <= agentStep ? '#f1f5f9' : '#475569', fontWeight: 600 }}>{step.label}</div>
                        <div style={{ fontSize: 11, color: '#64748b' }}>{i === agentStep && loading ? step.desc : i < agentStep ? '✓ Complete' : 'Waiting...'}</div>
                      </div>
                      {i < agentStep && <span style={{ marginLeft: 'auto', color: '#22c55e', fontSize: 12 }}>✓</span>}
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Right panel - Results */}
            <div>
              {result ? (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
                  {/* Severity badge */}
                  <div style={{ background: '#1e293b', borderRadius: 10, padding: 16, borderLeft: `4px solid ${SEVERITY_COLORS[result.triage?.severity] || '#64748b'}` }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 8 }}>
                      <span style={{ background: SEVERITY_COLORS[result.triage?.severity], color: '#fff', padding: '2px 10px', borderRadius: 4, fontSize: 12, fontWeight: 700 }}>{result.triage?.severity}</span>
                      <span style={{ color: '#94a3b8', fontSize: 13 }}>{result.triage?.category}</span>
                      <span style={{ marginLeft: 'auto', color: '#64748b', fontSize: 12 }}>Confidence: {result.root_cause?.confidence}</span>
                    </div>
                    <div style={{ color: '#f1f5f9', fontSize: 14, fontWeight: 600 }}>{result.triage?.summary}</div>
                  </div>

                  {/* Root Cause */}
                  <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                    <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>🧠 ROOT CAUSE (RAG-GROUNDED)</div>
                    <div style={{ color: '#f1f5f9', fontSize: 13, lineHeight: 1.6 }}>{result.root_cause?.rca_summary}</div>
                    {result.similar_incidents?.length > 0 && (
                      <div style={{ marginTop: 10 }}>
                        <div style={{ fontSize: 11, color: '#64748b', marginBottom: 4 }}>📚 Similar past incidents retrieved:</div>
                        {result.similar_incidents.map((inc, i) => (
                          <div key={i} style={{ fontSize: 11, color: '#3b82f6', padding: '2px 0' }}>• {inc.title} ({(inc.similarity * 100).toFixed(0)}% match)</div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Customer response */}
                  <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                    <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>📧 CUSTOMER RESPONSE</div>
                    <div style={{ fontSize: 12, color: '#94a3b8', fontWeight: 600, marginBottom: 4 }}>Subject: {result.resolution?.customer_response?.subject}</div>
                    <div style={{ fontSize: 12, color: '#cbd5e1', lineHeight: 1.6, whiteSpace: 'pre-line' }}>{result.resolution?.customer_response?.body}</div>
                  </div>

                  {/* Eng handoff */}
                  <div style={{ background: '#1e293b', borderRadius: 10, padding: 16 }}>
                    <div style={{ fontSize: 12, color: '#64748b', marginBottom: 8 }}>⚙️ ENGINEERING HANDOFF</div>
                    <div style={{ fontSize: 12, color: '#f1f5f9', marginBottom: 6 }}><strong>Fix time:</strong> {result.resolution?.estimated_fix_time}</div>
                    <div style={{ fontSize: 12, color: '#94a3b8', marginBottom: 4 }}>Investigation checklist:</div>
                    {result.resolution?.engineering_handoff?.investigation_checklist?.map((item, i) => (
                      <div key={i} style={{ fontSize: 12, color: '#cbd5e1', padding: '2px 0' }}>☐ {item}</div>
                    ))}
                  </div>
                </div>
              ) : (
                <div style={{ background: '#1e293b', borderRadius: 10, padding: 40, textAlign: 'center', color: '#475569' }}>
                  <div style={{ fontSize: 48, marginBottom: 12 }}>🤖</div>
                  <div>Submit a ticket to run the agent pipeline</div>
                  <div style={{ fontSize: 12, marginTop: 8 }}>4 specialized AI agents will collaborate to analyze it</div>
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'reports' && (
          <div>
            <div style={{ fontSize: 18, fontWeight: 700, color: '#f1f5f9', marginBottom: 20 }}>Past Incident Reports</div>
            {reports.length === 0 ? (
              <div style={{ color: '#475569', textAlign: 'center', padding: 40 }}>No reports yet. Analyze a ticket first.</div>
            ) : (
              reports.map((r, i) => (
                <div key={i} style={{ background: '#1e293b', borderRadius: 10, padding: 16, marginBottom: 12, borderLeft: `4px solid ${SEVERITY_COLORS[r.severity] || '#64748b'}` }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 6 }}>
                    <span style={{ background: SEVERITY_COLORS[r.severity], color: '#fff', padding: '2px 8px', borderRadius: 4, fontSize: 11, fontWeight: 700 }}>{r.severity}</span>
                    <span style={{ color: '#94a3b8', fontSize: 12 }}>{r.category}</span>
                    <span style={{ marginLeft: 'auto', color: '#475569', fontSize: 11 }}>{new Date(r.created_at).toLocaleString()}</span>
                  </div>
                  <div style={{ color: '#f1f5f9', fontSize: 14, fontWeight: 600 }}>{r.tickets?.title}</div>
                  <div style={{ color: '#64748b', fontSize: 12, marginTop: 4 }}>{r.root_cause_output?.rca_summary?.substring(0, 120)}...</div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
