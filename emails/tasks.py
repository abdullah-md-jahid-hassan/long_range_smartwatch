from celery import shared_task
from smtplib import SMTPException
from emails.utils.general import send_email_core

@shared_task(
    bind=True,
    autoretry_for=(SMTPException, ConnectionError),
    retry_kwargs={"max_retries": 3, "countdown": 30},
    retry_backoff=True,)
def send_email_task(self, **kwargs):
    send_email_core(**kwargs)