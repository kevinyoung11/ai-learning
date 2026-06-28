from pathlib import Path

from fastapi.testclient import TestClient

from aihot.api import create_app
from aihot.pipeline import run_pipeline_once


def make_client(tmp_path) -> TestClient:
    db_path = tmp_path / "aihot-ui.db"
    run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))
    return TestClient(create_app(db_path))


def test_home_page_renders_selected_stories_with_real_links(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "AI HOT · 精选" in response.text
    assert "OpenAI releases new agent tools" in response.text
    assert 'href="/story/59086c9068d6"' in response.text
    assert 'href="/all-news"' in response.text
    assert 'href="/digest"' in response.text


def test_story_page_renders_story_detail_and_source_items(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/story/59086c9068d6")

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
    assert "全部资讯" in response.text
    assert "DeepMind publishes Gemini robotics update" in response.text
    assert "Missing Fixture" in response.text
    assert "failed" in response.text


def test_digest_page_renders_daily_report_and_top_links(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/digest")

    assert response.status_code == 200
    assert "AI HOT · 每日摘要" in response.text
    assert "2026-06-28 AI 速报" in response.text
    assert "今日必读" in response.text
    assert "OpenAI releases new agent tools" in response.text
    assert 'href="/story/59086c9068d6"' in response.text


def test_ui_stylesheet_is_served(tmp_path):
    client = make_client(tmp_path)

    response = client.get("/assets/style.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert "--ink: #18181B" in response.text
