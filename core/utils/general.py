from rest_framework import status
from core.utils.response import error_response
from rest_framework.response import Response
from typing import Any



def _expected_type_name(data_type: type | tuple[type, ...]) -> str:
    """Human-readable name of an expected type (or tuple of types)."""
    if isinstance(data_type, tuple):
        return " or ".join(t.__name__ for t in data_type)
    return data_type.__name__


def get_or_400(
    data: dict,
    keys: dict[str, type | tuple[type, ...] | None],
    required: list[str] | None = None,
    required_together: list[list[str]] | None = None,
)-> tuple[bool, Response | dict]:
    """
    Extract and validate request data.

    Responsibilities:
    1. Extract values for the given `keys` from `data`. Each key maps to an
       expected type (or tuple of types) checked with isinstance; map to
       None to skip type checking for that field.
    2. Enforce presence of individually required fields (`required`).
    3. Enforce grouped requirement rules (`required_together`), where at least
       one field from each group must be present.
    4. Return `(True, values_dict)` on success or `(False, Response)` where
       the Response is a ready-to-return 400 error.

    Design notes:
    - Uses set operations for O(1) membership checks.
    - Type checks apply only to present (non-None) values.
    - Keeps validation order explicit and predictable.
    """

    required_set = set(required or [])
    values: dict[str, object] = {}
    missing_required: list[str] = []
    wrong_data_types: list[str] = []

    # Extract values and validate individually required fields
    for name, data_type in keys.items():
        value = data.get(name)
        if name in required_set and value is None:
            missing_required.append(name)
        elif data_type and value is not None and not isinstance(value, data_type):
            wrong_data_types.append(f'"{name}" must be of type {_expected_type_name(data_type)}')
        else:
            values[name] = value

    error_parts = []
    if missing_required:
        error_parts.append(f"Missing required field(s): {', '.join(missing_required)}")
    if wrong_data_types:
        error_parts.append(f"Wrong data type(s): {', '.join(wrong_data_types)}")
    if error_parts:
        return False, error_response(
            message="; ".join(error_parts),
            status_code=status.HTTP_400_BAD_REQUEST,
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
 
