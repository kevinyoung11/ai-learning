from datetime import datetime, timezone

from aihot.models import NormalizedItem, SourceConfig, SourceRun, Story
from aihot.repository import Repository


def make_item(url: str = "https://example.com/a") -> NormalizedItem:
    ts = datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)
    return NormalizedItem(
        source_id="src",
        source_type="rss",
        title="OpenAI releases new agent tools",
        url=url,
        canonical_url=url,
        raw_content="summary",
        published_at=ts,
        fetched_at=ts,
        content_hash="hash",
        title_key="openai releases new agent tools",
    )


def test_repository_creates_tables_and_upserts_sources(tmp_path):
    repo = Repository(tmp_path / "aihot.db")
    repo.init_db()
    source = SourceConfig("src", "Source", "rss", "rss", url="fixture://ai-feed.xml")

    repo.upsert_sources([source])
    repo.upsert_sources([source])

    assert len(repo.list_sources()) == 1
    assert repo.list_sources()[0]["id"] == "src"


def test_repository_item_story_and_run_persistence_is_idempotent(tmp_path):
    repo = Repository(tmp_path / "aihot.db")
    repo.init_db()
    repo.upsert_sources([SourceConfig("src", "Source", "rss", "rss", url="fixture://ai-feed.xml")])
    item = make_item()
    story = Story(
        id="story-1",
        canonical_title=item.title,
        day="2026-06-28",
        summary="Summary",
        hotness=80.0,
        source_count=1,
        item_urls=(item.canonical_url,),
    )
    run = SourceRun("src", "failed", datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc), 0, "boom")

    repo.upsert_items([item])
    repo.upsert_items([item])
    repo.upsert_stories([story])
    repo.upsert_stories([story])
    repo.insert_source_run(run)

    assert len(repo.list_items(mode="all")) == 1
    assert repo.list_items(mode="selected")[0]["story_id"] == "story-1"
    assert repo.get_story("story-1")["items"][0]["canonical_url"] == item.canonical_url
    assert repo.list_source_runs("src")[0]["status"] == "failed"
    assert repo.list_source_runs("src")[0]["error"] == "boom"


def test_repository_daily_report_round_trips(tmp_path):
    repo = Repository(tmp_path / "aihot.db")
    repo.init_db()

    repo.upsert_daily_report("2026-06-28", "Narrative", 3)

    report = repo.get_daily_report("2026-06-28")
    assert report["day"] == "2026-06-28"
    assert report["narrative"] == "Narrative"
    assert report["story_count"] == 3


def test_selected_items_order_by_story_hotness(tmp_path):
    repo = Repository(tmp_path / "aihot.db")
    repo.init_db()
    repo.upsert_sources([SourceConfig("src", "Source", "rss", "rss", url="fixture://ai-feed.xml")])
    low = make_item("https://example.com/low")
    high = make_item("https://example.com/high")
    object.__setattr__(high, "title", "High score story")
    repo.upsert_items([low, high])
    repo.upsert_stories(
        [
            Story(
                id="low-story",
                canonical_title="Low",
                day="2026-06-28",
                summary="Low",
                hotness=10.0,
                source_count=1,
                item_urls=(low.canonical_url,),
            ),
            Story(
                id="high-story",
                canonical_title="High",
                day="2026-06-28",
                summary="High",
                hotness=90.0,
                source_count=1,
                item_urls=(high.canonical_url,),
            ),
        ]
    )

    selected = repo.list_items(mode="selected")

    assert [item["story_id"] for item in selected] == ["high-story", "low-story"]
