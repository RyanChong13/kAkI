import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api } from "../../api/client";
import EventCard from "../../components/EventCard";
import type { Event, EventListResponse } from "../../types";

export default function Browse() {
  const [searchParams] = useSearchParams();

  const [events, setEvents] = useState<Event[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(true);

  const [search, setSearch] = useState("");
  const [category, setCategory] = useState(searchParams.get("category") || "");
  const [source, setSource] = useState("");
  const [difficulty, setDifficulty] = useState("");
  const [freeOnly, setFreeOnly] = useState(false);

  const [categories, setCategories] = useState<string[]>([]);
  const [sources, setSources] = useState<string[]>([]);
  const difficulties = ["Beginner", "Intermediate", "Advanced", "All Levels"];

  const debounceRef = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  // Load filter options
  useEffect(() => {
    api.get<string[]>("/api/events/meta/categories").then(setCategories).catch(() => {});
    api.get<string[]>("/api/events/meta/sources").then(setSources).catch(() => {});
  }, []);

  // Sync URL param
  useEffect(() => {
    const cat = searchParams.get("category");
    if (cat) setCategory(cat);
  }, [searchParams]);

  const fetchEvents = useCallback(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (search) params.set("search", search);
    if (category) params.set("category", category);
    if (source) params.set("source", source);
    if (difficulty) params.set("difficulty", difficulty);
    if (freeOnly) params.set("free_only", "true");

    api
      .get<EventListResponse>(`/api/events?${params.toString()}`)
      .then((res) => {
        setEvents(res.items);
        setTotal(res.total);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [search, category, source, difficulty, freeOnly]);

  useEffect(() => {
    if (debounceRef.current) clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(fetchEvents, 300);
    return () => {
      if (debounceRef.current) clearTimeout(debounceRef.current);
    };
  }, [fetchEvents]);

  return (
    <div className="page">
      <div className="container">
        <h2 style={{ marginBottom: "1.5rem" }}>Browse Events</h2>

        {/* Search bar */}
        <div className="row" style={{ gap: "0.5rem", marginBottom: "1.25rem" }}>
          <input
            type="text"
            placeholder="Search events, skills, organisers..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ flex: 1 }}
          />
          <button className="btn btn-primary" onClick={fetchEvents}>
            Search
          </button>
        </div>

        {/* Filters */}
        <div className="row" style={{ gap: "0.75rem", marginBottom: "1.5rem" }}>
          <select value={category} onChange={(e) => setCategory(e.target.value)} style={{ maxWidth: 200 }}>
            <option value="">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>

          <select value={source} onChange={(e) => setSource(e.target.value)} style={{ maxWidth: 200 }}>
            <option value="">All Sources</option>
            {sources.map((s) => (
              <option key={s} value={s}>
                {s}
              </option>
            ))}
          </select>

          <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)} style={{ maxWidth: 180 }}>
            <option value="">All Levels</option>
            {difficulties.map((d) => (
              <option key={d} value={d}>
                {d}
              </option>
            ))}
          </select>

          <label style={{ display: "flex", alignItems: "center", gap: "0.4rem", fontSize: "0.9rem", cursor: "pointer" }}>
            <input type="checkbox" checked={freeOnly} onChange={(e) => setFreeOnly(e.target.checked)} />
            Free only
          </label>

          {(category || source || difficulty || freeOnly || search) && (
            <button
              className="btn btn-ghost btn-sm"
              onClick={() => {
                setSearch("");
                setCategory("");
                setSource("");
                setDifficulty("");
                setFreeOnly(false);
              }}
            >
              Clear filters
            </button>
          )}
        </div>

        {/* Results count */}
        <p className="muted" style={{ marginBottom: "1rem" }}>
          {loading ? "Loading..." : `${total} events found`}
        </p>

        {/* Loading */}
        {loading && (
          <div style={{ display: "flex", justifyContent: "center", padding: "3rem 0" }}>
            <div className="spinner" />
          </div>
        )}

        {/* Event grid */}
        {!loading && events.length > 0 && (
          <div className="grid grid-3">
            {events.map((e) => (
              <EventCard key={e.id} event={e} />
            ))}
          </div>
        )}

        {/* Empty state */}
        {!loading && events.length === 0 && (
          <div style={{ textAlign: "center", padding: "3rem 0" }}>
            <p className="muted" style={{ fontSize: "1.1rem" }}>
              No events match your filters.
            </p>
            <p className="muted">Try adjusting your search or removing some filters.</p>
          </div>
        )}
      </div>
    </div>
  );
}
