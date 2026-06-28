from datetime import datetime, timezone
from pathlib import Path

import pytest

from urllib.error import URLError
from urllib.error import HTTPError

from aihot.adapters import FetchError, _fetch_url, fetch_source_entries, parse_feed_bytes
from aihot.models import RawEntry, SourceConfig
from aihot.normalize import canonicalize_url, normalize_entry, normalize_title_key


def test_parse_feed_bytes_handles_rss_entries():
    source = SourceConfig(
        id="ai_feed",
        name="AI Feed",
        source_type="rss",
        adapter="rss",
        url="fixture://ai-feed.xml",
    )
    entries = parse_feed_bytes(Path("tests/fixtures/ai-feed.xml").read_bytes(), source)

    assert len(entries) == 2
    assert entries[0].source_id == "ai_feed"
    assert entries[0].title == "OpenAI releases new agent tools"
    assert entries[0].url == "https://example.com/openai-agent?utm_source=x#section"
    assert entries[0].published_at == datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    assert "reliable agents" in entries[0].raw_content


def test_parse_feed_bytes_handles_atom_entries():
    source = SourceConfig(
        id="atom_feed",
        name="Atom Feed",
        source_type="rss",
        adapter="rss",
        url="fixture://atom-feed.xml",
    )
    entries = parse_feed_bytes(Path("tests/fixtures/atom-feed.xml").read_bytes(), source)

    assert len(entries) == 1
    assert entries[0].title == "Anthropic ships Claude workflow controls"
    assert entries[0].url == "https://example.com/claude-workflow"


def test_fetch_source_entries_supports_fixture_urls():
    source = SourceConfig(
        id="fixture",
        name="Fixture",
        source_type="rss",
        adapter="rss",
        url="fixture://ai-feed.xml",
    )

    entries = fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))

    assert len(entries) == 2


def test_fetch_source_entries_limits_each_source_fetch(tmp_path):
    items = "\n".join(
        f"""
        <item>
          <title>AI item {index}</title>
          <link>https://example.com/items/{index}</link>
          <pubDate>Sun, 28 Jun 2026 08:{index % 60:02d}:00 GMT</pubDate>
          <description>Item {index}</description>
        </item>
        """
        for index in range(75)
    )
    (tmp_path / "large-feed.xml").write_text(
        f"<rss><channel><title>Large Feed</title>{items}</channel></rss>",
        encoding="utf-8",
    )
    source = SourceConfig(
        id="large",
        name="Large",
        source_type="rss",
        adapter="rss",
        url="fixture://large-feed.xml",
    )

    entries = fetch_source_entries(source, fixture_dir=tmp_path)

    assert len(entries) == 50
    assert entries[0].title == "AI item 0"
    assert entries[-1].title == "AI item 49"


def test_fetch_source_entries_raises_structured_error_for_missing_fixture():
    source = SourceConfig(
        id="missing",
        name="Missing",
        source_type="rss",
        adapter="rss",
        url="fixture://missing.xml",
    )

    with pytest.raises(FetchError, match="missing.xml"):
        fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))


def test_parse_feed_bytes_rejects_malformed_feed_without_entries():
    source = SourceConfig(
        id="bad_feed",
        name="Bad Feed",
        source_type="rss",
        adapter="rss",
        url="https://example.com/feed.xml",
    )

    with pytest.raises(FetchError, match="malformed feed"):
        parse_feed_bytes(b"<html><body>not a feed</body></html>", source)


def test_fetch_source_entries_blocks_live_network_without_opt_in():
    source = SourceConfig(
        id="live",
        name="Live",
        source_type="rss",
        adapter="rss",
        url="https://example.com/feed.xml",
    )

    with pytest.raises(FetchError, match="live network"):
        fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))


def test_fetch_url_retries_transient_url_errors(monkeypatch):
    source = SourceConfig(
        id="retry",
        name="Retry",
        source_type="rss",
        adapter="rss",
        url="https://example.com/feed.xml",
    )
    calls = {"count": 0}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"ok"

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise URLError("temporary timeout")
        return Response()

    monkeypatch.setattr("aihot.adapters.urlopen", fake_urlopen)

    assert _fetch_url(source) == b"ok"
    assert calls["count"] == 2


def test_fetch_url_retries_http_5xx_then_succeeds(monkeypatch):
    source = SourceConfig("retry_500", "Retry 500", "rss", "rss", url="https://example.com/feed.xml")
    calls = {"count": 0}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return b"ok"

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        if calls["count"] == 1:
            raise HTTPError(source.url, 500, "server error", {}, None)
        return Response()

    monkeypatch.setattr("aihot.adapters.urlopen", fake_urlopen)

    assert _fetch_url(source) == b"ok"
    assert calls["count"] == 2


def test_fetch_url_does_not_retry_http_4xx(monkeypatch):
    source = SourceConfig("not_found", "Not Found", "rss", "rss", url="https://example.com/feed.xml")
    calls = {"count": 0}

    def fake_urlopen(request, timeout):
        calls["count"] += 1
        raise HTTPError(source.url, 404, "not found", {}, None)

    monkeypatch.setattr("aihot.adapters.urlopen", fake_urlopen)

    with pytest.raises(FetchError, match="HTTP 404"):
        _fetch_url(source)
    assert calls["count"] == 1


def test_fetch_source_entries_parses_github_org_repos(monkeypatch):
    source = SourceConfig(
        id="inclusionai_repos",
        name="inclusionAI Repos",
        source_type="github",
        adapter="github_org_repos",
        url="https://api.github.com/orgs/inclusionAI/repos",
    )

    monkeypatch.setattr(
        "aihot.adapters._fetch_json",
        lambda source: [
            {
                "full_name": "inclusionAI/AWorld",
                "html_url": "https://github.com/inclusionAI/AWorld",
                "description": "A multi-agent runtime",
                "created_at": "2026-06-28T05:00:00Z",
                "pushed_at": "2026-06-28T06:00:00Z",
                "language": "Python",
            }
        ],
    )

    entries = fetch_source_entries(source, allow_network=True)

    assert len(entries) == 1
    assert entries[0].title == "inclusionAI/AWorld"
    assert entries[0].url == "https://github.com/inclusionAI/AWorld"
    assert entries[0].published_at == datetime(2026, 6, 28, 5, 0, tzinfo=timezone.utc)
    assert entries[0].raw_content == "A multi-agent runtime"
    assert entries[0].tags == ("Python",)


def test_fetch_source_entries_parses_huggingface_models(monkeypatch):
    source = SourceConfig(
        id="inclusionai_models",
        name="inclusionAI Models",
        source_type="model",
        adapter="huggingface_models",
        url="https://huggingface.co/api/models?author=inclusionAI",
    )

    monkeypatch.setattr(
        "aihot.adapters._fetch_json",
        lambda source: [
            {
                "modelId": "inclusionAI/example-model",
                "createdAt": "2026-06-28T07:00:00.000Z",
                "lastModified": "2026-06-28T08:00:00.000Z",
                "downloads": 42,
                "likes": 7,
                "pipeline_tag": "text-generation",
            }
        ],
    )

    entries = fetch_source_entries(source, allow_network=True)

    assert entries[0].title == "inclusionAI/example-model"
    assert entries[0].url == "https://huggingface.co/inclusionAI/example-model"
    assert entries[0].published_at == datetime(2026, 6, 28, 7, 0, tzinfo=timezone.utc)
    assert "downloads: 42" in entries[0].raw_content
    assert entries[0].tags == ("text-generation",)


def test_fetch_source_entries_parses_hn_algolia_hits(monkeypatch):
    source = SourceConfig(
        id="hn_ai",
        name="Hacker News AI",
        source_type="community",
        adapter="hn_algolia",
        url="https://hn.algolia.com/api/v1/search_by_date?query=AI",
    )

    monkeypatch.setattr(
        "aihot.adapters._fetch_json",
        lambda source: {
            "hits": [
                {
                    "title": "New AI benchmark",
                    "url": "https://example.com/benchmark",
                    "created_at": "2026-06-28T09:00:00Z",
                    "author": "alice",
                    "objectID": "123",
                    "points": 100,
                    "num_comments": 35,
                }
            ]
        },
    )

    entries = fetch_source_entries(source, allow_network=True)

    assert entries[0].title == "New AI benchmark"
    assert entries[0].url == "https://example.com/benchmark"
    assert entries[0].author == "alice"
    assert "comments: 35" in entries[0].raw_content


def test_fetch_source_entries_parses_same_section_html_links(monkeypatch):
    source = SourceConfig(
        id="anthropic_news",
        name="Anthropic News",
        source_type="html",
        adapter="html_links",
        url="https://www.anthropic.com/news",
    )
    html = b"""
    <html><body>
      <a href="/news/claude-4">Claude 4 launches for developers</a>
      <a href="/company">Company</a>
      <a href="https://other.example.com/news/nope">External AI item</a>
    </body></html>
    """
    monkeypatch.setattr("aihot.adapters._fetch_url", lambda source: html)

    entries = fetch_source_entries(source, allow_network=True)

    assert len(entries) == 1
    assert entries[0].title == "Claude 4 launches for developers"
    assert entries[0].url == "https://www.anthropic.com/news/claude-4"
    assert entries[0].raw_content == "Claude 4 launches for developers"


def test_normalize_entry_canonicalizes_url_and_hashes_content():
    entry = RawEntry(
        source_id="ai_feed",
        source_type="rss",
        title="OpenAI releases new agent tools",
        url="https://Example.com/openai-agent/?utm_source=x&ref=home#comments",
        published_at=datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc),
        raw_content="New tools help developers build reliable agents.",
    )
    fetched_at = datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc)

    item = normalize_entry(entry, fetched_at=fetched_at)

    assert item is not None
    assert item.canonical_url == "https://example.com/openai-agent"
    assert item.published_at == entry.published_at
    assert item.fetched_at == fetched_at
    assert len(item.content_hash) == 64


def test_normalize_entry_content_hash_ignores_url_variants():
    fetched_at = datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc)
    first = normalize_entry(
        RawEntry(
            source_id="one",
            source_type="rss",
            title="🚀 OpenAI releases new agent tools!!!",
            url="https://example.com/a",
            published_at=fetched_at,
            raw_content="New tools help developers build reliable agents.",
        ),
        fetched_at=fetched_at,
    )
    second = normalize_entry(
        RawEntry(
            source_id="two",
            source_type="rss",
            title="openai releases new agent tools",
            url="https://other.example.com/b",
            published_at=fetched_at,
            raw_content="New tools help developers build reliable agents.",
        ),
        fetched_at=fetched_at,
    )

    assert first is not None
    assert second is not None
    assert first.content_hash == second.content_hash


def test_normalize_entry_skips_missing_title_or_url():
    fetched_at = datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc)

    assert normalize_entry(
        RawEntry("src", "rss", None, "https://example.com/a", None),
        fetched_at=fetched_at,
    ) is None
    assert normalize_entry(
        RawEntry("src", "rss", "Title", None, None),
        fetched_at=fetched_at,
    ) is None


def test_title_key_normalizes_punctuation_emoji_and_case():
    assert normalize_title_key("🚀 OpenAI releases new agent tools!!!") == normalize_title_key(
        "openai releases new agent tools"
    )


def test_canonicalize_url_removes_tracking_default_port_and_trailing_slash():
    assert canonicalize_url("https://Example.com:443/path/?utm_medium=x") == "https://example.com/path"
