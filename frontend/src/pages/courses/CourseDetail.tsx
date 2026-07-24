import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import type { Course } from "../../types";

export default function CourseDetail() {
  const { id } = useParams();
  const { user } = useAuth();
  const [course, setCourse] = useState<Course | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api
      .get<Course>(`/api/courses/${id}`)
      .then(setCourse)
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load this course."))
      .finally(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    if (!user) return;
    api
      .get<{ course: { id: number } }[]>("/api/saved-courses")
      .then((rows) => setSaved(rows.some((r) => r.course.id === Number(id))))
      .catch(() => {});
  }, [user, id]);

  async function toggleSave() {
    if (!user || !course) return;
    try {
      if (saved) {
        await api.del(`/api/saved-courses/${course.id}`);
        setSaved(false);
      } else {
        await api.post(`/api/saved-courses/${course.id}`);
        setSaved(true);
      }
    } catch {
      // non-critical
    }
  }

  if (loading) {
    return (
      <div className="page container">
        <div className="spinner" />
      </div>
    );
  }

  if (error || !course) {
    return (
      <div className="page container">
        <div className="notice notice-error">{error || "Course not found."}</div>
        <Link to="/courses">← Back to courses</Link>
      </div>
    );
  }

  const skills = course.skills ? course.skills.split(",").map((s) => s.trim()).filter(Boolean) : [];

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 760 }}>
        <Link to="/courses" className="muted">
          ← Back to courses
        </Link>

        <div className="row" style={{ margin: "1rem 0 0.5rem" }}>
          <span className="badge">{course.category}</span>
          <span className="badge badge-outline">{course.source === "eventbrite" ? "Eventbrite" : "SkillsFuture"}</span>
          {course.skillsfuture_credit_eligible && <span className="badge badge-success">SkillsFuture Credit eligible</span>}
        </div>

        <h1 style={{ fontSize: "1.8rem" }}>{course.title}</h1>
        <p className="muted" style={{ fontSize: "1rem" }}>
          {course.provider} &middot; {course.location}
        </p>

        <div className="card" style={{ margin: "1.5rem 0" }}>
          <div className="grid grid-2">
            <div>
              <p className="muted" style={{ marginBottom: "0.15rem" }}>
                Price
              </p>
              <strong style={{ fontSize: "1.2rem" }}>{course.price_sgd > 0 ? `S$${course.price_sgd.toLocaleString()}` : "Free"}</strong>
            </div>
            {course.duration_hours && (
              <div>
                <p className="muted" style={{ marginBottom: "0.15rem" }}>
                  Duration
                </p>
                <strong style={{ fontSize: "1.2rem" }}>{course.duration_hours} hours</strong>
              </div>
            )}
            {course.date && (
              <div>
                <p className="muted" style={{ marginBottom: "0.15rem" }}>
                  Date
                </p>
                <strong style={{ fontSize: "1.2rem" }}>{new Date(course.date).toLocaleString("en-SG")}</strong>
              </div>
            )}
            {course.skillsfuture_credit_eligible && (
              <div>
                <p className="muted" style={{ marginBottom: "0.15rem" }}>
                  SkillsFuture Credit
                </p>
                <strong style={{ fontSize: "1.2rem", color: "var(--purple-700)" }}>
                  S${course.skillsfuture_credit_amount.toLocaleString()}
                </strong>
              </div>
            )}
          </div>
        </div>

        <h3>About this course</h3>
        <p>{course.description || "No description provided."}</p>

        {skills.length > 0 && (
          <>
            <h3>Skills covered</h3>
            <div className="row" style={{ marginBottom: "1.5rem" }}>
              {skills.map((s) => (
                <span key={s} className="badge">
                  {s}
                </span>
              ))}
            </div>
          </>
        )}

        <div className="row">
          {course.url && (
            <a href={course.url} target="_blank" rel="noreferrer" className="btn btn-primary">
              View original listing ↗
            </a>
          )}
          {user && (
            <button className="btn btn-secondary" onClick={toggleSave}>
              {saved ? "★ Saved" : "☆ Save for later"}
            </button>
          )}
        </div>
      </div>
    </div>
  );
}
