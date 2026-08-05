from django.utils import timezone

from ..choices import DeviceLifecycleStatus
from ..models import Device


def register_device(*, user, device_uuid, model_name="", os_version="", app_version="", fcm_token="", ip=None) -> Device:
    """
    Create-or-update by (user, device_uuid). The app calls this on every cold
    start, not just first install, so re-registering an existing device_uuid
    updates metadata rather than erroring.

    Deliberately does NOT reset status to ACTIVE for an existing row: a
    revoke is a deliberate removal (console action or the user's own "remove
    this device"), and the same install calling register again on its next
    launch should not silently undo that — reactivation has to be explicit.
    """
    defaults = {
        "model_name": model_name,
        "os_version": os_version,
        "app_version": app_version,
        "last_seen_at": timezone.now(),
        "last_ip": ip,
    }
    if fcm_token:
        defaults["fcm_token"] = fcm_token
        defaults["fcm_token_set_at"] = timezone.now()

    existing = Device.objects.filter(user=user, device_uuid=device_uuid).first()
    if existing is None:
        defaults["status"] = DeviceLifecycleStatus.ACTIVE

    device, _created = Device.objects.update_or_create(
        user=user,
        device_uuid=device_uuid,
        defaults=defaults,
    )
    return device


def update_fcm_token(device: Device, fcm_token: str) -> Device:
    device.fcm_token = fcm_token
    device.fcm_token_set_at = timezone.now()
    device.save(update_fields=["fcm_token", "fcm_token_set_at", "updated_at"])
    return device


def touch_last_seen(device: Device, ip: str | None = None) -> None:
    """Called opportunistically off any authenticated, device-tagged request
    (see devices/middleware.py) rather than a dedicated heartbeat endpoint —
    keeps liveness tracking free of extra battery-draining network calls."""
    update_fields = ["last_seen_at", "updated_at"]
    device.last_seen_at = timezone.now()
    if ip:
        device.last_ip = ip
        update_fields.append("last_ip")
    device.save(update_fields=update_fields)


def revoke_device(device: Device) -> Device:
    device.status = DeviceLifecycleStatus.REVOKED
    device.save(update_fields=["status", "updated_at"])
    return device
