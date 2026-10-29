import React, { useEffect, useState } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { supabase } from './lib/supabase';

import Landing from './pages/Landing';
import Auth from './pages/Auth';
import Companion from './pages/Companion';
import History from './pages/History';

export default function App() {
  const [session, setSession] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setSession(session);
      setLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setSession(session);
    });

    return () => subscription.unsubscribe();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-companion-bg flex items-center justify-center text-white">
        <div className="w-8 h-8 rounded-full border-t-2 border-companion-accent animate-spin" />
      </div>
    );
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/auth" element={!session ? <Auth /> : <Navigate to="/companion" />} />
        
        {/* Protected Routes */}
        <Route 
          path="/companion" 
          element={session ? <Companion /> : <Navigate to="/auth" />} 
        />
        <Route 
          path="/history" 
          element={session ? <History /> : <Navigate to="/auth" />} 
        />
        
        <Route path="*" element={<Navigate to="/" />} />
      </Routes>
    </BrowserRouter>
  );
}
