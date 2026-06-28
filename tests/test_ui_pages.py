from pathlib import Path
import re

from fastapi.testclient import TestClient

from aihot.api import create_app
from aihot.pipeline import run_pipeline_once


def make_client(tmp_path) -> TestClient:
    db_path = tmp_path / "aihot-ui.db"
    run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))
    return TestClient(create_app(db_path))


def make_mixed_day_client(tmp_path) -> TestClient:
    fixture_dir = tmp_path / "fixtures"
    fixture_dir.mkdir()
    (fixture_dir / "old-one.xml").write_text(
        """
<rss><channel><title>Old One</title>
<item>
  <title>Old cross-source model release</title>
  <link>https://old.example.com/a</link>
  <pubDate>Fri, 01 May 2026 08:00:00 GMT</pubDate>
  <description>Older but higher score.</description>
</item>
</channel></rss>
""",
        encoding="utf-8",
    )
    (fixture_dir / "old-two.xml").write_text(
        """
<rss><channel><title>Old Two</title>
<item>
  <title>Developers discuss old model release</title>
  <link>https://old.example.com/b</link>
  <pubDate>Fri, 01 May 2026 09:00:00 GMT</pubDate>
  <description>Older but higher score.</description>
</item>
</channel></rss>
""",
        encoding="utf-8",
    )
    (fixture_dir / "today.xml").write_text(
        """
<rss><channel><title>Today</title>
<item>
  <title>Today AI product launch</title>
  <link>https://today.example.com/a</link>
  <pubDate>Sun, 28 Jun 2026 10:00:00 GMT</pubDate>
  <description>Fresh lower-score story.</description>
</item>
</channel></rss>
""",
        encoding="utf-8",
    )
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: old_one
    name: Old One
    source_type: rss
    adapter: rss
    url: fixture://old-one.xml
    enabled: true
  - id: old_two
    name: Old Two
    source_type: rss
    adapter: rss
    url: fixture://old-two.xml
    enabled: true
  - id: today
    name: Today
    source_type: rss
    adapter: rss
    url: fixture://today.xml
    enabled: true
""",
        encoding="utf-8",
    )
    db_path = tmp_path / "mixed-days.db"
    run_pipeline_once(catalog, db_path, fixture_dir=fixture_dir)
    return TestClient(create_app(db_path))


def test_home_page_renders_selected_stories_with_real_links(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI HOT · 精选" in response.text
    assert 'class="app-shell"' in response.text
    assert 'class="sidebar"' in response.text
    assert 'class="timeline"' in response.text
    assert 'class="timeline-card"' in response.text
    assert "推荐理由" in response.text
    assert "OpenAI releases new agent tools" in response.text
    assert re.search(r'href="/story/[a-f0-9]{12}"', response.text)
    assert 'href="/all-news"' in response.text
    assert 'href="/digest"' in response.text


def test_home_page_renders_latest_day_instead_of_highest_scoring_old_story(tmp_path):
    client = make_mixed_day_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "Today AI product launch" in response.text
    assert "Old cross-source model release" not in response.text


def test_story_page_renders_story_detail_and_source_items(tmp_path):
    client = make_client(tmp_path)
    home = client.get("/")
    story_id = re.search(r'/story/([a-f0-9]{12})', home.text).group(1)

    response = client.get(f"/story/{story_id}")

    assert response.status_code == 200
    assert "AI HOT · 故事详情" in response.text
    assert "OpenAI releases new agent tools" in response.text
    assert "New tools help developers build reliable agents." in response.text
    assert "全部来源 · 1" in response.text
    assert 'href="/"' in response.text


def test_all_news_page_renders_all_items_and_source_health(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/all-news")

    assert response.status_code == 200
    assert "AI HOT · 全部资讯" in response.text
    assert 'class="app-shell"' in response.text
    assert 'class="source-panel"' in response.text
    assert "全部资讯" in response.text
    assert "DeepMind publishes Gemini robotics update" in response.text
    assert "Missing Fixture" in response.text
    assert "failed" in response.text


def test_all_news_page_groups_multi_day_database_by_actual_dates(tmp_path):
    client = make_mixed_day_client(tmp_path)

    response = client.get("/all-news")

    assert response.status_code == 200
    assert "2026-06-28" in response.text
    assert "2026-05-01" in response.text
    assert "Today AI product launch" in response.text
    assert "Old cross-source model release" in response.text


def test_digest_page_renders_daily_report_and_top_links(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/digest")

    assert response.status_code == 200
    assert "AI HOT · 每日摘要" in response.text
    assert 'class="daily-brief"' in response.text
    assert "2026-06-28 AI 速报" in response.text
    assert "今日必读" in response.text
    assert "OpenAI releases new agent tools" in response.text
    assert re.search(r'href="/story/[a-f0-9]{12}"', response.text)


def test_digest_page_limits_must_read_to_digest_day(tmp_path):
    client = make_mixed_day_client(tmp_path)

    response = client.get("/digest")

    assert response.status_code == 200
    assert "2026-06-28 AI 速报" in response.text
    assert "Today AI product launch" in response.text
    assert "Old cross-source model release" not in response.text


def test_ui_stylesheet_is_served(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/assets/style.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert "--ink: #18181B" in response.text
