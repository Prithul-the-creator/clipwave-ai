import { motion } from 'framer-motion';

const plans = [
  {
    name: 'Free',
    price: '$0',
    features: [
      'Up to 3 clips per week',
      'AI-powered highlights',
      'HD exports',
      'Basic support'
    ],
    cta: 'Get Started',
    highlight: false
  },
  {
    name: 'Pro',
    price: '$15/mo',
    features: [
      'Unlimited clips',
      'Priority processing',
      '1080p+ exports',
      'Premium support'
    ],
    cta: 'Go Pro',
    highlight: true
  }
];

const PricingSection = () => (
  <motion.section
    id="pricing"
    className="py-24 bg-gradient-to-b from-dark-card/60 to-transparent"
    initial={{ opacity: 0, y: 40 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true, amount: 0.2 }}
    transition={{ duration: 0.7 }}
  >
    <div className="container mx-auto px-6">
      <h2 className="text-4xl font-bold text-center mb-4">Pricing</h2>
      <p className="text-lg text-center text-muted-foreground mb-12 max-w-2xl mx-auto">
        Start for free. Upgrade anytime for more power and flexibility.
      </p>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-3xl mx-auto">
        {plans.map((plan, i) => (
          <div key={i} className={`rounded-xl p-8 shadow-lg flex flex-col items-center text-center border-2 ${plan.highlight ? 'border-neon-purple bg-dark-card/80 scale-105' : 'border-dark-card/40 bg-dark-card/60'}`}>
            <h3 className="text-2xl font-bold mb-2">{plan.name}</h3>
            <div className="text-4xl font-extrabold mb-4">{plan.price}</div>
            <ul className="mb-6 space-y-2">
              {plan.features.map((f, j) => (
                <li key={j} className="text-muted-foreground">{f}</li>
              ))}
            </ul>
            <button className={`px-6 py-3 rounded-lg font-semibold transition-all ${plan.highlight ? 'bg-gradient-to-r from-neon-purple to-neon-pink text-white hover:from-neon-pink hover:to-neon-purple' : 'bg-dark-card/40 text-neon-blue border border-neon-blue hover:bg-neon-blue/10'}`}>
              {plan.cta}
            </button>
          </div>
        ))}
      </div>
    </div>
  </motion.section>
);

export default PricingSection; 