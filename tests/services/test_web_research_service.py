from apps.api_service.app.services.web_fetch_runtime import FetchResult
from apps.api_service.app.services.web_fetch_runtime import FetchRuntimeError
from apps.api_service.app.services.web_research_service import run_web_research


def test_web_research_collects_search_results_and_page_excerpts(monkeypatch) -> None:
    search_html = """
    <?xml version="1.0" encoding="utf-8" ?>
    <rss version="2.0">
      <channel>
        <item><title>Policy One</title><link>https://example.gov/policy1</link></item>
        <item><title>Policy Two</title><link>https://example.gov/policy2</link></item>
      </channel>
    </rss>
    """
    page_html = "<html><body><h1>Policy headline</h1><p>Important economic policy update for markets.</p></body></html>"

    class DummySettings:
        web_search_result_limit = 5
        web_search_fetch_page_limit = 2
        web_search_provider = "bing_html"
        web_search_base_url = "https://www.bing.com/search"

    def fake_fetch(url: str, allowed_domains=None):
        if "bing.com/search" in url:
            return FetchResult(
                url=url,
                final_url=url,
                status_code=200,
                content_type="text/html",
                body=search_html,
            )
        return FetchResult(
            url=url,
            final_url=url,
            status_code=200,
            content_type="text/html",
            body=page_html,
        )

    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.get_settings",
        lambda: DummySettings(),
    )
    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.fetch_url",
        fake_fetch,
    )

    result = run_web_research(query="japan central bank policy", max_results=5)

    assert result["status"] == "success"
    assert result["result_count"] == 2
    assert result["results"][0]["title"] == "Policy One"
    assert result["results"][0]["url"] == "https://example.gov/policy1"
    assert "Important economic policy update" in result["results"][0]["excerpt"]
    assert "网页检索" in result["summary"]


def test_web_research_returns_failed_payload_when_search_page_unavailable(monkeypatch) -> None:
    class DummySettings:
        web_search_result_limit = 5
        web_search_fetch_page_limit = 2
        web_search_provider = "bing_html"
        web_search_base_url = "https://www.bing.com/search"

    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.get_settings",
        lambda: DummySettings(),
    )
    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.fetch_url",
        lambda url, allowed_domains=None: (_ for _ in ()).throw(FetchRuntimeError("network down")),
    )

    result = run_web_research(query="fed policy", max_results=5)

    assert result["status"] == "failed"
    assert result["result_count"] == 0
    assert "网页检索暂时失败" in result["summary"]


def test_web_research_rewrites_macro_query_and_filters_untrusted_domains(monkeypatch) -> None:
    search_html = """
    <?xml version="1.0" encoding="utf-8" ?>
    <rss version="2.0">
      <channel>
        <item><title>Irrelevant</title><link>https://intema.pl/realizacje/</link></item>
        <item><title>Fed update</title><link>https://www.reuters.com/world/us/fed-update</link></item>
      </channel>
    </rss>
    """
    page_html = "<html><body><p>Federal Reserve officials signaled a cautious approach.</p></body></html>"

    class DummySettings:
        web_search_result_limit = 5
        web_search_fetch_page_limit = 3
        web_search_provider = "bing_html"
        web_search_base_url = "https://www.bing.com/search"

    seen_urls: list[str] = []

    def fake_fetch(url: str, allowed_domains=None):
        seen_urls.append(url)
        if "bing.com/search" in url:
            return FetchResult(
                url=url,
                final_url=url,
                status_code=200,
                content_type="text/html",
                body=search_html,
            )
        assert allowed_domains is not None
        assert "reuters.com" in allowed_domains
        return FetchResult(
            url=url,
            final_url=url,
            status_code=200,
            content_type="text/html",
            body=page_html,
        )

    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.get_settings",
        lambda: DummySettings(),
    )
    monkeypatch.setattr(
        "apps.api_service.app.services.web_research_service.fetch_url",
        fake_fetch,
    )

    result = run_web_research(query="你研究一下，美国的加降息情况", max_results=5)

    assert result["status"] == "success"
    assert result["source_policy"] == "macro_policy"
    assert result["rewrite_strategy"] in {"hint_rewrite", "macro_policy_rewrite"}
    assert result["result_count"] == 1
    assert result["results"][0]["url"] == "https://www.reuters.com/world/us/fed-update"
    assert "Federal+Reserve+rate+hike+rate+cut+outlook" in seen_urls[0]
