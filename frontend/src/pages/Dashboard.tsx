import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import EventCard from "../components/EventCard";
import type { EventRecommendation, EventRegistrationOut, SavedEventOut } from "../types";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [recs, setRecs] = useState<EventRecommendation[]>([]);
  const [saved, setSaved] = useState<SavedEventOut[]>([]);
  const [registered, setRegistered] = useState<EventRegistrationOut[]>([]);
  const [completedIds, setCompletedIds] = useState<number[]>([]);
  const [loading, setLoading] = useState(true);

  // Redirect organisers to their own dashboard
  useEffect(() => {
    if (user && user.role === "organiser") {
      navigate("/organiser", { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    Promise.all([
      api.get<EventRecommendation[]>("/api/ai/recommendations?limit=12").catch(() => []),
      api.get<SavedEventOut[]>("/api/events/saved/list").catch(() => []),
      api.get<number[]>("/api/events/completed/list").catch(() => []),
      api.get<EventRegistrationOut[]>("/api/events/registrations/list").catch(() => []),
    ]).then(([r, s, c, reg]) => {
      setRecs(r);
      setSaved(s);
      setCompletedIds(c);
      setRegistered(reg);
      setLoading(false);
    });
  }, []);

  if (!user) return null;

  return (
    <div className="page">
      <div className="container">
        {/* Welcome */}
        <h2 style={{ marginBottom: "0.25rem" }}>Welcome back, {user.name || user.email}</h2>
        <p className="muted" style={{ marginBottom: "2rem" }}>
          Here's your personalised growth dashboard powered by AI.
        </p>

        {/* Quick stats */}
        <div className="grid grid-4" style={{ marginBottom: "2rem" }}>
          <div className="card stat-card">
            <div className="stat-value">{recs.length}</div>
            <div className="stat-label">Recommendations</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{registered.length}</div>
            <div className="stat-label">Registered</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{saved.length}</div>
            <div className="stat-label">Saved Events</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{completedIds.length}</div>
            <div className="stat-label">Completed</div>
          </div>
          <Link to="/growth-plan" style={{ textDecoration: "none" }}>
            <div className="card stat-card card-hover">
              <div className="stat-value">AI</div>
              <div className="stat-label">Growth Plan</div>
            </div>
          </Link>
        </div>

        {/* Quick actions */}
        <div className="row" style={{ gap: "0.75rem", marginBottom: "2rem" }}>
          <Link to="/growth-plan" className="btn btn-primary btn-sm">Generate Growth Plan</Link>
          <Link to="/learning-journey" className="btn btn-secondary btn-sm">Create Learning Journey</Link>
          <Link to="/events" className="btn btn-ghost btn-sm">Browse All Events</Link>
          <Link to="/profile" className="btn btn-ghost btn-sm">Edit Profile</Link>
        </div>

        {/* AI Recommendations */}
        <section style={{ marginBottom: "2.5rem" }}>
          <div className="row-between" style={{ marginBottom: "1rem" }}>
            <h3 style={{ marginBottom: 0 }}>Recommended for You</h3>
            <Link to="/events" className="btn btn-ghost btn-sm">Browse all</Link>
          </div>

          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
              <div className="spinner" />
            </div>
          ) : recs.length > 0 ? (
            <div className="grid grid-3">
              {recs.map((r) => (
                <EventCard key={r.event.id} event={r.event} matchScore={r.match_score} reason={r.reason} />
              ))}
            </div>
          ) : (
            <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
              <p className="muted">
                Complete your <Link to="/profile">profile</Link> with interests and goals to get personalised recommendations.
              </p>
            </div>
          )}
        </section>

        {/* Registered Events */}
        {registered.length > 0 && (
          <section style={{ marginBottom: "2.5rem" }}>
            <h3 style={{ marginBottom: "1rem" }}>Registered Events ({registered.length})</h3>
            <div className="grid grid-3">
              {registered.map((r) => (
                <EventCard key={r.id} event={r.event} />
              ))}
            </div>
          </section>
        )}

        {/* Saved Events */}
        <section>
          <h3 style={{ marginBottom: "1rem" }}>Saved Events ({saved.length})</h3>
          {saved.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
              <p className="muted" style={{ marginBottom: "0.5rem" }}>No saved events yet.</p>
              <Link to="/events" className="btn btn-secondary btn-sm">Browse events</Link>
            </div>
          ) : (
            <div className="grid grid-3">
              {saved.map((s) => (
                <EventCard key={s.id} event={s.event} />
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
