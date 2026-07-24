import { useNavigate } from "react-router-dom";

export default function ChoosePath() {
  const navigate = useNavigate();

  return (
    <div className="page">
      <div className="container">
        <div className="step-track">
          <span className="step-pill done">1. Account</span>
          <span className="step-pill done">2. Resume</span>
          <span className="step-pill active">3. Choose path</span>
        </div>

        <h2>What are you looking for today?</h2>
        <p>Choose the path that matches where you want to go next.</p>

        <div className="path-choice">
          <button className="card path-card" onClick={() => navigate("/jobs/recommended")}>
            <h3>🔁 Job Redeployment</h3>
            <p>Get matched to open roles in Singapore based on your resume, and apply in bulk.</p>
            <span className="btn btn-secondary">Explore jobs</span>
          </button>

          <button className="card path-card" onClick={() => navigate("/upskilling/goal")}>
            <h3>📈 Upskilling</h3>
            <p>Tell us your goal, time, and budget — we'll recommend courses and available SkillsFuture Credit.</p>
            <span className="btn btn-secondary">Explore courses</span>
          </button>
        </div>
      </div>
    </div>
  );
}
