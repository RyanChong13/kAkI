import { useEffect, useMemo, useRef, useState } from "react";
import type { CSSProperties, DragEvent, FormEvent } from "react";
import { api, ApiError } from "../api/client";
import { makePlanId, savedPlansStore } from "../lib/savedPlans";
import type { SavedPlan } from "../lib/savedPlans";
import type {
  CareerMatch,
  RedesignResult,
  RedesignSuggestion,
  ResumeAnalysis,
  RoleListResponse,
  RoleOut,
  SchemeInfo,
  TaskWithScore,
} from "../types";

const IMPACT_STYLES: Record<string, { label: string; cls: string }> = {
  augment: { label: "AI helps you", cls: "badge-success" },
  automate: { label: "AI handles the routine parts", cls: "badge-warning" },
  transform: { label: "Your role evolves", cls: "badge-danger" },
};

function aiScoreBadge(score: number): { label: string; cls: string } {
  if (score >= 70) return { label: `${score}% AI-assisted`, cls: "badge-success" };
  if (score >= 40) return { label: `${score}% AI-assisted`, cls: "badge-warning" };
  return { label: `${score}% AI-assisted`, cls: "badge-danger" };
}

const FUNDING_LABELS: Record<string, string> = {
  base_credit: "$500 SkillsFuture Credit",
  mid_career: "$4,000 Mid-Career Credit",
  sctp: "SCTP \u2014 up to 90% course subsidy",
  level_up: "Level-Up \u2014 $3,000/mo training allowance",
};

export default function Redesign() {
  const [mode, setMode] = useState<"role" | "resume">("role");

  // Role input state
  const [roles, setRoles] = useState<RoleOut[]>([]);
  const [roleInput, setRoleInput] = useState("");
  const [age, setAge] = useState("");
  const [showDropdown, setShowDropdown] = useState(false);

  // Target-role selection ("I'm not sure" = current behaviour)
  const [wantTarget, setWantTarget] = useState(false);
  const [targetInput, setTargetInput] = useState("");

  // Resume state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [dragOver, setDragOver] = useState(false);
  const [analysis, setAnalysis] = useState<ResumeAnalysis | null>(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [funding, setFunding] = useState<SchemeInfo[] | null>(null);

  // Shared output state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RedesignResult | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // Saved plans (Phase 3 — device bookmarks now; moves to user accounts later)
  const [savedPlans, setSavedPlans] = useState<SavedPlan[]>([]);
  const [savedFlash, setSavedFlash] = useState(false);
  // Last request context — powers "Regenerate" and saving the request
  const lastRequestRef = useRef<{ role: string; userSkills?: string[]; targetRole?: string } | null>(null);
  // Staged loading messages (reduce anxiety during long AI calls)
  const [stageIdx, setStageIdx] = useState(0);

  useEffect(() => {
    api.get<RoleListResponse>("/api/roles")
      .then(res => setRoles(res.roles))
      .catch(() => {});
    setSavedPlans(savedPlansStore.list());
  }, []);

  const busy = loading || analyzing;
  useEffect(() => {
    if (!busy) {
      setStageIdx(0);
      return;
    }
    const t = setInterval(() => setStageIdx(i => i + 1), 7000);
    return () => clearInterval(t);
  }, [busy]);

  const analyzeStages = [
    "Reading your resume\u2026",
    "Picking out your skills\u2026",
    "Looking for careers that fit what you already do\u2026",
  ];
  const generateStages = [
    `Looking at how AI is changing ${roleInput.trim() || "this role"}\u2026`,
    "Building options around the skills you already have\u2026",
    "Finding SkillsFuture-funded courses to close the gaps\u2026",
  ];
  const stages = analyzing ? analyzeStages : generateStages;
  const stageMsg = stages[Math.min(stageIdx, stages.length - 1)];

  // Fetch user-level funding eligibility once we have an analysis + age
  useEffect(() => {
    if (!analysis || !age) {
      setFunding(null);
      return;
    }
    api.get<SchemeInfo[]>(`/api/schemes/eligibility?age=${Number(age)}`)
      .then(setFunding)
      .catch(() => setFunding(null));
  }, [analysis, age]);

  const eligibleFunding = funding?.filter(s => s.eligible) ?? [];

  const filteredRoles = useMemo(() => {
    const q = roleInput.toLowerCase().trim();
    if (!q) return roles.slice(0, 8);
    return roles
      .filter(r => r.title.toLowerCase().includes(q) || r.category.toLowerCase().includes(q))
      .slice(0, 8);
  }, [roles, roleInput]);

  function generateFor(roleTitle: string, userSkills?: string[], targetRole?: string) {
    if (!roleTitle.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    setShowDropdown(false);

    const body: Record<string, unknown> = { role: roleTitle.trim() };
    if (age) body.age = Number(age);
    if (userSkills && userSkills.length > 0) body.user_skills = userSkills;
    if (targetRole && targetRole.trim() && targetRole.trim().toLowerCase() !== roleTitle.trim().toLowerCase()) {
      body.target_role = targetRole.trim();
    }
    // Remember the request so we can regenerate or bookmark it
    lastRequestRef.current = {
      role: roleTitle.trim(),
      userSkills,
      targetRole: typeof body.target_role === "string" ? body.target_role : undefined,
    };

    api.post<RedesignResult>("/api/redesign", body)
      .then(res => {
        setResult(res);
        setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
      })
      .catch((err: unknown) => {
        const msg = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
        setError(msg);
      })
      .finally(() => setLoading(false));
  }

  function handleGenerate() {
    const target = wantTarget && targetInput.trim() ? targetInput : undefined;
    generateFor(roleInput, analysis ? analysis.skills : undefined, target);
  }

  function selectRole(role: RoleOut) {
    setRoleInput(role.title);
    setShowDropdown(false);
  }

  function pickFile(file: File | undefined | null) {
    if (!file) return;
    if (!file.name.toLowerCase().endsWith(".pdf")) {
      setError("Please upload a PDF file.");
      return;
    }
    setError(null);
    setResumeFile(file);
    setAnalysis(null);
  }

  function handleDrop(e: DragEvent<HTMLDivElement>) {
    e.preventDefault();
    setDragOver(false);
    pickFile(e.dataTransfer.files?.[0]);
  }

  async function handleAnalyze() {
    if (!resumeFile) return;
    setAnalyzing(true);
    setError(null);
    setResult(null);
    setAnalysis(null);

    const form = new FormData();
    form.append("file", resumeFile);
    try {
      const res = await api.postForm<ResumeAnalysis>("/api/resume/analyze", form);
      setAnalysis(res);
      // If the user picked a target role, go straight to a transition plan
      const target = wantTarget ? targetInput.trim() : "";
      if (target && res.current_role_guess) {
        generateFor(res.current_role_guess, res.skills, target);
      }
    } catch (err) {
      const msg = err instanceof ApiError ? err.message : "Something went wrong. Please try again.";
      setError(msg);
    } finally {
      setAnalyzing(false);
    }
  }

  function handleCareerSelect(match: CareerMatch) {
    setRoleInput(match.role_title);
    const current = analysis?.current_role_guess?.trim();
    if (current && current.toLowerCase() !== match.role_title.toLowerCase()) {
      // Transition plan: detected current role → this career
      generateFor(current, analysis?.skills, match.role_title);
    } else {
      generateFor(match.role_title, analysis ? analysis.skills : undefined);
    }
  }

  // ── Saved plans + regenerate (Phase 3) ───────────────────────────────────

  function handleRegenerate() {
    const last = lastRequestRef.current;
    if (!last) return;
    generateFor(last.role, last.userSkills, last.targetRole);
  }

  function handleSavePlan() {
    if (!result) return;
    const last = lastRequestRef.current;
    const plan: SavedPlan = {
      id: makePlanId(),
      saved_at: new Date().toISOString(),
      role: last?.role ?? result.role,
      target_role: result.target_role ?? null,
      age: age ? Number(age) : null,
      user_skills: last?.userSkills,
      result,
    };
    savedPlansStore.save(plan);
    setSavedPlans(savedPlansStore.list());
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 2000);
  }

  function handleOpenPlan(plan: SavedPlan) {
    setResult(plan.result);
    setAnalysis(null);
    setError(null);
    setRoleInput(plan.role);
    if (plan.target_role) {
      setWantTarget(true);
      setTargetInput(plan.target_role);
    } else {
      setWantTarget(false);
    }
    if (plan.age) setAge(String(plan.age));
    lastRequestRef.current = {
      role: plan.role,
      userSkills: plan.user_skills,
      targetRole: plan.target_role ?? undefined,
    };
    setTimeout(() => resultsRef.current?.scrollIntoView({ behavior: "smooth", block: "start" }), 100);
  }

  function handleDeletePlan(id: string) {
    savedPlansStore.remove(id);
    setSavedPlans(savedPlansStore.list());
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
            Type your job title or upload your resume. We'll show you ways to reshape
            your job around AI, plus SkillsFuture courses and the funding you can claim.
          </p>

          {/* Mode tabs */}
          <div className="row" style={{ justifyContent: "center", gap: "0.5rem", marginBottom: "1.5rem" }}>
            <button
              className={`btn ${mode === "role" ? "btn-primary" : "btn-ghost"}`}
              onClick={() => setMode("role")}
            >
              Type your role
            </button>
            <button
              className={`btn ${mode === "resume" ? "btn-primary" : "btn-ghost"}`}
              onClick={() => setMode("resume")}
            >
              Upload resume
            </button>
          </div>

          {/* ── Role input tab ── */}
          {mode === "role" && (
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
              <TargetSelector
                wantTarget={wantTarget}
                setWantTarget={setWantTarget}
                targetInput={targetInput}
                setTargetInput={setTargetInput}
                roles={roles}
                onSubmit={handleGenerate}
              />
              <button
                className="btn btn-primary btn-block"
                onClick={handleGenerate}
                disabled={loading || !roleInput.trim() || (wantTarget && !targetInput.trim())}
                style={{ marginTop: "1rem" }}
              >
                {loading ? (
                  <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Generating…</>
                ) : wantTarget && targetInput.trim() ? (
                  "Generate Transition Plan"
                ) : (
                  "Generate Redesign"
                )}
              </button>
            </div>
          )}

          {/* ── Resume upload tab ── */}
          {mode === "resume" && (
            <div style={{ maxWidth: 560, margin: "0 auto" }}>
              <div
                onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => fileInputRef.current?.click()}
                style={{
                  border: `2px dashed ${dragOver ? "var(--purple-600)" : "var(--border)"}`,
                  borderRadius: "var(--radius-lg)",
                  padding: "2rem 1.5rem",
                  cursor: "pointer",
                  background: dragOver ? "var(--purple-100)" : "var(--bg-card)",
                  transition: "all 0.15s ease",
                }}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="application/pdf,.pdf"
                  style={{ display: "none" }}
                  onChange={e => pickFile(e.target.files?.[0])}
                />
                {resumeFile ? (
                  <div>
                    <strong style={{ fontSize: "1rem" }}>{resumeFile.name}</strong>
                    <p className="muted" style={{ margin: "0.4rem 0 0", fontSize: "0.85rem" }}>
                      Click to choose a different file
                    </p>
                  </div>
                ) : (
                  <div>
                    <strong style={{ fontSize: "1rem" }}>Drop your resume here, or click to browse</strong>
                    <p className="muted" style={{ margin: "0.4rem 0 0", fontSize: "0.85rem" }}>
                      PDF only. We extract your skills — nothing is stored.
                    </p>
                  </div>
                )}
              </div>

              <TargetSelector
                wantTarget={wantTarget}
                setWantTarget={setWantTarget}
                targetInput={targetInput}
                setTargetInput={setTargetInput}
                roles={roles}
                style={{ marginTop: "1rem" }}
              />

              <div className="row" style={{ gap: "0.75rem", alignItems: "flex-end", marginTop: "1rem" }}>
                <div className="field" style={{ width: 90, marginBottom: 0 }}>
                  <label htmlFor="age-resume">Age</label>
                  <input
                    id="age-resume"
                    type="number"
                    placeholder="—"
                    value={age}
                    onChange={e => setAge(e.target.value)}
                    min={0}
                    max={120}
                  />
                </div>
                <button
                  className="btn btn-primary"
                  style={{ flex: 1 }}
                  onClick={handleAnalyze}
                  disabled={analyzing || !resumeFile}
                >
                  {analyzing ? (
                    <><span className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} /> Analysing resume…</>
                  ) : (
                    "Analyse Resume"
                  )}
                </button>
              </div>

              {analyzing && (
                <p className="muted" style={{ marginTop: "1rem" }}>
                  {stageMsg}
                </p>
              )}
            </div>
          )}
        </div>
      </section>

      {/* Saved plans (bookmarks) */}
      {savedPlans.length > 0 && (
        <div className="container" style={{ paddingTop: "0.5rem" }}>
          <div className="card" style={{ background: "var(--bg-subtle)" }}>
            <strong style={{ fontSize: "0.95rem" }}>Your saved plans</strong>
            <div className="stack" style={{ marginTop: "0.5rem" }}>
              {savedPlans.map(p => (
                <div key={p.id} className="row-between" style={{ flexWrap: "wrap", gap: "0.5rem" }}>
                  <div>
                    <strong style={{ fontSize: "0.9rem" }}>
                      {p.role}{p.target_role ? ` → ${p.target_role}` : ""}
                    </strong>
                    <span className="muted" style={{ marginLeft: "0.6rem", fontSize: "0.78rem" }}>
                      Saved {new Date(p.saved_at).toLocaleDateString(undefined, { day: "numeric", month: "short" })}
                    </span>
                  </div>
                  <div className="row" style={{ gap: "0.4rem" }}>
                    <button className="btn btn-secondary btn-sm" onClick={() => handleOpenPlan(p)}>Open</button>
                    <button className="btn btn-ghost btn-sm" onClick={() => handleDeletePlan(p.id)}>Remove</button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Error */}
      {error && (
        <div className="container" style={{ paddingTop: "1rem" }}>
          <div className="notice notice-error">{error}</div>
        </div>
      )}

      {/* Loading hint (redesign generation) — staged messages */}
      {loading && (
        <div className="container" style={{ textAlign: "center", padding: "2rem 0" }}>
          <div className="row" style={{ justifyContent: "center", gap: "0.6rem" }}>
            <span className="spinner" style={{ width: 18, height: 18, borderWidth: 2 }} />
            <p className="muted" style={{ margin: 0 }}>{stageMsg}</p>
          </div>
          <p className="muted" style={{ marginTop: "0.5rem", fontSize: "0.8rem" }}>
            This usually takes 20–40 seconds.
          </p>
        </div>
      )}

      {/* Resume analysis results */}
      {analysis && (
        <div className="container page" style={{ paddingTop: "1rem" }}>
          <div className="card" style={{ marginBottom: "1.5rem" }}>
            <div className="row-between" style={{ marginBottom: "0.75rem", flexWrap: "wrap", gap: "0.5rem" }}>
              <h2 style={{ fontSize: "1.4rem", margin: 0 }}>Your skills</h2>
              {analysis.current_role_guess && (
                <span className="muted" style={{ fontSize: "0.9rem" }}>
                  Detected current role: <strong>{analysis.current_role_guess}</strong>
                </span>
              )}
            </div>
            <div className="tags">
              {analysis.skills.map((s, i) => (
                <span key={i} className="badge" style={{ background: "var(--purple-100)", color: "var(--purple-700)" }}>{s}</span>
              ))}
            </div>
          </div>

          {/* Funding entitlement strip (age-based) */}
          {!age && (
            <p className="muted" style={{ marginBottom: "1.25rem", fontSize: "0.85rem" }}>
              Tip: enter your age above to see which SkillsFuture funding schemes you qualify for.
            </p>
          )}
          {age && eligibleFunding.length > 0 && (
            <div className="card" style={{ marginBottom: "1.5rem", background: "var(--bg-subtle)" }}>
              <strong style={{ fontSize: "0.95rem" }}>Your SkillsFuture funding at age {age}</strong>
              <div className="tags" style={{ marginTop: "0.5rem" }}>
                {eligibleFunding.map(s => (
                  <a
                    key={s.scheme_id}
                    className="badge badge-success"
                    href={s.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={s.description}
                    style={{ textDecoration: "none" }}
                  >
                    {FUNDING_LABELS[s.scheme_id] ?? s.scheme_name}
                  </a>
                ))}
              </div>
              <p className="muted" style={{ margin: "0.5rem 0 0", fontSize: "0.78rem" }}>
                Estimated from your age — verify your exact eligibility on MySkillsFuture.
              </p>
            </div>
          )}

          <h2 style={{ fontSize: "1.4rem", marginBottom: "0.25rem" }}>Careers that suit you</h2>
          <p className="muted" style={{ marginBottom: "1.25rem" }}>
            Ranked by fit — including careers in other industries where your skills transfer well.
          </p>

          <div className="stack">
            {analysis.career_matches.map(m => (
              <CareerMatchCard key={m.role_id} match={m} onSelect={() => handleCareerSelect(m)} disabled={loading} />
            ))}
          </div>
        </div>
      )}

      {/* Redesign results */}
      <div ref={resultsRef}>
        {result && (
          <div className="container page" style={{ paddingTop: "1rem" }}>
            {/* Role header */}
            <div style={{ marginBottom: "2rem" }}>
              <h2 style={{ fontSize: "1.6rem" }}>
                {result.role}
                {result.target_role && (
                  <>
                    {" "}<span style={{ color: "var(--purple-600)" }}>→</span> {result.target_role}
                  </>
                )}
              </h2>
              <div className="row" style={{ gap: "0.5rem" }}>
                <span className="badge">{result.role_category}</span>
                {result.target_role && result.target_role_category && (
                  <span className="badge badge-outline">Target: {result.target_role_category}</span>
                )}
                <span className="muted">{result.suggestions.length} {result.target_role ? "transition pathways" : "plan options"}</span>
              </div>
              {/* Plan actions: save (bookmark) + regenerate */}
              <div className="row" style={{ gap: "0.5rem", marginTop: "0.75rem" }}>
                <button className="btn btn-secondary btn-sm" onClick={handleSavePlan}>
                  {savedFlash ? "Saved ✓" : "Save this plan"}
                </button>
                <button className="btn btn-ghost btn-sm" onClick={handleRegenerate} disabled={loading}>
                  ↻ Regenerate
                </button>
              </div>
              {result.role_core_tasks.length > 0 && (
                <details style={{ marginTop: "0.75rem" }}>
                  <summary className="muted" style={{ cursor: "pointer", fontWeight: 600 }}>
                    {result.target_role
                      ? "What your target role does day-to-day (and how much AI can help)"
                      : "What this job does day-to-day (and how much AI can help)"}
                  </summary>
                  <ul style={{ marginTop: "0.5rem", color: "var(--ink-700)", paddingLeft: "1.5rem", listStyle: "none" }}>
                    {result.role_core_tasks.map((t, i) => <TaskRow key={i} task={t} />)}
                  </ul>
                </details>
              )}
            </div>

            {/* Suggestion cards */}
            <div className="stack">
              {result.suggestions.map((s, i) => (
                <SuggestionCard key={i} suggestion={s} role={result.role} targetRole={result.target_role} />
              ))}
            </div>

            {/* Disclaimer */}
            <div className="notice" style={{ marginTop: "2rem", fontSize: "0.85rem" }}>
              The funding shown here is an estimate based on your age. Before you sign up for a course,
              double-check exactly what you can claim on{" "}
              <a href="https://www.myskillsfuture.gov.sg" target="_blank" rel="noopener noreferrer">MySkillsFuture</a>{" "}
              — schemes change with each national Budget.
            </div>
          </div>
        )}
      </div>
    </>
  );
}


function TaskRow({ task }: { task: TaskWithScore }) {
  const badge = aiScoreBadge(task.ai_augmentable);
  return (
    <li style={{ marginBottom: "0.4rem", display: "flex", alignItems: "center", gap: "0.6rem", flexWrap: "wrap" }}>
      <span>{task.task}</span>
      <span className={`badge ${badge.cls}`} style={{ fontSize: "0.68rem" }} title="How much of this task AI could help with">
        {badge.label}
      </span>
    </li>
  );
}


function TargetSelector({
  wantTarget,
  setWantTarget,
  targetInput,
  setTargetInput,
  roles,
  onSubmit,
  style,
}: {
  wantTarget: boolean;
  setWantTarget: (v: boolean) => void;
  targetInput: string;
  setTargetInput: (v: string) => void;
  roles: RoleOut[];
  onSubmit?: () => void;
  style?: CSSProperties;
}) {
  const [showDropdown, setShowDropdown] = useState(false);

  const filtered = useMemo(() => {
    const q = targetInput.toLowerCase().trim();
    if (!q) return roles.slice(0, 8);
    return roles
      .filter(r => r.title.toLowerCase().includes(q) || r.category.toLowerCase().includes(q))
      .slice(0, 8);
  }, [roles, targetInput]);

  return (
    <div style={{
      background: "var(--bg-subtle)", border: "1px solid var(--border)",
      borderRadius: "var(--radius-lg)", padding: "1rem", textAlign: "left", ...style,
    }}>
      <strong style={{ fontSize: "0.9rem" }}>Where do you want to transition to?</strong>
      <div className="row" style={{ gap: "0.5rem", marginTop: "0.6rem", flexWrap: "wrap" }}>
        <button
          type="button"
          className={`btn btn-sm ${!wantTarget ? "btn-primary" : "btn-ghost"}`}
          onClick={() => setWantTarget(false)}
        >
          I'm not sure — show me options
        </button>
        <button
          type="button"
          className={`btn btn-sm ${wantTarget ? "btn-primary" : "btn-ghost"}`}
          onClick={() => setWantTarget(true)}
        >
          I have a target role
        </button>
      </div>

      {wantTarget && (
        <div className="field" style={{ marginTop: "0.75rem", marginBottom: 0, position: "relative" }}>
          <label htmlFor="target-role">Target role</label>
          <input
            id="target-role"
            type="text"
            placeholder="e.g. Data Analyst, Product Manager, UX Designer"
            value={targetInput}
            onChange={e => { setTargetInput(e.target.value); setShowDropdown(true); }}
            onFocus={() => setShowDropdown(true)}
            onBlur={() => setTimeout(() => setShowDropdown(false), 150)}
            onKeyDown={e => { if (e.key === "Enter" && onSubmit) onSubmit(); }}
            style={{ width: "100%" }}
          />
          {showDropdown && filtered.length > 0 && (
            <div style={{
              position: "absolute", top: "100%", left: 0, right: 0,
              background: "var(--bg-card)", border: "1px solid var(--border)",
              borderRadius: "0 0 14px 14px", boxShadow: "var(--shadow-lg)",
              zIndex: 30, textAlign: "left", maxHeight: 320, overflowY: "auto",
            }}>
              {filtered.map(r => (
                <button
                  key={r.id}
                  onClick={() => { setTargetInput(r.title); setShowDropdown(false); }}
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
      )}
    </div>
  );
}


function CareerMatchCard({ match, onSelect, disabled }: { match: CareerMatch; onSelect: () => void; disabled: boolean }) {
  return (
    <div className="card">
      <div className="row-between" style={{ marginBottom: "0.6rem", flexWrap: "wrap", gap: "0.5rem" }}>
        <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap" }}>
          <h3 style={{ fontSize: "1.2rem", margin: 0 }}>{match.role_title}</h3>
          <span className="badge badge-outline">{match.category}</span>
          {match.industry_switch && (
            <span className="badge badge-warning" title="This is a different industry from your current job — but your skills still fit">
              New industry
            </span>
          )}
        </div>
        <span className="badge badge-success" style={{ fontSize: "0.85rem" }}>{match.fit_score}% fit</span>
      </div>

      <p style={{ marginBottom: "0.75rem" }}>{match.reason}</p>

      {match.transferable_skills.length > 0 && (
        <div style={{ marginBottom: "0.6rem" }}>
          <strong style={{ fontSize: "0.8rem", color: "var(--ink-500)" }}>Transferable skills</strong>
          <div className="tags" style={{ marginTop: "0.3rem" }}>
            {match.transferable_skills.map((s, i) => (
              <span key={i} className="badge badge-success" style={{ fontSize: "0.72rem" }}>{s}</span>
            ))}
          </div>
        </div>
      )}

      {match.skill_gaps.length > 0 && (
        <div style={{ marginBottom: "0.75rem" }}>
          <strong style={{ fontSize: "0.8rem", color: "var(--ink-500)" }}>Skills to learn</strong>
          <div className="tags" style={{ marginTop: "0.3rem" }}>
            {match.skill_gaps.map((s, i) => (
              <span key={i} className="badge badge-warning" style={{ fontSize: "0.72rem" }}>{s}</span>
            ))}
          </div>
        </div>
      )}

      <button className="btn btn-primary btn-sm" onClick={onSelect} disabled={disabled}>
        Show my upskilling plan →
      </button>
    </div>
  );
}


function SuggestionCard({ suggestion, role, targetRole }: {
  suggestion: RedesignSuggestion;
  role: string;
  targetRole?: string | null;
}) {
  const [expanded, setExpanded] = useState(false);
  const [fbState, setFbState] = useState<"idle" | "comment" | "sending" | "done">("idle");
  const [fbComment, setFbComment] = useState("");
  const impact = IMPACT_STYLES[suggestion.ai_impact] || IMPACT_STYLES.augment;

  async function sendFeedback(rating: "helpful" | "not_right", comment?: string) {
    setFbState("sending");
    try {
      await api.post("/api/feedback", {
        role,
        target_role: targetRole ?? null,
        suggestion_title: suggestion.title,
        rating,
        comment: comment?.trim() || null,
      });
      setFbState("done");
    } catch {
      setFbState("idle");
    }
  }

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

      {/* Transferable skills + gaps (personalised) */}
      {(suggestion.transferable_skills.length > 0 || suggestion.skill_gaps.length > 0) && (
        <div className="row" style={{ gap: "1rem", marginBottom: "0.75rem", flexWrap: "wrap" }}>
          {suggestion.transferable_skills.length > 0 && (
            <div style={{ flex: 1, minWidth: 220 }}>
              <strong style={{ fontSize: "0.8rem", color: "var(--ink-500)" }}>Your transferable skills</strong>
              <div className="tags" style={{ marginTop: "0.3rem" }}>
                {suggestion.transferable_skills.map((s, i) => (
                  <span key={i} className="badge badge-success" style={{ fontSize: "0.72rem" }}>{s}</span>
                ))}
              </div>
            </div>
          )}
          {suggestion.skill_gaps.length > 0 && (
            <div style={{ flex: 1, minWidth: 220 }}>
              <strong style={{ fontSize: "0.8rem", color: "var(--ink-500)" }}>Skills to learn</strong>
              <div className="tags" style={{ marginTop: "0.3rem" }}>
                {suggestion.skill_gaps.map((s, i) => (
                  <span key={i} className="badge badge-warning" style={{ fontSize: "0.72rem" }}>{s}</span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

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

      {/* Feedback (Phase 3) */}
      <div style={{ marginTop: "0.75rem", borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
        {fbState === "done" ? (
          <p className="muted" style={{ margin: 0, fontSize: "0.85rem" }}>
            Thanks — your feedback is shaping future suggestions.
          </p>
        ) : fbState === "comment" ? (
          <div>
            <textarea
              value={fbComment}
              onChange={e => setFbComment(e.target.value)}
              placeholder="Optional: what didn't feel right? (e.g. too technical, not my industry…)"
              rows={2}
              style={{ width: "100%", fontSize: "0.85rem", marginBottom: "0.5rem" }}
            />
            <div className="row" style={{ gap: "0.4rem" }}>
              <button
                className="btn btn-primary btn-sm"
                disabled={fbState === "sending"}
                onClick={() => sendFeedback("not_right", fbComment)}
              >
                {fbState === "sending" ? "Sending…" : "Send feedback"}
              </button>
              <button className="btn btn-ghost btn-sm" onClick={() => setFbState("idle")}>Cancel</button>
            </div>
          </div>
        ) : (
          <div className="row" style={{ gap: "0.5rem", flexWrap: "wrap", alignItems: "center" }}>
            <span className="muted" style={{ fontSize: "0.85rem" }}>Was this option helpful?</span>
            <button className="btn btn-ghost btn-sm" disabled={fbState === "sending"} onClick={() => sendFeedback("helpful")}>
              👍 Helpful
            </button>
            <button className="btn btn-ghost btn-sm" disabled={fbState === "sending"} onClick={() => setFbState("comment")}>
              👎 Doesn't feel right for my role
            </button>
          </div>
        )}
      </div>
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
