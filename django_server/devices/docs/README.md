# Devices Module

## 1. Overview
`devices` is the foundation every other feature attaches to (see `documentation/plan/main_plan.md` §5.3 and `iteration_1/step_1.md`). A `Device` row is one installed app — in Phase 1 that's always the phone, since no watch hardware/protocol exists yet.

Key characteristics:
- **No separate device secret.** The phone already authenticates as a normal user via the `authentication` app's JWT flow. A device only needs a client-generated `device_uuid` (identifies *this install*) and an `fcm_token` (where to push wake-up messages later).
- **Online/offline is computed, not stored.** `Device.is_online` checks `last_seen_at` recency against `Device.ONLINE_THRESHOLD_SECONDS` — no background job flips devices offline.
- **No dedicated heartbeat.** `last_seen_at` is updated opportunistically by `DeviceLivenessMiddleware` off of any authenticated request carrying an `X-Device-Id` header, piggybacking on traffic the app is making for other reasons rather than adding a battery-draining ping loop.

### File Structure
```
devices/
├── migrations/
├── docs/README.md          # this file
├── services/
│   ├── __init__.py
│   └── device.py            # register_device, update_fcm_token, touch_last_seen, revoke_device
├── v1/
│   ├── serializers.py
│   ├── urls.py
│   └── views.py
├── choices.py                # DeviceLifecycleStatus
├── models.py                 # Device
├── middleware.py              # DeviceLivenessMiddleware
└── admin.py
```

## 2. API — base path `/v1/devices/`
All endpoints are JWT-authenticated (`IsAuthenticated`), same as the rest of the project.

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/devices/register/` | Upsert this install's `Device` row by `device_uuid`. Safe to call on every cold start. |
| PATCH | `/v1/devices/fcm-token/` | Update just the FCM token (Firebase re-issues these over an install's lifetime). |
| GET | `/v1/devices/` | List the authenticated user's own devices. |
| DELETE | `/v1/devices/<uuid:device_uuid>/` | Soft-revoke a device. Returns 404 (not 403) for another user's device — never confirms it exists. |

### `POST /v1/devices/register/`
```json
{
  "device_uuid": "b3b6...-uuid",
  "model_name": "Pixel 8",
  "os_version": "15",
  "app_version": "0.1.0",
  "fcm_token": "..."
}
```
Only `device_uuid` is required. Response mirrors `devices/v1/serializers.DeviceSerializer`.

## 3. `X-Device-Id` header
Every authenticated request the phone app makes for any feature (fetch battery, submit an action result, etc.) should carry `X-Device-Id: <device_uuid>`. `DeviceLivenessMiddleware` uses it to bump `last_seen_at` (throttled to once per minute per device), which is what powers the "online now" count and per-device online pill in the console. No separate endpoint call is needed for this.

## 4. Adding a field to "basic info" or another modular feature
`devices` only owns *what a device is* (identity, connection state). Feature data (battery %, lock state, location, etc.) lives in `device_actions` and is not modeled here — see that app's README and `device_actions/registry.py` for how to add a new fetchable feature without touching this app.

## 5. Integration Guide
`register_device()`/`touch_last_seen()`/`revoke_device()` in `devices/services/device.py` are the only supported way to mutate a `Device` from other apps — go through the service layer, not `Device.objects` directly, so behavior (e.g. what "seen" means) stays centralized.
