import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    if (!username.trim() || !password.trim()) {
      setError('Please enter your credentials to continue.');
      setIsLoading(false);
      return;
    }

    // Professional simulation of authentication
    setTimeout(() => {
      localStorage.setItem('isAuthenticated', 'true');
      navigate('/dashboard');
      setIsLoading(false);
    }, 600);
  };

  return (
    <div className="login-page">
      <div className="card login-card">
        <header className="login-header">
          <h1>InboxIQ</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
            Enterprise SLA Triage & Inbox Simulation
          </p>
        </header>

        {error && (
          <div style={{ 
            padding: '0.75rem', 
            background: 'var(--color-danger-soft)', 
            color: 'var(--color-danger)', 
            borderRadius: 'var(--radius-sm)', 
            marginBottom: '1rem',
            fontSize: '0.875rem',
            border: '1px solid var(--color-danger)'
          }}>
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">Email Address</label>
            <input
              id="username"
              className="form-input"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="operator@company.ai"
              autoComplete="username"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Access Key</label>
            <input
              id="password"
              className="form-input"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </div>

          <button 
            type="submit" 
            className="btn btn-primary" 
            style={{ width: '100%', marginTop: '0.5rem' }} 
            disabled={isLoading}
          >
            {isLoading ? 'Verifying...' : 'Sign In to Dashboard'}
          </button>

          <footer style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            <p>© 2024 InboxIQ Solutions Inc. · Demo Environment</p>
          </footer>
        </form>
      </div>
    </div>
  );
}
