"""
Celery tasks for async processing (e.g. memory extraction).
"""
import logging
from celery import shared_task
from api.supabase_client import get_supabase
import google.generativeai as genai
from django.conf import settings

logger = logging.getLogger(__name__)
genai.configure(api_key=settings.GOOGLE_API_KEY)

@shared_task
def extract_memory_task(session_id: str, user_id: str):
    """
    Extracts key facts from a session and stores them as vector embeddings in Supabase.
    """
    try:
        supabase = get_supabase()
        
        # 1. Fetch all messages for the session
        res = supabase.table("messages").select("role,content").eq("session_id", session_id).order("timestamp").execute()
        messages = res.data
        
        if not messages:
            logger.info(f"No messages found for session {session_id}")
            return
            
        # Format conversation history
        history = "\n".join([f"{msg['role'].capitalize()}: {msg['content']}" for msg in messages])
        
        # 2. Call Gemini Flash to extract facts
        prompt = (
            "Extract 3-5 key facts about this user from this conversation. "
            "Each fact should be one sentence. "
            "Focus on: emotional patterns, life events, stressors, coping strategies that helped.\n\n"
            f"Conversation:\n{history}\n\nFacts:"
        )
        
        try:
            model = genai.GenerativeModel('gemini-flash-latest')
            response = model.generate_content(prompt)
            facts_text = response.text.strip()
        except Exception as ai_err:
            logger.error(f"Gemini extraction failed for {session_id}: {ai_err}")
            return
        
        facts = [f.strip("- *").strip() for f in facts_text.split("\n") if f.strip("- *").strip()]
        
        # 3. Embed each fact and store
        for fact in facts:
            if not fact:
                continue
                
            try:
                # FIXED: Use Google's 768-dim embedding model
                embed_res = genai.embed_content(
                    model="models/gemini-embedding-001",
                    content=fact,
                    task_type="retrieval_document"
                )
                embedding = embed_res["embedding"]
                
                # Store in Supabase
                node_data = {
                    "user_id": user_id,
                    "content": fact,
                    "embedding": embedding,
                    "source_session_id": session_id
                }
                supabase.table("memory_nodes").insert(node_data).execute()
            except Exception as e:
                # FIXED: Log individual fact embedding failures without crashing the whole task
                logger.warning(f"Failed to store memory node: {e}")
            
        logger.info(f"Successfully extracted {len(facts)} memories for session {session_id}")
        
    except Exception as e:
        # FIXED: More descriptive top-level error log
        logger.error(f"FATAL Task Error: extract_memory_task for session {session_id}: {e}")
        raise e


def run_memory_extraction(session_id: str, user_id: str):
    """Queue memory extraction on Celery; run it inline if Redis is unreachable."""
    try:
        extract_memory_task.delay(session_id, user_id)
    except Exception as e:
        # ponytail: without Redis this blocks the request (~5s + Gemini time); run Redis + a worker to keep it async
        logger.warning(f"Celery broker unavailable ({e}); extracting memory inline")
        extract_memory_task(session_id, user_id)
