import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:7860' : '/api';

export default function DashboardPage() {
  const [obs, setObs] = useState(null);
  const [score, setScore] = useState(0);
  const [tier, setTier] = useState('easy');
  const [logs, setLogs] = useState([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [done, setDone] = useState(false);

  const navigate = useNavigate();

  useEffect(() => {
    resetEnv('easy');
  }, []);

  const resetEnv = async (selectTier) => {
    setIsProcessing(true);
    setDone(false);
    setLogs([]);
    setScore(0);

    try {
      const resp = await fetch(`${API_BASE}/reset`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ task_tier: selectTier }),
      });
      const data = await resp.json();
      setObs(data);
    } catch (e) {
      console.error(e);
      addLog('Connection Error', 'Backend server is unreachable.');
    } finally {
      setIsProcessing(false);
    }
  };

  const addLog = (message, details) => {
    setLogs((prev) => [{ message, details, time: new Date().toLocaleTimeString() }, ...prev]);
  };

  const autoStep = async () => {
    if (done || !obs || !obs.state || isProcessing) return;
    setIsProcessing(true);

    try {
      const resp = await fetch(`${API_BASE}/auto-step`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ state: obs.state }),
      });
      const data = await resp.json();

      setScore(data.state.total_reward);

      if (data.done) {
        setDone(true);
        setObs(null);
        addLog('Session Complete', `Final score achieved: ${data.state.total_reward.toFixed(2)}`);
      } else {
        const subject = obs?.email_subject ?? 'Request';
        setObs(data.observation);
        addLog(`Processed: ${subject.substring(0, 25)}...`, `R: +${data.reward.score.toFixed(2)} | P: -${data.reward.penalty.toFixed(2)}`);
      }
    } catch (e) {
      console.error(e);
      addLog('Execution Error', 'Autonomous pipeline failed.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleTierChange = (e) => {
    const value = e.target.value;
    setTier(value);
    resetEnv(value);
  };

  const handleLogout = () => {
    localStorage.removeItem('isAuthenticated');
    navigate('/login');
  };

  return (
    <div className="dashboard-layout">
      <header className="card header-nav">
        <div className="brand-section">
          <h1 className="brand-font" style={{ color: 'var(--accent-primary)', fontSize: '1.5rem' }}>InboxIQ <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}>| Simulation Portal</span></h1>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
          <select className="select-input" value={tier} onChange={handleTierChange} disabled={isProcessing}>
            <option value="easy">Easy Queue</option>
            <option value="medium">Medium Queue</option>
            <option value="hard">Hard Queue</option>
          </select>
          <button className="btn btn-secondary" onClick={() => resetEnv(tier)} disabled={isProcessing}>
            Refresh
          </button>
          <button className="btn btn-primary" onClick={autoStep} disabled={isProcessing || done || !obs}>
            {isProcessing ? 'Processing...' : 'Run Auto-Triage'}
          </button>
          <button className="btn btn-ghost" onClick={handleLogout}>Logout</button>
        </div>
      </header>

      <section className="metrics-row">
        <div className="card metric-card">
          <span className="metric-label">Cumulative Reward</span>
          <div className="metric-value" style={{ color: 'var(--accent-primary)' }}>{score.toFixed(2)}</div>
        </div>
        <div className="card metric-card">
          <span className="metric-label">Active Scenario</span>
          <div className="metric-value" style={{ textTransform: 'capitalize' }}>{tier}</div>
        </div>
        <div className="card metric-card">
          <span className="metric-label">System Health</span>
          <div className="metric-value" style={{ color: 'var(--color-success)', fontSize: '1.25rem' }}>Optimized</div>
        </div>
      </section>

      <main className="main-content">
        <section className="card simulation-panel">
          <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
            <h2 className="brand-font" style={{ fontSize: '1.25rem' }}>Current Observation</h2>
            {obs && (
              <span className={`badge badge-${obs.customer_tier}`}>
                {obs.customer_tier} tier
              </span>
            )}
          </header>

          {done ? (
            <div style={{ textAlign: 'center', padding: '4rem 2rem' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✅</div>
              <h3 style={{ marginBottom: '0.5rem' }}>Queue Fully Processed</h3>
              <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>The simulation for this tier has concluded successfully.</p>
              <button className="btn btn-primary" onClick={() => resetEnv(tier)}>Begin New Session</button>
            </div>
          ) : obs ? (
            <div className="email-view">
              <div className="email-header">
                <h3 style={{ fontSize: '1.5rem', marginBottom: '0.5rem' }}>{obs.email_subject}</h3>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', display: 'flex', gap: '1.5rem' }}>
                  <span>SLA: <strong>{obs.sla_hours} hours</strong></span>
                  <span>Elapsed: <strong>{obs.time_elapsed_hours.toFixed(1)} hours</strong></span>
                  <span style={{ color: obs.time_elapsed_hours > obs.sla_hours ? 'var(--color-danger)' : 'var(--color-success)', fontWeight: 600 }}>
                    {obs.time_elapsed_hours > obs.sla_hours ? 'SLA BREACHED' : 'WITHIN SLA'}
                  </span>
                </div>
              </div>
              <div className="email-body">
                {obs.email_body}
              </div>
              
              <footer style={{ marginTop: '2rem' }}>
                <button className="btn btn-primary" style={{ width: '100%', padding: '1rem' }} onClick={autoStep} disabled={isProcessing}>
                  {isProcessing ? 'AI Pipeline Executing...' : 'Trigger Autonomous Decision'}
                </button>
              </footer>
            </div>
          ) : (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
              Awaiting environment initialisation...
            </div>
          )}
        </section>

        <aside className="sidebar-panel">
          <div className="card log-panel">
            <header className="log-header">
              Activity Stream
            </header>
            <div className="log-list">
              {logs.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  No activity recorded yet.
                </div>
              ) : (
                logs.map((log, index) => (
                  <div key={index} className="log-item">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                      <strong style={{ fontSize: '0.8rem' }}>{log.message}</strong>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{log.time}</span>
                    </div>
                    <p style={{ color: 'var(--text-secondary)', fontSize: '0.75rem' }}>{log.details}</p>
                  </div>
                ))
              )}
            </div>
          </div>
        </aside>
      </main>
    </div>
  );
}
