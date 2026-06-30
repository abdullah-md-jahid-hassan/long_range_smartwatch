from otp.choices import OtpPurpose, OtpChannel
from dataclasses import dataclass
from django.conf import settings

config = settings.CONFIG


@dataclass(frozen=True)
class OTPPolicy:
    enable: bool # Will this Case is enable or not
    require_auth: bool  # Do we need Authentication?
    check_user_exists: bool # Do we need to check user existence?
    allow_duplicate: bool # Do we need to allow duplicate?
    require_identifier: bool# Do we need to require identifier?
    channel: OtpChannel = config.OTP_CHANNEL  # What is the channel of OTP?


def _assign_value(
    enable: bool,
    require_auth: bool,
    check_user_exists: bool,
    allow_duplicate: bool,
    require_identifier: bool, 
) -> OTPPolicy:
    return OTPPolicy(
        enable=enable,
        require_auth=require_auth,
        check_user_exists=check_user_exists,
        allow_duplicate=allow_duplicate,
        require_identifier=require_identifier,
    )

def get_otp_rules(purpose: OtpPurpose) -> OTPPolicy:
    match purpose:
        case OtpPurpose.LOGIN:
            return _assign_value(False, False, True, True, True)
        case OtpPurpose.REGISTRATION:
            return _assign_value(True, False, False, False, True)
        case OtpPurpose.PASSWORD_CHANGE:
            return _assign_value(False, True, True, True, False)
        case OtpPurpose.PASSWORD_RESET:
            return _assign_value(True, False, False, True, True)
        case OtpPurpose.CHANGE_EMAIL:
            return _assign_value(True, True, True, True, False)
        case OtpPurpose.CHANGE_PHONE:
            return _assign_value(False, True, True, True, False)
        case OtpPurpose.CHANGE_USERNAME:
            return _assign_value(False, True, True, True, False)
        case OtpPurpose.VERIFICATION:
            return _assign_value(False, True, True, True, False)
    raise ValueError(f"Invalid OTP purpose: {purpose}")
    

    
    

    