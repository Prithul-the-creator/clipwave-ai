const Footer = () => (
  <footer className="py-8 text-center text-muted-foreground bg-dark-card/80 border-t border-dark-card/40">
    <div className="mb-2">&copy; {new Date().getFullYear()} ClipWaveAI. All rights reserved.</div>
    <div className="mb-2">
      <a href="https://github.com/prithulb/clipwave-ai-shorts" target="_blank" rel="noopener noreferrer" className="underline hover:text-neon-blue">GitHub</a>
    </div>
    <div className="text-sm">Turn any YouTube video into a viral short with AI ✂️</div>
  </footer>
);

export default Footer; 