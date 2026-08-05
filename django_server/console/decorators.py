from functools import wraps

from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect


def staff_required(view_func):
    """Console has its own session-based staff gate, deliberately separate
    from the JWT auth the phone/watch-facing v1 API uses — these are two
    different authentication realms and shouldn't share a login path."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="console:login")
        if not request.user.is_staff:
            return redirect("console:login")
        return view_func(request, *args, **kwargs)
    return wrapper
