export const AnimatedBackground = () => {
  return (
    <div className="absolute inset-0 -z-10 h-full w-full bg-gradient-to-br from-indigo-950 via-black to-purple-950">
      <div className="absolute inset-0 h-full w-full bg-gradient-to-br from-indigo-950/50 via-black/50 to-purple-950/50 backdrop-blur-xl"></div>
      <div className="absolute top-20 left-10 w-72 h-72 bg-cyan-500/20 rounded-full blur-3xl animate-pulse"></div>
      <div className="absolute bottom-20 right-10 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000"></div>
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-500"></div>
    </div>
  );
}; 