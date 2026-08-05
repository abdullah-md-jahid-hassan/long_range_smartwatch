from django.utils import timezone

from devices.models import Device
from ..choices import ActionMode, ActionStatus
from ..connectors import get_connector
from ..models import ActionRequest, FeatureSchedule
from ..registry import get_feature


class UnknownFeatureError(Exception):
    pass


def trigger_action(
    *,
    device: Device,
    feature_key: str,
    mode: str = ActionMode.MANUAL,
    triggered_by=None,
    params: dict | None = None,
) -> ActionRequest:
    """
    The one entry point every caller — admin panel today, watch API later —
    uses to run a feature. Creates the audit row, then hands off to whatever
    connector is configured (main_plan.md §5.1/§5.2). Never contains
    per-feature branching: that lives in the registry and, eventually, in
    each connector's own transport logic.
    """
    feature = get_feature(feature_key)
    if feature is None:
        raise UnknownFeatureError(feature_key)

    action_request = ActionRequest.objects.create(
        device=device,
        feature_key=feature_key,
        mode=mode,
        triggered_by=triggered_by,
        params=params or {},
    )
    get_connector().dispatch(action_request)
    action_request.refresh_from_db()
    return action_request


def submit_action_result(
    *,
    action_request_id,
    device: Device,
    success: bool,
    result=None,
    error_message: str = "",
) -> ActionRequest:
    """
    The other half of the connector contract — this is what the mobile app
    will call once it exists (POST /v1/devices/actions/<device_uuid>/<id>/result/).
    Scoped to `device` so one paired phone can never resolve another's
    request; raises ActionRequest.DoesNotExist otherwise.
    """
    action_request = ActionRequest.objects.get(id=action_request_id, device=device)
    action_request.status = ActionStatus.SUCCEEDED if success else ActionStatus.FAILED
    action_request.result = result
    action_request.error_message = error_message
    action_request.responded_at = timezone.now()
    action_request.save(update_fields=["status", "result", "error_message", "responded_at", "updated_at"])
    return action_request


def latest_action_for(device: Device, feature_key: str) -> ActionRequest | None:
    return ActionRequest.objects.filter(device=device, feature_key=feature_key).order_by("-created_at").first()


def get_schedule(device: Device, feature_key: str) -> FeatureSchedule | None:
    return FeatureSchedule.objects.filter(device=device, feature_key=feature_key).first()


def set_feature_schedule(*, device: Device, feature_key: str, enabled: bool, interval_seconds: int) -> FeatureSchedule:
    feature = get_feature(feature_key)
    if feature is None:
        raise UnknownFeatureError(feature_key)
    if enabled and not feature.supports_auto:
        raise ValueError(f"{feature_key} does not support automatic/interval mode")

    schedule, _created = FeatureSchedule.objects.update_or_create(
        device=device,
        feature_key=feature_key,
        defaults={"enabled": enabled, "interval_seconds": interval_seconds},
    )
    return schedule
