import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Play, Download, Clock, Scissors } from 'lucide-react';
import { Job } from '@/lib/api';
import { apiClient } from '@/lib/api';

interface VideoPlayerProps {
  job: Job;
  user: { email: string; name?: string } | null;
}

export const VideoPlayer = ({ job, user }: VideoPlayerProps) => {
  const handleDownload = () => {
    if (job.video_url) {
      const link = document.createElement('a');
      link.href = apiClient.getVideoUrl(job.id, user?.email);
      link.download = `clip_${job.id}.mp4`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
    }
  };

  return (
      <Card className="glass-effect border-0 shadow-2xl">
        <CardHeader>
        <CardTitle className="text-xl text-neon-green flex items-center gap-2">
            <Play className="h-5 w-5" />
          Your Generated Clip
          </CardTitle>
        </CardHeader>
      <CardContent className="space-y-6">
        {/* Video Player */}
        {job.video_url && (
          <div className="relative">
            <video
              controls
              className="w-full rounded-lg bg-black"
              style={{ aspectRatio: '16/9' }}
            >
              <source src={apiClient.getVideoUrl(job.id, user?.email)} type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
        )}

        {/* Download Button */}
        <div className="flex justify-center">
          <Button
            onClick={handleDownload}
            className="bg-gradient-to-r from-neon-green to-neon-cyan hover:from-neon-cyan hover:to-neon-green transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-green/25"
          >
            <Download className="mr-2 h-5 w-5" />
            Download Clip
            </Button>
          </div>

        {/* Clips Information */}
        {job.clips && job.clips.length > 0 && (
          <div className="space-y-4">
            <div className="flex items-center gap-2">
              <Scissors className="h-4 w-4 text-neon-purple" />
              <h3 className="font-medium text-neon-purple">Generated Clips</h3>
            </div>
            
            <div className="grid gap-3">
            {job.clips.map((clip) => (
                <div
                  key={clip.id}
                  className="flex items-center justify-between p-3 rounded-lg bg-dark-card/50 border border-neon-purple/20"
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 rounded-full bg-neon-purple/20">
                      <Clock className="h-4 w-4 text-neon-purple" />
                    </div>
                    <div>
                      <p className="font-medium text-sm text-foreground">
                        {clip.title}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {clip.timeframe}
                      </p>
                  </div>
                </div>
                
                  <Badge className="bg-neon-purple/20 text-neon-purple border-neon-purple/30">
                    {clip.duration}
                  </Badge>
                </div>
              ))}
                </div>
              </div>
        )}

        {/* Job Information */}
        <div className="pt-4 border-t border-dark-card">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <p className="text-muted-foreground">Status</p>
              <p className="font-medium text-green-400">Completed</p>
            </div>
            <div>
              <p className="text-muted-foreground">Clips Generated</p>
              <p className="font-medium">{job.clips.length}</p>
            </div>
          </div>
          </div>
        </CardContent>
      </Card>
  );
};
