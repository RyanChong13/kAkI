import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { confirmApply } from '../api/client';
import { ApplyPreviewItem } from '../types';

const MassApplyReviewPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const previewId = searchParams.get('previewId') || '';
  const applyType = searchParams.get('type') || '';
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState<{ submitted: number; status: string } | null>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  // Items stored in sessionStorage by the preview step
  const [items, setItems] = useState<ApplyPreviewItem[]>([]);

  useEffect(() => {
    const stored = sessionStorage.getItem('applyPreview');
    if (stored) {
      try {
        const parsed = JSON.parse(stored);
        if (parsed.preview_id === previewId) {
          setItems(parsed.items || []);
        }
      } catch {
        // ignore
      }
    }
  }, [previewId]);

  const handleConfirm = async () => {
    if (!previewId) return;
    setSubmitting(true);
    setError('');
    try {
      const res = await confirmApply(previewId);
      setResult(res.data);
      sessionStorage.removeItem('applyPreview');
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Submission failed';
      setError(msg);
    }
    setSubmitting(false);
  };

  if (result) {
    return (
      <div style={{ maxWidth: 600, margin: '60px auto', padding: 24, textAlign: 'center' }}>
        <h1>Applications Submitted</h1>
        <p style={{ fontSize: 18 }}>{result.submitted} application(s) have been submitted successfully.</p>
        <p>Your applications have been recorded and an audit copy is stored for reference.</p>
        <button onClick={() => navigate('/dashboard')} style={{ padding: '10px 24px', marginTop: 16 }}>
          Return to Dashboard
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: 600, margin: '60px auto', padding: 24 }}>
      <h1>Review Applications</h1>
      <p>Review the details below before confirming your submission.</p>

      <div style={{
        padding: 16, background: '#fff3e0', borderRadius: 8, border: '1px solid #ff9800', marginBottom: 16,
      }}>
        <p style={{ margin: 0 }}>
          <strong>Important:</strong> No applications are submitted until you click Confirm.
          This action cannot be undone.
        </p>
      </div>

      {applyType && (
        <p>Application type: <strong>{applyType === 'job' ? 'Job Applications' : 'Grant Applications'}</strong></p>
      )}

      {items.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <h3>Items to submit:</h3>
          {items.map((item, i) => (
            <div key={i} style={{ padding: 12, border: '1px solid #ddd', borderRadius: 6, marginBottom: 8 }}>
              <strong>{item.target_name}</strong>
              <p style={{ margin: '4px 0 0', fontSize: 14, color: '#666' }}>
                Type: {item.type} | ID: {item.target_id}
              </p>
            </div>
          ))}
        </div>
      )}

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {!previewId && (
        <p style={{ color: '#888' }}>No preview available. Please go back and select items first.</p>
      )}

      <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
        <button onClick={handleConfirm} disabled={!previewId || submitting}
          style={{ padding: '10px 24px', background: '#4caf50', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
          {submitting ? 'Submitting...' : 'Confirm & Submit'}
        </button>
        <button onClick={() => navigate(-1)}
          style={{ padding: '10px 24px', border: '1px solid #ddd', borderRadius: 4, cursor: 'pointer', background: '#fff' }}>
          Go Back
        </button>
      </div>
    </div>
  );
};

export default MassApplyReviewPage;
