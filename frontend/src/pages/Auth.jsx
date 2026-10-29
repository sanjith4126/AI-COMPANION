import { useState, useEffect } from 'react'
import { Auth } from '@supabase/auth-ui-react'
import { ThemeSupa } from '@supabase/auth-ui-shared'
import { supabase } from '../lib/supabase'
import { useNavigate } from 'react-router-dom'

export default function AuthPage() {
  const navigate = useNavigate()

  useEffect(() => {
    supabase.auth.onAuthStateChange((event, session) => {
      if (session) {
        navigate('/companion')
      }
    })
  }, [navigate])

  return (
    <div className="min-h-screen flex items-center justify-center bg-companion-bg p-4 relative overflow-hidden">
      {/* Decorative background orbs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-companion-accent/20 rounded-full blur-3xl" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-companion-accentLight/20 rounded-full blur-3xl" />
      
      <div className="w-full max-w-md bg-companion-surface p-8 rounded-2xl shadow-2xl z-10 border border-white/5">
        <h1 className="text-3xl font-light text-center text-white mb-2">Welcome Back</h1>
        <p className="text-companion-textSubtle text-center mb-8">Sign in to continue to your companion.</p>
        
        <Auth
          supabaseClient={supabase}
          appearance={{
            theme: ThemeSupa,
            variables: {
              default: {
                colors: {
                  brand: '#7C3AED',
                  brandAccent: '#9333EA',
                  inputBackground: '#0B0F19',
                  inputText: 'white',
                  inputBorder: 'rgba(255,255,255,0.1)',
                }
              }
            },
            className: {
              container: 'text-white',
              label: 'text-companion-textSubtle',
              button: 'rounded-lg py-3 font-medium transition-all hover:scale-[1.02]',
              input: 'rounded-lg border-white/10 focus:border-companion-accent transition-colors'
            }
          }}
          providers={[]}
        />
      </div>
    </div>
  )
}
