from django.urls import path
from api import views

urlpatterns = [
    path("log/", views.log_mood, name="log_mood"),
    path("history/", views.get_mood_history, name="get_mood_history"),
]