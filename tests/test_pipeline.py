from pathlib import Path

import yaml

from aihot.pipeline import run_pipeline_once
from aihot.repository import Repository


def test_pipeline_ingests_fixtures_and_records_partial_failure(tmp_path):
    db_path = tmp_path / "aihot.db"

    summary = run_pipeline_once(
        catalog_path=Path("sources/aihot-mvp.yml"),
        db_path=db_path,
        fixture_dir=Path("tests/fixtures"),
    )

    repo = Repository(db_path)
    assert summary["sources_total"] == 4
    assert summary["sources_failed"] == 1
    assert summary["items_inserted"] == 3
    assert summary["stories"] >= 2
    assert len(repo.list_items(mode="all")) == 3
    assert any(run["status"] == "failed" for run in repo.list_source_runs("missing_fixture"))
    assert repo.get_daily_report("2026-06-28")["story_count"] >= 2


def test_pipeline_rerun_is_idempotent_for_items_and_stories(tmp_path):
    db_path = tmp_path / "aihot.db"

    first = run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))
    second = run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))

    repo = Repository(db_path)
    assert second["items_inserted"] == first["items_inserted"]
    assert len(repo.list_items(mode="all")) == 3
    assert len(repo.list_source_runs("openai_fixture")) == 2


def test_pipeline_reconciles_story_membership_when_cluster_grows(tmp_path):
    first_catalog = tmp_path / "first.yml"
    second_catalog = tmp_path / "second.yml"
    db_path = tmp_path / "aihot.db"
    first_catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "openai_fixture",
                        "name": "OpenAI Fixture",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://ai-feed.xml",
                        "enabled": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )
    second_catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "openai_fixture",
                        "name": "OpenAI Fixture",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://ai-feed.xml",
                        "enabled": True,
                    },
                    {
                        "id": "duplicate_fixture",
                        "name": "Duplicate Fixture",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://duplicate-feed.xml",
                        "enabled": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    run_pipeline_once(first_catalog, db_path, fixture_dir=Path("tests/fixtures"))
    run_pipeline_once(second_catalog, db_path, fixture_dir=Path("tests/fixtures"))

    repo = Repository(db_path)
    selected_urls = [item["canonical_url"] for item in repo.list_items(mode="selected")]
    assert len(selected_urls) == len(set(selected_urls))
    assert len(repo.list_items(mode="all")) == 2


def test_pipeline_preserves_cross_source_evidence_for_story_counts(tmp_path):
    db_path = tmp_path / "aihot.db"

    run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))

    repo = Repository(db_path)
    openai_items = [
        item
        for item in repo.list_items(mode="selected")
        if "OpenAI releases new agent tools" in item["title"]
    ]
    assert openai_items[0]["source_count"] == 2


def test_pipeline_clusters_same_hash_different_urls_without_foreign_key_leak(tmp_path):
    catalog = tmp_path / "same_hash.yml"
    db_path = tmp_path / "aihot.db"
    catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "primary",
                        "name": "Primary",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://ai-feed.xml",
                        "enabled": True,
                    },
                    {
                        "id": "mirror",
                        "name": "Mirror",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://same-content-other-url.xml",
                        "enabled": True,
                    },
                ]
            }
        ),
        encoding="utf-8",
    )

    summary = run_pipeline_once(catalog, db_path, fixture_dir=Path("tests/fixtures"))

    repo = Repository(db_path)
    openai_items = [
        item
        for item in repo.list_items(mode="selected")
        if "OpenAI releases new agent tools" in item["title"]
    ]
    assert summary["items_inserted"] == 2
    assert len(openai_items) == 1
    assert openai_items[0]["source_count"] == 2


def test_pipeline_records_skipped_malformed_entries_in_source_run(tmp_path):
    catalog = tmp_path / "malformed.yml"
    db_path = tmp_path / "aihot.db"
    catalog.write_text(
        yaml.safe_dump(
            {
                "sources": [
                    {
                        "id": "malformed_fixture",
                        "name": "Malformed Fixture",
                        "source_type": "rss",
                        "adapter": "rss",
                        "url": "fixture://malformed-feed.xml",
                        "enabled": True,
                    }
                ]
            }
        ),
        encoding="utf-8",
    )

    run_pipeline_once(catalog, db_path, fixture_dir=Path("tests/fixtures"))

    repo = Repository(db_path)
    run = repo.list_source_runs("malformed_fixture")[0]
    assert run["status"] == "success_with_skips"
    assert "skipped 2 malformed entries" in run["error"]
