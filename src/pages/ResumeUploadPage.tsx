import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { uploadResume } from '../api/client';

const ResumeUploadPage: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<{ parsed_skills: { skill: string; years: number; source: string }[] } | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleUpload = async () => {
    if (!file) return;
    setUploading(true);
    setError('');
    try {
      const res = await uploadResume(file);
      setResult(res.data);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Upload failed';
      setError(msg);
    }
    setUploading(false);
  };

  return (
    <div style={{ maxWidth: 600, margin: '60px auto', padding: 24 }}>
      <h1>Upload Resume</h1>
      <p>Upload your resume as a PDF file. Our AI will extract your skills and experience.</p>

      {!result && (
        <div style={{ marginBottom: 16 }}>
          <input type="file" accept=".pdf" onChange={e => setFile(e.target.files?.[0] || null)} />
          <button onClick={handleUpload} disabled={!file || uploading}
            style={{ marginLeft: 12, padding: '10px 24px' }}>
            {uploading ? 'Parsing...' : 'Upload & Parse'}
          </button>
        </div>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {result && (
        <div>
          <h3>Parsed Skills ({result.parsed_skills.length})</h3>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: 8 }}>Skill</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: 8 }}>Years</th>
                <th style={{ textAlign: 'left', borderBottom: '1px solid #ddd', padding: 8 }}>Source</th>
              </tr>
            </thead>
            <tbody>
              {result.parsed_skills.map((s, i) => (
                <tr key={i}>
                  <td style={{ padding: 8 }}>{s.skill}</td>
                  <td style={{ padding: 8 }}>{s.years}</td>
                  <td style={{ padding: 8 }}>{s.source}</td>
                </tr>
              ))}
            </tbody>
          </table>
          <button onClick={() => navigate('/choose-path')} style={{ marginTop: 16, padding: '10px 24px' }}>
            Continue to Path Selection
          </button>
        </div>
      )}
    </div>
  );
};

export default ResumeUploadPage;
