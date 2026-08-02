import { useEffect, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { api } from "../../api/client";
import type { Event } from "../../types";

export default function OrganiserProfile() {
  const { user } = useAuth();
  const [events, setEvents] = useState<Event[]>([]);

  useEffect(() => {
    api.get<Event[]>("/api/organiser/events").then(setEvents).catch(() => []);
  }, []);

  if (!user) return null;

  const publishedEvents = events.filter((e) => !e.is_cancelled);
  const totalAttendees = events.reduce((sum, e) => sum + e.attendees_count, 0);

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 720 }}>
        {/* Profile header */}
        <div className="card" style={{ marginBottom: "1.5rem", padding: "2rem" }}>
          <div style={{ display: "flex", gap: "1.5rem", alignItems: "flex-start" }}>
            {/* Avatar */}
            <div
              style={{
                width: 80,
                height: 80,
                borderRadius: "50%",
                background: "linear-gradient(135deg, var(--purple-500), var(--purple-700))",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                color: "white",
                fontWeight: 800,
                fontSize: "1.8rem",
                flexShrink: 0,
              }}
            >
              {(user.company_name || user.name || "O")[0].toUpperCase()}
            </div>
            <div style={{ flex: 1 }}>
              <h2 style={{ marginBottom: "0.2rem" }}>{user.company_name || user.name}</h2>
              {user.company_name && (
                <p className="muted" style={{ margin: 0, fontSize: "0.9rem" }}>
                  Contact: {user.name}
                </p>
              )}
              <div style={{ marginTop: "0.5rem", display: "flex", gap: "0.5rem", flexWrap: "wrap" }}>
                <span className="badge" style={{ background: "var(--purple-100)", color: "var(--purple-700)" }}>
                  Organiser
                </span>
                {user.website && (
                  <a
                    href={user.website}
                    target="_blank"
                    rel="noreferrer"
                    className="badge"
                    style={{ background: "var(--bg-subtle)", color: "var(--ink-700)", textDecoration: "none" }}
                  >
                    {new URL(user.website).hostname}
                  </a>
                )}
                {user.phone && (
                  <span className="badge" style={{ background: "var(--bg-subtle)", color: "var(--ink-700)" }}>
                    {user.phone}
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* Bio */}
          {user.bio && (
            <div style={{ marginTop: "1.25rem" }}>
              <p style={{ lineHeight: 1.6, margin: 0 }}>{user.bio}</p>
            </div>
          )}
        </div>

        {/* Stats row */}
        <div className="grid grid-3" style={{ marginBottom: "1.5rem" }}>
          <div className="card stat-card">
            <div className="stat-value">{events.length}</div>
            <div className="stat-label">Total Events</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{publishedEvents.length}</div>
            <div className="stat-label">Active Events</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{totalAttendees.toLocaleString()}</div>
            <div className="stat-label">Total Attendees</div>
          </div>
        </div>

        {/* Recent events */}
        <h3 style={{ marginBottom: "1rem" }}>Recent Events</h3>
        {publishedEvents.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No events published yet.</p>
          </div>
        ) : (
          <div className="stack" style={{ gap: "0.5rem" }}>
            {publishedEvents.slice(0, 5).map((ev) => (
              <div key={ev.id} className="card card-compact row-between">
                <div>
                  <strong>{ev.title}</strong>
                  <p className="muted" style={{ margin: "0.2rem 0 0", fontSize: "0.85rem" }}>
                    {ev.category} &middot;{" "}
                    {ev.date
                      ? new Date(ev.date).toLocaleDateString("en-SG", {
                          month: "short",
                          day: "numeric",
                          year: "numeric",
                        })
                      : "No date"}{" "}
                    &middot; {ev.attendees_count} attendees
                  </p>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
