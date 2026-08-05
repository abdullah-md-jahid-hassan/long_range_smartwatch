# Device Actions Module

## 1. Overview
`device_actions` is the Feature Registry + connector seam described in `documentation/plan/main_plan.md` §5.1/§5.2. It is what makes the console's admin panel, and later the watch-facing API, call *the same code* to run a feature — neither one ever branches on `feature_key` directly.

Three pieces:
1. **Registry** (`registry.py`) — a static `FEATURES: dict[str, FeatureSpec]`. Adding a feature (or another message source) is adding an entry here, not new plumbing.
2. **`ActionRequest` / `FeatureSchedule` models** — the audit trail (who triggered what, when, with what result) and the per-device auto-interval config.
3. **Connector** (`connectors.py`) — the transport. `PlaceholderConnector` is what's active today (no mobile app exists yet); it resolves every request honestly and immediately as `no_app_connected` rather than faking success. A real `FCMConnector` is a drop-in later: implement `BaseDeviceConnector.dispatch()`, register it in `_CONNECTOR_BACKENDS`, flip `DEVICE_CONNECTOR_BACKEND` — nothing else in the codebase changes.

### File Structure
```
device_actions/
├── migrations/
├── docs/README.md
├── services/
│   ├── __init__.py
│   └── actions.py            # trigger_action, submit_action_result, set_feature_schedule, latest_action_for
├── v1/
│   ├── serializers.py
│   ├── urls.py
│   └── views.py               # the phone-facing half of the connector contract
├── choices.py                 # ActionMode, ActionStatus
├── registry.py                 # FeatureSpec, FEATURES, CATEGORIES, MESSAGE_SOURCES
├── connectors.py                # BaseDeviceConnector, PlaceholderConnector, get_connector()
├── models.py                    # ActionRequest, FeatureSchedule
└── admin.py
```

## 2. Feature Registry
Every feature is a `FeatureSpec(key, label, category, description, supports_auto, requires_special_consent, has_facing_option)`. Categories match the console's action grid sections: `basic_info`, `notifications`, `messages`, `calls`, `screen`, `camera`.

**Adding a message source** (e.g. a 5th chat app): add one `(source_key, "Display Name")` tuple to `MESSAGE_SOURCES` in `registry.py`. The feature entry, the console card, and the trigger/schedule endpoints all pick it up automatically — no other file changes.

**Adding an unrelated new feature**: add one `FeatureSpec(...)` to `_STATIC_FEATURES`. Same effect.

## 3. Service layer
```python
from device_actions.services import trigger_action
from device_actions.choices import ActionMode

action_request = trigger_action(
    device=device,
    feature_key="basic_info.battery",
    mode=ActionMode.MANUAL,
    triggered_by=request.user,   # None for auto-scheduled / future watch-triggered runs
)
```
`trigger_action()` is the one entry point every caller uses — the console today, the watch API in Phase 2. It creates the `ActionRequest` audit row, then hands off to whatever connector `settings.DEVICE_CONNECTOR_BACKEND` names.

## 4. API — base path `/v1/devices/actions/`
These are the **phone-facing** half of the connector contract — not called by anything yet (no mobile app to call them), but real and testable today (simulate the app with curl/Postman) rather than documented-but-unbuilt.

| Method | Path | Purpose |
|---|---|---|
| POST | `/v1/devices/actions/<device_uuid>/<action_id>/result/` | Phone resolves a dispatched `ActionRequest` — `{"success": true, "result": {...}}` or `{"success": false, "error_message": "..."}`. Ownership-checked: only the owning device can resolve its own request. |
| GET | `/v1/devices/actions/<device_uuid>/schedules/` | Phone pulls its own enabled auto-interval config and self-schedules locally (WorkManager/AlarmManager) — the server never runs a per-device cron for "automatic" mode. |

There is deliberately **no** `POST .../trigger/` endpoint in this API — nothing outside the codebase should be able to trigger a feature yet (per `CONTEXT.md` §3.1, the watch API is explicitly deferred until watch hardware/protocol exists). The console calls `trigger_action()` as a plain Python function from `console/views.py`, not over HTTP.

## 5. Consent boundary
`requires_special_consent=True` (screen/remote-control/camera/audio features) is a registry flag today, surfaced in the console as a "Special consent required" tag. It becomes load-bearing once the mobile app exists: those features must additionally check a per-device `FeatureConsent` toggle before a real connector is allowed to dispatch to the phone (main_plan.md's hard boundary — the gate ships with the capability, not after it). That model is not yet built; this note exists so it isn't dropped when `FCMConnector` lands.
