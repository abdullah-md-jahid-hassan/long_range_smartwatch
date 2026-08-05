from django import template

register = template.Library()

_STATUS_PILL_CLASS = {
    "succeeded": "pill-success",
    "failed": "pill-danger",
    "no_app_connected": "pill-neutral",
    "dispatched": "pill-info",
    "pending": "pill-warning",
}

_STATUS_LABEL = {
    "succeeded": "Success",
    "failed": "Failed",
    "no_app_connected": "Awaiting mobile app",
    "dispatched": "Sent — awaiting device",
    "pending": "Pending",
}


@register.filter
def status_pill_class(status):
    return _STATUS_PILL_CLASS.get(status, "pill-neutral")


@register.filter
def status_label(status):
    return _STATUS_LABEL.get(status, status)


@register.filter
def monogram(label):
    words = [w for w in (label or "").split() if w]
    letters = "".join(w[0] for w in words[:2]).upper()
    return letters or "?"
