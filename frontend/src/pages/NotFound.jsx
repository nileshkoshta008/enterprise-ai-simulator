import React from 'react';
import { Link } from 'react-router-dom';

export default function NotFound() {
  return (
    <div className="notfound-page">
      <div className="notfound-card">
        <h1>404</h1>
        <p>Page not found. Return to dashboard or login to continue.</p>
        <div className="notfound-actions">
          <Link className="btn-secondary" to="/login">Go to Login</Link>
          <Link className="btn-primary" to="/dashboard">Go to Dashboard</Link>
        </div>
      </div>
    </div>
  );
}
