import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { startFlow } from '../api/client';

const PathSelectionPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const selectPath = async (path: string) => {
    setLoading(true);
    try {
      await startFlow(path);
      if (path === 'redeployment') {
        navigate('/jobs');
      } else {
        navigate('/upskilling');
      }
    } catch {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 700, margin: '60px auto', padding: 24 }}>
      <h1>Choose Your Path</h1>
      <p>Select the path that best fits your current situation.</p>

      <div style={{ display: 'flex', gap: 24, marginTop: 24 }}>
        <div style={{
          flex: 1, padding: 24, border: '2px solid #2196f3', borderRadius: 12, cursor: 'pointer',
        }} onClick={() => !loading && selectPath('redeployment')}>
          <h2 style={{ color: '#2196f3' }}>Job Redeployment</h2>
          <p>Get AI-recommended job matches based on your current skills. Review suggestions and apply to positions that interest you.</p>
          <ul>
            <li>AI matches your skills to open roles</li>
            <li>Review and select jobs to apply</li>
            <li>Batch apply with one confirmation</li>
          </ul>
        </div>

        <div style={{
          flex: 1, padding: 24, border: '2px solid #4caf50', borderRadius: 12, cursor: 'pointer',
        }} onClick={() => !loading && selectPath('upskilling')}>
          <h2 style={{ color: '#4caf50' }}>Upskilling</h2>
          <p>Explore courses and grants to build new skills. Define your goals and get personalised recommendations.</p>
          <ul>
            <li>Define your learning goals</li>
            <li>AI recommends courses matching your constraints</li>
            <li>Find matching grants and apply</li>
          </ul>
        </div>
      </div>

      {loading && <p style={{ marginTop: 16 }}>Starting session...</p>}
    </div>
  );
};

export default PathSelectionPage;
