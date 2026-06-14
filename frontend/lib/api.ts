import axios from 'axios';

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.response.use(
  (res) => res,
  (error) => {
    console.error('API Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

export default api;

// ─── Types ────────────────────────────────────────────────────────────────────

export interface Filter {
  field: string;
  operator: '>' | '<' | '>=' | '<=' | '=' | '!=';
  value: number | string;
}

export interface CampaignPlan {
  audience_name: string;
  filters: Filter[];
  channel: 'whatsapp' | 'sms' | 'email' | 'rcs';
  strategy: string;
  reasoning: string;
}

export interface Campaign {
  id: number;
  name: string;
  audience_name?: string;
  filters?: Filter[];
  channel: string;
  strategy?: string;
  message_template?: string;
  subject_line?: string;
  status: string;
  audience_size: number;
  business_goal?: string;
  ai_reasoning?: string;
  created_at: string;
  updated_at: string;
  metrics?: Record<string, number>;
}

// ─── Upload ───────────────────────────────────────────────────────────────────

export const uploadCustomers = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/customers', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

export const uploadOrders = (file: File) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/upload/orders', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
};

// ─── Intelligence ─────────────────────────────────────────────────────────────

export const generateProfiles = () => api.post('/intelligence/generate-profiles');
export const getProfiles = (params?: { segment?: string; page?: number }) =>
  api.get('/intelligence/profiles', { params });
export const getSegments = () => api.get('/intelligence/segments');
export const getSummary = () => api.get('/intelligence/summary');

// ─── Campaigns ────────────────────────────────────────────────────────────────

export const generatePlan = (goal: string) =>
  api.post('/campaigns/plan', { business_goal: goal });
export const createCampaign = (data: Partial<Campaign> & { filters?: Filter[] }) =>
  api.post('/campaigns', data);
export const generateMessage = (id: number) =>
  api.post(`/campaigns/${id}/generate-message`);
export const approveCampaign = (id: number) =>
  api.post(`/campaigns/${id}/approve`);
export const launchCampaign = (id: number) =>
  api.post(`/campaigns/${id}/launch`);
export const resetCampaign = (id: number) =>
  api.post(`/campaigns/${id}/reset`);
export const getCampaigns = (status?: string, page = 1) =>
  api.get('/campaigns', { params: { status, page } });
export const getCampaign = (id: number) => api.get(`/campaigns/${id}`);

// ─── Audience ─────────────────────────────────────────────────────────────────

export const previewAudience = (filters: Filter[]) =>
  api.post('/audience/preview', { filters });
export const buildAudience = (campaignId: number, filters: Filter[]) =>
  api.post('/audience/build', { campaign_id: campaignId, filters });
export const getCampaignAudience = (id: number, page = 1) =>
  api.get(`/audience/campaign/${id}`, { params: { page } });

// ─── Analytics ────────────────────────────────────────────────────────────────

export const getCampaignAnalytics = (id: number) =>
  api.get(`/analytics/campaigns/${id}`);
export const getDashboard = () => api.get('/analytics/dashboard');
export const getTimeline = (id: number) =>
  api.get(`/analytics/campaigns/${id}/timeline`);
