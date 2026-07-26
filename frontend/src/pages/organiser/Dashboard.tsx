import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../api/client";
import { useAuth } from "../../context/AuthContext";
import type { Event, OrganiserDashboardStats } from "../../types";

export default function OrganiserDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<OrganiserDashboardStats | null>(null);
  const [events, setEvents] = useState<Event[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  useEffect(() => {
    if (user && user.role !== "organiser") {
      navigate("/dashboard");
      return;
    }
    loadData();
  }, [user]);

  function loadData() {
    setLoading(true);
    Promise.all([
      api.get<OrganiserDashboardStats>("/api/organiser/dashboard").catch(() => null),
      api.get<Event[]>("/api/organiser/events").catch(() => []),
    ]).then(([s, e]) => {
      setStats(s);
      setEvents(e);
      setLoading(false);
    });
  }

  async function handleDelete(id: number) {
    if (deleteId !== id) {
      setDeleteId(id);
      return;
    }
    try {
      await api.del(`/api/organiser/events/${id}`);
      setEvents((prev) => prev.map((ev) => (ev.id === id ? { ...ev, is_cancelled: true } : ev)));
      loadData();
    } catch {
      // ignore
    } finally {
      setDeleteId(null);
    }
  }

  if (loading) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center" }}>
        <div className="spinner" />
      </div>
    );
  }

  const maxAttendees = stats ? Math.max(...stats.monthly_growth.map((m) => m.attendees), 1) : 1;

  return (
    <div className="page">
      <div className="container">
        <div className="row-between" style={{ marginBottom: "1.5rem" }}>
          <h2 style={{ marginBottom: 0 }}>Organiser Dashboard</h2>
          <div className="row" style={{ gap: "0.5rem" }}>
            <Link to="/organiser/settings" className="btn btn-ghost btn-sm">Settings</Link>
            <Link to="/organiser/events/new" className="btn btn-primary">+ Create Event</Link>
          </div>
        </div>

        {/* Stats cards */}
        {stats && (
          <div className="grid grid-4" style={{ marginBottom: "2rem" }}>
            <div className="card stat-card">
              <div className="stat-value">{stats.total_events}</div>
              <div className="stat-label">Total Events</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value">{stats.total_attendees.toLocaleString()}</div>
              <div className="stat-label">Total Attendees</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value">{stats.avg_rating.toFixed(1)}</div>
              <div className="stat-label">Avg Rating</div>
            </div>
            <div className="card stat-card">
              <div className="stat-value">S${stats.revenue_sgd.toLocaleString()}</div>
              <div className="stat-label">Revenue</div>
            </div>
          </div>
        )}

        {/* Monthly Growth Chart */}
        {stats && stats.monthly_growth.length > 0 && (
          <div className="card" style={{ marginBottom: "2rem" }}>
            <h3 style={{ marginBottom: "1rem" }}>Monthly Growth (Attendees)</h3>
            <div style={{ display: "flex", alignItems: "flex-end", gap: "0.5rem", height: 180, padding: "0.5rem 0" }}>
              {stats.monthly_growth.map((m) => {
                const heightPct = (m.attendees / maxAttendees) * 100;
                return (
                  <div key={m.month} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", gap: "0.3rem" }}>
                    <span style={{ fontSize: "0.75rem", fontWeight: 600 }}>{m.attendees}</span>
                    <div
                      style={{
                        width: "100%",
                        maxWidth: 60,
                        background: "linear-gradient(to top, var(--purple-600), var(--purple-400))",
                        borderRadius: "6px 6px 0 0",
                        height: `${Math.max(heightPct, 4)}%`,
                        transition: "height 0.4s ease",
                      }}
                    />
                    <span className="muted" style={{ fontSize: "0.7rem", textAlign: "center" }}>{m.month}</span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Upcoming Events */}
        {stats && (
          <div className="card" style={{ marginBottom: "2rem", maxWidth: 260 }}>
            <h4>Upcoming Events</h4>
            <p style={{ fontSize: "2rem", fontWeight: 800, color: "var(--purple-600)", margin: 0 }}>{stats.upcoming_events}</p>
          </div>
        )}

        {/* Event list */}
        <h3 style={{ marginBottom: "1rem" }}>My Events ({events.length})</h3>
        {events.length === 0 ? (
          <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
            <p className="muted">No events yet. Create your first event!</p>
            <Link to="/organiser/events/new" className="btn btn-primary btn-sm">Create Event</Link>
          </div>
        ) : (
          <div className="stack" style={{ gap: "0.5rem" }}>
            {events.map((ev) => (
              <div key={ev.id} className="card card-compact row-between">
                <div style={{ flex: 1 }}>
                  <div className="row" style={{ gap: "0.5rem" }}>
                    <strong>{ev.title}</strong>
                    {ev.is_cancelled && <span className="badge badge-danger">Cancelled</span>}
                  </div>
                  <p className="muted" style={{ margin: "0.2rem 0 0", fontSize: "0.85rem" }}>
                    {ev.category} · {ev.date ? new Date(ev.date).toLocaleDateString("en-SG", { month: "short", day: "numeric", year: "numeric" }) : "No date"} · S${ev.price_sgd}
                    {ev.attendees_count > 0 && ` · ${ev.attendees_count} attendees`}
                  </p>
                </div>
                <div className="row" style={{ gap: "0.5rem" }}>
                  <Link to={`/organiser/events/${ev.id}/edit`} className="btn btn-ghost btn-sm">Edit</Link>
                  <button
                    className="btn btn-ghost btn-sm"
                    style={{ color: deleteId === ev.id ? "var(--danger)" : undefined }}
                    onClick={() => handleDelete(ev.id)}
                    disabled={ev.is_cancelled}
                  >
                    {deleteId === ev.id ? "Confirm?" : ev.is_cancelled ? "Deleted" : "Delete"}
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
