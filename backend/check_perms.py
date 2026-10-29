
import psycopg2

import os
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
db_url = os.environ["SUPABASE_DB_URL"]

def check_permissions():
    print(f"Connecting to {db_url}...")
    try:
        conn = psycopg2.connect(db_url)
        cursor = conn.cursor()
        
        # Check table owner and permissions for public.sessions
        print("\n--- Permissions for public.sessions ---")
        cursor.execute("""
            SELECT grantee, privilege_type 
            FROM information_schema.role_table_grants 
            WHERE table_name = 'sessions' AND table_schema = 'public';
        """)
        grants = cursor.fetchall()
        for grant in grants:
            print(f"Grantee: {grant[0]}, Privilege: {grant[1]}")
            
        # Check if service_role has access
        print("\n--- Roles and Membership ---")
        cursor.execute("""
            SELECT rolname FROM pg_roles WHERE rolname IN ('service_role', 'anon', 'authenticated', 'postgres');
        """)
        roles = cursor.fetchall()
        for role in roles:
            print(f"Role: {role[0]}")

        # Check for RLS
        print("\n--- RLS Status ---")
        cursor.execute("""
            SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = 'public' AND tablename = 'sessions';
        """)
        rls = cursor.fetchone()
        print(f"Table: {rls[0]}, RLS Enabled: {rls[1]}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    check_permissions()
