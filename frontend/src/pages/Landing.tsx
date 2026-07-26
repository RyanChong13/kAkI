import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const ROTATING_WORDS = ["events", "workshops", "skills", "networks", "careers"];

export default function Landing() {
  const { user } = useAuth();
  const [wordIdx, setWordIdx] = useState(0);
  const [fade, setFade] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setWordIdx((i) => (i + 1) % ROTATING_WORDS.length);
        setFade(true);
      }, 400);
    }, 2800);
    return () => clearInterval(interval);
  }, []);

  return (
    <>
      {/* Hero */}
      <section className="hero hero-animated">
        {/* Floating orbs */}
        <div className="hero-orbs">
          <div className="hero-orb orb-1" />
          <div className="hero-orb orb-2" />
          <div className="hero-orb orb-3" />
          <div className="hero-orb orb-4" />
          <div className="hero-orb orb-5" />
        </div>

        <div className="container" style={{ position: "relative", zIndex: 2 }}>
          <div className="hero-badge-row">
            <span className="badge hero-badge">AI-Powered Personal Growth Platform</span>
          </div>
          <h1 className="hero-title">
            Discover <span className="hero-word-swap">{/* keep space */}</span>
            <span className={`hero-rotating-word ${fade ? "visible" : ""}`}>
              {ROTATING_WORDS[wordIdx]}
            </span>
            ,<br />build skills, grow your career
          </h1>
          <p className="hero-subtitle">
            Your personalised growth journey starts here. Let AI match you to the right opportunities.
          </p>
          <div className="row" style={{ justifyContent: "center", marginTop: "1.5rem" }}>
            <Link to={user ? "/dashboard" : "/register"} className="btn btn-primary btn-hero">
              {user ? "Go to Dashboard" : "Get Started Free"}
            </Link>
            <Link to="/events" className="btn btn-secondary btn-hero">Browse Events</Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section style={{ padding: "3rem 0" }}>
        <div className="container">
          <h2 style={{ textAlign: "center", marginBottom: "2rem" }}>Everything you need to grow</h2>
          <div className="grid grid-3">
            {[
              { label: "AI", title: "AI Recommendations", desc: "Semantic matching finds events that truly fit your goals, not just keyword matches." },
              { label: "LJ", title: "Learning Journeys", desc: "AI generates week-by-week roadmaps towards your career goals." },
              { label: "GP", title: "Growth Plans", desc: "7, 14, or 30-day personalised plans balancing courses, networking, and hobbies." },
              { label: "SF", title: "Substitute Finder", desc: "Event full or cancelled? AI finds alternatives covering the same skills." },
              { label: "ML", title: "Multilingual Support", desc: "English, Mandarin, Malay, and Tamil -- listings, search, and AI chatbot." },
              { label: "AL", title: "AI Auto Listing", desc: "Organisers paste a description, AI generates a complete event listing." },
            ].map((f, i) => (
              <div key={f.title} className="card card-hover feature-card" style={{ animationDelay: `${i * 0.1}s` }}>
                <div style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: 40, height: 40, borderRadius: 12, background: "var(--purple-100)", color: "var(--purple-700)", fontWeight: 800, fontSize: "0.85rem", marginBottom: "0.75rem" }}>{f.label}</div>
                <h3 style={{ fontSize: "1.1rem" }}>{f.title}</h3>
                <p className="muted" style={{ fontSize: "0.9rem", marginBottom: 0 }}>{f.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Categories */}
      <section style={{ padding: "3rem 0", background: "var(--bg-subtle)" }}>
        <div className="container" style={{ textAlign: "center" }}>
          <h2>Browse events by category</h2>
          <p>From AI workshops to pottery classes, find what sparks your interest.</p>
          <div className="row" style={{ justifyContent: "center", gap: "0.6rem", marginTop: "1.5rem" }}>
            {["AI", "Software Engineering", "Cybersecurity", "Entrepreneurship", "Marketing", "Finance", "Design", "Leadership", "Public Speaking", "Networking", "Volunteering", "Sports", "Hobbies", "Career Development"].map((c, i) => (
              <Link key={c} to={`/events?category=${encodeURIComponent(c)}`} className="badge category-badge" style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem", animationDelay: `${i * 0.05}s` }}>{c}</Link>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section style={{ padding: "4rem 0" }}>
        <div className="container" style={{ textAlign: "center" }}>
          <h2 style={{ marginBottom: "0.5rem" }}>Ready to grow?</h2>
          <p className="muted" style={{ marginBottom: "1.5rem" }}>
            Join Nexa and let AI guide your personal and professional development.
          </p>
          {!user && (
            <Link to="/register" className="btn btn-primary btn-hero">Create your free account</Link>
          )}
        </div>
      </section>
    </>
  );
}
