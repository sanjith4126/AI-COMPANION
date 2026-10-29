from django.urls import path
from api import views

urlpatterns = [
    path("extract/", views.extract_memory, name="extract_memory"),
    path("retrieve/", views.retrieve_memory, name="retrieve_memory"),
]
