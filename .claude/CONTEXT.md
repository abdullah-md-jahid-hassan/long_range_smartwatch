# Project Context: Internet-Relayed Smartwatch Platform

**Document purpose:** This is the single source of truth for what this project is, why it's built the way it is, and what phase of development we are currently in. Any contributor (including future-you) should be able to read this document and understand the full picture without needing prior conversation history.

---

## 1. What This Project Is About

### 1.1 The Core Problem
Traditional smartwatches pair with a phone over **Bluetooth**. Bluetooth's range is limited to roughly 10 meters (in practice often less). The moment the watch and phone are separated beyond that range — different rooms, different floors, different buildings, or the watch owner leaves the phone at home entirely — the watch loses its connection to the phone and stops receiving notifications, call alerts, messages, or any other phone-dependent data.

### 1.2 The Core Idea
Replace the direct Bluetooth radio link with an **internet-relayed connection**. Instead of the watch and phone talking to each other directly, both devices talk to a central **relay server** over the internet (Wi-Fi or mobile data on either side). The server acts as a trusted middleman that:

- Accepts data the phone wants to share (notifications, call logs, messages, sensor data, etc.)
- Accepts requests/instructions originating from the watch
- Forwards those requests to the correct paired phone
- Relays the phone's response back to the correct watch

Because the link no longer depends on physical radio proximity, **the watch and phone can be on opposite sides of the planet and still stay in sync**, as long as both have an internet connection.

### 1.3 The Business Vision
This isn't just a personal project — the long-term goal is to **build a smartwatch company** around this concept. The relay-over-internet architecture is the company's core technical differentiator versus traditional Bluetooth-only smartwatches. The product will eventually include:

- A companion **mobile app** (installed on the user's phone)
- A **smartwatch** (custom hardware, still in the design/sourcing/protocol-decision stage)
- A **cloud relay server/platform** that connects the two and provides admin/fleet management tooling

---

## 2. What We Are Going To Do (Overall Roadmap)

### Phase 1 — Software-First, No Hardware Yet (current phase — see Section 3)
Since no smartwatch hardware exists yet, and its design/protocol is undecided, we build everything that *can* be built without it: the server-side service layer and phone-side app, validated through a temporary human-operated admin panel that stands in for the watch.

### Phase 2 — API Layer for the Real Watch
Once the smartwatch's hardware, firmware, communication protocol, and form factor are finalized, we will build a **dedicated API layer** on top of the already-built service layer, tailored to however the real watch communicates (e.g., REST calls, WebSocket, MQTT, or a custom protocol depending on what the watch hardware/firmware supports). The watch becomes a live client of the same services the admin panel currently exercises.

### Phase 3 — Replace Simulation With Real Hardware
The temporary admin-panel action console is swapped out (or kept, in a reduced/monitoring-only form — see Section 5.4) as the actual watch becomes the thing triggering requests. No changes should be required to the phone app or the core service layer at this point — this is the payoff of building the service layer to be client-agnostic from day one.

### Phase 4 — Company/Product Hardening
Multi-tenant support, per-customer device fleets, permission groups and role-based admin access, billing/subscription tiers if applicable, and production-grade security, monitoring, and compliance.

---

## 3. What We Are Currently Doing (Phase 1 — Current Scope)

### 3.1 Explicit Decision: No Smartwatch, No Watch-Facing API Yet
**We are deliberately NOT building any smartwatch-facing API endpoints right now.** This is an intentional decision, not an oversight:

- The smartwatch's hardware, industrial design, and communication protocol are still under active design/decision.
- We do not yet know whether the eventual watch will talk to the server via plain REST, WebSocket, MQTT, or something else entirely — that depends on hardware/firmware choices not yet made.
- Building an API endpoint shaped around assumptions we might reverse later would mean throwaway work.

Instead, the current build order is:

1. **Build the service layer first.** Every action the system needs to perform (toggle live notifications, fetch notifications, fetch call history, fetch messages, initiate screen viewing, initiate remote access, etc.) is implemented as an internal Python/Django **service/function**, independent of any particular API shape or caller.
2. **Put a human-operated admin panel on top of those services**, for this phase only. The admin panel's UI buttons call the exact same service functions that a future watch API endpoint will eventually call. A person clicking "Fetch Notifications" in the admin panel exercises precisely the same code path a real watch's request will exercise later.
3. **Defer API endpoint design until the watch's protocol is known.** Once the hardware/protocol decisions are locked in, we build a thin API layer (REST/WebSocket/etc., whatever fits) that simply calls into the already-tested, already-working service layer. The service layer itself should require little to no modification at that point.

This means the admin panel is not just a demo — it is the **de facto integration test harness** for every service function before any real device depends on it.

### 3.2 What's In Scope Right Now
- **Django + Django REST Framework** backend implementing the service layer described above.
- **Django Channels** (or equivalent) for real-time, low-latency delivery of instructions to the phone app and responses back to the admin panel — chosen instead of plain polling to avoid battery drain and lag.
- **Admin panel** (server-rendered or lightweight frontend) with three core views, based on the wireframes already produced:
  - **Home dashboard** — fleet-level stats: total connected devices, online device count, total admins, total permission groups, and a global recent-activity feed.
  - **Devices registry** — sortable/filterable list of all paired devices (device ID, added date, online status, last-seen, connection state, server IP for provisioning).
  - **Device Detail / action console** — per-device info panel plus an action button grid (see 3.3) and a per-device activity log.
- **Mobile app** (Flutter, cross-platform) that:
  - Requests standard, user-consented runtime permissions (notifications access, call log, SMS/messages, etc.) — **not root access**. The user sees exactly what's being requested via native OS permission dialogs and can accept or deny each one; the app only functions within whatever the user has explicitly granted.
  - Maintains a persistent or push-triggered connection to the server (via Firebase Cloud Messaging for wake-on-instruction delivery, to avoid constant background polling and battery drain).
  - Executes whatever instruction the server forwards to it (e.g., "send current notifications") and reports the result back.
- **Attribution and logging**: every action taken through the admin panel is tied to the admin who triggered it, and logged with a timestamp — this is a real audit trail, not just a debug console.
- **Permission groups / role-based access** for admins: not every admin should necessarily be able to trigger every action (e.g., remote screen control might be restricted to a smaller admin group than "view notifications"). This needs to be explicitly modeled rather than defaulted to "all admins can do everything."

### 3.3 Current Action Set (Service Functions)
Based on the wireframe for the Device Detail screen, the following service functions are the initial target set. Each corresponds to one admin-panel button today, and will correspond to one watch-triggered request later:

| Action | Description |
|---|---|
| Toggle Live Notification | Turn real-time notification forwarding on/off for a device |
| Fetch Notifications | Pull the current notification list from the phone |
| See Live Screen | Stream/mirror the phone's current screen (view-only) |
| Initiate Remote Access | Take control of the phone remotely (input/gestures), not just view |
| See Notification Log | Retrieve historical notification log |
| See Missed Calls & Call History | Retrieve call history and missed-call list |
| See Messages | Retrieve SMS/message content |

Note: "Initiate Remote Access" appears twice in the original wireframe — this should be clarified/split into two distinct actions: **view-only screen mirroring** (lower-risk, simpler permission) vs. **full remote control** (input simulation via Accessibility Service — higher-risk, requires explicit, separately justified user consent and stricter app-store review).

### 3.4 Explicitly Out of Scope Right Now
- Any smartwatch hardware, firmware, or watch-specific communication protocol.
- Any API endpoint designed specifically for the watch to call.
- Physical device pairing/provisioning flows that assume specific watch hardware.

---

## 4. Technical Notes & Clarifications Carried Over From Design Discussion

- **"Root access" was a misunderstanding worth permanently recording:** rooting a phone means bypassing the OS's own security model entirely, is done by the device owner outside of any app, cannot be requested as an app permission, and is rejected by app stores as an installation requirement. What we actually want — broad, user-consented access to phone data categories — is fully achievable through the **standard runtime permission system** (the same "Allow/Deny" dialogs every Android/iOS app uses), with no root involved.
- **Remote control (viewing/controlling the phone screen from the watch, "AnyDesk-style") is achievable but requires two special, heavier permissions**, distinct from normal runtime permissions:
  - **Accessibility Service** — enables reading screen content and simulating taps/gestures; requires manual enabling in system settings (not a one-tap dialog) and stricter Play Store review/justification, since it's a common malware vector.
  - **MediaProjection** — enables screen capture/streaming; requires a one-time special system dialog.
  Both are fully legitimate with proper user consent (this is how real remote-support apps work), but they are a heavier, separate integration path from the rest of the permission set and should be scoped/reviewed accordingly.
- **Why Django Channels / WebSockets (or push notifications) instead of polling:** constant polling from the phone app would drain battery and add latency. A persistent connection or push-wake mechanism (FCM) lets the server deliver instructions to the phone in near real time, only when there's actually something to deliver.
- **Design principle for future-proofing:** the admin panel must call services through the *same internal contract* a real watch API will use later, so that swapping the admin panel's action console for real watch firmware in Phase 2/3 requires no changes to the phone app or the service layer — only a new, thin API surface.

---

## 5. Additional Feature Ideas (Proposed — Not Yet Decided)

These are suggestions to consider for the roadmap, beyond what's already been discussed. None of these are commitments — they're options to evaluate as the product matures.

### 5.1 Watch-side quality-of-life features
- **Quick reply to messages/calls** — canned or dictated short replies sent from the watch, relayed through the server to the phone to actually send.
- **Do Not Disturb sync** — toggling silent/DND mode on the watch mirrors it on the phone and vice versa.
- **Media/music control** — play/pause/skip/volume for whatever's playing on the phone.
- **Find My Phone** — trigger a loud sound/vibration on the phone from the watch (useful even over the internet, e.g., phone lost somewhere in the house while the watch is with the user).
- **Battery & connectivity status** — show the phone's battery level, signal strength, and Wi-Fi status on the watch face or a dedicated screen.
- **Remote camera shutter** — use the phone as a remote camera trigger, with a live or delayed preview relayed to the watch.
- **Calendar/agenda glance** — pull upcoming calendar events to the watch.
- **Weather glance** — relay phone-side location + a weather API result to the watch (or fetch independently if the watch has its own connectivity).

### 5.2 Safety / emergency features
- **SOS trigger** — a watch-side emergency button that, via the server, can trigger the phone to send location + an alert message to predefined emergency contacts.
- **Fall/inactivity detection relay** — if the watch has motion sensors, anomalous readings could be relayed through the server to trigger phone-side alerts.
- **Geofencing alerts** — notify the watch (or a linked account, e.g., a parent's account) when the phone/watch pair leaves or enters a defined zone.

### 5.3 Admin/company-side platform features
- **Fine-grained role-based access control (RBAC)** — beyond a flat "admin" role, define permission groups with specific allowed actions (e.g., "support agent" can view logs but not initiate remote access; "senior admin" can do everything).
- **Device health monitoring** — surface connectivity drops, battery health, and last-sync gaps proactively on the dashboard rather than requiring manual lookup.
- **Data retention & privacy controls** — configurable retention windows for notification/message/call logs relayed through the server, plus a way for end users to view/export/delete their own data (useful both ethically and for future compliance needs, e.g., GDPR-style regimes).
- **End-to-end encryption in transit** — since sensitive data (messages, call logs, screen content) passes through a third-party relay server, encrypting payloads so the server itself cannot read the content (only route it) would be a strong trust/privacy differentiator for a smartwatch *company*.
- **Offline queuing** — if the phone is briefly offline when a request comes in, queue it server-side and deliver once the phone reconnects, rather than failing the request outright.
- **Rate limiting & abuse protection** — especially important for actions like remote access; prevent runaway or malicious request floors from a compromised admin account or watch.
- **Audit trail export** — the existing per-action admin log is a great foundation; consider making it exportable/searchable for support and compliance purposes as the user base grows.
- **Multi-watch-per-account support** — allow one phone to be paired with more than one watch (e.g., a user's own watch plus a family member's), which the current schema (device registry with device IDs) already seems to anticipate.

### 5.4 On the admin panel's long-term role
Even after real watch hardware exists, the admin panel doesn't have to disappear — it's valuable to keep (in a reduced or reworked form) as:
- A **support/debugging tool** for your team to diagnose a specific customer's device issues.
- A **fleet monitoring dashboard** for the company's operational health, separate from the end-user-facing watch experience.

---

## 6. Summary

| Question | Answer |
|---|---|
| What is this? | A smartwatch platform where the watch and phone connect over the internet via a relay server instead of Bluetooth, removing range limits |
| What's the end goal? | A smartwatch company built around this internet-relay architecture |
| What are we building right now? | The server-side service layer (Django/DRF/Channels) + a human-operated admin panel that simulates the watch by calling those same services, + a Flutter mobile app with standard runtime permissions |
| What are we explicitly NOT building yet? | Any smartwatch-facing API endpoint, or anything assuming specific watch hardware/protocol |
| Why not build the watch API yet? | The watch's hardware, design, and communication protocol are still undecided, so we don't yet know what shape that API needs to take |
| What happens when the watch is ready? | A thin API layer is added on top of the already-built, already-tested service layer, tailored to whatever protocol the real watch uses — the phone app and core services shouldn't need to change |
