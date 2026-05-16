from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import get_user_model

User = get_user_model()


def change_password(user: User, new_password: str) -> User:
    validate_password(new_password, user=user)
    user.set_password(new_password)
    user.save(update_fields=["password"])
    return user


def reset_password(email: str, new_password: str) -> User:
    """
    Set a new password for the user identified by email.
    Call this only after OTP verification is confirmed.
    """
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        from rest_framework import serializers
        raise serializers.ValidationError("No account found with this email address.")

    return change_password(user, new_password)
