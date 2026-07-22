import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getJobRecommendations, listJobSuggestions, submitFeedback, getApplyPreview } from '../api/client';
import { JobSuggestion } from '../types';

const JobRecommendationsPage: React.FC = () => {
  const [jobs, setJobs] = useState<JobSuggestion[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const load = async () => {
      try {
        // Try to get existing suggestions first
        const existing = await listJobSuggestions();
        if (existing.data.length > 0) {
          setJobs(existing.data);
        } else {
          // Generate new recommendations
          const res = await getJobRecommendations();
          setJobs(res.data);
        }
      } catch {
        // ignore
      }
      setLoading(false);
    };
    load();
  }, []);

  const toggleSelect = (id: number) => {
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const handleFeedback = async (feedback: string) => {
    try {
      const res = await submitFeedback(feedback, feedback === 'liked' ? selectedIds : undefined);
      const action = res.data.action;
      if (action === 'proceed_to_apply') {
        // Step 1 of mass-apply: assemble preview
        const previewRes = await getApplyPreview('job', selectedIds);
        const previewData = previewRes.data;
        sessionStorage.setItem('applyPreview', JSON.stringify(previewData));
        navigate(`/review?previewId=${previewData.preview_id}&type=job`);
      } else if (action === 'redirect_to_upskilling') {
        navigate('/upskilling');
      } else if (action === 'exit') {
        navigate('/exit');
      }
    } catch {
      // ignore
    }
  };

  if (loading) return <div style={{ padding: 24 }}>Generating recommendations...</div>;

  return (
    <div style={{ maxWidth: 700, margin: '40px auto', padding: 24 }}>
      <h1>Job Recommendations</h1>
      <p>Review the AI-generated job matches below. Select the ones you'd like to apply for.</p>

      {jobs.length === 0 && <p>No job suggestions available.</p>}

      {jobs.map(job => (
        <div key={job.id} style={{
          padding: 16, border: '1px solid #ddd', borderRadius: 8, marginBottom: 12,
          borderLeft: selectedIds.includes(job.id) ? '4px solid #2196f3' : '4px solid transparent',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <input type="checkbox" checked={selectedIds.includes(job.id)}
              onChange={() => toggleSelect(job.id)} />
            <h3 style={{ margin: 0 }}>{job.title}</h3>
          </div>
          <p style={{ margin: '8px 0 4px' }}>
            <strong>Matched skills:</strong> {job.matched_skills.join(', ')}
          </p>
          <p style={{ margin: 0 }}>
            <strong>Missing skills:</strong> {job.missing_skills.join(', ') || 'None'}
          </p>
        </div>
      ))}

      {jobs.length > 0 && (
        <div style={{ display: 'flex', gap: 12, marginTop: 16 }}>
          <button onClick={() => handleFeedback('liked')} disabled={selectedIds.length === 0}
            style={{ padding: '10px 24px', background: '#4caf50', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Apply to Selected ({selectedIds.length})
          </button>
          <button onClick={() => handleFeedback('disliked')}
            style={{ padding: '10px 24px', background: '#f44336', color: '#fff', border: 'none', borderRadius: 4, cursor: 'pointer' }}>
            Not Interested
          </button>
        </div>
      )}
    </div>
  );
};

export default JobRecommendationsPage;
