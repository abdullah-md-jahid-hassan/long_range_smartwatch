from otp.choices import OtpPurpose
from django.template.loader import render_to_string
from emails.tasks import send_email_task
from emails.choices import EmailBodyType, EmailPurpose


def send_otp_email(email: str, otp: str, otp_purpose: str = OtpPurpose.OTHER):
    send_email_task.delay(
        subject=f"Your OTP Code",
        to_emails=[email],
        body=render_to_string(
            "otp_body.html",
            {
                "otp": otp,
                "purpose": otp_purpose,
            },
        ),
        body_type=EmailBodyType.HTML,
        purpose=EmailPurpose.OTP,
    )
