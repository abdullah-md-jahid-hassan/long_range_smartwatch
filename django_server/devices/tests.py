import uuid

from django.test import TestCase
from django.utils import timezone

from authentication.models import User
from .choices import DeviceLifecycleStatus
from .models import Device
from .services import register_device, touch_last_seen, revoke_device


class DeviceRegistrationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(email="watch-owner@example.com", password="x")
        self.other_user = User.objects.create_user(email="someone-else@example.com", password="x")

    def test_registering_same_uuid_twice_updates_not_duplicates(self):
        device_uuid = uuid.uuid4()
        register_device(user=self.user, device_uuid=device_uuid, model_name="Pixel 8")
        register_device(user=self.user, device_uuid=device_uuid, model_name="Pixel 8 Pro")

        self.assertEqual(Device.objects.filter(device_uuid=device_uuid).count(), 1)
        self.assertEqual(Device.objects.get(device_uuid=device_uuid).model_name, "Pixel 8 Pro")

    def test_is_online_immediately_after_touch(self):
        device = register_device(user=self.user, device_uuid=uuid.uuid4())
        touch_last_seen(device)
        device.refresh_from_db()
        self.assertTrue(device.is_online)

    def test_is_online_false_after_threshold(self):
        device = register_device(user=self.user, device_uuid=uuid.uuid4())
        device.last_seen_at = timezone.now() - timezone.timedelta(seconds=Device.ONLINE_THRESHOLD_SECONDS + 1)
        device.save(update_fields=["last_seen_at"])
        self.assertFalse(device.is_online)

    def test_revoked_device_never_online(self):
        device = register_device(user=self.user, device_uuid=uuid.uuid4())
        touch_last_seen(device)
        revoke_device(device)
        device.refresh_from_db()
        self.assertFalse(device.is_online)

    def test_list_only_returns_own_devices(self):
        register_device(user=self.user, device_uuid=uuid.uuid4())
        register_device(user=self.other_user, device_uuid=uuid.uuid4())

        self.client.force_login(self.user)
        response = self.client.get("/v1/devices/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()["data"]), 1)

    def test_revoke_other_users_device_returns_404(self):
        device = register_device(user=self.other_user, device_uuid=uuid.uuid4())

        self.client.force_login(self.user)
        response = self.client.delete(f"/v1/devices/{device.device_uuid}/")
        self.assertEqual(response.status_code, 404)
        device.refresh_from_db()
        self.assertEqual(device.status, DeviceLifecycleStatus.ACTIVE)
