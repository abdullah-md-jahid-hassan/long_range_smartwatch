from rest_framework import status, permissions
from rest_framework.views import APIView

from core.utils.response import success_response, error_response
from core.utils.general import get_or_400
from devices.models import Device
from ..models import ActionRequest, FeatureSchedule
from ..services import submit_action_result
from .serializers import ActionRequestSerializer, FeatureScheduleSerializer


def _own_device_or_404(request, device_uuid):
    return Device.objects.filter(user=request.user, device_uuid=device_uuid).first()


class SubmitActionResultView(APIView):
    """
    POST /v1/devices/actions/<device_uuid>/<action_id>/result/

    The other half of the connector contract (see device_actions/connectors.py):
    this is what the mobile app calls once it exists, to resolve a request the
    server dispatched to it. Not called by anything yet — no app to call it —
    but it's real and testable today (simulate the app with curl/Postman)
    rather than a documented-but-unbuilt placeholder.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, device_uuid, action_id):
        device = _own_device_or_404(request, device_uuid)
        if device is None:
            return error_response(message="Device not found", status_code=status.HTTP_404_NOT_FOUND)

        ok, result = get_or_400(
            data=request.data,
            keys={"success": bool, "result": None, "error_message": str},
            required=["success"],
        )
        if not ok:
            return result

        try:
            action_request = submit_action_result(
                action_request_id=action_id,
                device=device,
                success=result["success"],
                result=result.get("result"),
                error_message=result.get("error_message") or "",
            )
        except ActionRequest.DoesNotExist:
            return error_response(message="Action request not found", status_code=status.HTTP_404_NOT_FOUND)

        return success_response(message="Result recorded", data=ActionRequestSerializer(action_request).data)


class DeviceScheduleListView(APIView):
    """
    GET /v1/devices/actions/<device_uuid>/schedules/

    The phone pulls its own auto-interval config here (at register/heartbeat
    time) and self-schedules locally with WorkManager/AlarmManager — the
    server never runs a per-device cron for "automatic" mode (main_plan.md §4).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, device_uuid):
        device = _own_device_or_404(request, device_uuid)
        if device is None:
            return error_response(message="Device not found", status_code=status.HTTP_404_NOT_FOUND)

        schedules = FeatureSchedule.objects.filter(device=device, enabled=True)
        return success_response(data=FeatureScheduleSerializer(schedules, many=True).data)
