import { useState, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Upload } from 'lucide-react';
import { JobQueue } from './JobQueue';
import { VideoPlayer } from './VideoPlayer';
import { ProgressTracker } from './ProgressTracker';
import { useJobQueue } from '@/hooks/useJobQueue';
import { Job } from '@/lib/api';
import { toast } from 'sonner';
import HeroSection from './HeroSection';

interface DashboardProps {
  user: { email: string; name?: string } | null;
}

export const Dashboard = ({ user }: DashboardProps) => {
  const [youtubeUrl, setYoutubeUrl] = useState('');
  const [instructions, setInstructions] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [currentJobId, setCurrentJobId] = useState<string | null>(null);
  
  const { 
    jobs, 
    loading, 
    error, 
    createJob, 
    deleteJob 
  } = useJobQueue(user?.email);

  const currentJob = currentJobId ? jobs.find(job => job.id === currentJobId) || null : null;

  useEffect(() => {
    if (!currentJobId && jobs.length > 0) {
      setCurrentJobId(jobs[0].id);
    }
  }, [jobs, currentJobId]);

  const handleSubmit = async () => {
    if (!youtubeUrl.trim()) {
      toast.error('Please enter a YouTube URL');
      return;
    }
    
    setIsSubmitting(true);
    
    try {
      const jobId = await createJob({
        youtube_url: youtubeUrl.trim(),
        instructions: instructions.trim(),
        user_id: user?.email || 'anonymous'
      });
      setCurrentJobId(jobId);
      setYoutubeUrl('');
      setInstructions('');
      toast.success('Job created successfully! Processing will begin shortly.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to create job');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleJobSelect = (job: Job) => {
    setCurrentJobId(job.id);
  };

  const handleJobDelete = async (jobId: string) => {
    try {
      await deleteJob(jobId);
      if (currentJobId === jobId) {
        setCurrentJobId(null);
      }
      toast.success('Job deleted successfully');
    } catch (err) {
      toast.error('Failed to delete job');
    }
  };

  useEffect(() => {
    if (error) {
      toast.error(error);
    }
  }, [error]);

  return (
    <div className="pt-20">
      <HeroSection user={user} />
      <div className="container mx-auto px-6 pb-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2 space-y-8">
            <Card className="glass-effect border-0 shadow-2xl">
              <CardHeader>
                <CardTitle className="text-2xl text-neon-blue flex items-center gap-2">
                  <Upload className="w-6 h-6" />
                  Create New Clip
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-2">
                  <label className="text-sm font-medium">YouTube URL</label>
                  <Input
                    placeholder="https://youtube.com/watch?v=..."
                    value={youtubeUrl}
                    onChange={(e) => setYoutubeUrl(e.target.value)}
                    className="bg-dark-card/50 border-neon-blue/30 focus:border-neon-blue text-foreground placeholder:text-muted-foreground"
                    disabled={isSubmitting}
                  />
                </div>
                
                <div className="space-y-2">
                  <label className="text-sm font-medium">Instructions (Optional)</label>
                  <Textarea
                    placeholder="e.g., Only parts where the speaker mentions AI, or highlight emotional moments..."
                    value={instructions}
                    onChange={(e) => setInstructions(e.target.value)}
                    className="bg-dark-card/50 border-neon-blue/30 focus:border-neon-blue text-foreground placeholder:text-muted-foreground min-h-[100px]"
                    disabled={isSubmitting}
                  />
                </div>

                <Button
                  onClick={handleSubmit}
                  disabled={!youtubeUrl.trim() || isSubmitting || loading}
                  className="w-full bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25"
                >
                  <Upload className="mr-2 h-5 w-5" />
                  {isSubmitting ? 'Creating Job...' : 'Create Clips'}
                </Button>
              </CardContent>
            </Card>

            {currentJob && currentJob.status === 'processing' && (
              <ProgressTracker job={currentJob} />
            )}

            {currentJob && currentJob.status === 'completed' && (
              <VideoPlayer job={currentJob} user={user} />
            )}

            {currentJob && currentJob.status === 'failed' && (
              <Card className="glass-effect border-0 shadow-2xl border-red-500/30">
                <CardHeader>
                  <CardTitle className="text-xl text-red-400 flex items-center gap-2">
                    <Upload className="h-5 w-5" />
                    Processing Failed
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <p className="text-red-300 mb-4">
                    {currentJob.error || 'An error occurred during processing'}
                  </p>
                  <Button
                    variant="outline"
                    onClick={() => setCurrentJobId(null)}
                    className="border-red-500/30 text-red-400 hover:bg-red-500/10"
                  >
                    Dismiss
                  </Button>
                </CardContent>
              </Card>
            )}
          </div>

          <div className="lg:col-span-1">
            <JobQueue 
              jobs={jobs} 
              currentJob={currentJob}
              onJobSelect={handleJobSelect}
              onJobDelete={handleJobDelete}
              loading={loading}
            />
          </div>
        </div>
      </div>
    </div>
  );
};
