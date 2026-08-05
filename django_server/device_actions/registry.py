"""
Single source of truth for "what features exist" (main_plan.md §5.1). Both
the admin panel today and the watch-facing API later read this same
registry instead of branching on feature_key throughout the codebase —
adding a feature is adding an entry here, not new plumbing.
"""
from dataclasses import dataclass, field


@dataclass(frozen=True)
class FeatureSpec:
    key: str
    label: str
    category: str
    description: str
    supports_auto: bool = True
    # Special access (Accessibility Service / MediaProjection / camera+mic),
    # as opposed to a standard one-tap runtime permission dialog — see
    # main_plan.md §3's legend for why this distinction matters.
    requires_special_consent: bool = False
    has_facing_option: bool = False


CATEGORIES: dict[str, str] = {
    "basic_info": "Basic Info",
    "notifications": "Notifications",
    "messages": "Messages",
    "calls": "Calls",
    "screen": "Screen & Remote",
    "camera": "Camera & Audio",
}

# Add a (key, label) tuple here to support another message source — nothing
# else in this file, the service layer, or the console templates changes.
MESSAGE_SOURCES: list[tuple[str, str]] = [
    ("sms", "SMS"),
    ("whatsapp", "WhatsApp"),
    ("imo", "Imo"),
    ("gmail", "Gmail"),
]


def _message_features() -> list[FeatureSpec]:
    features = []
    for source_key, source_label in MESSAGE_SOURCES:
        if source_key == "sms":
            description = "Last N SMS messages, read from the native SMS provider (full content)."
        else:
            description = (
                f"Last N captured {source_label} notification events, going forward from when "
                f"forwarding was enabled — not a retroactive chat history dump (see main_plan.md §3)."
            )
        features.append(FeatureSpec(
            key=f"messages.{source_key}",
            label=f"{source_label} Messages",
            category="messages",
            description=description,
            supports_auto=True,
        ))
    return features


_STATIC_FEATURES: list[FeatureSpec] = [
    FeatureSpec("basic_info.battery", "Battery Level", "basic_info", "Current battery percentage."),
    FeatureSpec("basic_info.lock_state", "Lock State", "basic_info", "Locked or unlocked, and for how long."),
    FeatureSpec("basic_info.location", "Location", "basic_info", "Current device location."),
    FeatureSpec("notifications.fetch", "Fetch Notifications", "notifications", "Pull the current notification list — app, time, content."),
    FeatureSpec("notifications.live_toggle", "Live Notification Forwarding", "notifications", "Turn real-time notification forwarding on or off.", supports_auto=False),
    FeatureSpec("calls.history", "Call History", "calls", "Last N calls with caller detail."),
    FeatureSpec("screen.screenshot", "Screenshot", "screen", "One-off capture of the current screen.", supports_auto=False, requires_special_consent=True),
    FeatureSpec("screen.live_view", "Live Screen (view only)", "screen", "Stream the current screen — no input.", supports_auto=False, requires_special_consent=True),
    FeatureSpec("screen.remote_control", "Remote Control", "screen", "Full remote input control via Accessibility Service.", supports_auto=False, requires_special_consent=True),
    FeatureSpec("camera.photo", "Take Photo", "camera", "Front or back camera still capture.", supports_auto=False, requires_special_consent=True, has_facing_option=True),
    FeatureSpec("camera.video", "Record Video", "camera", "Front or back camera video, with audio.", supports_auto=False, requires_special_consent=True, has_facing_option=True),
    FeatureSpec("camera.audio", "Record Audio", "camera", "Microphone-only capture.", supports_auto=False, requires_special_consent=True),
]

FEATURES: dict[str, FeatureSpec] = {f.key: f for f in (_STATIC_FEATURES + _message_features())}


def get_feature(key: str) -> FeatureSpec | None:
    return FEATURES.get(key)


def features_by_category() -> dict[str, list[FeatureSpec]]:
    grouped: dict[str, list[FeatureSpec]] = {cat: [] for cat in CATEGORIES}
    for feature in FEATURES.values():
        grouped.setdefault(feature.category, []).append(feature)
    return grouped
