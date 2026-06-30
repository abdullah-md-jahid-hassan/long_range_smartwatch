import uuid
import hmac
from typing import Optional
from datetime import timedelta

from django.conf import settings
from django.utils.crypto import get_random_string

from core.cache.redis_client import redis_client
from core.utils.generators import random_string
from otp.choices import OtpPurpose, OtpChannel
from emails.tasks import send_email_task
from emails.choices import EmailBodyType
from django.template.loader import render_to_string
from django.conf import settings
import hashlib

CONFIG = settings.CONFIG


class OTPService:
    """
    Secure Redis-backed OTP service.

    - Max 5 active OTPs per user per purpose
    - OTP TTL: 5 minutes
    - One-time use
    - OTP stored hashed
    """

    OTP_TTL_SECONDS = CONFIG.OTP_EXPIRY_MINUTES * 60
    MAX_ACTIVE_OTPS = CONFIG.MAX_ACTIVE_OTPS
    MAX_VERIFY_ATTEMPTS = CONFIG.MAX_VERIFY_ATTEMPTS

    @staticmethod
    def _user_hash(user: str) -> str:
        """Return SHA256 hash of user identifier."""
        return hashlib.sha256(user.encode()).hexdigest()

    @staticmethod
    def _hash_otp(otp: str) -> str:
        """Hash OTP before storing."""
        return hashlib.sha256(otp.encode()).hexdigest()

    @classmethod
    def _otp_key(cls, purpose: OtpPurpose, user_hash: str, otp_id: str) -> str:
        """Redis key for a specific OTP."""
        return f"otp:{purpose}:{user_hash}:{otp_id}"

    @classmethod
    def _index_key(cls, purpose: OtpPurpose, user_hash: str) -> str:
        """Redis key storing active OTP ids."""
        return f"otp:index:{purpose}:{user_hash}"

    # ---------------------------------------------------------
    # PUBLIC API
    # ---------------------------------------------------------

    @classmethod
    def generate(cls, user: str, purpose: OtpPurpose) -> str:
        """
        Generate and store a new OTP.

        Ensures max 5 active OTPs per user.
        """

        user_hash = cls._user_hash(user)
        index_key = cls._index_key(purpose, user_hash)

        otp = random_string(
            length=CONFIG.OTP_LENGTH,
            allow_numbers=CONFIG.OTP_ALLOW_NUMBER,
            allow_capital=CONFIG.OTP_ALLOW_CAPITAL,
        )
        otp_hash = cls._hash_otp(otp)
        otp_id = str(uuid.uuid4())

        otp_key = cls._otp_key(purpose, user_hash, otp_id)

        pipe = redis_client.pipeline()

        # Store OTP with TTL
        pipe.set(otp_key, otp_hash, ex=cls.OTP_TTL_SECONDS)

        # Push OTP id to index list
        pipe.rpush(index_key, otp_id)
        pipe.expire(index_key, cls.OTP_TTL_SECONDS)

        pipe.execute()

        # Enforce max active OTPs
        cls._enforce_limit(index_key, purpose, user_hash)

        return otp

    @classmethod
    def verify(cls, user: str, purpose: OtpPurpose, submitted_otp: str) -> bool:
        """
        Verify OTP against active ones.

        Deletes OTP on successful match.
        """

        user_hash = cls._user_hash(user)
        index_key = cls._index_key(purpose, user_hash)

        otp_ids = redis_client.lrange(index_key, 0, -1)

        submitted_hash = cls._hash_otp(submitted_otp)

        for otp_id in otp_ids:
            otp_key = cls._otp_key(purpose, user_hash, otp_id)
            stored_hash = redis_client.get(otp_key)

            if not stored_hash:
                continue

            # Constant-time comparison
            if hmac.compare_digest(stored_hash, submitted_hash):
                cls._delete_otp(index_key, otp_key, otp_id)
                return True

        return False

    # ---------------------------------------------------------
    # INTERNAL HELPERS
    # ---------------------------------------------------------

    @classmethod
    def _delete_otp(cls, index_key: str, otp_key: str, otp_id: str) -> None:
        """Remove OTP from Redis and index."""
        pipe = redis_client.pipeline()
        pipe.delete(otp_key)
        pipe.lrem(index_key, 0, otp_id)
        pipe.execute()

    @classmethod
    def _enforce_limit(cls, index_key: str, purpose: OtpPurpose, user_hash: str) -> None:
        """Ensure only MAX_ACTIVE_OTPS are stored."""
        length = redis_client.llen(index_key)

        if length <= cls.MAX_ACTIVE_OTPS:
            return

        excess = length - cls.MAX_ACTIVE_OTPS

        for _ in range(excess):
            oldest_id = redis_client.lpop(index_key)
            if oldest_id:
                otp_key = cls._otp_key(purpose, user_hash, oldest_id)
                redis_client.delete(otp_key)

    @classmethod
    def send(cls, user: str, purpose: OtpPurpose, channel: OtpChannel) -> None:
        """Send OTP to user."""
        # Get OTP
        otp = cls.generate(user, purpose)
        match channel:
            case OtpChannel.EMAIL:
                from emails.utils.general import send_email_core
                send_email_task.delay(
                    subject="OTP",
                    to_emails=[user],
                    body=render_to_string(
                        "otp_body.html", 
                        {
                            "otp": otp,
                            "purpose": purpose,
                        }
                    ),
                    body_type=EmailBodyType.HTML,
                    purpose=purpose,
                )
            case OtpChannel.PHONE:
                raise NotImplementedError("SMS OTP channel is not yet implemented")
            case _:
                raise ValueError("Invalid OTP channel")
    
