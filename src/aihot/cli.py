from __future__ import annotations

import json
from pathlib import Path

import typer

from aihot.api import create_app
from aihot.pipeline import run_pipeline_once

app = typer.Typer(help="AI HOT ingestion MVP")


@app.command()
def ingest(
    sources: Path = typer.Option(..., "--sources", exists=True, readable=True),
    db: Path = typer.Option(..., "--db"),
    fixture_dir: Path | None = typer.Option(None, "--fixture-dir", exists=True, readable=True),
    allow_network: bool = typer.Option(False, "--allow-network", help="Allow fetching live HTTP(S) sources."),
) -> None:
    summary = run_pipeline_once(sources, db, fixture_dir=fixture_dir, allow_network=allow_network)
    typer.echo(json.dumps(summary, ensure_ascii=False, sort_keys=True))


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
