"""Notifier registry."""

from oppwatch.notifiers import console, telegram, email_smtp

NOTIFIERS = {
    "console": console.send,
    "telegram": telegram.send,
    "email": email_smtp.send,
}
