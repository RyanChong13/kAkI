import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

// Attach JWT token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const register = (data: { email: string; password: string; name: string; age?: number; sector?: string; income_band?: string }) =>
  api.post('/auth/register', data);

export const login = (data: { email: string; password: string }) =>
  api.post('/auth/login', data);

// Resume
export const uploadResume = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/resume/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const getResume = () => api.get('/resume/me');

// Flow
export const startFlow = (path: string) => api.post('/flow/start', { path });
export const getSession = () => api.get('/flow/session');
export const submitFeedback = (feedback: string, selected_job_ids?: number[]) =>
  api.post('/flow/feedback', { feedback, selected_job_ids });

// Jobs
export const getJobRecommendations = () => api.post('/jobs/recommend');
export const listJobSuggestions = () => api.get('/jobs/suggestions');

// Upskilling
export const getUpskillingPlan = (data: { goal: string; time: string; cost: string; scope: string }) =>
  api.post('/upskilling/plan', data);

// Grants
export const getMatchingGrants = (course_name: string) =>
  api.post(`/grants/match?course_name=${encodeURIComponent(course_name)}`);
export const listGrantRecommendations = () => api.get('/grants/recommendations');

// Apply
export const getApplyPreview = (type: string, target_ids: number[]) =>
  api.post('/apply/preview', { type, target_ids });
export const confirmApply = (preview_id: string) =>
  api.post('/apply/confirm', { preview_id, confirmed: true });
export const getApplyHistory = () => api.get('/apply/history');

export default api;
