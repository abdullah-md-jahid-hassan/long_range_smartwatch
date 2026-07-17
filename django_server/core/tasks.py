from celery import shared_task
from django.core.cache import cache
from datetime import datetime

@shared_task
def beat_heartbeat():
    cache.set("beat_last_seen", datetime.utcnow().isoformat(), timeout=120)
