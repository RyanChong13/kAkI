import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import type { Course, CourseListResponse, GrantApplicationOut } from "../../types";
import { useAuth } from "../../context/AuthContext";

export default function CoursesBrowse() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [applying, setApplying] = useState(false);
  const [applyResult, setApplyResult] = useState<string | null>(null);
  const [appliedIds, setAppliedIDs] = useState<Set<number>>(new Set());

  useEffect(() => {
    api.get<string[]>("/api/courses/meta/categories").then(setCategories).catch(() => []);
    loadCourses();
    // Load already applied
    if (user) {
      api
        .get<GrantApplicationOut[]>("/api/grants")
        .then((apps) => setAppliedIDs(new Set(apps.map((a) => a.course_id))))
        .catch(() => {});
    }
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

  function toggleSelect(id: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (selected.size === courses.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(courses.map((c) => c.id)));
    }
  }

  async function handleMassApply() {
    if (selected.size === 0) return;
    setApplying(true);
    setApplyResult(null);
    try {
      const result = await api.post<GrantApplicationOut[]>("/api/grants/mass-apply", {
        course_ids: Array.from(selected),
      });
      setAppliedIDs((prev) => {
        const next = new Set(prev);
        result.forEach((r) => next.add(r.course_id));
        return next;
      });
      setApplyResult(`Successfully applied to ${result.length} course(s)!`);
      setSelected(new Set());
    } catch (err) {
      setApplyResult(err instanceof Error ? err.message : "Failed to apply.");
    } finally {
      setApplying(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <h2 style={{ marginBottom: "0.5rem" }}>Browse Courses</h2>
        <p className="muted" style={{ marginBottom: "1.5rem" }}>
          Find SkillsFuture courses and apply directly through Nexa. Select multiple courses to apply at once.
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
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
          <button className="btn btn-secondary btn-sm" onClick={loadCourses}>
            Search
          </button>
        </div>

        {/* Multi-select bar */}
        {user && (
          <div
            className="card card-compact row-between"
            style={{
              marginBottom: "1rem",
              background: selected.size > 0 ? "var(--purple-50)" : "var(--bg-subtle)",
              border: selected.size > 0 ? "1px solid var(--purple-300)" : undefined,
            }}
          >
            <div className="row" style={{ gap: "0.75rem" }}>
              <button className="btn btn-ghost btn-sm" onClick={selectAll}>
                {selected.size === courses.length ? "Deselect All" : "Select All"}
              </button>
              <span className="muted" style={{ fontSize: "0.9rem" }}>
                {selected.size > 0 ? `${selected.size} course(s) selected` : "Select courses to apply"}
              </span>
            </div>
            {selected.size > 0 && (
              <button className="btn btn-primary btn-sm" onClick={handleMassApply} disabled={applying}>
                {applying ? "Applying..." : `Apply to ${selected.size} Course(s)`}
              </button>
            )}
          </div>
        )}

        {applyResult && (
          <div
            className="notice"
            style={{
              marginBottom: "1rem",
              background: applyResult.includes("Success") ? undefined : "var(--danger-bg, #fee)",
            }}
          >
            {applyResult}
          </div>
        )}

        {loading ? (
          <div style={{ display: "flex", justifyContent: "center", padding: "3rem" }}>
            <div className="spinner" />
          </div>
        ) : courses.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No courses found. Try a different search or category.</p>
          </div>
        ) : (
          <div
            style={{
              display: "grid",
              gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))",
              gap: "1rem",
            }}
          >
            {courses.map((course) => {
              const isSelected = selected.has(course.id);
              return (
                <div
                  key={course.id}
                  className="card"
                  style={{
                    border: isSelected ? "2px solid var(--purple-500)" : undefined,
                    cursor: "pointer",
                    transition: "border 0.15s, box-shadow 0.15s, transform 0.15s",
                    display: "flex",
                    flexDirection: "column",
                    minHeight: 280,
                  }}
                  onClick={() => navigate(`/courses/${course.id}`)}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.boxShadow = "0 4px 12px rgba(0,0,0,0.1)";
                    e.currentTarget.style.transform = "translateY(-2px)";
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.boxShadow = "";
                    e.currentTarget.style.transform = "";
                  }}
                >
                  {/* Header */}
                  <div style={{ marginBottom: "0.8rem" }}>
                    <div className="row-between" style={{ alignItems: "flex-start", marginBottom: "0.4rem" }}>
                      <h3 style={{ fontSize: "1.05rem", lineHeight: 1.3, flex: 1, marginRight: "0.5rem" }}>
                        {course.title}
                      </h3>
                      {course.skillsfuture_credit_eligible && (
                        <span
                          className="badge"
                          style={{
                            background: "var(--green-100, #dcfce7)",
                            color: "var(--green-700, #166534)",
                            fontSize: "0.75rem",
                            padding: "0.3rem 0.6rem",
                            flexShrink: 0,
                          }}
                        >
                          SFC Eligible
                        </span>
                      )}
                    </div>
                    <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                      {course.provider} · {course.category}
                    </p>
                  </div>

                  {/* Pricing */}
                  <div style={{ marginBottom: "0.8rem" }}>
                    <div style={{ fontSize: "1.3rem", fontWeight: 700, color: "var(--purple-700, #6d28d9)" }}>
                      S${course.price_sgd.toLocaleString()}
                    </div>
                    <div className="muted" style={{ fontSize: "0.75rem" }}>Payable after subsidy</div>
                  </div>

                  {/* Skills */}
                  {course.skills && (
                    <div style={{ flex: 1 }}>
                      <div className="muted" style={{ fontSize: "0.75rem", marginBottom: "0.4rem", fontWeight: 500 }}>
                        Skills you'll gain:
                      </div>
                      <div className="tags" style={{ gap: "0.4rem" }}>
                        {course.skills
                          .split(",")
                          .slice(0, 4)
                          .map((s) => (
                            <span
                              key={s.trim()}
                              className="badge"
                              style={{
                                fontSize: "0.75rem",
                                padding: "0.3rem 0.6rem",
                                background: "var(--purple-50, #f3e8ff)",
                                color: "var(--purple-700, #6d28d9)",
                              }}
                            >
                              {s.trim()}
                            </span>
                          ))}
                        {course.skills.split(",").length > 4 && (
                          <span className="badge" style={{ fontSize: "0.75rem", padding: "0.3rem 0.6rem" }}>
                            +{course.skills.split(",").length - 4} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Footer with duration/location */}
                  <div
                    className="row"
                    style={{
                      gap: "1rem",
                      marginTop: "0.8rem",
                      paddingTop: "0.8rem",
                      borderTop: "1px solid var(--border)",
                      fontSize: "0.8rem",
                      color: "var(--text-muted)",
                    }}
                  >
                    {course.duration_hours && <span>{course.duration_hours}h</span>}
                    {course.location && <span>{course.location}</span>}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}
