from datetime import datetime, timezone
from pathlib import Path

import pytest
import yaml

from aihot.adapters import FetchError, fetch_source_entries
from aihot.config import SourceCatalogError, load_sources
from aihot.models import SourceConfig
from aihot.pipeline import run_pipeline_once
from aihot.repository import Repository


def test_rss_proxy_adapter_consumes_proxy_feed_fixtures():
    source = SourceConfig(
        id="wechat_proxy",
        name="WeChat Proxy",
        source_type="wechat",
        adapter="rss_proxy",
        url="fixture://ai-feed.xml",
        run_mode="shadow",
    )

    entries = fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))

    assert len(entries) == 2
    assert entries[0].source_type == "wechat"
    assert entries[0].title == "OpenAI releases new agent tools"


def test_json_api_adapter_uses_configured_paths():
    source = SourceConfig(
        id="zhipu_json",
        name="Zhipu JSON",
        source_type="api",
        adapter="json_api",
        url="fixture://json-api.json",
        config={
            "items_path": "data.items",
            "title_path": "title",
            "url_path": "url",
            "date_path": "published_at",
            "content_path": "summary",
            "id_path": "id",
            "tags_path": "tags",
        },
    )

    entries = fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))

    assert len(entries) == 1
    assert entries[0].title == "Zhipu releases a new GLM research note"
    assert entries[0].url == "https://example.com/research/glm-note"
    assert entries[0].published_at == datetime(2026, 6, 28, 11, 0, tzinfo=timezone.utc)
    assert entries[0].raw_content == "A structured research feed item."
    assert entries[0].external_id == "glm-note-1"
    assert entries[0].tags == ("research", "glm")


def test_html_extract_adapter_uses_selector_config():
    source = SourceConfig(
        id="claude_blog",
        name="Claude Blog",
        source_type="html",
        adapter="html_extract",
        url="fixture://html-extract.html",
        config={
            "item_selector": "article.post",
            "title_selector": "h2",
            "link_selector": "a.post-link",
            "date_selector": "time",
            "content_selector": "p.summary",
        },
    )

    entries = fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))

    assert len(entries) == 2
    assert entries[0].title == "Claude Code adds source gateway support"
    assert entries[0].url == "https://example.com/blog/source-gateways"
    assert entries[0].published_at == datetime(2026, 6, 28, 12, 30, tzinfo=timezone.utc)
    assert entries[0].raw_content == "Adapters can extract structured items from HTML pages."


def test_x_api_adapter_parses_user_timeline_with_bearer_token(monkeypatch):
    source = SourceConfig(
        id="x_openai",
        name="OpenAI on X",
        source_type="x",
        adapter="x_api_user_timeline",
        url="fixture://x-api.json",
        auth_env="X_BEARER_TOKEN",
        config={"username": "OpenAI"},
    )
    monkeypatch.setenv("X_BEARER_TOKEN", "test-token")

    entries = fetch_source_entries(source, fixture_dir=Path("tests/fixtures"))

    assert len(entries) == 1
    assert entries[0].title == "We shipped a new AI model release today."
    assert entries[0].url == "https://x.com/OpenAI/status/1800000000000000001"
    assert entries[0].published_at == datetime(2026, 6, 28, 13, 0, tzinfo=timezone.utc)
    assert entries[0].external_id == "1800000000000000001"


def test_x_api_adapter_requires_bearer_token(monkeypatch):
    source = SourceConfig(
        id="x_openai",
        name="OpenAI on X",
        source_type="x",
        adapter="x_api_user_timeline",
        auth_env="X_BEARER_TOKEN",
        config={"username": "OpenAI"},
    )
    monkeypatch.delenv("X_BEARER_TOKEN", raising=False)

    with pytest.raises(FetchError, match="missing required environment variable X_BEARER_TOKEN"):
        fetch_source_entries(source, allow_network=True)


def test_source_catalog_supports_shadow_quarantine_auth_and_config(tmp_path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "shadow_wechat",
                        "name": "Shadow WeChat",
                        "source_type": "wechat",
                        "adapter": "rss_proxy",
                        "url": "env://WECHAT_RSS_BASE/shadow_wechat.xml",
                        "run_mode": "shadow",
                        "enabled": True,
                    },
                    {
                        "id": "x_openai",
                        "name": "X OpenAI",
                        "source_type": "x",
                        "adapter": "x_api_user_timeline",
                        "auth_env": "X_BEARER_TOKEN",
                        "run_mode": "shadow",
                        "config": {"username": "OpenAI"},
                        "enabled": True,
                    },
                    {
                        "id": "dead_source",
                        "name": "Dead Source",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "https://example.com/dead.xml",
                        "quarantined": True,
                        "enabled": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    sources = load_sources(catalog, enabled_only=False)

    assert sources[0].run_mode == "shadow"
    assert sources[0].url == "env://WECHAT_RSS_BASE/shadow_wechat.xml"
    assert sources[1].auth_env == "X_BEARER_TOKEN"
    assert sources[1].config["username"] == "OpenAI"
    assert sources[2].quarantined is True
    assert load_sources(catalog, enabled_only=True) == []


def test_source_catalog_rejects_active_disabled_adapter(tmp_path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: broken
    name: Broken
    source_type: rss
    adapter: disabled
    run_mode: active
    enabled: true
""",
        encoding="utf-8",
    )

    with pytest.raises(SourceCatalogError, match="disabled adapter"):
        load_sources(catalog)


def test_pipeline_shadow_sources_ingest_without_affecting_selected_stories(tmp_path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "active",
                        "name": "Active",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://ai-feed.xml",
                        "enabled": True,
                    },
                    {
                        "id": "shadow",
                        "name": "Shadow",
                        "source_type": "wechat",
                        "adapter": "rss_proxy",
                        "url": "fixture://atom-feed.xml",
                        "run_mode": "shadow",
                        "enabled": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    db_path = tmp_path / "aihot.db"

    default_summary = run_pipeline_once(catalog, db_path, fixture_dir=Path("tests/fixtures"))
    shadow_summary = run_pipeline_once(
        catalog,
        db_path,
        fixture_dir=Path("tests/fixtures"),
        include_shadow=True,
    )

    repo = Repository(db_path)
    assert default_summary["sources_total"] == 1
    assert shadow_summary["sources_total"] == 2
    assert any(item["source_id"] == "shadow" for item in repo.list_items(mode="all"))
    assert not any(item["source_id"] == "shadow" for item in repo.list_items(mode="selected"))


def test_pipeline_records_blocked_config_and_quarantined_sources(tmp_path, monkeypatch):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "missing_proxy",
                        "name": "Missing Proxy",
                        "source_type": "wechat",
                        "adapter": "rss_proxy",
                        "url": "env://WECHAT_RSS_BASE/missing.xml",
                        "run_mode": "shadow",
                        "enabled": True,
                    },
                    {
                        "id": "quarantined",
                        "name": "Quarantined",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://ai-feed.xml",
                        "quarantined": True,
                        "enabled": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.delenv("WECHAT_RSS_BASE", raising=False)

    summary = run_pipeline_once(
        catalog,
        tmp_path / "aihot.db",
        fixture_dir=Path("tests/fixtures"),
        include_shadow=True,
    )

    repo = Repository(tmp_path / "aihot.db")
    assert summary["sources_failed"] == 0
    assert summary["sources_blocked"] == 1
    assert repo.list_source_runs("missing_proxy")[0]["status"] == "blocked_config"
    assert repo.list_source_runs("quarantined")[0]["status"] == "quarantined"
