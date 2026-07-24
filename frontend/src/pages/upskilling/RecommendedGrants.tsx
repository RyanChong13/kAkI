import { useEffect, useState } from "react";
import { useLocation, Link } from "react-router-dom";
import { api, ApiError } from "../../api/client";
import type { GrantApplicationOut, GrantOffer } from "../../types";

interface LocationState {
  courseIds?: number[];
}

export default function RecommendedGrants() {
  const location = useLocation();
  const courseIds = (location.state as LocationState | null)?.courseIds ?? [];

  const [offers, setOffers] = useState<GrantOffer[]>([]);
  const [selected, setSelected] = useState<Set<number>>(new Set());
  const [applications, setApplications] = useState<GrantApplicationOut[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    if (courseIds.length === 0) {
      setLoading(false);
      return;
    }
    const query = courseIds.map((id) => `course_ids=${id}`).join("&");
    api
      .get<GrantOffer[]>(`/api/grants/available?${query}`)
      .then((data) => {
        setOffers(data);
        setSelected(new Set(data.filter((o) => o.eligible).map((o) => o.course.id)));
      })
      .catch((err) => setError(err instanceof ApiError ? err.message : "Could not load grant info."))
      .finally(() => setLoading(false));
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  function toggleSelect(courseId: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(courseId)) next.delete(courseId);
      else next.add(courseId);
      return next;
    });
  }

  async function handleMassApply() {
    setSubmitting(true);
    setError(null);
    try {
      const result = await api.post<GrantApplicationOut[]>("/api/grants/mass-apply", {
        course_ids: Array.from(selected),
      });
      setApplications(result);
    } catch (err) {
      setError(err instanceof ApiError ? err.message : "Could not submit grant applications.");
    } finally {
      setSubmitting(false);
    }
  }

  if (courseIds.length === 0) {
    return (
      <div className="page container">
        <div className="notice">
          No courses selected. <Link to="/upskilling/goal">Start over</Link>.
        </div>
      </div>
    );
  }

  const totalCredit = offers
    .filter((o) => selected.has(o.course.id) && o.eligible)
    .reduce((sum, o) => sum + o.credit_amount_sgd, 0);

  return (
    <div className="page">
      <div className="container">
        <h2>Available SkillsFuture Credit</h2>
        <p>
          These amounts reflect standard SkillsFuture Credit eligibility for each course. Actual claims are filed via
          the government MySkillsFuture portal with Singpass, which can't be automated by a third-party app — this
          records your intent so your selections carry through. See the README for details.
        </p>

        {error && <div className="notice notice-error">{error}</div>}

        {loading ? (
          <div className="spinner" />
        ) : (
          <div className="stack">
            {offers.map((offer) => {
              const app = applications?.find((a) => a.course_id === offer.course.id);
              return (
                <div key={offer.course.id} className="card card-compact row-between">
                  <div>
                    <strong>{offer.course.title}</strong>
                    <p className="muted" style={{ marginBottom: 0 }}>
                      {offer.course.provider}
                    </p>
                  </div>
                  <div className="row">
                    {offer.eligible ? (
                      <span className="badge badge-success">S${offer.credit_amount_sgd.toLocaleString()} credit</span>
                    ) : (
                      <span className="badge badge-outline">Not eligible</span>
                    )}
                    {app ? (
                      <span className="badge badge-success">Submitted</span>
                    ) : (
                      <label className="row" style={{ gap: "0.4rem" }}>
                        <input
                          type="checkbox"
                          checked={selected.has(offer.course.id)}
                          disabled={!offer.eligible}
                          onChange={() => toggleSelect(offer.course.id)}
                        />
                        Claim
                      </label>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {applications ? (
          <div className="notice" style={{ marginTop: "1.5rem" }}>
            <strong>{applications.length} grant claim(s) recorded</strong>, totaling S${totalCredit.toLocaleString()}.
            <div className="row" style={{ marginTop: "1rem" }}>
              <Link to="/dashboard" className="btn btn-primary">
                Go to dashboard
              </Link>
            </div>
          </div>
        ) : (
          <div
            className="card row-between"
            style={{ position: "sticky", bottom: "1rem", marginTop: "2rem", boxShadow: "var(--shadow)" }}
          >
            <span>
              Claiming <strong>{selected.size}</strong> credit(s), totaling{" "}
              <strong>S${totalCredit.toLocaleString()}</strong>
            </span>
            <button className="btn btn-primary" disabled={selected.size === 0 || submitting} onClick={handleMassApply}>
              {submitting ? "Submitting…" : "Claim selected credit"}
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
