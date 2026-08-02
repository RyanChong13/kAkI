import { useEffect, useState } from "react";
import { api } from "../../api/client";
import type { Course, CourseListResponse, GrantApplicationOut } from "../../types";
import { useAuth } from "../../context/AuthContext";

export default function CoursesBrowse() {
  const { user } = useAuth();
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
          <div className="stack" style={{ gap: "0.75rem" }}>
            {courses.map((course) => {
              const isSelected = selected.has(course.id);
              const isApplied = appliedIds.has(course.id);
              return (
                <div
                  key={course.id}
                  className="card"
                  style={{
                    border: isSelected ? "2px solid var(--purple-500)" : undefined,
                    cursor: user ? "pointer" : undefined,
                    transition: "border 0.15s",
                  }}
                  onClick={() => user && !isApplied && toggleSelect(course.id)}
                >
                  <div style={{ display: "flex", gap: "1rem", alignItems: "flex-start" }}>
                    {/* Checkbox */}
                    {user && (
                      <div
                        style={{
                          width: 22,
                          height: 22,
                          borderRadius: 6,
                          border: `2px solid ${isSelected ? "var(--purple-500)" : "var(--border)"}`,
                          background: isSelected ? "var(--purple-500)" : "transparent",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "center",
                          flexShrink: 0,
                          marginTop: 2,
                        }}
                      >
                        {isSelected && (
                          <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                            <path d="M3 7l3 3 5-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
                          </svg>
                        )}
                      </div>
                    )}

                    {/* Content */}
                    <div style={{ flex: 1 }}>
                      <div className="row-between">
                        <h3 style={{ fontSize: "1.05rem", marginBottom: "0.2rem" }}>{course.title}</h3>
                        <div style={{ display: "flex", gap: "0.4rem" }}>
                          {isApplied && <span className="badge badge-success">Applied</span>}
                          {course.skillsfuture_credit_eligible && (
                            <span className="badge" style={{ background: "var(--green-100, #dcfce7)", color: "var(--green-700, #166534)" }}>
                              SFC Eligible
                            </span>
                          )}
                        </div>
                      </div>
                      <p className="muted" style={{ fontSize: "0.85rem", margin: "0.2rem 0" }}>
                        {course.provider} &middot; {course.category}
                      </p>
                      <p style={{ fontSize: "0.9rem", margin: "0.4rem 0" }}>
                        {course.description.length > 200
                          ? course.description.slice(0, 200) + "..."
                          : course.description}
                      </p>
                      <div className="row" style={{ gap: "1rem", marginTop: "0.5rem", fontSize: "0.85rem" }}>
                        <span>
                          <strong>S${course.price_sgd.toLocaleString()}</strong>
                        </span>
                        {course.date && (
                          <span>
                            {new Date(course.date).toLocaleDateString("en-SG", { weekday: "short", day: "numeric", month: "short", year: "numeric" })}
                            {new Date(course.date).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" }) !== "00:00" &&
                              ` at ${new Date(course.date).toLocaleTimeString("en-SG", { hour: "2-digit", minute: "2-digit" })}`}
                          </span>
                        )}
                        {course.duration_hours && <span>{course.duration_hours}h</span>}
                        {course.location && <span>{course.location}</span>}
                        {course.skillsfuture_credit_eligible && (
                          <span style={{ color: "var(--green-700, #166534)" }}>
                            SFC: S${course.skillsfuture_credit_amount}
                          </span>
                        )}
                      </div>
                      {course.skills && (
                        <div className="tags" style={{ marginTop: "0.5rem" }}>
                          {course.skills
                            .split(",")
                            .slice(0, 5)
                            .map((s) => (
                              <span key={s.trim()} className="badge" style={{ fontSize: "0.7rem", padding: "0.15rem 0.5rem" }}>
                                {s.trim()}
                              </span>
                            ))}
                        </div>
                      )}
                    </div>
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
