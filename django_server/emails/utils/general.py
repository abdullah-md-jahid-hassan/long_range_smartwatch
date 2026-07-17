from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import transaction
from emails.models import EmailLog
from emails.choices import EmailStatus
from emails.serializers import (
    EmailLogSerializer, 
)
from emails.choices import (
    EmailBodyType,
    EmailPurpose,
)

def send_email_core(
    *,
    subject: str,
    to_emails: list[str],
    bcc: list[str] = None,
    from_email: str = settings.DEFAULT_FROM_EMAIL,
    body: str = "",
    body_type: EmailBodyType = EmailBodyType.HTML,
    email_log_id: int = None,
    purpose: EmailPurpose = EmailPurpose.OTHERS,
    ):
    """
    Send email core function.

    Parameters:
        from_email (str): From email address.
        to_emails (list[str]): To email address.
        subject (str): Email subject.
        body (str): Email body.
        body_type (EmailBodyType): Email body type.
        email_log_id (int): Email log id.
        purpose (EmailPurpose): Email purpose.

    """
    email_log = None

    if email_log_id:
        try:
            email_log = EmailLog.objects.get(id=email_log_id)
            email_log.try_count += 1
            email_log.save(update_fields=["try_count"])
        except EmailLog.DoesNotExist:
            pass

    if not email_log:
        log_serializer = EmailLogSerializer(
            data={
                "from_email": from_email,
                "to_emails": ",".join(to_emails),
                "bcc": ",".join(bcc) if bcc else None,
                "subject": subject,
                "body": body,
                "body_type": body_type,
                "purpose": purpose,
            }
        )
        log_serializer.is_valid(raise_exception=True)
        email_log = log_serializer.save()

    def _send():
        email = EmailMultiAlternatives(
            subject=subject,
            body=body if body_type == EmailBodyType.TEXT else "",
            from_email=from_email,
            to=to_emails,
            bcc=bcc,
        )
        if body_type == EmailBodyType.HTML:
            email.attach_alternative(body, "text/html")

        email.send()

        EmailLog.objects.filter(id=email_log.id).update(
            status=EmailStatus.SENT
        )

    transaction.on_commit(_send)

