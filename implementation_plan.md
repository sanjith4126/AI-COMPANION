# AI Voice Mental Health Companion — Implementation Plan

## Overview
Build a production-ready AI voice mental health companion with:
- **React + Vite + Tailwind** frontend
- **Django + DRF** backend with full voice pipeline
- **Supabase** (PostgreSQL + pgvector) as database + auth
- **OpenAI Whisper** (STT), **GPT-4o** (LLM), **ElevenLabs** (TTS), **HuggingFace** (emotion detection)
- **Celery + Redis** for async memory extraction

## Project Structure
```
AI-COMPANION/
├── database/
│   └── schema.sql              # Supabase SQL migration
├── backend/                    # Django project
│   ├── mindcompanion/          # Django project config
│   ├── api/                    # Django app
│   ├── requirements.txt
│   └── .env.example
└── frontend/                   # Vite + React app
    └── .env.example
```

---

## AGENT 1 — Database Schema

### [NEW] database/schema.sql
- Enable `pgvector` extension
- Create tables: `users`, `sessions`, `messages`, `mood_logs`, `memory_nodes`
- `memory_nodes.embedding` → `vector(1536)`
- `ivfflat` index on embedding column (cosine ops, lists=100)
- RLS policies: each table only allows access where `user_id = auth.uid()`

---

## AGENT 2 — Django Backend

### [NEW] backend/mindcompanion/settings.py
- DB: `dj-database-url` parsing `SUPABASE_DB_URL`
- Installed apps: `api`, `corsheaders`, `rest_framework`
- Celery config pointing to Redis

### [NEW] backend/api/middleware.py
- `SupabaseJWTMiddleware` — verifies Supabase JWT tokens on every protected request

### [NEW] backend/api/views/auth_views.py
- `POST /api/auth/verify-token/` — verifies JWT, upserts user in Supabase

### [NEW] backend/api/views/session_views.py
- `POST /api/sessions/start/`
- `POST /api/sessions/end/` (triggers Celery task)

### [NEW] backend/api/views/voice_views.py
- `POST /api/voice/process/` — full pipeline:
  1. OpenAI Whisper → transcript
  2. HuggingFace `j-hartmann/emotion-english-distilroberta-base` → emotion
  3. pgvector memory retrieval (top 5)
  4. GPT-4o with system prompt template
  5. ElevenLabs TTS → audio
  6. Save messages to DB
  7. Return JSON response

### [NEW] backend/api/views/memory_views.py
- `POST /api/memory/extract/` (Celery async)
- `GET /api/memory/retrieve/`

### [NEW] backend/api/views/mood_views.py
- `POST /api/mood/log/`
- `GET /api/mood/history/`

### [NEW] backend/api/tasks.py
- Celery task: extract memories after session ends

### [NEW] backend/requirements.txt
Pinned versions for all dependencies

### [NEW] backend/.env.example
All environment variables documented

---

## AGENT 3 — React Frontend

### [NEW] frontend/ (Vite scaffold)
- React 18 + Vite + Tailwind CSS v3
- React Router v6
- Supabase JS v2
- Wavesurfer.js, Recharts

### Pages
- `/` — Landing page (dark blue/purple, minimal)
- `/auth` — Supabase Auth UI
- `/companion` — Main companion page (protected)
- `/history` — Mood history (protected)

### Components
- `VoiceOrb` — animated orb (IDLE/LISTENING/SPEAKING CSS states)
- `EmotionIndicator` — color-coded emotion pill badge
- `TranscriptFeed` — conversation bubbles with auto-scroll
- `AudioWaveform` — Wavesurfer.js waveform during AI speech
- `MoodTracker` — 1-10 slider + submit

### Voice Logic
- `MediaRecorder` API → webm audio blob
- POST blob to `/api/voice/process/`
- Play returned audio with Web Audio API

---

## AGENT 4 — Integration

### [NEW] INTEGRATION_CHECKLIST.md
- DB connectivity verification steps
- Endpoint test curl commands
- Frontend flow checklist
- Memory system verification steps

---

## Verification Plan

### Automated / Manual Checks

1. **Database**
   - Apply `database/schema.sql` to Supabase SQL editor
   - Verify all 5 tables exist and RLS is active

2. **Backend**
   ```bash
   cd backend
   pip install -r requirements.txt
   python manage.py migrate
   python manage.py runserver
   ```

3. **API Endpoint Tests** (curl commands in INTEGRATION_CHECKLIST.md)
   - Auth token verification
   - Session start/end
   - Voice processing (with sample audio file)
   - Mood log + history

4. **Frontend**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
   - Login/signup flow
   - Microphone permission + recording
   - Orb animation state changes
   - Audio playback
   - Mood chart rendering

5. **Memory System**
   - End a session → check `memory_nodes` table for new rows
   - Confirm embedding dimensions = 1536
