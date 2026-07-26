import { useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { ResumeAnalysisResult } from "../types";

const TOTAL_STEPS = 4;

export default function Onboarding() {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();
  const fileRef = useRef<HTMLInputElement>(null);

  const [step, setStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Step 1: Profile
  const [name, setName] = useState(user?.name || "");
  const [linkedinUrl, setLinkedinUrl] = useState(user?.linkedin_url || "");

  // Step 2: Resume
  const [fileName, setFileName] = useState("");
  const [analysis, setAnalysis] = useState<ResumeAnalysisResult | null>(null);

  // Step 3: Interests & goals
  const [interests, setInterests] = useState(user?.interests || "");
  const [careerGoals, setCareerGoals] = useState(user?.career_goals || "");

  // Step 4: Preferences
  const [preferredTimings, setPreferredTimings] = useState(user?.preferred_timings || "");
  const [availabilityHours, setAvailabilityHours] = useState(String(user?.availability_hours_per_week ?? 5));
  const [budget, setBudget] = useState(String(user?.budget_sgd ?? 200));

  async function handleResumeUpload(file: File) {
    setFileName(file.name);
    setLoading(true);
    setError(null);
    const form = new FormData();
    form.append("file", file);
    try {
      const result = await api.postForm<ResumeAnalysisResult>("/api/resume/analyse", form);
      setAnalysis(result);
      // Auto-fill interests from analysis
      if (result.extracted_interests.length > 0 && !interests) {
        setInterests(result.extracted_interests.join(", "));
      }
      if (result.extracted_skills.length > 0 && !careerGoals) {
        setCareerGoals(`Build on my ${result.extracted_skills.slice(0, 5).join(", ")} skills`);
      }
    } catch {
      setError("Could not analyse resume. You can skip this step.");
    } finally {
      setLoading(false);
    }
  }

  async function next() {
    setError(null);
    if (step < TOTAL_STEPS) {
      setStep(step + 1);
    } else {
      // Final step: save everything
      setLoading(true);
      try {
        await updateUser({
          name,
          linkedin_url: linkedinUrl,
          interests,
          career_goals: careerGoals,
          preferred_timings: preferredTimings,
          availability_hours_per_week: parseFloat(availabilityHours) || 5,
          budget_sgd: parseFloat(budget) || 200,
        });
        navigate("/dashboard");
      } catch (err) {
        setError(err instanceof Error ? err.message : "Failed to save. Please try again.");
      } finally {
        setLoading(false);
      }
    }
  }

  function skip() {
    if (step < TOTAL_STEPS) {
      setStep(step + 1);
    } else {
      navigate("/dashboard");
    }
  }

  return (
    <div className="page">
      <div className="container">
        <div className="onboard-wrapper">
          {/* Progress dots */}
          <div className="onboard-progress">
            {Array.from({ length: TOTAL_STEPS }, (_, i) => (
              <div
                key={i}
                className={`onboard-dot ${i + 1 === step ? "active" : i + 1 < step ? "done" : ""}`}
              />
            ))}
          </div>

          <div className="onboard-step">
            {step === 1 && (
              <>
                <h2 style={{ marginBottom: "0.5rem" }}>Tell us about yourself</h2>
                <p className="muted" style={{ marginBottom: "1.5rem" }}>
                  This helps us personalise your experience.
                </p>
                <div className="stack">
                  <div className="field">
                    <label>Your Name</label>
                    <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" />
                  </div>
                  <div className="field">
                    <label>LinkedIn Profile URL</label>
                    <input
                      type="url"
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                      placeholder="https://linkedin.com/in/yourname"
                    />
                    <span className="muted" style={{ fontSize: "0.8rem" }}>
                      We use your LinkedIn to understand your professional background.
                    </span>
                  </div>
                </div>
              </>
            )}

            {step === 2 && (
              <>
                <h2 style={{ marginBottom: "0.5rem" }}>Upload your resume</h2>
                <p className="muted" style={{ marginBottom: "1.5rem" }}>
                  We analyse your resume to discover your skills and suggest relevant events.
                </p>
                <div
                  className={`upload-zone ${fileName ? "has-file" : ""}`}
                  onClick={() => fileRef.current?.click()}
                >
                  <input
                    ref={fileRef}
                    type="file"
                    accept=".pdf,.txt,.doc,.docx"
                    style={{ display: "none" }}
                    onChange={(e) => {
                      const f = e.target.files?.[0];
                      if (f) handleResumeUpload(f);
                    }}
                  />
                  {loading ? (
                    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "0.75rem" }}>
                      <div className="spinner" />
                      <span className="muted">Analysing your resume...</span>
                    </div>
                  ) : fileName ? (
                    <div>
                      <p style={{ fontWeight: 700, marginBottom: "0.3rem" }}>{fileName}</p>
                      {analysis && (
                        <p className="muted" style={{ fontSize: "0.85rem", marginBottom: 0 }}>{analysis.summary}</p>
                      )}
                    </div>
                  ) : (
                    <div>
                      <p style={{ fontWeight: 700, marginBottom: "0.3rem" }}>Drop your resume here or click to browse</p>
                      <span className="muted">Supports PDF, TXT, DOC (max 10MB)</span>
                    </div>
                  )}
                </div>

                {analysis && analysis.extracted_skills.length > 0 && (
                  <div className="card" style={{ marginTop: "1rem", background: "var(--bg-subtle)" }}>
                    <h4 style={{ marginBottom: "0.5rem" }}>Skills Detected</h4>
                    <div className="tags">
                      {analysis.extracted_skills.map((s) => (
                        <span key={s} className="badge">{s}</span>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}

            {step === 3 && (
              <>
                <h2 style={{ marginBottom: "0.5rem" }}>Your interests and goals</h2>
                <p className="muted" style={{ marginBottom: "1.5rem" }}>
                  Help us find the right events and learning paths for you.
                </p>
                <div className="stack">
                  <div className="field">
                    <label>Interests</label>
                    <textarea
                      value={interests}
                      onChange={(e) => setInterests(e.target.value)}
                      placeholder="e.g. AI, data science, public speaking, design thinking"
                    />
                    {analysis && analysis.suggested_categories.length > 0 && (
                      <div className="row" style={{ gap: "0.4rem", marginTop: "0.5rem" }}>
                        <span className="muted" style={{ fontSize: "0.8rem" }}>Suggested:</span>
                        {analysis.suggested_categories.map((c) => (
                          <button
                            key={c}
                            type="button"
                            className="btn btn-ghost btn-sm"
                            style={{ fontSize: "0.75rem" }}
                            onClick={() =>
                              setInterests((prev) =>
                                prev.toLowerCase().includes(c.toLowerCase()) ? prev : `${prev}, ${c}`.trim().replace(/^,\s*/, "")
                              )
                            }
                          >
                            {c}
                          </button>
                        ))}
                      </div>
                    )}
                  </div>
                  <div className="field">
                    <label>Career Goals</label>
                    <textarea
                      value={careerGoals}
                      onChange={(e) => setCareerGoals(e.target.value)}
                      placeholder="e.g. Transition into product management within 6 months"
                    />
                  </div>
                </div>
              </>
            )}

            {step === 4 && (
              <>
                <h2 style={{ marginBottom: "0.5rem" }}>Your preferences</h2>
                <p className="muted" style={{ marginBottom: "1.5rem" }}>
                  This helps us recommend events that fit your schedule and budget.
                </p>
                <div className="stack">
                  <div className="field">
                    <label>Preferred Timings</label>
                    <input
                      value={preferredTimings}
                      onChange={(e) => setPreferredTimings(e.target.value)}
                      placeholder="e.g. Weekday evenings, Saturday mornings"
                    />
                  </div>
                  <div className="row" style={{ gap: "1rem" }}>
                    <div className="field" style={{ flex: 1 }}>
                      <label>Availability (hours/week)</label>
                      <input
                        type="number"
                        min={0}
                        max={168}
                        value={availabilityHours}
                        onChange={(e) => setAvailabilityHours(e.target.value)}
                      />
                    </div>
                    <div className="field" style={{ flex: 1 }}>
                      <label>Monthly Budget (SGD)</label>
                      <input
                        type="number"
                        min={0}
                        value={budget}
                        onChange={(e) => setBudget(e.target.value)}
                      />
                    </div>
                  </div>
                </div>
              </>
            )}

            {error && <div className="notice notice-error" style={{ marginTop: "1rem" }}>{error}</div>}

            {/* Actions */}
            <div className="row-between" style={{ marginTop: "2rem" }}>
              <button className="btn btn-ghost btn-sm" onClick={skip}>
                {step < TOTAL_STEPS ? "Skip" : "Finish later"}
              </button>
              <div className="row" style={{ gap: "0.5rem" }}>
                {step > 1 && (
                  <button className="btn btn-ghost btn-sm" onClick={() => setStep(step - 1)}>
                    Back
                  </button>
                )}
                <button className="btn btn-primary" onClick={next} disabled={loading}>
                  {loading ? "Saving..." : step < TOTAL_STEPS ? "Continue" : "Go to Dashboard"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
