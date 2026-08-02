import type { ReactNode } from "react";
import { Link } from "react-router-dom";
import type { Event } from "../types";

const CATEGORY_LABELS: Record<string, string> = {
  AI: "AI", "Software Engineering": "SWE", Cybersecurity: "SEC", Entrepreneurship: "ENT",
  Marketing: "MKT", Finance: "FIN", Design: "DSN", Leadership: "LDR",
  "Public Speaking": "SPK", Networking: "NET", Volunteering: "VOL", Sports: "SPT",
  Hobbies: "HBY", "Career Development": "CAR",
};

export default function EventCard({
  event,
  matchScore,
  reason,
  action,
}: {
  event: Event;
  matchScore?: number;
  reason?: string;
  action?: ReactNode;
}) {
  const skills = event.skills ? event.skills.split(",").map(s => s.trim()).filter(Boolean).slice(0, 4) : [];

  return (
    <div className="card card-compact card-hover stack" style={{ gap: "0.5rem" }}>
      <div className="event-img">
        {event.image_url ? (
          <img src={event.image_url} alt={event.title} />
        ) : (
          <div className="event-img-placeholder">{CATEGORY_LABELS[event.category] || event.category}</div>
        )}
      </div>

      <div className="row" style={{ marginBottom: "0.2rem" }}>
        <span className="badge">{event.category}</span>
        <span className="badge badge-outline">{event.source}</span>
        {event.created_by && <span className="badge" style={{ background: "var(--purple-600)", color: "white" }}>Created on Nexa</span>}
        {event.price_sgd === 0 && <span className="badge badge-success">Free</span>}
        {event.is_full && <span className="badge badge-warning">Full</span>}
      </div>

      <h3 style={{ fontSize: "1.05rem", margin: 0 }}>
        <Link to={`/events/${event.id}`} style={{ color: "var(--ink-900)", textDecoration: "none" }}>{event.title}</Link>
      </h3>

      <p className="muted" style={{ marginBottom: "0.2rem", fontSize: "0.85rem" }}>
        {event.organiser} · {event.location.split(",")[0]}
      </p>

      <div className="tags">
        {skills.map(s => <span key={s} className="badge badge-outline" style={{ fontSize: "0.7rem" }}>{s}</span>)}
      </div>

      {reason && <p style={{ fontSize: "0.84rem", fontStyle: "italic", color: "var(--purple-600)", margin: "0.2rem 0 0", fontWeight: 600 }}>{reason}</p>}

      <div className="row-between" style={{ marginTop: "0.3rem" }}>
        <strong style={{ color: "var(--purple-700)" }}>
          {event.price_sgd > 0 ? `S$${event.price_sgd.toLocaleString()}` : "Free"}
        </strong>
        <div className="row" style={{ gap: "0.5rem" }}>
          {event.duration_hours && <span className="muted" style={{ fontSize: "0.8rem" }}>{event.duration_hours}h</span>}
          {event.date && <span className="muted" style={{ fontSize: "0.8rem" }}>{new Date(event.date).toLocaleDateString("en-SG", { month: "short", day: "numeric" })}</span>}
          {matchScore !== undefined && (
            <span className="badge" style={{ background: "var(--purple-600)", color: "white" }}>
              {Math.round(matchScore * 100)}%
            </span>
          )}
        </div>
      </div>

      {action}
    </div>
  );
}
