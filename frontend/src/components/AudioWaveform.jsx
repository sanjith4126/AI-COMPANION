import React, { useEffect, useRef, forwardRef, useImperativeHandle } from 'react';
import WaveSurfer from 'wavesurfer.js';

const AudioWaveform = forwardRef(({ onFinish }, ref) => {
  const containerRef = useRef(null);
  const wavesurferRef = useRef(null);

  useEffect(() => {
    wavesurferRef.current = WaveSurfer.create({
      container: containerRef.current,
      waveColor: '#7C3AED',
      progressColor: '#9333EA',
      cursorColor: 'transparent',
      barWidth: 3,
      barGap: 2,
      barRadius: 2,
      height: 48,
      normalize: true,
      interact: false,
    });

    wavesurferRef.current.on('finish', () => {
      if (onFinish) onFinish();
    });

    return () => {
      if (wavesurferRef.current) {
        wavesurferRef.current.destroy();
      }
    };
  }, [onFinish]);

  useImperativeHandle(ref, () => ({
    loadAndPlay: (base64Audio) => {
      if (!wavesurferRef.current) return;
      
      try {
        // FIXED: Clear old listeners before starting new load
        wavesurferRef.current.un('ready');
        
        // Convert base64 to Blob URL
        const binary = atob(base64Audio);
        const array = new Uint8Array(binary.length);
        for (let i = 0; i < binary.length; i++) {
          array[i] = binary.charCodeAt(i);
        }
        const blob = new Blob([array], { type: 'audio/mpeg' });
        const url = URL.createObjectURL(blob);
        
        wavesurferRef.current.load(url);
        
        // FIXED: Use once() to avoid listener buildup and revoke URL to prevent leaks
        wavesurferRef.current.once('ready', () => {
          wavesurferRef.current.play();
          URL.revokeObjectURL(url); // FIXED: Prevent memory bloat
        });
      } catch (err) {
        console.error('Failed to play audio in wavesurfer', err);
      }
    },
    stop: () => {
      wavesurferRef.current?.stop();
    }
  }));

  return (
    <div className="w-full max-w-md mx-auto my-4 transition-opacity duration-300">
      <div ref={containerRef} />
    </div>
  );
});

export default AudioWaveform;
