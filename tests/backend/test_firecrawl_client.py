import types

from backend.config import settings


def test_firecrawl_client_search_normalizes_results(monkeypatch):
    class DummyResponse:
        data = [
            {
                "url": "https://example.com/a",
                "title": "A",
                "description": "Desc",
                "markdown": "Body",
                "metadata": {"sourceURL": "https://example.com/a"},
            }
        ]

    class DummyFirecrawlApp:
        def __init__(self, api_key: str):
            self.api_key = api_key

        def search(self, query, params=None):
            return DummyResponse()

        def scrape_url(self, url, params=None):
            return {"url": url, "markdown": "Scraped"}

        def crawl_url(self, url, params=None, wait_until_done=True, timeout=120):
            return types.SimpleNamespace(data=[{"url": url + "/p1", "markdown": "P1"}])

        def map_url(self, url, params=None):
            return types.SimpleNamespace(links=[url + "/a", url + "/b"])

    monkeypatch.setattr(settings, "firecrawl_api_key", "fc-test-key")
    monkeypatch.setattr(settings, "max_firecrawl_pages_per_search", 3)
    monkeypatch.setitem(
        __import__("sys").modules,
        "firecrawl",
        types.SimpleNamespace(FirecrawlApp=DummyFirecrawlApp),
    )

    from backend.core.research.firecrawl_client import FirecrawlClient

    client = FirecrawlClient()
    results = client.search("test query")
    assert len(results) == 1
    assert results[0]["url"] == "https://example.com/a"
    assert results[0]["markdown"] == "Body"

