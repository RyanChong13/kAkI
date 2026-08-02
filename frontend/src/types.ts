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

// ── Event ─────────────────────────────────────────────────────────────────────

export interface Event {
  id: number;
  external_id: string;
  source: string;
  title: string;
  organiser: string;
  description: string;
  category: string;
  location: string;
  date: string | null;
  duration_hours: number | null;
  price_sgd: number;
  skills: string;
  difficulty: string;
  image_url: string;
  tags: string;
  seo_keywords: string;
  recommended_audience: string;
  embedding_tags: string;
  capacity: number | null;
  attendees_count: number;
  is_cancelled: boolean;
  is_full: boolean;
  created_by: number | null;
  fetched_at: string;
}

export interface EventListResponse {
  items: Event[];
  total: number;
}

export interface EventRecommendation {
  event: Event;
  match_score: number;
  matched_skills: string[];
  reason: string;
}

export interface SavedEventOut {
  id: number;
  event: Event;
  created_at: string;
}

export interface EventRegistrationOut {
  id: number;
  event: Event;
  registered_at: string;
}

export interface ResumeAnalysisResult {
  extracted_skills: string[];
  extracted_interests: string[];
  experience_years: number | null;
  suggested_categories: string[];
  summary: string;
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
  events: Event[];
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

export interface SubstituteResult {
  original: Event;
  alternatives: EventRecommendation[];
  reason: string;
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

export interface EventAnalytics {
  event_id: number;
  title: string;
  views: number;
  registrations: number;
  attendance_rate: number;
  avg_rating: number;
  demographics: Record<string, Record<string, number>>;
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
  price_sgd: number;
  skillsfuture_credit_eligible: boolean;
  skillsfuture_credit_amount: number;
  location: string;
  url: string;
  image_url: string;
  skills: string;
  fetched_at: string;
}

export interface CourseListResponse {
  items: Course[];
  total: number;
  eventbrite_available: boolean;
  eventbrite_notice: string | null;
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
