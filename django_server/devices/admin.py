from django.contrib import admin

from .models import Device


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ("display_name", "user", "model_name", "status", "is_online", "last_seen_at", "created_at")
    list_filter = ("status",)
    search_fields = ("label", "model_name", "device_uuid", "user__email")
    readonly_fields = ("device_uuid", "created_at", "updated_at", "fcm_token_set_at")
