import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Landing() {
  const { user } = useAuth();

  return (
    <div className="page">
      <div className="container" style={{ textAlign: "center", maxWidth: 720 }}>
        <span className="badge" style={{ marginBottom: "1rem" }}>
          Built for Singapore's workforce
        </span>
        <h1 style={{ fontSize: "2.4rem" }}>Find your next course, workshop, or career move</h1>
        <p style={{ fontSize: "1.05rem" }}>
          Discover SkillsFuture courses and live Singapore workshops in one place, or let us match your resume to
          jobs and upskilling paths that fit your goals.
        </p>
        <div className="row" style={{ justifyContent: "center", marginTop: "1.5rem" }}>
          <Link to={user ? "/choose-path" : "/register"} className="btn btn-primary">
            {user ? "Get started" : "Create your account"}
          </Link>
          <Link to="/courses" className="btn btn-secondary">
            Browse courses
          </Link>
        </div>
      </div>

      <div className="container grid grid-2" style={{ marginTop: "3.5rem" }}>
        <div className="card">
          <h3>📄 Upload your resume</h3>
          <p>We parse it to understand your skills so recommendations are tailored to you.</p>
        </div>
        <div className="card">
          <h3>🧭 Choose your path</h3>
          <p>Job redeployment or upskilling — pick the direction that matches where you're headed.</p>
        </div>
        <div className="card">
          <h3>🎯 Get matched</h3>
          <p>See recommended jobs or courses, ranked by how well they fit your skills and goals.</p>
        </div>
        <div className="card">
          <h3>💳 Claim your credit</h3>
          <p>We surface SkillsFuture Credit eligibility so you know what's subsidized before you commit.</p>
        </div>
      </div>
    </div>
  );
}
