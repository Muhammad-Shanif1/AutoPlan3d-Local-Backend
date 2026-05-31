import random
from typing import Optional, Callable
from fastapi import BackgroundTasks
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr
import logging
from services.settings import settings

# Build connection configuration from `settings` (must expose MAIL_* variables)
def _build_mailer() -> Optional[FastMail]:
    """Build and return a FastMail instance or None if config is incomplete.

    This avoids constructing a ConnectionConfig at import time which will raise
    a Pydantic ValidationError when environment variables are not set.
    """

    mail_username = getattr(settings, "MAIL_USERNAME", None)
    mail_password = getattr(settings, "MAIL_PASSWORD", None)
    mail_from = getattr(settings, "MAIL_FROM", None)
    mail_port = getattr(settings, "MAIL_PORT", 587)
    mail_server = getattr(settings, "MAIL_SERVER", None)

    # If no mail server is configured, skip building the mailer (no-op send).
    if not mail_server or not mail_from:
        return None

    conf = ConnectionConfig(
        MAIL_USERNAME=mail_username,
        MAIL_PASSWORD=mail_password,
        MAIL_FROM=mail_from,
        MAIL_PORT=mail_port,
        MAIL_SERVER=mail_server,
        MAIL_STARTTLS=True,
        MAIL_SSL_TLS=False,
        USE_CREDENTIALS=bool(mail_username and mail_password),
        VALIDATE_CERTS=True,
    )

    try:
        return FastMail(conf)
    except Exception:
        return None


_mailer_instance: Optional[FastMail] = None
def _get_mailer() -> Optional[FastMail]:
    global _mailer_instance
    if _mailer_instance is None:
        _mailer_instance = _build_mailer()
    return _mailer_instance


def generate_otp() -> str:
    """Return a random 6-digit numeric OTP as a string."""
    return f"{random.randint(100000, 999999)}"


def send_otp_email(
    email_to: EmailStr,
    background_tasks: BackgroundTasks,
    save_callback: Optional[Callable[[str, str], None]] = None,   
    subject: str = "Your Registration OTP",
    expires_minutes: int = 10,
) -> str:
    """
    Generate an OTP, queue the email to be sent in the background, and return the OTP.

    Args:
      email_to: recipient email address.
      background_tasks: FastAPI BackgroundTasks instance.
      save_callback: optional callable to persist the OTP (signature: fn(email, otp)).
      subject: email subject.
      expires_minutes: human-facing expiration time included in the message.

    Returns:
      The generated OTP string.
    """

    otp = generate_otp()

    html = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Your verification code is: <b>{otp}</b></p>
            <p>This code will expire in {expires_minutes} minutes.</p>
        </body>
    </html>
    """

    message = MessageSchema(
        subject=subject,
        recipients=[email_to],
        body=html,
        subtype=MessageType.html,
    )

    # Optionally persist OTP (e.g., DB or cache) before sending
    if save_callback:
        try:
            save_callback(email_to, otp)
        except Exception:
            # Do not block sending if persistence fails; caller may handle logging
            pass

    # Queue the send call; FastMail.send_message is async so pass it to background tasks
    mailer = _get_mailer()
    if mailer is None:
        logging.warning(
            "Email not sent: mailer not configured (MAIL_SERVER or MAIL_FROM missing)"
        )
        return {
            "otp": otp,
            "mail_sent": False,
            "message": (
                "OTP generated, but email was not sent because SMTP settings are missing. "
                "Check MAIL_SERVER and MAIL_FROM in services/.env."
            ),
        }

    background_tasks.add_task(mailer.send_message, message)
    return {"otp": otp}


__all__ = ["generate_otp", "send_otp_email"]   # it means that when we import * from this module, only these two functions will be imported.
