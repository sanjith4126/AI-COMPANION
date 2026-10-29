"""
Root URL configuration for mindcompanion Django project.
"""
from django.urls import path, include

from api import views

urlpatterns = [
    path("",             views.home, name="home"),
    path("api/auth/",    include("api.urls.auth_urls")),
    path("api/sessions/",include("api.urls.session_urls")),
    path("api/voice/",   include("api.urls.voice_urls")),
    path("api/memory/",  include("api.urls.memory_urls")),
    path("api/mood/",    include("api.urls.mood_urls")),
]
