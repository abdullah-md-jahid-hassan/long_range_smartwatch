from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.utils.response import success_response, error_response
from core.utils.validators import validate_phone
from otp.choices import OtpPurpose, OtpChannel
from otp.services import OTPService
from otp.services.rules import get_otp_rules
from otp.throttles import GetOtpRateThrottle


class GetOtpView(APIView):
    permission_classes = [AllowAny]
    throttle_classes = [GetOtpRateThrottle]

    def post(self, request):
        # Validate purpose
        purpose = request.data.get("purpose")
        if not purpose or purpose not in OtpPurpose.values:
            return error_response(
                message='"purpose" is required and must be a valid value',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        otp_rules = get_otp_rules(purpose)

        if not otp_rules.enable:
            return error_response(
                message="OTP is not enabled for this purpose",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        if otp_rules.require_auth and not request.user.is_authenticated:
            return error_response(
                message="Authentication required for this OTP purpose",
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        # Resolve user identifier
        user_identifier = request.data.get("user_identifier")
        if otp_rules.require_identifier and not user_identifier:
            return error_response(
                message='"user_identifier" is required for this OTP purpose',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve channel
        otp_channel = otp_rules.channel
        if otp_channel == OtpChannel.ALL:
            otp_channel = request.data.get("otp_channel")
        if not otp_channel:
            return error_response(
                message='"otp_channel" is required',
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Fall back to authenticated user's identifier
        if request.user.is_authenticated and not user_identifier:
            user_identifier = (
                request.user.email
                if otp_channel == OtpChannel.EMAIL
                else getattr(request.user, "phone", None)
            )

        if not user_identifier:
            return error_response(
                message="Could not determine user identifier",
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        # Validate identifier format against channel
        try:
            if otp_channel == OtpChannel.EMAIL:
                validate_email(user_identifier)
            elif otp_channel == OtpChannel.PHONE:
                region = request.data.get("region")
                if not region:
                    return error_response(
                        message='"region" is required for phone OTP',
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )
                validate_phone(user_identifier, region)
            else:
                return error_response(
                    message='"otp_channel" is not valid',
                    status_code=status.HTTP_400_BAD_REQUEST,
                )
        except ValidationError as e:
            return error_response(
                message="Invalid user identifier",
                errors=e,
                status_code=status.HTTP_400_BAD_REQUEST,
            )

        OTPService.send(user=user_identifier, purpose=purpose, channel=otp_channel)

        return success_response(
            message=f"OTP sent successfully. Please check your {otp_channel}. Valid for {5} minutes.",
            status_code=status.HTTP_200_OK,
        )
