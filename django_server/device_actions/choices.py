from django.db import models


class ActionMode(models.TextChoices):
    MANUAL = "manual", "Manual"
    AUTO = "auto", "Automatic"


class ActionStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    NO_APP_CONNECTED = "no_app_connected", "No app connected"
    DISPATCHED = "dispatched", "Dispatched"
    SUCCEEDED = "succeeded", "Succeeded"
    FAILED = "failed", "Failed"
