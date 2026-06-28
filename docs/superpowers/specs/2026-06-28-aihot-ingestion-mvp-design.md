# AI HOT Ingestion MVP Design

## Objective

Build a testable personal-use AI information radar MVP that can ingest a bounded source catalog, fetch feed-like content, normalize items, deduplicate them, group related items into stories, score stories, persist results, and expose read APIs for selected items, all items, source health, and daily summaries.

The first PR must prove the full local flow works end to end without depending on fragile external services or secrets.

## Product Boundary

In scope:

- A Python backend package for the ingestion pipeline.
- A YAML source catalog with stable first-batch sources and adapter metadata.
- Feed ingestion through standard RSS/Atom parsing and deterministic HTTP fixture feeds.
- Source health tracking for every fetch attempt.
- Item normalization, URL canonicalization, content hashing, duplicate suppression, lightweight story clustering, and deterministic hotness scoring.
- SQLite persistence.
- A CLI that runs the pipeline once.
- FastAPI read endpoints matching the first useful slice of AI HOT-style behavior.
- Automated tests plus an end-to-end verification command that starts from fixtures and proves data reaches the API layer.

Out of scope for the first PR:

- Production X/Twitter scraping.
- Production WeChat scraping.
- Paid APIs, browser-cookie extraction, captcha handling, or credential storage.
- LLM calls. The MVP uses deterministic summary and scoring logic so tests are stable.
- A polished frontend.
- Public hosting, auth, rate limits, background scheduler, and operational dashboards.

## Source Integration Strategy

Sources are classified by operational confidence, not by brand importance.

- `stable_rss`: official RSS/Atom feeds and GitHub releases. These are the first production-ready path.
- `rsshub_rss`: RSSHub-derived feeds. The system supports them as ordinary feed URLs, but source health makes failure visible.
- `http_fixture`: deterministic local or test HTTP feeds used for TDD and end-to-end verification.
- `manual_placeholder`: sources known from `news-source.md` but not enabled until a working adapter or feed URL exists.

The first implementation must not require live RSSHub, X cookies, WeChat cookies, or external APIs. It must support adding those later by extending source catalog entries and adapters without changing the core pipeline.

## Architecture

```text
source catalog
  -> fetch adapters
  -> raw feed entries
  -> normalized items
  -> URL/hash dedupe
  -> story clustering
  -> deterministic scoring/summary
  -> SQLite repository
  -> CLI / FastAPI read endpoints
```

Core modules:

- `aihot.config`: loads and validates source catalog files.
- `aihot.adapters`: fetches raw entries from feed URLs or deterministic fixtures.
- `aihot.normalize`: converts raw entries into canonical items.
- `aihot.dedupe`: creates stable URL keys and content hashes.
- `aihot.cluster`: assigns items to lightweight stories.
- `aihot.score`: computes deterministic hotness and summary text.
- `aihot.repository`: owns SQLite schema and persistence.
- `aihot.pipeline`: orchestrates one ingestion run.
- `aihot.api`: exposes read endpoints.
- `aihot.cli`: provides `ingest`, `serve`, and inspection commands.

## Data Model

Tables:

- `sources`: source registry and operational state.
- `source_runs`: one row per source fetch attempt.
- `items`: normalized raw news records.
- `stories`: clustered events used by selected feeds and daily summaries.
- `story_items`: many-to-many mapping between stories and items.
- `daily_reports`: deterministic daily digest generated from top stories.

The database schema is created automatically by `init_db`.

## Error Handling

Per-source failures are isolated. A failed source creates a `source_runs` row with status `failed`, error text, and item count `0`; the pipeline continues with remaining sources.

Malformed feed entries are skipped with enough context in the run error summary. Duplicate items do not fail ingestion. Database writes are idempotent for item URLs and story membership.

## Acceptance Criteria

- Behavior: Running the CLI against fixture sources creates a SQLite database containing sources, source runs, deduplicated items, clustered stories, and a daily report.
- Behavior: Failed source fetches are recorded without stopping successful sources.
- Behavior: Duplicate URLs and near-identical titles do not create duplicate items or separate stories.
- API: `/health`, `/sources`, `/items?mode=all`, `/items?mode=selected`, `/stories/{id}`, and `/daily/{day}` return JSON from the SQLite repository.
- Boundaries: The first PR does not depend on external secrets, live X/Twitter, live WeChat, paid APIs, or live LLMs.
- Tests: Focused failing tests are added before production code. Tests cover source config validation, feed parsing, normalization, dedupe, clustering/scoring, repository persistence, pipeline failure isolation, CLI ingestion, and API responses.
- Verification: `pytest` passes, and an end-to-end command ingests fixture data then queries API endpoints with FastAPI `TestClient`.
- GitHub: Work is committed on `codex/aihot-ingestion-mvp`, pushed to `origin`, and a PR is opened against `main`.

## Rollback And Risk

The PR is additive. It does not change existing docs except to reference the new implementation. Rollback is removing the new package, tests, catalog, and docs.

Main risks:

- Source volatility is real for X and WeChat. The MVP contains explicit placeholders and health tracking instead of pretending these are stable.
- Lightweight clustering will not match embedding quality. It is acceptable for first PR because it is deterministic and testable.
- No LLM summaries means generated text is less rich than AI HOT. This is intentional for stable TDD; LLM integration can be a later adapter with cached outputs and fallback behavior.
