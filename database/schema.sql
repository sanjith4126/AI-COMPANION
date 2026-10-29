-- ============================================================
-- AI Voice Mental Health Companion — Supabase Database Schema
-- Run this entire file in the Supabase SQL Editor
-- ============================================================

-- ────────────────────────────────────────────────────────────
-- STEP 1: Enable required extensions
-- ────────────────────────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- ────────────────────────────────────────────────────────────
-- STEP 2: TABLE — users
-- Stores user profiles. Linked to Supabase Auth via id.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.users (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email               TEXT UNIQUE NOT NULL,
    full_name           TEXT,
    created_at          TIMESTAMPTZ DEFAULT now(),
    onboarding_complete BOOLEAN DEFAULT false,
    preferences         JSONB DEFAULT '{}'::jsonb
);

-- ────────────────────────────────────────────────────────────
-- STEP 3: TABLE — sessions
-- Each therapy/companion session per user.
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.sessions (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    started_at        TIMESTAMPTZ DEFAULT now(),
    ended_at          TIMESTAMPTZ,
    session_summary   TEXT,
    dominant_emotion  TEXT
);

-- ────────────────────────────────────────────────────────────
-- STEP 4: TABLE — messages
-- Individual messages within a session (user + AI turns).
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.messages (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id      UUID NOT NULL REFERENCES public.sessions(id) ON DELETE CASCADE,
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    role            TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content         TEXT NOT NULL,
    emotion_label   TEXT,
    emotion_score   FLOAT,
    timestamp       TIMESTAMPTZ DEFAULT now()
);

-- ────────────────────────────────────────────────────────────
-- STEP 5: TABLE — mood_logs
-- Manual mood check-ins by the user (score 1–10).
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.mood_logs (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    mood_score      INTEGER NOT NULL CHECK (mood_score BETWEEN 1 AND 10),
    emotion_label   TEXT NOT NULL,
    note            TEXT,
    logged_at       TIMESTAMPTZ DEFAULT now()
);

-- ────────────────────────────────────────────────────────────
-- STEP 6: TABLE — memory_nodes
-- Long-term semantic memories extracted from sessions.
-- Uses pgvector for similarity search (1536-dim OpenAI embeddings).
-- ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS public.memory_nodes (
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id           UUID NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    content           TEXT NOT NULL,
    embedding         vector(1536),
    created_at        TIMESTAMPTZ DEFAULT now(),
    source_session_id UUID REFERENCES public.sessions(id) ON DELETE SET NULL
);

-- ────────────────────────────────────────────────────────────
-- STEP 7: Vector Similarity Index
-- ivfflat index for fast approximate cosine-similarity search.
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS memory_nodes_embedding_idx
    ON public.memory_nodes
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ────────────────────────────────────────────────────────────
-- STEP 8: Performance indexes (standard B-tree)
-- ────────────────────────────────────────────────────────────
CREATE INDEX IF NOT EXISTS idx_sessions_user_id     ON public.sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_session_id  ON public.messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_user_id     ON public.messages(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_logs_user_id    ON public.mood_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_mood_logs_logged_at  ON public.mood_logs(logged_at DESC);
CREATE INDEX IF NOT EXISTS idx_memory_nodes_user_id ON public.memory_nodes(user_id);

-- ────────────────────────────────────────────────────────────
-- STEP 9: Row Level Security (RLS)
-- Users can ONLY read and write their OWN data.
-- auth.uid() is the Supabase Auth user UUID.
-- ────────────────────────────────────────────────────────────

-- Enable RLS on all tables
ALTER TABLE public.users        ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.sessions     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.messages     ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.mood_logs    ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.memory_nodes ENABLE ROW LEVEL SECURITY;

-- ── users ──────────────────────────────────────────────────
CREATE POLICY "users: select own row" ON public.users
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "users: insert own row" ON public.users
    FOR INSERT WITH CHECK (auth.uid() = id);

CREATE POLICY "users: update own row" ON public.users
    FOR UPDATE USING (auth.uid() = id);

-- ── sessions ───────────────────────────────────────────────
CREATE POLICY "sessions: select own" ON public.sessions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "sessions: insert own" ON public.sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "sessions: update own" ON public.sessions
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "sessions: delete own" ON public.sessions
    FOR DELETE USING (auth.uid() = user_id);

-- ── messages ───────────────────────────────────────────────
CREATE POLICY "messages: select own" ON public.messages
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "messages: insert own" ON public.messages
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "messages: delete own" ON public.messages
    FOR DELETE USING (auth.uid() = user_id);

-- ── mood_logs ──────────────────────────────────────────────
CREATE POLICY "mood_logs: select own" ON public.mood_logs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "mood_logs: insert own" ON public.mood_logs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "mood_logs: delete own" ON public.mood_logs
    FOR DELETE USING (auth.uid() = user_id);

-- ── memory_nodes ───────────────────────────────────────────
CREATE POLICY "memory_nodes: select own" ON public.memory_nodes
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "memory_nodes: insert own" ON public.memory_nodes
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "memory_nodes: delete own" ON public.memory_nodes
    FOR DELETE USING (auth.uid() = user_id);

-- ────────────────────────────────────────────────────────────
-- STEP 10: Helper function for pgvector similarity search
-- Called from Django via raw SQL or supabase-py rpc
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.match_memories(
    query_embedding vector(1536),
    match_user_id   UUID,
    match_count     INT DEFAULT 5
)
RETURNS TABLE (
    id         UUID,
    content    TEXT,
    similarity FLOAT
)
LANGUAGE SQL STABLE
AS $$
    SELECT
        mn.id,
        mn.content,
        1 - (mn.embedding <=> query_embedding) AS similarity
    FROM public.memory_nodes mn
    WHERE mn.user_id = match_user_id
    ORDER BY mn.embedding <=> query_embedding
    LIMIT match_count;
$$;

-- ────────────────────────────────────────────────────────────
-- STEP 12: Trigger for automatic user profile creation
-- Syncs auth.users (Supabase Auth) to public.users
-- ────────────────────────────────────────────────────────────
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO public.users (id, email, full_name)
  VALUES (
    NEW.id,
    NEW.email,
    COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', '')
  )
  ON CONFLICT (id) DO NOTHING;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Drop trigger if it exists (for item-level updates)
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- ────────────────────────────────────────────────────────────
-- DATABASE SCHEMA COMPLETE — API CONTRACT READY
-- ────────────────────────────────────────────────────────────
