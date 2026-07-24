import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../api/client";
import CourseCard from "../components/CourseCard";
import type { ApplicationOut, GrantApplicationOut, Job, ResumeProfile, SavedCourseOut } from "../types";

export default function Dashboard() {
  const [saved, setSaved] = useState<SavedCourseOut[]>([]);
  const [applications, setApplications] = useState<ApplicationOut[]>([]);
  const [jobsById, setJobsById] = useState<Record<number, Job>>({});
  const [grantApplications, setGrantApplications] = useState<GrantApplicationOut[]>([]);
  const [resume, setResume] = useState<ResumeProfile | null>(null);

  useEffect(() => {
    api.get<SavedCourseOut[]>("/api/saved-courses").then(setSaved).catch(() => {});
    api.get<GrantApplicationOut[]>("/api/grants").then(setGrantApplications).catch(() => {});
    api.get<ResumeProfile>("/api/resume/me").then(setResume).catch(() => {});
    api
      .get<ApplicationOut[]>("/api/applications")
      .then((apps) => {
        setApplications(apps);
        return api.get<Job[]>("/api/jobs");
      })
      .then((jobs) => setJobsById(Object.fromEntries(jobs.map((j) => [j.id, j]))))
      .catch(() => {});
  }, []);

  return (
    <div className="page">
      <div className="container">
        <h2>Your dashboard</h2>

        <div className="card" style={{ marginBottom: "2rem" }}>
          <h3>Resume</h3>
          {resume ? (
            <p className="muted" style={{ marginBottom: 0 }}>
              {resume.filename} &middot; {resume.extracted_skills.split(",").filter(Boolean).length} skills detected
            </p>
          ) : (
            <p className="muted" style={{ marginBottom: 0 }}>
              No resume uploaded yet. <Link to="/resume-upload">Upload one</Link> to get better recommendations.
            </p>
          )}
        </div>

        <section style={{ marginBottom: "2.5rem" }}>
          <h3>Saved courses ({saved.length})</h3>
          {saved.length === 0 ? (
            <p className="muted">
              No saved courses yet. <Link to="/courses">Browse courses</Link>.
            </p>
          ) : (
            <div className="grid grid-2">
              {saved.map((s) => (
                <CourseCard key={s.id} course={s.course} />
              ))}
            </div>
          )}
        </section>

        <section style={{ marginBottom: "2.5rem" }}>
          <h3>Job applications ({applications.length})</h3>
          {applications.length === 0 ? (
            <p className="muted">
              No applications yet. <Link to="/jobs/recommended">Find jobs</Link>.
            </p>
          ) : (
            <div className="stack">
              {applications.map((app) => (
                <div key={app.id} className="card card-compact row-between">
                  <span>{jobsById[app.job_id]?.title ?? `Job #${app.job_id}`}</span>
                  <span className="badge badge-success">{app.status}</span>
                </div>
              ))}
            </div>
          )}
        </section>

        <section>
          <h3>SkillsFuture Credit claims ({grantApplications.length})</h3>
          {grantApplications.length === 0 ? (
            <p className="muted">
              No credit claims yet. <Link to="/upskilling/goal">Explore upskilling</Link>.
            </p>
          ) : (
            <div className="stack">
              {grantApplications.map((g) => (
                <div key={g.id} className="card card-compact row-between">
                  <span>Course #{g.course_id}</span>
                  <span className="badge badge-success">S${g.credit_amount_sgd.toLocaleString()} claimed</span>
                </div>
              ))}
            </div>
          )}
        </section>
      </div>
    </div>
  );
}
