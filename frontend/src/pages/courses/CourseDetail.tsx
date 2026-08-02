import { useEffect, useState } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import type { Course } from "../../types";

export default function CourseDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [course, setCourse] = useState<Course | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    api
      .get<Course>(`/api/courses/${id}`)
      .then(setCourse)
      .catch(() => navigate("/courses"))
      .finally(() => setLoading(false));
  }, [id, navigate]);

  if (loading) {
    return (
      <div className="page">
        <div className="container" style={{ display: "flex", justifyContent: "center", padding: "3rem" }}>
          <div className="spinner" />
        </div>
      </div>
    );
  }

  if (!course) {
    return (
      <div className="page">
        <div className="container" style={{ textAlign: "center", padding: "3rem" }}>
          <p className="muted">Course not found.</p>
          <button className="btn btn-primary" onClick={() => navigate("/courses")}>
            Back to Courses
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 900 }}>
        {/* Back button */}
        <button
          className="btn btn-ghost btn-sm"
          onClick={() => navigate("/courses")}
          style={{ marginBottom: "1rem" }}
        >
          ← Back to Courses
        </button>

        {/* Main card */}
        <div className="card">
          {/* Header */}
          <div className="row-between" style={{ alignItems: "flex-start", marginBottom: "1rem" }}>
            <h1 style={{ fontSize: "1.6rem", marginBottom: "0.3rem", flex: 1 }}>{course.title}</h1>
            {course.skillsfuture_credit_eligible && (
              <span
                className="badge"
                style={{
                  background: "var(--green-100, #dcfce7)",
                  color: "var(--green-700, #166534)",
                  fontSize: "0.85rem",
                  padding: "0.4rem 0.8rem",
                }}
              >
                SFC Eligible
              </span>
            )}
          </div>

          {/* Provider & Category */}
          <p className="muted" style={{ fontSize: "0.95rem", marginBottom: "1.5rem" }}>
            {course.provider} · {course.category}
          </p>

          {/* Fee details section */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h2 style={{ fontSize: "1.4rem", marginBottom: "1rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M20.59 13.41l-7.17 7.17a2 2 0 01-2.83 0L2 12V2h10l8.59 8.59a2 2 0 010 2.82z" />
                <line x1="7" y1="7" x2="7.01" y2="7" />
              </svg>
              Fee details
            </h2>
            <div
              style={{
                border: "1px solid var(--border, #e5e7eb)",
                borderRadius: 12,
                padding: "1.5rem",
                background: "white",
              }}
            >
              {/* Fee breakdown */}
              <h3 style={{ fontSize: "1.1rem", marginBottom: "1rem", fontWeight: 600 }}>Fee breakdown</h3>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.8rem", marginBottom: "1.5rem" }}>
                <div className="row-between">
                  <span>Full course fee:</span>
                  <strong style={{ fontSize: "1.05rem" }}>
                    ${course.full_price_sgd > 0 ? course.full_price_sgd.toLocaleString() : course.price_sgd.toLocaleString()}.00
                  </strong>
                </div>
                {course.skillsfuture_credit_eligible && course.skillsfuture_credit_amount > 0 && (
                  <div className="row-between">
                    <span>SkillsFuture Subsidies:</span>
                    <strong style={{ fontSize: "1.05rem", color: "var(--green-700, #166534)" }}>
                      -${course.skillsfuture_credit_amount.toLocaleString()}.00
                    </strong>
                  </div>
                )}
              </div>

              {/* Estimated payable fee */}
              {course.skillsfuture_credit_eligible && (
                <>
                  <div
                    style={{
                      background: "var(--purple-50, #f3e8ff)",
                      borderRadius: 8,
                      padding: "1rem 1.2rem",
                      display: "flex",
                      justifyContent: "space-between",
                      alignItems: "center",
                      marginBottom: "1rem",
                    }}
                  >
                    <div>
                      <div style={{ fontWeight: 600, fontSize: "0.95rem" }}>Estimated payable fee:</div>
                      <div className="muted" style={{ fontSize: "0.8rem", marginTop: "0.2rem" }}>
                        After SkillsFuture subsidy
                      </div>
                    </div>
                    <div style={{ fontSize: "1.5rem", fontWeight: 700, color: "var(--purple-700, #6d28d9)" }}>
                      ${course.price_sgd.toLocaleString()}.00
                    </div>
                  </div>
                  <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                    The actual fee may be lower depending on your personal SkillsFuture Credit balance.
                    Visit MySkillsFuture to see your full eligible subsidy.
                  </p>
                </>
              )}
            </div>
          </div>

          {/* Course details grid */}
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fit, minmax(180px, 1fr))",
              gap: "1rem",
              marginBottom: "1.5rem",
            }}
          >
            {course.duration_hours && (
              <div>
                <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                  Duration
                </div>
                <div style={{ fontWeight: 500 }}>{course.duration_hours} hours</div>
              </div>
            )}
            {course.location && (
              <div>
                <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                  Location
                </div>
                <div style={{ fontWeight: 500 }}>{course.location}</div>
              </div>
            )}
            {course.date && (
              <div>
                <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                  Date
                </div>
                <div style={{ fontWeight: 500 }}>
                  {new Date(course.date).toLocaleDateString("en-SG", {
                    day: "numeric",
                    month: "short",
                    year: "numeric",
                  })}
                </div>
              </div>
            )}
            <div>
              <div className="muted" style={{ fontSize: "0.8rem", marginBottom: "0.2rem" }}>
                Source
              </div>
              <div style={{ fontWeight: 500, textTransform: "capitalize" }}>{course.source}</div>
            </div>
          </div>

          {/* Description */}
          <div style={{ marginBottom: "1.5rem" }}>
            <h3 style={{ fontSize: "1.1rem", marginBottom: "0.6rem" }}>About This Course</h3>
            <p style={{ lineHeight: 1.7, whiteSpace: "pre-wrap" }}>{course.description}</p>
          </div>

          {/* Skills */}
          {course.skills && (
            <div style={{ marginBottom: "1.5rem" }}>
              <h3 style={{ fontSize: "1.1rem", marginBottom: "0.6rem" }}>Skills You'll Gain</h3>
              <div className="tags">
                {course.skills.split(",").map((s) => (
                  <span key={s.trim()} className="badge" style={{ padding: "0.4rem 0.8rem" }}>
                    {s.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* External link button */}
          {course.url && (
            <div style={{ marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid var(--border)" }}>
              <a
                href={course.url}
                target="_blank"
                rel="noopener noreferrer"
                className="btn btn-primary"
                style={{ textDecoration: "none", display: "inline-flex", alignItems: "center", gap: "0.5rem", padding: "0.8rem 1.5rem", fontSize: "1rem" }}
              >
                View Full Details & Subsidy on MySkillsFuture
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <path d="M18 13v6a2 2 0 01-2 2H5a2 2 0 01-2-2V8a2 2 0 012-2h6" />
                  <polyline points="15 3 21 3 21 9" />
                  <line x1="10" y1="14" x2="21" y2="3" />
                </svg>
              </a>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
