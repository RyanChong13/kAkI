import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import type { GrowthPlanOut } from "../types";

export default function GrowthPlan() {
  const [plan, setPlan] = useState<GrowthPlanOut | null>(null);
  const [pastPlans, setPastPlans] = useState<GrowthPlanOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Form state
  const [days, setDays] = useState(7);
  const [interests, setInterests] = useState("");
  const [goals, setGoals] = useState("");
  const [availability, setAvailability] = useState("");
  const [preferredTimings, setPreferredTimings] = useState("");
  const [budget, setBudget] = useState("");

  useEffect(() => {
    api
      .get<GrowthPlanOut[]>("/api/ai/growth-plans")
      .then((plans) => {
        setPastPlans(plans);
        if (plans.length > 0) setPlan(plans[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    setGenerating(true);
    try {
      const result = await api.post<GrowthPlanOut>("/api/ai/growth-plan", {
        days,
        interests,
        goals,
        availability,
        preferred_timings: preferredTimings,
        budget_sgd: budget ? parseFloat(budget) : null,
      });
      setPlan(result);
      setPastPlans((prev) => [result, ...prev]);
    } catch {
      // ignore
    } finally {
      setGenerating(false);
    }
  }

  if (loading) {
    return (
      <div className="page" style={{ display: "flex", justifyContent: "center" }}>
        <div className="spinner" />
      </div>
    );
  }

  // Phase A: Generate form
  if (!plan) {
    return (
      <div className="page">
        <div className="container" style={{ maxWidth: 640 }}>
          <h2>Generate Your Growth Plan</h2>
          <p className="muted">
            AI creates a personalised day-by-day plan with events, networking, and skill-building activities.
          </p>

          {/* Duration selector */}
          <div className="step-track" style={{ marginBottom: "1.5rem" }}>
            {[7, 14, 30].map((d) => (
              <button
                key={d}
                className={`step-pill ${days === d ? "active" : ""}`}
                onClick={() => setDays(d)}
              >
                {d} Days
              </button>
            ))}
          </div>

          <form onSubmit={handleGenerate} className="stack">
            <div className="field">
              <label>Interests</label>
              <input
                value={interests}
                onChange={(e) => setInterests(e.target.value)}
                placeholder="e.g. AI, leadership, design, networking"
              />
            </div>
            <div className="field">
              <label>Goals</label>
              <textarea
                value={goals}
                onChange={(e) => setGoals(e.target.value)}
                placeholder="What do you want to achieve? e.g. Transition into AI product management"
              />
            </div>
            <div className="field">
              <label>Availability</label>
              <input
                value={availability}
                onChange={(e) => setAvailability(e.target.value)}
                placeholder="e.g. Weekday evenings, weekends"
              />
            </div>
            <div className="field">
              <label>Preferred Timings</label>
              <input
                value={preferredTimings}
                onChange={(e) => setPreferredTimings(e.target.value)}
                placeholder="e.g. Morning, afternoon, evening"
              />
            </div>
            <div className="field">
              <label>Budget (SGD)</label>
              <input
                type="number"
                min={0}
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
                placeholder="200"
              />
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={generating}>
              {generating ? "Generating..." : `Generate ${days}-Day Plan`}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Phase B: Plan display
  const currentDay = 1; // In a real app this would track actual progress

  return (
    <div className="page">
      <div className="container">
        <div className="row-between" style={{ marginBottom: "1.5rem" }}>
          <div>
            <h2 style={{ marginBottom: "0.25rem" }}>Your {plan.plan_type}-Day Growth Plan</h2>
            <p className="muted" style={{ marginBottom: 0 }}>
              Generated on {new Date(plan.created_at).toLocaleDateString("en-SG", { year: "numeric", month: "long", day: "numeric" })}
            </p>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => setPlan(null)}>
            Generate New Plan
          </button>
        </div>

        {/* Progress bar */}
        <div className="progress-bar" style={{ marginBottom: "2rem" }}>
          <div
            className="progress-bar-fill"
            style={{ width: `${(currentDay / plan.days.length) * 100}%` }}
          />
        </div>

        {/* Day-by-day timeline */}
        <div className="timeline">
          {plan.days.map((day) => (
            <div key={day.day} className="timeline-item">
              <h4 style={{ marginBottom: "0.5rem" }}>
                Day {day.day} — {day.date_label}
              </h4>
              {day.activities.length === 0 ? (
                <p className="muted" style={{ fontSize: "0.88rem" }}>Rest day — reflect on what you've learned.</p>
              ) : (
                <div className="stack" style={{ gap: "0.5rem" }}>
                  {day.activities.map((act, i) => (
                    <div key={i} className="card card-compact">
                      <div className="row-between">
                        <div>
                          <Link to={`/events/${act.event_id}`} style={{ fontWeight: 600, fontSize: "0.95rem" }}>
                            {act.title}
                          </Link>
                          <p className="muted" style={{ margin: "0.2rem 0 0", fontSize: "0.82rem" }}>
                            {act.type} · {act.time} · {act.duration_hours}h · {act.location}
                          </p>
                        </div>
                        <span className="badge">{act.category}</span>
                      </div>
                      <p style={{ fontSize: "0.84rem", marginTop: "0.4rem", marginBottom: 0, color: "var(--purple-600)", fontStyle: "italic" }}>
                        {act.explanation}
                      </p>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Past plans */}
        {pastPlans.filter((p) => p.id !== plan.id).length > 0 && (
          <section style={{ marginTop: "3rem" }}>
            <h3>Past Plans</h3>
            <div className="stack" style={{ gap: "0.5rem" }}>
              {pastPlans
                .filter((p) => p.id !== plan.id)
                .map((p) => (
                  <div
                    key={p.id}
                    className="card card-compact card-hover row-between"
                    style={{ cursor: "pointer" }}
                    onClick={() => setPlan(p)}
                  >
                    <span style={{ fontWeight: 600 }}>{p.plan_type}-day plan</span>
                    <span className="muted">{new Date(p.created_at).toLocaleDateString()}</span>
                  </div>
                ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
