import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import JobCard from "../../components/JobCard";
import type { JobRecommendation } from "../../types";

export default function RecommendedJobs() {
  const navigate = useNavigate();
  const [recommendations, setRecommendations] = useState<JobRecommendation[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function loadRecommendations() {
    setLoading(true);
    setError(null);
    try {
      const results = await api.get<JobRecommendation[]>("/api/jobs/recommendations");
      setRecommendations(results);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load job recommendations.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadRecommendations();
  }, []);

  async function handleFeedback(jobId: number, liked: boolean) {
    try {
      await api.post("/api/jobs/feedback", { job_id: jobId, liked });
      if (!liked) {
        setRecommendations((prev) => prev.filter((r) => r.job.id !== jobId));
        setSelected((prev) => {
          const next = new Set(prev);
          next.delete(jobId);
          return next;
        });
      }
    } catch {
      // non-critical — feedback failing shouldn't block browsing
    }
  }

  function toggleSelect(jobId: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(jobId)) next.delete(jobId);
      else next.add(jobId);
      return next;
    });
  }

  function handleContinue() {
    navigate("/jobs/apply", { state: { jobIds: Array.from(selected) } });
  }

  return (
    <div className="page">
      <div className="container">
        <h2>Recommended jobs for you</h2>
        <p>Based on skills from your resume. Like a job to keep it, dislike to see something different.</p>

        {error && <div className="notice notice-error">{error}</div>}

        {loading ? (
          <div className="spinner" />
        ) : recommendations.length === 0 ? (
          <div className="notice">No more recommendations right now. Try browsing all jobs, or check back later.</div>
        ) : (
          <div className="grid grid-2">
            {recommendations.map(({ job, match_score, matched_skills }) => (
              <JobCard
                key={job.id}
                job={job}
                matchScore={match_score}
                matchedSkills={matched_skills}
                action={
                  <div className="row-between">
                    <div className="row">
                      <button className="btn btn-secondary" onClick={() => handleFeedback(job.id, true)}>
                        👍 Like
                      </button>
                      <button className="btn btn-ghost" onClick={() => handleFeedback(job.id, false)}>
                        👎 Not for me
                      </button>
                    </div>
                    <label className="row" style={{ gap: "0.4rem", fontWeight: 600 }}>
                      <input type="checkbox" checked={selected.has(job.id)} onChange={() => toggleSelect(job.id)} />
                      Select
                    </label>
                  </div>
                }
              />
            ))}
          </div>
        )}

        <div
          className="card row-between"
          style={{ position: "sticky", bottom: "1rem", marginTop: "2rem", boxShadow: "var(--shadow)" }}
        >
          <span>
            <strong>{selected.size}</strong> job{selected.size === 1 ? "" : "s"} selected
          </span>
          <button className="btn btn-primary" disabled={selected.size === 0} onClick={handleContinue}>
            Continue to apply
          </button>
        </div>
      </div>
    </div>
  );
}
