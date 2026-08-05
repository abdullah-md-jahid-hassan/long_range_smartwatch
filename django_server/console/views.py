from datetime import timedelta

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST

from devices.choices import DeviceLifecycleStatus
from devices.models import Device
from devices.services import revoke_device
from device_actions.choices import ActionMode
from device_actions.models import ActionRequest, FeatureSchedule
from device_actions.registry import CATEGORIES, features_by_category, get_feature
from device_actions.services import trigger_action, set_feature_schedule, UnknownFeatureError

from .decorators import staff_required

User = get_user_model()

# Bound on how far back we look for "the latest run of each feature" —
# avoids an unbounded per-device history scan while comfortably covering
# every feature's most recent run in practice.
RECENT_ACTION_WINDOW = 200


@staff_required
def dashboard(request):
    online_threshold = timezone.now() - timedelta(seconds=Device.ONLINE_THRESHOLD_SECONDS)
    stats = {
        "total_devices": Device.objects.count(),
        "online_devices": Device.objects.filter(
            status=DeviceLifecycleStatus.ACTIVE,
            last_seen_at__gte=online_threshold,
        ).count(),
        "actions_today": ActionRequest.objects.filter(created_at__date=timezone.localdate()).count(),
        "staff_admins": User.objects.filter(is_staff=True).count(),
    }
    recent_actions = (
        ActionRequest.objects.select_related("device", "triggered_by")
        .order_by("-created_at")[:20]
    )
    return render(request, "console/dashboard.html", {
        "stats": stats,
        "recent_actions": recent_actions,
    })


@staff_required
def device_list(request):
    query = request.GET.get("q", "").strip()
    devices = Device.objects.select_related("user").order_by("-last_seen_at")
    if query:
        devices = devices.filter(
            Q(label__icontains=query) | Q(model_name__icontains=query) | Q(user__email__icontains=query)
        )
    page_obj = Paginator(devices, 25).get_page(request.GET.get("page"))
    return render(request, "console/device_list.html", {"page_obj": page_obj, "query": query})


def _device_action_context(device):
    """Shared by device_detail and the two AJAX action views so a triggered
    row and a freshly loaded page always render identically."""
    recent_window = list(
        ActionRequest.objects.filter(device=device).order_by("-created_at")[:RECENT_ACTION_WINDOW]
    )
    latest_by_feature = {}
    for action in recent_window:
        latest_by_feature.setdefault(action.feature_key, action)

    schedule_by_feature = {
        schedule.feature_key: schedule
        for schedule in FeatureSchedule.objects.filter(device=device)
    }

    categories = []
    for cat_key, cat_label in CATEGORIES.items():
        rows = [
            {
                "feature": feature,
                "latest": latest_by_feature.get(feature.key),
                "schedule": schedule_by_feature.get(feature.key),
            }
            for feature in features_by_category().get(cat_key, [])
        ]
        categories.append({"key": cat_key, "label": cat_label, "rows": rows})

    return categories, recent_window


@staff_required
def device_detail(request, device_uuid):
    device = get_object_or_404(Device.objects.select_related("user"), device_uuid=device_uuid)
    categories, recent_window = _device_action_context(device)
    return render(request, "console/device_detail.html", {
        "device": device,
        "categories": categories,
        "recent_actions": recent_window[:20],
    })


def _row_context(device, feature_key):
    feature = get_feature(feature_key)
    latest = ActionRequest.objects.filter(device=device, feature_key=feature_key).order_by("-created_at").first()
    schedule = FeatureSchedule.objects.filter(device=device, feature_key=feature_key).first()
    return {"feature": feature, "latest": latest, "schedule": schedule}


@staff_required
@require_POST
def trigger_action_view(request, device_uuid, feature_key):
    device = get_object_or_404(Device, device_uuid=device_uuid)

    params = {}
    if request.POST.get("facing"):
        params["facing"] = request.POST["facing"]
    if request.POST.get("enabled") is not None:
        params["enabled"] = request.POST["enabled"] == "true"

    try:
        trigger_action(
            device=device,
            feature_key=feature_key,
            mode=ActionMode.MANUAL,
            triggered_by=request.user,
            params=params,
        )
    except UnknownFeatureError:
        messages.error(request, f"Unknown feature: {feature_key}")

    return render(request, "console/partials/_action_row.html", {
        "device": device,
        "row": _row_context(device, feature_key),
    })


@staff_required
@require_POST
def update_schedule_view(request, device_uuid, feature_key):
    device = get_object_or_404(Device, device_uuid=device_uuid)
    enabled = request.POST.get("enabled") == "on"
    try:
        interval_seconds = max(30, int(request.POST.get("interval_seconds", 300)))
    except ValueError:
        interval_seconds = 300

    try:
        set_feature_schedule(device=device, feature_key=feature_key, enabled=enabled, interval_seconds=interval_seconds)
    except UnknownFeatureError:
        messages.error(request, f"Unknown feature: {feature_key}")
    except ValueError as exc:
        messages.error(request, str(exc))

    return render(request, "console/partials/_action_row.html", {
        "device": device,
        "row": _row_context(device, feature_key),
    })


@staff_required
@require_POST
def revoke_device_view(request, device_uuid):
    device = get_object_or_404(Device, device_uuid=device_uuid)
    revoke_device(device)
    messages.success(request, f"{device.display_name} revoked.")
    return redirect("console:device-detail", device_uuid=device_uuid)
