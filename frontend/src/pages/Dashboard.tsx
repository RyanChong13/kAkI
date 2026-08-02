import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { GrowthPlanOut, LearningJourneyOut } from "../types";

export default function Dashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [growthPlans, setGrowthPlans] = useState<GrowthPlanOut[]>([]);
  const [learningJourneys, setLearningJourneys] = useState<LearningJourneyOut[]>([]);
  const [loading, setLoading] = useState(true);

  // Redirect organisers to their own dashboard
  useEffect(() => {
    if (user && user.role === "organiser") {
      navigate("/organiser", { replace: true });
    }
  }, [user, navigate]);

  useEffect(() => {
    Promise.all([
      api.get<GrowthPlanOut[]>("/api/ai/growth-plans").catch(() => []),
      api.get<LearningJourneyOut[]>("/api/ai/learning-journeys").catch(() => []),
    ]).then(([plans, journeys]) => {
      setGrowthPlans(plans);
      setLearningJourneys(journeys);
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
            <div className="stat-value">{growthPlans.length}</div>
            <div className="stat-label">Growth Plans</div>
          </div>
          <div className="card stat-card">
            <div className="stat-value">{learningJourneys.length}</div>
            <div className="stat-label">Learning Journeys</div>
          </div>
          <Link to="/growth-plan" style={{ textDecoration: "none" }}>
            <div className="card stat-card card-hover">
              <div className="stat-value">AI</div>
              <div className="stat-label">New Growth Plan</div>
            </div>
          </Link>
          <Link to="/learning-journey" style={{ textDecoration: "none" }}>
            <div className="card stat-card card-hover">
              <div className="stat-value">AI</div>
              <div className="stat-label">New Journey</div>
            </div>
          </Link>
        </div>

        {/* Quick actions */}
        <div className="row" style={{ gap: "0.75rem", marginBottom: "2rem" }}>
          <Link to="/growth-plan" className="btn btn-primary btn-sm">Generate Growth Plan</Link>
          <Link to="/learning-journey" className="btn btn-secondary btn-sm">Create Learning Journey</Link>
          <Link to="/courses" className="btn btn-ghost btn-sm">Browse Courses</Link>
          <Link to="/profile" className="btn btn-ghost btn-sm">Edit Profile</Link>
        </div>

        {/* Recent Growth Plans */}
        <section style={{ marginBottom: "2.5rem" }}>
          <div className="row-between" style={{ marginBottom: "1rem" }}>
            <h3 style={{ marginBottom: 0 }}>Your Growth Plans</h3>
            <Link to="/growth-plan" className="btn btn-ghost btn-sm">View all</Link>
          </div>

          {loading ? (
            <div style={{ display: "flex", justifyContent: "center", padding: "2rem" }}>
              <div className="spinner" />
            </div>
          ) : growthPlans.length > 0 ? (
            <div className="grid grid-3">
              {growthPlans.slice(0, 6).map((plan) => (
                <div key={plan.id} className="card card-hover">
                  <h4 style={{ margin: "0 0 0.5rem 0" }}>{plan.plan_type}-Day Plan</h4>
                  <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                    {plan.days.length} days of activities
                  </p>
                  <p className="muted" style={{ fontSize: "0.75rem", margin: "0.5rem 0 0 0" }}>
                    Created {new Date(plan.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
              <p className="muted">
                No growth plans yet. <Link to="/growth-plan">Create one</Link> to get started.
              </p>
            </div>
          )}
        </section>

        {/* Recent Learning Journeys */}
        <section>
          <div className="row-between" style={{ marginBottom: "1rem" }}>
            <h3 style={{ marginBottom: 0 }}>Your Learning Journeys</h3>
            <Link to="/learning-journey" className="btn btn-ghost btn-sm">View all</Link>
          </div>

          {learningJourneys.length === 0 ? (
            <div className="card" style={{ textAlign: "center", padding: "2rem" }}>
              <p className="muted" style={{ marginBottom: "0.5rem" }}>No learning journeys yet.</p>
              <Link to="/learning-journey" className="btn btn-secondary btn-sm">Create one</Link>
            </div>
          ) : (
            <div className="grid grid-3">
              {learningJourneys.slice(0, 6).map((journey) => (
                <div key={journey.id} className="card card-hover">
                  <h4 style={{ margin: "0 0 0.5rem 0" }}>{journey.goal}</h4>
                  <p className="muted" style={{ fontSize: "0.85rem", margin: 0 }}>
                    Week {journey.current_week} of {journey.total_weeks}
                  </p>
                  <p className="muted" style={{ fontSize: "0.75rem", margin: "0.5rem 0 0 0" }}>
                    Created {new Date(journey.created_at).toLocaleDateString()}
                  </p>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
