interface HeroSectionProps {
  user: { email: string; name?: string } | null;
}

const HeroSection = ({ user }: HeroSectionProps) => {
  return (
    <div className="relative text-center py-8 px-4">
      <div className="relative z-10 text-center px-6 max-w-4xl mx-auto">
        {/* Main Heading */}
        <h1 className="text-6xl md:text-8xl font-black mb-6 bg-gradient-to-r from-cyan-300 via-blue-400 to-purple-400 bg-clip-text text-transparent animate-fade-in">
          ClipWaveAI
        </h1>
        
        {/* Subtitle */}
        <p className="text-xl md:text-2xl text-gray-300 mb-8 animate-fade-in delay-200">
          Transform your YouTube videos into perfect clips with AI
        </p>

        {/* Welcome Message */}
        {user && (
          <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 backdrop-blur-sm border border-cyan-500/20 rounded-2xl p-4 mb-12 animate-fade-in delay-400">
            <p className="text-cyan-300 text-lg">
              Welcome back, <span className="font-semibold text-white">{user.name || user.email}</span>! You're viewing your personal job queue.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default HeroSection; 