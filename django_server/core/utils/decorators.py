from functools import wraps
from rest_framework import status
from rest_framework.permissions import BasePermission
from core.utils.response import error_response

def is_admin(user):
    return bool(
        user
        and user.is_authenticated
        and user.is_staff
    )


class IsAdminUser(BasePermission):
    """
    DRF permission class. Use this on class-based views:
        permission_classes = [IsAdminUser]
    """
    message = "Admin access required."

    def has_permission(self, request, view):
        return is_admin(request.user)


def admin_required(view_func):
    """
    Decorator for function-based views.
    Blocks non-staff users with 403.

    Usage:
        @admin_required
        def my_view(request): ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user or not request.user.is_authenticated:
            return error_response(
                message="Authentication required.",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )
        if not request.user.is_staff:
            return error_response(
                message="Admin access required.",
                status_code=status.HTTP_403_FORBIDDEN,
            )
        return view_func(request, *args, **kwargs)

    return wrapper
