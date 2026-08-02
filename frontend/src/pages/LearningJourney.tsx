import { useEffect, useState } from "react";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { LearningJourneyOut } from "../types";

export default function LearningJourney() {
  const { user } = useAuth();
  const [journey, setJourney] = useState<LearningJourneyOut | null>(null);
  const [pastJourneys, setPastJourneys] = useState<LearningJourneyOut[]>([]);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  // Form state
  const [goal, setGoal] = useState("");
  const [weeks, setWeeks] = useState(4);

  useEffect(() => {
    api
      .get<LearningJourneyOut[]>("/api/ai/learning-journeys")
      .then((journeys) => {
        setPastJourneys(journeys);
        if (journeys.length > 0) setJourney(journeys[0]);
      })
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [user]);

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault();
    if (!goal.trim()) return;
    setGenerating(true);
    try {
      const result = await api.post<LearningJourneyOut>("/api/ai/learning-journey", { goal, weeks });
      setJourney(result);
      setPastJourneys((prev) => [result, ...prev]);
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

  // Phase A: Goal input form
  if (!journey) {
    return (
      <div className="page">
        <div className="container" style={{ maxWidth: 640 }}>
          <h2>Create Your Learning Journey</h2>
          <p className="muted">
            Describe your career goal and AI will build a week-by-week roadmap to help you get there.
          </p>

          <form onSubmit={handleGenerate} className="stack">
            <div className="field">
              <label>Your Goal</label>
              <textarea
                value={goal}
                onChange={(e) => setGoal(e.target.value)}
                placeholder="e.g. Become a full-stack developer in 3 months"
                required
                style={{ minHeight: 120 }}
              />
            </div>
            <div className="field">
              <label>Duration: {weeks} week{weeks > 1 ? "s" : ""}</label>
              <input
                type="range"
                min={1}
                max={12}
                value={weeks}
                onChange={(e) => setWeeks(parseInt(e.target.value))}
                style={{ width: "100%", accentColor: "var(--purple-600)" }}
              />
              <div className="row-between" style={{ fontSize: "0.8rem" }}>
                <span className="muted">1 week</span>
                <span className="muted">12 weeks</span>
              </div>
            </div>

            {/* Example goals */}
            <div className="notice" style={{ fontSize: "0.88rem" }}>
              <strong>Example goals:</strong>
              <div className="row" style={{ gap: "0.5rem", marginTop: "0.5rem" }}>
                {["Become an AI Product Manager", "Transition to cybersecurity", "Build leadership skills", "Master cloud architecture"].map((ex) => (
                  <button
                    key={ex}
                    type="button"
                    className="btn btn-ghost btn-sm"
                    onClick={() => setGoal(ex)}
                    style={{ fontSize: "0.8rem" }}
                  >
                    {ex}
                  </button>
                ))}
              </div>
            </div>

            <button type="submit" className="btn btn-primary btn-block" disabled={generating || !goal.trim()}>
              {generating ? "Generating roadmap..." : "Generate Journey"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  // Phase B: Roadmap display
  return (
    <div className="page">
      <div className="container">
        <div className="row-between" style={{ marginBottom: "1rem" }}>
          <div>
            <h2 style={{ marginBottom: "0.25rem" }}>{journey.goal}</h2>
            <p className="muted" style={{ marginBottom: 0 }}>
              {journey.total_weeks}-week learning journey · Created {new Date(journey.created_at).toLocaleDateString()}
            </p>
          </div>
          <button className="btn btn-ghost btn-sm" onClick={() => setJourney(null)}>
            New Journey
          </button>
        </div>

        {/* Progress */}
        <div className="row" style={{ marginBottom: "1.5rem", gap: "1rem" }}>
          <span className="badge">Week {journey.current_week} of {journey.total_weeks}</span>
          <div className="progress-bar" style={{ flex: 1 }}>
            <div
              className="progress-bar-fill"
              style={{ width: `${(journey.current_week / journey.total_weeks) * 100}%` }}
            />
          </div>
        </div>

        {/* Week-by-week timeline */}
        <div className="timeline">
          {journey.roadmap.map((week) => (
            <div key={week.week} className="timeline-item">
              <div className="row-between" style={{ marginBottom: "0.3rem" }}>
                <h4 style={{ marginBottom: 0 }}>Week {week.week}: {week.title}</h4>
                <span className={`badge ${week.week <= journey.current_week ? "badge-success" : ""}`}>
                  {week.week <= journey.current_week ? "Done" : "Upcoming"}
                </span>
              </div>
              <p className="muted" style={{ fontSize: "0.88rem", marginBottom: "0.75rem" }}>
                Focus: {week.focus}
              </p>
            </div>
          ))}
        </div>

        {/* Past journeys */}
        {pastJourneys.filter((j) => j.id !== journey.id).length > 0 && (
          <section style={{ marginTop: "3rem" }}>
            <h3>Past Journeys</h3>
            <div className="stack" style={{ gap: "0.5rem" }}>
              {pastJourneys
                .filter((j) => j.id !== journey.id)
                .map((j) => (
                  <div
                    key={j.id}
                    className="card card-compact card-hover row-between"
                    style={{ cursor: "pointer" }}
                    onClick={() => setJourney(j)}
                  >
                    <span style={{ fontWeight: 600 }}>{j.goal}</span>
                    <span className="muted">{j.total_weeks} weeks · {new Date(j.created_at).toLocaleDateString()}</span>
                  </div>
                ))}
            </div>
          </section>
        )}
      </div>
    </div>
  );
}
