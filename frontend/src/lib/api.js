import axios from 'axios'
import { supabase } from './supabase'

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Helper to get auth header + user id
const getAuthHeaders = async () => {
  const { data: { session } } = await supabase.auth.getSession()

  if (!session?.access_token) throw new Error('Not authenticated')

  return {
    Authorization: `Bearer ${session.access_token}`,  // future use
    "x-user-id": session.user.id                      // 🔥 IMPORTANT FIX
  }
}

export const api = {
  // --- Sessions ---
  startSession: async () => {
    const headers = await getAuthHeaders()

    const res = await axios.post(
      `${API_BASE}/sessions/start/`,
      {},
      { headers }
    )

    console.log("START SESSION RESPONSE:", res.data) // 🔍 debug
    return res.data
  },

  endSession: async (sessionId) => {
    const headers = await getAuthHeaders()

    const res = await axios.post(
      `${API_BASE}/sessions/end/`,
      { session_id: sessionId },
      { headers }
    )

    return res.data
  },

  // --- Voice ---
  processVoice: async (audioBlob, sessionId) => {
    const headers = await getAuthHeaders()

    const formData = new FormData()
    formData.append('audio', audioBlob, 'user_audio.webm')
    formData.append('session_id', sessionId)

    const res = await axios.post(
      `${API_BASE}/voice/process/`,
      formData,
      {
        headers: {
          ...headers,
          'Content-Type': 'multipart/form-data'
        }
      }
    )

    return res.data
  },

  // --- Mood ---
  logMood: async (moodScore, emotionLabel, note = '') => {
    const headers = await getAuthHeaders()

    const res = await axios.post(
      `${API_BASE}/mood/log/`,
      {
        mood_score: moodScore,
        emotion_label: emotionLabel,
        note
      },
      { headers }
    )

    return res.data
  },

  getMoodHistory: async () => {
    const headers = await getAuthHeaders()

    const res = await axios.get(
      `${API_BASE}/mood/history/`,
      { headers }
    )

    return res.data
  }
}