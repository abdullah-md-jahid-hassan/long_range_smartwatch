from django.contrib import admin

from .models import ActionRequest, FeatureSchedule


@admin.register(ActionRequest)
class ActionRequestAdmin(admin.ModelAdmin):
    list_display = ("feature_key", "device", "mode", "status", "triggered_by", "created_at")
    list_filter = ("status", "mode", "feature_key")
    search_fields = ("feature_key", "device__label", "device__device_uuid")
    readonly_fields = [f.name for f in ActionRequest._meta.fields]


@admin.register(FeatureSchedule)
class FeatureScheduleAdmin(admin.ModelAdmin):
    list_display = ("feature_key", "device", "enabled", "interval_seconds")
    list_filter = ("enabled", "feature_key")
