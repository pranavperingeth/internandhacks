"""HTTP helper with retries, User-Agent, and rate limiting."""

import logging
import time

import requests

USER_AGENT = "oppwatch/0.1 (personal weekly digest; contact: set-your-email)"

logger = logging.getLogger(__name__)


def get(
    url: str,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: int = 20,
    retries: int = 2,
    delay: float = 1.0,
) -> requests.Response:
    """GET with User-Agent, timeout, and retries. Sleep `delay` seconds before each request."""
    final_headers = {"User-Agent": USER_AGENT}
    if headers:
        final_headers.update(headers)
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            resp = requests.get(url, params=params, headers=final_headers, timeout=timeout)
            if resp.status_code >= 500:
                logger.warning("Attempt %d: %s returned %d", attempt, url, resp.status_code)
                last_exc = requests.HTTPError(f"Server error {resp.status_code}", response=resp)
                continue
            resp.raise_for_status()
            return resp
        except requests.ConnectionError as exc:
            logger.warning("Attempt %d: connection error for %s: %s", attempt, url, exc)
            last_exc = exc
        except requests.Timeout as exc:
            logger.warning("Attempt %d: timeout for %s: %s", attempt, url, exc)
            last_exc = exc
        except requests.HTTPError:
            raise
    raise last_exc  # type: ignore[misc]


def post(
    url: str,
    json_body: dict | None = None,
    headers: dict | None = None,
    timeout: int = 20,
    retries: int = 2,
    delay: float = 1.0,
) -> requests.Response:
    """POST with User-Agent, timeout, and retries. Sleep `delay` seconds before each request."""
    final_headers = {"User-Agent": USER_AGENT}
    if headers:
        final_headers.update(headers)
    last_exc: Exception | None = None
    for attempt in range(1, retries + 1):
        time.sleep(delay)
        try:
            resp = requests.post(url, json=json_body, headers=final_headers, timeout=timeout)
            if resp.status_code >= 500:
                logger.warning("Attempt %d: POST %s returned %d", attempt, url, resp.status_code)
                last_exc = requests.HTTPError(f"Server error {resp.status_code}", response=resp)
                continue
            resp.raise_for_status()
            return resp
        except requests.ConnectionError as exc:
            logger.warning("Attempt %d: connection error for POST %s: %s", attempt, url, exc)
            last_exc = exc
        except requests.Timeout as exc:
            logger.warning("Attempt %d: timeout for POST %s: %s", attempt, url, exc)
            last_exc = exc
        except requests.HTTPError:
            raise
    raise last_exc  # type: ignore[misc]
