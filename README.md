# MindCompanion 🎙️

An AI voice companion for mental health support. Speak naturally and it transcribes you,
detects your emotion, remembers past conversations and replies in a natural voice.

**Pipeline:** Mic → Gemini (speech-to-text) → HuggingFace emotion model → pgvector memory recall → Gemini (reply) → ElevenLabs (voice)

**Stack:** React + Vite + Tailwind · Django REST · Supabase (Postgres + pgvector + Auth) · Celery + Redis

**Features:** animated voice orb · live transcript with emotion badges · 1–10 mood tracking with history charts · memory saved at the end of each session

## Run locally

1. Run `database/schema.sql` in the Supabase SQL editor.
2. Copy `backend/.env.example` → `backend/.env` and `frontend/.env.example` → `frontend/.env`, fill in your keys.
3. On Windows, run `start.bat`. Or manually:

```bash
cd backend && python -m venv venv && venv\Scripts\activate && pip install -r requirements.txt && python manage.py runserver
cd frontend && npm install && npm run dev
```

Frontend: http://localhost:5173 · Backend: http://localhost:8000

See [INTEGRATION_CHECKLIST.md](INTEGRATION_CHECKLIST.md) for the full test walkthrough.
