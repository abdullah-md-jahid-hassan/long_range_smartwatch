from rest_framework.throttling import UserRateThrottle


class GetOtpRateThrottle(UserRateThrottle):
    # UserRateThrottle (unlike AnonRateThrottle) keys authenticated
    # requests by user id instead of no-op'ing them — several OTP
    # purposes require auth (password_change, change_email, ...), and
    # AnonRateThrottle silently skipped the get_otp cap for those callers.
    scope = "get_otp"
