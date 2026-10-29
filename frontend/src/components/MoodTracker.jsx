import React, { useState } from 'react';
import { api } from '../lib/api';

export default function MoodTracker({ onLog }) {
  const [score, setScore] = useState(5);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    try {
      // Derive a basic emotion label from the score just for the log
      let label = 'neutral';
      if (score >= 8) label = 'joy';
      else if (score <= 3) label = 'sadness';
      
      await api.logMood(score, label, 'Manual check-in');
      setSuccess(true);
      if (onLog) onLog();
      
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Failed to log mood', err);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="bg-companion-surface p-6 rounded-2xl border border-white/5 w-full">
      <h3 className="text-white font-medium mb-4 text-center">How are you feeling right now?</h3>
      
      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="flex items-center space-x-4">
          <span className="text-companion-textSubtle text-sm">Low</span>
          <input 
            type="range" 
            min="1" 
            max="10" 
            value={score}
            onChange={(e) => setScore(Number(e.target.value))}
            className="w-full h-2 bg-companion-bg rounded-lg appearance-none cursor-pointer accent-companion-accent" 
          />
          <span className="text-companion-textSubtle text-sm">Great</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-2xl font-light text-companion-accentLight">{score}/10</span>
          <button 
            type="submit"
            disabled={isSubmitting || success}
            className={`px-6 py-2 rounded-lg font-medium transition-all ${
              success 
                ? 'bg-green-500/20 text-green-400 border border-green-500/50'
                : 'bg-companion-accent hover:bg-companion-accentLight text-white disabled:opacity-50'
            }`}
          >
            {success ? 'Logged!' : 'Log Mood'}
          </button>
        </div>
      </form>
    </div>
  );
}
