from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from aihot.adapters import FetchError, fetch_source_entries
from aihot.cluster import cluster_items, dedupe_items
from aihot.config import load_sources
from aihot.models import NormalizedItem, SourceConfig, SourceRun, Story
from aihot.normalize import normalize_entry
from aihot.repository import Repository
from aihot.score import generate_daily_report, score_story


def run_pipeline_once(
    catalog_path: str | Path,
    db_path: str | Path,
    *,
    fixture_dir: str | Path | None = None,
) -> dict[str, int]:
    fetched_at = datetime.now(timezone.utc)
    all_sources = load_sources(catalog_path, enabled_only=False)
    enabled_sources = [source for source in all_sources if source.enabled]
    source_map = {source.id: source for source in all_sources}
    repo = Repository(db_path)
    repo.init_db()
    repo.upsert_sources(all_sources)

    normalized_items: list[NormalizedItem] = []
    failed = 0
    for source in enabled_sources:
        try:
            raw_entries = fetch_source_entries(
                source,
                fixture_dir=Path(fixture_dir) if fixture_dir is not None else None,
            )
            source_items = [
                item
                for entry in raw_entries
                if (item := normalize_entry(entry, fetched_at=fetched_at)) is not None
            ]
            normalized_items.extend(source_items)
            skipped = len(raw_entries) - len(source_items)
            if skipped:
                repo.insert_source_run(
                    SourceRun(
                        source.id,
                        "success_with_skips",
                        fetched_at,
                        len(source_items),
                        f"skipped {skipped} malformed entries",
                    )
                )
            else:
                repo.insert_source_run(SourceRun(source.id, "success", fetched_at, len(source_items)))
        except FetchError as exc:
            failed += 1
            repo.insert_source_run(SourceRun(source.id, "failed", fetched_at, 0, str(exc)))

    deduped_items = dedupe_items(normalized_items)
    persisted_url_by_hash = {item.content_hash: item.canonical_url for item in deduped_items}
    persisted_url_by_canonical = {item.canonical_url: item.canonical_url for item in deduped_items}
    repo.upsert_items(deduped_items)
    clustered_stories = cluster_items(normalized_items)
    persisted_stories = _rewrite_story_membership(
        clustered_stories,
        normalized_items,
        persisted_url_by_hash,
        persisted_url_by_canonical,
    )
    stories = _score_stories(persisted_stories, source_map)
    repo.replace_stories(stories)
    for day, day_stories in _stories_by_day(stories).items():
        report = generate_daily_report(day, day_stories)
        repo.upsert_daily_report(day, str(report["narrative"]), int(report["story_count"]))

    return {
        "sources_total": len(enabled_sources),
        "sources_failed": failed,
        "items_inserted": len(repo.list_items(mode="all")),
        "stories": len(stories),
    }


def _score_stories(stories: list[Story], source_map: dict[str, SourceConfig]) -> list[Story]:
    scored: list[Story] = []
    for story in stories:
        scored.append(
            Story(
                id=story.id,
                canonical_title=story.canonical_title,
                day=story.day,
                summary=story.summary,
                hotness=score_story(story, source_map),
                source_count=story.source_count,
                item_urls=story.item_urls,
                selected=story.selected,
            )
        )
    return scored


def _rewrite_story_membership(
    stories: list[Story],
    normalized_items: list[NormalizedItem],
    persisted_url_by_hash: dict[str, str],
    persisted_url_by_canonical: dict[str, str],
) -> list[Story]:
    item_by_canonical = {item.canonical_url: item for item in normalized_items}
    rewritten: list[Story] = []
    for story in stories:
        item_urls: list[str] = []
        for url in story.item_urls:
            item = item_by_canonical[url]
            persisted_url = persisted_url_by_canonical.get(url) or persisted_url_by_hash[item.content_hash]
            if persisted_url not in item_urls:
                item_urls.append(persisted_url)
        rewritten.append(
            Story(
                id=story.id,
                canonical_title=story.canonical_title,
                day=story.day,
                summary=story.summary,
                hotness=story.hotness,
                source_count=story.source_count,
                item_urls=tuple(item_urls),
                selected=story.selected,
            )
        )
    return rewritten


def _stories_by_day(stories: list[Story]) -> dict[str, list[Story]]:
    by_day: dict[str, list[Story]] = defaultdict(list)
    for story in stories:
        by_day[story.day].append(story)
    return dict(by_day)
