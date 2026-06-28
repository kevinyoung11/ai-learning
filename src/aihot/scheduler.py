from __future__ import annotations

import json
import time as time_module
from collections.abc import Callable
from datetime import datetime, time, timedelta
from pathlib import Path
from typing import Any

from aihot.pipeline import run_pipeline_once


Emit = Callable[[dict[str, Any]], None]
Sleep = Callable[[float], None]
Now = Callable[[], datetime]


def parse_daily_at(value: str) -> time:
    parts = value.split(":")
    if len(parts) != 2 or any(len(part) != 2 or not part.isdigit() for part in parts):
        raise ValueError("daily time must use HH:MM")
    hour, minute = (int(part) for part in parts)
    if hour > 23 or minute > 59:
        raise ValueError("daily time must use HH:MM")
    return time(hour=hour, minute=minute)


def next_daily_run(now: datetime, daily_at: time) -> datetime:
    candidate = now.replace(
        hour=daily_at.hour,
        minute=daily_at.minute,
        second=0,
        microsecond=0,
    )
    if candidate <= now:
        candidate += timedelta(days=1)
    return candidate


def run_scheduled_ingest(
    catalog_path: str | Path,
    db_path: str | Path,
    *,
    fixture_dir: str | Path | None = None,
    allow_network: bool = False,
    interval_seconds: int | None = None,
    daily_at: str | None = None,
    run_immediately: bool = True,
    max_runs: int | None = None,
    sleep: Sleep = time_module.sleep,
    now: Now = datetime.now,
    emit: Emit | None = None,
) -> None:
    if interval_seconds is None and daily_at is None:
        interval_seconds = 24 * 60 * 60
    if interval_seconds is not None and interval_seconds <= 0:
        raise ValueError("interval_seconds must be positive")
    if max_runs is not None and max_runs <= 0:
        raise ValueError("max_runs must be positive")

    daily_time = parse_daily_at(daily_at) if daily_at else None
    runs = 0
    first_run = True
    while max_runs is None or runs < max_runs:
        if not (first_run and run_immediately):
            wait_seconds, next_run_at = _next_wait(interval_seconds, daily_time, now())
            _emit(
                emit,
                {
                    "event": "sleep",
                    "seconds": wait_seconds,
                    "next_run_at": next_run_at.isoformat() if next_run_at else None,
                },
            )
            sleep(wait_seconds)

        summary = run_pipeline_once(
            catalog_path,
            db_path,
            fixture_dir=fixture_dir,
            allow_network=allow_network,
        )
        runs += 1
        first_run = False
        _emit(emit, {"event": "ingest", "run": runs, "summary": summary})


def _next_wait(
    interval_seconds: int | None,
    daily_time: time | None,
    now_value: datetime,
) -> tuple[float, datetime | None]:
    if daily_time is not None:
        next_run_at = next_daily_run(now_value, daily_time)
        return max((next_run_at - now_value).total_seconds(), 0), next_run_at
    assert interval_seconds is not None
    return float(interval_seconds), None


def _emit(emit: Emit | None, event: dict[str, Any]) -> None:
    if emit is not None:
        emit(event)
    else:
        print(json.dumps(event, ensure_ascii=False, sort_keys=True), flush=True)
