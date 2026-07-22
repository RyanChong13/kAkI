import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getSession, getResume } from '../api/client';
import { FlowSession, Resume } from '../types';

const DashboardPage: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [session, setSession] = useState<FlowSession | null>(null);
  const [resume, setResume] = useState<Resume | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const [sessRes, resRes] = await Promise.allSettled([getSession(), getResume()]);
        if (sessRes.status === 'fulfilled' && sessRes.value.data) setSession(sessRes.value.data);
        if (resRes.status === 'fulfilled' && resRes.value.data) setResume(resRes.value.data);
      } catch {
        // ignore
      }
      setLoading(false);
    };
    load();
  }, []);

  if (loading) {
    return (
      <div className="dashboard-shell">
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-shell">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">Dashboard</span>
          <h1 style={{ marginBottom: 0 }}>Welcome, {user?.email}</h1>
        </div>
        <button
          className="btn btn-secondary"
          onClick={() => { logout(); navigate('/login'); }}
        >
          Logout
        </button>
      </div>

      <div className="path">
        {session && session.status !== 'active' && (
          <div className="step-card done">
            <span className="badge">Previous session</span>
            <p style={{ margin: 0 }}>
              Status: <strong>{session.status.replace(/_/g, ' ')}</strong>
            </p>
          </div>
        )}

        {!resume && (
          <div className="step-card active">
            <span className="badge">Step 1</span>
            <h3>Upload your resume</h3>
            <p>Upload a PDF resume to get started.</p>
            <Link to="/resume">
              <button className="btn btn-primary">Upload resume</button>
            </Link>
          </div>
        )}

        {resume && !session && (
          <div className="step-card active">
            <span className="badge">Step 2</span>
            <h3>Choose your path</h3>
            <p>Your resume has been parsed with {resume.parsed_skills.length} skills identified.</p>
            <Link to="/choose-path">
              <button className="btn btn-primary">Choose path</button>
            </Link>
          </div>
        )}

        {session && session.status === 'active' && (
          <div className="step-card active">
            <span className="badge">Round {session.round_number}</span>
            <h3>Active session</h3>
            <p>Path: {session.path}</p>
            {session.path === 'redeployment' && (
              <Link to="/jobs">
                <button className="btn btn-primary">View job recommendations</button>
              </Link>
            )}
            {session.path === 'upskilling' && (
              <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
                <Link to="/upskilling">
                  <button className="btn btn-primary">Continue upskilling</button>
                </Link>
                {session.round_number === 2 && (
                  <Link to="/jobs">
                    <button className="btn btn-secondary">View updated job recommendations</button>
                  </Link>
                )}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default DashboardPage;
