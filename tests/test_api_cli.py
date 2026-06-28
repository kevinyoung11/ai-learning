from pathlib import Path

from fastapi.testclient import TestClient
from typer.testing import CliRunner

from aihot.api import create_app
from aihot.cli import app
from aihot.pipeline import run_pipeline_once


def test_cli_ingest_creates_database_and_prints_summary(tmp_path):
    db_path = tmp_path / "aihot.db"
    runner = CliRunner()

    result = runner.invoke(
        app,
        [
            "ingest",
            "--sources",
            "sources/aihot-mvp.yml",
            "--db",
            str(db_path),
            "--fixture-dir",
            "tests/fixtures",
        ],
    )

    assert result.exit_code == 0
    assert '"sources_failed": 1' in result.stdout
    assert db_path.exists()


def test_api_reads_ingested_database(tmp_path):
    db_path = tmp_path / "aihot.db"
    run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))
    client = TestClient(create_app(db_path))

    assert client.get("/health").json() == {"status": "ok"}
    sources = client.get("/sources")
    assert sources.status_code == 200
    assert len(sources.json()["sources"]) == 5

    all_items = client.get("/items?mode=all")
    assert all_items.status_code == 200
    assert len(all_items.json()["items"]) == 3

    selected = client.get("/items?mode=selected")
    assert selected.status_code == 200
    selected_items = selected.json()["items"]
    assert selected_items
    story_id = selected_items[0]["story_id"]

    story = client.get(f"/stories/{story_id}")
    assert story.status_code == 200
    assert story.json()["story"]["id"] == story_id
    assert story.json()["items"]

    daily = client.get("/daily/2026-06-28")
    assert daily.status_code == 200
    assert daily.json()["daily"]["story_count"] >= 2

    assert client.get("/stories/missing").status_code == 404
    assert client.get("/daily/2099-01-01").status_code == 404
