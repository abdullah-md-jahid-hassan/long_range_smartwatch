from django.conf import settings
from django.db import models

from core.models import BaseModel
from devices.models import Device
from .choices import ActionMode, ActionStatus


class ActionRequest(BaseModel):
    """One row per feature invocation — manual click or auto-interval run.
    This is the audit trail for "who triggered it and when" (an admin today,
    the watch API later) as well as the record the connector resolves."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="action_requests")
    feature_key = models.CharField(max_length=100, db_index=True)
    mode = models.CharField(max_length=10, choices=ActionMode.choices)
    status = models.CharField(max_length=20, choices=ActionStatus.choices, default=ActionStatus.PENDING, db_index=True)
    triggered_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="triggered_actions",
    )
    params = models.JSONField(default=dict, blank=True)
    result = models.JSONField(null=True, blank=True)
    error_message = models.CharField(max_length=500, blank=True)
    responded_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "device_actions_action_request"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["device", "feature_key", "-created_at"]),
            models.Index(fields=["device", "-created_at"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return f"{self.feature_key} -> device {self.device_id} [{self.status}]"


class FeatureSchedule(BaseModel):
    """Per-device, per-feature auto-interval config (main_plan.md §4). The
    server only stores this; the phone pulls it and self-schedules with
    WorkManager/AlarmManager — there is no per-device cron on the server."""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name="feature_schedules")
    feature_key = models.CharField(max_length=100, db_index=True)
    enabled = models.BooleanField(default=False)
    interval_seconds = models.PositiveIntegerField(default=300)

    class Meta:
        db_table = "device_actions_feature_schedule"
        constraints = [
            models.UniqueConstraint(fields=["device", "feature_key"], name="unique_device_feature_schedule"),
        ]

    def __str__(self):
        state = "auto" if self.enabled else "manual"
        return f"{self.feature_key} @ device {self.device_id} ({state}, every {self.interval_seconds}s)"
