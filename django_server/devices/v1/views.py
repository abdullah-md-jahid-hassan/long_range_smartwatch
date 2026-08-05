from rest_framework import status, permissions
from rest_framework.views import APIView

from core.utils.response import success_response, error_response
from core.utils.general import get_or_400
from ..models import Device
from ..services import register_device, update_fcm_token, revoke_device
from .serializers import DeviceSerializer


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


class RegisterDeviceView(APIView):
    """
    POST /v1/devices/register/
    Called on every app cold start (not just first install) — upserts this
    install's Device row by device_uuid. See devices/docs/README.md for the
    full "what is a connection" writeup.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        ok, result = get_or_400(
            data=request.data,
            keys={
                "device_uuid": str,
                "model_name": str,
                "os_version": str,
                "app_version": str,
                "fcm_token": str,
            },
            required=["device_uuid"],
        )
        if not ok:
            return result

        device = register_device(
            user=request.user,
            device_uuid=result["device_uuid"],
            model_name=result.get("model_name") or "",
            os_version=result.get("os_version") or "",
            app_version=result.get("app_version") or "",
            fcm_token=result.get("fcm_token") or "",
            ip=_client_ip(request),
        )
        return success_response(
            message="Device registered",
            data=DeviceSerializer(device).data,
            status_code=status.HTTP_201_CREATED,
        )


class UpdateFcmTokenView(APIView):
    """PATCH /v1/devices/fcm-token/ — called whenever Firebase issues a new token."""
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request):
        ok, result = get_or_400(
            data=request.data,
            keys={"device_uuid": str, "fcm_token": str},
            required=["device_uuid", "fcm_token"],
        )
        if not ok:
            return result

        device = Device.objects.filter(user=request.user, device_uuid=result["device_uuid"]).first()
        if device is None:
            return error_response(message="Device not found", status_code=status.HTTP_404_NOT_FOUND)

        update_fcm_token(device, result["fcm_token"])
        return success_response(message="FCM token updated")


class DeviceListView(APIView):
    """GET /v1/devices/ — the authenticated user's own devices only."""
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        devices = Device.objects.filter(user=request.user)
        return success_response(data=DeviceSerializer(devices, many=True).data)


class DeviceRevokeView(APIView):
    """DELETE /v1/devices/<device_uuid>/ — soft-revoke, own devices only.

    Returns 404 (not 403) when the device belongs to another user, so the
    response never confirms whether a given device_uuid exists at all.
    """
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, device_uuid):
        device = Device.objects.filter(user=request.user, device_uuid=device_uuid).first()
        if device is None:
            return error_response(message="Device not found", status_code=status.HTTP_404_NOT_FOUND)

        revoke_device(device)
        return success_response(message="Device revoked")
