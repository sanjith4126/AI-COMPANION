import React from 'react';

const EMOTION_COLORS = {
  joy: 'bg-yellow-500/20 text-yellow-400 border-yellow-500/50',
  sadness: 'bg-blue-500/20 text-blue-400 border-blue-500/50',
  anger: 'bg-red-500/20 text-red-400 border-red-500/50',
  fear: 'bg-purple-500/20 text-purple-400 border-purple-500/50',
  neutral: 'bg-gray-500/20 text-gray-400 border-gray-500/50',
  surprise: 'bg-orange-500/20 text-orange-400 border-orange-500/50'
};

export default function EmotionIndicator({ emotionLabel }) {
  if (!emotionLabel) return null;
  
  const colorClass = EMOTION_COLORS[emotionLabel] || EMOTION_COLORS.neutral;

  return (
    <div className={`inline-flex items-center px-3 py-1 rounded-full border text-xs font-semibold capitalize transition-colors duration-500 ${colorClass}`}>
      <div className="w-1.5 h-1.5 rounded-full bg-current mr-2 animate-pulse" />
      {emotionLabel}
    </div>
  );
}
