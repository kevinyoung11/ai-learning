# AI Learning

Personal AI learning roadmap and notes.

## Contents

- `ai-radar.md`: AI learning roadmap, course plan, output-driven study method, and English practice plan.
- `IMPLEMENTATION_PLAN.md`: AI HOT-style information radar architecture notes.
- `src/aihot/`: executable ingestion MVP for feed-like AI information sources.
- `sources/aihot-mvp.yml`: fixture-backed MVP source catalog.
- `sources/aihot-live.yml`: live AI news source catalog.

## AI HOT Ingestion MVP

The MVP proves the local flow:

```text
source catalog -> RSS/Atom adapter -> normalization -> dedupe -> clustering
-> deterministic scoring/daily report -> SQLite -> CLI/FastAPI reads
```

Install and test:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -e '.[test]'
.venv/bin/python -m pytest -q
```

Run one fixture-backed ingestion:

```bash
.venv/bin/python -m aihot.cli ingest \
  --sources sources/aihot-mvp.yml \
  --db /tmp/aihot-mvp.db \
  --fixture-dir tests/fixtures
```

Run one live ingestion into the local app database:

```bash
.venv/bin/python -m aihot.cli ingest \
  --sources sources/aihot-live.yml \
  --db data/aihot.db \
  --allow-network
```

Run a long-lived hourly scanner. This command runs once immediately, then
continues every hour:

```bash
.venv/bin/python -m aihot.cli watch \
  --sources sources/aihot-live.yml \
  --db data/aihot.db \
  --allow-network
```

For systemd/launchd smoke tests, add `--max-runs 1` to exit after one scan.
For a fixed daily time instead of hourly scanning, add `--daily-at 08:30`.

Serve the read API:

```bash
.venv/bin/python -m aihot.cli serve --db data/aihot.db
```

Useful endpoints:

- `GET /health`
- `GET /sources`
- `GET /items?mode=all`
- `GET /items?mode=selected`
- `GET /stories/{id}`
- `GET /daily/{day}`

Current boundaries: stable RSS/Atom/API sources are enabled by default. Generic
HTML sources are cataloged but disabled by default until each site has a
source-specific parser, because navigation pages can produce noisy headlines.
This implementation does not depend on live X/Twitter, WeChat, RSSHub, paid
APIs, or LLM calls.

## Local-only Files

- `yy-all-query.md` is intentionally ignored because it may contain local history, internal paths, logs, cookies, tokens, or other sensitive content.
