"""Sending email. In development the SMTP server is Mailpit, which shows every message at
http://localhost:8025 and delivers nothing; production points the same settings at a real
provider."""

import logging
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from typing import Protocol

from app.core.config import Settings, get_settings

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class OutgoingEmail:
    to: str
    subject: str
    body: str


class EmailSender(Protocol):
    def send(self, email: OutgoingEmail) -> None: ...


class SmtpEmailSender:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    def send(self, email: OutgoingEmail) -> None:
        settings = self._settings
        message = EmailMessage()
        message["From"] = settings.email_from
        message["To"] = email.to
        message["Subject"] = email.subject
        message.set_content(email.body)

        # Runs as a background task after the response: a mail outage must not fail the
        # request that triggered it, so it is logged instead of raised.
        try:
            with smtplib.SMTP(settings.smtp_host, settings.smtp_port, timeout=10) as smtp:
                if settings.smtp_use_tls:
                    smtp.starttls()
                if settings.smtp_username and settings.smtp_password:
                    smtp.login(settings.smtp_username, settings.smtp_password)
                smtp.send_message(message)
        except (OSError, smtplib.SMTPException):
            logger.exception("Could not send email %r", email.subject)


def get_email_sender() -> EmailSender:
    return SmtpEmailSender(get_settings())


# --- messages (Turkish: these reach the user) ---


def verification_email(to: str, link: str) -> OutgoingEmail:
    hours = get_settings().email_verification_expire_hours
    return OutgoingEmail(
        to=to,
        subject="Harcamam: e-posta adresini doğrula",
        body=(
            "Merhaba,\n\n"
            "Harcamam hesabındaki e-posta adresini doğrulamak için aşağıdaki bağlantıyı aç:\n\n"
            f"{link}\n\n"
            f"Bağlantı {hours} saat geçerlidir. Bu isteği sen yapmadıysan bu e-postayı yok "
            "sayabilirsin.\n\n"
            "Harcamam"
        ),
    )


def email_change_notice(to: str, new_email: str) -> OutgoingEmail:
    return OutgoingEmail(
        to=to,
        subject="Harcamam: e-posta adresi değişikliği talebi",
        body=(
            "Merhaba,\n\n"
            f"Harcamam hesabının e-posta adresini {new_email} olarak değiştirme talebi alındı. "
            "Değişiklik, yeni adres doğrulandığında geçerli olur.\n\n"
            "Bu talebi sen yapmadıysan hemen giriş yapıp şifreni değiştir ve Ayarlar'dan "
            "bekleyen değişikliği iptal et.\n\n"
            "Harcamam"
        ),
    )
