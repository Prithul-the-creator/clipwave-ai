import { useEffect, useRef, useState } from 'react';
import { motion, useAnimation, AnimatePresence } from 'framer-motion';
import { FaLink, FaCommentDots, FaRobot, FaPlay } from 'react-icons/fa';
import { BsHandIndexThumbFill } from 'react-icons/bs';

interface AnimatedDemoProps {
  boxHeight?: string;
  onStartCreating?: () => void;
}

const FAKE_LINK = 'https://youtube.com/watch?v=DEMO12345';
const FAKE_PROMPT = 'Find the funniest moment';

export default function AnimatedDemo({ boxHeight, onStartCreating }: AnimatedDemoProps) {
  const minHeightClass = boxHeight || "min-h-[420px] md:min-h-[440px] lg:min-h-[480px]";
  const [typed, setTyped] = useState('');
  const [showArrow, setShowArrow] = useState(false);
  const [arrowClicked, setArrowClicked] = useState(false);
  const [step, setStep] = useState<'link' | 'prompt' | 'processing' | 'preview' | 'complete'>('link');
  const [typedPrompt, setTypedPrompt] = useState('');
  const [progress, setProgress] = useState(0);
  const [showCheck, setShowCheck] = useState(false);
  const inputRef = useRef<HTMLDivElement>(null);
  const controls = useAnimation();
  const [replayCount, setReplayCount] = useState(0);

  useEffect(() => {
    // Start arrow animation after a short delay
    const arrowTimeout = setTimeout(() => setShowArrow(true), 600);
    return () => clearTimeout(arrowTimeout);
  }, [replayCount]);

  useEffect(() => {
    if (showArrow && step === 'link') {
      // Animate arrow to input, then "click"
      controls.start({
        x: 0,
        y: 0,
        transition: { duration: 0.7, type: 'spring', bounce: 0.3 }
      }).then(() => {
        setTimeout(() => {
          setArrowClicked(true);
        }, 300);
      });
    }
  }, [showArrow, controls, step]);

  useEffect(() => {
    if (arrowClicked && step === 'link') {
      // Typing effect for link
      let i = 0;
      const type = () => {
        setTyped(FAKE_LINK.slice(0, i));
        if (i <= FAKE_LINK.length) {
          i++;
          setTimeout(type, 30);
        } else {
          // After typing, transition to prompt step
          setTimeout(() => {
            setStep('prompt');
          }, 500);
        }
      };
      setTimeout(type, 250);
    }
  }, [arrowClicked, step]);

  useEffect(() => {
    if (step === 'prompt') {
      // Typing effect for prompt
      let i = 0;
      const typePrompt = () => {
        setTypedPrompt(FAKE_PROMPT.slice(0, i));
        if (i <= FAKE_PROMPT.length) {
          i++;
          setTimeout(typePrompt, 30);
        } else {
          // After typing, transition to processing step
          setTimeout(() => {
            setStep('processing');
          }, 1000);
        }
      };
      setTimeout(typePrompt, 1100);
    }
  }, [step]);

  useEffect(() => {
    if (step === 'processing') {
      setProgress(0);
      setShowCheck(false);
      let p = 0;
      const animateProgress = () => {
        setProgress(p);
        if (p < 100) {
          p += 2;
          setTimeout(animateProgress, 16);
        }
      };
      setTimeout(animateProgress, 80);
    }
  }, [step]);

  // Animate transition to preview after check mark
  useEffect(() => {
    if (showCheck) {
      const toPreview = setTimeout(() => {
        setStep('preview');
      }, 1100);
      return () => clearTimeout(toPreview);
    }
  }, [showCheck]);

  // Animate transition to complete after preview
  useEffect(() => {
    if (step === 'preview') {
      const toComplete = setTimeout(() => {
        setStep('complete');
      }, 2400);
      return () => clearTimeout(toComplete);
    }
  }, [step]);

  // Reset all state for replay
  function handleReplay() {
    setTyped('');
    setShowArrow(false);
    setArrowClicked(false);
    setTypedPrompt('');
    setProgress(0);
    setShowCheck(false);
    setStep('link');
    setReplayCount((c) => c + 1);
  }

  return (
    <div className="w-full h-full flex flex-col items-center justify-center">
      <div className={`w-full h-full ${minHeightClass} mx-auto px-2 md:px-0 flex flex-col justify-center`}>
        <div className="relative h-full flex flex-col justify-start backdrop-blur-md bg-dark-card/80 border border-neon-blue/30 rounded-2xl shadow-lg py-8 px-2 md:px-8">
          {/* Heading */}
          <div className="w-full text-center mb-10">
            <h2 className="text-4xl md:text-5xl font-extrabold font-space tracking-tight bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink bg-clip-text text-transparent drop-shadow-lg">
              Here's how it works
            </h2>
          </div>
          {/* Animated Steps */}
          <div className="flex flex-col items-center justify-center flex-1 w-full relative min-h-[260px] h-full">
            <AnimatePresence mode="wait">
              {step === 'link' && (
                <motion.div
                  key="link"
                  initial={{ opacity: 0, y: -60 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: 60 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="flex flex-col items-center justify-center w-full h-full py-8"
                >
                  <FaLink className="text-8xl md:text-9xl text-neon-blue mb-10 bg-transparent" />
                  <div className="text-5xl md:text-6xl font-extrabold font-space tracking-tight text-white mb-10 drop-shadow-lg">Paste YouTube Link</div>
                  <div className="w-full max-w-4xl flex justify-center relative">
                    <div
                      ref={inputRef}
                      className="w-full max-w-2xl h-[110px] min-h-[110px] bg-dark-card/90 border-4 border-neon-blue/60 rounded-3xl px-16 py-12 flex items-center animate-glow shadow-2xl relative justify-start text-left overflow-hidden"
                    >
                      <span className="text-4xl md:text-5xl font-bold font-space tracking-tight text-muted-foreground truncate min-w-[18ch] max-w-full overflow-hidden">
                        {typed || ' '}
                      </span>
                    </div>
                    {/* Animated Arrow */}
                    {showArrow && (
                      <motion.div
                        initial={{ x: -120, y: -60, opacity: 0 }}
                        animate={controls}
                        style={{ position: 'absolute', left: '60px', top: '-60px', zIndex: 10 }}
                        transition={{ type: 'spring', bounce: 0.3 }}
                      >
                        <BsHandIndexThumbFill
                          className={`text-5xl md:text-6xl text-neon-blue drop-shadow-lg ${arrowClicked ? 'animate-bounce' : ''}`}
                          style={{ filter: arrowClicked ? 'brightness(1.5)' : undefined }}
                        />
                      </motion.div>
                    )}
                  </div>
                </motion.div>
              )}
              {step === 'prompt' && (
                <motion.div
                  key="prompt"
                  initial={{ opacity: 0, y: 60 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -60 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="flex flex-col items-center justify-center w-full h-full py-8"
                >
                  <FaCommentDots className="text-8xl md:text-9xl text-neon-purple mb-10 bg-transparent" />
                  <div className="text-5xl md:text-6xl font-extrabold font-space tracking-tight text-white mb-10 drop-shadow-lg">Describe Your Clip</div>
                  <div className="w-full max-w-4xl flex justify-center">
                    <div className="w-full max-w-2xl h-[110px] min-h-[110px] bg-dark-card/90 border-4 border-neon-purple/60 rounded-3xl px-16 py-12 flex items-center animate-glow shadow-2xl relative justify-start text-left overflow-hidden">
                      <span className="text-4xl md:text-5xl font-bold font-space tracking-tight text-muted-foreground truncate min-w-[18ch] max-w-full overflow-hidden">
                        {typedPrompt || ' '}
                      </span>
                    </div>
                  </div>
                </motion.div>
              )}
              {step === 'processing' && (
                <motion.div
                  key="processing"
                  initial={{ opacity: 0, y: 60 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -60 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="flex flex-col items-center justify-center w-full absolute left-0 top-0"
                >
                  <FaRobot className="text-6xl md:text-7xl text-neon-pink mb-6 bg-transparent" />
                  <div className="text-4xl md:text-5xl font-extrabold font-space tracking-tight text-white mb-6 drop-shadow-lg">AI Processing</div>
                  <div className="w-full max-w-2xl flex justify-center">
                    <div className="w-full max-w-xl bg-dark-card/90 border-2 border-neon-pink/40 rounded-2xl px-8 py-6 flex flex-col items-center animate-glow shadow-xl relative">
                      <div className="flex items-center gap-4 w-full mb-4">
                        <FaRobot className="text-3xl md:text-4xl text-neon-pink" />
                        <span className="text-2xl md:text-3xl font-bold font-space tracking-tight text-muted-foreground">Processing...</span>
                      </div>
                      <div className="w-full h-5 bg-neon-blue/20 rounded-full overflow-hidden mt-2">
                        <motion.div
                          className="h-5 bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink rounded-full"
                          initial={{ width: 0 }}
                          animate={{ width: `${progress}%` }}
                          transition={{ duration: 1.8, ease: 'linear' }}
                          onAnimationComplete={() => { if (progress === 100) setShowCheck(true); }}
                        />
                      </div>
                      {/* Animated Check Mark */}
                      <div className="flex justify-center items-center mt-8 min-h-[60px]">
                        <AnimatePresence>
                          {showCheck && (
                            <motion.svg
                              key="check"
                              width="60" height="60" viewBox="0 0 60 60"
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              exit={{ opacity: 0 }}
                              transition={{ duration: 0.2 }}
                            >
                              <motion.path
                                d="M15 32 L27 44 L45 18"
                                fill="none"
                                stroke="#00FF88"
                                strokeWidth="6"
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                initial={{ pathLength: 0 }}
                                animate={{ pathLength: 1 }}
                                transition={{ duration: 0.5, ease: 'easeInOut' }}
                              />
                            </motion.svg>
                          )}
                        </AnimatePresence>
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              {step === 'preview' && (
                <motion.div
                  key="preview"
                  initial={{ opacity: 0, y: 60 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -60 }}
                  transition={{ duration: 0.4, ease: 'easeOut' }}
                  className="flex flex-col items-center justify-center w-full h-full py-8"
                >
                  <FaPlay className="text-6xl md:text-7xl text-neon-green mb-8 bg-transparent" />
                  <div className="text-4xl md:text-5xl font-extrabold font-space tracking-tight text-white mb-8 drop-shadow-lg">Clip Preview</div>
                  <div className="w-full max-w-2xl flex justify-center">
                    <div className="w-full max-w-2xl bg-dark-card/90 border-4 border-neon-green/60 rounded-3xl px-10 py-8 flex flex-col items-center animate-glow shadow-2xl relative min-h-[90px] box-border">
                      <div className="flex items-center gap-6 w-full mb-6">
                        <FaPlay className="text-3xl md:text-4xl text-neon-green" />
                        <span className="text-3xl md:text-4xl font-bold font-space tracking-tight text-muted-foreground">Your Clip is Ready!</span>
                      </div>
                      <div className="w-full h-8 bg-neon-blue/20 rounded-full overflow-hidden mt-2 flex items-center">
                        <div className="h-8 w-full bg-gradient-to-r from-neon-blue via-neon-purple to-neon-pink rounded-full" />
                      </div>
                    </div>
                  </div>
                </motion.div>
              )}
              {step === 'complete' && (
                <motion.div
                  key="complete"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  transition={{ duration: 1.2, ease: 'easeInOut' }}
                  className="flex flex-col items-center justify-center w-full h-full absolute left-0 top-0 bg-transparent"
                >
                  <motion.svg
                    width="120" height="120" viewBox="0 0 60 60"
                    className="mb-10"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ duration: 0.6 }}
                  >
                    <motion.path
                      d="M15 32 L27 44 L45 18"
                      fill="none"
                      stroke="#00FF88"
                      strokeWidth="10"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      initial={{ pathLength: 0 }}
                      animate={{ pathLength: 1 }}
                      transition={{ duration: 0.7, ease: 'easeInOut' }}
                    />
                  </motion.svg>
                  <div className="text-6xl md:text-7xl font-extrabold font-space tracking-tight text-neon-green mb-10 drop-shadow-lg text-center">Done!</div>
                  <button
                    className="px-10 py-5 rounded-2xl bg-gradient-to-r from-neon-blue to-neon-purple text-white text-2xl font-semibold shadow-lg hover:scale-105 transition-all text-center block"
                    onClick={onStartCreating}
                  >
                    Start Creating Now
                  </button>
                </motion.div>
              )}
            </AnimatePresence>
          </div>
        </div>
      </div>
    </div>
  );
} 