# Console (Admin Panel)

## 1. Overview
`console` is the Phase 1 stand-in for the watch (`CONTEXT.md` §3.1/§3.2): a staff-only, server-rendered (Django templates) operator UI. Every button in it calls `device_actions.services.trigger_action()` / `set_feature_schedule()` — the exact same functions the watch-facing API will call in Phase 2 — so replacing this UI with real watch hardware later requires no change to the service layer underneath it, only a new caller.

Deliberately dependency-free: no frontend framework, no CDN script. A small vanilla-JS layer (`static/console/js/console.js`) intercepts the two per-feature forms (trigger / schedule) and swaps in the server-rendered partial, so clicking "Fetch Now" doesn't reload the page — but the page works with JS disabled too (full form POST + redirect-free re-render), since progressive enhancement, not a JS framework, is doing the work.

## 2. Auth
Console has its own **session-based** staff gate (`decorators.staff_required`, `auth.ConsoleLoginView`), deliberately separate from the JWT auth the phone/watch-facing `/v1/` API uses. A user must have `is_staff=True` to sign in at `/console/login/` — attempting to log in as a non-staff user rejects with a form error rather than a generic 403 after the fact.

## 3. Pages
| Path | View | Purpose |
|---|---|---|
| `/console/login/` | `ConsoleLoginView` | Staff-only sign-in |
| `/console/` | `dashboard` | Fleet stats + recent activity across all devices |
| `/console/devices/` | `device_list` | Searchable device registry |
| `/console/devices/<uuid>/` | `device_detail` | Device info + the full feature action grid, grouped by category |
| `/console/devices/<uuid>/actions/<feature_key>/trigger/` | `trigger_action_view` | POST-only, AJAX — runs one feature manually |
| `/console/devices/<uuid>/actions/<feature_key>/schedule/` | `update_schedule_view` | POST-only, AJAX — sets auto/manual + interval for one feature |
| `/console/devices/<uuid>/revoke/` | `revoke_device_view` | POST-only — soft-revokes a device |

## 4. Action grid
Rendered from `device_actions.registry.features_by_category()` — the console never hardcodes a feature list. Each card (`templates/console/partials/_action_row.html`) is also the AJAX swap target: both the trigger and schedule forms POST and get back a freshly rendered copy of the same partial, so the card after a click always matches what a full page load would show.

Camera features (`has_facing_option=True`) get an inline front/back selector; `notifications.live_toggle` (the one feature that's a toggle, not a data fetch) gets an on/off selector instead of the usual "Fetch Now" semantics — both are registry-driven, not special-cased in the template beyond checking those two flags/keys.

## 5. What's not here yet
- Role-based access control beyond a flat `is_staff` check (`CONTEXT.md` §3.2/§5.3 — deferred, not forgotten).
- Any of this being exposed to non-staff users — the end user's own device list/actions belong in the eventual mobile app UI and the `devices`/`device_actions` v1 JWT API, not here.
