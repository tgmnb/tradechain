from __future__ import annotations

import json
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse

import yaml

from apps.api_service.app.core.config import get_settings
from apps.api_service.app.services.web_fetch_runtime import FetchRuntimeError, fetch_url


@dataclass(slots=True)
class PolicySource:
    country: str
    economy_rank: int
    source_id: str
    source_name: str
    department_id: str
    url: str
    allowed_domains: list[str]
    include_keywords: list[str]


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
        text = " ".join(part.strip() for part in self._current_text if part.strip()).strip()
        self.anchors.append({"href": self._current_href, "text": text})
        self._current_href = None
        self._current_text = []


def run_policy_crawl(*, limit_per_source: int = 5, source_ids: list[str] | None = None) -> dict:
    settings = get_settings()
    sources = _load_sources(settings.policy_watch_sources_path)
    requested_ids = set(source_ids or [])
    crawl_sources = [source for source in sources if not requested_ids or source.source_id in requested_ids]

    started_at = datetime.now(UTC)
    run_id = started_at.strftime("%Y%m%dT%H%M%SZ")
    output_dir = Path(settings.policy_watch_output_dir) / started_at.strftime("%Y-%m-%d") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict] = []
    for source in crawl_sources:
        result = _crawl_source(source, limit_per_source=limit_per_source)
        _write_source_output(output_dir, source, result)
        results.append(result)

    summary = {
        "status": "success",
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "source_count": len(results),
        "document_count": sum(len(item["documents"]) for item in results),
        "output_dir": str(output_dir),
        "sources": results,
    }
    (output_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    (output_dir / "summary.md").write_text(_render_summary_markdown(summary), encoding="utf-8")
    return summary


def _crawl_source(source: PolicySource, *, limit_per_source: int) -> dict:
    try:
        fetched = fetch_url(source.url, allowed_domains=source.allowed_domains)
        parser = _AnchorParser()
        parser.feed(fetched.body)
        documents = _extract_policy_links(
            source=source,
            page_url=fetched.final_url,
            anchors=parser.anchors,
            limit_per_source=limit_per_source,
        )
        return {
            "country": source.country,
            "economy_rank": source.economy_rank,
            "source_id": source.source_id,
            "source_name": source.source_name,
            "url": source.url,
            "fetched_url": fetched.final_url,
            "status": "success",
            "document_count": len(documents),
            "documents": documents,
        }
    except FetchRuntimeError as exc:
        return {
            "country": source.country,
            "economy_rank": source.economy_rank,
            "source_id": source.source_id,
            "source_name": source.source_name,
            "url": source.url,
            "status": "failed",
            "error": str(exc),
            "document_count": 0,
            "documents": [],
        }


def _extract_policy_links(
    *,
    source: PolicySource,
    page_url: str,
    anchors: list[dict[str, str]],
    limit_per_source: int,
) -> list[dict]:
    documents: list[dict] = []
    seen_urls: set[str] = set()
    keywords = [item.lower() for item in source.include_keywords]

    for anchor in anchors:
        href = (anchor.get("href") or "").strip()
        text = re.sub(r"\s+", " ", (anchor.get("text") or "").strip())
        if not href or href.startswith("#") or not text:
            continue
        absolute_url = urljoin(page_url, href)
        hostname = (urlparse(absolute_url).hostname or "").lower()
        if source.allowed_domains and not any(
            hostname == domain.lstrip(".") or hostname.endswith(domain.lower()) for domain in source.allowed_domains
        ):
            continue
        haystack = f"{text} {absolute_url}".lower()
        if keywords and not any(keyword in haystack for keyword in keywords):
            continue
        if absolute_url in seen_urls:
            continue
        seen_urls.add(absolute_url)
        documents.append(
            {
                "title": text[:300],
                "url": absolute_url,
                "published_at": _extract_date(haystack),
                "policy_status": "candidate",
                "source_name": source.source_name,
            }
        )
        if len(documents) >= limit_per_source:
            break
    return documents


def _extract_date(text: str) -> str | None:
    patterns = [
        r"(20\d{2}-\d{2}-\d{2})",
        r"(20\d{2}/\d{2}/\d{2})",
        r"(20\d{2}\.\d{2}\.\d{2})",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _load_sources(path_str: str) -> list[PolicySource]:
    path = Path(path_str)
    payload = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    sources = payload.get("sources", [])
    return [
        PolicySource(
            country=item["country"],
            economy_rank=item["economy_rank"],
            source_id=item["source_id"],
            source_name=item["source_name"],
            department_id=item["department_id"],
            url=item["url"],
            allowed_domains=item.get("allowed_domains", []),
            include_keywords=item.get("include_keywords", []),
        )
        for item in sources
    ]


def _write_source_output(output_dir: Path, source: PolicySource, result: dict) -> None:
    source_dir = output_dir / source.source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    (source_dir / "result.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = [
        f"# {source.source_name}",
        "",
        f"- country: {source.country}",
        f"- status: {result['status']}",
        f"- url: {source.url}",
    ]
    if result["status"] == "failed":
        lines.append(f"- error: {result['error']}")
    else:
        lines.append(f"- document_count: {result['document_count']}")
        lines.append("")
        for item in result["documents"]:
            lines.append(f"## {item['title']}")
            lines.append("")
            lines.append(f"- url: {item['url']}")
            lines.append(f"- published_at: {item['published_at'] or 'date_unverified'}")
            lines.append(f"- policy_status: {item['policy_status']}")
            lines.append("")
    (source_dir / "result.md").write_text("\n".join(lines).strip() + "\n", encoding="utf-8")


def _render_summary_markdown(summary: dict) -> str:
    lines = [
        "# Policy Watch Summary",
        "",
        f"- run_id: {summary['run_id']}",
        f"- source_count: {summary['source_count']}",
        f"- document_count: {summary['document_count']}",
        f"- output_dir: {summary['output_dir']}",
        "",
    ]
    for source in summary["sources"]:
        lines.append(f"## {source['source_name']}")
        lines.append("")
        lines.append(f"- country: {source['country']}")
        lines.append(f"- status: {source['status']}")
        lines.append(f"- document_count: {source['document_count']}")
        if source["status"] == "failed":
            lines.append(f"- error: {source['error']}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"
