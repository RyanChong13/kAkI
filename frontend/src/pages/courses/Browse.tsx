import { useEffect, useState, type FormEvent } from "react";
import { api, ApiError } from "../../api/client";
import CourseCard from "../../components/CourseCard";
import { useAuth } from "../../context/AuthContext";
import type { CourseListResponse } from "../../types";

export default function Browse() {
  const { user } = useAuth();
  const [search, setSearch] = useState("");
  const [category, setCategory] = useState("");
  const [provider, setProvider] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [source, setSource] = useState("");
  const [categories, setCategories] = useState<string[]>([]);
  const [providers, setProviders] = useState<string[]>([]);

  const [data, setData] = useState<CourseListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [savedIds, setSavedIds] = useState<Set<number>>(new Set());

  useEffect(() => {
    api.get<string[]>("/api/courses/meta/categories").then(setCategories).catch(() => {});
    api.get<string[]>("/api/courses/meta/providers").then(setProviders).catch(() => {});
  }, []);

  useEffect(() => {
    if (!user) return;
    api
      .get<{ course: { id: number } }[]>("/api/saved-courses")
      .then((rows) => setSavedIds(new Set(rows.map((r) => r.course.id))))
      .catch(() => {});
  }, [user]);

  async function loadCourses() {
    setLoading(true);
    setError(null);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    if (provider) params.set("provider", provider);
    if (maxPrice) params.set("max_price", maxPrice);
    if (source) params.set("source", source);

    try {
      const result = await api.get<CourseListResponse>(`/api/courses?${params.toString()}`);
      setData(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not load courses. Please try again shortly.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    loadCourses();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function handleFilterSubmit(e: FormEvent) {
    e.preventDefault();
    loadCourses();
  }

  async function toggleSave(courseId: number) {
    if (!user) return;
    try {
      if (savedIds.has(courseId)) {
        await api.del(`/api/saved-courses/${courseId}`);
        setSavedIds((prev) => {
          const next = new Set(prev);
          next.delete(courseId);
          return next;
        });
      } else {
        await api.post(`/api/saved-courses/${courseId}`);
        setSavedIds((prev) => new Set(prev).add(courseId));
      }
    } catch {
      // non-critical
    }
  }

  return (
    <div className="page">
      <div className="container">
        <h2>Browse courses & workshops</h2>
        <p>SkillsFuture courses plus live Singapore workshops from Eventbrite, all in one place.</p>

        {data && !data.eventbrite_available && data.eventbrite_notice && (
          <div className="notice">{data.eventbrite_notice}</div>
        )}
        {error && <div className="notice notice-error">{error}</div>}

        <form onSubmit={handleFilterSubmit} className="card card-compact" style={{ marginBottom: "1.5rem" }}>
          <div className="row" style={{ gap: "1rem" }}>
            <div className="field" style={{ flex: 2, minWidth: 200, marginBottom: 0 }}>
              <label htmlFor="search">Search</label>
              <input
                id="search"
                type="text"
                placeholder="Title, description, or skill"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <div className="field" style={{ flex: 1, minWidth: 160, marginBottom: 0 }}>
              <label htmlFor="category">Category</label>
              <select id="category" value={category} onChange={(e) => setCategory(e.target.value)}>
                <option value="">All categories</option>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </div>
            <div className="field" style={{ flex: 1, minWidth: 160, marginBottom: 0 }}>
              <label htmlFor="provider">Provider</label>
              <select id="provider" value={provider} onChange={(e) => setProvider(e.target.value)}>
                <option value="">All providers</option>
                {providers.map((p) => (
                  <option key={p} value={p}>
                    {p}
                  </option>
                ))}
              </select>
            </div>
            <div className="field" style={{ flex: 1, minWidth: 140, marginBottom: 0 }}>
              <label htmlFor="max-price">Max price (SGD)</label>
              <input id="max-price" type="number" min={0} value={maxPrice} onChange={(e) => setMaxPrice(e.target.value)} />
            </div>
            <div className="field" style={{ flex: 1, minWidth: 160, marginBottom: 0 }}>
              <label htmlFor="source">Source</label>
              <select id="source" value={source} onChange={(e) => setSource(e.target.value)}>
                <option value="">All sources</option>
                <option value="skillsfuture">SkillsFuture</option>
                <option value="eventbrite">Eventbrite</option>
              </select>
            </div>
          </div>
          <div className="row" style={{ marginTop: "1rem" }}>
            <button type="submit" className="btn btn-primary">
              Apply filters
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={() => {
                setSearch("");
                setCategory("");
                setProvider("");
                setMaxPrice("");
                setSource("");
                setTimeout(loadCourses, 0);
              }}
            >
              Clear
            </button>
          </div>
        </form>

        {loading ? (
          <div className="spinner" />
        ) : data && data.items.length > 0 ? (
          <>
            <p className="muted">{data.total} result(s)</p>
            <div className="grid grid-2">
              {data.items.map((course) => (
                <CourseCard
                  key={course.id}
                  course={course}
                  action={
                    user && (
                      <button
                        className={savedIds.has(course.id) ? "btn btn-secondary" : "btn btn-ghost"}
                        onClick={() => toggleSave(course.id)}
                      >
                        {savedIds.has(course.id) ? "★ Saved" : "☆ Save"}
                      </button>
                    )
                  }
                />
              ))}
            </div>
          </>
        ) : (
          <div className="notice">No courses match these filters. Try widening your search.</div>
        )}
      </div>
    </div>
  );
}
