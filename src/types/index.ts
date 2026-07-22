export interface User {
  id: number;
  email: string;
  name: string;
  age?: number;
  sector?: string;
  income_band?: string;
  grant_history: string[];
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface SkillItem {
  skill: string;
  years: number;
  source: string;
}

export interface Resume {
  id: number;
  user_id: number;
  parsed_skills: SkillItem[];
  uploaded_at: string;
}

export interface FlowSession {
  id: number;
  user_id: number;
  path: 'redeployment' | 'upskilling';
  round_number: number;
  status: 'active' | 'applied_round_1' | 'applied_round_2' | 'exited';
  created_at: string;
  updated_at: string;
}

export interface JobSuggestion {
  id: number;
  session_id: number;
  title: string;
  matched_skills: string[];
  missing_skills: string[];
  user_feedback?: 'liked' | 'disliked';
  round_number: number;
  selected: boolean;
}

export interface GrantInfo {
  id: number;
  name: string;
  amount: number;
  cap_remaining: number;
}

export interface GrantRecommendation {
  id: number;
  session_id: number;
  grant_id: number;
  course_name?: string;
  selected: boolean;
  grant?: GrantInfo;
}

export interface CourseSuggestion {
  name: string;
  provider: string;
  duration: string;
  cost: string;
  skill_gap_addressed: string;
}

export interface ApplyPreviewItem {
  target_id: number;
  target_name: string;
  type: string;
  details: Record<string, unknown>;
}

export interface Application {
  id: number;
  user_id: number;
  session_id: number;
  type: 'job' | 'grant';
  target_id: number;
  target_name: string;
  confirmed: boolean;
  submitted_at?: string;
}
