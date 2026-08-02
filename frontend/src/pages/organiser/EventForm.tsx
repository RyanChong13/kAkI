import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../api/client";
import type { AIListingResult, Event } from "../../types";

export default function EventForm() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const isEdit = !!id;

  // Form state
  const [title, setTitle] = useState("");
  const [organiser, setOrganiser] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("AI");
  const [location, setLocation] = useState("Singapore");
  const [date, setDate] = useState("");
  const [durationHours, setDurationHours] = useState("");
  const [priceSgd, setPriceSgd] = useState("0");
  const [capacity, setCapacity] = useState("");
  const [skills, setSkills] = useState("");
  const [difficulty, setDifficulty] = useState("All Levels");
  const [tags, setTags] = useState("");
  const [seoKeywords, setSeoKeywords] = useState("");
  const [recommendedAudience, setRecommendedAudience] = useState("");

  // AI state
  const [aiInput, setAiInput] = useState("");
  const [aiLoading, setAiLoading] = useState(false);
  const [aiResult, setAiResult] = useState<AIListingResult | null>(null);

  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Terms & Conditions modal
  const [showTnc, setShowTnc] = useState(false);
  const [tncAgreed, setTncAgreed] = useState(false);

  // Load existing event for editing
  useEffect(() => {
    if (id) {
      api
        .get<Event>(`/api/events/${id}`)
        .then((ev) => {
          setTitle(ev.title);
          setOrganiser(ev.organiser);
          setDescription(ev.description);
          setCategory(ev.category);
          setLocation(ev.location);
          setDate(ev.date ? new Date(ev.date).toISOString().slice(0, 16) : "");
          setDurationHours(ev.duration_hours ? String(ev.duration_hours) : "");
          setPriceSgd(String(ev.price_sgd));
          setCapacity(ev.capacity ? String(ev.capacity) : "");
          setSkills(ev.skills);
          setDifficulty(ev.difficulty);
          setTags(ev.tags);
          setSeoKeywords(ev.seo_keywords);
          setRecommendedAudience(ev.recommended_audience);
        })
        .catch(() => setError("Event not found"));
    }
  }, [id]);

  async function handleAIGenerate() {
    if (!aiInput.trim()) return;
    setAiLoading(true);
    setError(null);
    try {
      const result = await api.post<AIListingResult>("/api/organiser/ai-generate", { input_text: aiInput });
      setAiResult(result);
      // Auto-fill form
      if (result.title) setTitle(result.title);
      if (result.description) setDescription(result.description);
      if (result.category) setCategory(result.category);
      if (result.tags?.length) setTags(result.tags.join(", "));
      if (result.skills?.length) setSkills(result.skills.join(", "));
      if (result.seo_keywords?.length) setSeoKeywords(result.seo_keywords.join(", "));
      if (result.difficulty) setDifficulty(result.difficulty);
      if (result.recommended_audience) setRecommendedAudience(result.recommended_audience);
      if (result.duration_hours) setDurationHours(String(result.duration_hours));
      if (result.price_suggestion_sgd) setPriceSgd(String(result.price_suggestion_sgd));
    } catch {
      setError("AI generation failed. Please try again.");
    } finally {
      setAiLoading(false);
    }
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    // Show T&C modal before submitting
    setShowTnc(true);
  }

  async function handleConfirmedSubmit() {
    setShowTnc(false);
    setTncAgreed(false);
    setSaving(true);
    setError(null);

    const payload = {
      title,
      organiser,
      description,
      category,
      location,
      date: date || null,
      duration_hours: durationHours ? parseFloat(durationHours) : null,
      price_sgd: parseFloat(priceSgd) || 0,
      capacity: capacity ? parseInt(capacity) : null,
      skills,
      difficulty,
      tags,
      seo_keywords: seoKeywords,
      recommended_audience: recommendedAudience,
    };

    try {
      if (isEdit) {
        await api.put(`/api/organiser/events/${id}`, payload);
      } else {
        await api.post("/api/organiser/events", payload);
      }
      navigate("/organiser");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to save event.");
    } finally {
      setSaving(false);
    }
  }

  const TNC_TERMS = [
    {
      title: "Accuracy of Information",
      text: "You confirm that all event details provided are accurate and up-to-date. Misleading or false information may result in event removal.",
    },
    {
      title: "Compliance with Laws",
      text: "Your event must comply with all applicable Singapore laws and regulations, including PDPA for data collection and any required permits.",
    },
    {
      title: "No Discriminatory Content",
      text: "Events must not promote discrimination based on race, religion, gender, sexual orientation, nationality, or disability.",
    },
    {
      title: "Intellectual Property",
      text: "You have the rights to all content, images, and materials used in your event listing. Nexa is not liable for IP infringements.",
    },
    {
      title: "Refund Policy",
      text: "If your event is cancelled, you are responsible for issuing refunds to registered attendees in accordance with your stated refund policy.",
    },
    {
      title: "Platform Fees & Liability",
      text: "Nexa acts as a discovery platform. We are not liable for disputes between organisers and attendees, event quality, or financial losses.",
    },
    {
      title: "Content Moderation",
      text: "Nexa reserves the right to remove, edit, or flag any event listing that violates these terms or community guidelines without prior notice.",
    },
  ];

  const categories = [
    "AI", "Software Engineering", "Cybersecurity", "Entrepreneurship",
    "Marketing", "Finance", "Design", "Leadership", "Public Speaking",
    "Networking", "Volunteering", "Sports", "Hobbies", "Career Development",
  ];

  return (
    <div className="page">
      <div className="container" style={{ maxWidth: 720 }}>
        <Link to="/organiser" className="muted" style={{ fontSize: "0.9rem", fontWeight: 600 }}>Back to dashboard</Link>
        <h2 style={{ marginTop: "0.5rem" }}>{isEdit ? "Edit Event" : "Create Event"}</h2>

        {/* AI Auto-Fill section */}
        <div className="card" style={{ marginBottom: "1.5rem", background: "var(--bg-subtle)" }}>
          <h3 style={{ marginBottom: "0.5rem" }}>AI Auto-Fill</h3>
          <p className="muted" style={{ fontSize: "0.88rem" }}>
            Paste an event description or URL and let AI fill in the details for you.
          </p>
          <textarea
            value={aiInput}
            onChange={(e) => setAiInput(e.target.value)}
            placeholder="Paste event description, flyer text, or URL here..."
            style={{ marginBottom: "0.5rem" }}
          />
          <div className="row" style={{ gap: "0.5rem" }}>
            <button
              className="btn btn-secondary btn-sm"
              onClick={handleAIGenerate}
              disabled={aiLoading || !aiInput.trim()}
            >
              {aiLoading ? "Generating..." : "Generate with AI"}
            </button>
            {aiResult && <span className="badge badge-success">Fields auto-filled!</span>}
          </div>
        </div>

        {/* Event form */}
        <form onSubmit={handleSubmit} className="stack">
          <div className="field">
            <label>Title *</label>
            <input value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="Event title" />
          </div>

          <div className="row" style={{ gap: "1rem" }}>
            <div className="field" style={{ flex: 1 }}>
              <label>Organiser</label>
              <input value={organiser} onChange={(e) => setOrganiser(e.target.value)} placeholder="Organiser name" />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Category</label>
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                {categories.map((c) => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="field">
            <label>Description</label>
            <textarea value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Full event description" />
          </div>

          <div className="field">
            <label>Location</label>
            <input value={location} onChange={(e) => setLocation(e.target.value)} placeholder="e.g. Marina Bay Sands, Singapore" />
          </div>

          <div className="row" style={{ gap: "1rem" }}>
            <div className="field" style={{ flex: 1 }}>
              <label>Date & Time</label>
              <input type="text" value={date} onChange={(e) => setDate(e.target.value)} placeholder="2026-08-15T09:00" />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Duration (hours)</label>
              <input type="number" min={0} step={0.5} value={durationHours} onChange={(e) => setDurationHours(e.target.value)} placeholder="3" />
            </div>
          </div>

          <div className="row" style={{ gap: "1rem" }}>
            <div className="field" style={{ flex: 1 }}>
              <label>Price (SGD)</label>
              <input type="number" min={0} value={priceSgd} onChange={(e) => setPriceSgd(e.target.value)} />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Capacity</label>
              <input type="number" min={0} value={capacity} onChange={(e) => setCapacity(e.target.value)} placeholder="Leave blank for unlimited" />
            </div>
            <div className="field" style={{ flex: 1 }}>
              <label>Difficulty</label>
              <select value={difficulty} onChange={(e) => setDifficulty(e.target.value)}>
                <option>Beginner</option>
                <option>Intermediate</option>
                <option>Advanced</option>
                <option>All Levels</option>
              </select>
            </div>
          </div>

          <div className="field">
            <label>Skills (comma-separated)</label>
            <input value={skills} onChange={(e) => setSkills(e.target.value)} placeholder="e.g. Python, Machine Learning, Data Analysis" />
          </div>

          <div className="field">
            <label>Tags (comma-separated)</label>
            <input value={tags} onChange={(e) => setTags(e.target.value)} placeholder="e.g. workshop, hands-on, beginner-friendly" />
          </div>

          <div className="field">
            <label>SEO Keywords (comma-separated)</label>
            <input value={seoKeywords} onChange={(e) => setSeoKeywords(e.target.value)} placeholder="e.g. AI workshop Singapore, machine learning course" />
          </div>

          <div className="field">
            <label>Recommended Audience</label>
            <input value={recommendedAudience} onChange={(e) => setRecommendedAudience(e.target.value)} placeholder="e.g. Software engineers, data scientists" />
          </div>

          {error && <div className="notice notice-error">{error}</div>}

          <div className="row" style={{ gap: "0.75rem" }}>
            <button type="submit" className="btn btn-primary" disabled={saving || !title.trim()}>
              {saving ? "Saving..." : isEdit ? "Update Event" : "Create Event"}
            </button>
            <Link to="/organiser" className="btn btn-ghost">Cancel</Link>
          </div>
        </form>

        {/* Terms & Conditions Modal */}
        {showTnc && (
          <div className="modal-overlay" onClick={(e) => { if (e.target === e.currentTarget) setShowTnc(false); }}>
            <div className="modal-box">
              <div className="modal-header">
                <h3 style={{ marginBottom: 0 }}>Terms and Conditions</h3>
                <p className="muted" style={{ margin: "0.3rem 0 0", fontSize: "0.88rem" }}>
                  Please review and agree to the following before publishing your event on Nexa.
                </p>
              </div>
              <div className="modal-body">
                {TNC_TERMS.map((t) => (
                  <div key={t.title} className="tnc-item">
                    <strong style={{ display: "block", marginBottom: "0.2rem", fontSize: "0.92rem" }}>{t.title}</strong>
                    <p className="muted" style={{ margin: 0, fontSize: "0.88rem" }}>{t.text}</p>
                  </div>
                ))}
                <label className="tnc-check">
                  <input
                    type="checkbox"
                    checked={tncAgreed}
                    onChange={(e) => setTncAgreed(e.target.checked)}
                    style={{ marginTop: "2px" }}
                  />
                  <span>I have read and agree to the Nexa Terms and Conditions for event organisers.</span>
                </label>
              </div>
              <div className="modal-footer">
                <button className="btn btn-ghost" onClick={() => { setShowTnc(false); setTncAgreed(false); }}>
                  Cancel
                </button>
                <button
                  className="btn btn-primary"
                  disabled={!tncAgreed}
                  onClick={handleConfirmedSubmit}
                >
                  {saving ? "Publishing..." : "Agree & Publish"}
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
