from django.urls import path

from .views import RegisterDeviceView, UpdateFcmTokenView, DeviceListView, DeviceRevokeView

app_name = "devices_v1"

urlpatterns = [
    path("register/", RegisterDeviceView.as_view(), name="register"),
    path("fcm-token/", UpdateFcmTokenView.as_view(), name="fcm-token"),
    path("", DeviceListView.as_view(), name="list"),
    path("<uuid:device_uuid>/", DeviceRevokeView.as_view(), name="revoke"),
]
