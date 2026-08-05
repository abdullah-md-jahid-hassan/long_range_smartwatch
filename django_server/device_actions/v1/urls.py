from django.urls import path

from .views import SubmitActionResultView, DeviceScheduleListView

app_name = "device_actions_v1"

urlpatterns = [
    path("<uuid:device_uuid>/schedules/", DeviceScheduleListView.as_view(), name="schedules"),
    path("<uuid:device_uuid>/<int:action_id>/result/", SubmitActionResultView.as_view(), name="result"),
]
