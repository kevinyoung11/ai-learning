from datetime import datetime, timezone
from pathlib import Path

import pytest

from aihot.adapters import FetchError, fetch_source_entries, parse_feed_bytes
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
