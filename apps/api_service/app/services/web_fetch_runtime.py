from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

import httpx

from apps.api_service.app.core.config import get_settings


@dataclass(slots=True)
class FetchResult:
    url: str
    final_url: str
    status_code: int
    content_type: str
    body: str


class FetchRuntimeError(RuntimeError):
    pass


def fetch_url(url: str, *, allowed_domains: list[str] | None = None) -> FetchResult:
    _validate_domain(url, allowed_domains or [])

    settings = get_settings()
    try:
        with httpx.Client(
            timeout=settings.browser_request_timeout_seconds,
            headers={
                "User-Agent": settings.browser_user_agent,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            },
            proxy=settings.web_proxy_url or None,
            follow_redirects=True,
            trust_env=False,
        ) as client:
            response = client.get(url)
            response.raise_for_status()
    except Exception as exc:
        raise FetchRuntimeError(f"http fetch failed for {url}: {exc}") from exc

    return FetchResult(
        url=url,
        final_url=str(response.url),
        status_code=response.status_code,
        content_type=response.headers.get("Content-Type", "text/html"),
        body=response.text,
    )


def _validate_domain(url: str, allowed_domains: list[str]) -> None:
    if not allowed_domains:
        return
    hostname = (urlparse(url).hostname or "").lower()
    normalized = [domain.lower().lstrip(".") for domain in allowed_domains]
    if any(hostname == domain or hostname.endswith(f".{domain}") for domain in normalized):
        return
    raise FetchRuntimeError(f"domain not allowed for browser fetch: {url}")
