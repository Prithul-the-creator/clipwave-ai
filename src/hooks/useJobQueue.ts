import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient, Job, VideoRequest } from '@/lib/api';

export const useJobQueue = (userId?: string) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const websocketRef = useRef<WebSocket | null>(null);

  // Load initial jobs
  useEffect(() => {
    loadJobs();
  }, [userId]);

  const loadJobs = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await apiClient.listJobs(userId);
      setJobs(response.jobs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load jobs');
    } finally {
      setLoading(false);
    }
  }, [userId]);

  const createJob = useCallback(async (request: VideoRequest) => {
    try {
      setError(null);
      const response = await apiClient.createJob({
        ...request,
        user_id: userId || 'anonymous'
      });

      // Add the new job to the queue
      const newJob: Job = {
        id: response.job_id,
        youtube_url: request.youtube_url,
        instructions: request.instructions || '',
        user_id: userId || 'anonymous',
        status: 'queued',
        progress: 0,
        current_step: 'Queued',
        clips: [],
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      };

      setJobs(prev => [newJob, ...prev]);

      // Connect to WebSocket for real-time updates
      connectWebSocket(response.job_id);

      return response.job_id;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create job');
      throw err;
    }
  }, [userId]);

  const deleteJob = useCallback(async (jobId: string) => {
    try {
      await apiClient.deleteJob(jobId, userId);
      setJobs(prev => prev.filter(job => job.id !== jobId));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete job');
    }
  }, [userId]);

  const connectWebSocket = useCallback((jobId: string) => {
    // Close existing connection if any
    if (websocketRef.current) {
      websocketRef.current.close();
    }

    const ws = new WebSocket(apiClient.getWebSocketUrl(jobId));
    websocketRef.current = ws;

    ws.onopen = () => {
      console.log(`WebSocket connected for job ${jobId}`);
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.type === 'job_update' && data.job_id === jobId) {
          setJobs(prev => prev.map(job => 
            job.id === jobId 
              ? { ...job, ...data.data }
              : job
          ));
        }
      } catch (err) {
        console.error('Failed to parse WebSocket message:', err);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    ws.onclose = () => {
      console.log(`WebSocket disconnected for job ${jobId}`);
    };
  }, []);

  const disconnectWebSocket = useCallback(() => {
    if (websocketRef.current) {
      websocketRef.current.close();
      websocketRef.current = null;
    }
  }, []);

  // Cleanup WebSocket on unmount
  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  const getJobById = useCallback((jobId: string) => {
    return jobs.find(job => job.id === jobId);
  }, [jobs]);

  const getCurrentJob = useCallback(() => {
    return jobs.find(job => job.status === 'processing') || null;
  }, [jobs]);

  const getCompletedJobs = useCallback(() => {
    return jobs.filter(job => job.status === 'completed');
  }, [jobs]);

  const getFailedJobs = useCallback(() => {
    return jobs.filter(job => job.status === 'failed');
  }, [jobs]);

  return {
    jobs,
    loading,
    error,
    createJob,
    deleteJob,
    loadJobs,
    getJobById,
    getCurrentJob,
    getCompletedJobs,
    getFailedJobs,
    connectWebSocket,
    disconnectWebSocket
  };
}; 