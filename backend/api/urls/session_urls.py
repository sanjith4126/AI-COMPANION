from django.urls import path
from api import views

urlpatterns = [
    path("start/", views.start_session, name="start_session"),
    path("end/", views.end_session, name="end_session"),
]
