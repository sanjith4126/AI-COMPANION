
import psycopg2

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
db_url = os.environ["SUPABASE_DB_URL"]

def apply_grants():
    print(f"Connecting to {db_url}...")
    try:
        conn = psycopg2.connect(db_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        commands = [
            'GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;',
            'GRANT ALL ON ALL TABLES IN SCHEMA public TO postgres, service_role;',
            'GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO postgres, service_role;',
            'GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO postgres, service_role;',
            'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO authenticated;',
            'GRANT SELECT, INSERT, UPDATE, DELETE ON ALL SEQUENCES IN SCHEMA public TO authenticated;',
            'GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;'
        ]
        
        for cmd in commands:
            try:
                print(f"Executing: {cmd}")
                cursor.execute(cmd)
            except Exception as e:
                print(f"Warning: Command failed: {cmd}. Error: {e}")
        
        print("Grants application process finished.")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    apply_grants()
