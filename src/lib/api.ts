const API_BASE_URL = 'http://localhost:8000';

export interface VideoRequest {
  youtube_url: string;
  instructions?: string;
  user_id?: string;
}

export interface JobResponse {
  job_id: string;
  status: string;
  message: string;
}

export interface JobStatus {
  job_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  error?: string;
  video_url?: string;
  clips?: Array<{
    id: string;
    title: string;
    duration: string;
    timeframe: string;
    start: number;
    end: number;
  }>;
  created_at: string;
  updated_at: string;
}

export interface Job {
  id: string;
  youtube_url: string;
  instructions: string;
  user_id: string;
  status: 'queued' | 'processing' | 'completed' | 'failed';
  progress: number;
  current_step: string;
  video_path?: string;
  video_url?: string;
  clips: Array<{
    id: string;
    title: string;
    duration: string;
    timeframe: string;
    start: number;
    end: number;
  }>;
  error?: string;
  created_at: string;
  updated_at: string;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      const error = await response.text();
      throw new Error(`API Error: ${response.status} - ${error}`);
    }

    return response.json();
  }

  async createJob(request: VideoRequest): Promise<JobResponse> {
    return this.request<JobResponse>('/api/jobs', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getJobStatus(jobId: string, userId?: string): Promise<JobStatus> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<JobStatus>(`/api/jobs/${jobId}${params}`);
  }

  async listJobs(userId?: string): Promise<{ jobs: Job[] }> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<{ jobs: Job[] }>(`/api/jobs${params}`);
  }

  async deleteJob(jobId: string, userId?: string): Promise<{ message: string }> {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return this.request<{ message: string }>(`/api/jobs/${jobId}${params}`, {
      method: 'DELETE',
    });
  }

  getVideoUrl(jobId: string, userId?: string): string {
    const params = userId ? `?user_id=${encodeURIComponent(userId)}` : '';
    return `${this.baseUrl}/api/videos/${jobId}${params}`;
  }

  getWebSocketUrl(jobId: string): string {
    return `ws://localhost:8000/ws/${jobId}`;
  }
}

export const apiClient = new ApiClient(); 