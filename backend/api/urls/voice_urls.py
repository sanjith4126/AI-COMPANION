from django.urls import path
from api import views

urlpatterns = [
    path("process/", views.process_voice, name="process_voice"),
]
