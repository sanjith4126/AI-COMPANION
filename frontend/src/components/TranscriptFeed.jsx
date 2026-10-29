import React, { useRef, useEffect } from 'react';
import EmotionIndicator from './EmotionIndicator';

export default function TranscriptFeed({ messages }) {
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-full text-companion-textSubtle text-center">
        <p>No messages yet.</p>
        <p className="text-sm mt-2">Start talking to begin your session.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col space-y-4 p-4 overflow-y-auto h-full pr-2">
      {messages.map((msg, idx) => {
        const isUser = msg.role === 'user';
        return (
          <div key={idx} className={`flex flex-col ${isUser ? 'items-end' : 'items-start'}`}>
            <div 
              className={`max-w-[80%] p-4 rounded-2xl ${
                isUser 
                  ? 'bg-companion-surface text-white rounded-tr-sm border border-white/5 shadow-sm' 
                  : 'bg-companion-accent/20 text-white rounded-tl-sm border border-companion-accent/30 shadow-md'
              }`}
            >
              <p className="text-[15px] leading-relaxed font-light">{msg.content}</p>
            </div>
            
            {/* Emotion Badge for User Messages */}
            {isUser && msg.emotion_label && (
              <div className="mt-2">
                <EmotionIndicator emotionLabel={msg.emotion_label} />
              </div>
            )}
          </div>
        );
      })}
      <div ref={bottomRef} />
    </div>
  );
}
