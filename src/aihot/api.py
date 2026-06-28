from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse, Response

from aihot.repository import Repository
from aihot.ui import STYLE_CSS, render_all_news, render_digest, render_home, render_story


def create_app(db_path: str | Path) -> FastAPI:
    repo = Repository(db_path)
    app = FastAPI(title="AI HOT Ingestion MVP")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/assets/style.css")
    def stylesheet() -> Response:
        return Response(STYLE_CSS, media_type="text/css")

    @app.get("/", response_class=HTMLResponse)
    def home_page() -> str:
        day = _latest_day(repo)
        items = _items_for_day(repo.list_items(mode="selected"), day)
        return render_home(items, day)

    @app.get("/story/{story_id}", response_class=HTMLResponse)
    def story_page(story_id: str) -> str:
        row = repo.get_story(story_id)
        if row is None:
            raise HTTPException(status_code=404, detail="story not found")
        items = row.pop("items")
        return render_story(row, items)

    @app.get("/all-news", response_class=HTMLResponse)
    def all_news_page() -> str:
        return render_all_news(repo.list_items(mode="all"), _sources_with_health(repo))

    @app.get("/digest", response_class=HTMLResponse)
    def digest_page() -> str:
        daily_rows = repo.list_daily_reports()
        if not daily_rows:
            raise HTTPException(status_code=404, detail="daily report not found")
        daily = daily_rows[0]
        day = str(daily["day"])
        return render_digest(day, daily, _items_for_day(repo.list_items(mode="selected"), day))

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


def _sources_with_health(repo: Repository) -> list[dict[str, object]]:
    source_rows = repo.list_sources()
    runs = repo.list_source_runs()
    latest_by_source: dict[str, dict[str, object]] = {}
    for run in runs:
        latest_by_source.setdefault(str(run["source_id"]), run)
    enriched = []
    for source in source_rows:
        latest = latest_by_source.get(str(source["id"]))
        enriched.append(
            {
                **source,
                "last_status": latest["status"] if latest else None,
                "last_error": latest["error"] if latest else None,
                "last_item_count": latest["item_count"] if latest else None,
            }
        )
    return enriched


def _latest_day(repo: Repository) -> str | None:
    daily_rows = repo.list_daily_reports()
    if daily_rows:
        return str(daily_rows[0]["day"])
    items = repo.list_items(mode="selected")
    return str(items[0]["published_at"])[:10] if items else None


def _items_for_day(items: list[dict[str, object]], day: str | None) -> list[dict[str, object]]:
    if day is None:
        return items
    return [item for item in items if str(item.get("published_at", "")).startswith(day)]
