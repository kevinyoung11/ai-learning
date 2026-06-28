# AI HOT Source Gateway Boundaries

This project treats source ingestion as three modes:

- `active`: fetched by the default hourly job and eligible for selected stories, scoring, digest, and the home page.
- `shadow`: fetched only when `--include-shadow` is passed. Items are stored for inspection, but they are not clustered into selected stories or daily reports.
- `quarantined`: registered but skipped. The pipeline records a `quarantined` source run instead of attempting network access.

## External Boundaries

- WeChat public accounts must be exposed through a self-hosted RSS-compatible gateway such as `we-mp-rss` or RSSHub. Configure `WECHAT_RSS_BASE`; each WeChat source resolves to `env://WECHAT_RSS_BASE/<source_id>.xml`.
- X accounts default to an RSSHub-compatible proxy route. Configure `X_RSS_BASE`; each X source resolves to `env://X_RSS_BASE/<handle>`.
- The `x_api_user_timeline` adapter supports official X API style JSON and requires `X_BEARER_TOKEN` when `auth_env: X_BEARER_TOKEN` is configured. Sources need either a direct `url` or `config.user_id` to perform a live API request.
- Secrets are never stored in `sources/*.yml` or SQLite. YAML stores only environment variable names.
- Missing environment variables are recorded as `blocked_config`, not as source failures.

## Acceptance Criteria

- Default hourly ingestion runs only `active` non-quarantined sources.
- Shadow ingestion requires explicit `--include-shadow`.
- A single source failure must not abort the whole run.
- Missing proxy/API configuration must be visible in `/sources` as `blocked_config`.
- Shadow items may appear in `/items?mode=all`, but must not appear in `/items?mode=selected`, selected stories, or daily reports.
- Quarantined sources must be persisted and visible, but skipped during fetch.
- Full verification requires `python -m pytest` and at least one CLI ingest run against `sources/aihot-live.yml`.

## Useful Commands

```bash
.venv/bin/python -m aihot.cli ingest --sources sources/aihot-live.yml --db data/aihot.db --allow-network
.venv/bin/python -m aihot.cli ingest --sources sources/aihot-live.yml --db /tmp/aihot-shadow.db --allow-network --include-shadow
```

Set proxy environment variables before shadow ingestion:

```bash
export WECHAT_RSS_BASE="https://your-wechat-rss.example/feeds"
export X_RSS_BASE="https://rsshub.example/twitter/user"
```
