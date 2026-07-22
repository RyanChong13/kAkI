import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getMatchingGrants, getApplyPreview } from '../api/client';
import { GrantRecommendation } from '../types';

const GrantSelectionPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const courseName = searchParams.get('course') || '';
  const [grants, setGrants] = useState<GrantRecommendation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        const res = await getMatchingGrants(courseName);
        setGrants(res.data);
      } catch {
        // ignore
      }
      setLoading(false);
    };
    load();
  }, [courseName]);

  const toggleSelect = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleContinue = async () => {
    try {
      const previewRes = await getApplyPreview('grant', selectedIds);
      const previewData = previewRes.data;
      sessionStorage.setItem('applyPreview', JSON.stringify(previewData));
      navigate(`/review?previewId=${previewData.preview_id}&type=grant`);
    } catch {
      // ignore
    }
  };

  if (loading) return <div style={{ padding: 24 }}>Finding matching grants...</div>;

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: 24 }}>
      <h1>Matching Grants</h1>
      {courseName && <p>Based on course: <strong>{courseName}</strong></p>}
      <p>Select grants you'd like to apply for.</p>

      {grants.length === 0 && <p>No matching grants found for your profile.</p>}

      {grants.map(g => (
        <div key={g.id} style={{
          padding: 16, border: '1px solid #ddd', borderRadius: 8, marginBottom: 12,
          borderLeft: selectedIds.includes(g.grant_id) ? '4px solid #4caf50' : '4px solid transparent',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <input type="checkbox" checked={selectedIds.includes(g.grant_id)}
              onChange={() => toggleSelect(g.grant_id)} />
            <div>
              <h4 style={{ margin: 0 }}>{g.grant?.name || `Grant #${g.grant_id}`}</h4>
              <p style={{ margin: '4px 0' }}>
                Amount: ${g.grant?.amount?.toLocaleString() || 'N/A'} | Remaining: {g.grant?.cap_remaining || 'N/A'}
              </p>
            </div>
          </div>
        </div>
      ))}

      {selectedIds.length > 0 && (
        <button onClick={handleContinue} style={{ padding: '10px 24px', marginTop: 12 }}>
          Review Applications ({selectedIds.length})
        </button>
      )}
    </div>
  );
};

export default GrantSelectionPage;
