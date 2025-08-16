import { FaMagic, FaBolt, FaHighlighter, FaShareAlt } from 'react-icons/fa';
import { motion } from 'framer-motion';

const features = [
  {
    icon: <FaMagic className="text-3xl text-neon-blue mb-2" />,
    title: 'AI-Powered Clipping',
    desc: 'Let advanced AI find the best moments in your YouTube videos—no manual scrubbing needed.'
  },
  {
    icon: <FaBolt className="text-3xl text-neon-purple mb-2" />,
    title: 'Instant Processing',
    desc: 'Get your clips in seconds, not hours. Our cloud pipeline is built for speed.'
  },
  {
    icon: <FaHighlighter className="text-3xl text-neon-pink mb-2" />,
    title: 'HD Quality Export',
    desc: 'Download or share your clips in crisp HD, ready for any platform.'
  },
  {
    icon: <FaShareAlt className="text-3xl text-neon-green mb-2" />,
    title: 'Easy Sharing',
    desc: 'Share your clips directly to social media or with a simple link.'
  }
];

const FeaturesSection = () => (
  <motion.section
    id="features"
    className="py-24 bg-gradient-to-b from-dark-card/60 to-transparent"
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.2 }}
    transition={{ duration: 0.7 }}
  >
    <div className="container mx-auto px-6">
      <h2 className="text-4xl font-bold text-center mb-4">Features</h2>
      <p className="text-lg text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
        Everything you need to turn long videos into shareable, viral moments—powered by AI.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8 mb-16">
        {features.map((f, i) => (
          <div key={i} className="bg-dark-card rounded-xl p-8 shadow-lg flex flex-col items-center text-center">
            {f.icon}
            <h3 className="text-xl font-semibold mb-2">{f.title}</h3>
            <p className="text-muted-foreground">{f.desc}</p>
          </div>
        ))}
      </div>
      <div className="flex justify-center">
        <div className="w-full max-w-xl aspect-video bg-dark-card/60 rounded-xl flex items-center justify-center text-muted-foreground border border-dashed border-neon-blue">
          Demo video or GIF coming soon!
        </div>
      </div>
    </div>
  </motion.section>
);

export default FeaturesSection; 