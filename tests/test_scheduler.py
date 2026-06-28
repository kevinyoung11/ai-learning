from datetime import datetime, timezone
from pathlib import Path

import pytest

from aihot.scheduler import next_daily_run, parse_daily_at, run_scheduled_ingest


def test_parse_daily_at_validates_hh_mm():
    assert parse_daily_at("08:30").hour == 8
    assert parse_daily_at("08:30").minute == 30

    with pytest.raises(ValueError, match="HH:MM"):
        parse_daily_at("8:30")

    with pytest.raises(ValueError, match="HH:MM"):
        parse_daily_at("25:00")


def test_next_daily_run_uses_today_or_tomorrow():
    now = datetime(2026, 6, 28, 7, 0, tzinfo=timezone.utc)
    assert next_daily_run(now, parse_daily_at("08:00")) == datetime(
        2026, 6, 28, 8, 0, tzinfo=timezone.utc
    )

    later = datetime(2026, 6, 28, 9, 0, tzinfo=timezone.utc)
    assert next_daily_run(later, parse_daily_at("08:00")) == datetime(
        2026, 6, 29, 8, 0, tzinfo=timezone.utc
    )


def test_run_scheduled_ingest_runs_immediately_then_sleeps_between_runs(tmp_path, monkeypatch):
    calls = []
    sleeps = []
    events = []

    def fake_pipeline(catalog_path, db_path, *, fixture_dir=None, allow_network=False, include_shadow=False):
        calls.append((catalog_path, db_path, fixture_dir, allow_network, include_shadow))
        return {"sources_total": 1, "sources_failed": 0, "items_inserted": len(calls), "stories": 1}

    monkeypatch.setattr("aihot.scheduler.run_pipeline_once", fake_pipeline)

    run_scheduled_ingest(
        Path("sources/aihot-mvp.yml"),
        tmp_path / "aihot.db",
        interval_seconds=60,
        allow_network=True,
        max_runs=2,
        sleep=sleeps.append,
        emit=events.append,
    )

    assert len(calls) == 2
    assert calls[0][3] is True
    assert sleeps == [60]
    assert [event["event"] for event in events] == ["ingest", "sleep", "ingest"]


def test_run_scheduled_ingest_defaults_to_hourly_interval(tmp_path, monkeypatch):
    calls = []
    sleeps = []

    def fake_pipeline(catalog_path, db_path, *, fixture_dir=None, allow_network=False, include_shadow=False):
        calls.append((catalog_path, db_path))
        return {"sources_total": 1, "sources_failed": 0, "items_inserted": len(calls), "stories": 1}

    monkeypatch.setattr("aihot.scheduler.run_pipeline_once", fake_pipeline)

    run_scheduled_ingest(
        Path("sources/aihot-mvp.yml"),
        tmp_path / "aihot.db",
        run_immediately=False,
        max_runs=1,
        sleep=sleeps.append,
        emit=lambda event: None,
    )

    assert len(calls) == 1
    assert sleeps == [3600]


def test_run_scheduled_ingest_can_wait_until_daily_time(tmp_path, monkeypatch):
    calls = []
    sleeps = []
    events = []
    now_values = [
        datetime(2026, 6, 28, 7, 30, tzinfo=timezone.utc),
        datetime(2026, 6, 28, 7, 30, tzinfo=timezone.utc),
    ]

    def fake_now():
        return now_values.pop(0) if now_values else datetime(2026, 6, 28, 8, 0, tzinfo=timezone.utc)

    def fake_pipeline(catalog_path, db_path, *, fixture_dir=None, allow_network=False, include_shadow=False):
        calls.append((catalog_path, db_path))
        return {"sources_total": 1, "sources_failed": 0, "items_inserted": 1, "stories": 1}

    monkeypatch.setattr("aihot.scheduler.run_pipeline_once", fake_pipeline)

    run_scheduled_ingest(
        Path("sources/aihot-mvp.yml"),
        tmp_path / "aihot.db",
        daily_at="08:00",
        run_immediately=False,
        max_runs=1,
        sleep=sleeps.append,
        now=fake_now,
        emit=events.append,
    )

    assert len(calls) == 1
    assert sleeps == [1800]
    assert events[0]["event"] == "sleep"
    assert events[1]["event"] == "ingest"
