# AI Learning

Personal AI learning roadmap and notes.

## Contents

- `ai-radar.md`: AI learning roadmap, course plan, output-driven study method, and English practice plan.
- `IMPLEMENTATION_PLAN.md`: AI HOT-style information radar architecture notes.
- `src/aihot/`: executable ingestion MVP for feed-like AI information sources.
- `sources/aihot-mvp.yml`: fixture-backed MVP source catalog.

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

Serve the read API:

```bash
.venv/bin/python -m aihot.cli serve --db /tmp/aihot-mvp.db
```

Useful endpoints:

- `GET /health`
- `GET /sources`
- `GET /items?mode=all`
- `GET /items?mode=selected`
- `GET /stories/{id}`
- `GET /daily/{day}`

MVP boundaries: this first implementation does not depend on live X/Twitter,
WeChat, RSSHub, paid APIs, or LLM calls. Those integrations should be added as
separate adapters after the fixture-only ingestion path is stable.

## Local-only Files

- `yy-all-query.md` is intentionally ignored because it may contain local history, internal paths, logs, cookies, tokens, or other sensitive content.
