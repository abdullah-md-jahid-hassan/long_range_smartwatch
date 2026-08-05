import logging

from django.utils import timezone

logger = logging.getLogger("django.logs.app")

_TOUCH_MIN_INTERVAL_SECONDS = 60


class DeviceLivenessMiddleware:
    """
    Piggybacks liveness tracking on requests the phone app is already making
    for other reasons (fetch a feature, post a result, etc.) instead of a
    dedicated heartbeat endpoint — see devices/docs/README.md. Any
    authenticated request carrying `X-Device-Id` gets its device's
    `last_seen_at` bumped, throttled to once per minute per device so a burst
    of calls doesn't turn into a write per request.

    Must run after AuthenticationMiddleware (request.user must be resolved).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        self._maybe_touch(request)
        return response

    def _maybe_touch(self, request):
        device_uuid = request.headers.get("X-Device-Id")
        if not device_uuid:
            return
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated:
            return

        try:
            from .models import Device
            from .services import touch_last_seen

            device = Device.objects.filter(user=user, device_uuid=device_uuid).first()
            if device is None:
                return
            if device.last_seen_at and (timezone.now() - device.last_seen_at).total_seconds() < _TOUCH_MIN_INTERVAL_SECONDS:
                return
            touch_last_seen(device, ip=request.META.get("REMOTE_ADDR"))
        except Exception as exc:
            logger.warning(
                "DeviceLivenessMiddleware: touch failed: %s", exc,
                extra={"event_name": "devices.liveness.touch_failed"},
            )
