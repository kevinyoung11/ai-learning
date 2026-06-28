from pathlib import Path

import pytest

from aihot.config import SourceCatalogError, load_sources


def test_load_sources_returns_enabled_sources_with_tiers(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: decoder
    name: The Decoder
    source_type: rss
    adapter: rss
    url: https://example.com/decoder.xml
    tier: stable
    weight: 1.4
    enabled: true
  - id: x_placeholder
    name: X Placeholder
    source_type: x
    adapter: disabled
    tier: experimental
    enabled: false
""",
        encoding="utf-8",
    )

    sources = load_sources(catalog, enabled_only=True)

    assert [source.id for source in sources] == ["decoder"]
    assert sources[0].tier == "stable"
    assert sources[0].weight == 1.4
    assert sources[0].source_type == "rss"


def test_load_sources_rejects_duplicate_ids(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: duplicate
    name: One
    source_type: rss
    adapter: rss
    url: https://example.com/one.xml
  - id: duplicate
    name: Two
    source_type: rss
    adapter: rss
    url: https://example.com/two.xml
""",
        encoding="utf-8",
    )

    with pytest.raises(SourceCatalogError, match="duplicate"):
        load_sources(catalog)


def test_load_sources_rejects_enabled_source_without_fetch_url(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: broken
    name: Broken
    source_type: rss
    adapter: rss
    enabled: true
""",
        encoding="utf-8",
    )

    with pytest.raises(SourceCatalogError, match="url"):
        load_sources(catalog)


def test_load_sources_allows_disabled_manual_placeholder(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: wechat_placeholder
    name: WeChat Placeholder
    source_type: wechat
    adapter: disabled
    tier: experimental
    enabled: false
""",
        encoding="utf-8",
    )

    sources = load_sources(catalog, enabled_only=False)

    assert sources[0].enabled is False
    assert sources[0].adapter == "disabled"


def test_live_catalog_registers_priority_sources():
    sources = load_sources("sources/aihot-live.yml", enabled_only=False)
    enabled_sources = load_sources("sources/aihot-live.yml", enabled_only=True)
    by_id = {source.id: source for source in sources}
    enabled_adapters = {source.adapter for source in enabled_sources}

    assert len(sources) >= 40
    assert len(enabled_sources) >= 20
    assert by_id["inclusionai_github_repos"].adapter == "github_org_repos"
    assert by_id["inclusionai_hf_models"].adapter == "huggingface_models"
    assert by_id["openai_news"].adapter == "rss"
    assert by_id["anthropic_news"].adapter == "html_links"
    assert by_id["hn_ai"].adapter == "hn_algolia"
    assert not [source.id for source in enabled_sources if source.adapter in {"disabled", "html_links"}]
    assert not [source.id for source in enabled_sources if not source.url]
    assert {"github_org_repos", "github_releases", "hn_algolia", "huggingface_models", "rss"} <= enabled_adapters
