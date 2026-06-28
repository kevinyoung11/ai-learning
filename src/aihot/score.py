from __future__ import annotations

from aihot.cluster import get_story_source_ids
from aihot.models import SourceConfig, Story


def score_story(story: Story, sources: dict[str, SourceConfig] | None = None) -> float:
    source_ids = get_story_source_ids(story)
    source_weight = sum(
        (sources or {}).get(source_id, SourceConfig(source_id, source_id, "", "")).weight
        for source_id in source_ids
    )
    if not source_ids:
        source_weight = float(story.source_count)

    return story.hotness + story.source_count + source_weight


def generate_daily_report(day: str, stories: list[Story]) -> dict[str, object]:
    ranked = sorted(
        stories,
        key=lambda story: (-story.hotness, -story.source_count, story.canonical_title, story.id),
    )
    titles = [story.canonical_title for story in ranked]
    narrative = "\n".join(titles)

    return {
        "day": day,
        "narrative": narrative,
        "story_count": len(stories),
    }
