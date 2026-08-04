import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Landing() {
  const { user } = useAuth();

  return (
    <>
      {/* Hero */}
      <section className="hero hero-animated" style={{ overflow: "visible" }}>
        <div className="hero-orbs" style={{ overflow: "hidden" }}>
          <div className="hero-orb orb-1" />
          <div className="hero-orb orb-2" />
          <div className="hero-orb orb-3" />
        </div>
        <div className="container" style={{ position: "relative", zIndex: 2 }}>
          <div className="hero-badge-row">
            <span className="badge hero-badge" style={{ background: "var(--purple-100)", color: "var(--purple-700)" }}>
              AI Career Redesign
            </span>
          </div>
          <h1 className="hero-title" style={{ fontSize: "3.2rem", fontWeight: 900, letterSpacing: "-0.03em", marginBottom: "1.25rem" }}>
            Don't let AI replace you.
            <br />
            <span style={{ color: "var(--purple-600)" }}>Redesign your role.</span>
          </h1>
          <p className="hero-subtitle">
            See exactly how AI will change your job, get a practical plan to stay
            ahead, and find MySkillsFuture courses with funding you can claim — all
            in minutes.
          </p>
          <div className="btn-hero" style={{ display: "flex", gap: "0.75rem", justifyContent: "center", flexWrap: "wrap" }}>
            <Link to="/redesign" className="btn btn-primary" style={{ fontSize: "1rem", padding: "0.9rem 2rem" }}>
              {user ? "Start redesigning" : "Try it free"}
            </Link>
            {!user && (
              <Link to="/register" className="btn btn-ghost" style={{ fontSize: "1rem", padding: "0.9rem 2rem" }}>
                Create account
              </Link>
            )}
          </div>
          <p className="muted" style={{ marginTop: "1.5rem", fontSize: "0.85rem", opacity: 0.7 }}>
            No sign-up needed to try · Powered by live MySkillsFuture data
          </p>
        </div>
      </section>

      {/* How it works */}
      <section className="container" style={{ paddingTop: "2rem", paddingBottom: "3rem" }}>
        <h2 style={{ fontSize: "1.8rem", fontWeight: 800, textAlign: "center", marginBottom: "0.5rem" }}>
          Three steps to a future-proof career
        </h2>
        <p className="muted" style={{ textAlign: "center", maxWidth: 520, margin: "0 auto 2.5rem" }}>
          No fluff. No generic advice. Just a clear plan tailored to your role.
        </p>

        <div className="grid" style={{ marginBottom: 0, gridTemplateColumns: "repeat(3, 1fr)" }}>
          {[
            { num: "1", title: "Tell us your role", desc: "Type your job title or upload your resume. We identify your skills and how AI is changing your field." },
            { num: "2", title: "Get your redesign", desc: "AI shows you practical ways to reshape your role around AI — with tasks it can augment, automate, or transform." },
            { num: "3", title: "Learn & claim funding", desc: "Browse matched MySkillsFuture courses and see exactly which funding schemes you're eligible for." },
          ].map((step, i) => (
            <div
              key={step.num}
              className="card feature-card"
              style={{ animationDelay: `${0.6 + i * 0.15}s`, textAlign: "center" }}
            >
              <div style={{
                width: 48, height: 48, borderRadius: "50%",
                background: "var(--purple-100)", color: "var(--purple-700)",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.3rem", fontWeight: 800, margin: "0 auto 1rem",
              }}>
                {step.num}
              </div>
              <h3 style={{ fontSize: "1.1rem", fontWeight: 700, marginBottom: "0.5rem" }}>{step.title}</h3>
              <p className="muted" style={{ fontSize: "0.9rem", margin: 0 }}>{step.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section style={{ background: "var(--bg-subtle)", padding: "2rem 0" }}>
        <div className="container">
          <h2 style={{ fontSize: "1.8rem", fontWeight: 800, textAlign: "center", marginBottom: "1.5rem" }}>
            Built for Singapore's workforce
          </h2>
          <div className="grid" style={{ gridTemplateColumns: "repeat(2, 1fr)", maxWidth: 760, margin: "0 auto" }}>
            {[
              { icon: "🎯", title: "Role-specific, not generic", desc: "We analyse the actual tasks in your job and show how AI changes each one — augment, automate, or evolve." },
              { icon: "📚", title: "Live MySkillsFuture courses", desc: "Course recommendations pulled directly from MySkillsFuture, matched to the exact skills you need to build." },
              { icon: "💰", title: "Funding you can actually claim", desc: "See your eligibility for SkillsFuture Credit, Mid-Career Credit, and SCTP subsidies based on your age." },
              { icon: "🔖", title: "Save & revisit your plans", desc: "Bookmark redesign plans to your account and pick up where you left off on any device." },
            ].map((feat, i) => (
              <div
                key={feat.title}
                className="card feature-card"
                style={{ animationDelay: `${0.1 + i * 0.12}s`, display: "flex", gap: "1rem", alignItems: "flex-start" }}
              >
                <span style={{ fontSize: "1.8rem", lineHeight: 1, flexShrink: 0 }}>{feat.icon}</span>
                <div>
                  <h3 style={{ fontSize: "1.05rem", fontWeight: 700, marginBottom: "0.35rem" }}>{feat.title}</h3>
                  <p className="muted" style={{ fontSize: "0.9rem", margin: 0 }}>{feat.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="container" style={{ padding: "4rem 1.5rem", textAlign: "center" }}>
        <h2 style={{ fontSize: "2rem", fontWeight: 800, marginBottom: "0.75rem" }}>
          Ready to see what's next?
        </h2>
        <p className="muted" style={{ maxWidth: 480, margin: "0 auto 2rem" }}>
          It takes 30 seconds to get started. No account required to try.
        </p>
        <Link to="/redesign" className="btn btn-primary" style={{ fontSize: "1.05rem", padding: "1rem 2.5rem" }}>
          Generate my AI career redesign →
        </Link>
      </section>

      {/* Footer */}
      <footer style={{ borderTop: "1px solid var(--border)", padding: "2rem 0" }}>
        <div className="container" style={{ textAlign: "center" }}>
          <strong style={{ fontSize: "1.1rem" }}>Nexa</strong>
          <p className="muted" style={{ fontSize: "0.85rem", margin: "0.25rem 0 0" }}>
            AI-powered career redesign for Singapore's workforce
          </p>
        </div>
      </footer>
    </>
  );
}
