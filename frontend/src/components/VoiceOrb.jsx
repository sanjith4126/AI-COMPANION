import React from 'react';

export default function VoiceOrb({ state, onClick }) {
  // state can be: 'idle', 'listening', 'speaking'
  
  let animationClass = 'animate-orb-idle';
  
  if (state === 'listening') {
    animationClass = 'animate-orb-listen';
  } else if (state === 'speaking') {
    animationClass = 'animate-orb-speak';
  } else if (state === 'processing') {
    animationClass = 'animate-pulse scale-90 opacity-60';
  }

  return (
    <div className="relative flex items-center justify-center w-64 h-64 lg:w-80 lg:h-80 mx-auto cursor-pointer" onClick={onClick}>
      {/* Outer spinning ring for processing */}
      {state === 'processing' && (
        <div className="absolute w-40 h-40 lg:w-56 lg:h-56 border-2 border-companion-accent/30 border-t-companion-accent rounded-full animate-spin" />
      )}

      <div className={`absolute w-32 h-32 lg:w-48 lg:h-48 bg-companion-accent rounded-full transition-all duration-300 ${animationClass}`} />
      
      {/* Glossy overlay */}
      <div className={`absolute w-32 h-32 lg:w-48 lg:h-48 bg-gradient-to-tr from-white/10 to-transparent rounded-full transition-transform ${animationClass}`} />
      
      {/* Instruction text */}
      <div className="absolute -bottom-12 text-companion-textSubtle text-sm font-medium tracking-wide">
        {state === 'idle' && 'Click to Start Talking'}
        {state === 'listening' && 'Listening... Click to Stop'}
        {state === 'speaking' && 'AI is Speaking...'}
        {state === 'processing' && 'Processing your voice...'}
      </div>
    </div>
  );
}
