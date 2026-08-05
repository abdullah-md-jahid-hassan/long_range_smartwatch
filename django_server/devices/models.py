from django.conf import settings
from django.db import models
from django.utils import timezone

from core.models import BaseModel
from .choices import DeviceLifecycleStatus


class Device(BaseModel):
    """
    One row per installed app (currently always the phone — see main_plan.md
    §5.3: in Phase 1 "the device" is the phone itself; a paired watch is a
    Phase 2+ concept once its hardware/protocol exists).
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="devices",
    )
    device_uuid = models.UUIDField(unique=True, db_index=True)
    label = models.CharField(max_length=100, blank=True)
    model_name = models.CharField(max_length=100, blank=True)
    os_version = models.CharField(max_length=50, blank=True)
    app_version = models.CharField(max_length=30, blank=True)
    fcm_token = models.CharField(max_length=255, blank=True)
    fcm_token_set_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=DeviceLifecycleStatus.choices,
        default=DeviceLifecycleStatus.ACTIVE,
    )
    last_seen_at = models.DateTimeField(null=True, blank=True, db_index=True)
    last_ip = models.GenericIPAddressField(null=True, blank=True)

    # Recency window used by `is_online` — not a stored/pushed flag, so there
    # is no background job needed to flip devices to "offline".
    ONLINE_THRESHOLD_SECONDS = 180

    class Meta:
        db_table = "devices_device"
        ordering = ["-last_seen_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["last_seen_at"]),
        ]

    def __str__(self):
        return self.label or f"{self.model_name or 'device'} ({str(self.device_uuid)[:8]})"

    @property
    def is_online(self) -> bool:
        if self.status != DeviceLifecycleStatus.ACTIVE or self.last_seen_at is None:
            return False
        return (timezone.now() - self.last_seen_at).total_seconds() < self.ONLINE_THRESHOLD_SECONDS

    @property
    def display_name(self) -> str:
        return self.label or self.model_name or "Unnamed device"
