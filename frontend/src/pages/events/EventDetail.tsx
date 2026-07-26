import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import EventCard from "../../components/EventCard";
import type { Event, EventRegistrationOut, SubstituteResult } from "../../types";

const CATEGORY_COLORS: Record<string, string> = {
  AI: "#7c3aed", "Software Engineering": "#2563eb", Cybersecurity: "#dc2626", Entrepreneurship: "#ea580c",
  Marketing: "#d946ef", Finance: "#059669", Design: "#8b5cf6", Leadership: "#b45309",
  "Public Speaking": "#0891b2", Networking: "#4f46e5", Volunteering: "#e11d48", Sports: "#16a34a",
  Hobbies: "#a855f7", "Career Development": "#0284c7",
};

export default function EventDetail() {
  const { id } = useParams<{ id: string }>();
  const { user } = useAuth();

  const [event, setEvent] = useState<Event | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaved, setIsSaved] = useState(false);
  const [isCompleted, setIsCompleted] = useState(false);
  const [isRegistered, setIsRegistered] = useState(false);
  const [saving, setSaving] = useState(false);
  const [registering, setRegistering] = useState(false);
  const [substitutes, setSubstitutes] = useState<SubstituteResult | null>(null);
  const [findingSubs, setFindingSubs] = useState(false);

  useEffect(() => {
    if (!id) return;
    setLoading(true);

    const eventPromise = api.get<Event>(`/api/events/${id}`);

    const savedPromise = user
      ? api.get<Array<{ event_id: number }>>("/api/events/saved/list").catch(() => [])
      : Promise.resolve([]);
    const completedPromise = user
      ? api.get<number[]>("/api/events/completed/list").catch(() => [])
      : Promise.resolve([]);
    const registeredPromise = user
      ? api.get<EventRegistrationOut[]>("/api/events/registrations/list").catch(() => [])
      : Promise.resolve([]);

    Promise.all([eventPromise, savedPromise, completedPromise, registeredPromise])
      .then(([ev, savedList, completedList, registeredList]) => {
        setEvent(ev);
        setIsSaved(savedList.some((s: { event_id?: number; event?: Event }) => (s.event_id ?? s.event?.id) === ev.id));
        setIsCompleted((completedList as number[]).includes(ev.id));
        setIsRegistered((registeredList as EventRegistrationOut[]).some((r) => r.event.id === ev.id));
      })
      .catch(() => setError("Event not found."))
      .finally(() => setLoading(false));
  }, [id, user]);

  async function toggleSave() {
    if (!id) return;
    setSaving(true);
    try {
      if (isSaved) {
        await api.del(`/api/events/saved/${id}`);
        setIsSaved(false);
      } else {
        await api.post(`/api/events/saved/${id}`);
        setIsSaved(true);
      }
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  }

  async function markComplete() {
    if (!id) return;
    try {
      await api.post(`/api/events/complete/${id}`);
      setIsCompleted(true);
    } catch {
      // ignore
    }
  }

  async function findSubstitutes() {
    if (!id) return;
    setFindingSubs(true);
    try {
      const res = await api.post<SubstituteResult>("/api/ai/substitutes", { event_id: parseInt(id) });
      setSubstitutes(res);
    } catch {
      // ignore
    } finally {
      setFindingSubs(false);
    }
  }

  async function toggleRegistration() {
    if (!id) return;
    setRegistering(true);
    try {
      if (isRegistered) {
        await api.del(`/api/events/register/${id}`);
        setIsRegistered(false);
      } else {
        await api.post(`/api/events/register/${id}`);
        setIsRegistered(true);
      }
    } catch {
      // ignore
    } finally {
      setRegistering(false);
    }
  }

  if (loading) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center" }}>
        <div className="spinner" />
      </div>
    );
  }

  if (error || !event) {
    return (
      <div className="page">
        <div className="container" style={{ textAlign: "center" }}>
          <h2>Event not found</h2>
          <p className="muted">{error || "This event doesn't exist or has been removed."}</p>
          <Link to="/events" className="btn btn-primary">Browse Events</Link>
        </div>
      </div>
    );
  }

  const color = CATEGORY_COLORS[event.category] || "#7c3aed";
  const skills = event.skills ? event.skills.split(",").map((s) => s.trim()).filter(Boolean) : [];
  const tags = event.tags ? event.tags.split(",").map((s) => s.trim()).filter(Boolean) : [];

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 800 }}>
        <Link to="/events" className="muted" style={{ fontSize: "0.9rem", fontWeight: 600 }}>
          Back to events
        </Link>

        {/* Event image */}
        <div className="event-img" style={{ height: 280, marginTop: "1rem" }}>
          {event.image_url ? (
            <img src={event.image_url} alt={event.title} />
          ) : (
            <div className="event-img-placeholder" style={{ background: `linear-gradient(135deg, ${color}22, ${color}44)`, color, fontSize: "1.1rem" }}>
              {event.category}
            </div>
          )}
        </div>

        {/* Header */}
        <div className="row-between" style={{ marginBottom: "0.75rem" }}>
          <div>
            <h1 style={{ fontSize: "1.8rem", marginBottom: "0.3rem" }}>{event.title}</h1>
            <p className="muted" style={{ marginBottom: 0 }}>
              {event.organiser} · {event.location}
            </p>
          </div>
          {user && (
            <div className="row" style={{ gap: "0.5rem" }}>
              <button
                className={`btn ${isRegistered ? "btn-success" : "btn-primary"}`}
                onClick={toggleRegistration}
                disabled={registering}
              >
                {isRegistered ? "Registered" : "Register"}
              </button>
              <button className={`btn ${isSaved ? "btn-primary" : "btn-secondary"}`} onClick={toggleSave} disabled={saving}>
                {isSaved ? "Saved" : "Save"}
              </button>
              <button className="btn btn-ghost" onClick={markComplete} disabled={isCompleted}>
                {isCompleted ? "Completed" : "Mark Complete"}
              </button>
            </div>
          )}
        </div>

        {/* Badges */}
        <div className="row" style={{ marginBottom: "1.5rem" }}>
          <span className="badge">{event.category}</span>
          <span className="badge badge-outline">{event.source}</span>
          <span className="badge badge-outline">{event.difficulty}</span>
          {event.created_by && <span className="badge" style={{ background: "var(--purple-600)", color: "white" }}>Created on Nexa</span>}
          {event.price_sgd === 0 && <span className="badge badge-success">Free</span>}
          {event.is_full && <span className="badge badge-warning">Full</span>}
          {event.is_cancelled && <span className="badge badge-danger">Cancelled</span>}
        </div>

        {/* Details card */}
        <div className="card" style={{ marginBottom: "1rem" }}>
          <h3>About</h3>
          <p>{event.description}</p>
          <div className="row" style={{ gap: "2rem", marginTop: "1rem" }}>
            <div>
              <strong>Date</strong>
              <p className="muted" style={{ margin: 0 }}>
                {event.date
                  ? new Date(event.date).toLocaleDateString("en-SG", { weekday: "short", year: "numeric", month: "long", day: "numeric" })
                  : "TBA"}
              </p>
            </div>
            <div>
              <strong>Duration</strong>
              <p className="muted" style={{ margin: 0 }}>{event.duration_hours ? `${event.duration_hours} hours` : "N/A"}</p>
            </div>
            <div>
              <strong>Price</strong>
              <p className="muted" style={{ margin: 0 }}>{event.price_sgd > 0 ? `S$${event.price_sgd.toLocaleString()}` : "Free"}</p>
            </div>
            <div>
              <strong>Attendees</strong>
              <p className="muted" style={{ margin: 0 }}>{event.attendees_count}{event.capacity ? ` / ${event.capacity}` : ""}</p>
            </div>
          </div>
        </div>

        {/* Skills */}
        {skills.length > 0 && (
          <div className="card" style={{ marginBottom: "1rem" }}>
            <h3>Skills</h3>
            <div className="tags">
              {skills.map((s) => (
                <span key={s} className="badge badge-outline">{s}</span>
              ))}
            </div>
          </div>
        )}

        {/* Tags */}
        {tags.length > 0 && (
          <div className="card" style={{ marginBottom: "1rem" }}>
            <h3>Tags</h3>
            <div className="tags">
              {tags.map((t) => (
                <span key={t} className="badge" style={{ background: "var(--bg-subtle)" }}>{t}</span>
              ))}
            </div>
          </div>
        )}

        {/* Recommended audience */}
        {event.recommended_audience && (
          <div className="card" style={{ marginBottom: "1rem" }}>
            <h3>Recommended Audience</h3>
            <p className="muted" style={{ marginBottom: 0 }}>{event.recommended_audience}</p>
          </div>
        )}

        {/* Substitute Finder */}
        <div className="card">
          <div className="row-between" style={{ marginBottom: "1rem" }}>
            <h3 style={{ marginBottom: 0 }}>Find Alternatives</h3>
            <button className="btn btn-ghost btn-sm" onClick={findSubstitutes} disabled={findingSubs}>
              {findingSubs ? "Searching..." : "Find Substitutes"}
            </button>
          </div>
          <p className="muted" style={{ fontSize: "0.88rem" }}>
            Looking for something similar? Our AI can find alternative events covering the same skills.
          </p>

          {substitutes && (
            <div style={{ marginTop: "1rem" }}>
              <p style={{ color: "var(--purple-600)", fontWeight: 600, fontSize: "0.9rem" }}>{substitutes.reason}</p>
              {substitutes.alternatives.length === 0 ? (
                <p className="muted">No alternatives found at this time.</p>
              ) : (
                <div className="grid grid-2" style={{ marginTop: "0.75rem" }}>
                  {substitutes.alternatives.map((a) => (
                    <EventCard key={a.event.id} event={a.event} matchScore={a.match_score} reason={a.reason} />
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
