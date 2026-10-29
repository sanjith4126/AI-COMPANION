import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_URL = os.environ.get("SUPABASE_DB_URL")

def migrate():
    print(f"Connecting to {DB_URL}...")
    conn = psycopg2.connect(DB_URL)
    conn.autocommit = True
    cur = conn.cursor()
    
    try:
        print("Dropping existing vector index...")
        cur.execute("DROP INDEX IF EXISTS public.memory_nodes_embedding_idx;")
        
        print("Updating column from vector(1536) to vector(768)...")
        # Altering vector dimension usually requires dropping and recreating the column
        cur.execute("ALTER TABLE public.memory_nodes DROP COLUMN IF EXISTS embedding;")
        cur.execute("ALTER TABLE public.memory_nodes ADD COLUMN embedding vector(768);")
        
        print("Recreating vector index...")
        cur.execute("""
            CREATE INDEX IF NOT EXISTS memory_nodes_embedding_idx
            ON public.memory_nodes
            USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
        """)
        
        print("Updating match_memories function...")
        cur.execute("""
            CREATE OR REPLACE FUNCTION public.match_memories(
                query_embedding vector(768),
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
        """)
        
        print("Migration successful.")
    except Exception as e:
        print(f"Migration failed: {e}")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    migrate()
