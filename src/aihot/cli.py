from __future__ import annotations

import json
from pathlib import Path

import typer

from aihot.api import create_app
from aihot.pipeline import run_pipeline_once
from aihot.scheduler import run_scheduled_ingest

app = typer.Typer(help="AI HOT ingestion MVP")


@app.command()
def ingest(
    sources: Path = typer.Option(..., "--sources", exists=True, readable=True),
    db: Path = typer.Option(..., "--db"),
    fixture_dir: Path | None = typer.Option(None, "--fixture-dir", exists=True, readable=True),
    allow_network: bool = typer.Option(False, "--allow-network", help="Allow fetching live HTTP(S) sources."),
    include_shadow: bool = typer.Option(False, "--include-shadow", help="Also fetch shadow/experimental sources."),
) -> None:
    summary = run_pipeline_once(
        sources,
        db,
        fixture_dir=fixture_dir,
        allow_network=allow_network,
        include_shadow=include_shadow,
    )
    typer.echo(json.dumps(summary, ensure_ascii=False, sort_keys=True))


@app.command()
def watch(
    sources: Path = typer.Option(..., "--sources", exists=True, readable=True),
    db: Path = typer.Option(..., "--db"),
    fixture_dir: Path | None = typer.Option(None, "--fixture-dir", exists=True, readable=True),
    allow_network: bool = typer.Option(False, "--allow-network", help="Allow fetching live HTTP(S) sources."),
    include_shadow: bool = typer.Option(False, "--include-shadow", help="Also fetch shadow/experimental sources."),
    interval_minutes: int | None = typer.Option(
        None,
        "--interval-minutes",
        min=1,
        help="Run repeatedly after this many minutes. Defaults to 60 when --daily-at is omitted.",
    ),
    daily_at: str | None = typer.Option(
        None,
        "--daily-at",
        help="Run once per day at local HH:MM. Use --wait-first to wait until the next matching time.",
    ),
    wait_first: bool = typer.Option(False, "--wait-first", help="Wait for the first scheduled time before running."),
    max_runs: int | None = typer.Option(None, "--max-runs", min=1, help="Stop after N runs; useful for smoke tests."),
) -> None:
    interval_seconds = interval_minutes * 60 if interval_minutes is not None else None
    run_scheduled_ingest(
        sources,
        db,
        fixture_dir=fixture_dir,
        allow_network=allow_network,
        include_shadow=include_shadow,
        interval_seconds=interval_seconds,
        daily_at=daily_at,
        run_immediately=not wait_first,
        max_runs=max_runs,
    )


@app.command()
def serve(
    db: Path = typer.Option(..., "--db", exists=True, readable=True),
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8000, "--port"),
) -> None:
    import uvicorn

    uvicorn.run(create_app(db), host=host, port=port)


if __name__ == "__main__":
    app()
