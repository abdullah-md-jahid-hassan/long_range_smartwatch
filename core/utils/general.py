from rest_framework import status
from core.utils.response import error_response
from rest_framework.response import Response
from typing import Any

def get_or_400(
    data: dict,
    keys: list[str],
    required: list[str] | None = None,
    required_together: list[list[str]] | None = None,
)-> tuple[bool, Response | dict]:
    """
    Extract and validate request data.

    Responsibilities:
    1. Extract values for the given `keys` from `data`.
    2. Enforce presence of individually required fields (`required`).
    3. Enforce grouped requirement rules (`required_together`), where at least
       one field from each group must be present.
    4. Return a standardized (status_code, payload) tuple suitable for DRF views.

    Design notes:
    - Uses set operations for O(1) membership checks.
    - Avoids redundant loops and unnecessary state flags.
    - Keeps validation order explicit and predictable.
    """

    required_set = set(required or [])
    values: dict[str, object] = {}
    missing_required: list[str] = []

    # Extract values and validate individually required fields
    for key in keys:
        value = data.get(key)
        if key in required_set and value is None:
            missing_required.append(key)
        else:
            values[key] = value

    if missing_required:
        return (
            False,
            error_response(
                message=f"Missing required field(s): {', '.join(missing_required)}",
                status_code=status.HTTP_400_BAD_REQUEST,
            ),
        )

    # Validate grouped requirements (at least one field per group)
    if required_together:
        present_keys = {k for k, v in values.items() if v is not None}

        for group in required_together:
            if not present_keys.intersection(group):
                return (
                    False,
                    error_response(
                        message=f"Field(s): {' or '.join(group)} is required",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    ),
                )

    return True, values



def availability_check(data: dict)->tuple:
    missing_keys = []
    for key, value in data.items():
        if value is None:
            missing_keys.append(key)
    if missing_keys:
        return False, error_response(
                message=f"Data is not available for: {', '.join(missing_keys).replace(' ', '_').title()}",
                status_code=status.HTTP_400_BAD_REQUEST,
            )
    return True, None


def str_replace_from_dict(text: str, replacements: dict[str, str]) -> str:
    """
    Docstring for str_replace_from_dict
    
    :param text: Description
    :type text: str
    :param replacements: Description
    :type replacements: dict[str, str]
    :return: Description
    :rtype: str
    """
    for key, value in replacements.items():
        text = text.replace(key, str(value))
    return text


def update_record(qs:object, data: dict[str, Any]) -> object:
    qs.update(**data)
    return qs
 
