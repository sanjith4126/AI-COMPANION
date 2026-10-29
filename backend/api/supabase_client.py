"""
Supabase client singleton used across the backend.
Uses the service role key for server-side operations (bypasses RLS).
"""
from django.conf import settings
from supabase import create_client, Client

_client: Client = None


def get_supabase() -> Client:
    """Return a cached Supabase client instance."""
    global _client
    if _client is None:
        _client = create_client(
            settings.SUPABASE_URL,
            settings.SUPABASE_SERVICE_ROLE_KEY,
        )
    return _client
