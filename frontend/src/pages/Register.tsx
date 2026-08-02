import { useState, type FormEvent } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ApiError } from "../api/client";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [role, setRole] = useState<"public" | "organiser">("public");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const newUser = await register(email, password, name, role);
      if (newUser.role === "organiser") {
        navigate("/organiser");
      } else {
        navigate("/onboarding");
      }
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Something went wrong. Please try again.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page">
      <div className="container">
        <div className="card center-form">
          <h2>Create your account</h2>
          <p className="muted">Join Nexa — your AI-powered growth platform.</p>

          {error && <div className="notice notice-error">{error}</div>}

          <form onSubmit={handleSubmit} className="stack">
            <div className="field">
              <label htmlFor="name">Full name</label>
              <input id="name" type="text" value={name} onChange={(e) => setName(e.target.value)} required />
            </div>
            <div className="field">
              <label htmlFor="email">Email</label>
              <input id="email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </div>
            <div className="field">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                minLength={8}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
              />
              <span className="muted">At least 8 characters.</span>
            </div>
            <div className="field">
              <label>I am a...</label>
              <div className="row" style={{ gap: "0.5rem" }}>
                <button
                  type="button"
                  className={`btn ${role === "public" ? "btn-primary" : "btn-ghost"} btn-sm`}
                  onClick={() => setRole("public")}
                >
                  Public User
                </button>
                <button
                  type="button"
                  className={`btn ${role === "organiser" ? "btn-primary" : "btn-ghost"} btn-sm`}
                  onClick={() => setRole("organiser")}
                >
                  Event Organiser
                </button>
              </div>
            </div>
            <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
              {loading ? "Creating account…" : "Create account"}
            </button>
          </form>

          <p className="muted" style={{ marginTop: "1.25rem", textAlign: "center" }}>
            Already have an account? <Link to="/login">Log in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
