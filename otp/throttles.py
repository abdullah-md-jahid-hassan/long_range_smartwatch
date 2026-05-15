from rest_framework.throttling import AnonRateThrottle


class GetOtpRateThrottle(AnonRateThrottle):
    scope = "get_otp"
