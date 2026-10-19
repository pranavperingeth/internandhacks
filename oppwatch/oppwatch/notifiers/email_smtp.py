"""SMTP email notifier: sends digest via email."""

from email.message import EmailMessage
import logging
import smtplib

from oppwatch.config import get_env

logger = logging.getLogger(__name__)


def send(text: str) -> bool:
    """Send digest email using SMTP. Return True only if delivery succeeded."""
    host = get_env("SMTP_HOST")
    port_str = get_env("SMTP_PORT", "587")
    user = get_env("SMTP_USER")
    password = get_env("SMTP_PASSWORD")
    email_to = get_env("EMAIL_TO")

    if not host or not user or not password or not email_to:
        logger.error("Email notifier: missing SMTP configuration in environment variables")
        return False

    try:
        port = int(port_str)
        msg = EmailMessage()
        msg["Subject"] = "Weekly Opportunities"
        msg["From"] = user
        msg["To"] = email_to
        msg.set_content(text)

        with smtplib.SMTP(host, port, timeout=30) as server:
            server.starttls()
            server.login(user, password)
            server.send_message(msg)
        return True
    except Exception as exc:
        logger.error("Email send failed: %s", exc)
        return False
