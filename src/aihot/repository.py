from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any

from aihot.models import NormalizedItem, SourceConfig, SourceRun, Story


class Repository:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def init_db(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS sources (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    adapter TEXT NOT NULL,
                    url TEXT,
                    tier TEXT NOT NULL,
                    weight REAL NOT NULL,
                    enabled INTEGER NOT NULL,
                    timeout_seconds REAL NOT NULL
                );

                CREATE TABLE IF NOT EXISTS source_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_id TEXT NOT NULL,
                    status TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    item_count INTEGER NOT NULL,
                    error TEXT,
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                );

                CREATE TABLE IF NOT EXISTS items (
                    canonical_url TEXT PRIMARY KEY,
                    source_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    url TEXT NOT NULL,
                    raw_content TEXT NOT NULL,
                    published_at TEXT NOT NULL,
                    fetched_at TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    title_key TEXT NOT NULL,
                    FOREIGN KEY (source_id) REFERENCES sources(id)
                );

                CREATE TABLE IF NOT EXISTS stories (
                    id TEXT PRIMARY KEY,
                    canonical_title TEXT NOT NULL,
                    day TEXT NOT NULL,
                    summary TEXT NOT NULL,
                    hotness REAL NOT NULL,
                    source_count INTEGER NOT NULL,
                    selected INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS story_items (
                    story_id TEXT NOT NULL,
                    canonical_url TEXT NOT NULL,
                    PRIMARY KEY (story_id, canonical_url),
                    FOREIGN KEY (story_id) REFERENCES stories(id),
                    FOREIGN KEY (canonical_url) REFERENCES items(canonical_url)
                );

                CREATE TABLE IF NOT EXISTS daily_reports (
                    day TEXT PRIMARY KEY,
                    narrative TEXT NOT NULL,
                    story_count INTEGER NOT NULL
                );
                """
            )

    def upsert_sources(self, sources: list[SourceConfig]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO sources (
                    id, name, source_type, adapter, url, tier, weight, enabled, timeout_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name = excluded.name,
                    source_type = excluded.source_type,
                    adapter = excluded.adapter,
                    url = excluded.url,
                    tier = excluded.tier,
                    weight = excluded.weight,
                    enabled = excluded.enabled,
                    timeout_seconds = excluded.timeout_seconds
                """,
                [
                    (
                        source.id,
                        source.name,
                        source.source_type,
                        source.adapter,
                        source.url,
                        source.tier,
                        source.weight,
                        int(source.enabled),
                        source.timeout_seconds,
                    )
                    for source in sources
                ],
            )

    def list_sources(self) -> list[dict[str, Any]]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT id, name, source_type, adapter, url, tier, weight, enabled, timeout_seconds
                FROM sources
                ORDER BY id
                """
            ).fetchall()
        return [self._source_row(row) for row in rows]

    def upsert_items(self, items: list[NormalizedItem]) -> None:
        with self._connect() as conn:
            conn.executemany(
                """
                INSERT INTO items (
                    canonical_url, source_id, source_type, title, url, raw_content,
                    published_at, fetched_at, content_hash, title_key
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(canonical_url) DO UPDATE SET
                    source_id = excluded.source_id,
                    source_type = excluded.source_type,
                    title = excluded.title,
                    url = excluded.url,
                    raw_content = excluded.raw_content,
                    published_at = excluded.published_at,
                    fetched_at = excluded.fetched_at,
                    content_hash = excluded.content_hash,
                    title_key = excluded.title_key
                """,
                [
                    (
                        item.canonical_url,
                        item.source_id,
                        item.source_type,
                        item.title,
                        item.url,
                        item.raw_content,
                        self._format_dt(item.published_at),
                        self._format_dt(item.fetched_at),
                        item.content_hash,
                        item.title_key,
                    )
                    for item in items
                ],
            )

    def list_items(self, mode: str = "all") -> list[dict[str, Any]]:
        if mode not in {"all", "selected"}:
            raise ValueError("mode must be 'all' or 'selected'")

        if mode == "selected":
            query = """
                SELECT i.*, si.story_id, s.hotness, s.source_count
                FROM items i
                JOIN story_items si ON si.canonical_url = i.canonical_url
                JOIN stories s ON s.id = si.story_id
                WHERE s.selected = 1
                ORDER BY s.hotness DESC, i.published_at DESC, i.canonical_url
            """
        else:
            query = """
                SELECT i.*, si.story_id, s.hotness, s.source_count
                FROM items i
                LEFT JOIN story_items si ON si.canonical_url = i.canonical_url
                LEFT JOIN stories s ON s.id = si.story_id
                ORDER BY i.published_at DESC, i.canonical_url
            """

        with self._connect() as conn:
            rows = conn.execute(query).fetchall()
        return [self._item_row(row) for row in rows]

    def upsert_stories(self, stories: list[Story]) -> None:
        with self._connect() as conn:
            for story in stories:
                conn.execute(
                    """
                    INSERT INTO stories (
                        id, canonical_title, day, summary, hotness, source_count, selected
                    ) VALUES (?, ?, ?, ?, ?, ?, ?)
                    ON CONFLICT(id) DO UPDATE SET
                        canonical_title = excluded.canonical_title,
                        day = excluded.day,
                        summary = excluded.summary,
                        hotness = excluded.hotness,
                        source_count = excluded.source_count,
                        selected = excluded.selected
                    """,
                    (
                        story.id,
                        story.canonical_title,
                        story.day,
                        story.summary,
                        story.hotness,
                        story.source_count,
                        int(story.selected),
                    ),
                )
                conn.execute("DELETE FROM story_items WHERE story_id = ?", (story.id,))
                conn.executemany(
                    """
                    INSERT OR IGNORE INTO story_items (story_id, canonical_url)
                    VALUES (?, ?)
                    """,
                    [(story.id, url) for url in story.item_urls],
                )

    def replace_stories(self, stories: list[Story]) -> None:
        with self._connect() as conn:
            conn.execute("DELETE FROM story_items")
            conn.execute("DELETE FROM stories")
        self.upsert_stories(stories)

    def get_story(self, story_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            story = conn.execute(
                """
                SELECT id, canonical_title, day, summary, hotness, source_count, selected
                FROM stories
                WHERE id = ?
                """,
                (story_id,),
            ).fetchone()
            if story is None:
                return None

            items = conn.execute(
                """
                SELECT i.*, si.story_id
                FROM story_items si
                JOIN items i ON i.canonical_url = si.canonical_url
                WHERE si.story_id = ?
                ORDER BY i.published_at DESC, i.canonical_url
                """,
                (story_id,),
            ).fetchall()

        result = self._story_row(story)
        result["items"] = [self._item_row(row) for row in items]
        return result

    def insert_source_run(self, run: SourceRun) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO source_runs (source_id, status, fetched_at, item_count, error)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    run.source_id,
                    run.status,
                    self._format_dt(run.fetched_at),
                    run.item_count,
                    run.error,
                ),
            )

    def list_source_runs(self, source_id: str | None = None) -> list[dict[str, Any]]:
        if source_id is None:
            query = """
                SELECT id, source_id, status, fetched_at, item_count, error
                FROM source_runs
                ORDER BY fetched_at DESC, id DESC
            """
            params: tuple[Any, ...] = ()
        else:
            query = """
                SELECT id, source_id, status, fetched_at, item_count, error
                FROM source_runs
                WHERE source_id = ?
                ORDER BY fetched_at DESC, id DESC
            """
            params = (source_id,)

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [dict(row) for row in rows]

    def upsert_daily_report(self, day: str, narrative: str, story_count: int) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO daily_reports (day, narrative, story_count)
                VALUES (?, ?, ?)
                ON CONFLICT(day) DO UPDATE SET
                    narrative = excluded.narrative,
                    story_count = excluded.story_count
                """,
                (day, narrative, story_count),
            )

    def get_daily_report(self, day: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT day, narrative, story_count
                FROM daily_reports
                WHERE day = ?
                """,
                (day,),
            ).fetchone()
        return dict(row) if row is not None else None

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    @staticmethod
    def _format_dt(value: datetime) -> str:
        return value.isoformat()

    @staticmethod
    def _source_row(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["enabled"] = bool(result["enabled"])
        return result

    @staticmethod
    def _item_row(row: sqlite3.Row) -> dict[str, Any]:
        return dict(row)

    @staticmethod
    def _story_row(row: sqlite3.Row) -> dict[str, Any]:
        result = dict(row)
        result["selected"] = bool(result["selected"])
        return result
