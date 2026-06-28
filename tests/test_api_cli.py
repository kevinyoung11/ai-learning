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


def test_cli_ingest_accepts_allow_network_option(tmp_path, monkeypatch):
    db_path = tmp_path / "aihot.db"
    runner = CliRunner()
    captured = {}

    def fake_run_pipeline_once(sources, db, *, fixture_dir=None, allow_network=False, include_shadow=False):
        captured["sources"] = sources
        captured["db"] = db
        captured["fixture_dir"] = fixture_dir
        captured["allow_network"] = allow_network
        captured["include_shadow"] = include_shadow
        return {"sources_total": 1, "sources_failed": 0, "items_inserted": 1, "stories": 1}

    monkeypatch.setattr("aihot.cli.run_pipeline_once", fake_run_pipeline_once)

    result = runner.invoke(
        app,
        [
            "ingest",
            "--sources",
            "sources/aihot-mvp.yml",
            "--db",
            str(db_path),
            "--allow-network",
        ],
    )

    assert result.exit_code == 0
    assert captured["allow_network"] is True
    assert captured["include_shadow"] is False
    assert '"items_inserted": 1' in result.stdout


def test_cli_watch_passes_schedule_options(tmp_path, monkeypatch):
    db_path = tmp_path / "aihot.db"
    runner = CliRunner()
    captured = {}

    def fake_run_scheduled_ingest(
        sources,
        db,
        *,
        fixture_dir=None,
        allow_network=False,
        include_shadow=False,
        interval_seconds=None,
        daily_at=None,
        run_immediately=True,
        max_runs=None,
    ):
        captured.update(
            {
                "sources": sources,
                "db": db,
                "fixture_dir": fixture_dir,
                "allow_network": allow_network,
                "include_shadow": include_shadow,
                "interval_seconds": interval_seconds,
                "daily_at": daily_at,
                "run_immediately": run_immediately,
                "max_runs": max_runs,
            }
        )

    monkeypatch.setattr("aihot.cli.run_scheduled_ingest", fake_run_scheduled_ingest)

    result = runner.invoke(
        app,
        [
            "watch",
            "--sources",
            "sources/aihot-mvp.yml",
            "--db",
            str(db_path),
            "--fixture-dir",
            "tests/fixtures",
            "--allow-network",
            "--daily-at",
            "08:30",
            "--wait-first",
            "--max-runs",
            "1",
        ],
    )

    assert result.exit_code == 0
    assert captured["allow_network"] is True
    assert captured["include_shadow"] is False
    assert captured["daily_at"] == "08:30"
    assert captured["run_immediately"] is False
    assert captured["max_runs"] == 1


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
