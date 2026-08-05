import uuid

from django.test import TestCase

from authentication.models import User
from devices.services import register_device
from .choices import ActionMode, ActionStatus
from .models import ActionRequest, FeatureSchedule
from .registry import get_feature, features_by_category, FEATURES
from .services import (
    UnknownFeatureError,
    trigger_action,
    submit_action_result,
    set_feature_schedule,
)


class RegistryTests(TestCase):
    def test_every_message_source_has_a_feature(self):
        for key in ("messages.sms", "messages.whatsapp", "messages.imo", "messages.gmail"):
            self.assertIsNotNone(get_feature(key))

    def test_unknown_feature_returns_none(self):
        self.assertIsNone(get_feature("not.a.real.feature"))

    def test_features_grouped_by_category_cover_every_feature(self):
        grouped_count = sum(len(v) for v in features_by_category().values())
        self.assertEqual(grouped_count, len(FEATURES))


class TriggerActionTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="owner@example.com", password="x")
        self.device = register_device(user=self.user, device_uuid=uuid.uuid4())

    def test_trigger_unknown_feature_raises(self):
        with self.assertRaises(UnknownFeatureError):
            trigger_action(device=self.device, feature_key="nope", mode=ActionMode.MANUAL)

    def test_placeholder_connector_resolves_immediately_as_no_app_connected(self):
        action_request = trigger_action(
            device=self.device,
            feature_key="basic_info.battery",
            mode=ActionMode.MANUAL,
            triggered_by=self.user,
        )
        self.assertEqual(action_request.status, ActionStatus.NO_APP_CONNECTED)
        self.assertIsNotNone(action_request.responded_at)
        self.assertEqual(action_request.triggered_by, self.user)

    def test_submit_action_result_is_scoped_to_owning_device(self):
        action_request = ActionRequest.objects.create(
            device=self.device, feature_key="basic_info.battery", mode=ActionMode.MANUAL,
        )
        other_device = register_device(user=self.user, device_uuid=uuid.uuid4())

        with self.assertRaises(ActionRequest.DoesNotExist):
            submit_action_result(action_request_id=action_request.id, device=other_device, success=True)

        resolved = submit_action_result(
            action_request_id=action_request.id, device=self.device, success=True, result={"battery_pct": 87},
        )
        self.assertEqual(resolved.status, ActionStatus.SUCCEEDED)
        self.assertEqual(resolved.result, {"battery_pct": 87})

    def test_schedule_rejected_for_feature_without_auto_support(self):
        with self.assertRaises(ValueError):
            set_feature_schedule(device=self.device, feature_key="screen.screenshot", enabled=True, interval_seconds=60)

    def test_schedule_upsert_does_not_duplicate(self):
        set_feature_schedule(device=self.device, feature_key="basic_info.battery", enabled=True, interval_seconds=120)
        set_feature_schedule(device=self.device, feature_key="basic_info.battery", enabled=True, interval_seconds=300)

        schedules = FeatureSchedule.objects.filter(device=self.device, feature_key="basic_info.battery")
        self.assertEqual(schedules.count(), 1)
        self.assertEqual(schedules.first().interval_seconds, 300)
