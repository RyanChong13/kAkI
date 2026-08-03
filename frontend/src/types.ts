// ── Core User ─────────────────────────────────────────────────────────────────

export type UserRole = "public" | "organiser";

export interface User {
  id: number;
  email: string;
  name: string;
  role: UserRole;
  linkedin_url: string;
  interests: string;
  career_goals: string;
  preferred_timings: string;
  availability_hours_per_week: number;
  budget_sgd: number;
  company_name?: string;
  bio?: string;
  website?: string;
  phone?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

// ── Course ────────────────────────────────────────────────────────────────────

export type CourseSource = "skillsfuture";

export interface Course {
  id: number;
  external_id: string;
  source: CourseSource;
  title: string;
  provider: string;
  description: string;
  category: string;
  date: string | null;
  duration_hours: number | null;
  price_sgd: number;
  full_price_sgd: number;
  skillsfuture_credit_eligible: boolean;
  skillsfuture_credit_amount: number;
  base_credit_eligible: boolean;
  mid_career_eligible: boolean;
  sctp_eligible: boolean;
  level_up_eligible: boolean;
  location: string;
  url: string;
  image_url: string;
  skills: string;
  fetched_at: string;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
}

// ── Role Taxonomy ─────────────────────────────────────────────────────────────

export interface TaskWithScore {
  task: string;
  ai_augmentable: number;
}

export interface RoleOut {
  id: string;
  title: string;
  category: string;
  core_tasks: TaskWithScore[];
}

export interface RoleListResponse {
  categories: string[];
  roles: RoleOut[];
}

// ── Redesign ──────────────────────────────────────────────────────────────────

export interface RedesignRequest {
  role: string;
  age?: number;
  user_skills?: string[];
  target_role?: string;
}

export interface SchemeInfo {
  scheme_id: string;
  scheme_name: string;
  eligible: boolean;
  credit_amount_sgd: number | null;
  description: string;
  eligibility_notes: string;
  age_note: string;
  official_url: string;
}

export interface MatchedCourseOut {
  course: Course;
  match_score: number;
  matched_skills: string[];
  schemes: SchemeInfo[];
}

export interface RedesignSuggestion {
  title: string;
  description: string;
  why: string;
  ai_impact: string;
  upskilling_areas: string[];
  estimated_timeframe: string;
  transferable_skills: string[];
  skill_gaps: string[];
  matched_courses: MatchedCourseOut[];
}

export interface RedesignResult {
  role: string;
  role_category: string;
  role_core_tasks: TaskWithScore[];
  target_role?: string | null;
  target_role_category?: string | null;
  suggestions: RedesignSuggestion[];
}

// ── Resume Analysis ─────────────────────────────────────────────────────────────

export interface CareerMatch {
  role_id: string;
  role_title: string;
  category: string;
  fit_score: number;
  reason: string;
  transferable_skills: string[];
  skill_gaps: string[];
  industry_switch: boolean;
}

export interface ResumeAnalysis {
  skills: string[];
  current_role_guess: string;
  career_matches: CareerMatch[];
}
