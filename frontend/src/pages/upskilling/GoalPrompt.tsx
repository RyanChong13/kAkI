import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import type { CourseRecommendation } from "../../types";

export default function GoalPrompt() {
  const navigate = useNavigate();
  const [goalText, setGoalText] = useState("");
  const [timeCommitment, setTimeCommitment] = useState("<5 hrs/week");
  const [maxCost, setMaxCost] = useState("");
  const [scope, setScope] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const recommendations = await api.post<CourseRecommendation[]>("/api/courses/recommendations", {
        goal_text: goalText,
        time_commitment: timeCommitment,
        max_cost_sgd: maxCost ? Number(maxCost) : null,
        scope,
      });
      navigate("/upskilling/courses", { state: { recommendations } });
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not get recommendations. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <h2>What do you want to achieve?</h2>
        <p>Tell us your goal, time commitment, and budget — we'll recommend courses that fit.</p>

        {error && <div className="notice notice-error">{error}</div>}

        <form onSubmit={handleSubmit} className="card stack" style={{ maxWidth: 640 }}>
          <div className="field">
            <label htmlFor="goal">What do you want to achieve?</label>
            <textarea
              id="goal"
              placeholder="e.g. I want to move into a data analytics role"
              value={goalText}
              onChange={(e) => setGoalText(e.target.value)}
              required
            />
          </div>

          <div className="field">
            <label htmlFor="scope">Scope (optional)</label>
            <input
              id="scope"
              type="text"
              placeholder="e.g. Python, SQL, dashboards"
              value={scope}
              onChange={(e) => setScope(e.target.value)}
            />
          </div>

          <div className="row" style={{ gap: "1.5rem" }}>
            <div className="field" style={{ flex: 1, minWidth: 180 }}>
              <label htmlFor="time">Time commitment</label>
              <select id="time" value={timeCommitment} onChange={(e) => setTimeCommitment(e.target.value)}>
                <option>&lt;5 hrs/week</option>
                <option>5-10 hrs/week</option>
                <option>10-20 hrs/week</option>
                <option>Full-time</option>
              </select>
            </div>
            <div className="field" style={{ flex: 1, minWidth: 180 }}>
              <label htmlFor="cost">Max cost (SGD, optional)</label>
              <input id="cost" type="number" min={0} value={maxCost} onChange={(e) => setMaxCost(e.target.value)} />
            </div>
          </div>

          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? "Finding courses…" : "Get recommendations"}
          </button>
        </form>
      </div>
    </div>
  );
}
