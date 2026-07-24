import { useState, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import { api, ApiError } from "../api/client";
import type { ResumeProfile } from "../types";

export default function ResumeUpload() {
  const navigate = useNavigate();
  const [file, setFile] = useState<File | null>(null);
  const [profile, setProfile] = useState<ResumeProfile | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    setFile(e.target.files?.[0] ?? null);
    setProfile(null);
    setError(null);
  }

  async function handleUpload() {
    if (!file) return;
    setLoading(true);
    setError(null);
    try {
      const form = new FormData();
      form.append("file", file);
      const result = await api.postForm<ResumeProfile>("/api/resume/upload", form);
      setProfile(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not parse this resume. Please try another PDF.");
    } finally {
      setLoading(false);
    }
  }

  const skills = profile?.extracted_skills ? profile.extracted_skills.split(",").map((s) => s.trim()).filter(Boolean) : [];

  return (
    <div className="page">
      <div className="container">
        <div className="step-track">
          <span className="step-pill done">1. Account</span>
          <span className="step-pill active">2. Resume</span>
          <span className="step-pill">3. Choose path</span>
        </div>

        <div className="card" style={{ maxWidth: 640, margin: "0 auto" }}>
          <h2>Upload your resume</h2>
          <p>
            We'll parse your resume (PDF) to pull out your skills so job and course recommendations are tailored to
            you. This uses simple keyword extraction, not an external AI service.
          </p>

          {error && <div className="notice notice-error">{error}</div>}

          <div className="field">
            <label htmlFor="resume-file">Resume (PDF)</label>
            <input id="resume-file" type="file" accept="application/pdf" onChange={handleFileChange} />
          </div>

          <div className="row">
            <button className="btn btn-primary" onClick={handleUpload} disabled={!file || loading}>
              {loading ? "Parsing…" : "Upload & parse"}
            </button>
            <button className="btn btn-ghost" onClick={() => navigate("/choose-path")}>
              Skip for now
            </button>
          </div>

          {profile && (
            <div className="notice" style={{ marginTop: "1.5rem" }}>
              <strong>Parsed successfully.</strong>
              {profile.extracted_name && (
                <p style={{ marginTop: "0.5rem", marginBottom: "0.25rem" }}>Name detected: {profile.extracted_name}</p>
              )}
              {profile.years_experience_guess != null && (
                <p style={{ marginBottom: "0.25rem" }}>Experience: ~{profile.years_experience_guess} years</p>
              )}
              <p style={{ marginBottom: "0.5rem" }}>Skills found ({skills.length}):</p>
              <div className="row">
                {skills.length > 0 ? (
                  skills.map((s) => (
                    <span key={s} className="badge">
                      {s}
                    </span>
                  ))
                ) : (
                  <span className="muted">No matching skills found in this document — recommendations will use general matches.</span>
                )}
              </div>
              <button className="btn btn-primary" style={{ marginTop: "1.25rem" }} onClick={() => navigate("/choose-path")}>
                Continue
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
