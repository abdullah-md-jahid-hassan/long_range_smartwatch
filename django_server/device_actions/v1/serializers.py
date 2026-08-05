from rest_framework import serializers

from ..models import ActionRequest, FeatureSchedule


class ActionRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ActionRequest
        fields = ["id", "feature_key", "mode", "status", "params", "result", "error_message", "created_at", "responded_at"]
        read_only_fields = fields


class FeatureScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = FeatureSchedule
        fields = ["feature_key", "enabled", "interval_seconds"]
        read_only_fields = fields
