from pathlib import Path

from apps.api_service.app.services.policy_crawl_service import run_policy_crawl
from apps.api_service.app.services.web_fetch_runtime import FetchResult


def test_policy_crawl_writes_local_summary(tmp_path, monkeypatch) -> None:
    sources_file = tmp_path / "sources.yaml"
    sources_file.write_text(
        """
sources:
  - country: Testland
    economy_rank: 1
    source_id: test_source
    source_name: Test Source
    department_id: national_statistics_bureau
    url: https://example.gov/policy
    allowed_domains:
      - example.gov
    include_keywords:
      - policy
      - guidance
""".strip()
        + "\n",
        encoding="utf-8",
    )

    html = """
    <html><body>
    <a href="/docs/policy-update-2026-03-14">Policy update 2026-03-14</a>
    <a href="https://example.gov/docs/guidance-note">Economic guidance note</a>
    <a href="https://example.com/ignore">External site</a>
    </body></html>
    """

    class DummySettings:
        policy_watch_sources_path = str(sources_file)
        policy_watch_output_dir = str(tmp_path / "output")

    monkeypatch.setattr(
        "apps.api_service.app.services.policy_crawl_service.get_settings",
        lambda: DummySettings(),
    )
    monkeypatch.setattr(
        "apps.api_service.app.services.policy_crawl_service.fetch_url",
        lambda url, allowed_domains=None: FetchResult(
            url=url,
            final_url=url,
            status_code=200,
            content_type="text/html",
            body=html,
        ),
    )

    result = run_policy_crawl(limit_per_source=5)

    assert result["status"] == "success"
    assert result["source_count"] == 1
    assert result["document_count"] == 2
    assert Path(result["output_dir"]).exists()
    assert (Path(result["output_dir"]) / "summary.json").exists()
    assert (Path(result["output_dir"]) / "test_source" / "result.md").exists()
    first_doc = result["sources"][0]["documents"][0]
    assert first_doc["url"] == "https://example.gov/docs/policy-update-2026-03-14"
    assert first_doc["published_at"] == "2026-03-14"
