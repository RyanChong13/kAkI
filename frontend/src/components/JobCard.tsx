import type { ReactNode } from "react";
import type { Job } from "../types";

export default function JobCard({
  job,
  matchScore,
  matchedSkills,
  action,
}: {
  job: Job;
  matchScore?: number;
  matchedSkills?: string[];
  action?: ReactNode;
}) {
  return (
    <div className="card card-compact stack" style={{ gap: "0.6rem" }}>
      <div className="row-between" style={{ alignItems: "flex-start" }}>
        <div>
          <span className="badge" style={{ marginBottom: "0.3rem" }}>
            {job.category}
          </span>
          <h3 style={{ fontSize: "1.05rem" }}>{job.title}</h3>
          <p className="muted" style={{ marginBottom: "0.3rem" }}>
            {job.company} &middot; {job.location}
          </p>
        </div>
        {matchScore !== undefined && (
          <span className="badge" style={{ background: "var(--purple-600)", color: "white", whiteSpace: "nowrap" }}>
            {Math.round(matchScore * 100)}% match
          </span>
        )}
      </div>

      <p style={{ fontSize: "0.9rem", marginBottom: 0 }}>
        {job.description.length > 140 ? job.description.slice(0, 140) + "…" : job.description}
      </p>

      <div className="row-between">
        <strong style={{ color: "var(--purple-700)" }}>
          S${job.salary_min_sgd.toLocaleString()} - S${job.salary_max_sgd.toLocaleString()}
        </strong>
        <a href={job.url} target="_blank" rel="noreferrer" className="muted">
          View listing ↗
        </a>
      </div>

      {matchedSkills && matchedSkills.length > 0 && (
        <div className="row">
          {matchedSkills.map((s) => (
            <span key={s} className="badge badge-outline">
              {s}
            </span>
          ))}
        </div>
      )}

      {action}
    </div>
  );
}
