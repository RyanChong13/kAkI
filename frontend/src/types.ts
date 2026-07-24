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

export interface CourseRecommendation {
  course: Course;
  match_score: number;
  matched_skills: string[];
}

export interface Job {
  id: number;
  external_id: string;
  source: string;
  title: string;
  company: string;
  description: string;
  category: string;
  salary_min_sgd: number;
  salary_max_sgd: number;
  location: string;
  url: string;
  skills_required: string;
  posted_date: string | null;
}

export interface JobRecommendation {
  job: Job;
  match_score: number;
  matched_skills: string[];
}

export interface User {
  id: number;
  email: string;
  name: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface ResumeProfile {
  filename: string;
  extracted_name: string;
  extracted_skills: string;
  years_experience_guess: number | null;
  uploaded_at: string;
}

export interface ApplicationOut {
  id: number;
  job_id: number;
  status: string;
  created_at: string;
}

export interface GrantOffer {
  course: Course;
  credit_amount_sgd: number;
  eligible: boolean;
}

export interface GrantApplicationOut {
  id: number;
  course_id: number;
  credit_amount_sgd: number;
  status: string;
  created_at: string;
}

export interface SavedCourseOut {
  id: number;
  course: Course;
  created_at: string;
}
