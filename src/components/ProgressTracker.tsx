import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Download, FileText, Scissors, Video, CheckCircle } from 'lucide-react';
import { Job } from '@/lib/api';

interface ProgressTrackerProps {
  job: Job;
}

const steps = [
  { id: 1, name: 'Downloading Video', icon: Download, range: [0, 25] },
  { id: 2, name: 'Transcribing with AI', icon: FileText, range: [25, 50] },
  { id: 3, name: 'Identifying Clips', icon: Scissors, range: [50, 75] },
  { id: 4, name: 'Rendering Clips', icon: Video, range: [75, 100] }
];

export const ProgressTracker = ({ job }: ProgressTrackerProps) => {
  const progress = job.progress;

  // Determine current step based on progress
  const currentStep = steps.find(s => progress >= s.range[0] && progress < s.range[1])?.id || 1;

  return (
    <Card className="glass-effect border-0 shadow-2xl">
      <CardHeader>
        <CardTitle className="text-xl text-neon-cyan flex items-center gap-2">
          <Video className="h-5 w-5 animate-pulse" />
          Processing Video
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Overall Progress */}
        <div className="space-y-2">
          <div className="flex justify-between items-center">
            <span className="text-sm font-medium">Overall Progress</span>
            <span className="text-sm text-neon-blue font-mono">{Math.round(progress)}%</span>
          </div>
          <Progress value={progress} className="h-3 bg-dark-card">
            <div 
              className="h-full bg-gradient-to-r from-neon-blue to-neon-purple rounded-full transition-all duration-500 animate-glow"
              style={{ width: `${progress}%` }}
            />
          </Progress>
        </div>

        {/* Current Step Display */}
        <div className="text-center py-4">
          <p className="text-neon-blue font-medium">
            {job.current_step}
          </p>
        </div>

        {/* Step by Step Progress */}
        <div className="space-y-4">
          {steps.map((step) => {
            const isActive = currentStep === step.id;
            const isCompleted = progress >= step.range[1];
            const stepProgress = Math.max(0, Math.min(100, 
              ((progress - step.range[0]) / (step.range[1] - step.range[0])) * 100
            ));

            return (
              <div key={step.id} className="flex items-center gap-4">
                <div className={`p-2 rounded-full transition-all duration-300 ${
                  isCompleted 
                    ? 'bg-green-500/20 text-green-400' 
                    : isActive 
                      ? 'bg-neon-blue/20 text-neon-blue animate-pulse' 
                      : 'bg-dark-card text-muted-foreground'
                }`}>
                  {isCompleted ? (
                    <CheckCircle className="h-4 w-4" />
                  ) : (
                    <step.icon className="h-4 w-4" />
                  )}
                </div>
                
                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-sm font-medium ${
                      isActive ? 'text-neon-blue' : isCompleted ? 'text-green-400' : 'text-muted-foreground'
                    }`}>
                      {step.name}
                    </span>
                    {isActive && (
                      <Badge className="bg-neon-blue/20 text-neon-blue border-neon-blue/30 text-xs">
                        Active
                      </Badge>
                    )}
                    {isCompleted && (
                      <Badge className="bg-green-500/20 text-green-400 border-green-500/30 text-xs">
                        Complete
                      </Badge>
                    )}
                  </div>
                  
                  {isActive && (
                    <div className="w-full bg-dark-card rounded-full h-1.5">
                      <div 
                        className="bg-gradient-to-r from-neon-blue to-neon-cyan h-1.5 rounded-full transition-all duration-300"
                        style={{ width: `${stepProgress}%` }}
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* ETA */}
        <div className="text-center pt-4 border-t border-dark-card">
          <p className="text-sm text-muted-foreground">
            Estimated time remaining: <span className="text-neon-blue font-mono">
              {Math.max(0, Math.round((100 - progress) / 10))} minutes
            </span>
          </p>
        </div>
      </CardContent>
    </Card>
  );
};
