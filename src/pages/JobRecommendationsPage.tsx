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

  if (loading) {
    return (
      <div className="dashboard-shell">
        <p>Generating recommendations...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-shell" style={{ maxWidth: 700 }}>
      <span className="eyebrow">Redeployment</span>
      <h1>Job recommendations</h1>
      <p>Review the AI-generated job matches below. Select the ones you'd like to apply for.</p>

      {jobs.length === 0 && <p>No job suggestions available.</p>}

      {jobs.map(job => (
        <div
          key={job.id}
          className={`job-card${selectedIds.includes(job.id) ? ' selected' : ''}`}
        >
          <div className="job-card-header">
            <input
              type="checkbox"
              checked={selectedIds.includes(job.id)}
              onChange={() => toggleSelect(job.id)}
            />
            <h3>{job.title}</h3>
          </div>

          <div className="skill-row">
            <span className="label">Matched skills</span>
            {job.matched_skills.length > 0
              ? job.matched_skills.map(skill => (
                  <span key={skill} className="skill-tag matched">{skill}</span>
                ))
              : <span style={{ color: 'var(--text-muted)' }}>None</span>}
          </div>

          <div className="skill-row">
            <span className="label">Missing skills</span>
            {job.missing_skills.length > 0
              ? job.missing_skills.map(skill => (
                  <span key={skill} className="skill-tag missing">{skill}</span>
                ))
              : <span style={{ color: 'var(--text-muted)' }}>None</span>}
          </div>
        </div>
      ))}

      {jobs.length > 0 && (
        <div className="job-actions">
          <button
            className="btn btn-primary"
            onClick={() => handleFeedback('liked')}
            disabled={selectedIds.length === 0}
          >
            Apply to selected ({selectedIds.length})
          </button>
          <button className="btn btn-muted" onClick={() => handleFeedback('disliked')}>
            Not interested
          </button>
        </div>
      )}
    </div>
  );
};

export default JobRecommendationsPage;
