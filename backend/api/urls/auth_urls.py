from django.urls import path
from api import views

urlpatterns = [
    path("verify-token/", views.verify_token, name="verify_token"),
]