import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { supabase } from '../lib/supabase';
import { api } from '../lib/api';
import VoiceOrb from '../components/VoiceOrb';
import TranscriptFeed from '../components/TranscriptFeed';
import AudioWaveform from '../components/AudioWaveform';
import MoodTracker from '../components/MoodTracker';

export default function Companion() {
  const navigate = useNavigate();
  const [session, setSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [orbState, setOrbState] = useState('idle'); // idle, listening, speaking, processing
  const [error, setError] = useState(null);
  
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  const waveformRef = useRef(null);
  
  // Start Session on Mount
  useEffect(() => {
    let activeSession = null;
    let mounted = true;
    
    const initSession = async () => {
      try {
        const { data: { session: authSession } } = await supabase.auth.getSession();
        if (!authSession) {
          navigate('/auth');
          return;
        }
        const res = await api.startSession();
        console.log("SESSION RESPONSE:", res);  // 👈 ADD THIS
       if (mounted && res.session) {
        setSession(res.session);     // ✅ FIX
        activeSession = res.session; // ✅ FIX
      }
      } catch (err) {
        console.error('Failed to start session', err);
        setError('Could not connect to the therapy session. Please refresh.');
      }
    };
    
    initSession();
    
    return () => {
      mounted = false;
      if (activeSession) {
        // End session on unmount
        api.endSession(activeSession.id).catch(err => console.error('End session error', err));
      }
    };
  }, [navigate]);
  
  // ... rest of component updates ...

  const audioPlayerRef = useRef(null); // Native Audio element for reliable playback

  const playAuraResponse = (base64Audio, fallbackText) => {
    // Try ElevenLabs audio first
    if (base64Audio) {
      try {
        const binary = atob(base64Audio);
        const bytes = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
        const blob = new Blob([bytes], { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);

        const audio = new Audio(url);
        audioPlayerRef.current = audio;

        audio.onplay = () => setOrbState('speaking');
        audio.onended = () => {
          setOrbState('idle');
          URL.revokeObjectURL(url);
        };
        audio.onerror = () => {
          console.warn('ElevenLabs audio failed, using browser TTS fallback');
          URL.revokeObjectURL(url);
          speakWithBrowser(fallbackText);
        };

        audio.play().catch(() => speakWithBrowser(fallbackText));
        return;
      } catch (e) {
        console.warn('Audio decode error, using browser TTS fallback:', e);
      }
    }

    // Fallback: Browser built-in Text-to-Speech
    speakWithBrowser(fallbackText);
  };

  const speakWithBrowser = (text) => {
    if (!text || !window.speechSynthesis) {
      setOrbState('idle');
      return;
    }
    window.speechSynthesis.cancel();

    const speak = () => {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = 0.92;    // Slightly slower = more natural
      utterance.pitch = 1.1;   // Slightly warmer/higher
      utterance.volume = 1.0;

      // Pick the best available voice — prefer natural female voices
      const voices = window.speechSynthesis.getVoices();
      const preferred = voices.find(v =>
        v.name.includes('Samantha') ||       // macOS natural
        v.name.includes('Google UK English Female') ||
        v.name.includes('Microsoft Aria') ||
        v.name.includes('Microsoft Jenny') ||
        v.name.includes('Google US English')
      ) || voices.find(v => v.lang.startsWith('en') && v.name.toLowerCase().includes('female'))
        || voices.find(v => v.lang.startsWith('en'));

      if (preferred) utterance.voice = preferred;

      setOrbState('speaking');
      utterance.onend = () => setOrbState('idle');
      utterance.onerror = () => setOrbState('idle');
      window.speechSynthesis.speak(utterance);
    };

    // Voices may not be loaded yet — wait if needed
    if (window.speechSynthesis.getVoices().length > 0) {
      speak();
    } else {
      window.speechSynthesis.onvoiceschanged = () => speak();
    }
  };

  const processVoiceInput = async (audioBlob) => {
    if (!session) return;
    
    try {
      setOrbState('processing');
      
      const response = await api.processVoice(audioBlob, session.id);
      
      // Add both messages to UI
      setMessages(prev => [
        ...prev, 
        { role: 'user', content: response.transcript, emotion_label: response.emotion },
        { role: 'assistant', content: response.ai_response_text }
      ]);
      
      // PLAY AUDIO - always speaks, never silent
      playAuraResponse(response.audio_base64, response.ai_response_text);
      
    } catch (err) {
      console.error('Voice process error:', err);
      setError('The AI had trouble processing that. Try again.');
      setOrbState('idle');
    }
  };

  const handleOrbClick = async () => {
    if (orbState === 'speaking') {
      // Stop speaking immediately
      if (audioPlayerRef.current) {
        audioPlayerRef.current.pause();
        audioPlayerRef.current = null;
      }
      window.speechSynthesis?.cancel();
      setOrbState('idle');
      return;
    }

    if (orbState === 'processing') return;
    
    if (orbState === 'listening') {
      mediaRecorderRef.current?.stop();
      return;
    }
    
    // Start listening
    try {
      setError(null);
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) audioChunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = async () => {
        stream.getTracks().forEach(track => track.stop());
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceInput(audioBlob);
      };
      
      mediaRecorder.start();
      setOrbState('listening');
      
    } catch (err) {
      console.error('Mic error:', err);
      setError('Microphone access denied or unavailable.');
      setOrbState('idle');
    }
  };

  const handleAudioFinish = () => {
    setOrbState('idle');
  };

  const handleLogout = async () => {
    await supabase.auth.signOut();
    navigate('/auth');
  };

  if (!session) {
    return (
      <div className="min-h-screen bg-companion-bg flex items-center justify-center text-white">
        <div className="animate-pulse flex flex-col items-center">
          <div className="w-8 h-8 rounded-full border-t-2 border-companion-accent animate-spin mb-4" />
          <p>Connecting to your companion...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-companion-bg text-white flex flex-col h-screen overflow-hidden relative">
      <header className="flex justify-between items-center p-6 border-b border-white/5 bg-companion-surface/50 backdrop-blur-md z-10">
        <div>
          <h1 className="text-xl font-medium tracking-wide">MindCompanion</h1>
          <p className="text-xs text-companion-textSubtle">Secure, private space</p>
        </div>
        <div className="flex gap-4">
          <button onClick={() => navigate('/history')} className="text-sm text-companion-textSubtle hover:text-white transition-colors">Mood History</button>
          <button onClick={handleLogout} className="text-sm text-companion-accentLight hover:text-companion-accent transition-colors">End Session</button>
        </div>
      </header>

      {error && (
        <div className="absolute top-20 left-1/2 -translate-x-1/2 bg-red-500/20 text-red-200 px-4 py-2 rounded-lg border border-red-500/30 z-50 text-sm">
          {error}
        </div>
      )}

      <main className="flex-1 flex flex-col lg:flex-row overflow-hidden pb-6">
        {/* Left Side: Orb & Audio */}
        <div className="flex-1 flex flex-col justify-center items-center p-8 relative">
          <VoiceOrb state={orbState} onClick={handleOrbClick} />
          
          <div className={`mt-16 w-full max-w-sm transition-opacity duration-500 ${orbState === 'speaking' ? 'opacity-100' : 'opacity-0 pointer-events-none'}`}>
            <AudioWaveform ref={waveformRef} onFinish={handleAudioFinish} />
          </div>
        </div>
        
        {/* Right Side: Transcript & Mood */}
        <div className="flex-1 lg:max-w-md w-full flex flex-col h-full bg-companion-bg/50 border-l border-white/5">
          <div className="flex-1 overflow-hidden">
            <TranscriptFeed messages={messages} />
          </div>
          <div className="p-4 border-t border-white/5 bg-companion-bg">
            <MoodTracker />
          </div>
        </div>
      </main>
    </div>
  );
}
