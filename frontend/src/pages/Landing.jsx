import React from 'react';
import { Link } from 'react-router-dom';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-companion-bg flex flex-col items-center justify-center p-6 relative overflow-hidden">
      {/* Soft animated background elements */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-companion-accent/10 rounded-full blur-[100px]" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-indigo-500/10 rounded-full blur-[100px]" />

      <div className="z-10 flex flex-col items-center text-center max-w-2xl">
        <div className="w-24 h-24 mb-8 rounded-full bg-gradient-to-tr from-companion-accent to-companion-accentLight flex items-center justify-center shadow-[0_0_40px_rgba(124,58,237,0.4)]">
          {/* Simple logo representation */}
          <div className="w-12 h-12 bg-white/20 rounded-full mix-blend-overlay" />
        </div>

        <h1 className="text-4xl md:text-6xl font-light text-white tracking-tight mb-6">
          A companion that listens, remembers and cares.
        </h1>
        
        <p className="text-lg md:text-xl text-companion-textSubtle mb-12 font-light leading-relaxed">
          Talk to your AI mental health companion. <br className="hidden md:block" />
          Available 24/7. Completely private.
        </p>

        <Link
          to="/auth"
          className="group relative px-8 py-4 bg-companion-accent text-white rounded-full font-medium tracking-wide overflow-hidden transition-all hover:scale-105 hover:shadow-[0_0_30px_rgba(124,58,237,0.6)]"
        >
          <span className="relative z-10 transition-transform group-hover:scale-110">Start Talking</span>
          <div className="absolute inset-0 bg-gradient-to-r from-companion-accent to-companion-accentLight opacity-0 group-hover:opacity-100 transition-opacity" />
        </Link>
      </div>
      
      <footer className="absolute bottom-6 text-companion-textSubtle text-sm">
        Not a substitute for professional medical advice.
      </footer>
    </div>
  );
}
