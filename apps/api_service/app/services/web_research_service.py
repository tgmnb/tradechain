from __future__ import annotations

import re
from base64 import urlsafe_b64decode
from dataclasses import dataclass
from html import unescape
from html.parser import HTMLParser
from xml.etree import ElementTree
from urllib.parse import parse_qs, quote_plus, urljoin, urlparse

from apps.api_service.app.core.config import get_settings
from apps.api_service.app.services.web_fetch_runtime import FetchRuntimeError, fetch_url


@dataclass(slots=True)
class SearchCandidate:
    title: str
    url: str


class _AnchorParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.anchors: list[dict[str, str]] = []
        self._current_href: str | None = None
        self._current_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag != "a":
            return
        attrs_map = dict(attrs)
        self._current_href = attrs_map.get("href")
        self._current_text = []

    def handle_data(self, data: str) -> None:
        if self._current_href is None:
            return
        self._current_text.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "a" or self._current_href is None:
            return
        text = re.sub(r"\s+", " ", " ".join(self._current_text)).strip()
        self.anchors.append({"href": self._current_href, "text": text})
        self._current_href = None
        self._current_text = []


def run_web_research(*, query: str, max_results: int | None = None) -> dict:
    settings = get_settings()
    limit = max_results or settings.web_search_result_limit
    normalized_query = _normalize_query(query)
    search_url = _build_search_url(
        normalized_query,
        settings.web_search_base_url,
        provider=settings.web_search_provider,
    )

    try:
        fetched = fetch_url(search_url)
    except FetchRuntimeError as exc:
        return {
            "status": "failed",
            "query": normalized_query,
            "provider": settings.web_search_provider,
            "result_count": 0,
            "results": [],
            "summary": f"网页检索暂时失败：{exc}",
        }

    candidates = _parse_search_results(
        fetched.body,
        limit=limit,
        provider=settings.web_search_provider,
    )

    results: list[dict] = []
    for candidate in candidates[: settings.web_search_fetch_page_limit]:
        try:
            page = fetch_url(candidate.url)
            excerpt = _extract_excerpt(page.body)
            results.append(
                {
                    "title": candidate.title,
                    "url": candidate.url,
                    "excerpt": excerpt,
                }
            )
        except FetchRuntimeError:
            results.append(
                {
                    "title": candidate.title,
                    "url": candidate.url,
                    "excerpt": "",
                }
            )

    summary = _build_summary(query=normalized_query, results=results)
    return {
        "status": "success",
        "query": normalized_query,
        "provider": settings.web_search_provider,
        "result_count": len(results),
        "results": results,
        "summary": summary,
    }


def _build_search_url(query: str, base_url: str, *, provider: str) -> str:
    separator = "&" if "?" in base_url else "?"
    if provider == "bing_html":
        return f"{base_url}{separator}format=rss&q={quote_plus(query)}"
    return f"{base_url}{separator}q={quote_plus(query)}"


def _parse_search_results(body: str, *, limit: int, provider: str) -> list[SearchCandidate]:
    if provider == "bing_html":
        return _parse_bing_rss_results(body, limit=limit)

    parser = _AnchorParser()
    parser.feed(body)

    results: list[SearchCandidate] = []
    seen_urls: set[str] = set()
    for anchor in parser.anchors:
        title = anchor["text"].strip()
        href = anchor["href"].strip()
        if not title or not href:
            continue
        url = _normalize_search_result_url(href)
        if not url or url in seen_urls:
            continue
        if _is_internal_search_link(url, title):
            continue
        seen_urls.add(url)
        results.append(SearchCandidate(title=title, url=url))
        if len(results) >= limit:
            break
    return results


def _parse_bing_rss_results(body: str, *, limit: int) -> list[SearchCandidate]:
    try:
        root = ElementTree.fromstring(body.lstrip())
    except ElementTree.ParseError:
        return []

    results: list[SearchCandidate] = []
    seen_urls: set[str] = set()
    for item in root.findall("./channel/item"):
        title = (item.findtext("title") or "").strip()
        url = (item.findtext("link") or "").strip()
        if not title or not url or url in seen_urls:
            continue
        if _is_internal_search_link(url, title):
            continue
        seen_urls.add(url)
        results.append(SearchCandidate(title=title, url=url))
        if len(results) >= limit:
            break
    return results


def _normalize_search_result_url(href: str) -> str | None:
    if "bing.com/ck/a" in href:
        parsed = parse_qs(urlparse(href).query)
        encoded = parsed.get("u", [None])[0]
        if encoded and encoded.startswith("a1"):
            return _decode_bing_target(encoded[2:])
    if href.startswith("//duckduckgo.com/l/?") or href.startswith("https://duckduckgo.com/l/?"):
        parsed = parse_qs(urlparse(href.replace("//duckduckgo.com", "https://duckduckgo.com", 1)).query)
        target = parsed.get("uddg", [None])[0]
        return unescape(target) if target else None
    if href.startswith("//"):
        return f"https:{href}"
    if href.startswith("/l/?"):
        parsed = parse_qs(urlparse(href).query)
        target = parsed.get("uddg", [None])[0]
        return unescape(target) if target else None
    if href.startswith("http://") or href.startswith("https://"):
        return href
    return None


def _is_internal_search_link(url: str, title: str) -> bool:
    lowered_url = url.lower()
    lowered_title = title.lower()
    if any(domain in lowered_url for domain in ("duckduckgo.com", "html.duckduckgo.com")):
        return True
    if "bing.com/images/search" in lowered_url or "bing.com/videos/search" in lowered_url or "bing.com/news/search" in lowered_url:
        return True
    if "bing.com/maps" in lowered_url or "bing.com/travel/search" in lowered_url or "bing.com/shop" in lowered_url:
        return True
    nav_titles = {"画像", "動画", "地図", "ニュース", "ショッピング", "フライト", "旅行", "images", "videos", "maps", "news"}
    return lowered_title in nav_titles


def _extract_excerpt(html: str) -> str:
    text = re.sub(r"(?is)<script.*?>.*?</script>", " ", html)
    text = re.sub(r"(?is)<style.*?>.*?</style>", " ", text)
    text = re.sub(r"(?s)<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", unescape(text)).strip()
    return text[:500]


def _decode_bing_target(encoded: str) -> str | None:
    try:
        padding = "=" * (-len(encoded) % 4)
        return urlsafe_b64decode(encoded + padding).decode("utf-8", errors="ignore")
    except Exception:
        return None


def _normalize_query(query: str) -> str:
    normalized = " ".join(query.strip().split())
    for phrase in (
        "帮我查一下",
        "帮我查",
        "帮我搜一下",
        "帮我搜",
        "帮我看看",
        "查一下",
        "搜一下",
        "查一查",
        "搜一搜",
    ):
        normalized = normalized.replace(phrase, "").strip()

    hints = {
        "日本央行": "日本銀行 金融政策",
        "日本银行": "日本銀行 金融政策",
        "bank of japan": "Bank of Japan monetary policy site:boj.or.jp",
        "美联储": "Federal Reserve policy site:federalreserve.gov",
        "联储": "Federal Reserve policy site:federalreserve.gov",
        "欧洲央行": "European Central Bank monetary policy site:ecb.europa.eu",
        "英国央行": "Bank of England monetary policy site:bankofengland.co.uk",
    }
    lowered = normalized.lower()
    for pattern, replacement in hints.items():
        if pattern in lowered or pattern in normalized:
            return replacement
    return normalized


def _build_summary(*, query: str, results: list[dict]) -> str:
    if not results:
        return f"没有检索到与“{query}”相关的网页结果。"

    lines = [f"围绕“{query}”做了网页检索，当前优先结果如下：", ""]
    for index, item in enumerate(results, start=1):
        excerpt = item["excerpt"][:140] if item["excerpt"] else "未能提取正文摘要。"
        lines.append(f"{index}. {item['title']}")
        lines.append(f"   {excerpt}")
        lines.append(f"   {item['url']}")
    return "\n".join(lines)
