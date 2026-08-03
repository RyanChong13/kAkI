import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import type { Course, CourseListResponse } from "../../types";

export default function CoursesBrowse() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [categories, setCategories] = useState<string[]>([]);

  useEffect(() => {
    api.get<string[]>("/api/courses/meta/categories").then(setCategories).catch(() => []);
    loadCourses();
  }, []);

  function loadCourses() {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    api
      .get<CourseListResponse>(`/api/courses?${params}`)
      .then((res) => setCourses(res.items))
      .catch(() => [])
      .finally(() => setLoading(false));
  }

  return (
    <div className="page">
      <div className="container">
        <h2 style={{ marginBottom: "0.5rem" }}>Browse Courses</h2>
        <p className="muted" style={{ marginBottom: "1.5rem" }}>
          SkillsFuture courses from MySkillsFuture. Click a course to see fee details and subsidy information.
        </p>

        {/* Filters */}
        <div className="row" style={{ gap: "0.75rem", marginBottom: "1.5rem", flexWrap: "wrap" }}>
          <input
            style={{ flex: 1, minWidth: 200 }}
            placeholder="Search courses..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && loadCourses()}
          />
          <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ minWidth: 160 }}>
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
          <button className="btn btn-secondary btn-sm" onClick={loadCourses}>Search</button>
        </div>

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "3rem" }}>
            <div className="spinner" />
          </div>
        ) : courses.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No courses found. Try a different search or category.</p>
          </div>
        ) : (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem" }}>
            {courses.map((course) => (
              <div
                key={course.id}
                className="card card-hover"
                style={{ display: "flex", flexDirection: "column", minHeight: 260 }}
                onClick={() => navigate(`/courses/${course.id}`)}
              >
                <div style={{ marginBottom: "0.8rem" }}>
                  <h3 style={{ fontSize: "1.05rem", lineHeight: 1.3 }}>{course.title}</h3>
                  <p className="muted" style={{ fontSize: "0.85rem", margin: "0.25rem 0 0" }}>
                    {course.provider} · {course.category}
                  </p>
                </div>

                <div style={{ marginBottom: "0.8rem" }}>
                  <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "var(--purple-700)" }}>
                    S${course.price_sgd.toLocaleString()}
                  </div>
                  <div className="muted" style={{ fontSize: "0.75rem" }}>
                    {course.full_price_sgd > course.price_sgd
                      ? `Was $${course.full_price_sgd.toLocaleString()} (after subsidy)`
                      : "Payable fee"}
                  </div>
                </div>

                {course.skills && (
                  <div style={{ flex: 1 }}>
                    <div className="tags" style={{ gap: "0.4rem" }}>
                      {course.skills.split(",").slice(0, 4).map((s) => (
                        <span key={s.trim()} className="badge" style={{ fontSize: "0.75rem" }}>
                          {s.trim()}
                        </span>
                      ))}
                      {course.skills.split(",").length > 4 && (
                        <span className="badge badge-outline" style={{ fontSize: "0.75rem" }}>
                          +{course.skills.split(",").length - 4} more
                        </span>
                      )}
                    </div>
                  </div>
                )}

                <div className="row" style={{ gap: "1rem", marginTop: "0.8rem", paddingTop: "0.8rem", borderTop: "1px solid var(--border)", fontSize: "0.8rem" }}>
                  {course.duration_hours && <span className="muted">{course.duration_hours}h</span>}
                  {course.location && <span className="muted">{course.location}</span>}
                  {course.base_credit_eligible && <span className="badge badge-success" style={{ fontSize: "0.7rem" }}>SFC</span>}
                  {course.mid_career_eligible && <span className="badge badge-warning" style={{ fontSize: "0.7rem" }}>Mid-Career</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
