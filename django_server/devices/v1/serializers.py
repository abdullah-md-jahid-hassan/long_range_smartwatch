from rest_framework import serializers

from ..models import Device


class DeviceSerializer(serializers.ModelSerializer):
    is_online = serializers.BooleanField(read_only=True)

    class Meta:
        model = Device
        fields = [
            "device_uuid", "label", "model_name", "os_version", "app_version",
            "status", "is_online", "last_seen_at", "created_at",
        ]
        read_only_fields = fields
