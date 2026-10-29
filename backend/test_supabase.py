
import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mindcompanion.settings')
django.setup()

from api.supabase_client import get_supabase

def test_supabase():
    supabase = get_supabase()
    print(f"Testing Supabase at {settings.SUPABASE_URL}")
    print(f"Using Service Role Key (first 10 chars): {settings.SUPABASE_SERVICE_ROLE_KEY[:10]}...")
    
    try:
        # Try to select from sessions
        res = supabase.table("sessions").select("*").limit(1).execute()
        print("Successfully selected from sessions table.")
        print(f"Data: {res.data}")
    except Exception as e:
        print(f"Error selecting from sessions: {e}")

    try:
        # Try to insert a dummy session (need a valid user_id though)
        # Let's try to find a user first
        user_res = supabase.table("users").select("id").limit(1).execute()
        if user_res.data:
            user_id = user_res.data[0]["id"]
            print(f"Attempting to insert session for user {user_id}...")
            ins_res = supabase.table("sessions").insert({"user_id": user_id}).execute()
            print("Successfully inserted session.")
            print(f"New session ID: {ins_res.data[0]['id']}")
        else:
            print("No users found to test session insertion.")
    except Exception as e:
        print(f"Error inserting into sessions: {e}")

if __name__ == "__main__":
    test_supabase()
