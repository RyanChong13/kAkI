import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";

export default function OrganiserSettings() {
  const { user, updateUser } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState("");
  const [companyName, setCompanyName] = useState("");
  const [bio, setBio] = useState("");
  const [website, setWebsite] = useState("");
  const [phone, setPhone] = useState("");

  const [saving, setSaving] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!user) return;
    if (user.role !== "organiser") {
      navigate("/dashboard");
      return;
    }
    setName(user.name || "");
    setCompanyName(user.company_name || "");
    setBio(user.bio || "");
    setWebsite(user.website || "");
    setPhone(user.phone || "");
  }, [user]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);
    try {
      await updateUser({
        name,
        company_name: companyName,
        bio,
        website,
        phone,
      });
      setSuccess(true);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save settings.");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 640 }}>
        <div className="row-between" style={{ marginBottom: "1rem" }}>
          <h2 style={{ marginBottom: 0 }}>Organiser Settings</h2>
          <button className="btn btn-ghost btn-sm" onClick={() => navigate("/organiser")}>
            Back to Dashboard
          </button>
        </div>
        <p className="muted" style={{ marginBottom: "1.5rem" }}>
          Tell attendees about your organisation. This information appears on your public events.
        </p>

        {success && <div className="notice">Settings saved successfully.</div>}
        {error && <div className="notice notice-error">{error}</div>}

        <form onSubmit={handleSubmit} className="stack">
          <div className="field">
            <label>Contact Person Name</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Your full name"
            />
          </div>

          <div className="field">
            <label>Company / Organisation Name</label>
            <input
              value={companyName}
              onChange={(e) => setCompanyName(e.target.value)}
              placeholder="e.g. Nexa Events Pte Ltd"
            />
          </div>

          <div className="field">
            <label>About Your Organisation</label>
            <textarea
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Describe what your organisation does, your mission, and the types of events you host..."
              rows={5}
            />
            <span className="muted" style={{ fontSize: "0.8rem" }}>
              {bio.length}/500 characters
            </span>
          </div>

          <div className="field">
            <label>Website</label>
            <input
              type="url"
              value={website}
              onChange={(e) => setWebsite(e.target.value)}
              placeholder="https://yourcompany.com"
            />
          </div>

          <div className="field">
            <label>Contact Phone</label>
            <input
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+65 9123 4567"
            />
          </div>

          <div className="card" style={{ background: "var(--bg-subtle)", marginTop: "0.5rem" }}>
            <h4 style={{ marginBottom: "0.5rem" }}>Account Info</h4>
            <div className="row" style={{ gap: "1.5rem" }}>
              <div>
                <span className="muted" style={{ fontSize: "0.85rem" }}>Email</span>
                <p style={{ margin: 0, fontWeight: 600 }}>{user?.email}</p>
              </div>
              <div>
                <span className="muted" style={{ fontSize: "0.85rem" }}>Role</span>
                <p style={{ margin: 0 }}>
                  <span className="badge">Organiser</span>
                </p>
              </div>
            </div>
          </div>

          <button type="submit" className="btn btn-primary btn-block" disabled={saving}>
            {saving ? "Saving..." : "Save Settings"}
          </button>
        </form>
      </div>
    </div>
  );
}
