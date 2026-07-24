import { useState } from "react";
import { useLocation, useNavigate, Link } from "react-router-dom";
import CourseCard from "../../components/CourseCard";
import type { CourseRecommendation } from "../../types";

interface LocationState {
  recommendations?: CourseRecommendation[];
}

export default function RecommendedCourses() {
  const location = useLocation();
  const navigate = useNavigate();
  const recommendations = (location.state as LocationState | null)?.recommendations ?? [];
  const [selected, setSelected] = useState<Set<number>>(new Set());

  function toggleSelect(courseId: number) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(courseId)) next.delete(courseId);
      else next.add(courseId);
      return next;
    });
  }

  function handleContinue() {
    navigate("/upskilling/grants", { state: { courseIds: Array.from(selected) } });
  }

  if (recommendations.length === 0) {
    return (
      <div className="page container">
        <div className="notice">
          No recommendations to show. <Link to="/upskilling/goal">Go back and tell us your goal</Link>.
        </div>
      </div>
    );
  }

  return (
    <div className="page">
      <div className="container">
        <h2>Courses we recommend</h2>
        <p>Pick the ones you'd like to take — we'll show you the SkillsFuture Credit available next.</p>

        <div className="grid grid-2">
          {recommendations.map(({ course, match_score }) => (
            <CourseCard
              key={course.id}
              course={course}
              matchScore={match_score}
              action={
                <label className="row" style={{ gap: "0.4rem", fontWeight: 600 }}>
                  <input type="checkbox" checked={selected.has(course.id)} onChange={() => toggleSelect(course.id)} />
                  Select this course
                </label>
              }
            />
          ))}
        </div>

        <div
          className="card row-between"
          style={{ position: "sticky", bottom: "1rem", marginTop: "2rem", boxShadow: "var(--shadow)" }}
        >
          <span>
            <strong>{selected.size}</strong> course{selected.size === 1 ? "" : "s"} selected
          </span>
          <button className="btn btn-primary" disabled={selected.size === 0} onClick={handleContinue}>
            See available grants
          </button>
        </div>
      </div>
    </div>
  );
}
