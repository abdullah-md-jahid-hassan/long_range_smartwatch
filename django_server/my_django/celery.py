import os
from celery import Celery
from django.conf import settings

# -------------------------------------------------------------------
# Set default Django settings module for 'celery' CLI programs
# -------------------------------------------------------------------
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "my_django.settings")

# -------------------------------------------------------------------
# Create Celery application
# -------------------------------------------------------------------
app = Celery("my_django")

# -------------------------------------------------------------------
# Load configuration from Django settings
# Namespace all Celery-related settings with `CELERY_`
# Example: CELERY_BROKER_URL, CELERY_RESULT_BACKEND
# -------------------------------------------------------------------
app.config_from_object("django.conf:settings", namespace="CELERY")

# -------------------------------------------------------------------
# Auto-discover tasks from all registered Django apps
# Looks for tasks.py inside each app
# -------------------------------------------------------------------
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

# -------------------------------------------------------------------
# Optional: Debug task (useful for verifying Celery is working)
# -------------------------------------------------------------------
@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f"Request: {self.request!r}")