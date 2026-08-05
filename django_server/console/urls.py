from django.contrib.auth.views import LogoutView
from django.urls import path

from . import views
from .auth import ConsoleLoginView

app_name = "console"

urlpatterns = [
    path("login/", ConsoleLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(next_page="console:login"), name="logout"),

    path("", views.dashboard, name="dashboard"),
    path("devices/", views.device_list, name="device-list"),
    path("devices/<uuid:device_uuid>/", views.device_detail, name="device-detail"),
    path("devices/<uuid:device_uuid>/revoke/", views.revoke_device_view, name="revoke-device"),
    path(
        "devices/<uuid:device_uuid>/actions/<str:feature_key>/trigger/",
        views.trigger_action_view,
        name="trigger-action",
    ),
    path(
        "devices/<uuid:device_uuid>/actions/<str:feature_key>/schedule/",
        views.update_schedule_view,
        name="update-schedule",
    ),
]
