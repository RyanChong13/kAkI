import React from 'react';
import { useNavigate } from 'react-router-dom';

const ExitPage: React.FC = () => {
  const navigate = useNavigate();

  return (
    <div style={{ maxWidth: 600, margin: '60px auto', padding: 24, textAlign: 'center' }}>
      <h1>Session Complete</h1>
      <p style={{ fontSize: 16, lineHeight: 1.6 }}>
        You have reached the end of the recommendation flow for this session.
        Your profile and parsed skills have been retained in case you return later.
      </p>

      <div style={{
        padding: 24, background: '#f5f5f5', borderRadius: 12, marginTop: 24, textAlign: 'left',
      }}>
        <h3 style={{ marginTop: 0 }}>Additional Resources</h3>
        <p>If you'd like further support, consider these external career resources:</p>
        <ul>
          <li>
            <a href="https://www.wsg.gov.sg" target="_blank" rel="noopener noreferrer">
              Workforce Singapore (WSG)
            </a> — Career conversion programmes and support
          </li>
          <li>
            <a href="https://www.e2i.com.sg" target="_blank" rel="noopener noreferrer">
              e2i (Employment and Employability Institute)
            </a> — Career coaching and job matching
          </li>
        </ul>
      </div>

      <button onClick={() => navigate('/dashboard')} style={{ padding: '10px 24px', marginTop: 24 }}>
        Return to Dashboard
      </button>
    </div>
  );
};

export default ExitPage;
