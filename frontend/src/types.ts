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
  // Organiser-specific
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

// ── AI Features ───────────────────────────────────────────────────────────────

export interface GrowthPlanDay {
  day: number;
  date_label: string;
  activities: Array<{
    event_id: number;
    title: string;
    type: string;
    time: string;
    duration_hours: number;
    location: string;
    explanation: string;
    category: string;
  }>;
}

export interface GrowthPlanOut {
  id: number;
  plan_type: string;
  days: GrowthPlanDay[];
  created_at: string;
}

export interface LearningJourneyWeek {
  week: number;
  title: string;
  events: any[];
  focus: string;
}

export interface LearningJourneyOut {
  id: number;
  goal: string;
  current_week: number;
  total_weeks: number;
  roadmap: LearningJourneyWeek[];
  created_at: string;
}

export interface AIListingResult {
  title: string;
  description: string;
  category: string;
  tags: string[];
  skills: string[];
  seo_keywords: string[];
  difficulty: string;
  recommended_audience: string;
  duration_hours: number | null;
  price_suggestion_sgd: number;
}

export interface ChatResponse {
  reply: string;
  language: string;
}

// ── Organiser ─────────────────────────────────────────────────────────────────

export interface OrganiserDashboardStats {
  total_events: number;
  total_attendees: number;
  avg_rating: number;
  upcoming_events: number;
  revenue_sgd: number;
  monthly_growth: Array<{
    month: string;
    events: number;
    attendees: number;
    revenue: number;
  }>;
}

// ── Legacy ────────────────────────────────────────────────────────────────────

export type CourseSource = "skillsfuture" | "eventbrite";

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
  price_sgd: number;  // estimated payable after subsidy
  full_price_sgd: number;  // full course fee before subsidy
  skillsfuture_credit_eligible: boolean;
  skillsfuture_credit_amount: number;  // subsidy amount
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

export interface ResumeProfile {
  filename: string;
  extracted_name: string;
  extracted_skills: string;
  years_experience_guess: number | null;
  uploaded_at: string;
}

export interface GrantApplicationOut {
  id: number;
  course_id: number;
  credit_amount_sgd: number;
  status: string;
  created_at: string;
}
