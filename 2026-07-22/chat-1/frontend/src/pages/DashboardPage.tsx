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

  if (loading) return <div style={{ padding: 24 }}>Loading...</div>;

  return (
    <div style={{ maxWidth: 600, margin: '60px auto', padding: 24 }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h1>Dashboard</h1>
        <button onClick={() => { logout(); navigate('/login'); }}>Logout</button>
      </div>

      <p>Welcome, {user?.email}</p>

      {session && session.status !== 'active' && (
        <div style={{ padding: 16, background: '#f0f0f0', borderRadius: 8, marginBottom: 16 }}>
          <p>Previous session: <strong>{session.status.replace(/_/g, ' ')}</strong></p>
        </div>
      )}

      {!resume && (
        <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16 }}>
          <h3>Step 1: Upload your resume</h3>
          <p>Upload a PDF resume to get started.</p>
          <Link to="/resume"><button style={{ padding: '10px 24px' }}>Upload Resume</button></Link>
        </div>
      )}

      {resume && !session && (
        <div style={{ padding: 16, border: '1px solid #ddd', borderRadius: 8, marginBottom: 16 }}>
          <h3>Step 2: Choose your path</h3>
          <p>Your resume has been parsed with {resume.parsed_skills.length} skills identified.</p>
          <Link to="/choose-path"><button style={{ padding: '10px 24px' }}>Choose Path</button></Link>
        </div>
      )}

      {session && session.status === 'active' && (
        <div style={{ padding: 16, border: '1px solid #2196f3', borderRadius: 8, marginBottom: 16 }}>
          <h3>Active Session (Round {session.round_number})</h3>
          <p>Path: {session.path}</p>
          {session.path === 'redeployment' && (
            <Link to="/jobs"><button style={{ padding: '10px 24px' }}>View Job Recommendations</button></Link>
          )}
          {session.path === 'upskilling' && (
            <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              <Link to="/upskilling"><button style={{ padding: '10px 24px' }}>Continue Upskilling</button></Link>
              {session.round_number === 2 && (
                <Link to="/jobs"><button style={{ padding: '10px 24px' }}>View Updated Job Recommendations</button></Link>
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default DashboardPage;
