"""Telegram notifier: sends digest chunks using Telegram Bot API."""

import logging
import requests

from oppwatch.config import get_env
from oppwatch.digest import split_message

logger = logging.getLogger(__name__)


def send(text: str) -> bool:
    """Send text chunks via Telegram Bot API. Return True only if delivery succeeded."""
    token = get_env("TELEGRAM_BOT_TOKEN")
    chat_id = get_env("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logger.error("Telegram notifier: TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID is missing")
        return False

    chunks = split_message(text)
    api_url = f"https://api.telegram.org/bot{token}/sendMessage"

    for chunk in chunks:
        payload = {
            "chat_id": chat_id,
            "text": chunk,
            "disable_web_page_preview": "true",
        }
        try:
            resp = requests.post(api_url, data=payload, timeout=20)
            if resp.status_code != 200:
                logger.error("Telegram send failed with status %d", resp.status_code)
                return False
        except Exception as exc:
            logger.error("Telegram send encountered network error: %s", exc)
            return False

    return True
