import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Progress } from '@/components/ui/progress';
import { Trash2, Clock, CheckCircle, AlertCircle, Loader2 } from 'lucide-react';
import { formatDistanceToNow } from 'date-fns';
import { Job } from '@/lib/api';

interface JobQueueProps {
  jobs: Job[];
  currentJob: Job | null;
  onJobSelect: (job: Job) => void;
  onJobDelete: (jobId: string) => void;
  loading?: boolean;
}

export const JobQueue = ({ jobs, currentJob, onJobSelect, onJobDelete, loading = false }: JobQueueProps) => {
  const getStatusIcon = (status: Job['status']) => {
    switch (status) {
      case 'processing':
        return <Clock className="h-4 w-4 text-neon-blue animate-pulse" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      case 'queued':
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusColor = (status: Job['status']) => {
    switch (status) {
      case 'processing':
        return 'bg-neon-blue/20 text-neon-blue border-neon-blue/30';
      case 'completed':
        return 'bg-green-500/20 text-green-400 border-green-500/30';
      case 'failed':
        return 'bg-red-500/20 text-red-400 border-red-500/30';
      case 'queued':
        return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/30';
    }
  };

  const getJobTitle = (job: Job) => {
    // Extract video ID from YouTube URL for a simple title
    const url = job.youtube_url;
    const videoIdMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    return videoIdMatch ? `Video ${videoIdMatch[1].substring(0, 8)}...` : 'YouTube Video';
  };

  const getJobThumbnail = (job: Job) => {
    // Generate thumbnail URL from YouTube video ID
    const url = job.youtube_url;
    const videoIdMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^&\n?#]+)/);
    if (videoIdMatch) {
      return `https://img.youtube.com/vi/${videoIdMatch[1]}/mqdefault.jpg`;
    }
    return 'https://images.unsplash.com/photo-1611162617474-5b21e879e113?w=300&h=200&fit=crop&crop=center';
  };

  return (
    <Card className="glass-effect border-0 shadow-2xl h-fit">
      <CardHeader>
        <CardTitle className="text-xl text-neon-purple flex items-center gap-2">
          <Clock className="h-5 w-5" />
          Job Queue
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4 max-h-[600px] overflow-y-auto">
          {jobs.length === 0 ? (
            <div className="text-center py-8 text-muted-foreground">
              <p>No jobs yet</p>
              <p className="text-sm">Submit a YouTube URL to get started</p>
            </div>
          ) : (
            jobs.map((job) => (
              <div
                key={job.id}
                className={`p-4 rounded-lg cursor-pointer transition-all duration-200 ${
                  currentJob?.id === job.id
                    ? 'bg-neon-blue/10 border border-neon-blue/30'
                    : 'bg-dark-card/50 hover:bg-dark-card/70 border border-transparent'
                }`}
                onClick={() => onJobSelect(job)}
              >
                <div className="flex items-start gap-3">
                  <img
                    src={getJobThumbnail(job)}
                    alt={getJobTitle(job)}
                    className="w-16 h-12 rounded object-cover flex-shrink-0"
                  />
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <h3 className="font-medium text-sm truncate text-foreground">
                        {getJobTitle(job)}
                      </h3>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation();
                          onJobDelete(job.id);
                        }}
                        className="text-muted-foreground hover:text-red-400 p-1 h-auto"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                    
                    <div className="flex items-center gap-2 mt-2">
                      {getStatusIcon(job.status)}
                      <Badge className={`text-xs ${getStatusColor(job.status)}`}>
                        {job.status}
                      </Badge>
                    </div>

                    {job.status === 'processing' && (
                      <div className="mt-2">
                        <Progress value={job.progress} className="h-1" />
                        <p className="text-xs text-muted-foreground mt-1">
                          {job.progress}% complete
                        </p>
                      </div>
                    )}

                    {job.status === 'completed' && (
                      <p className="text-xs text-muted-foreground mt-1">
                        {job.clips.length} clips generated
                      </p>
                    )}

                    {job.status === 'failed' && job.error && (
                      <p className="text-xs text-red-400 mt-1 truncate">
                        {job.error}
                      </p>
                    )}
                    
                    <p className="text-xs text-muted-foreground mt-1">
                      {formatDistanceToNow(new Date(job.created_at), { addSuffix: true })}
                    </p>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </CardContent>
    </Card>
  );
};
