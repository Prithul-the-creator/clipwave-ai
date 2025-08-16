import { motion } from 'framer-motion';
import { useState } from 'react';

const faqs = [
  {
    q: 'Is ClipWaveAI free to use?',
    a: 'Yes! You can create up to 3 clips per week for free. Upgrade to Pro for unlimited access.'
  },
  {
    q: 'What kind of videos can I clip?',
    a: 'Any public YouTube video. Just paste the link and let our AI do the rest.'
  },
  {
    q: 'How long does it take to process a video?',
    a: 'Most clips are ready in under a minute, thanks to our optimized cloud pipeline.'
  },
  {
    q: 'Can I share my clips on social media?',
    a: 'Absolutely! Download your clips or share them directly with a link.'
  },
  {
    q: 'Is my data private and secure?',
    a: 'We take privacy seriously. Your videos and clips are processed securely and never shared without your permission.'
  }
];

const FAQSection = () => {
  const [open, setOpen] = useState<number | null>(null);
  return (
    <motion.section
      id="faq"
      className="py-24 bg-gradient-to-b from-transparent to-dark-card/60"
      initial={{ opacity: 0, y: 40 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, amount: 0.2 }}
      transition={{ duration: 0.7 }}
    >
      <div className="container mx-auto px-6 max-w-3xl">
        <h2 className="text-4xl font-bold text-center mb-4">FAQ</h2>
        <p className="text-lg text-center text-muted-foreground mb-12">
          Got questions? We've got answers.
        </p>
        <div className="space-y-4">
          {faqs.map((faq, i) => (
            <div key={i} className="border border-neon-blue/20 rounded-lg bg-dark-card/60">
              <button
                className="w-full text-left px-6 py-4 font-semibold text-neon-blue focus:outline-none flex justify-between items-center"
                onClick={() => setOpen(open === i ? null : i)}
              >
                {faq.q}
                <span className="ml-2 text-neon-purple">{open === i ? '-' : '+'}</span>
              </button>
              {open === i && (
                <div className="px-6 pb-4 text-muted-foreground animate-fade-in">
                  {faq.a}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    </motion.section>
  );
};

export default FAQSection; 