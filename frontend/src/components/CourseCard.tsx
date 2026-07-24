import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import type { Course } from "../types";

export default function CourseCard({
  course,
  matchScore,
  action,
}: {
  course: Course;
  matchScore?: number;
  action?: ReactNode;
}) {
  return (
    <div className="card card-compact stack" style={{ gap: "0.6rem" }}>
      <div className="row-between" style={{ alignItems: "flex-start" }}>
        <div>
          <div className="row" style={{ marginBottom: "0.3rem" }}>
            <span className="badge">{course.category}</span>
            <span className="badge badge-outline">{course.source === "eventbrite" ? "Eventbrite" : "SkillsFuture"}</span>
            {course.skillsfuture_credit_eligible && <span className="badge badge-success">SkillsFuture Credit</span>}
          </div>
          <h3 style={{ fontSize: "1.05rem" }}>
            <Link to={`/courses/${course.id}`}>{course.title}</Link>
          </h3>
          <p className="muted" style={{ marginBottom: "0.3rem" }}>
            {course.provider} &middot; {course.location}
          </p>
        </div>
        {matchScore !== undefined && (
          <span className="badge" style={{ background: "var(--purple-600)", color: "white", whiteSpace: "nowrap" }}>
            {Math.round(matchScore * 100)}% match
          </span>
        )}
      </div>

      <p style={{ fontSize: "0.9rem", marginBottom: 0 }}>
        {course.description.length > 140 ? course.description.slice(0, 140) + "…" : course.description}
      </p>

      <div className="row-between">
        <strong style={{ color: "var(--purple-700)" }}>
          {course.price_sgd > 0 ? `S$${course.price_sgd.toLocaleString()}` : "Free"}
        </strong>
        {course.duration_hours && <span className="muted">{course.duration_hours}h</span>}
      </div>

      {action}
    </div>
  );
}
