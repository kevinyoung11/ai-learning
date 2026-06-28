from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query

from aihot.repository import Repository


def create_app(db_path: str | Path) -> FastAPI:
    repo = Repository(db_path)
    app = FastAPI(title="AI HOT Ingestion MVP")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/sources")
    def sources() -> dict[str, object]:
        source_rows = repo.list_sources()
        runs = repo.list_source_runs()
        latest_by_source: dict[str, dict[str, object]] = {}
        for run in runs:
            latest_by_source.setdefault(str(run["source_id"]), run)
        enriched = []
        for source in source_rows:
            latest = latest_by_source.get(source["id"])
            enriched.append(
                {
                    **source,
                    "last_status": latest["status"] if latest else None,
                    "last_error": latest["error"] if latest else None,
                    "last_item_count": latest["item_count"] if latest else None,
                }
            )
        return {"sources": enriched}

    @app.get("/items")
    def items(mode: str = Query(default="all", pattern="^(all|selected)$")) -> dict[str, object]:
        return {"items": repo.list_items(mode=mode)}

    @app.get("/stories/{story_id}")
    def story(story_id: str) -> dict[str, object]:
        row = repo.get_story(story_id)
        if row is None:
            raise HTTPException(status_code=404, detail="story not found")
        items = row.pop("items")
        return {"story": row, "items": items}

    @app.get("/daily/{day}")
    def daily(day: str) -> dict[str, object]:
        row = repo.get_daily_report(day)
        if row is None:
            raise HTTPException(status_code=404, detail="daily report not found")
        return {"daily": row}

    return app
