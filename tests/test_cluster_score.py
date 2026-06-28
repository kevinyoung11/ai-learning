from datetime import datetime, timedelta, timezone

from aihot.cluster import dedupe_items, cluster_items
from aihot.models import NormalizedItem, SourceConfig
from aihot.score import generate_daily_report, score_story


def make_item(
    title: str,
    url: str,
    source_id: str = "src",
    published_at: datetime | None = None,
    content_hash: str | None = None,
) -> NormalizedItem:
    published = published_at or datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    key = "".join(ch for ch in title.lower() if ch.isalnum() or ch.isspace()).strip()
    return NormalizedItem(
        source_id=source_id,
        source_type="rss",
        title=title,
        url=url,
        canonical_url=url,
        raw_content=title,
        published_at=published,
        fetched_at=published,
        content_hash=content_hash or key,
        title_key=key,
    )


def test_dedupe_items_keeps_one_item_per_canonical_url_and_hash():
    first = make_item("OpenAI releases agent tools", "https://example.com/a", "one", content_hash="same")
    duplicate = make_item("OpenAI releases agent tools!!!", "https://example.com/a", "two", content_hash="same")
    near_duplicate = make_item("OpenAI releases agent tools", "https://example.com/b", "three", content_hash="same")

    deduped = dedupe_items([first, duplicate, near_duplicate])

    assert deduped == [first]


def test_cluster_items_groups_related_titles_inside_day_window():
    items = [
        make_item("OpenAI releases new agent tools", "https://example.com/a", "openai"),
        make_item("Developers react to OpenAI agent tools release", "https://example.com/b", "hn"),
        make_item("DeepMind publishes robotics update", "https://example.com/c", "deepmind"),
    ]

    stories = cluster_items(items)

    source_counts = sorted(story.source_count for story in stories)
    assert source_counts == [1, 2]


def test_cluster_items_story_membership_uses_canonical_urls():
    item = make_item("OpenAI releases new agent tools", "https://example.com/canonical", "openai")
    object.__setattr__(item, "url", "https://example.com/canonical?utm_source=x#section")

    story = cluster_items([item])[0]

    assert story.item_urls == ("https://example.com/canonical",)


def test_cluster_items_separates_related_titles_outside_time_window():
    first = make_item("OpenAI releases new agent tools", "https://example.com/a")
    later = make_item(
        "OpenAI releases new agent tools",
        "https://example.com/b",
        published_at=first.published_at + timedelta(days=2),
    )

    stories = cluster_items([first, later])

    assert len(stories) == 2


def test_score_story_increases_with_source_count_and_weight():
    low = cluster_items([make_item("OpenAI releases new agent tools", "https://example.com/a", "low")])[0]
    high = cluster_items(
        [
            make_item("OpenAI releases new agent tools", "https://example.com/a", "low"),
            make_item("Developers react to OpenAI agent tools release", "https://example.com/b", "high"),
        ]
    )[0]
    weights = {
        "low": SourceConfig("low", "Low", "rss", "rss", weight=1.0),
        "high": SourceConfig("high", "High", "rss", "rss", weight=2.0),
    }

    assert score_story(high, weights) > score_story(low, weights)


def test_generate_daily_report_lists_top_story_titles():
    stories = cluster_items(
        [
            make_item("OpenAI releases new agent tools", "https://example.com/a", "openai"),
            make_item("DeepMind publishes robotics update", "https://example.com/c", "deepmind"),
        ]
    )

    report = generate_daily_report("2026-06-28", stories)

    assert report["day"] == "2026-06-28"
    assert "OpenAI releases new agent tools" in report["narrative"]
    assert report["story_count"] == 2
