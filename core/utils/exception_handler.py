import traceback

from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.exceptions import (
    APIException,
    AuthenticationFailed,
    MethodNotAllowed,
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    Throttled,
    ValidationError,
)
from rest_framework.response import Response
from rest_framework.views import exception_handler


def _friendly_message(exc: APIException) -> str:
    if isinstance(exc, ValidationError):
        return "Validation failed."
    if isinstance(exc, NotAuthenticated):
        return "Authentication credentials were not provided."
    if isinstance(exc, AuthenticationFailed):
        return "Authentication failed."
    if isinstance(exc, PermissionDenied):
        return "You do not have permission to perform this action."
    if isinstance(exc, NotFound):
        return "The requested resource was not found."
    if isinstance(exc, MethodNotAllowed):
        return "Method not allowed."
    if isinstance(exc, Throttled):
        wait = getattr(exc, "wait", None)
        if wait:
            return f"Too many requests. Try again in {int(wait)} second(s)."
        return "Too many requests."
    return "An error occurred."


def _extract_field_errors(data: dict) -> dict | None:
    """
    Return field-level errors only when multiple field keys are present.
    {"detail": "..."} is a non-field error — message alone is sufficient.
    """
    if not isinstance(data, dict) or list(data.keys()) == ["detail"]:
        return None
    return {
        field: [str(m) for m in (msgs if isinstance(msgs, list) else [msgs])]
        for field, msgs in data.items()
    } or None


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        # Non-DRF exception bubbled up — normalize to 500
        payload = {
            "success": False,
            "message": "Internal server error.",
            "data": None,
            "errors": None,
        }
        if settings.DEBUG:
            payload["debug"] = {
                "exception": exc.__class__.__name__,
                "traceback": traceback.format_exc(),
            }
        return Response(payload, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    errors = _extract_field_errors(response.data) if isinstance(exc, ValidationError) else None

    payload = {
        "success": False,
        "message": _friendly_message(exc),
        "data": None,
        "errors": errors,
    }
    if settings.DEBUG:
        payload["debug"] = {
            "exception": exc.__class__.__name__,
            "traceback": traceback.format_exc(),
        }

    response.data = payload
    return response


def handle_404(request, exception=None):
    return JsonResponse(
        {
            "success": False,
            "message": "The requested endpoint does not exist.",
            "data": None,
            "errors": None,
        },
        status=404,
    )


def handle_500(request):
    return JsonResponse(
        {
            "success": False,
            "message": "Internal server error.",
            "data": None,
            "errors": None,
        },
        status=500,
    )
