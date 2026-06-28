from pathlib import Path

from fastapi.testclient import TestClient

from aihot.api import create_app
from aihot.pipeline import run_pipeline_once
from aihot.repository import Repository


def test_fixture_ingestion_to_api_flow(tmp_path):
    db_path = tmp_path / "aihot-e2e.db"

    summary = run_pipeline_once(Path("sources/aihot-mvp.yml"), db_path, fixture_dir=Path("tests/fixtures"))
    repo = Repository(db_path)
    client = TestClient(create_app(db_path))

    assert summary["items_inserted"] == 3
    assert len(repo.list_sources()) == 5
    assert len(repo.list_items(mode="all")) == 3
    assert any(run["status"] == "failed" for run in repo.list_source_runs("missing_fixture"))

    selected = client.get("/items?mode=selected").json()["items"]
    assert selected
    assert selected[0]["story_id"]
    assert client.get(f"/stories/{selected[0]['story_id']}").json()["items"]
    assert client.get("/daily/2026-06-28").json()["daily"]["story_count"] >= 2
