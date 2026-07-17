from django.conf import settings
from django.db import models

from core.models import BaseModel


class Notification(BaseModel):
    user    = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
    )
    title   = models.CharField(max_length=255)
    body    = models.TextField()
    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"

    def __str__(self):
        return f"{self.user_id} — {self.title} [{'read' if self.is_read else 'unread'}]"
