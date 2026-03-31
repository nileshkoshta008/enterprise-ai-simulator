import React, { useState, useEffect } from 'react';

// Use relative /api for Vercel monorepo routing
const API_BASE = window.location.origin.includes("localhost") ? "http://localhost:8000" : "/api";

function App() {
  const [obs, setObs] = useState(null);
  const [score, setScore] = useState(0);
  const [tier, setTier] = useState("easy");
  const [logs, setLogs] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [done, setDone] = useState(false);

  // Load initial state
  useEffect(() => {
    resetEnv("easy");
  }, []);

  const resetEnv = async (selectTier) => {
    setIsProcessing(true);
    setDone(false);
    setLogs([]);
    setScore(0);
    try {
      const resp = await fetch(`${API_BASE}/reset`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ task_tier: selectTier })
      });
      const data = await resp.json();
      setObs(data);
    } catch (e) {
      console.error(e);
      setLogs(l => [{ message: "Error connecting to backend.", details: "Is the server running?" }, ...l]);
    }
    setIsProcessing(false);
  };

  const autoStep = async () => {
    if (done || !obs || !obs.state) return;
    setIsProcessing(true);
    try {
      const resp = await fetch(`${API_BASE}/auto-step`, { 
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: obs.state })
      });
      const data = await resp.json();
      
      setScore(data.state.total_reward);
      
      if (data.done) {
        setDone(true);
        setObs(null);
        setLogs(l => [{ message: "Queue Completed!", details: `Final Score: ${data.state.total_reward.toFixed(2)}` }, ...l]);
      } else {
        setObs(data.observation);
        setLogs(l => [
          { 
            message: `Processed: ${obs.email_subject}`, 
            details: `Reward: +${data.reward.score} | Penalty: -${data.reward.penalty}` 
          }, 
          ...l
        ]);
      }
    } catch (e) {
      console.error(e);
      setLogs(l => [{ message: "Error in AI Autopilot.", details: "Check console for details." }, ...l]);
    }
    setIsProcessing(false);
  };

  const handleTierChange = (e) => {
    const val = e.target.value;
    setTier(val);
    resetEnv(val);
  };

  return (
    <div className="dashboard-container">
      {/* Main Panel */}
      <div className="glass-panel">
        <header className="header">
          <h1>InBox IQ <span className="badge badge-tier-gold" style={{marginLeft: '1rem'}}>AI Autopilot</span></h1>
          <h2 className="subtitle">Enterprise Data & SLA Triage Multi-Agent Simulation</h2>
        </header>

        {done ? (
          <div className="email-view" style={{display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column'}}>
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
                <polyline points="22 4 12 14.01 9 11.01"></polyline>
            </svg>
            <h2 style={{marginTop: '1rem'}}>Inbox Queue Empty</h2>
            <p className="subtitle">All active tickets have been triaged by the agents.</p>
          </div>
        ) : (
          <div className="email-view">
            {obs ? (
              <>
                <div className="email-header">
                  <h2 className="email-subject">{obs.email_subject}</h2>
                  <div className="email-meta">
                    <span className={`badge badge-tier-${obs.customer_tier}`}>{obs.customer_tier} Tier</span>
                    <span>Elapsed: {obs.time_elapsed_hours}h / SLA: {obs.sla_hours}h</span>
                  </div>
                </div>
                <div className="email-body">
                  {obs.email_body}
                </div>
              </>
            ) : (
              <div className="email-body" style={{opacity: 0.5}}>Loading initial state...</div>
            )}
          </div>
        )}

        <div className="controls">
          <select value={tier} onChange={handleTierChange} disabled={isProcessing}>
            <option value="easy">Easy Queue</option>
            <option value="medium">Medium Queue</option>
            <option value="hard">Hard Queue</option>
          </select>
          
          <button className="secondary" onClick={() => resetEnv(tier)} disabled={isProcessing}>
            Reset Simulation
          </button>
          
          <button onClick={autoStep} disabled={isProcessing || done || !obs}>
            {isProcessing ? "Agents Thinking..." : "Trigger AI Autopilot"}
          </button>
        </div>
      </div>

      {/* Sidebar Panel */}
      <div className="sidebar">
        <div className="metric-card">
          <div className="metric-label">Cumulative Reward</div>
          <div className="metric-value">{score.toFixed(2)}</div>
          <div className="subtitle">Simulation Max: 1.0 / step</div>
        </div>

        <div className="action-log">
          <div className="log-header">Agent Action Log</div>
          <div style={{flexGrow: 1, overflowY: 'auto', padding: '1rem', background: 'rgba(0,0,0,0.1)'}}>
            {logs.length === 0 && <div className="subtitle">Waiting for agent activity...</div>}
            {logs.map((log, i) => (
              <div className="log-item" key={i} style={{animationDelay: `${i * 0.05}s`}}>
                <strong>{log.message}</strong>
                <span>{log.details}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
