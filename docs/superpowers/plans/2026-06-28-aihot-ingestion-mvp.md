# AI HOT Ingestion MVP Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Python ingestion MVP that proves source catalog loading, feed ingestion, dedupe, clustering, scoring, SQLite persistence, CLI execution, and FastAPI read endpoints end to end.

**Architecture:** A small Python package under `src/aihot` owns the pipeline. Tests drive behavior with local fixtures and FastAPI `TestClient`, avoiding external services and secrets. The first implementation is deterministic; live RSSHub, X, WeChat, and LLM adapters remain catalog-level future extensions.

**Tech Stack:** Python 3.11+, FastAPI, Typer, PyYAML, feedparser, httpx, pytest, SQLite from the standard library.

---

## File Map

- Create `pyproject.toml`: package metadata, dependencies, pytest config, console script.
- Create `src/aihot/__init__.py`: package version.
- Create `src/aihot/models.py`: dataclasses for source config, raw entries, normalized items, stories, source runs.
- Create `src/aihot/config.py`: YAML source catalog loader and validator.
- Create `src/aihot/adapters.py`: adapter registry, RSS/Atom parser, fixture HTTP fetcher.
- Create `src/aihot/normalize.py`: canonical URL, content hash, entry normalization.
- Create `src/aihot/cluster.py`: deterministic lightweight story grouping.
- Create `src/aihot/score.py`: deterministic hotness and digest generation.
- Create `src/aihot/repository.py`: SQLite schema and queries.
- Create `src/aihot/pipeline.py`: one-run orchestration and failure isolation.
- Create `src/aihot/api.py`: FastAPI application factory.
- Create `src/aihot/cli.py`: Typer CLI.
- Create `sources/aihot-mvp.yml`: first-batch source catalog using fixture and stable source shapes.
- Create `tests/fixtures/*.xml`: RSS fixtures with duplicates and related stories.
- Create `tests/test_*.py`: focused TDD coverage.

## Acceptance Checklist

- [ ] `pytest` passes.
- [ ] `python -m aihot.cli ingest --sources sources/aihot-mvp.yml --db /tmp/aihot-mvp.db` exits 0 and prints a JSON summary.
- [ ] API test proves `/health`, `/sources`, `/items?mode=all`, `/items?mode=selected`, `/stories/{id}`, and `/daily/{day}` return expected JSON from the generated DB.
- [ ] Failed source fixtures create failed `source_runs` rows and do not block successful sources.
- [ ] No tests require live network, secrets, X, WeChat, RSSHub, or LLM calls.

## Task 1: Project Harness And Source Config

**Files:**
- Create: `pyproject.toml`
- Create: `src/aihot/__init__.py`
- Create: `src/aihot/models.py`
- Create: `src/aihot/config.py`
- Create: `sources/aihot-mvp.yml`
- Test: `tests/test_config.py`

- [ ] **Step 1: Write failing config tests**

`tests/test_config.py` must assert:

```python
from pathlib import Path

import pytest

from aihot.config import SourceCatalogError, load_sources


def test_load_sources_returns_enabled_sources_with_tiers(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: decoder
    name: The Decoder
    type: stable_rss
    adapter: rss
    url: https://example.com/decoder.xml
    tier: stable
    weight: 1.4
    enabled: true
  - id: x_placeholder
    name: X Placeholder
    type: manual_placeholder
    adapter: disabled
    tier: experimental
    enabled: false
""",
        encoding="utf-8",
    )

    sources = load_sources(catalog, enabled_only=True)

    assert [source.id for source in sources] == ["decoder"]
    assert sources[0].tier == "stable"
    assert sources[0].weight == 1.4


def test_load_sources_rejects_duplicate_ids(tmp_path: Path):
    catalog = tmp_path / "sources.yml"
    catalog.write_text(
        """
sources:
  - id: duplicate
    name: One
    type: stable_rss
    adapter: rss
    url: https://example.com/one.xml
  - id: duplicate
    name: Two
    type: stable_rss
    adapter: rss
    url: https://example.com/two.xml
""",
        encoding="utf-8",
    )

    with pytest.raises(SourceCatalogError, match="duplicate"):
        load_sources(catalog)
```

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_config.py -q`

Expected: fails because `aihot.config` does not exist.

- [ ] **Step 3: Implement minimal config loader**

Create dataclasses in `models.py` and implement `load_sources(path, enabled_only=False)` in `config.py`. Validation must reject missing `sources`, duplicate ids, and enabled sources without a usable adapter.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_config.py -q`

Expected: 2 passed.

## Task 2: Feed Adapter And Normalization

**Files:**
- Create: `tests/fixtures/ai-feed.xml`
- Create: `tests/test_adapters_normalize.py`
- Create: `src/aihot/adapters.py`
- Create: `src/aihot/normalize.py`

- [ ] **Step 1: Write failing adapter and normalization tests**

Tests must cover:

- `parse_feed_bytes` returns raw entries with title, url, published timestamp, summary.
- `normalize_entry` strips tracking query params, preserves canonical URL, computes content hash, and requires a title and URL.
- duplicate titles with different punctuation produce the same normalized title key.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_adapters_normalize.py -q`

Expected: fails because adapter and normalizer functions do not exist.

- [ ] **Step 3: Implement parser and normalizer**

Use `feedparser.parse`. Use standard-library URL parsing. Remove `utm_*`, `ref`, and empty fragments. Use SHA-256 over normalized title plus summary for `content_hash`.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_adapters_normalize.py -q`

Expected: all tests pass.

## Task 3: Dedupe, Clustering, And Scoring

**Files:**
- Create: `tests/test_cluster_score.py`
- Create: `src/aihot/cluster.py`
- Create: `src/aihot/score.py`

- [ ] **Step 1: Write failing tests**

Tests must assert:

- same canonical URL dedupes to one item.
- related titles within the same day cluster into one story.
- unrelated titles create separate stories.
- story hotness increases with source count and source weight.
- generated daily digest includes top story titles.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_cluster_score.py -q`

Expected: fails because cluster and score modules do not exist.

- [ ] **Step 3: Implement deterministic logic**

Implement token-overlap clustering with a conservative threshold and same-day window. Implement scoring with source count, max source weight, and recency-independent deterministic weights.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_cluster_score.py -q`

Expected: all tests pass.

## Task 4: SQLite Repository

**Files:**
- Create: `tests/test_repository.py`
- Create: `src/aihot/repository.py`

- [ ] **Step 1: Write failing repository tests**

Tests must assert:

- `init_db` creates all tables.
- upserting sources is idempotent.
- inserting the same item URL twice stores one row.
- story and story-item persistence can be queried by selected/all modes.
- source run failures are persisted with error text.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_repository.py -q`

Expected: fails because repository module does not exist.

- [ ] **Step 3: Implement SQLite repository**

Use `sqlite3`, row factory dictionaries, explicit schema migrations via `CREATE TABLE IF NOT EXISTS`, and idempotent `INSERT OR IGNORE` / `ON CONFLICT` where appropriate.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_repository.py -q`

Expected: all tests pass.

## Task 5: Pipeline Orchestration

**Files:**
- Create: `tests/test_pipeline.py`
- Create: `src/aihot/pipeline.py`
- Modify: `src/aihot/adapters.py`
- Modify: `sources/aihot-mvp.yml`

- [ ] **Step 1: Write failing pipeline tests**

Tests must assert:

- running the pipeline against fixture sources stores sources, runs, items, stories, and a daily report.
- one missing fixture source records a failed run while another source succeeds.
- duplicate entries across sources do not create duplicate item rows.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_pipeline.py -q`

Expected: fails because `run_pipeline_once` does not exist.

- [ ] **Step 3: Implement orchestrator**

Load enabled sources, fetch each source through adapter registry, normalize entries, persist source runs, dedupe, cluster, score, write stories and daily report. Return a summary dictionary.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_pipeline.py -q`

Expected: all tests pass.

## Task 6: API And CLI

**Files:**
- Create: `tests/test_api_cli.py`
- Create: `src/aihot/api.py`
- Create: `src/aihot/cli.py`

- [ ] **Step 1: Write failing API and CLI tests**

Tests must assert:

- CLI `ingest` creates a database and prints JSON summary.
- `/health` returns `{"status":"ok"}`.
- `/sources` returns source rows and health fields.
- `/items?mode=all` returns all items.
- `/items?mode=selected` returns selected story-backed items ordered by score.
- `/stories/{id}` returns story plus source items.
- `/daily/{day}` returns daily report.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_api_cli.py -q`

Expected: fails because API and CLI modules do not exist.

- [ ] **Step 3: Implement API and CLI**

Expose `create_app(db_path)` and Typer commands `ingest` and `serve`. `serve` may create a Uvicorn app entrypoint but tests only need `create_app`.

- [ ] **Step 4: Run green test**

Run: `pytest tests/test_api_cli.py -q`

Expected: all tests pass.

## Task 7: End-To-End Verification And Documentation

**Files:**
- Modify: `README.md`
- Modify: `IMPLEMENTATION_PLAN.md` if needed only to link the executable MVP.
- Create: `tests/test_e2e.py`

- [ ] **Step 1: Write failing E2E test**

Test must create a temp database, run the pipeline with `sources/aihot-mvp.yml`, create the API app, and verify at least one selected item, one story, one failed source run, and one daily report can be read.

- [ ] **Step 2: Run red test**

Run: `pytest tests/test_e2e.py -q`

Expected: fails until all integration pieces are connected.

- [ ] **Step 3: Add README usage**

Document install, test, ingest, and API usage. Include explicit MVP boundaries for X/WeChat/LLM.

- [ ] **Step 4: Run full verification**

Run:

```bash
pytest -q
python -m aihot.cli ingest --sources sources/aihot-mvp.yml --db /tmp/aihot-mvp.db
```

Expected: tests pass and CLI prints JSON with nonzero items and stories plus one failed fixture source.

## Parallelization Plan

- Explorer agents can independently review source feasibility and test strategy while the main thread writes the design and plan.
- Worker agents may implement disjoint tasks only after red tests exist:
  - Worker A: adapter and normalization files.
  - Worker B: clustering and scoring files.
  - Worker C: repository files.
- Main thread owns integration tasks: pipeline, API, CLI, final verification, commit, push, PR.

Subagents must not edit overlapping files without coordination. The main thread verifies every subagent result with focused tests and full tests.
