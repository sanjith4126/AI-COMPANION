"""
Celery application configuration for mindcompanion.
"""
import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "mindcompanion.settings")

app = Celery("mindcompanion")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
