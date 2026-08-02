import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

const LINKEDIN_REGEX = /^https?:\/\/(www\.)?linkedin\.com\/in\/.+$/;

export default function Profile() {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [linkedinUrl, setLinkedinUrl] = useState("");
  const [interests, setInterests] = useState("");
  const [careerGoals, setCareerGoals] = useState("");
  const [preferredTimings, setPreferredTimings] = useState("");
  const [availabilityHours, setAvailabilityHours] = useState("5");
  const [budget, setBudget] = useState("200");

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (user) {
      // Redirect organisers to their unique profile page
      if (user.role === "organiser") {
        navigate("/organiser/profile");
        return;
      }
      setName(user.name || "");
      setLinkedinUrl(user.linkedin_url || "");
      setInterests(user.interests || "");
      setCareerGoals(user.career_goals || "");
      setPreferredTimings(user.preferred_timings || "");
      setAvailabilityHours(String(user.availability_hours_per_week ?? 5));
      setBudget(String(user.budget_sgd ?? 200));
    }
  }, [user]);

  const linkedinError = linkedinUrl && !LINKEDIN_REGEX.test(linkedinUrl);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (linkedinError) return;
    setSaving(true);
    setError(null);
    setSuccess(false);
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
      setSuccess(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save profile.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 640 }}>
        <h2>Your Profile</h2>
        <p className="muted">
          Update your profile to improve AI recommendations. The more we know, the better we can match you.
        </p>

        {success && <div className="notice">Profile updated successfully.</div>}
        {error && <div className="notice notice-error">{error}</div>}

        <form onSubmit={handleSubmit} className="stack">
          <div className="field">
            <label>Full Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Your full name" />
          </div>

          <div className="field">
            <label>LinkedIn URL</label>
            <input
              type="url"
              value={linkedinUrl}
              onChange={(e) => {
                setLinkedinUrl(e.target.value);
                setSuccess(false);
              }}
              placeholder="https://linkedin.com/in/yourname"
            />
            {linkedinError && (
              <span style={{ color: "var(--danger)", fontSize: "0.82rem" }}>
                Must be a valid LinkedIn profile URL (e.g. https://linkedin.com/in/name)
              </span>
            )}
          </div>

          <div className="field">
            <label>Interests</label>
            <textarea
              value={interests}
              onChange={(e) => setInterests(e.target.value)}
              placeholder="e.g. AI, data science, public speaking, design thinking"
            />
          </div>

          <div className="field">
            <label>Career Goals</label>
            <textarea
              value={careerGoals}
              onChange={(e) => setCareerGoals(e.target.value)}
              placeholder="e.g. Transition into product management within 6 months"
            />
          </div>

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
              <label>Budget (SGD)</label>
              <input
                type="number"
                min={0}
                value={budget}
                onChange={(e) => setBudget(e.target.value)}
              />
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={saving || !!linkedinError}>
            {saving ? "Saving..." : "Save Profile"}
          </button>
        </form>

        {/* Role info */}
        <div className="card" style={{ marginTop: "2rem", background: "var(--bg-subtle)" }}>
          <h4 style={{ marginBottom: "0.5rem" }}>Account Info</h4>
          <div className="row" style={{ gap: "1.5rem" }}>
            <div>
              <span className="muted" style={{ fontSize: "0.85rem" }}>Email</span>
              <p style={{ margin: 0, fontWeight: 600 }}>{user?.email}</p>
            </div>
            <div>
              <span className="muted" style={{ fontSize: "0.85rem" }}>Role</span>
              <p style={{ margin: 0 }}>
                <span className="badge">{user?.role === "organiser" ? "Organiser" : "Public User"}</span>
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
