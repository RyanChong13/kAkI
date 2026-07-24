import { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import type { ApplicationOut, Job } from "../../types";

interface LocationState {
  jobIds?: number[];
}

export default function MassApply() {
  const location = useLocation();
  const jobIds = (location.state as LocationState | null)?.jobIds ?? [];

  const [jobs, setJobs] = useState<Job[]>([]);
  const [applications, setApplications] = useState<ApplicationOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (jobIds.length === 0) return;
    api.get<Job[]>("/api/jobs").then((all) => setJobs(all.filter((j) => jobIds.includes(j.id))));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  async function handleApply() {
    setLoading(true);
    setError(null);
    try {
      const result = await api.post<ApplicationOut[]>("/api/applications/mass-apply", { job_ids: jobIds });
      setApplications(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not submit applications.");
    } finally {
      setLoading(false);
    }
  }

  if (jobIds.length === 0) {
    return (
      <div className="page container">
        <div className="notice">No jobs selected. <Link to="/jobs/recommended">Go back and select some jobs</Link>.</div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h2>Review & apply</h2>
        <p>
          We'll record your application intent with your uploaded resume attached. Note: there is no public Singapore
          job-board submission API, so this tracks your applications here rather than submitting them to employers'
          own systems — see the README for what a real integration would need.
        </p>

        {error && <div className="notice notice-error">{error}</div>}

        <div className="stack">
          {jobs.map((job) => {
            const app = applications?.find((a) => a.job_id === job.id);
            return (
              <div key={job.id} className="card card-compact row-between">
                <div>
                  <strong>{job.title}</strong>
                  <p className="muted" style={{ marginBottom: 0 }}>
                    {job.company}
                  </p>
                </div>
                {app && <span className="badge badge-success">Submitted</span>}
              </div>
            );
          })}
        </div>

        {applications ? (
          <div className="notice" style={{ marginTop: "1.5rem" }}>
            <strong>{applications.length} application(s) submitted.</strong> You can track these from your dashboard.
            <div className="row" style={{ marginTop: "1rem" }}>
              <Link to="/dashboard" className="btn btn-primary">
                Go to dashboard
              </Link>
              <Link to="/jobs/recommended" className="btn btn-ghost">
                Find more jobs
              </Link>
            </div>
          </div>
        ) : (
          <button className="btn btn-primary" style={{ marginTop: "1.5rem" }} onClick={handleApply} disabled={loading}>
            {loading ? "Submitting…" : `Mass apply to ${jobIds.length} job(s)`}
          </button>
        )}
      </div>
    </div>
  );
}
