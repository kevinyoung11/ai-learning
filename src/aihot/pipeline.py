from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from aihot.adapters import FetchError, fetch_source_entries
from aihot.cluster import cluster_items, dedupe_items
from aihot.config import load_sources
from aihot.models import NormalizedItem, RawEntry, SourceConfig, SourceRun, Story
from aihot.normalize import normalize_entry
from aihot.repository import Repository
from aihot.score import generate_daily_report, score_story


def run_pipeline_once(
    catalog_path: str | Path,
    db_path: str | Path,
    *,
    fixture_dir: str | Path | None = None,
    allow_network: bool = False,
    include_shadow: bool = False,
) -> dict[str, int]:
    fetched_at = datetime.now(timezone.utc)
    all_sources = load_sources(catalog_path, enabled_only=False)
    enabled_sources = _selected_sources(all_sources, include_shadow=include_shadow)
    source_map = {source.id: source for source in all_sources}
    repo = Repository(db_path)
    repo.init_db()
    repo.upsert_sources(all_sources)

    normalized_items: list[NormalizedItem] = []
    story_items: list[NormalizedItem] = []
    failed = 0
    blocked = 0
    quarantined = 0
    for source in enabled_sources:
        if source.quarantined:
            quarantined += 1
            repo.insert_source_run(SourceRun(source.id, "quarantined", fetched_at, 0, "source is quarantined"))
            continue
        try:
            raw_entries = fetch_source_entries(
                source,
                fixture_dir=Path(fixture_dir) if fixture_dir is not None else None,
                allow_network=allow_network,
            )
            source_items, normalize_skips = _normalize_entries(raw_entries, fetched_at)
            normalized_items.extend(source_items)
            if source.run_mode == "active":
                story_items.extend(source_items)
            skipped = normalize_skips
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
            if _is_blocked_config_error(exc):
                blocked += 1
                repo.insert_source_run(SourceRun(source.id, "blocked_config", fetched_at, 0, str(exc)))
            else:
                failed += 1
                repo.insert_source_run(SourceRun(source.id, "failed", fetched_at, 0, str(exc)))

    deduped_items = dedupe_items(normalized_items)
    persisted_url_by_hash = {item.content_hash: item.canonical_url for item in deduped_items}
    persisted_url_by_canonical = {item.canonical_url: item.canonical_url for item in deduped_items}
    repo.upsert_items(deduped_items)
    clustered_stories = cluster_items(story_items)
    persisted_stories = _rewrite_story_membership(
        clustered_stories,
        story_items,
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
        "sources_blocked": blocked,
        "sources_quarantined": quarantined,
        "items_inserted": len(repo.list_items(mode="all")),
        "stories": len(stories),
    }


def _selected_sources(sources: list[SourceConfig], *, include_shadow: bool) -> list[SourceConfig]:
    return [
        source
        for source in sources
        if source.enabled and (source.run_mode == "active" or include_shadow)
    ]


def _is_blocked_config_error(exc: FetchError) -> bool:
    return exc.reason.startswith("missing required environment variable") or "requires url or config.user_id" in exc.reason


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


def _normalize_entries(
    raw_entries: list[RawEntry],
    fetched_at: datetime,
) -> tuple[list[NormalizedItem], int]:
    items: list[NormalizedItem] = []
    skipped = 0
    for entry in raw_entries:
        try:
            item = normalize_entry(entry, fetched_at=fetched_at)
        except (TypeError, ValueError):
            skipped += 1
            continue
        if item is None:
            skipped += 1
            continue
        items.append(item)
    return items, skipped


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
