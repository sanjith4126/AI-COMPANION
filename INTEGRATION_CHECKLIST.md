# Integration & Testing Checklist

Follow this guide to spin up the entire application stack and verify integration.

## 1. Supabase Database Status
- [ ] Created Supabase project
- [ ] Copied `SUPABASE_DB_URL`, `SUPABASE_URL`, `SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY`, `SUPABASE_JWT_SECRET`
- [ ] Ran `database/schema.sql` in Supabase SQL editor
- [ ] Verified tables created: `users`, `sessions`, `messages`, `mood_logs`, `memory_nodes`
- [ ] Verified `pgvector` extension and RLS policies are active

## 2. API Keys
- [ ] Set `OPENAI_API_KEY`
- [ ] Set `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID`
- [ ] Set `HUGGINGFACE_API_KEY`

## 3. Backend (Django)
```bash
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
```

**Run Backend Server:**
```bash
python manage.py runserver
```

**Run Celery Worker (In a separate terminal, requires Redis):**
```bash
celery -A mindcompanion worker -l info
```

### Backend Endpoint Quick Tests
Using curl or Postman:
1. **Mood History (Requires Auth Token):**
   ```bash
   curl -X GET http://localhost:8000/api/mood/history/ \
   -H "Authorization: Bearer <SUPABASE_JWT>"
   ```
2. **Start Session:**
   ```bash
   curl -X POST http://localhost:8000/api/sessions/start/ \
   -H "Authorization: Bearer <SUPABASE_JWT>"
   ```

## 4. Frontend (React/Vite)
```bash
cd frontend
npm install
```

**Run Frontend Development Server:**
```bash
npm run dev
```

### Frontend Verification Steps
- [ ] Navigate to `http://localhost:5173`
- [ ] Click "Start Talking" -> should redirect to `/auth`
- [ ] Sign up / Log in using Supabase Auth UI
- [ ] Redirection to `/companion` succeeds
- [ ] Orb appears and pulses (Idle state)
- [ ] Grant Microphone permissions
- [ ] Click Orb -> State changes to 'Listening', speak clearly into the mic
- [ ] Click Orb again -> State changes back to 'Idle' (processing)
- [ ] Backend processes voice, returns audio, orb changes to 'Speaking'
- [ ] Waveform animates while AI voice plays
- [ ] Transcript feed updates with accurate text and emotion badge
- [ ] Move slider to log mood -> Submit works
- [ ] Go to "Mood History" -> Chart displays correctly
- [ ] End Session -> Verification that memory extraction celery task fires

## 5. Memory System Verification
- [ ] In Supabase SQL editor, check the `memory_nodes` table after ending a session.
- [ ] Verify `content` text is populated.
- [ ] Verify `embedding` column contains 1536-dimensional float arrays.

---
*If all above steps succeed, your AI Voice Mental Health Companion is production-ready.*
