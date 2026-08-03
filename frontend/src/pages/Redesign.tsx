import { useEffect, useMemo, useState } from "react";
import { api, ApiError } from "../api/client";
import type { RedesignResult, RedesignSuggestion, RoleListResponse, RoleOut, SchemeInfo } from "../types";

const IMPACT_STYLES: Record<string, { label: string; cls: string }> = {
  augment: { label: "Augment", cls: "badge-success" },
  automate: { label: "Automate", cls: "badge-warning" },
  transform: { label: "Transform", cls: "badge-danger" },
};

export default function Redesign() {
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [roleInput, setRoleInput] = useState("");
  const [age, setAge] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RedesignResult | null>(null);
  const [showDropdown, setShowDropdown] = useState(false);

  useEffect(() => {
    api.get<RoleListResponse>("/api/roles")
      .then(res => setRoles(res.roles))
      .catch(() => {});
  }, []);

  const filteredRoles = useMemo(() => {
    const q = roleInput.toLowerCase().trim();
    if (!q) return roles.slice(0, 8);
    return roles
      .filter(r => r.title.toLowerCase().includes(q) || r.category.toLowerCase().includes(q))
      .slice(0, 8);
  }, [roles, roleInput]);

  function handleGenerate() {
    if (!roleInput.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setShowDropdown(false);

    const body = { role: roleInput.trim(), ...(age ? { age: Number(age) } : {}) };
    api.post<RedesignResult>("/api/redesign", body)
      .then(setResult)
      .catch((err: unknown) => {
        const msg = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
        setError(msg);
      })
      .finally(() => setLoading(false));
  }

  function selectRole(role: RoleOut) {
    setRoleInput(role.title);
    setShowDropdown(false);
  }

  return (
    <>
      {/* Hero / Input */}
      <section className="hero" style={{ padding: "4rem 0 3rem" }}>
        <div className="container" style={{ position: "relative", zIndex: 2, textAlign: "center" }}>
          <span className="badge" style={{ marginBottom: "1rem" }}>AI Career Redesign</span>
          <h1 style={{ fontSize: "2.6rem", fontWeight: 900, marginBottom: "1rem" }}>
            How will AI change <span style={{ color: "var(--purple-600)" }}>your role?</span>
          </h1>
          <p style={{ fontSize: "1.15rem", maxWidth: 580, margin: "0 auto 2rem" }}>
            Enter your job title. Get AI-augmented redesign directions, matched SkillsFuture courses,
            and the funding schemes you're eligible for.
          </p>

          {/* Input form */}
          <div style={{ maxWidth: 560, margin: "0 auto", position: "relative" }}>
            <div className="row" style={{ gap: "0.75rem", alignItems: "flex-end" }}>
              <div className="field" style={{ flex: 1, marginBottom: 0, position: "relative" }}>
                <label htmlFor="role">Your role</label>
                <input
                  id="role"
                  type="text"
                  placeholder="e.g. Data Analyst, Nurse, HR Executive"
                  value={roleInput}
                  onChange={e => { setRoleInput(e.target.value); setShowDropdown(true); }}
                  onFocus={() => setShowDropdown(true)}
                  onKeyDown={e => { if (e.key === "Enter") handleGenerate(); }}
                  style={{ width: "100%" }}
                />
                {showDropdown && filteredRoles.length > 0 && (
                  <div style={{
                    position: "absolute", top: "100%", left: 0, right: 0,
                    background: "var(--bg-card)", border: "1px solid var(--border)",
                    borderRadius: "0 0 14px 14px", boxShadow: "var(--shadow-lg)",
                    zIndex: 30, textAlign: "left", maxHeight: 320, overflowY: "auto",
                  }}>
                    {filteredRoles.map(r => (
                      <button
                        key={r.id}
                        onClick={() => selectRole(r)}
                        style={{
                          display: "block", width: "100%", padding: "0.7rem 1rem",
                          border: "none", background: "transparent", textAlign: "left",
                          cursor: "pointer", borderBottom: "1px solid var(--border)",
                          color: "var(--ink-900)", fontWeight: 600, fontSize: "0.9rem",
                        }}
                      >
                        {r.title}
                        <span className="muted" style={{ marginLeft: "0.5rem", fontWeight: 400, fontSize: "0.8rem" }}>
                          {r.category}
                        </span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              <div className="field" style={{ width: 90, marginBottom: 0 }}>
                <label htmlFor="age">Age</label>
                <input
                  id="age"
                  type="number"
                  placeholder="—"
                  value={age}
                  onChange={e => setAge(e.target.value)}
                  min={0}
                  max={120}
                />
              </div>
            </div>
            <button
              className="btn btn-primary btn-block"
              onClick={handleGenerate}
              disabled={loading || !roleInput.trim()}
              style={{ marginTop: "1rem" }}
            >
              {loading ? (
                <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Generating…</>
              ) : (
                "Generate Redesign"
              )}
            </button>
          </div>
        </div>
      </section>

      {/* Error */}
      {error && (
        <div className="container" style={{ paddingTop: "1rem" }}>
          <div className="notice notice-error">{error}</div>
        </div>
      )}

      {/* Loading hint */}
      {loading && (
        <div className="container" style={{ textAlign: "center", padding: "2rem 0" }}>
          <p className="muted">Claude is analysing how AI transforms this role and matching SkillsFuture courses…</p>
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="container page" style={{ paddingTop: "1rem" }}>
          {/* Role header */}
          <div style={{ marginBottom: "2rem" }}>
            <h2 style={{ fontSize: "1.6rem" }}>{result.role}</h2>
            <div className="row" style={{ gap: "0.5rem" }}>
              <span className="badge">{result.role_category}</span>
              <span className="muted">{result.suggestions.length} redesign directions</span>
            </div>
            {result.role_core_tasks.length > 0 && (
              <details style={{ marginTop: "0.75rem" }}>
                <summary className="muted" style={{ cursor: "pointer", fontWeight: 600 }}>Core tasks for this role</summary>
                <ul style={{ marginTop: "0.5rem", color: "var(--ink-700)", paddingLeft: "1.5rem" }}>
                  {result.role_core_tasks.map((t, i) => <li key={i} style={{ marginBottom: "0.25rem" }}>{t}</li>)}
                </ul>
              </details>
            )}
          </div>

          {/* Suggestion cards */}
          <div className="stack">
            {result.suggestions.map((s, i) => (
              <SuggestionCard key={i} suggestion={s} />
            ))}
          </div>

          {/* Disclaimer */}
          <div className="notice" style={{ marginTop: "2rem", fontSize: "0.85rem" }}>
            Scheme eligibility is estimated using heuristics for this prototype. Always verify on{" "}
            <a href="https://www.myskillsfuture.gov.sg" target="_blank" rel="noopener noreferrer">MySkillsFuture</a>{" "}
            before enrolling. Schemes change every Budget cycle.
          </div>
        </div>
      )}
    </>
  );
}


function SuggestionCard({ suggestion }: { suggestion: RedesignSuggestion }) {
  const [expanded, setExpanded] = useState(false);
  const impact = IMPACT_STYLES[suggestion.ai_impact] || IMPACT_STYLES.augment;

  return (
    <div className="card">
      {/* Header */}
      <div className="row-between" style={{ marginBottom: "0.75rem" }}>
        <h3 style={{ fontSize: "1.25rem", margin: 0 }}>{suggestion.title}</h3>
        <div className="row" style={{ gap: "0.4rem" }}>
          <span className={`badge ${impact.cls}`}>{impact.label}</span>
          <span className="badge badge-outline">{suggestion.estimated_timeframe}</span>
        </div>
      </div>

      <p style={{ marginBottom: "0.75rem" }}>{suggestion.description}</p>

      <div style={{ background: "var(--bg-subtle)", borderRadius: "var(--radius-sm)", padding: "0.75rem 1rem", marginBottom: "0.75rem" }}>
        <strong style={{ fontSize: "0.85rem", color: "var(--ink-500)" }}>Why this makes sense</strong>
        <p style={{ margin: "0.25rem 0 0", fontSize: "0.92rem" }}>{suggestion.why}</p>
      </div>

      {/* Upskilling areas */}
      <div style={{ marginBottom: "0.75rem" }}>
        <strong style={{ fontSize: "0.85rem", color: "var(--ink-500)" }}>Upskilling areas</strong>
        <div className="tags" style={{ marginTop: "0.4rem" }}>
          {suggestion.upskilling_areas.map((area, i) => (
            <span key={i} className="badge" style={{ background: "var(--purple-100)", color: "var(--purple-700)" }}>{area}</span>
          ))}
        </div>
      </div>

      {/* Matched courses */}
      {suggestion.matched_courses.length > 0 && (
        <div>
          <button
            className="btn btn-ghost btn-sm"
            onClick={() => setExpanded(!expanded)}
            style={{ marginBottom: "0.5rem" }}
          >
            {expanded ? "Hide" : "Show"} {suggestion.matched_courses.length} matched course{suggestion.matched_courses.length > 1 ? "s" : ""}
          </button>

          {expanded && (
            <div className="stack">
              {suggestion.matched_courses.map((mc, i) => (
                <CourseMatch key={i} match={mc} />
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}


function CourseMatch({ match }: { match: RedesignResult["suggestions"][0]["matched_courses"][0] }) {
  const { course, match_score, matched_skills, schemes } = match;
  const eligibleSchemes = schemes.filter(s => s.eligible);
  const ineligibleSchemes = schemes.filter(s => !s.eligible);

  return (
    <div className="card card-compact" style={{ border: "1px solid var(--border)" }}>
      <div className="row-between" style={{ marginBottom: "0.4rem" }}>
        <div>
          <strong style={{ fontSize: "0.95rem" }}>{course.title}</strong>
          <span className="muted" style={{ marginLeft: "0.5rem", fontSize: "0.8rem" }}>{course.provider}</span>
        </div>
        <span className="badge badge-outline" title="Match score">
          {Math.round(match_score * 100)}% match
        </span>
      </div>

      {/* Matched skills */}
      {matched_skills.length > 0 && (
        <div className="tags" style={{ marginBottom: "0.5rem" }}>
          {matched_skills.map((s, i) => (
            <span key={i} className="badge badge-success" style={{ fontSize: "0.7rem" }}>{s}</span>
          ))}
        </div>
      )}

      {/* Fee + scheme badges */}
      <div className="row" style={{ gap: "0.5rem", marginBottom: "0.5rem" }}>
        <span className="muted" style={{ fontSize: "0.85rem" }}>
          {course.full_price_sgd > 0 && `Full fee: $${course.full_price_sgd.toFixed(0)}`}
          {course.full_price_sgd > course.price_sgd && ` → Payable: $${course.price_sgd.toFixed(0)}`}
        </span>
      </div>

      {/* Eligible schemes */}
      {eligibleSchemes.length > 0 && (
        <div style={{ marginBottom: "0.4rem" }}>
          <strong style={{ fontSize: "0.8rem", color: "var(--ink-500)" }}>Eligible funding:</strong>
          <div className="tags" style={{ marginTop: "0.3rem" }}>
            {eligibleSchemes.map(s => (
              <SchemeBadge key={s.scheme_id} scheme={s} />
            ))}
          </div>
        </div>
      )}

      {/* Ineligible schemes (collapsed) */}
      {ineligibleSchemes.length > 0 && (
        <details style={{ marginTop: "0.25rem" }}>
          <summary className="muted" style={{ cursor: "pointer", fontSize: "0.8rem" }}>
            {ineligibleSchemes.length} scheme(s) you may not qualify for
          </summary>
          <div className="tags" style={{ marginTop: "0.3rem" }}>
            {ineligibleSchemes.map(s => (
              <SchemeBadge key={s.scheme_id} scheme={s} />
            ))}
          </div>
        </details>
      )}

      {/* CTA */}
      {course.url && (
        <a
          href={course.url}
          target="_blank"
          rel="noopener noreferrer"
          className="btn btn-secondary btn-sm"
          style={{ marginTop: "0.5rem" }}
        >
          View on MySkillsFuture →
        </a>
      )}
    </div>
  );
}


function SchemeBadge({ scheme }: { scheme: SchemeInfo }) {
  const cls = scheme.eligible ? "badge-success" : "badge-danger";
  const credit = scheme.credit_amount_sgd
    ? `$${scheme.credit_amount_sgd.toFixed(0)}`
    : scheme.scheme_id === "sctp" ? "Up to 90% subsidy" : "Allowance";
  return (
    <span
      className={`badge ${cls}`}
      title={`${scheme.scheme_name}: ${scheme.age_note || scheme.eligibility_notes}`}
      style={{ fontSize: "0.7rem" }}
    >
      {scheme.scheme_name} ({credit})
    </span>
  );
}
