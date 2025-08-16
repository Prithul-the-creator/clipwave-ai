import { FaLink, FaCommentDots, FaCheckCircle } from 'react-icons/fa';
import { motion } from 'framer-motion';

const steps = [
  {
    icon: <FaLink className="text-3xl text-neon-blue mb-2" />,
    title: 'Paste YouTube Link',
    desc: 'Just drop in any public YouTube video URL.'
  },
  {
    icon: <FaCommentDots className="text-3xl text-neon-purple mb-2" />,
    title: 'Describe Your Clip',
    desc: 'Tell us what you want—topic, moment, or vibe. Our AI gets it.'
  },
  {
    icon: <FaCheckCircle className="text-3xl text-neon-pink mb-2" />,
    title: 'Get Your Result',
    desc: 'Download, share, or edit your new clip in seconds.'
  }
];

const HowItWorksSection = () => (
  <motion.section
    id="demo"
    className="py-24 bg-gradient-to-b from-transparent to-dark-card/60"
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.2 }}
    transition={{ duration: 0.7 }}
  >
    <div className="container mx-auto px-6">
      <h2 className="text-4xl font-bold text-center mb-4">How It Works</h2>
      <p className="text-lg text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
        From YouTube link to viral clip in three simple steps.
      </p>
      <div className="flex flex-col md:flex-row justify-center items-center gap-12 mb-16">
        {steps.map((s, i) => (
          <div key={i} className="flex flex-col items-center text-center max-w-xs">
            <div className="w-12 h-12 flex items-center justify-center rounded-full bg-dark-card mb-4 border-2 border-neon-blue/30">
              <span className="text-2xl font-bold text-neon-blue mr-2">{i+1}</span>
              {s.icon}
            </div>
            <h3 className="text-lg font-semibold mb-2">{s.title}</h3>
            <p className="text-muted-foreground">{s.desc}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center">
        <div className="w-full max-w-2xl aspect-video bg-dark-card/60 rounded-xl flex items-center justify-center text-muted-foreground border border-dashed border-neon-purple">
          Workflow animation or screenshot coming soon!
        </div>
      </div>
    </div>
  </motion.section>
);

export default HowItWorksSection; 