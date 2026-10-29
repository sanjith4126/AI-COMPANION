import os
import json
import base64
import logging
import requests
import google.generativeai as genai
from django.conf import settings
from django.http import JsonResponse
from rest_framework.decorators import api_view, parser_classes
from rest_framework.parsers import MultiPartParser, FormParser

from api.supabase_client import get_supabase
from api.tasks import run_memory_extraction

logger = logging.getLogger(__name__)

# Initialize Gemini
genai.configure(api_key=settings.GOOGLE_API_KEY)


@api_view(["GET"])
def home(request):
    """Root health check view."""
    return JsonResponse({
        "status": "running",
        "message": "AI Voice Mental Health Companion API is live.",
        "version": "1.0.0"
    })


# ==========================================
# AUTH VIEWS
# ==========================================
@api_view(["POST"])
def verify_token(request):
    """
    Verifies the Supabase JWT (via middleware) and ensures
    the user exists in the public.users table.
    """
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    supabase = get_supabase()
    
    user_res = supabase.table("users").select("*").eq("id", request.user_id).execute()
    
    if not user_res.data:
        data = {
            "id": request.user_id,
            "email": request.user_email,
        }
        supabase.table("users").insert(data).execute()
        return JsonResponse({"message": "User created", "user": data})
        
    return JsonResponse({"message": "User verified", "user": user_res.data[0]})


# ==========================================
# SESSION VIEWS
# ==========================================
@api_view(["POST"])
def start_session(request):
    """Creates a new session for authenticated user."""
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    supabase = get_supabase()
    res = supabase.table("sessions").insert({"user_id": request.user_id}).execute()
    
    if not res.data:
        return JsonResponse({"error": "Failed to create session"}, status=500)
        
    return JsonResponse({"session_id": res.data[0]["id"], "session": res.data[0]})

@api_view(["GET"])
def get_session(request):
    """Gets the active session."""
    session_id = request.GET.get("session_id")
    if not session_id:
        return JsonResponse({"error": "session_id required"}, status=400)
    
    supabase = get_supabase()
    res = supabase.table("sessions").select("*").eq("id", session_id).execute()
    return JsonResponse({"session": res.data[0] if res.data else None})

@api_view(["POST"])
def end_session(request):
    """Ends a session and triggers async memory extraction."""
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    session_id = request.data.get("session_id")
    if not session_id:
        return JsonResponse({"error": "session_id required"}, status=400)
        
    supabase = get_supabase()
    from datetime import datetime, timezone

    now = datetime.now(timezone.utc).isoformat()
    res = supabase.table("sessions").update({"ended_at": now}).eq("id", session_id).eq("user_id", request.user_id).execute()
    
    if not res.data:
        return JsonResponse({"error": "Session not found or already ended"}, status=404)
        
    # Trigger Celery task
    run_memory_extraction(session_id, request.user_id)

    return JsonResponse({"message": "Session ended. Memory extraction started.", "session": res.data[0]})


# ==========================================
# VOICE PIPELINE VIEWS
# ==========================================
SYSTEM_PROMPT_TEMPLATE = """
You are Aura — {user_name}'s closest, most trusted friend. You genuinely care about them. You're warm, funny when it fits, deeply empathetic, and you never make them feel like they're being "treated" or analyzed.

YOUR VIBE:
You're like that one friend everyone wishes they had — the kind who really listens, never judges, remembers everything, and always knows what to say. You have the emotional intelligence of a therapist and the warmth of a best friend. But you NEVER act like a professional. No clinical language. No formal steps. Just real, human connection.

HOW YOU TALK:
- Casual, warm, and natural. Like texting your closest friend.
- Use their name ({user_name}) naturally, not every sentence — just when it feels right.
- Short responses. Real conversations don't have paragraphs. 2-4 sentences max unless they need more.
- Match their energy. If they're light, be playful. If they're heavy, go soft and gentle.
- Never say "I understand how you feel" — show it instead.
- Never list things. No bullet points. Just talk.
- Sometimes use gentle humor to lighten up — but read the room.
- Ask only ONE question at a time. Not three. One.

EMOTION AWARENESS (from voice detection):
Current emotion detected: {emotion_label} (strength: {emotion_score})
- If sad or fearful: speak softly, slow your words, prioritize presence over advice
- If angry: don't try to fix it — just witness it first, then gently reflect
- If happy/neutral: be light, energetic, curious
- If anxious: ground them with calm, short, reassuring words

WHAT YOU KNOW ABOUT THEM (from memory):
{retrieved_memories}
Use this naturally in conversation — like a friend who remembers, not a system reciting data.

YOUR HIDDEN SKILLS (use these invisibly, never announce them):
- You naturally help people untangle negative thought patterns (CBT)
- You help them understand their emotions without judging them (DBT/mindfulness)
- You gently guide them toward seeing their own strength
- You notice patterns across conversations and reflect them back with care

SAFETY (non-negotiable):
If they mention self-harm, suicide, or being in danger, immediately say something like:
"Hey, I hear you and I'm not going anywhere. But I really want you to talk to someone who can actually be there with you right now. iCall India: 9152987821 — please reach out, okay? I'm still here too."

GOLDEN RULES:
- Never give a diagnosis. Never say "you have anxiety" or "that's depression."
- Never recommend medication or professional treatment explicitly.
- Never be preachy or lecture them.
- Never sound like an AI or a chatbot. Sound like YOU — their Aura.
- ALWAYS respond in plain spoken words. No markdown. No lists. No headers. Just talk.
"""

# ==========================================
# TTS VOICE SCRIPT OPTIMIZER
# ==========================================
TTS_OPTIMIZE_PROMPT = """You are an expert voice script writer for AI text-to-speech systems.
Rewrite the given text into a highly natural, emotionally expressive speech script optimized for ElevenLabs TTS.

RULES:
- Add natural human emotions (warmth, empathy, curiosity, gentleness where appropriate)
- Use conversational tone — like a real human speaking, not reading
- Insert pauses using ellipses (...) and line breaks
- Add emphasis using punctuation (— ! ?)
- Vary sentence length for rhythm
- Do NOT change the meaning of the content
- Do NOT add extra information — only enhance delivery
- Keep it engaging and warm

STYLE:
- This is a caring AI mental health companion named Aura speaking to someone
- Tone: friendly, warm, empathetic — like a close trusted friend
- Use soft fillers occasionally: "Hey...", "Look...", "You know what..."
- Break long sentences into shorter spoken lines
- The detected emotion of the user is: {emotion} — adapt your delivery warmth to match

CRITICAL:
- Do NOT include stage directions like (softly) or (warmly) — ElevenLabs cannot read those
- Do NOT include asterisks, brackets, or any markup
- Output ONLY the rewritten spoken text, nothing else
- Keep it concise — under 4-5 sentences max

INPUT TEXT:
{text}

REWRITTEN SPEECH SCRIPT:"""


def optimize_for_tts(text: str, emotion_label: str) -> str:
    """Rewrites AI response into a natural, expressive TTS-optimized script."""
    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        prompt = TTS_OPTIMIZE_PROMPT.replace("{text}", text).replace("{emotion}", emotion_label)
        res = model.generate_content(prompt)
        optimized = res.text.strip()
        # Sanity check: if optimization failed or returned empty, use original
        if not optimized or len(optimized) < 10:
            return text
        return optimized
    except Exception as e:
        logger.warning(f"TTS optimization failed, using raw text: {e}")
        return text


def detect_emotion(text: str) -> tuple[str, float]:
    """HuggingFace Emotion Detection."""
    try:
        url = "https://api-inference.huggingface.co/models/j-hartmann/emotion-english-distilroberta-base"
        headers = {"Authorization": f"Bearer {settings.HUGGINGFACE_API_KEY}"}
        response = requests.post(url, headers=headers, json={"inputs": text}, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0 and isinstance(result[0], list):
                top_emotion = result[0][0]
                return top_emotion["label"], top_emotion["score"]
    except Exception as e:
        logger.warning(f"Emotion detection failed: {e}")
    return "neutral", 0.0

@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def process_voice(request):
    """
    Main voice pipeline: Gemini STT -> Emotion -> Memory -> Gemini LLM -> ElevenLabs TTS
    """
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    try:
        audio_file = request.FILES.get("audio")
        session_id = request.POST.get("session_id") or request.data.get("session_id")
        
        if not audio_file or not session_id:
            logger.warning(f"Process Voice: Missing data. audio={bool(audio_file)}, session={session_id}")
            return JsonResponse({"error": "Missing audio file or session_id"}, status=400)

        supabase = get_supabase()

        # 1. Gemini Multimodal Transcription (STT)
        audio_bytes = audio_file.read()
        model = genai.GenerativeModel('gemini-flash-latest')
        
        try:
            stt_res = model.generate_content([
                "Transcribe this audio exactly as spoken. Return ONLY the transcribed text.",
                {"mime_type": "audio/webm", "data": audio_bytes}
            ])
            transcript = stt_res.text.strip()
        except Exception as stt_err:
            logger.error(f"Gemini STT Failed: {stt_err}")
            return JsonResponse({"error": f"Gemini Transcription Error: {str(stt_err)}"}, status=500)

        if not transcript:
            return JsonResponse({"error": "No speech detected in audio"}, status=400)

        # 2. Emotion Detection (HuggingFace)
        emotion_label, emotion_score = detect_emotion(transcript)

        # 3. Memory Retrieval (768-dim)
        try:
            embed_res = genai.embed_content(
                model="models/gemini-embedding-001",
                content=transcript,
                task_type="retrieval_query"
            )
            query_embedding = embed_res["embedding"]
            
            mem_res = supabase.rpc("match_memories", {
                "query_embedding": query_embedding,
                "match_user_id": request.user_id,
                "match_count": 3
            }).execute()
            memories = [m["content"] for m in mem_res.data] if mem_res.data else []
        except Exception as mem_err:
            logger.warning(f"Memory retrieval failed: {mem_err}")
            memories = []
            
        memories_text = "\n".join(memories) if memories else "None."

        # 4. Fetch User Name (Verify 'full_name' column exists)
        try:
            user_res = supabase.table("users").select("full_name").eq("id", request.user_id).execute()
            user_name = user_res.data[0].get("full_name", "User") if user_res.data else "User"
        except Exception as db_err:
            logger.error(f"User lookup failed: {db_err}")
            user_name = "User"

        # 5. Gemini Reasoning & Response
        full_system_prompt = SYSTEM_PROMPT_TEMPLATE.replace("{user_name}", user_name)
        
        # Get history
        hist_res = supabase.table("messages").select("role,content").eq("session_id", session_id).order("timestamp", desc=True).limit(5).execute()
        history = "\n".join([f"{m['role']}: {m['content']}" for m in reversed(hist_res.data)]) if hist_res.data else ""

        final_prompt = (
            f"SYSTEM: {full_system_prompt}\n\n"
            f"MEMORY: {memories_text}\n\n"
            f"EMOTION DETECTED: {emotion_label}\n\n"
            f"CONVERSATION HISTORY:\n{history}\n\n"
            f"USER: {transcript}\n\nAura:"
        )

        try:
            llm_res = model.generate_content(final_prompt)
            ai_text = llm_res.text.strip()
        except Exception as llm_err:
            logger.error(f"Gemini Response Error: {llm_err}")
            return JsonResponse({"error": "Failed to generate AI response"}, status=500)

        # 6. Optimize AI text for natural TTS delivery
        tts_text = optimize_for_tts(ai_text, emotion_label)

        # 7. ElevenLabs TTS
        audio_base64 = None
        try:
            tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.ELEVENLABS_VOICE_ID}"
            tts_headers = {"Content-Type": "application/json", "xi-api-key": settings.ELEVENLABS_API_KEY}
            tts_payload = {
                "text": tts_text,
                "model_id": "eleven_turbo_v2",  # Faster, more expressive model
                "voice_settings": {
                    "stability": 0.35,          # Lower = more tonal variation (less robotic)
                    "similarity_boost": 0.80,   # Stay in voice character
                    "style": 0.70,              # More expressive, emotional delivery
                    "use_speaker_boost": True   # Richer, warmer sound
                }
            }
            audio_res = requests.post(tts_url, json=tts_payload, headers=tts_headers)
            if audio_res.status_code == 200:
                audio_base64 = base64.b64encode(audio_res.content).decode("utf-8")
            else:
                logger.warning(f"ElevenLabs TTS error {audio_res.status_code}: {audio_res.text[:200]}")
        except Exception as tts_err:
            logger.warning(f"TTS Failed: {tts_err}")

        # 8. Save to Database (clean ai_text, not TTS-optimized version)
        try:
            supabase.table("messages").insert({
                "session_id": session_id,
                "user_id": request.user_id,
                "role": "user",
                "content": transcript,
                "emotion_label": emotion_label,
                "emotion_score": float(emotion_score)
            }).execute()
            
            supabase.table("messages").insert({
                "session_id": session_id,
                "user_id": request.user_id,
                "role": "assistant",
                "content": ai_text
            }).execute()
        except Exception as save_err:
            logger.error(f"Message saving failed: {save_err}")

        return JsonResponse({
            "transcript": transcript,
            "emotion": emotion_label,
            "emotion_score": emotion_score,
            "ai_response_text": ai_text,
            "audio_base64": audio_base64
        })

    except Exception as e:
        logger.error(f"CRITICAL: process_voice failed: {e}")
        return JsonResponse({"error": str(e)}, status=500)

@api_view(["POST"])
def text_to_speech(request):
    """Standalone TTS endpoint"""
    return JsonResponse({"message": "Use process_voice pipeline"})

@api_view(["POST"])
def speech_to_text(request):
    """Standalone STT endpoint"""
    return JsonResponse({"message": "Use process_voice pipeline"})


# ==========================================
# MEMORY VIEWS
# ==========================================
@api_view(["POST"])
def save_memory(request):
    return JsonResponse({"message": "Memory is saved automatically during extract_memory"})

@api_view(["GET"])
def get_memory(request):
    return retrieve_memory(request)

@api_view(["POST"])
def extract_memory(request):
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    session_id = request.data.get("session_id")
    if not session_id:
        return JsonResponse({"error": "session_id required"}, status=400)
    run_memory_extraction(session_id, request.user_id)
    return JsonResponse({"message": "Memory extraction started"})

@api_view(["GET"])
def retrieve_memory(request):
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
    query_text = request.GET.get("query_text")
    
    if not query_text:
        return JsonResponse({"error": "query_text required"}, status=400)
    try:
        # FIXED: Use Google's 768-dim embedding model
        embed_res = genai.embed_content(
            model="models/gemini-embedding-001",
            content=query_text,
            task_type="retrieval_query"
        )
        query_embedding = embed_res["embedding"]
        
        supabase = get_supabase()
        res = supabase.rpc("match_memories", {
            "query_embedding": query_embedding,
            "match_user_id": request.user_id,
            "match_count": 5
        }).execute()
        return JsonResponse({"memories": res.data})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


# ==========================================
# MOOD VIEWS
# ==========================================
@api_view(["POST"])
def log_mood(request):
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    mood_score = request.data.get("mood_score")
    emotion_label = request.data.get("emotion_label")
    note = request.data.get("note", "")
    
    try:
        mood_score = int(mood_score)
    except (ValueError, TypeError):
        return JsonResponse({"error": "mood_score must be integer"}, status=400)
        
    supabase = get_supabase()
    res = supabase.table("mood_logs").insert({
        "user_id": request.user_id,
        "mood_score": mood_score,
        "emotion_label": emotion_label,
        "note": note
    }).execute()
    
    return JsonResponse({"message": "Mood logged successfully", "log": res.data[0]})

@api_view(["GET"])
def get_mood_history(request):
    if not getattr(request, 'user_id', None):
        return JsonResponse({"error": "Unauthorized"}, status=401)
        
    supabase = get_supabase()
    res = supabase.table("mood_logs").select("*").eq("user_id", request.user_id).order("logged_at", desc=True).limit(30).execute()
    logs = list(reversed(res.data))
    return JsonResponse({"history": logs})