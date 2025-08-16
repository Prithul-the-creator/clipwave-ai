import { useState } from 'react';
import { Dashboard } from '@/components/Dashboard';
import { Navbar } from '@/components/Navbar';
import { AuthModal } from '@/components/AuthModal';
import MagnetLines from '@/components/MagnetLines';
import { AnimatedBackground } from '@/components/AnimatedBackground';
import FeaturesSection from '@/components/FeaturesSection';
import HowItWorksSection from '@/components/HowItWorksSection';
import Footer from '@/components/Footer';
import { motion } from 'framer-motion';
import AnimatedDemo from '@/components/AnimatedDemo';

const Index = () => {
  const [user, setUser] = useState<{ email: string; name?: string } | null>(null);
  const [showAuthModal, setShowAuthModal] = useState(false);

  const handleLogin = (email: string) => {
    setUser({ email, name: email.split('@')[0] });
  };

  const handleLogout = () => {
    setUser(null);
  };

  return (
    <div className="relative min-h-screen">
      <AnimatedBackground />
      <Navbar
        user={user}
        onLogin={() => setShowAuthModal(true)}
        onLogout={handleLogout}
      />
      
      {user ? (
        <Dashboard user={user} />
      ) : (
        <>
          <motion.section
            id="about"
            className="relative min-h-screen flex flex-col items-center justify-start pt-32 px-6 overflow-hidden"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.7 }}
          >
            <MagnetLines
              className="absolute top-0 left-0 w-full h-full"
              rows={30}
              columns={30}
              containerSize="100%"
              lineColor="rgba(59, 130, 246, 0.3)"
              lineWidth="1px"
              lineHeight="3vmin"
            />
            <div className="relative z-10 w-full">
              {/* Main Content Grid */}
              <div className="grid lg:[grid-template-columns:auto_1fr] gap-2 items-center mb-16 lg:mb-0">
                {/* Left Column - Main Content */}
                <div className="space-y-8 z-10 max-w-md w-full">
                  {/* Badge */}
                  <div className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-neon-blue/20 to-neon-purple/20 border border-neon-blue/30 rounded-full text-sm font-medium text-neon-blue">
                    <div className="w-2 h-2 bg-neon-blue rounded-full animate-pulse"></div>
                    AI-Powered Video Intelligence
            </div>
            
                  {/* Main Heading */}
                  <h1 className="text-5xl lg:text-7xl font-bold leading-tight break-words">
                    <span className="bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent">
                      Transform
                    </span>
                    <br />
                    <span className="text-white">
                      Your Videos
                    </span>
                    <br />
                    <span className="bg-gradient-to-r from-neon-pink via-neon-purple to-neon-blue bg-clip-text text-transparent">
                      Into Magic
                    </span>
            </h1>
            
                  {/* Description */}
                  <p className="text-xl text-muted-foreground leading-relaxed max-w-lg">
                    Stop spending hours editing. Our AI instantly finds the most engaging moments in any YouTube video and creates shareable clips that go viral.
            </p>
            
                  {/* CTA Buttons */}
                  <div className="flex flex-col sm:flex-row gap-4">
              <button
                onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-neon-blue to-neon-purple hover:from-neon-purple hover:to-neon-pink text-white font-semibold py-4 px-8 rounded-xl text-lg transition-all duration-300 transform hover:scale-105 shadow-lg hover:shadow-neon-blue/25 animate-glow"
              >
                      Start Creating Free
              </button>
                    <a
                      href="#demo"
                      className="border border-neon-blue/30 text-neon-blue hover:bg-neon-blue/10 font-semibold py-4 px-8 rounded-xl text-lg transition-all duration-300 transform hover:scale-105"
                    >
                      Watch Demo
                    </a>
                  </div>
                  
                  {/* Stats */}
                  <div className="flex gap-8 pt-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-neon-blue">10K+</div>
                      <div className="text-sm text-muted-foreground">Clips Created</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-neon-purple">99%</div>
                      <div className="text-sm text-muted-foreground">Accuracy Rate</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-neon-pink">30s</div>
                      <div className="text-sm text-muted-foreground">Avg. Processing</div>
                    </div>
                </div>
                </div>
                {/* Right Column - Animated Demo, always contained and separated */}
                <div className="flex-1 flex items-start justify-stretch w-full h-full z-20 pt-8 lg:pt-0">
                  <AnimatedDemo boxHeight="min-h-[320px] md:min-h-[340px] lg:min-h-[360px]" onStartCreating={() => setShowAuthModal(true)} />
                </div>
              </div>
            </div>
          </motion.section>
          <motion.section
            id="features"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.7 }}
          >
            <FeaturesSection />
          </motion.section>
          <motion.section
            id="demo"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.7 }}
          >
            <HowItWorksSection />
          </motion.section>
          <motion.section
            id="pricing"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.7 }}
          >
            {/* <PricingSection /> removed */}
          </motion.section>
          <motion.section
            id="faq"
            initial={{ opacity: 0, y: 40 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.7 }}
          >
            {/* <FAQSection /> removed */}
          </motion.section>
          <Footer />
        </>
      )}

      <AuthModal 
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        onLogin={handleLogin}
      />
    </div>
  );
};

export default Index;
