"""
The seam between "decide to run a feature" (services/actions.py) and
"actually get a phone to run it" (transport). Swapping Phase 1's
PlaceholderConnector for a real FCM-backed one later is the entire
integration point — trigger_action(), the admin panel, and the eventual
watch API never change. See main_plan.md's hard boundary on consent: a
connector is what makes a feature real, so this file is the one place
that decides whether anything can actually reach a phone yet.
"""
from abc import ABC, abstractmethod

from django.conf import settings
from django.utils import timezone

from .choices import ActionStatus


class BaseDeviceConnector(ABC):
    @abstractmethod
    def dispatch(self, action_request) -> None:
        """Mutate and persist action_request's status/result in place."""
        raise NotImplementedError


class PlaceholderConnector(BaseDeviceConnector):
    """
    Active for every device until the mobile app exists to pair with (no
    exceptions — there is nothing to fake here). Resolves every request
    immediately and honestly: there is no installed app anywhere to deliver
    this to yet. Not a stub that silently no-ops or fakes a success.
    """

    def dispatch(self, action_request) -> None:
        action_request.status = ActionStatus.NO_APP_CONNECTED
        action_request.error_message = (
            "No companion app is paired with this device yet. This action will "
            "run automatically once the mobile app is installed, the required "
            "permission is granted, and the device is connected."
        )
        action_request.responded_at = timezone.now()
        action_request.save(update_fields=["status", "error_message", "responded_at", "updated_at"])


_CONNECTOR_BACKENDS = {
    "placeholder": PlaceholderConnector,
}


def get_connector() -> BaseDeviceConnector:
    backend_key = getattr(settings, "DEVICE_CONNECTOR_BACKEND", "placeholder")
    connector_cls = _CONNECTOR_BACKENDS.get(backend_key)
    if connector_cls is None:
        raise ValueError(f"Unknown DEVICE_CONNECTOR_BACKEND: {backend_key!r}")
    return connector_cls()
